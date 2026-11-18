# Runtime experiment

Use this branch for feasibility, performance, bounded-memory, compatibility or recovery questions. The artifact is an executable experiment and its evidence. A terminal UI is useful only if the question needs interactive control.

## Define the verdict before measuring

State the hypothesis, workload, authorized execution environment and measurable acceptance criteria. Separate these outcomes where relevant:

- **Accounting:** output is correct and produced, retained, evicted, dropped and invalid data reconcile.
- **Resources:** configured limits and observed CPU, memory, storage or network usage meet declared budgets.
- **Recovery:** useful output resumes within a defined deadline after a fault ends.
- **Performance:** cost relative to a matched baseline, with repeated measurements and variation.

A process staying alive, a queue draining or counts reconciling does not establish useful recovery. For recovery, define what fresh correct output must appear after the grace period and how long it must remain healthy. Preserve a failed or unverified outcome even when other dimensions pass. A negative feasibility result can answer the question without authorizing a production redesign.

## Gate the expensive work

Use the smallest real experiment that can disprove the design first:

1. **Prepare dependencies.** Resolve runtime paths, versions, permissions and hidden library-owned resource pools. Read the relevant SDK contracts for limits and settings that must precede initialization. Confirm a matching runtime before compiling.
2. **Complete transfer before preparation.** Transfer inputs into owned staging, await successful completion, then verify their hashes before extraction or installation. A build must consume verified complete inputs. Publish readiness only after all required preparation and build steps succeed; invalidate it when inputs, source or outputs change.
3. **Run a correctness fixture.** Check actual values and records, not just process exit or compilation. Record the execution environment and source/binary/configuration identities with the result.
4. **Run a short normal experiment.** Check real output, clock alignment, loss counters and resource observations. Keep startup and shutdown outside the steady-state measurement unless startup cost is the question.
5. **Inject pressure and check recovery.** Exercise relevant bounded queues or dependency pools. Observe beyond the fault and recovery grace. Expected loss during overload stays distinct from failure to recover afterward. Repeated faults may expose failures a single fault misses.
6. **Measure overhead and soak only after required early gates pass.** Reuse the exact passing candidate and configuration. Compare against a matched baseline, report variation, and measure helper processes as well as the main workload. Distinguish configured allocation bounds from sampled RSS and opaque library allocations.
7. **Finish with evidence and cleanup.** Record per-dimension verdicts, raw outputs, counters, timing, limits, tested identities and remaining uncertainty. Account for owned processes and retained artifacts.

Make this sequence executable through one entry point. Required failed or unverified gates return a nonzero status, preserve their evidence and skip dependent expensive stages. A failure stops the experiment at the useful finding rather than silently weakening acceptance criteria. If a failed run should be studied further, keep that investigation explicit and separate from a passing verdict.

## Keep verification cheap and real

Inspect the project's existing checks before adding another command. Use focused harness regressions when a parser, validator or runner bug could invalidate the experiment. Prefer saved real healthy and degraded artifacts when available, supplemented by small boundary cases where needed. A verifier should reject known degraded output and accept known healthy output for the appropriate criteria.

When bootstrap checks already exist, wire them into the entry point rather than duplicating them. Use structured phase logs and result paths so retries and follow-up validation consume the intended run instead of whichever historical directory happens to be latest.

Capture the answer in the prototype's notes. Keep measured facts, hypotheses and unqualified deployment conditions distinct. Disposable code can be removed or absorbed later; preserve the evidence needed to understand the conclusion.
