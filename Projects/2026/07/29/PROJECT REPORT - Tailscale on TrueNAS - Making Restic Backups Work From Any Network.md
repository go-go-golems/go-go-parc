---
title: "PROJECT REPORT - Tailscale on TrueNAS - Making Restic Backups Work From Any Network"
aliases:
  - Tailscale TrueNAS configuration
  - restic backup over Tailscale
  - TrueNAS SCALE Tailscale app setup
  - truenas-scale tailnet node
status: active
type: article
created: 2026-07-29
repo: /home/manuel/code/wesen/claw-stuff
related_ticket: BACKUP-SCOPE-2026-07-25
related_playbook: "[[PLAYBOOK - Restic Backups to the Crib NAS]]"
related_report: "[[PROJECT REPORT - Restic Backup Scope Design - From 1.7T Home to a 247G Recovery Unit]]"
tags:
  - article
  - project-report
  - backup
  - restic
  - tailscale
  - truenas
  - networking
  - infra
  - operations
---

# PROJECT REPORT - Tailscale on TrueNAS - Making Restic Backups Work From Any Network

A scheduled backup that only works on one network is not a scheduled backup. It is a backup that succeeds when the laptop is at home and silently fails when it is not. This report documents the installation of Tailscale directly on the TrueNAS SCALE virtual machine, the configuration that makes the restic SFTP transport reachable from any network, and the two failure modes that had to be resolved before the node appeared on the correct tailnet.

The crib backup system, documented in [[ARTICLE - Crib Backup - From Design to Operational Restic Baseline]] and scoped in [[PROJECT REPORT - Restic Backup Scope Design - From 1.7T Home to a 247G Recovery Unit]], uses SFTP over SSH to transfer encrypted restic snapshots from laptop `f` to the TrueNAS NAS at `192.168.0.25`. The SFTP preflight is fail-closed: if the NAS is unreachable, the backup aborts rather than writing to a wrong location. This design is correct for data integrity, but it means the backup cannot run unless the laptop is on the same LAN as the NAS. Two consecutive nightly timer runs failed with `ssh: connect to host 192.168.0.25 port 22: Network is unreachable` because the laptop was on a different network at 03:30.

The solution is to make the TrueNAS reachable from any network via Tailscale. Tailscale creates a WireGuard-based mesh network that assigns each node a stable `100.x.x.x` address reachable from any other node on the same tailnet, regardless of the underlying network. The TrueNAS SCALE community catalog includes a Tailscale application that runs the Tailscale daemon inside a Kubernetes pod managed by the TrueNAS app framework. Once configured, the TrueNAS receives a Tailscale address, and the restic environment file is updated to use the Tailscale hostname instead of the LAN IP.

> [!summary]
> - Tailscale was installed on TrueNAS SCALE 23.10.2 via the community catalog app (v1.0.51, bundling Tailscale 1.80.3).
> - The TrueNAS node `truenas-scale` joined the `go-go-golems.org.github` tailnet at Tailscale IPv4 `100.121.81.46`.
> - Two failure modes were resolved: cached state from a wrong-tailnet auth key, and `hostNetwork: false` preventing SSH access through the Tailscale IP.
> - The restic env file and both backup scripts were updated from `192.168.0.25` to `truenas-scale`.
> - A dry-run backup over Tailscale completed successfully: 244.4 GiB scope, 4.08 GiB delta, 6 minutes 55 seconds.
> - The nightly timer at 03:30 EDT now works from any network with Tailscale connectivity.

## 1. The network reachability problem

The restic backup system uses SFTP as its transport. The backup script performs a mandatory preflight before every run:

```bash
ssh -i "${HOME}/.ssh/id_restic_crib_f" \
  -o BatchMode=yes \
  -o ConnectTimeout=10 \
  backup-f@192.168.0.25 \
  'test -d /mnt/media-pool/backups/laptops/f-restic'
```

If this preflight fails, the script exits immediately. There is no fallback path. This is a deliberate design decision documented in `CRIB-BACKUP-01`: a prior TrueNAS outage demonstrated that a missing NFS mount can be silently replaced by an empty local directory, causing a backup to write to the wrong location while reporting success. SFTP fails closed. The connection either authenticates and opens the remote repository, or it fails.

The consequence is that the backup only runs when the laptop can reach `192.168.0.25`. On the home LAN, this is always true. On any other network — a coffee shop, a hotel, a cellular hotspot — the address is unreachable and the backup aborts. The systemd timer logs confirmed this:

