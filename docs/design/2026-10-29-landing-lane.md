# Select a robust landing mechanism

Goal: get useful agent work to local mainline without losing concurrent work,
accepting stale evidence or repeating a landing after interruption. Compare paths
by observable ownership and recovery behavior, not how elaborate they look.

| Option | Strength | Unresolved fault | Decision |
|---|---|---|---|
| Bare rebase and fast-forward | Small, native Git; rejects divergent fast-forwards | No check/subject binding, queue ownership or interrupted-operation record | Insufficient by itself; retain as final Git operation |
| Tracker plus named coordinator | Good human visibility and dependency discussion | Prose ownership cannot exclude competing processes or attribute half-recorded effects | Keep as human task interface, not the safety mechanism |
| Repository-locked local CLI with durable items | One lane across worktrees and both direct/queued paths; pinned subjects/check inputs; recoverable intents | Cooperative local scope; arbitrary oracle semantics and noncooperating writers remain external contracts | Implement as the minimal fallback adapter |
| Existing Harp or hosted integration service | Existing execution/approval infrastructure may already qualify required guarantees | Integration cost and policy fit; Harp has separate owner approval and candidate protocols | Prefer when already qualified; do not replace it with a second controller |

The chosen adapter is a program owned by `phi9t-land`, not a new agent scheduler.
It accepts JSON argv checks and immutable Git candidates and returns JSON status
and evidence. SQLite and a repository-scoped lock own local transitions; Git owns
source identities and mainline history. The worker's source worktree is untouched.
Detached integration worktrees preserve original contributor refs.

The policy is initialized once by an authorized local integration owner. Hooks
and external Git conversion/merge commands are disabled; required acceptance must
be expressed in trusted checks. Script/input file identities are pinned outside
candidate source. This is appropriate only where that explicit local policy
satisfies the repository's review and authority requirements.

Real CLI tests compare bare fast-forward with guarded acceptance, then exercise
ordering, dependency failures, rebase conflicts, dirty/ignored state, candidate and
checker drift, mutable HEAD, timeout, competing direct/queued processes, changing
mainline and actual process death during submission/check/landing phases. The
Git interruption tests wrap the real Git executable to hold at the relevant
boundary, then SIGKILL the integrator. They do not simulate power loss, hostile
kernel escape, remote hosting behavior or distributed locks.

Do not claim all future integration safe. The resulting guarantee is narrower:
cooperating local writers use one guarded lane, exact prepared source is checked,
known failures remain unlanded, and ambiguous operations require reconciliation.
