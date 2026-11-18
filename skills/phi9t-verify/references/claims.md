# Verify facts and derivations

Use the [research claim contract](../../phi9t-research/SKILL.md#synthesize-a-useful-result)
and its human-readable report style. Record the report revision or hash and
scope so the verdict identifies the artifact actually inspected. Keep the
producer's claim IDs in the verification output.

## Reopen the evidence

For each selected Fact, read the cited primary material or original observation.
Check that it supports the exact claim, with the same version, population,
conditions and time period. A valid URL or matching quotation alone is not
enough. Distinguish a source's assertion from an independently established fact.
Inspect contrary evidence and material omitted qualifications. Record unavailable
sources as gaps; do not turn inaccessible evidence into a confirmed falsehood.

## Check the derivation

For each selected Inference, follow its premise IDs to the evidence. Check each
step against the stated assumptions. Reproduce calculations with their original
inputs, units and method. Check scope changes, circular support, hidden premises,
and alternatives that fit the same evidence. Several copies of one source do
not provide independent corroboration. An uncertain premise limits the conclusion.

Ask whether the premises justify the actual strength of the conclusion: a
possible explanation, a likely explanation and an established implication have
different burdens of evidence. Code behavior alone does not prove author intent;
a successful demonstration does not establish general reliability.

When a decisive premise remains unsettled, call research with that narrow
question, evidence pointers and remaining budget. Reinspect the returned sources.
For runtime claims, inspect retained raw results and rerun the decisive probe
when practical and authorized, following the main verifier's execution rules.
State when the review checks records only and does not reproduce the experiment.
For coding and executable behavior claims, source evidence and reasoning are
early signals; final acceptance requires the real end-to-end path described in
the main skill. Research claims use the proof appropriate to the claim: primary
source checks for facts, sound derivations for inferences, and observations or
experiments when the conclusion depends on empirical behavior. Research does
not require an end-to-end software run merely because it needs verification.

## Return a checkable verdict

For every selected claim return its ID, **supported**, **refuted**, **unsupported**
or **inconclusive**, the inspected evidence and a concise reason. For an inference,
name the disputed premise or derivation step. Unsupported means the supplied
evidence does not establish the claim; refuted requires evidence against it.
Inconclusive means the available evidence or access cannot settle the claim.

Keep evidence validity separate from labels and presentation. A sound claim
with a missing label needs a contract correction; good formatting does not make
a claim sound. Identify the smallest correction or additional evidence needed.
Evaluate which findings affect the report's main conclusion and explain why.
List unverified claims, searched sources, access gaps and reproduction limits.
An overall verdict cannot exceed its coverage or its decisive unresolved premise.

## Published basis

This method adapts the evidence checks in Lauren Tan's
[why synthesizer](https://github.com/cursor/plugins/blob/main/pstack/skills/why/references/synthesizer-prompt.md)
and [confidence framework](https://github.com/cursor/plugins/blob/main/pstack/skills/why/references/epistemics.md).
The executable branch draws on her
[verification generator](https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/SKILL.md)
and [maintenance method](https://github.com/cursor/plugins/blob/main/pstack/skills/maintain-verification-skill/SKILL.md).
Our explicit Fact/Inference labels and derivations are the user's requirements;
these adaptations are not a claim of her review or endorsement.
