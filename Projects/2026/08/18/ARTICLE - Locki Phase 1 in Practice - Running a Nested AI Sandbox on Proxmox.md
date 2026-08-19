---
title: "ARTICLE - Locki Phase 1 in Practice - Running a Nested AI Sandbox on Proxmox"
aliases:
  - locki phase 1 nested proxmox
  - lima incus nested kvm permission denied
  - locki container-setup icmp connectivity check
tags:
  - article
  - locki
  - proxmox
  - sandboxing
  - ai-agents
  - incus
  - lima
  - nested-virt
  - homelab
status: active
type: article
created: 2026-08-18
repo: /home/manuel/code/wesen/claw-stuff
---

# Locki Phase 1 in Practice: Running a Nested AI Sandbox on Proxmox

A design for hosting Locki on a home Proxmox node separates the work into two phases: a nested setup that requires no changes to Locki, and a native port that replaces the Lima layer with a Proxmox-managed virtual machine. This article records the execution of the nested setup — Phase 1 — and the two failures that had to be solved before a sandbox would run. The earlier article [[ARTICLE - Locki on Proxmox - Sandboxing AI Coding Agents on a Homelab Hypervisor]] covers the architecture and the upgrade that preceded this work; this one covers what happened when the design met the hardware.

The outcome is that Locki runs nested on the crib node. A Linux virtual machine that Proxmox hosts contains a Lima-managed QEMU virtual machine, which contains a Fedora system running Incus, which contains the per-sandbox container. File synchronization between the sandbox and the host virtual machine works. The command bridge that scopes Git writes to namespaced branches works. The two failures were both narrow and both diagnostic: a userspace permission on a device file, and a connectivity probe that assumed a protocol the network does not pass.

> [!summary]
> 1. **Nested virtualization works once the host virtual machine's user can open `/dev/kvm`** — the failure is a group-membership problem, not a nesting problem, and the diagnosis lives in the Lima stderr log rather than Locki's own output.
> 2. **The sandbox's first-run setup assumes Internet Control Message Protocol works** — on a network where it is filtered, an unguarded `ping` under `set -e` aborts the entire setup even though HyperText Transfer Protocol works fine.
> 3. **The core guarantees hold once these two are fixed** — a file written in the sandbox appears on the host worktree, and a Git commit made in the sandbox lands on the real worktree scoped to the sandbox's own branch.
> 4. **An agent, a repository, and direct tailnet access are the remaining steps from a working sandbox to real use** — the agent auto-installs via Locki's shim, the repository is an ordinary clone, and Tailscale removes the jump host. Only the agent's one-time OAuth login is manual, and it persists across all sandboxes.

## Why this note exists

This note preserves the engineering knowledge from executing Phase 1, written so a reader can reproduce the setup, recognize the two failures, and understand why each fix is correct rather than coincidental. The triggering work lives in the docmgr ticket `LOCKI-PROXMOX-CRIB-2026-08-18` (diary steps 5–10).

## The host virtual machine

Phase 1 begins with a Linux virtual machine that Proxmox hosts. Locki itself is unchanged; it runs inside this virtual machine exactly as it would on a desktop. The virtual machine is created with the same `qm` sequence already proven on this node for the k3s workload, sized for Locki and given nested-virtualization exposure:

```bash
qm create 9410 --name locki-host --memory 16384 --cores 4 --cpu host \
  --net0 virtio,bridge=vmbr0 --bios ovmf --machine q35 --agent enabled=1
qm importdisk 9410 /var/lib/vz/template/iso/noble-server-cloudimg-amd64.img local-lvm
qm set 9410 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9410-disk-0 \
  --efidisk0 local-lvm:1,efitype=4m,pre-enrolled-keys=0 \
  --ide2 local-lvm:cloudinit --boot order=scsi0 \
  --ciuser ubuntu --sshkeys /root/.ssh/authorized_keys --ipconfig0 ip=dhcp
qm resize 9410 scsi0 60G
qm start 9410
```