```text
Jul 25 11:08:33 f restic-crib-backup[4179587]: ssh: connect to host 192.168.0.25 port 22: Network is unreachable
Jul 26 11:17:49 f restic-crib-backup[1834735]: ssh: connect to host 192.168.0.25 port 22: Network is unreachable
```

Two consecutive nightly runs failed. The laptop was not on the home network at 03:30 EDT on either night. The backup was not broken; it was correctly refusing to run. But a backup that only works at home is not adequate for a laptop that travels.

## 2. Why Tailscale and not a VPN or port forwarding

Three approaches exist for making the TrueNAS reachable from outside the home network:

| Approach | How it works | Why it was rejected |
|---|---|---|
| Port forwarding | Forward port 22 on the home router to `192.168.0.25:22` | Exposes SSH to the public internet; requires dynamic DNS; the home ISP may use CGNAT |
| Traditional VPN | Run WireGuard or OpenVPN on a home server | Requires a publicly reachable endpoint; same CGNAT problem; adds a single point of failure |
| Tailscale | WireGuard mesh with DERP relay coordination | No public ports needed; works through CGNAT; the laptop already runs Tailscale |

The laptop `f` was already a Tailscale node on the `go-go-golems.org.github` tailnet (`tail879302.ts.net`) with address `100.72.131.20`. Other nodes on the same tailnet included `pve` (the Proxmox host at `100.81.254.116`), `mimimi` (the Mac at `100.113.140.75`), and several k3s nodes. The TrueNAS was the only crib infrastructure component not on Tailscale.

Tailscale uses WireGuard for direct peer-to-peer connections when possible, and DERP (Designated Encrypted Relay for Packets) relay servers as a fallback when NAT prevents direct connections. No public ports need to be opened on the home router. This makes it suitable for networks behind CGNAT or restrictive firewalls.

## 3. The TrueNAS Tailscale application

TrueNAS SCALE 23.10.2 uses a Kubernetes-based (k3s) app system. The Tailscale application is available in the community catalog train.

### 3.1 Catalog verification

The catalog was verified via the TrueNAS middleware CLI (`midclt`) over admin SSH:

```bash
ssh admin@192.168.0.25 'ls /var/run/middleware/ix-applications/catalogs/github_com_truenas_charts_git_master/community/tailscale/'
```

Output:

```text
1.0.51
app_versions.json
item.yaml
```

The app bundles Tailscale v1.80.3 in a container image from `tailscale/tailscale`. The chart defines two networking modes controlled by configuration values:

| Configuration | Default | Effect |
|---|---|---|
| `tailscaleNetwork.hostNetwork` | `false` | Tailscale runs in the pod's network namespace; the Tailscale IP is not on the host |
| `tailscaleConfig.userspace` | `true` | Tailscale runs as non-root user 568 using userspace networking (no `/dev/net/tun`) |

### 3.2 The hostNetwork decision

The default configuration (`hostNetwork: false`, `userspace: true`) runs Tailscale inside the pod's isolated network namespace. The Tailscale `100.x.x.x` address is assigned to an interface inside the pod, not on the TrueNAS host. When a remote node connects to the TrueNAS Tailscale IP on port 22, the connection reaches the pod, not the host's SSH daemon. The pod does not run SSH, so the connection is refused:

```text
ssh: connect to host truenas-scale port 22: Connection refused
```

Setting `hostNetwork: true` places the Tailscale interface directly on the host's network namespace. The Tailscale IP becomes a host address, and port 22 on that IP reaches the host's SSH daemon. This is the configuration required for the restic SFTP transport to work.

When `hostNetwork: true` is set, the `userspace` option must be set to `false` as well. With `userspace: false`, Tailscale runs as root and mounts `/dev/net/tun` from the host to create a kernel WireGuard interface. The pod template confirms this:

```yaml
securityContext:
  runAsUser: 0
  runAsGroup: 0
  runAsNonRoot: false
  capabilities:
    add:
      - NET_ADMIN
      - NET_RAW
```

### 3.3 The auth key

Tailscale auth keys are generated from the Tailscale admin console at `https://login.tailscale.com/admin/settings/keys`. A key is specific to one tailnet. The key must be:

- **Reusable**: so the pod can re-authenticate after restarts without generating a new key each time
- **Non-ephemeral**: so the node is permanent, not cleaned up after going offline
- **From the correct tailnet**: this is the failure mode documented in section 5

## 4. Installation via midclt

The Tailscale app was installed via the TrueNAS middleware CLI from an operator workstation with admin SSH access to the TrueNAS. The installation creates a chart release named `tailscale` in the `ix-tailscale` namespace.

