# Proxmox Locki Setup Comparison

- URL: https://chatgpt.com/c/6a845e40-d528-83ea-9a80-60ed290fd26f
- Created: 2026-08-18T13:29:38.965Z

---

> I have a proxmox server, and I kind of want to use https://github.com/janpokorny/locki on it (so I don't need qemu or don't need a linux VM). Would that make sense, or should I just provision a linux in proxmox and then run qemu and their virtualization on there?

I’m checking Locki’s actual execution model and what it expects from the host, then I’ll compare that with Proxmox’s KVM/LXC constraints. The key question is whether Locki can safely own `/dev/kvm` and its networking/storage pieces directly on the Proxmox host.

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/get_repo","args":{"repository_full_name":"janpokorny/locki"}}
```

<details><summary>💭 Thinking</summary>

**Clarifying virtualization layers**

I’m distinguishing Locki’s required QEMU layer from Proxmox’s own virtualization. Running Locki inside a Proxmox VM may work with nested virtualization enabled, but a dedicated Linux VM is safer than installing it directly on the Proxmox host.

**Clarified virtualization layers**

**Inspected Locki virtualization architecture, deployment, and VM backend code**

</details>

The repo answers one important part: on Linux, Locki does **not** replace QEMU. It explicitly checks for `qemu-system-<arch>` and `qemu-img`, then uses Lima to create one Fedora VM; the per-agent sandboxes are Incus containers inside that VM. 

So your choice is really **Locki directly on the PVE host** vs **Proxmox VM → nested KVM/QEMU → Locki’s Lima VM → Incus containers**.

```json
{"system1_search_query":[{"q":"site:pve.proxmox.com pve nested virtualization KVM documentation"},{"q":"site:pve.proxmox.com Proxmox VE host install additional software Debian packages recommendation"},{"q":"site:lima-vm.io Linux QEMU KVM acceleration Lima documentation"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"JanPokorny/locki","path":"pyproject.toml"}}
```

<details><summary>💭 Thinking</summary>

**Assessing deployment boundaries**

I’m checking where Locki’s control components, mounts, credentials, and agent workloads run. Direct installation on Proxmox could expose the hypervisor, while a Linux VM provides a cleaner isolation boundary, despite requiring nested virtualization.

**Assessed deployment boundaries**

**Evaluated Locki requirements and searched compatibility issues for Proxmox environments**

</details>

There’s another strong reason not to put it on the Proxmox node: Locki currently sizes its Lima VM to **all CPUs and essentially all RAM visible to the Locki host**, with a 200 GiB sparse disk. On bare PVE, that means it will size itself against the entire hypervisor node rather than a controlled guest allocation. 

Inside a dedicated Proxmox VM, that behavior is naturally capped by the vCPU/RAM you assign to that VM.

```json
{"system2_search_query":[{"q":"site:lima-vm.io QEMU memory ballooning Lima dynamic memory Linux"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"query":"memory cpus disk VMService config","repository_name":"JanPokorny/locki","topn":20}}
```

<details><summary>💭 Thinking</summary>

**Chose Proxmox VM deployment for Locki**

</details>

I would **provision a dedicated Linux VM in Proxmox and run Locki inside that VM with nested KVM enabled**.

The main correction is that **running Locki directly on Proxmox does not eliminate QEMU**. On Linux, Locki explicitly refuses to start unless `qemu-system-<arch>` and `qemu-img` are available, and Lima uses QEMU as its Linux virtualization backend. fileciteturn7file0L2-L2 Lima's own documentation confirms QEMU is the Linux VM driver. citeturn566929search2turn566929search1

So the recommended layout is:

```text
Bare metal
└── Proxmox / KVM                 L0
    └── Debian/Ubuntu VM          L1
        └── Locki
            └── Lima/QEMU VM      L2
                ├── Incus sandbox 1
                ├── Incus sandbox 2
                └── Incus sandbox N
```

That may look like a lot of nesting, but Locki only creates **one** Lima VM; its individual agent sandboxes are lightweight Incus containers inside that VM. That's precisely its architecture. fileciteturn1file0L2-L2 Nested KVM is a standard supported KVM configuration, provided the L1 VM is given VMX/SVM capabilities; the kernel documentation specifically recommends host CPU passthrough for this case. citeturn188352search2turn188352search0

### Why I wouldn't run Locki on the PVE host

The biggest issue isn't that it couldn't work. Proxmox is Debian underneath, so it probably can. The problem is **failure-domain separation**.

Locki runs a host daemon, manages mounts/worktrees, invokes QEMU/Lima, creates disk images, performs networking/port forwarding, and generally expects to be installed on a developer workstation. I wouldn't put that software stack directly into the same OS responsible for your hypervisor, storage, networking, backups, and every other VM.

There's also a particularly relevant detail in Locki's current implementation: when creating its Lima VM, it sets:

```python
"memory": <essentially all host RAM>,
"cpus": os.cpu_count(),
"disk": "200GiB",
```

There doesn't appear to be a user-facing resource override in the current code. fileciteturn7file0L2-L2 On the **Proxmox host**, "host RAM/CPU" means your entire physical server. Inside a dedicated VM, at least Locki's view of the machine is constrained to the resources you've allocated to that VM.

I'd actually consider that enough reason by itself not to run it on PVE bare metal.

| Approach | Would it work? | Isolation | Complexity | My choice |
|---|---:|---:|---:|---:|
| Locki directly on PVE | Probably | Poor | Low | ❌ |
| PVE LXC + `/dev/kvm` passthrough | Probably, with tweaking | Medium/poor | High | ⚠️ |
| **PVE Linux VM + nested KVM** | **Yes** | **Good** | Moderate | **✅** |

The LXC option is tempting because you could expose the host's `/dev/kvm` to a container and let Locki's QEMU use KVM directly. But you'd likely need nesting/device passthrough and possibly AppArmor/cgroup changes. Proxmox itself warns that enabling LXC nesting exposes host `/proc` and `/sys` information to the container. citeturn312420search3 For something whose entire purpose is sandboxing potentially unruly AI agents, weakening the outer isolation layer seems counterproductive.

### How I'd configure the VM

Assuming an x86_64 Proxmox machine, create something like a Debian 13 or Ubuntu VM and set the **CPU type to `host`**. Proxmox supports host CPU passthrough, and KVM's nested-virtualization docs recommend it because it makes VMX/SVM available to the guest hypervisor. citeturn312420search2turn188352search2

On the PVE host, first check nesting:

```bash
# Intel
cat /sys/module/kvm_intel/parameters/nested

# AMD
cat /sys/module/kvm_amd/parameters/nested
```

You want `Y`/`1`. Modern Linux kernels normally enable nested KVM by default, although distributions can override it. citeturn188352search2

Then configure the Proxmox VM:

```bash
qm set <VMID> --cpu host
```

Inside that Linux VM, verify:

```bash
grep -E 'vmx|svm' /proc/cpuinfo | head
ls -l /dev/kvm
```

Then install QEMU there—for Debian/Ubuntu, roughly:

```bash
sudo apt install qemu-system-x86 qemu-utils
```

and install Locki normally:

```bash
uv tool install locki
```

At that point Locki's Lima QEMU instance should be able to use **nested KVM acceleration** rather than falling back to painfully slow software emulation.

One caveat I'd pay attention to is Locki assigning its inner Lima VM all the RAM it sees. If you're going to push it hard, I would consider a tiny local patch to Locki's `vm.py` to reserve perhaps 1–2 GiB for the outer Linux VM, e.g. give Lima 14 GiB in a 16 GiB VM rather than 16 GiB. Currently it appears hardcoded rather than configurable. fileciteturn7file0L2-L2

**So, yes: accept the slightly silly-looking nested setup.** Proxmox → Linux VM → Locki/Lima VM → Incus is cleaner than turning your Proxmox node itself into the Locki workstation. The additional VM boundary is doing useful work here, and nested KVM makes the performance cost much less severe than "QEMU inside QEMU" sounds.


---

> ok but how hard would it be to adapt locki to use proxmox as backend and would I gain benefits from it?

It’s feasible, but the effort depends on what you mean by “Proxmox backend.” I’m checking where Locki assumes Lima specifically, because a clean backend swap is very different from just replacing the one VM launcher.

```json
{"paths":["GitHub"],"query":"fetch_file"}
```

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"JanPokorny/locki","path":"src/locki/services/container.py"}}
```

<details><summary>💭 Thinking</summary>

**Fetched Proxmox container, bridge, daemon, and Locki integration files**

</details>

```json
{"system2_search_query":[{"q":"site:pve.proxmox.com pve qm virtiofs shared directory VM documentation"},{"q":"site:pve.proxmox.com Proxmox VE API authentication API token documentation"},{"q":"site:pve.proxmox.com qm guest exec qemu guest agent documentation Proxmox VE"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Assessing Proxmox integration**

I’m examining whether the existing VM interface can stay unchanged while replacing Lima centrally. The main challenge is preserving host worktree mounts, especially when Proxmox is remote. A permanent Linux guest running Incus may be the simplest design.

**Assessed Proxmox integration**

**Searched 1 website**

</details>

The important split is becoming clear: **replacing Lima while keeping Locki’s single-VM + Incus architecture is fairly contained; replacing Incus too and making each sandbox a Proxmox VM is a much larger rewrite.** The first option is the one I’d consider.

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"JanPokorny/locki","path":"src/locki/data/vm-setup.sh","start_line":1,"end_line":260}}
```

<details><summary>💭 Thinking</summary>

**Inspected VM setup assumptions**

</details>

```json
{"system2_search_query":[{"q":"site:pve.proxmox.com/pve-docs-8/qm.1.html \"qm clone\""},{"q":"site:pve.proxmox.com/pve-docs-8/qm.1.html \"qm template\""},{"q":"site:pve.proxmox.com/pve-docs-8/qm.1.html \"guest exec\""}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Refining the backend**

I’m narrowing the design: preserving the existing VM interface should leave container logic mostly unchanged. A persistent Proxmox guest running Incus seems practical, while per-sandbox guest provisioning adds complexity. The key unresolved issue remains reliably sharing worktrees and sandbox-home data.

**Searched 1 website**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"JanPokorny/locki","path":"src/locki/data/locki-ssh-config"}}
```

<details><summary>💭 Thinking</summary>

**Inspected host gateway and reachability configurations for binding**

</details>

```json
{"system1_search_query":[{"q":"site:git.proxmox.com \"virtiofs\" qemu-server Proxmox"},{"q":"site:pve.proxmox.com \"dir mapping\" \"virtiofs\""},{"q":"site:pve.proxmox.com \"virtiofsd\" Proxmox VE"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searching 10 websites**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"repository_name":"JanPokorny/locki","query":"from locki.services.vm import","topn":20}}
```

<details><summary>💭 Thinking</summary>

**Evaluated Locki’s Proxmox VirtioFS integration and Lima port-forwarding coupling**

</details>

Yes. **If you replace only Lima with a Proxmox-managed VM and leave Incus intact, this is a fairly reasonable adaptation.** I would not replace the Incus-per-sandbox layer with Proxmox VMs.

### How difficult?

My estimate:

| Version | Effort | Verdict |
|---|---:|---|
| Hack for your own PVE node | ~1–2 days | Quite feasible |
| Clean configurable backend | ~3–7 days | Reasonable project |
| Upstream-quality + tests/docs | ~1–2 weeks | More substantial |
| Proxmox VM per Locki sandbox | ~1–3+ weeks | Probably wrong design |

Locki already has a surprisingly convenient seam for this. `VMService` owns the outer VM operations—status, execute commands, interactive shell, copy files, start, stop, delete—and the Incus sandbox code mostly talks to the outer VM through that service. fileciteturn7file0L2-L2 fileciteturn11file0L2-L2

So conceptually you'd turn:

```text
Locki
  │
  ├── LimaVMBackend
  │      └── QEMU
  │
  └── ProxmoxVMBackend
         └── PVE VM
         
             ↓ either way

       Fedora VM
          │
          └── Incus
              ├── sandbox A
              ├── sandbox B
              └── sandbox C
```

That is much less invasive than it sounds.

### And yes, there are real benefits

Your current nested setup would be:

```text
Proxmox/KVM
   ↓
Linux VM
   ↓
QEMU/KVM (Lima)
   ↓
Locki Fedora VM
   ↓
Incus
   ↓
sandbox
```

With a PVE backend:

```text
Proxmox/KVM
   ↓
Locki Fedora VM
   ↓
Incus
   ↓
sandbox
```

That removes an entire VM layer.

This gets particularly attractive if a sandbox itself wants KVM. Locki deliberately passes `/dev/kvm` and `/dev/vhost-net` into its Incus sandboxes when available. fileciteturn15file0L2-L2 With the nested-Locki arrangement, you're asking virtualization extensions to pass through PVE → Linux VM → Lima VM → sandbox. With PVE directly hosting the Locki VM, you're only doing PVE → Locki VM → sandbox VM.

You'd also get Proxmox-native allocation, monitoring and lifecycle management. Proxmox exposes its management functionality through CLI and REST APIs, including VM/storage/network management, so Locki would no longer need to own QEMU itself. citeturn333049search0turn333049search4

And PVE can use scoped API tokens rather than giving Locki blanket control of the hypervisor; Proxmox supports privilege-separated API tokens whose permissions are a subset of the backing user's permissions. citeturn333049search17

### The good news: file sharing is now much easier

This would have been considerably more annoying on older PVE versions because Locki depends heavily on host directories appearing inside its VM.

Currently Lima mounts:

```text
Locki host                                  Locki VM

~/.local/share/locki/worktrees/...  ──────> same path
~/.local/share/locki/home/           ──────> /root/.locki/home
```

Those mounts are fundamental: the actual code is edited in a host-side Git worktree while the container sees the same files. fileciteturn7file0L2-L2

**Proxmox VE 8.4 added native virtiofs directory sharing between the PVE host and VMs.** citeturn391676search11 That's almost exactly what you need here.

If Locki itself runs on the PVE node, you could have something like:

```text
PVE host
│
├── /home/you/.local/share/locki/worktrees/
│        │
│        └──── virtiofs ────► Fedora VM, same path
│
├── /home/you/.local/share/locki/home/
│        │
│        └──── virtiofs ────► /root/.locki/home
│
└── Locki Python CLI
         │
         └──── Proxmox API ──► manage VM 9410
```

That is a pretty clean architecture.

### There are three annoying bits

This is why I wouldn't call it a two-hour patch.

First, Locki's guest-to-host command bridge has a Lima-specific assumption:

```text
Host locki-proxy
    HostName host.lima.internal
```

fileciteturn16file0L1-L6

And Locki deliberately has that SSH bridge listen only on `127.0.0.1` on the host. fileciteturn18file0L2-L2

You don't want to solve that by casually changing it to:

```python
host="0.0.0.0"
```

on your Proxmox node.

I'd instead make the VM backend establish a small SSH tunnel. Then the Incus containers talk to the PVE-managed Fedora VM, and that connection gets tunneled back to Locki's localhost-only command bridge.

Second, port forwarding needs adjustment. `locki port-forward` currently installs an Incus proxy device **inside the Locki VM**. fileciteturn20file0L2-L2 With a normal bridged PVE VM, `0.0.0.0:8080` there means:

```text
Locki VM IP:8080
```

rather than necessarily:

```text
PVE host localhost:8080
```

Again, an SSH tunnel is probably the clean solution.

Third, VM creation/provisioning needs translating from Lima config to Proxmox. Fortunately, most of Locki's interesting guest configuration isn't Lima-specific at all: `vm-setup.sh` installs/configures Incus, btrfs, nginx caches, BuildKit, networking, and so forth inside Fedora. fileciteturn15file0L2-L2

I'd therefore make a **Fedora Proxmox template**, clone it once for Locki, and execute the existing setup script. No reason to rewrite that part.

## What I would actually implement

I wouldn't call it `ProxmoxVMService` initially. I'd refactor Locki into a generic **external/remote VM backend**.

Something approximately like:

```python
class VMBackend(Protocol):
    def status(self) -> str | None: ...
    def ensure_running(self) -> None: ...

    def run(
        self,
        command: list[str],
        ...
    ) -> CompletedProcess: ...

    def shell(
        self,
        command: list[str],
        ...
    ) -> CompletedProcess: ...

    def copy_into(
        self,
        src: Path,
        dst: str,
        ...
    ) -> None: ...

    def stop(self, ...): ...
    def delete(self): ...
```

Then:

```text
VMBackend
├── LimaBackend
└── SSHBackend
```

And configure the SSH backend as:

```toml
[vm]
backend = "ssh"
host = "locki-vm"
```

Proxmox itself can then be a thin lifecycle provider:

```text
              ┌──────── Proxmox API
              │         start/stop/create VM
              ▼
Locki ──────► Fedora VM
       SSH     │
               └── Incus
```

That's actually more useful upstream than baking Proxmox into Locki. The same backend could support libvirt, VMware, an existing physical Linux box, a remote server, etc.

Then a small optional `ProxmoxLifecycle` component could provision/start/stop/delete the machine via PVE's REST API. Proxmox explicitly provides that API for third-party management tooling. citeturn333049search18

### Would *I* bother?

If you just want to try Locki this weekend: **no**. Put it in the nested VM and see whether you even like Locki first.

If you expect to use Locki heavily on this Proxmox server: **yes, I think the backend is worth building.** In particular, you get:

- one less virtualization layer;
- no QEMU/Lima installation in an intermediate Linux VM;
- simpler nested-KVM topology;
- explicit PVE CPU/RAM/disk limits;
- native PVE VM visibility/monitoring;
- direct use of your PVE storage;
- host↔guest worktrees through native virtiofs on modern PVE;
- potentially a reusable generic remote-VM backend rather than a Proxmox-specific fork.

I **would not** do Proxmox-VM-per-sandbox. Locki's central design advantage is one real VM providing the security boundary and cheap Incus containers underneath it. Its setup includes shared caches and btrfs storage specifically to make many disposable sandboxes inexpensive. fileciteturn1file0L2-L2 Turning every sandbox into a PVE VM throws much of that design away.

So the sweet spot is **PVE owns Locki's one Fedora VM; Locki continues owning Incus inside it.** That's a technically sensible modification rather than just a novelty.