The host virtual machine came up as `locki-host`, Ubuntu 24.04.4 LTS, kernel 6.8.0-62-generic, four virtual processors, fifteen gibibytes of memory, and `/dev/kvm` present. The `--cpu host` setting passes the host's virtualization extensions through to the guest, so the virtual machine can itself run accelerated virtual machines. The earlier article documents why the design originally specified eight cores; this node enforces a four-virtual-processor-per-VM cap, which the existing agent-runner virtual machines already respect, so the host virtual machine was set to four.

The virtual machine receives its address over Dynamic Host Configuration Protocol. The Ubuntu cloud image does not install the QEMU guest agent, so the Proxmox `qm guest cmd` interface is unavailable until it is installed manually; the address was found instead by scanning the bridge with `nmap -sn` and matching the virtual machine's media access control address:

```text
nmap -sn -n 192.168.0.0/24 | grep -B2 <MAC>
Nmap scan report for 192.168.0.87
MAC Address: BC:24:11:0E:F9:75
```

The cable modem on this network blocks layer-three traffic to virtual media access control addresses from other local devices. Reachability from the operator's development machine therefore goes through the Proxmox node as a jump host rather than directly to the virtual machine. This is a property of the network, documented in the prior deployment, and it recurs throughout Phase 1: every command to the host virtual machine is an Secure Shell command through the node.

## Installing Locki inside the host virtual machine

Locki is a Python command-line tool installed with `uv tool install locki`. Lima, the virtual machine manager Locki uses, requires QEMU on Linux, so the two prerequisites are installed inside the host virtual machine:

```bash
sudo apt install -y qemu-system-x86 qemu-utils   # QEMU 8.2.2
curl -LsSf https://astral.sh/uv/install.sh | sh    # uv 0.12.5
uv tool install locki                             # locki 0.0.27
locki setup --defaults                            # config.toml: ai_command, ide_command
```

At this point `locki vm status` reports `VM: none`. No Lima virtual machine exists yet. The first command that needs a sandbox triggers `VMService.ensure_running()`, which downloads the Fedora image and runs the guest provisioning script. This is the heavy step, and it is the step that fails first.

## The first failure: `/dev/kvm` permission denied

The first sandbox creation reported only `Lima VM failed to start. LIMA_HOME=...`. Locki's own output gave no detail. The detail was in the Lima host-agent stderr log at `~/.local/state/locki/lima/locki/ha.stderr.log`:

```text
qemu[stderr]: Could not access KVM kernel module: Permission denied
qemu-system-x86_64: failed to initialize kvm: Permission denied
Driver stopped due to error: "exit status 1"
```

The QEMU command line Lima constructed was correct for nested virtualization:

```text
qemu-system-x86_64 -m 15360 -cpu host -machine q35,accel=kvm \
  -smp 4,sockets=1,cores=4,threads=1 -drive if=pflash,...,file=/usr/share/OVMF/OVMF_CODE_4M.fd ...
```

It used `accel=kvm` and `-cpu host`, which is the right shape for a nested guest on a host whose `kvm_intel` module has `nested=1`. The failure was not a nesting failure. It was a userspace permission failure: Lima runs QEMU as the unprivileged user, and the device file `/dev/kvm` was owned by `root:kvm` with mode `0660`, while the `ubuntu` user created by cloud-init was not a member of the `kvm` group.

```text
crw-rw---- 1 root kvm 10, 232 ... /dev/kvm
$ id
uid=1000(ubuntu) ... groups=...,105(lxd)   # no kvm
```

The fix is to add the user to the `kvm` group and start a fresh login session, because group membership is evaluated at login time:

```bash
sudo usermod -aG kvm ubuntu
# a new ssh session: id now lists kvm (gid 993), and [ -w /dev/kvm ] is true
```