```bash
AUTHKEY="tskey-auth-..."

ssh admin@192.168.0.25 "midclt call chart.release.create '{
  \"release_name\": \"tailscale\",
  \"catalog\": \"TRUENAS\",
  \"train\": \"community\",
  \"item\": \"tailscale\",
  \"version\": \"1.0.51\",
  \"values\": {
    \"tailscaleConfig\": {
      \"authkey\": \"'\$AUTHKEY'\",
      \"hostname\": \"truenas-scale\",
      \"userspace\": false,
      \"authOnce\": true,
      \"acceptDns\": false,
      \"advertiseRoutes\": [],
      \"advertiseExitNode\": false,
      \"extraArgs\": []
    },
    \"tailscaleNetwork\": {
      \"hostNetwork\": true
    }
  }
}'"
```

The key configuration values:

| Value | Setting | Rationale |
|---|---|---|
| `authkey` | `tskey-auth-...` | Authenticates the node to the tailnet |
| `hostname` | `truenas-scale` | Lowercase, hyphenated; appears in `tailscale status` |
| `userspace` | `false` | Required for `hostNetwork: true`; runs as root with `/dev/net/tun` |
| `authOnce` | `true` | Do not re-authenticate on every restart |
| `acceptDns` | `false` | Keep TrueNAS DNS configuration unchanged |
| `hostNetwork` | `true` | Place Tailscale interface on host namespace so SSH port 22 is reachable |

After installation, the pod status was verified:

```bash
ssh admin@192.168.0.25 'midclt call chart.release.get_instance "tailscale" | jq "{status, pod_status}"'
```

```json
{
  "status": "ACTIVE",
  "pod_status": {"desired": 1, "available": 1}
}
```

## 5. Failure mode 1: cached state from a wrong tailnet

The first installation attempt used an auth key that was generated from a different tailnet than the one the laptop belongs to. The TrueNAS admin console showed the node as connected, but with the full domain `truenas-scale.beagle-duck.ts.net` — a different tailnet than the laptop's `tail879302.ts.net`. No node on the laptop's tailnet could see `truenas-scale`, because the node was on a different tailnet entirely.

### 5.1 Multiple tailnets under one account

A single Tailscale account (`wesen@github`) had access to multiple tailnets:

| Tailnet | Magic DNS suffix | Nodes visible |
|---|---|---|
| `go-go-golems.org.github` | `tail879302.ts.net` | `f`, `pve`, `mimimi`, `k3s-*` |
| `beagle-duck` | `beagle-duck.ts.net` | `truenas-scale` (wrong tailnet) |

Tailscale auth keys are tailnet-specific. A key generated while the `beagle-duck` tailnet is selected in the admin console cannot join a node to `go-go-golems.org.github`. The admin console has a tailnet selector, but it is not prominently displayed, and it is easy to generate a key from the wrong tailnet without realizing it.

### 5.2 The cached state secret

After generating a correct key from the `go-go-golems.org.github` tailnet and updating the app via `midclt call chart.release.update`, the node still did not appear on the correct tailnet. The reason was a cached Kubernetes state secret.

The Tailscale app stores its node state (node key, machine identity, tailnet association) in a Kubernetes secret named `tailscale-tailscale-secret` in the `ix-tailscale` namespace. When the app restarts with a new auth key, it reads the existing state secret and attempts to reuse the cached node identity. If the cached identity belongs to a different tailnet, the new auth key is rejected with `invalid key`, and the node remains on the old tailnet.

The log output confirmed this:

```text
boot: No authkey found in state Secret and TS_AUTHKEY not provided, login will be interactive if needed.
...
control: RegisterReq: got response; nodeKeyExpired=false, machineAuthorized=false; authURL=false
Received error: invalid key: API key k471TbhsjT11CNTRL not valid
```

The `No authkey found in state Secret` message means the pod found cached state and tried to use it instead of the new auth key. The `invalid key` error is the control server rejecting the old tailnet's key.

### 5.3 Resolution: complete deletion and reinstallation

Updating the auth key and deleting the pod was not sufficient because the state secret persisted. The resolution was to delete the entire chart release and reinstall from scratch:

```bash
# Delete the entire release (removes pod, secret, and all resources)
ssh admin@192.168.0.25 'midclt call chart.release.delete "tailscale"'

# Wait for cleanup
sleep 15

# Reinstall with the correct auth key
ssh admin@192.168.0.25 "midclt call chart.release.create '{...correct key...}'"

# Wait for the pod to start and authenticate
sleep 25
```

After the fresh installation, the node appeared on the correct tailnet:

```text
$ tailscale status | grep truenas
100.121.81.46   truenas-scale  wesen@  linux  -
```

The state secret was recreated at `2026-07-29T16:52:25Z`, confirming a fresh authentication with the new key.

