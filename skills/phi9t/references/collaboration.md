# Collaboration and continuation

Choose the arrangement by its actual need. Sequential handoff preserves intent
and unfinished work. Parallel investigation divides attention across independent
questions. Parallel implementation introduces concurrent changes that must work
together. Parallelism and durable recovery are separate choices: one costly
operation may need reconciliation while many read-only investigations need
little shared operational state. Follow the session's delegation authority.

Give a worker the bounded goal and purpose, starting revision, owned artifacts
and resources, relevant program/data contracts, required proof and return path.
Define shared semantics before splitting writers: different files can still
disagree on a schema, error behavior or lifecycle. Prefer independent exploration
before concurrent writing when it can resolve the uncertainty more cheaply.
Workers can commit and test in their own task-owned worktrees. Give mutable
files, caches, processes and external resources explicit ownership; worktrees
provide cooperative separation, not enforced process or filesystem confinement.

One accountable integrator promotes candidates into accepted mainline. Workers
return exact candidates, evidence, dependencies and unresolved questions. The
integrator checks composed behavior against current mainline; mergeability and
separate old-base passes do not establish compatibility. Reassess evidence when
relevant code, dependencies or assumptions change. Return contribution defects
to their worker when available. Otherwise retain provenance for an owned repair.
Behavioral decisions return to the appropriate owner; integration is not authority
to invent a compromise. Follow [landing](../../phi9t-land/SKILL.md).

A handoff must preserve useful dirty and untracked state as well as commits.
Record what exists, who owns it, what remains useful and what still depends on
it. Inspect the actual artifact rather than accepting a worker's summary.
Before cleanup, preserve needed results and confirm that consumers and owned
processes have stopped. Age and accepted commits alone do not establish that
all remaining state is disposable. Use the project's existing task record.
