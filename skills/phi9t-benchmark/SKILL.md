---
name: phi9t-benchmark
description: "Design or validate a performance comparison. Use for latency, throughput, memory, cost or optimization claims that need a matched baseline and repeatable measurements."
---

# Measure a decision

Select the measurement environment using the shared
[execution defaults](../phi9t/references/architecture.md#2-insula-execution).

Before running, state the decision, workload, metric, units and improvement large
enough to matter. Identify the limiting resource and a physical bound or sanity
check. Qualify correctness before accepting a speedup.

Bind baseline and candidate to exact source, configuration, toolchain and relevant
hardware. Match workload, concurrency, production tuning, caching and startup
policy. State warmup and synchronization requirements. Confirm completed useful
work, error counts and output equivalence; early exit or dropped work is not a win.

Run a short baseline first to expose an unsuitable environment. Alternate baseline
and candidate to reduce ordering effects. Use enough repeats to see variation,
starting with five per side when affordable. Retain raw observations and report
median and range with the workload. Explain any reduced sample and its limits.
Profile in separate runs when instrumentation changes the measurement.

For GPU work, distinguish host enqueue time from completed device work and account
for synchronization, warmup and shared-device contention. For memory, distinguish
configured limits, sampled resident memory and allocations outside the measured
process. Report helper costs where relevant.

Accept the claim only when its threshold exceeds observed noise and both sides
performed comparable work correctly. Otherwise report no demonstrated win or an
inconclusive experiment. Preserve the measurement harness and raw evidence needed
to rerun the comparison.
