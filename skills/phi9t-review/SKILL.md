---
name: phi9t-review
description: "Review a change against its requested behavior and inspect safety assumptions beyond the diff. Use for code review, review feedback, or changes across shared boundaries."
---

# Review behavior and consequences

For architectural or execution changes, assess the actual contracts against
the shared [architectural defaults](../phi9t/references/architecture.md).

Resolve the exact source range and intended behavior. Read the target's
instructions and relevant callers, dependencies and tests. Compare the final
change with the user's contract, then examine whether the code remains easy to
change without breaking it. Keep review requests read-only.

For a risky change, read [blast radius](references/blast-radius.md). Trace the
one or two facts on which safety depends and test them through real code.
For each finding, give the trigger, consequence, precise location and supporting
evidence. Execution claims need a reproduction or observable trace. When a
reproduction is unavailable, label the finding's uncertainty rather than
inventing a run. Wording-only edits need a reading, not an artificial runtime test.

Independent reviewers can challenge different assumptions when permitted. The
lead inspects every decisive artifact and reruns its proof. Agreement does not
replace evidence; an unavailable different-family judge stays unavailable.

Keep actionable defects separate from design preferences and unconfirmed risks.
Report no findings when none survive checking. When receiving feedback, verify
the claim against the real contract before changing code. Implement only within
the authorized change scope, then exercise the affected behavior again.
