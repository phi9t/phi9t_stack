---
name: phi9t-codify
description: "Turn an exploratory recipe into production code. Use when scout/prototype scripts, docs, notebooks or command sequences should become a maintained program, CLI or service capability."
---

# Codify a recipe

Scout and prototype can produce scripts, docs, notebooks, command sequences or
other artifacts. These are recipes: useful expressions of an approach, without
a required format. Codification turns their useful behavior into a maintained
production capability. A recipe alone is not authorization to change the product;
a request to codify it includes implementation and verification within that scope.
Follow [Git workspace hygiene](../phi9t/references/workspaces.md) throughout:
implement in a task-owned worktree and integrate small verified increments with
rebase and fast-forward landing.

## Recover the behavior

Read the recipe and its evidence. Identify the user operation it enables, useful
behavior, inputs, outputs, dependencies, effects and unresolved assumptions.
Distinguish executed observations from instructions nobody has tried. Preserve
the original evidence and link production work to it. Reproduce the uncertain
step that could change the design, under the shared
[execution defaults](../phi9t/references/architecture.md#2-insula-execution).
Use [research](../phi9t-research/SKILL.md) for a specific unresolved factual claim,
or [prototype](../phi9t-prototype/SKILL.md) when a bounded experiment is needed.

## Design and implement the production capability

Follow our [repository design principles](../phi9t/references/architecture.md)
and the target repository's instructions. Organize by semantic ownership;
co-locate related implementation, contracts, tests and docs. Design composable
program/CLI/service boundaries around explicit data models so an MTS can
understand the system at those boundaries. Apply Insula execution and its native
exceptions, and use durable coordination only where the work requires it.
For Python, apply the shared [Python engineering principles](../phi9t/references/architecture.md#python-engineering):
explicit data models and composition are the default, with clear types,
dependencies, resource ownership and behavior checks.

Use [design](../phi9t-design/SKILL.md) to choose the production shape from the
operation and data contracts. Choose the semantic owner, program/CLI/service
boundary, data models and runtime. Prefer an existing owner when the behavior
belongs there. Name the failure, retry, resource and lifecycle requirements that
matter to this use. The recipe's incidental structure does not determine the
production architecture.

Implement the smallest coherent production capability. Reuse recipe code when
it fits; rewrite or discard scaffolding when it obscures the contract. Avoid an
automatic wrapper that leaves a fragile experiment as the production core.
Keep a trace from useful recipe behavior to its production interface and checks.
This trace can live in the existing task record or design note; it needs no new
schema or document hierarchy.

## Establish production acceptance

Use cheap checks for early signals, then
[verify](../phi9t-verify/SKILL.md) the real end-to-end operation and important
failure paths before production acceptance. Account for dependencies and side
effects the original recipe skipped. A working recipe is evidence for the
approach, not proof of the resulting production system. When end-to-end proof is
blocked, deliver the implementation with its verified scope and missing proof
explicit; do not label the capability accepted.

Leave production code, relevant verification evidence and a clear account of
what was incorporated, changed or left unresolved. Keep a recipe when it still
explains or reproduces something useful; otherwise retire it with its evidence
and decision preserved in the project's existing record. Keep user changes and
still-needed artifacts intact. Exploration need not meet production form before
codification is requested.
Complete coding delivery through [land](../phi9t-land/SKILL.md), directly or via
the existing landing queue. Unlanded capabilities remain intermediate results
with an owner and a concrete next action.
