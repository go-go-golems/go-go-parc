---
title: "TTC MCP follow-up: confirmation CSP correction committed"
type: article
created: 2026-09-07
status: complete
repo: /home/manuel/code/ttc/ttc
tags:
  - project-report
  - mcp
  - oauth
publish: false
---

# Confirmation CSP correction committed

The WordPress CSP correction described as staged in [[PROJECT REPORT - Building the TTC MCP Connector - Employee Authority Shared SQL and Browser Verification]] is now committed in the TTC repository as **`fd59d991c`**, with message `fix: allow the validated MCP callback in the confirmation page CSP`.

The operator explicitly authorized bypassing the failing hooks for this one checkpoint. The override applied only to the commit command; persistent hook configuration was not changed. The original report and its exact patch remain historical evidence of the implementation and validation before that approval.

The code is the same correction already verified by Chromium, the operator, four real WordPress tests with 36 assertions, and focused ECS/Psalm checks. It sets the validated callback-origin form-action policy on the GET document containing the confirmation form as well as its POST response. No new behavior was introduced during this checkpoint.

The installed full PHP tooling limitations remain. No TTC source push, MCP deployment or dependency release was performed. This follow-up updates the source-management status of the report, not its deployment status.
