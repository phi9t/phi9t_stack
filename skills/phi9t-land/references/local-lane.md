# Cooperative local landing lane

Use [the packaged CLI](../scripts/land.py) when a repository lacks a suitable
guarded landing tool. Direct and queued landing use the same lane and lock.
Prefer an existing qualified repository or hosted integration service when its
authority and checks already fit. No background service or automatic push is added.

## Operating contract

This adapter supports cooperating local agents in a trusted POSIX repository,
Git with `rebase --no-update-refs` support, SHA-1 objects, and Python 3.9+ in a
managed uv environment. One designated clean mainline checkout belongs to the
integration owner. Other work happens in task worktrees. Explicit initialization
authorizes local landing under the configured acceptance policy; it does not
implement a human candidate-approval service. Do not use this adapter where
required review, signatures, or separate owner approval cannot be enforced by
that policy. Keep publication under the repository's existing process.

Git hooks, external filters and custom merge commands do not run during tool
operations. Acceptance must explicitly cover required repository checks. Raw
checkout bytes, executable modes and file types must match the verified commit.
Repositories needing LFS hydration, custom conversions, submodules or custom
merge behavior need their own qualified adapter. This is not a hostile-worker
sandbox, distributed lock, durable process supervisor or power-loss guarantee.

## Configure once

Use absolute paths below. `PYTHON` denotes the managed uv interpreter;
`LAND` denotes the installed `phi9t-land/scripts/land.py`. These are documentation
placeholders, not commands that set or replace system environment variables.

```text
PYTHON LAND --repo REPOSITORY init --mainline main \
  --destination MAINLINE_CHECKOUT --acknowledge-local-landing \
  --checks '[["/absolute/uv-env/bin/python","/absolute/oracle-v1.py","{worktree}"]]' \
  --timeout 300
```

The `--checks` value is a JSON array of argv arrays, executed without a shell.
Use an existing absolute executable and existing absolute files for acceptance
scripts and inputs. Keep them outside every worker-controlled source tree and
outside the repository; avoid candidate-controlled imports or mutable lookup
paths. `{worktree}` is the sole substitution token and must occupy an entire
argument. Inline or dynamically located check logic defeats file pinning; prefer
explicit immutable files. The operator owns the check's semantics and dependency
closure; the tool cannot prove that an arbitrary passing command is a good oracle.

File arguments are pinned by their resolved identity and SHA-256. Changes require
restoring the frozen policy or an explicit new configuration/qualification plan;
there is no silent policy refresh. Checks run in the isolated integration worktree.
Write build outputs, environments and caches outside it. Tracked, untracked or
ignored worktree changes invalidate the check. Use an Insula or permitted native
path as required; a Python launcher does not exempt arbitrary workloads.

## Submit and land

```text
PYTHON LAND --repo REPOSITORY submit --id task-a --candidate COMMIT \
  --base BASE_COMMIT --owner AGENT
PYTHON LAND --repo REPOSITORY submit --id task-b --candidate OTHER_COMMIT \
  --base OTHER_BASE --owner OTHER_AGENT --depends task-a
PYTHON LAND --repo REPOSITORY status
PYTHON LAND --repo REPOSITORY run --id task-a
PYTHON LAND --repo REPOSITORY run
```

`run --id` is the direct path. `run` processes queued eligible items in submission
order, with dependencies first. Both acquire the same nonblocking repository
lock; a competitor receives a refusal rather than entering another integration
lane. Configured checks inherit that lock so a surviving direct check keeps
another integrator out after parent death. Checks must not launch detached or
background processes; their full lifecycle needs a qualified execution owner.

Each submission pins a commit/base, owner and dependency versions. Moving its
source branch does not change the queued candidate. Preparation creates a
detached integration worktree; rebase never updates contributor refs. Conflicts
and failed checks retain artifacts and block that item. Independent eligible
items can continue. The final mainline/base check, fast-forward and receipt
remain serialized. Mainline movement invalidates the prepared result.

`status` uses a read-only database snapshot and remains available while the
integrator runs. It reports item state and any unresolved operation. The database also keeps
submission, verification, failure and landing events. State, pinned refs, logs and
attempt worktrees live in the repository's Git common directory under
`phi9t-land/` and `refs/phi9t-land/`. Preserve them as a set. No automatic worktree
deletion or garbage collection runs. The lock is `phi9t-land.lock` in that same
Git common directory, so task worktrees share one lane.

## Repair and recover

```text
PYTHON LAND --repo REPOSITORY retry --id task-a --candidate REPAIRED_COMMIT --base BASE
PYTHON LAND --repo REPOSITORY recover
PYTHON LAND --repo REPOSITORY recover --stopped
```

`retry` only updates a blocked item. Old candidate pins and attempt evidence remain.
An explicit retry rebinds dependency versions; dependent items cannot silently
inherit a changed parent's inputs. Cycles and unknown dependencies are refused.

An unresolved operation blocks all further landing. `recover` accepts a completed
landing only when mainline contains the candidate and reflog attribution matches
the recorded attempt and predecessor. It then records completion without another
merge. Ancestry alone is insufficient. Interrupted preparation/checks require the
operator to establish that owned work stopped before `recover --stopped`; the
item becomes blocked for inspection and explicit retry.

For an uncertain landing with no matching attribution, inspect the retained
operation and destination. Only after establishing that work stopped and landing
did not occur may an authorized operator use
`recover --stopped --not-landed`. The tool additionally requires a clean destination
at the original base. This is an explicit operator reconciliation, not an automatic
deduction from a missing acknowledgment. Otherwise retain the blocked lane.

Refusals use exit 2. A `run` with unfinished selected work uses exit 1;
`run --id` reports completion of that item separately from `queue_unfinished`.
Inspect each result because successful items can coexist with waiting or blocked items. Other
successful commands use exit 0. JSON output reports actual state. A missing
dependency, timeout or partial pass never becomes accepted delivery.

Qualification currently uses real Git/CLI processes on macOS. Linux portability,
power loss, network filesystems and noncooperating writers are not qualified by
that pass. Checks need their own environment/dependency/resource policy; the
per-check timeout is not a disk-output quota or full descendant containment.
