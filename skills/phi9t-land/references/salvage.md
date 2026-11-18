# Salvage useful code

Inspect relevant branches, commits and owned worktrees before replacing code or
discarding an attempt. Record source tips/bases, dirty changes, untracked files,
useful ignored artifacts and outstanding owners. Inspect foreign trees read-only.

Preserve exact identities and recoverable copies before transformation. For
uncommitted work, retain patches and necessary file contents; patches alone omit
untracked and ignored files. Do not execute unknown worker scripts or Git hooks
merely to inventory artifacts. Keep credentials out of shared evidence and code.

Compare intent and behavior against current mainline. Classify changes as already
integrated, ready to port, needing repair, conflicting, superseded or unresolved,
with reasons. Similar names or commit messages do not establish preserved behavior.
Distinguish a failed approach from a useful fragment.

Port coherent behavior into a task-owned worktree: cherry-pick suitable commits,
apply reviewed patches or reimplement useful parts against current contracts.
Keep source references and an account of what was retained, adapted and left
unresolved. Preserve both contributors' useful intent during conflict resolution.
Use [codify](../../phi9t-codify/SKILL.md) when a recipe needs production engineering.

Verify the new candidate, including composed behavior and relevant regressions.
Historical green results do not qualify a port. Submit coherent results to the
mainline landing path. Keep original work recoverable until its value is integrated
or explicitly accounted for. Age or a stopped agent is not deletion authority.
Escalate material intent conflicts rather than silently discarding someone's work.
