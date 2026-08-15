---
title: Architecture Garden — dropcut-studio
aliases:
  - dropcut-studio architecture study
  - Makera Z1 / z1ctl control architecture
status: active
type: architecture-garden-project
created: 2026-08-14
analyzed: 2026-08-14
analysis_schema: architecture-garden-v1
repository: /home/manuel/workspaces/2026-08-11/cnc-control-dropcut/dropcut-studio
repository_remote: git@github.com:wesen/dropcut-studio
repository_branch: task/cnc-control-dropcut
repository_commit: 5f33ba1
repository_worktree: dirty (unpushed branch; 13 commits ahead of origin)
go_module: github.com/wesen/dropcut-studio/makera-z1-cli
tags:
  - architecture-garden
  - dropcut-studio
  - cnc
  - protocol
  - command-control
  - safety
  - go
related_files:
  - makera-z1-cli/pkg/makera/client.go
  - makera-z1-cli/pkg/makera/protocol.go
  - makera-z1-cli/pkg/makera/frame.go
  - makera-z1-cli/pkg/makera/safety.go
  - makera-z1-cli/pkg/makera/preflight.go
  - makera-z1-cli/pkg/makera/motion.go
  - makera-z1-cli/pkg/makera/jobctl.go
  - makera-z1-cli/docs/protocol.md
related_notes:
  - "[[Research/Software Architecture Garden/README|Software Architecture Garden]]"
  - "[[Research/Software Architecture Garden/dropcut-studio/designs/01 - Sentinel-Delimited Command Completion over an Ordered Line Queue]]"
---

# Architecture Garden — dropcut-studio

`dropcut-studio` is a TypeScript CAM monorepo with a nested Go controller
(`makera-z1-cli`) that commands a Makera Z1 CNC machine over a single TCP
connection. This Garden project studies the **communication / command-control
protocol** between the Go controller (`z1ctl`) and the machine firmware — not
the CAM compiler, the JavaScript scripting host, or the machining certificate,
which are covered by the repository's own docmgr tickets (MZ1-004 and the CAM
series).

The controller is better structured than a typical ad hoc CNC client: typed
motion operations, an explicit risk-class ladder, a no-retry rule for motion,
fresh preflight, a dead-man jog, and loopback-first web posture are all sound.
The reusable pattern documented here is the one that sits underneath all of
those and that is the most broadly portable to other command-control line
protocols: how a host that does **not** own a device's output stream still
delimits and correlates per-command replies.

> [!summary]
> - The controller speaks a framed binary protocol to the machine and uses an
>   **injected sentinel** (`echo \x04`) to mark the end of each command's
>   output, relying on the firmware's ordered line queue.
> - The pattern is portable to any command-control line protocol where the
>   host cannot frame the peer's replies directly (embedded serial shells,
>   GRBL/Smoothieware-derived firmware, U-Boot, Expect-style automation).
> - Its correctness hinges on one distinction: a **constant sentinel is a
>   delimiter, not a correlation identifier**. A correct design correlates by
>   value (a per-command nonce) or quarantines the session on any ambiguous
>   timeout — it never treats a timed-out exchange as silently resumable.

## Design entries

- [[Research/Software Architecture Garden/dropcut-studio/designs/01 - Sentinel-Delimited Command Completion over an Ordered Line Queue|01 — Sentinel-Delimited Command Completion over an Ordered Line Queue]]
- [[Research/Software Architecture Garden/dropcut-studio/designs/02 - Latched Safety Channel over a Lossy Inbound Queue|02 — Latched Safety Channel over a Lossy Inbound Queue]]
- [[Research/Software Architecture Garden/dropcut-studio/designs/03 - Dead-Man Keepalive - Fail-Safe Motion by Causal Inversion|03 — Dead-Man Keepalive: Fail-Safe Motion by Causal Inversion]]

## Source provenance

The detailed study behind this Garden project is a docmgr ticket, `MZ1-005`,
authored in the source repository's `ttmp/` tree (branch `task/cnc-control-
dropcut`, local commit `5f33ba1`, not yet pushed at analysis time). The Garden
entry is the cross-project distillation; the ticket is the full evidence-led
investigation. Where they disagree, the ticket has the deeper line-anchored
evidence and the Garden entry has the portable abstraction.
