---
name: phi9t-debug
description: "Diagnose a broken, failing, flaky or slow behavior, and repair it when requested. Build a loop that can detect the reported symptom before selecting a fix."
---

# Debug through a falsifiable loop

Before running the reproduction, apply the shared
[execution defaults](../phi9t/references/architecture.md#2-insula-execution).

Locate the exact input, source/runtime and user-observed failure. Inspect the
relevant entrypoint enough to build the cheapest real reproduction. Run it and
retain the result. A useful loop distinguishes the reported failure from another
nearby error. If reproduction needs unavailable state, name what was tried and
the specific missing artifact or environment. Continue safe independent analysis.

Shrink the reproduction while keeping the failure. Rank a few falsifiable
causes and test the distinguishing prediction, changing one relevant variable
at a time. For flakes, increase the reproduction rate and record the rate and
conditions. For slowness, establish the workload and measurement first.

When a repair is authorized, fix the owning cause. Add a regression at the real
caller seam when it is cheap and can catch this failure. Observe it fail before
the fix and pass afterward; avoid a shallow test that cannot express the bug.
Rerun the original input through the same public path. Remove temporary probes.

Report the reproduced symptom, cause, actual before/after result and limits.
Diagnosis alone does not authorize implementation. A test passing for another
failure mode does not establish that the user's bug is fixed.