## 6. Failure mode 2: hostNetwork and SSH reachability

After the node appeared on the correct tailnet, Tailscale ping succeeded but SSH to port 22 was refused:

```text
$ tailscale ping truenas-scale
pong from truenas-scale (100.121.81.46) via DERP(nyc) in 36ms

$ ssh -i ~/.ssh/id_restic_crib_f backup-f@truenas-scale
ssh: connect to host truenas-scale port 22: Connection refused
```

The cause was the `hostNetwork: false` default. With host networking disabled, the Tailscale interface lives inside the pod's network namespace. Port 22 on the Tailscale IP reaches the pod, not the host. The pod runs `tailscaled`, not `sshd`, so the connection is refused.

Setting `hostNetwork: true` via `chart.release.update` moved the Tailscale interface to the host's network namespace. After the pod redeployed, SSH reached the host's SSH daemon.

A secondary issue was SSH host key verification. The Tailscale IP presents the same host key as the LAN IP, but `ssh-keygen -R` and `ssh-keyscan` were needed to add the `truenas-scale` hostname to `known_hosts` because the laptop had previously only connected via `192.168.0.25`.

## 7. Updating the restic configuration

Three files contained the hardcoded LAN address `192.168.0.25`:

| File | Role | Change |
|---|---|---|
| `~/.config/restic/crib/env` | Restic environment (repository URL) | `backup-f@192.168.0.25` → `backup-f@truenas-scale` |
| `~/.local/bin/restic-crib-backup` | Scheduled backup script (preflight) | `backup-f@192.168.0.25` → `backup-f@truenas-scale` |
| `~/.local/bin/restic-crib-manual-full` | Manual full backup wrapper (preflight + backup) | `backup-f@192.168.0.25` → `backup-f@truenas-scale` |

The updated env file:

```text
RESTIC_REPOSITORY=sftp:backup-f@truenas-scale:/mnt/media-pool/backups/laptops/f-restic
RESTIC_PASSWORD_FILE=${HOME}/.config/restic/crib/password
RESTIC_CACHE_DIR=${HOME}/.cache/restic
RESTIC_EXCLUDE_FILE=${HOME}/.config/restic/crib/excludes
RESTIC_SFTP_ARGS="-i ${HOME}/.ssh/id_restic_crib_f -o BatchMode=yes -o IdentitiesOnly=yes"
```

The SSH host key for `truenas-scale` was added to `~/.ssh/known_hosts`:

```bash
ssh-keygen -R truenas-scale
ssh-keyscan -t ed25519,rsa,ecdsa truenas-scale >> ~/.ssh/known_hosts
```

## 8. Verification

### 8.1 SFTP preflight

```bash
ssh -i ~/.ssh/id_restic_crib_f -o BatchMode=yes -o IdentitiesOnly=yes \
  backup-f@truenas-scale 'test -d /mnt/media-pool/backups/laptops/f-restic && echo "REACHABLE"'
```

```text
REACHABLE: repository path exists
```

### 8.2 Restic snapshots over Tailscale

```bash
set -a; . ~/.config/restic/crib/env; set +a
restic -o "sftp.args=$RESTIC_SFTP_ARGS" snapshots
```

The command listed all 29 existing snapshots, confirming that the repository is accessible over Tailscale and that the restic password and SFTP arguments are correct.

### 8.3 Dry-run backup over Tailscale

```bash
restic -o "sftp.args=$RESTIC_SFTP_ARGS" backup /home/manuel \
  --one-file-system \
  --exclude-file "$RESTIC_EXCLUDE_FILE" \
  --dry-run \
  --tag laptop-f \
  --tag tailscale-test
```

```text
using parent snapshot 85ab676b

Files:       109217 new,  12784 changed, 3718075 unmodified
Dirs:         9614 new,  6042 changed, 637076 unmodified
Would add to the repository: 4.080 GiB (1.701 GiB stored)

processed 3840076 files, 244.438 GiB in 6:55
```

The dry-run completed in 6 minutes 55 seconds. The scope (244.4 GiB, 3.8 million files) matches the scope verified in the prior LAN-based dry-run (246.9 GiB). The difference is due to files added or modified between the two runs. The delta of 4.08 GiB (1.70 GiB stored) represents the new and changed data since the parent snapshot `85ab676b`.

### 8.4 Tailscale connectivity characteristics

The `tailscale ping` output showed connectivity via DERP relay:

```text
pong from truenas-scale (100.121.81.46) via DERP(nyc) in 36ms
```

