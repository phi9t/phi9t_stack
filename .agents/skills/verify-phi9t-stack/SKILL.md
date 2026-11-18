---
name: verify-phi9t-stack
description: "Verify changes to phi9t_stack packages, installation, migration or recovery using this repository's isolated behavior map."
---

# Verify this repository

Read the [behavior map](../../../docs/verification.md). Prepare the pinned source
environment with `uv sync --locked`, then run `./scripts/verify.sh` from the
repository root. It owns format, lint, scoped types, shell lint and behavior
checks. Exercise the affected journeys through the actual CLI
in owned temporary targets. Keep commands and evidence outside those targets.
A complete audit covers every declared row; a narrower pass names its coverage.
For dogfooding, also follow the [full product surface contract](../../../docs/dogfooding.md):
method trials, runtime discovery and external qualification stay distinct from
the source gate's local executable coverage.

Inspect the candidate's changes and selected runtime before execution. For
packaging changes, install this checkout's complete selected catalog and inspect
bytes, modes and local resource resolution. For recovery or migration changes,
exercise valid and rejected state and inspect preserved files. Retain the failed
case as well as the successful one.

Report the exact source identity, commands, exits, observations and cleanup.
Keep runtime discovery separate from local file verification. Rerun the
relevant checks for every candidate; earlier receipts do not qualify it.
