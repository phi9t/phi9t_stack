---
name: phi9t-pstack
description: "Use poteto-mode, the pstack engineering skills or their principles when the user asks for poteto style, /poteto-mode, or a pstack method such as swarm, interrogate, architect, how, why, unslop or tdd."
---

# phi9t pstack

Vendored copy of Lauren Tan's [pstack](https://github.com/cursor/plugins/tree/93b916d4a1e806507e22f4716b352fa91f2b227e/pstack)
0.15.43 (MIT; see [LICENSE](LICENSE)), pinned in `vendor.json`. The files below are
unmodified upstream bytes; refresh them with `scripts/vendor.py`, never by editing.
Start with [poteto-mode](poteto-mode/SKILL.md). It names its sibling skills, which sit
beside it at `../<name>/SKILL.md`, and delegates through [poteto-agent](agents/poteto-agent.md).

## Running it on Codex or TRAE CLI

Upstream targets Cursor. Map its runtime terms to the host instead of editing it:

- `Task` and `subagent_type: "poteto-agent"` mean the host's native child session
  (Codex subagent, TRAE CLI child session) with the poteto-agent text in its prompt.
  Use the host's own model names and reasoning levels; ignore Cursor model tables.
- `AskQuestion` is the host's user-question tool, or a plain question when none exists.
- `cursor-team-kit` skills (`deslop`, `control-cli`, `control-ui`) and `/setup-pstack`
  are optional. Use an installed equivalent, such as phi9t-verify for behavior checks,
  or do the step by hand. Missing ones never block the task.
- Repository instructions, permissions and landing policy outrank any playbook.
  For phi9t_stack work, [phi9t](../phi9t/SKILL.md) owns workspaces and landing.

## Skills

- [architect](architect/SKILL.md)
- [arena](arena/SKILL.md)
- [benchmark-checklist](benchmark-checklist/SKILL.md)
- [correct](correct/SKILL.md)
- [create-verification-skill](create-verification-skill/SKILL.md)
- [figure-it-out](figure-it-out/SKILL.md)
- [how](how/SKILL.md)
- [in-your-own-words](in-your-own-words/SKILL.md)
- [interrogate](interrogate/SKILL.md)
- [maintain-verification-skill](maintain-verification-skill/SKILL.md)
- [no-comments](no-comments/SKILL.md)
- [poteto-mode](poteto-mode/SKILL.md)
- [principle-attack-the-premise](principle-attack-the-premise/SKILL.md)
- [principle-boundary-discipline](principle-boundary-discipline/SKILL.md)
- [principle-build-the-lever](principle-build-the-lever/SKILL.md)
- [principle-encode-lessons-in-structure](principle-encode-lessons-in-structure/SKILL.md)
- [principle-exhaust-the-design-space](principle-exhaust-the-design-space/SKILL.md)
- [principle-experience-first](principle-experience-first/SKILL.md)
- [principle-explain-the-number](principle-explain-the-number/SKILL.md)
- [principle-fix-root-causes](principle-fix-root-causes/SKILL.md)
- [principle-foundational-thinking](principle-foundational-thinking/SKILL.md)
- [principle-guard-the-context-window](principle-guard-the-context-window/SKILL.md)
- [principle-laziness-protocol](principle-laziness-protocol/SKILL.md)
- [principle-make-operations-idempotent](principle-make-operations-idempotent/SKILL.md)
- [principle-migrate-callers-then-delete-legacy-apis](principle-migrate-callers-then-delete-legacy-apis/SKILL.md)
- [principle-minimize-reader-load](principle-minimize-reader-load/SKILL.md)
- [principle-model-the-domain](principle-model-the-domain/SKILL.md)
- [principle-never-block-on-the-human](principle-never-block-on-the-human/SKILL.md)
- [principle-outcome-oriented-execution](principle-outcome-oriented-execution/SKILL.md)
- [principle-prove-it-works](principle-prove-it-works/SKILL.md)
- [principle-redesign-from-first-principles](principle-redesign-from-first-principles/SKILL.md)
- [principle-separate-before-serializing-shared-state](principle-separate-before-serializing-shared-state/SKILL.md)
- [principle-sequence-verifiable-units](principle-sequence-verifiable-units/SKILL.md)
- [principle-subtract-before-you-add](principle-subtract-before-you-add/SKILL.md)
- [principle-test-behavior-not-implementation](principle-test-behavior-not-implementation/SKILL.md)
- [principle-type-system-discipline](principle-type-system-discipline/SKILL.md)
- [reflect](reflect/SKILL.md)
- [show-me-your-work](show-me-your-work/SKILL.md)
- [swarm](swarm/SKILL.md)
- [tdd](tdd/SKILL.md)
- [technical-writing](technical-writing/SKILL.md)
- [unslop](unslop/SKILL.md)
- [why](why/SKILL.md)
