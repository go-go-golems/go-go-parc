---
title: "MicroVM as Execution Boundary — How We Do It"
aliases:
  - microVM boundary
  - VM as execution boundary
  - host-mediated I/O
  - sandboxed execution
tags: [knowledge-base, tribal, vm, sandbox, wasm, firecracker, embedded, security]
status: active
type: knowledge-base
created: 2026-05-11
---

# MicroVM as Execution Boundary — How We Do It

> [!summary]
> A small virtual machine defines the execution boundary; the host mediates all I/O. We use this pattern across three very different scales: Firecracker microVMs on x86 for code sandboxing, WAMR (WebAssembly Micro Runtime) on ESP32-S3 for embedded extensibility, and pi-sandbox for coding agent isolation. The core insight is the same regardless of scale: the VM owns computation, the host owns everything else.

## The pattern

We run untrusted or semi-trusted code inside a small virtual machine. The host process creates the VM, provides API functions for side effects, and controls all communication between the VM and the outside world. The VM has no direct access to the filesystem, network, display, or peripherals unless the host explicitly provides it.

This pattern has three invariants:

1. **The VM is the execution boundary.** Code inside the VM cannot reach the host except through the provided API surface. This is true whether the VM is a KVM-backed Firecracker microVM, a WAMR interpreter on a microcontroller, or a goja runtime in a Go process.

2. **The host mediates all I/O.** Every file read, network request, display draw, or serial write goes through a host-provided function. The host decides whether to allow each operation. The host can log, rate-limit, filter, or deny any request.

3. **The host decides the API surface.** Different deployments expose different APIs to the same VM. A Firecracker microVM gets a network tap and a block device. A WAMR module on ESP32 gets console I/O and hardware access. A goja sandbox gets domain-specific functions. The VM doesn't know what it's missing.

## Why we do it this way

**MicroVMs provide strong isolation without heavy containerization.** A Firecracker microVM boots in ~125ms, has a ~5MB memory footprint, and provides KVM-level isolation. This is much lighter than a full container or VM while providing comparable security boundaries.

**WAMR provides embedded extensibility without recompilation.** On ESP32-S3, we embed Wasm modules in firmware and run them through WAMR's interpreter. This lets us extend device behavior without reflashing — the Wasm module is the extension point, and the firmware is the stable host.

**The pattern scales across orders of magnitude.** Firecracker VMs have megabytes of RAM and Linux kernels. WAMR on ESP32 has kilobytes and runs bare-metal. The goja runtime has Go's full standard library. But the architecture is the same: VM + host API + mediated I/O.

Alternatives we considered:
- **Container-based isolation** — Heavier boot times (~1s), larger memory footprint, shared kernel attack surface. Good for trusted workloads, insufficient for untrusted code.
- **Process-level isolation (setuid/chroot)** — No memory safety guarantee. A memory corruption bug in the guest can escape. Not suitable for adversarial code.
- **No isolation (in-process execution)** — Fastest but zero security. A bug in the guest crashes the host. Only acceptable for fully trusted code.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `2026-03-31--firecracker-vm` | `internal/vm/`, `internal/agent/` | Firecracker microVM creation, host-mediated secret delivery |
| `2026-04-17--pi-sandbox` | `internal/firecracker/`, `internal/agent/` | Pi coding agent sandbox: Firecracker + Proxmox + k3s control plane |
| `esp32-s3-m5/0082-...` | `main/wasm_module_runner.cpp`, `main/wasm_module_registry.cpp` | WAMR module loading, source-mode selection (embedded/ram/spiram) |

### Related PARC project reports

- [[PROJ - Firecracker VM - Guest Bring-Up, Host-Mediated Secrets, and Isolation Design]] — canonical x86 instance: KVM-backed microVM, host-mediated secret delivery, ext4 workspace artifacts
- [[PROJ - pi-sandbox - Sandboxed Pi Runner and Firecracker Research Guide]] — Firecracker-based coding agent sandbox on Proxmox + k3s
- [[PROJ - PaperS3 WAMR Debugging - Embedded Wasm Root Cause]] — embedded instance: WAMR on ESP32-S3, flash-mapped buffer mutability bug, reduction-ladder debugging

## Common mistakes

1. **Assuming the VM's source buffer is writable.** This is the bug that drove the PaperS3 WAMR debugging campaign. WAMR's interpreter loader assumes it can rewrite const strings in the source buffer. When the source comes from flash-mapped firmware (`EMBED_FILES`), those bytes are read-only. The loader's in-place mutation causes a bus fault or corrupts adjacent flash — but the visible crash happens later, when PSRAM is touched. The fix is to copy the Wasm binary to RAM before loading, or to force the loader's `reuse_const_strings` flag off. In the Firecracker world, the analogous mistake would be assuming the guest can write to the boot disk — the host must provide a writable overlay.

2. **Giving the VM more API surface than it needs.** The smallest secure VM is one that can do nothing. Every API function you add is an attack surface. In Firecracker, we provide only a network tap and a block device. In WAMR, we provide only `esp_console` I/O. In goja, we provide only domain-specific functions. If you find yourself adding "just one more" convenience function, stop and ask whether the guest really needs it.

3. **Confusing the VM's view of the world with the host's view.** The guest sees a filesystem, a network, or a serial port. The host sees a VM process, a buffer, or a UART. These are different abstraction levels. In Firecracker, the guest sees ext4 on a block device; the host sees a file-backed sparse image. In WAMR, the guest sees Wasm linear memory; the host sees an ESP32 heap allocation. Bugs happen when host code assumes the guest's view is the same as its own.

4. **Not handling VM exit/crash gracefully.** When the VM crashes or exits, the host must clean up. Firecracker VMs release their network tap and block device. WAMR modules free their runtime state. goja runtimes release their Go allocations. If the host doesn't clean up on VM exit, resources leak — and on embedded hardware, that means memory exhaustion with no recovery.

5. **Ignoring the performance cost of mediated I/O.** Every I/O operation crosses the VM boundary. On Firecracker, this is a KVM exit (~1μs). On WAMR, this is a host function call (~1μs). On goja, this is a Go function call (~100ns). For most workloads, this is negligible. But for I/O-heavy workloads (like streaming a bitmap to a thermal printer at 9600 baud), the boundary crossing overhead can cause gaps that corrupt output. The SToMS3R firmware's "buffer-full-body-before-UART" pattern exists because the HTTP-read-then-UART-write approach introduced gaps at the VM boundary.

## Variations

- **Firecracker microVM** (Firecracker VM, pi-sandbox). The VM is a full Linux kernel running under KVM. The host creates the VM with `firecracker --config-file`, provides a network tap and block device, and monitors the VM process. The guest runs untrusted code with kernel-level isolation. Boot time ~125ms, memory ~5MB.

- **WAMR embedded runtime** (PaperS3 WAMR). The VM is a WebAssembly interpreter running on an ESP32-S3 microcontroller. The host (firmware) creates the WAMR runtime, loads the Wasm module, and provides host functions for console I/O. The guest runs extension code with interpreter-level isolation. No OS, no KVM, no memory protection — the boundary is the Wasm sandbox model.

- **goja runtime** (see [[Tribal/goja-execution-model]]). The VM is a JavaScript interpreter running in a Go process. The host creates the goja runtime, installs API objects via `vm.Set()`, and mediates all side effects. The guest runs domain scripts with Go-process-level isolation. This is the lightest variation — the VM shares the host's memory and address space.
