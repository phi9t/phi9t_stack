---
name: phi9t
description: "Use phi9t_stack for an engineering task or to choose its focused methods. Follow the requested explain, review, diagnose or implement scope."
---

# phi9t

Begin with why the user needs the result, what substantive answer or behavior
would satisfy that purpose, and what evidence would establish it. Choose methods
and tools to serve that outcome. Completed searches, checks or commits alone do
not establish that the user's problem is solved. Keep this proportionate; a small
task needs no purpose template. Read the target's instructions and current state.
Use its existing tools and owners. Repository policy controls authority and integration.

For actual changes, follow [Git workspace hygiene](references/workspaces.md):
trunk/mainline development, task-owned worktrees, prompt integration of small
increments, and rebase followed by fast-forward landing for linear history.

For codebase organization, program/data-model boundaries, execution selection or
explaining architecture to an MTS, read the shared
[architectural defaults](references/architecture.md). They own the semantic
layout, Insula vocabulary and exceptions, program contracts, MTS legibility and
composition preferences used across these methods.
For Python implementation or review, also apply its
[Python engineering principles](references/architecture.md#python-engineering).

Choose only the method the current uncertainty calls for:

| Need | Method |
|---|---|
| Explore unfamiliar ground and identify promising leads | [scout](../phi9t-scout/SKILL.md) |
| Turn an exploratory recipe into production code | [codify](../phi9t-codify/SKILL.md) |
| Salvage task code and deliver it to mainline | [land](../phi9t-land/SKILL.md) |
| Understand behavior, ownership or rationale | [understand](../phi9t-understand/SKILL.md) |
| Write a clear technical explanation for a reader | [explain](../phi9t-explain/SKILL.md) |
| Investigate an open question against primary sources | [research](../phi9t-research/SKILL.md) |
| Choose a consequential interface or architecture | [design](../phi9t-design/SKILL.md) |
| Reproduce and repair a failure | [debug](../phi9t-debug/SKILL.md) |
| Assess a change and its downstream effects | [review](../phi9t-review/SKILL.md) |
| Check facts/derivations, establish behavior or maintain a behavior map | [verify](../phi9t-verify/SKILL.md) |
| Make a repository usable by the next agent | [bootstrap](../phi9t-bootstrap/SKILL.md) |
| Eliminate a recurring mistake | [correct](../phi9t-correct/SKILL.md) |
| Assess a performance claim | [benchmark](../phi9t-benchmark/SKILL.md) |
| Resolve feasibility or compare concrete alternatives | [prototype](../phi9t-prototype/SKILL.md) |

Use scout to find questions worth pursuing, research to establish what the
evidence supports and prototype to test what needs execution. Scout and prototype
can call research as a scoped subroutine and retain their own mission ownership.
Feed measured findings back into the canonical research or
design note. Choose the next method by the remaining uncertainty, rather than
requiring every task to pass through a fixed sequence.

For a small change, inspect, change and exercise the result directly. For work
spanning dependent steps or sessions, keep enough state in the project's existing
task record for a fresh reader to continue: purpose, candidate and dirty work,
observations and evidence, unsettled questions, next action and its owner. Update
it when the user steers the work. Logs preserve history; a handoff selects the
current state; durable project guidance belongs to AGENTS.md. No new ledger or
fixed format is required. Task state must outlive the execution instance it
needs to recover from; an Insula or current context window is not its sole owner.
Before retrying an uncertain external effect, reconcile what actually happened.

For handoffs or multi-agent work, read [collaboration](references/collaboration.md).
Delegate only when session policy permits it and the benefit warrants the cost.
Use session model defaults; diversity is useful only when it actually exists.
Keep every delivery unit independently checkable. Coding tasks finish through
[mainline landing](../phi9t-land/SKILL.md); a ready branch or queue entry does
not complete delivery. Preserve exact candidates and blockers until landed.

Runtime details belong in [Codex](references/codex.md) or
[TRAE CLI](references/traecli.md). Read the relevant adapter when selecting tools,
not for ordinary engineering decisions. For unavailable tools, use an equivalent
observable path or report the exact capability gap.

Finish with what changed or what was learned, the observed evidence, remaining
limits and the actual integration state. Keep the final answer self-contained.
For coding and executable behavior, use cheap checks for early signals and real
end-to-end verification for final acceptance of the claimed scope. Otherwise name
the remaining proof and keep acceptance unverified. For research, verify facts
against primary evidence and check inference derivations; use experiments when
the claim requires empirical evidence.
