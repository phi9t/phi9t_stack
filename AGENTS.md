# Working on phi9t_stack

This repository owns the shared skill packages and their file installer.
Repository guidance must remain useful to both Codex and TRAE CLI.

For engineering work here, use this checkout's `skills/phi9t/SKILL.md` router
and select the methods the task needs. Prefer these source definitions when
evaluating the stack. Retain concrete dogfood findings in `docs/evidence/`.
Dogfooding runs cover the complete engineering product surface defined in
`docs/dogfooding.md`. Inventory current methods and entrypoints, exercise their
real success/refusal/recovery paths, and report every surface as verified,
failed, blocked or not run. A green source gate alone is not full dogfood coverage.
Keep this repository focused on the phi9t skillset for Codex and TRAE CLI and
the tools those skills need. Unrelated integrations belong outside this repository.

For program design, codebase organization and execution selection, follow
the user's shared architectural defaults in
`skills/phi9t/references/architecture.md`. Keep that reference as the canonical
skillset definition; method entrypoints link to it instead of copying its rules.

## Owners

- `pyproject.toml` and `uv.lock` own the non-package development environment and
  pinned checks. `VERSION` remains the release identity.
- `skills/<name>/SKILL.md` is the sole entrypoint for that method. Keep its trigger
  specific. Put conditional detail in linked relative resources.
- `scripts/stack.py` owns package validation, installation identity, backups and
  recovery. Runtime discovery is a separate integration check.
- `scripts/release.py` owns deterministic release bundles, static inspection,
  safe unpacking and artifact qualification. `VERSION`, `releases/` and
  `docs/releases.md` own version, notes and promotion procedure. No automatic
  tags, remote publishing or global installation belong in release checks.
- `skills/phi9t-land/scripts/land.py` owns the cooperative local landing lane,
  queue records, candidate pins and recovery. It does not own agent scheduling
  or remote publication. Its CLI behavior is exercised in `tests/test_landing.py`.
- `docs/verification.md` owns the behavior map. Run receipts belong in dated
  evidence notes, separate from the stable recipes.
- `legacy.json` records exact pre-rebuild identities. Retire only matching files;
  modified legacy content belongs to the user and must remain intact.

## Changes

Follow trunk/mainline-based development. Make actual changes in a task-owned
Git worktree on a short-lived branch; reuse a suitable existing worktree.
Integrate small verified increments promptly. Rebase onto current mainline and
land by fast-forward only so mainline history remains linear. Preserve existing
work and required review/publication authority. The shared workflow is defined in
`skills/phi9t/references/workspaces.md`.
Mainline integration is mandatory for coding delivery. Use `phi9t-land` for
direct or queued rebase/fast-forward landing and salvage. Keep unlanded work
assigned with evidence and a next action; a branch or queue entry is not completed
delivery. Failed gates remain blockers, not reasons to bypass checks.

Keep native nested skills as the source format. Frontmatter uses a plain `name`
and a JSON-quoted YAML `description`. Package every referenced local resource.
Use session capability discovery and model defaults instead of model tables.
Add a skill only for an independently useful method; put baseline project rules
here rather than in a new skill. Preserve current user authorization and task scope.

For package, installer or recovery changes, use
`.agents/skills/verify-phi9t-stack/SKILL.md`. Bootstrap with `uv sync --locked`;
run `./scripts/verify.sh` after changes. Installer behavior needs isolated-root
checks of bytes, modes and side effects. A metadata pass does not prove instruction
quality; substantial method changes need a realistic task trial when practical.
Update the behavior map when a journey changes. Keep network calls and global
installation out of automated checks. Use an explicit scratch target for trials.

A rebuild does not authorize replacing user-global customizations, changing
runtime permissions, publishing, or merging unrelated work. Report implementation,
verification and installation state separately.

## Agent skills

### Issue tracker

Track issues and specs as local Markdown under `.scratch/<feature>/`.
Before publishing or fetching work, read `docs/agents/issue-tracker.md`.

### Triage labels

Use the five default triage roles.
Before assigning status, read `docs/agents/triage-labels.md`.

### Domain docs

Use a single-context layout.
Before exploring domain terminology or architectural decisions, read
`docs/agents/domain.md`.
