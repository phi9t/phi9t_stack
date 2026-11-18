# Git workspace hygiene

Use trunk/mainline-based development. Resolve the repository's actual mainline
from its instructions and Git configuration; do not assume its name is `main`.
Keep work small, coherent and short-lived. Land verified increments promptly
rather than accumulating a long-running branch or waiting for unrelated work.
Mainline landing is a mandatory coding-delivery step. Use
[land](../../phi9t-land/SKILL.md) for direct integration, a durable landing queue,
and salvage of interrupted or overlapping work. Unlanded work remains assigned
and delivery-incomplete; record an explicit blocker when integration cannot finish.

## Work in a worktree

Do actual changes in a task-owned Git worktree on a short-lived branch, including
recipe scripts, docs and skill edits. Read-only inspection needs no new worktree.
Inspect status, branch, base and worktree ownership first. Reuse a suitable
task-owned worktree when one exists; otherwise create one from current mainline.
Use the runtime's managed worktree tools when available. Follow the repository's
branch naming convention. Give concurrent writers separate worktrees/branches.

Keep the mainline checkout available for integration. Preserve user changes and
other agents' work; do not stash, reset or move them to manufacture a clean tree.
A worktree does not isolate ignored outputs or external resources automatically;
give builds, databases and temporary state explicit ownership as well.

## Integrate frequently and land linearly

Refresh mainline, then rebase the task branch onto its current tip. Resolve
conflicts in the task worktree and rerun affected checks on the rebased result.
Use cheap checks for early feedback and the real end-to-end path for final
acceptance of executable behavior. Rebase changes source identity; an earlier
verification receipt does not automatically qualify the rebased candidate.

Land through fast-forward integration only. Keep mainline history linear, with
no merge commits. Use the repository's required review, CI and publication path
while preserving that result. A local integration uses `git merge --ff-only`
against the verified task tip in a clean, appropriately owned mainline checkout.
If mainline moves, refresh, rebase and verify the affected result again. Never
force mainline backward or bypass a failed fast-forward to land stale work.

Rebase only task history that is safe to rewrite. Preserve other contributors'
commits and published history. A policy to land promptly does not authorize
force-pushing shared branches, bypassing required review or publishing outside
the task's authority. Report implementation, verification and landing separately.

After confirmed integration, retire the task worktree and branch when no longer
needed. Preserve uncommitted work and useful ignored artifacts before cleanup;
use recoverable managed archival when available. An open task or an unlanded
branch is not abandoned work merely because it is old.
