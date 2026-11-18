---
name: phi9t-explain
description: "Use when writing or revising a technical explanation, walkthrough or engineering concept for a reader, or when asked for STE-inspired technical English with a light Hemingway influence."
---

# Explain with precision and restraint

Write technical explanations in controlled, plain English. Apply the rules below
to the explanation itself, not just its summary. Keep the reader's technical
level, requested format and question in view.

This is an adaptation inspired by
[ASD-STE100](https://www.asd-ste100.org/about.html), with a light Hemingway
influence. It does not enforce the STE dictionary or certify STE compliance.
Use the rules here without requiring the reader to obtain the specification.

## Build the explanation

Lead with the answer or the behavior the reader needs to understand. Introduce
necessary concepts before using them. Trace cause and effect through a concrete
operation: what enters, which actor does what, what changes, and what comes out.
Include the failure or boundary condition that changes the answer.

For codebase explanations, use [understand](../phi9t-understand/SKILL.md) to
establish the behavior and its evidence. This skill controls expression; it does
not supply missing facts. Distinguish observations, assumptions and inferences.
For a supplied draft, preserve its claims and flag material ambiguities instead
of silently choosing an interpretation.

## Use controlled English

- Give each term one meaning. Use the same term for the same thing. Define an
  unfamiliar technical term or acronym at first use. Keep exact API names,
  identifiers, commands, error text, units and mathematical notation intact.
- Prefer common words and concrete verbs. Write "use" for "utilize" and "retry"
  for "perform a retry operation." Keep a specialist term when it is more exact;
  explain it rather than replacing it with a misleading everyday word.
- Name the actor and prefer subject, verb, object. Use passive voice when the
  actor is unknown or irrelevant. Do not invent an actor to avoid a passive.
- Give each sentence one main proposition. Put a condition beside the action it
  controls. Use explicit nouns when "it," "this" or "then" could refer to two things.
- Keep prose sentences at 25 words or fewer. Split longer sentences unless that
  would damage a necessary logical relation or exact technical expression.
  Code, formulas, identifiers and verbatim quotations keep their required form.
- Give each paragraph one topic and no more than six sentences. Use connected
  prose for explanations, numbered steps for procedures, and tables for comparisons.
- Preserve negation, quantifiers, preconditions, uncertainty and causal direction.
  Keep "must," "should," "may" and "can" distinct. Brevity never licenses a stronger
  guarantee, an omitted exception or a lost warning.

## Add a little Hemingway

Use direct statements, concrete detail and restrained emphasis. Vary sentence
length within the limits above. Let a short sentence carry a consequence.
Cut throat-clearing, ornamental adjectives and adverbs that add no information.
Keep the tone calm and human. Avoid literary imitation, dramatic fragments and
metaphors that hide the mechanism. A useful analogy must return to the actual
system and state its limit.

## Check before sending

Read the explanation once for technical fidelity and once for language. Check
each condition and identifier against the source. Split dense sentences, resolve
ambiguous references, and remove filler. Retain the detail needed to answer
"how?" or "under what conditions?" Keep citations beside the claims they support.
Return the explanation in the requested format without a style audit unless asked.

For example, replace "The worker leverages retries to ensure delivery" with:

> The worker retries a failed request up to three times. Retries do not guarantee
> delivery. A lost response can cause a duplicate action unless the receiver
> deduplicates requests.

Use that wording only when those facts hold. The example demonstrates expression,
not a default retry policy.