The diagnostic lesson is about where the failure surfaces. Locki reports a terse message; Lima writes the real cause to its own stderr log under `LIMA_HOME/locki/ha.stderr.log`. When a Lima virtual machine fails to start, that log is the first place to look, not Locki's standard output. The fix is also a provisioning step that a cloud-init `--ciuser ubuntu` virtual machine does not perform by default: any host virtual machine that will run Locki must place its user in the `kvm` group, or make `/dev/kvm` world-readable, before the first sandbox.

## The second failure: a connectivity probe that assumes ICMP

With `/dev/kvm` accessible, the Lima virtual machine started in one minute twenty-six seconds, the worktree was created, and the Incus container started. Then the container's first-run setup script aborted with exit status 124. Exit 124 is the exit status of the GNU `timeout` command, which means a `timeout(1)` invocation somewhere in the setup script killed a command.

Locki's `run_command` has no Python-level timeout, so the 124 came from a `timeout` shell builtin inside `container-setup.sh`. The script runs under `set -eux`, which means any command that returns non-zero aborts the whole script. The offending line, near the networking section, is a reachability probe:

```bash
# network is not available for a short while, wait for it
timeout 30s sh -c 'while ! ping -c1 -W1 connectivitycheck.gstatic.com >/dev/null 2>&1; do sleep 1; done'
```

The probe sends an Internet Control Message Protocol echo to `connectivitycheck.gstatic.com` and waits up to thirty seconds for a reply. On the network path between the sandbox and the internet, ICMP is filtered, but HTTP and HTTPS are not. The probe therefore always times out, returns 124, and `set -e` aborts the entire setup before the bulk pre-install of tools can run.

The sandbox container itself has working HTTPS connectivity. Invoking `mise` inside the half-configured sandbox triggered a download and installed mise, proving the network path is open for the protocols the tool installs actually use. The failure is purely that the probe chose a protocol the network does not pass.

A second sandbox creation, after the network was warm, reproduced the same exit 124, which rules out a transient first-boot race and confirms the probe as the cause. The minimal workaround is to tolerate the probe's failure, since HTTPS — which the installs need — works:

```bash
# local eval patch on the installed package's container-setup.sh:
.../locki/data/container-setup.sh:
  timeout 30s sh -c 'while ! ping ... connectivitycheck.gstatic.com ...; do sleep 1; done' || true
```

After this patch, a fresh sandbox's setup completed. The sandbox reported `SETUP_COMPLETE`, and the tools were preinstalled at the documented locations:

```text
/opt/locki/bin/low/mise      (mise v26.7.0)
/opt/locki/bin/high/node
/opt/locki/bin/high/uv
```

The upstream-quality fix is to probe with HTTPS instead of ICMP — for example, `curl -sf https://connectivitycheck.gstatic.com/generate_204` — or to guard the probe with `|| true` so that a filtered protocol does not abort the whole setup. The lesson generalizes: a reachability probe that assumes a specific protocol will fail on networks that filter that protocol, and under `set -e` an unguarded probe failure is fatal to the entire script. A connectivity check should test the protocol the system will actually use, or treat the check as advisory.

## Validation: file synchronization and the command bridge

With both failures fixed, the core guarantees of a Locki sandbox were validated directly.

A file written inside the sandbox appears on the host worktree. A command run in the sandbox created `sandbox-created.txt`; reading the same path on the host virtual machine's worktree returned the same content immediately. Locki mounts the worktree directory into the Lima virtual machine over the 9p filesystem — the QEMU command line contains `-virtfs local,mount_tag=...,path=/home/ubuntu/.local/share/locki/worktrees,security_model=none` — so writes in the sandbox traverse the container, the Incus disk device, the Lima virtual machine, and the 9p mount to the host virtual machine's filesystem without copying.

The command bridge, which scopes Git writes to a sandbox's own namespaced branch, works in both directions. A read — `git status` inside the sandbox — succeeded and reported the correct branch `untitled#locki-<id>`. A write — `git add` followed by `git commit` inside the sandbox — produced a new commit on the host worktree:

```text
host worktree: ~/.local/share/locki/worktrees/test-locki-locki-li4qmeya
  de180da add sandbox file
  96a2d1b init
  branch: untitled#locki-li4qmeya
```

