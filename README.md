# phi9t_stack

A small engineering toolkit for Codex and TRAE CLI. One shared core supplies
focused methods; the active runtime supplies tools, model choices and execution
policy. Project instructions remain authoritative.

## Use

Ask for `$phi9t` with a task, or select a focused method directly:

| Skill | Use it for |
|---|---|
| `phi9t` | Choose the method and carry a task through to evidence |
| `phi9t-scout` | Explore unfamiliar ground and identify promising leads |
| `phi9t-codify` | Turn exploratory recipes into maintained production code |
| `phi9t-land` | Salvage code and land through one guarded direct/queued lane |
| `phi9t-understand` | Trace behavior, ownership and recorded rationale |
| `phi9t-explain` | Explain technical behavior in STE-inspired English with restrained Hemingway rhythm |
| `phi9t-research` | Investigate a question and retain primary-source evidence |
| `phi9t-design` | Choose interfaces, data structures and module boundaries |
| `phi9t-debug` | Reproduce, isolate and repair a failure |
| `phi9t-review` | Review requirements and prove safety assumptions |
| `phi9t-verify` | Check facts and derivations, exercise results and maintain a behavior map |
| `phi9t-bootstrap` | Leave a repository usable by the next agent |
| `phi9t-correct` | Turn recurring mistakes into enforced constraints |
| `phi9t-benchmark` | Establish or challenge a performance claim |
| `phi9t-prototype` | Answer a bounded design or runtime question |

For an unfamiliar area, `$phi9t-scout` returns a map, supported leads and the next
questions worth investigating. Scout and prototype can call research as a scoped
subroutine while retaining ownership of their missions.

For an open question, `$phi9t-research` returns a cited finding, its limits and
the decision it supports. When the answer needs execution, `$phi9t-prototype`
builds and runs a bounded probe with retained inputs, outputs and a verdict.
Measured findings return to the canonical research or design note. Use either
method directly; a small task does not need a mandatory research phase.

For mainline integration, `phi9t-land` includes an optional
[local landing CLI](skills/phi9t-land/references/local-lane.md). Both direct and
queued work share a repository lock, pinned candidate/check identities and
recoverable operation records. Use the repository's existing qualified landing
service where available. The bundled fallback never pushes or installs a daemon.

Skills load only the references relevant to their branch. There are no fixed
model tables, required agent quotas, personas or automatically installed hooks.

The shared [architectural defaults](skills/phi9t/references/architecture.md)
define semantic ownership, Insula execution, program/data contracts, MTS
legibility, and Unix composition with durable coordination where needed.

## Check and install

For a versioned bundle, see [releases](docs/releases.md). Releases identify the
exact source commit, include file hashes and modes, and exercise the actual
bundled installer before promotion. Local checkout installation remains supported.

The installer requires Python 3.9+ in a managed uv environment and a POSIX
filesystem. It has no third-party Python runtime dependencies. For source
development, use uv 0.7.8+ and the committed `pyproject.toml` and `uv.lock`:

```bash
uv sync --locked
./scripts/verify.sh
uv run --locked python scripts/stack.py install --target "$HOME/.agents"
uv run --locked python scripts/stack.py verify --target "$HOME/.agents"
```

`uv sync --locked` creates `.venv` with the pinned development tools. Activation
is optional. The verification script selects the repository root and runs Ruff
format/lint checks, ty on the typed release and landing programs, ShellCheck,
package validation and the isolated behavior suite. It refuses a stale lockfile.
Run `uv run --locked ruff format scripts tests skills` to apply formatting.
Exploratory recipes under `docs/research/` retain their freedom of form; they
are excluded from release bundles.
For an intentional tool update, change its dev dependency, run `uv lock`, then
review the lockfile and rerun the gate. `VERSION` remains the release version;
the non-package project's `0.0.0` is development workspace metadata.

Choose a target root the active runtime discovers. Installation copies complete
native skill directories into `<target>/skills/`. It does not edit runtime
settings, credentials, AGENTS.md or hooks. Restart or refresh skill discovery,
then confirm `phi9t` is visible before retiring the previous stack. Codex and
TRAE integration notes live with the entrypoint's runtime references.

`install.sh` is a thin wrapper for the install subcommand. Every target must be
explicit. Unmanaged collisions refuse installation. Updates also refuse missing
or edited owned files; inspect the changes before choosing `--replace-modified`.
That flag backs up the observed prior state. It never overrides an unmanaged
collision or a modified legacy file.

## Restore and recover

Every changed installation prints a backup identity. Repeating an identical
installation returns `unchanged` without producing another backup. File content
and permission modes are checked, including executable resources.

```bash
uv run --locked python scripts/stack.py restore --target "$HOME/.agents" --backup BACKUP_ID
uv run --locked python scripts/stack.py recover --target "$HOME/.agents"
```

Restore reinstates the files and manifest from before that transaction. It
refuses to overwrite later edits. Restore itself produces an undo backup.
Recover is for an interrupted transaction; it refuses unexpected file state and
leaves the pending record intact for inspection. Backups live under
`<target>/.phi9t/backups/`; keep them while a rollback may be needed. Empty package
directories may remain after restoring a first installation.

The manifest records owned files only. Unrelated files are preserved. A lock
serializes this tool's writers. Recovery covers interrupted local processes;
this is not a guarantee against power loss or hostile concurrent filesystem edits.

## Maintenance

[Verification](docs/verification.md) maps the supported journeys and their proof.
[Landing lane](docs/design/2026-10-29-landing-lane.md) records the local landing design.
[Provenance](docs/provenance.md) distinguishes adapted methods and retained tools.
[Release procedure](docs/releases.md) covers versioning, artifacts, promotion and rollback.

```text
skills/         fifteen phi9t method packages plus the vendored phi9t-pstack and phi9t-pocock
                skill trees (pinned in vendor.json), with conditional references
scripts/        source validation and reversible installation
legacy.json     exact identities of retired files (empty by default)
tests/          isolated behavioral checks
docs/           current design and verification
```
