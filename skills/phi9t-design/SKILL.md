---
name: phi9t-design
description: "Design semantic codebase ownership, program/CLI/service boundaries and data models. Use when a consequential interface or architecture choice needs to be resolved before implementation."
---

# Design from first principles

[Codify](../phi9t-codify/SKILL.md) owns the recipe-to-production workflow; this
method supplies its architectural decisions. When called by codify, return those
decisions to the caller. Exploration recipes remain free-form; production
structure follows the intended behavior and contracts.

Apply the shared [architectural defaults](../phi9t/references/architecture.md).
Name the program boundaries, exchanged data models, semantic owners and
execution contexts first. Explain one useful composition at the MTS level;
then sketch the internal modules that support it.

Restate the goal in terms of the user's operation. Trace the existing behavior
and constraints before replacing it. Identify the access patterns and invariants
that the data model must represent. Ask what the design would be if the new
requirement had existed on day one.

Write a caller's usage example first. Sketch the essential types, public
signatures, ownership and failure behavior needed to make that usage natural.
One owner per invariant; derive values instead of synchronizing copies. Validate
external input at the boundary and keep internal operations simple. If concurrent
actors can interfere, separate their state before adding coordination.

Make complexity earn its place. Tie added coordination, durable state or another
layer to a specific consequential failure, observed or credibly anticipated.
Choose the smallest adequate mechanism and state what would demonstrate its
benefit and operational cost. Anticipate expensive or destructive failures
before they occur. Parallelism and durability solve different problems; neither
requires the other. Test simplification too: remove mechanisms incrementally and
check that the required behavior and recovery still hold.

When a consequential choice is open, compare distinct alternatives. Use a
bounded [prototype](../phi9t-prototype/SKILL.md) for the fact that could change the
choice. More reviewers cannot answer a question that needs a measurement. Use
independent candidates only when permitted and useful.

Use [research](../phi9t-research/SKILL.md) when the choice depends on an external
contract, prior result or unfamiliar source. Carry its citations and unresolved
claims into the prototype or design rationale rather than treating a summary as
proof of runtime behavior.

Record the selected shape, rejected alternative, accepted tradeoff, unresolved
fact and proof needed. Detail an execution plan only after the uncertainty is
small enough to implement. Sequence independently verifiable units. Continue
implementation when already requested; honor an explicit design-only boundary.

Revisit the shape when unrelated callers repeatedly need the same workaround,
casts, hidden ordering or knowledge of internals. Fix the owner or representation
rather than adding another layer around the symptom.
