---
name: phi9t-scout
description: "Explore an unfamiliar area and identify promising leads for further investigation. Use when the useful questions, sources or opportunities are not yet known; return an evidence-backed map and next missions."
---

# Scout unfamiliar ground

Explore to discover promising leads. Research answers a defined question;
scouting determines which questions deserve attention. A mission can cover a
codebase, technical field, ecosystem or collection of existing work.

State the mission objective, search boundary, time or resource budget and what
makes a lead valuable to the user. Use the session's constraints; state reasonable
defaults where unspecified. Leave the target system unchanged apart from owned
exploration artifacts: scripts, docs, captured evidence or other useful recipes.
Respect the user's access and execution policies.
Create or change recipe files in a task-owned worktree, following
[Git workspace hygiene](../phi9t/references/workspaces.md).

## Explore and follow leads

Build an initial map from the area's entrypoints, terminology, primary sources
and existing work. For codebases, start at programs, CLI/service contracts and
exchanged data, using the shared
[architectural defaults](../phi9t/references/architecture.md).

Sample distinct parts of the area before concentrating on the first promising
result. Follow concrete signals: relevant capabilities, unexplained behavior,
contradictions, reusable approaches or gaps that matter to the objective.
Record inspected sources, sample boundaries, empty searches and access gaps.
Describe coverage at the level actually inspected; a sample is not an exhaustive
survey. Change direction when the evidence weakens a lead.

Call [research](../phi9t-research/SKILL.md) as a subroutine when a lead needs a
specific factual question answered. Pass the question, why it matters, source
pointers, remaining budget and expected evidence. Retain ownership of the scout
mission: inspect the returned evidence, update the map and continue or stop.
Calling a skill does not itself require another agent. Delegate only when the
session permits it. A subroutine retains the mission's authority and budget.

## Return a useful map

Scripts and docs are useful mission outputs, not merely temporary residue.
Treat them as recipes: choose whatever form best expresses the exploration and
makes it useful to the next reader or agent. No fixed schema, template, language
or production module structure is required. Keep their purpose, inputs, observed
results and limitations understandable; label unexecuted instructions accordingly.
Preserve useful recipes in an explicit location rather than deleting them just
because they are exploratory. Exploration artifacts do not change the target's
production behavior or expand permission to execute their contents.

Write clear prose for the human reader. Follow research's
[report language and claim rules](../phi9t-research/SKILL.md#report-language):
label Facts and Inferences, cite evidence and give each inference's derivation.
Separate an observed signal from the inferred value of pursuing it.

Return the terrain map, promising leads, obstacles and coverage gaps. For each
lead, give its evidence, relevance, uncertainty and the next question or smallest
experiment that could establish its value. Rank leads with explicit reasons
relative to the mission objective. Preserve useful negative findings; if no lead
is supported, say so rather than manufacture opportunities.

Stop when the map supports a reasoned choice of next investigations or the
mission budget ends. Report unfinished coverage and why the mission stopped.
Recommend focused research, a prototype or deeper understanding as appropriate.
An experiment or implementation beyond the scout brief needs its own scope;
discovering a lead is not proof of feasibility or permission to build it.
When production implementation is requested, use
[codify](../phi9t-codify/SKILL.md).