The commit landed on the real worktree on the host virtual machine, not on a copy, and on the branch namespaced to the sandbox. This is the security property that makes Locki safe to run in `--dangerously-skip-permissions` mode: an agent in one sandbox cannot alter another sandbox's branch, the main branch, or unrelated stashes, because every Git write is validated against a grammar and scoped to the `#locki-<wt-id>` suffix before it reaches the host.

## Nested virtualization, two levels deep

The topology that ran is three levels of virtualization below Proxmox:

```text
Proxmox/KVM  →  host VM 9410 (locki-host)  →  QEMU (Lima)  →  Locki Fedora VM  →  Incus  →  sandbox container
```

Level one is the Proxmox host running the host virtual machine with `--cpu host`. Level two is Lima's QEMU inside that virtual machine, also using `-cpu host -machine q35,accel=kvm`. The Lima virtual machine itself has `/dev/kvm`:

```text
$ limactl shell locki -- ls -l /dev/kvm
crw-rw-rw-. 1 root kvm 10, 232 ... /dev/kvm
```

So two levels of nested virtualization function. The sandbox container, however, did not surface `/dev/kvm` — Incus did not pass the device through into the container, even though the Locki profile includes a `kvm` device with `required="false"`. This means a sandbox can run ordinary development work, but a sandbox that wants to run its own virtual machines would need the Incus device passthrough investigated. For Phase 1's purpose — evaluating whether Locki fits an operator's workflow — the absence of `/dev/kvm` in the sandbox is a characterization, not a blocker.

## Making the sandbox usable: an agent, a repository, and direct access

A sandbox that spawns and syncs files is not yet a tool an operator can use for real work. Three things remain: an agent that can run inside the sandbox, a real repository to work on, and a way to reach the host virtual machine that does not require a double Secure Shell jump through the Proxmox node.

The agent is the least work. Locki's `container-setup.sh` installs a shim at `/opt/locki/bin/low/claude` that auto-installs on first invocation. On Fedora it installs the official Claude Code package from the rpm repository at `downloads.claude.ai/claude-code/rpm/latest` via `dnf`; if `dnf` is absent it falls back to `npm:@anthropic-ai/claude-code` through mise. No manual installation is needed. The first `claude` call inside a fresh sandbox triggers the install and produces `2.1.235 (Claude Code)` at `/usr/bin/claude`.

The repository is cloned into the host virtual machine as an ordinary `git clone`. For this evaluation the target was `github.com/go-go-golems/glazed`, cloned to `~/glazed`. Running `locki x -n` inside that directory creates a sandbox — `irdph9p4` — and its worktree at `~/.local/share/locki/worktrees/glazed-locki-irdph9p4` on the branch `untitled#locki-irdph9p4`. Container setup completes (the Internet Control Message Protocol tolerance from the previous section is in place), and `claude --version` confirms the agent is invocable.

The one step that cannot be automated is the agent's own authentication. Claude reports `Not logged in · Please run /login`; the OAuth flow is interactive and requires a browser. The credential it writes lands in `~/.local/share/locki/home/.claude/`, which is mounted as `~/.claude` inside every sandbox. A single login therefore persists across all sandboxes — this is the structure Locki promises, and it holds. The login itself is the operator's to perform.

Direct access to the host virtual machine is the last friction. The cable modem blocks layer-three traffic to the virtual machine's media access control address, so every command had gone through the Proxmox node as a jump host: `ssh -t root@192.168.0.227 'ssh -t ubuntu@192.168.0.87'`. Two Secure Shell hops with forced terminal allocation is workable for a one-off upgrade but clumsy for a daily `locki ai` session. The node already ran Tailscale, so the host virtual machine joined the same tailnet:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --hostname=locki-host --accept-routes
```

The join is interactive — `tailscale up` blocks until the operator opens the printed `https://login.tailscale.com/a/...` URL and approves the device — and the tailnet it joins is determined by which account authenticates in the browser, not by any flag. Once joined, the host virtual machine is reachable directly: `ssh -t ubuntu@locki-host` resolves through MagicDNS and needs no jump host. With the agent auto-installing, the repository cloned, and direct access in place, the only remaining manual step is the one-time `claude /login`, after which `locki ai -m irdph9p4` opens a real session on glazed.

