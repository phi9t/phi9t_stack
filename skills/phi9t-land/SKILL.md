---
name: phi9t-land
description: "Salvage useful task code and deliver it to mainline through verified rebase and fast-forward integration, directly or through a landing queue. Use to finish coding work or recover interrupted and overlapping branches."
---

# Land useful work on mainline

Coding delivery includes mainline integration. A commit, green branch, review
packet or queue entry is an intermediate result, not completed delivery. Follow
[workspace hygiene](../phi9t/references/workspaces.md), repository requirements
and existing user authorization. Respect explicit branch-only or review-only
requests. Publication and release retain their separate authority.

## Resolve and preserve the candidate

Identify the task, actual mainline, exact source candidate, base, dependencies
and required acceptance. Inspect the complete diff and worktree ownership. For
interrupted, dirty or overlapping work, use [salvage](references/salvage.md) first.
Preserve user work and stage only explicit task paths. Keep source provenance
and the evidence that establishes what is ready.

## Choose a landing path

The agent determines the landing path from current repository state and existing
policy; this is a routine execution decision, not a question to delegate to the
human. Follow an explicitly required repository path. Otherwise default to
direct serialized landing for one ready candidate with satisfied dependencies,
checks and authority, and no competing integration owner.

Choose the existing queue when candidates compete, dependency order needs
coordination, another owner is integrating, or required checks/review are pending.
State the selected path and reason briefly, then execute it. Reassess as state
changes: a ready queue item should be drained promptly; a direct attempt that
encounters contention should join the coordinated path. Escalate only a material
policy or authority conflict, not the mechanics of choosing a path.

Without a queue, a durable record in the existing tracker suffices; do not build
a daemon or scheduler merely to land code. A tracker is not a concurrency lock.
For a repository without a qualified landing tool, use the
[cooperative local lane](references/local-lane.md), driven by its
[packaged CLI](scripts/land.py). Both direct and queued paths share its lock,
immutable candidates, pinned checks and recovery journal. Initialize it only
when its explicit local authority contract fits the repository.

A queued item identifies its owner, task, candidate/base, destination, dependency
order, verification evidence, authority, state and next action. Existing fields
or clear prose suffice. Distinguish ready, integrating, landed, blocked and
superseded work. A queued item retains an accountable owner and unfinished work.

## Verify and fast-forward

One integration owner accepts and promotes each candidate against current
mainline; workers may create their own commits. Check semantic compatibility,
not just clean merging or separate worker passes. Return defects to their owner
when available, or preserve provenance for an owned repair. Route changes to
intended behavior to the appropriate decision-maker instead of silently changing
the contract to make integration pass. Rebase
safe-to-rewrite task history and resolve conflicts in its worktree. When published
history must remain intact, construct a new owned integration candidate with
source provenance instead of rewriting someone else's branch. Preserve useful
changes from every contributor and review the assembled diff.

Run required checks on the exact integrated result. Use cheap checks for early
signals and real end-to-end verification for final executable acceptance, following
[verify](../phi9t-verify/SKILL.md). Keep required review and authority bound to the
actual candidate. A changed candidate/base needs refreshed evidence and any
candidate-specific approval required by the repository.

Fast-forward mainline through its landing tool or `git merge --ff-only` in a
clean, appropriately owned integration checkout. Serialize destination changes.
If mainline moves, refresh, rebase and reverify before retrying. Never force
mainline or bypass failed gates. Push only when publication is authorized;
local landing and remote publication are distinct outcomes.

## Close the delivery loop

Confirm the accepted commit is reachable from mainline and check the delivered
tree and required behavior. Record landing identity and queue/ticket outcome.
If receipt writing fails after landing, reconcile actual state rather than apply
the patch again. Retire worktrees only after safe retention and closure.

Continue safe, authorized repairs until landing succeeds. If required authority,
access or checks prevent landing, retain a concrete queued/blocked candidate with
the exact blocker, evidence, owner and next resolving action. Report delivery as
incomplete. A mandate to land does not make broken or unverified code acceptable.
