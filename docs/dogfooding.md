# Dogfood the complete engineering surface

A dogfood run exercises the product an engineer uses: methods, programs, data
contracts, runtime integration and delivery. A passing test suite is necessary
evidence for executable changes. It is not the whole product.

The acceptance scope is the phi9t skillset, its delivery tools and its use
through Codex and TRAE CLI. Unrelated integrations belong
outside this repository. Linux and remote publication qualification need their
own requested scope.

Start each run by comparing this inventory with current skill entrypoints,
CLI help/dispatch, runtime adapters and recent changes. Add new surfaces before
claiming full coverage. Use the checked-out methods and the
[behavior map](verification.md). Keep dated receipts in `docs/evidence/` and
reusable exploration recipes in the existing research area.

Before launching native runtimes, retain an inventory of the live profile's
file bytes, modes and symlink targets. Keep owner-only copies of configuration
bytes as well as hashes outside the repository. A hash detects drift but cannot
explain or safely undo it. Native runtimes may record trust for new scratch
projects; account for that state separately. Preserve concurrent or unattributed
configuration edits and keep their preservation claim unverified until reconciled.

## Inventory and required observations

| Surface | Exercise through its real boundary |
|---|---|
| Engineering methods | Every `skills/*/SKILL.md`: retain a useful task, method decisions, actual artifact/result, source identity and limits. One coherent mission can exercise several methods. Reading instructions or listing skills is not a behavioral trial. |
| Routing and composition | Select by uncertainty; trace scout/research/prototype/design/codify handoffs through their actual outputs. Preserve failed findings and do not force irrelevant methods into ordinary tasks. |
| Installer | `check`, `install`, `verify`, `restore`, `recover`, the shell wrapper, no-op update, drift/replacement, unmanaged collisions, exact legacy retirement, permissions, locks and interruption. Inspect installed bytes, modes, preserved files and backups. |
| Release | `build`, `verify`, `unpack`, `qualify`: version/notes, committed source, reproducibility, inventory/checksum/modes, malformed/truncated/oversized data, output collisions, real bundle installation, upgrade and rollback. Bind receipts to exact archive bytes. |
| Local landing | `init`, `submit`, `status`, `run`, `retry`, `recover`: direct and queued work, dependency versions, pins, real rebase/fast-forward, contention, failed/stale checks, conflicts and interrupted/uncertain outcomes. Preserve useful work. |
| Salvage and actual integration | Inspect existing work, retain provenance, repair an assigned blocked candidate when needed, and confirm accepted work reaches actual mainline. Match hook/review authority; scratch queue success does not authorize disabling this repo's hooks. |
| Source development | Fresh managed uv environment, locked sync/repeat, formatter/lint/scoped type/shell checks, complete behavior suite, stale dependency refusal and a failing style fixture. Exercise launching from outside the repo. |
| Codex discovery | Fresh runtime process: absent project packages → scratch install → all expected packages discovered at exact project paths and enabled → restore → project packages absent. This proves discovery, not an inference task or model effectiveness. |
| TRAE discovery | The same lifecycle using the installed TRAE runtime's actual supported interface. Flat/nested layout compatibility remains an observed property of that version. |
| Execution and portability | Use the architectural execution route. Name native uv Python versus Linux Insula. Record admitted dependencies and exercise actual program behavior per platform. A Linux help/export smoke test does not qualify Git landing or Python installation. |
| Distribution and promotion | Prepare durable artifacts, checksums, notes and receipts. Actual publication/download integrity needs an authorized destination and publication authority; do not invent a remote, overwrite a version or publish merely to close a row. |

The method inventory currently includes `phi9t`, scout, understand, explain, research,
design, prototype, benchmark, codify, debug, correct, bootstrap, verify, review
and land. Discover the directories again on each run; this list is not an
immutable registry.

## Coverage and completion

Give each surface an outcome: **verified**, **failed**, **blocked**, or **not run**.
List explicit exclusions separately, with the user instruction or product scope
that excludes them. Cover every remaining core surface in both runtime contexts.
Bind every verified claim to its environment, input, source/artifact identity,
observed outputs, refusal/recovery proof where relevant, and retained evidence.
Split local simulation from live integration and smoke coverage from full
acceptance. A surface can have verified local cases and a blocked external case.

Full coverage accounting means every surface has an explicit outcome. Full
acceptance additionally requires every required surface to pass its real gate.
Do not call a run fully verified while required rows are failed, blocked or not
run. Preserve narrow passes and the exact missing proof. Historical evidence
may be reused only with an explicit identity/prerequisite comparison; label it
as reused rather than a fresh run.

Use facts, inferences and derivations for the research/decision report. Retain
the initial failures when a repair is made. Review the assembled change, run the
required source gate, and land coding increments through the normal rebase and
fast-forward process. A queue entry is unfinished delivery. Release preparation,
global installation, external publication and runtime permission changes retain
their separate authority.

This inventory covers the stack's supported engineering product. It does not
create claims of exhaustive input coverage, hosted/distributed queue support,
power-loss safety, Windows support or universal agent productivity.
