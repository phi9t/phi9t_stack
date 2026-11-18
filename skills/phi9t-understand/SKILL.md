---
name: phi9t-understand
description: "Explain how a subsystem works, locate its owner, or investigate why a design exists. Use before changing unfamiliar behavior; explanation and diagnosis remain read-only."
---

# Understand a system

Use the shared [architectural defaults](../phi9t/references/architecture.md)
when constructing the MTS-level map. Start with programs, CLIs, services,
exchanged data and execution boundaries, then trace the relevant implementation.

State the question and the boundary being investigated. Start at the user's
entrypoint and trace a representative input through the actual implementation
to its observable output. Name the owner, state transitions, external systems,
failure paths and checks. Inspect enough callers to distinguish an interface's
contract from an accidental implementation detail.

For why questions, inspect history, tests and maintained decisions. Consult the
connected issue, document or conversation source when the question references it.
Separate recorded rationale from inference. A current code path proves what
happens; it may not prove why someone chose it.

Return a compact traced example, the key constraints with file or source links,
and the unresolved fact that matters to the task. A list of filenames is not a
runtime explanation. When behavior can be observed safely, use that observation
to test the model. Keep a read-only request read-only.
