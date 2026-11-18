---
name: phi9t-verify
description: "Verify research claims and inference derivations, exercise task results through the real interface, or maintain a project behavior map. Use for independent evidence checks and before declaring a result complete."
---

# Verify the result

Resolve the exact artifact and claims under review. State full coverage or the
specific claims/journeys selected; list everything left unchecked. Use evidence
independent of the producer's summary. A separate agent can perform this method
when delegation is authorized, but another agent's agreement is not proof.

Distinguish independent execution of a check, independent assessment of its
assumptions, and independent authority over acceptance. Another model does not
automatically provide any of these. State which the available workflow supplies;
a cooperative pinned check is not a separate approval or security authority.

Check the oracle as well as the candidate: does the test observe the claimed
user operation, use the owning program's actual contract and reveal relevant
failure effects? Investigate an oracle mismatch before changing product behavior
to satisfy it. A passing check or accurate report can still miss the user's
purpose; establish whether the substantive result answers the original request.

For scout/research reports or conclusions drawn from a prototype, read
[claim verification](references/claims.md). For executable behavior, follow the
runtime path below. Use both when a conclusion depends on measured behavior.
Verification is read-only apart from evidence and owned test state unless fixes
are separately in scope. Report defects without silently changing the candidate.

## Verify executable behavior

Use a verification ladder. Cheap checks such as static analysis, builds, unit
tests, component tests and source review give early signals and help find faults
quickly. Run the useful ones before expensive checks; choose them by the claim
and risk rather than requiring every layer for every task.

**For coding and executable system behavior, real end-to-end verification is
the final acceptance mechanism.** Drive the actual user entrypoint through the relevant
components and integrations to the observable result and side effects. Confirm
the candidate, environment and dependencies match the claim. Cheaper passes do
not replace this proof. A simulated external dependency proves a narrower
boundary, not the real integration. When the real path cannot run, report the
early signals and the missing end-to-end proof; keep acceptance unverified.

An end-to-end pass establishes the exercised behavior under the observed
conditions. It does not prove all inputs, environments or future runs. Keep the
acceptance claim within that scope.

Choose the qualified execution path using the shared
[execution defaults](../phi9t/references/architecture.md#2-insula-execution).

Define the claim and the observation that could disprove it. Resolve the exact
candidate, input and runtime. Read the target's actual check entrypoints and
prerequisites. Run the relevant checks, inspect full results and conditional skips,
and exercise the changed behavior through its public interface.

Check the important refusal or failure path, including forbidden side effects.
Use fakes at owned external boundaries when needed and state what they exclude.
A source-string assertion, metadata check, build or an agent's self-report cannot
substitute for the behavior it does not exercise.

Retain commands, source/runtime identity, inputs, exits, observed outputs and
coverage gaps in the target's existing evidence location. Keep evidence after
cleanup. Confirm run-owned processes and fixtures are accounted for. Report
verified, failed, blocked or inconclusive as appropriate; a partial pass stays
partial. Historical evidence identifies an earlier result. Reassess its
applicability when relevant code, dependencies, configuration or assumptions
change; an unrelated edit need not invalidate every previous observation.

For maintaining an existing packet, read [maintenance](references/maintenance.md).
For a repository without a usable path, use [bootstrap](../phi9t-bootstrap/SKILL.md).
