---
name: phi9t-prototype
description: "Build a bounded experiment to resolve a design, interface or runtime feasibility question. Use for competing UI or logic choices, resource limits, performance, compatibility and recovery."
---

# Prototype the uncertainty

Select execution using the shared
[architectural defaults](../phi9t/references/architecture.md#2-insula-execution).
Disposable work retains its Insula or permitted native execution requirements.
Create or change recipe files in a task-owned worktree, following
[Git workspace hygiene](../phi9t/references/workspaces.md).

State the question, smallest experiment that could answer it and acceptance
criterion. Build close to the actual caller with an explicit disposable location
and one run command. Reuse project setup and controls. Keep the candidate and
baseline identifiable.

If a dependency, protocol or published claim is unclear, use
[research](../phi9t-research/SKILL.md) as a scoped subroutine to locate its primary
evidence. Pass the factual question, relevant inputs and remaining budget;
inspect its evidence and retain ownership of the experiment and verdict.
Calling the skill does not require delegation or expand execution authority.
Carry the unresolved hypothesis and evidence into the experiment. Define the
time/resource bound and the observation that would reject the proposal before
writing the probe. Prefer a minimal real CLI, service or data-model contract
over a mock of the implementation being evaluated.

For interface or logic choices, expose the relevant states and demonstrate the
caller's operation. Compare distinct alternatives only where the choice is open.
For appearance, show actual rendered states and interactions. Disposable code
needs enough checking to make the experiment's verdict trustworthy, without
production scaffolding.

Run the experiment and retain its actual invocation, inputs, source/runtime
identity, outputs and verdict. Include a meaningful baseline or negative control
where it is needed to distinguish a real result from a broken observer. An
unrun sketch is a proposed experiment, not a completed prototype.

For feasibility, pressure, resources or recovery, read
[runtime experiments](references/runtime.md). For a comparative speed claim, use
[benchmark](../phi9t-benchmark/SKILL.md). A negative result can answer the question;
it does not authorize an unrelated production rewrite.

Keep raw evidence and the resulting decision. Preserve useful scripts and docs
as recipes when they remain valuable for reproduction or later implementation.
Recipes can take any useful form; no fixed template, schema, language or
production structure is required. Let the agent choose the most expressive form
for the question. Keep purpose, inputs, invocation and limits understandable,
and distinguish observed results from proposed or unexecuted steps.
State which production properties
were not tested. A successful demonstration is evidence about the experiment's
conditions, not general deployment readiness.

Hand the evidence back to the research note or design owner: what was learned,
which choice it supports or rejects, and the next unresolved question. Research
and prototyping can alternate; a simple task need not run both methods.
When production implementation is requested, use
[codify](../phi9t-codify/SKILL.md).