## Working rules

1. **When a Lima virtual machine fails to start, read `ha.stderr.log`, not Locki's output.** Locki reports a terse message; the QEMU error that explains it is in the Lima host-agent stderr log under `LIMA_HOME/locki/`.
2. **Put the host virtual machine's user in the `kvm` group before the first sandbox.** A cloud-init `--ciuser` virtual machine does not add the user to `kvm` by default, and Lima runs QEMU as that user. Without group membership, QEMU cannot open `/dev/kvm` and reports `Permission denied`.
3. **Find a cloud-init virtual machine's address by MAC scan when the guest agent is absent.** The Ubuntu cloud image does not install the QEMU guest agent, so `qm guest cmd` fails until it is installed manually; `nmap -sn | grep <MAC>` is the reliable fallback.
4. **A connectivity probe under `set -e` must test the protocol the system uses, or be advisory.** An unguarded `ping` aborts the entire script on networks where ICMP is filtered, even when HTTPS works. Probe with `curl` over HTTPS, or append `|| true`.
5. **Validate a sandbox by writing a file and committing on a branch.** File synchronization is confirmed by a write in the sandbox appearing on the host worktree; the command bridge is confirmed by a Git commit in the sandbox landing on the host worktree scoped to the `#locki-<wt-id>` branch. These two checks are the minimum that prove a Locki sandbox is real.
6. **Three levels of nested virtualization function, but the innermost container may not receive `/dev/kvm`.** Two levels (Proxmox → host VM → Lima VM) pass `/dev/kvm` through; the third (Incus → container) did not surface it here. Plan for sandboxes that need their own virtual machines to require extra Incus device configuration.
7. **Let the agent auto-install; do not preinstall it.** Locki's `claude` shim installs Claude Code from the dnf rpm on first invocation, so a sandbox is ready for `locki ai` with no manual setup. Resist the urge to install agents by hand; the shim is the supported path and it also handles the npm fallback.
8. **Persist agent login in the shared sandbox home, not per-sandbox.** `~/.local/share/locki/home/.claude/` is mounted as `~/.claude` in every sandbox, so one `claude /login` works across all sandboxes. Do not log in inside a single sandbox's container; that credential would not carry over.
9. **Join the host virtual machine to the same tailnet as the operator's machine for direct access.** The cable modem blocks layer-three to virtual media access control addresses; Tailscale bypasses it, and `ssh -t ubuntu@locki-host` over MagicDNS removes the double jump host. Which tailnet you join is chosen by which account authenticates in the browser, not by a flag.

## Related notes

- [[ARTICLE - Locki on Proxmox - Sandboxing AI Coding Agents on a Homelab Hypervisor]] — the architecture, the two-phase plan, the `VMService` port seam, and the 8.1.4 → 8.4 upgrade that preceded this execution.
- [[ARTICLE - Deploying k3s on Proxmox - A Technical Deep Dive]] — the prior crib-node deployment that established the `qm` workflow, the cable-modem layer-three restriction, and the jump-host access pattern reused here.
- Docmgr ticket: `ttmp/2026/08/18/LOCKI-PROXMOX-CRIB-2026-08-18--...` — diary steps 5–10 record the execution with exact commands and errors; `scripts/locki-run3-success.log` is the evidence of the completed setup, and `scripts/06-install-tailscale-host-vm.sh` plus the `90`–`94` helpers cover the agent, repository, and tailnet steps.
- Locki source (cloned reference): `/home/manuel/code/others/llms/locki/` — `src/locki/data/container-setup.sh` (the ICMP probe, line ~489, and the `claude` auto-install shim, line ~354) and `src/locki/services/vm.py` (the `ensure_running` that builds the Lima QEMU command).