DERP relay adds latency compared to a direct WireGuard connection. The 36ms round-trip through the New York City DERP relay is acceptable for the backup workload, which transfers data in bulk and is not latency-sensitive. If both nodes are on networks that allow direct UDP connections, Tailscale will establish a direct WireGuard tunnel automatically, reducing latency to the network round-trip time between the two endpoints.

## 9. The Tailscale node configuration

The final TrueNAS Tailscale node configuration:

| Property | Value |
|---|---|
| Hostname | `truenas-scale` |
| Tailscale IPv4 | `100.121.81.46` |
| Tailscale IPv6 | `fd7a:115c:a1e0::2f38:262a` |
| Full domain | `truenas-scale.tail879302.ts.net` |
| Tailnet | `go-go-golems.org.github` |
| Tailscale version | 1.80.3 |
| OS | Linux 6.1.74-production+truenas |
| App version | 1.0.51 (community catalog) |
| hostNetwork | true |
| userspace | false |
| authOnce | true |

## 10. Working rules

- A scheduled backup that only works on one network is not a scheduled backup. Transport reachability is a backup requirement, not an optimization.
- Tailscale on TrueNAS SCALE requires `hostNetwork: true` for the Tailscale IP to be reachable on host services like SSH. The default `hostNetwork: false` isolates the Tailscale interface inside the pod.
- When `hostNetwork: true` is set, `userspace` must be `false`. The pod runs as root with `NET_ADMIN` capability and `/dev/net/tun` mounted from the host.
- Tailscale auth keys are tailnet-specific. An account with multiple tailnets must generate the key while the correct tailnet is selected in the admin console.
- The Tailscale app caches node state in a Kubernetes secret. Changing the auth key via `chart.release.update` is not sufficient if the cached state belongs to a different tailnet. Delete the entire chart release and reinstall from scratch.
- The restic env file, the scheduled backup script, and the manual full backup wrapper all contain the NAS address. All three must be updated when switching from a LAN IP to a Tailscale hostname.
- SSH host key verification requires adding the Tailscale hostname to `known_hosts` even if the host key is the same as the LAN IP's, because `ssh` matches by the connection hostname.
- DERP relay connectivity (36ms via NYC) is acceptable for bulk backup transfers. Tailscale will upgrade to a direct WireGuard connection when both endpoints allow direct UDP.

## 11. Open questions and remaining work

1. **First scheduled run over Tailscale.** The nightly timer at 03:30 EDT has not yet fired since the Tailscale configuration was completed. Monitor the next run to confirm it succeeds from whatever network the laptop is on.

2. **macOS `mimimi-2` backup.** The Mac Lightroom backup documented in [[ARTICLE - Recoverable Mac Photo Backups with Restic TrueNAS and launchd]] also uses `192.168.0.25` as the NAS address. It should be updated to use `truenas-scale` so it also works over Tailscale.

3. **Direct WireGuard connection.** The current connection uses DERP relay. If both the laptop and the TrueNAS are on networks that allow direct UDP, Tailscale should establish a direct tunnel. Verify with `tailscale status` (look for `direct` instead of `via DERP`).

4. **Stale node cleanup.** The `beagle-duck` tailnet has a stale `truenas-scale` node from the first failed installation. It should be removed from the Tailscale admin console to avoid confusion.

5. **Offsite copy.** Tailscale solves the reachability problem but not the site-loss problem. If the home is lost, both the laptop and the TrueNAS are lost. A complete 3-2-1 design still requires an offsite copy of the restic repository.

## Evidence and implementation references

- **Related report:** [[PROJECT REPORT - Restic Backup Scope Design - From 1.7T Home to a 247G Recovery Unit]]
- **Playbook:** [[PLAYBOOK - Restic Backups to the Crib NAS]]
- **Prior implementations:**
  - [[ARTICLE - Crib Backup - From Design to Operational Restic Baseline]]
  - [[ARTICLE - Recoverable Mac Photo Backups with Restic TrueNAS and launchd]]
  - [[ARTICLE - TrueNAS Backup with Vault - A Systems Integration Case Study]]
- **Infra MOC:** [[Research/KB/Projects/infrastructure-and-release]]
- **TrueNAS app:** community catalog train, `tailscale` v1.0.51 (Tailscale 1.80.3)
- **Live configuration:**
  - `~/.config/restic/crib/env` — restic environment (uses `truenas-scale`)
  - `~/.local/bin/restic-crib-backup` — scheduled backup script (uses `truenas-scale`)
  - `~/.local/bin/restic-crib-manual-full` — manual full backup wrapper (uses `truenas-scale`)
- **Tailscale admin:** `https://login.tailscale.com/admin/machines` (tailnet: `go-go-golems.org.github`)
