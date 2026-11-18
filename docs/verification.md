# Verifying phi9t_stack

The supported behavior is preparing complete method packages for an agent,
updating them without silent data loss, checking their identity and restoring
prior state. The installer is the control tool. The table below is the behavior
map; dated receipts in `docs/evidence/` describe actual runs.

The full dogfood contract and surface inventory live in
[dogfooding](dogfooding.md); source-gate coverage is one part of that contract.
Instruction behavior is checked separately from package integrity: a realistic
task trial qualifies that task and handoff, not every domain or a general
improvement in agent quality.

## Readiness

Use a clean or understood checkout, Python 3.9+, uv 0.7.8+, Bash and a POSIX
filesystem. Run `uv sync --locked` to create the repository's managed `.venv`
from the committed development dependencies. Activation is optional. The native Python path is the
exception used for this stack's local package checks; runtime workloads follow
the shared [execution defaults](../skills/phi9t/references/architecture.md#2-insula-execution).
Inspect `git status --short` before a change. Run `./scripts/verify.sh` for source
validation and the isolated behavior suite. The gate also enforces Ruff
formatting/lint, ty on the installer, release and landing programs, and ShellCheck on
the shell entrypoints. Existing untyped test fixtures are outside the type-check
scope. All maintained Python is covered by Ruff;
exploratory recipes are outside this source gate. The gate uses `uv run --locked`,
so stale dependency metadata refuses instead of rewriting the lockfile.
Development tools may download during setup. Tests do not contact a network service or
modify the user's agent root. A standalone installation bundle still needs only
managed Python; its users do not need the source development tools.

Run module-level fault tests from their source owner root. The normal source
gate already selects the repository root. The copied bundled-installer corpus
also selects its own root and asserts that the imported `scripts.stack` is the
actual copied driver, rather than loading a file through an import workaround.
Ruff enforces top-level imports for maintained Python; exploratory recipes stay
outside the normal source gate.

## Behavior map

| Journey | Starting state and action | Observable proof and refusal | Automated exercise |
|---|---|---|---|
| Bootstrap source checks | Start from a fresh source copy without `.venv`; run `uv sync --locked`, then `./scripts/verify.sh`, including from another working directory. | Pinned tools and the actual behavior suite pass. Changed dependency metadata refuses with the lockfile and unrelated files preserved. | Fresh-environment qualification in dated bootstrap evidence |
| Vendored skills stay pinned | Run `vendor.py check`; then edit a vendored file. | Unedited trees match `vendor.json` hashes and ship with their MIT notice. An edited file is named and refuses with exit 1. | `RepositoryTests.test_vendored_trees_match_pins_and_refuse_edits` |
| Install and repeat | Run `stack.py install --target SCRATCH/agent`, then repeat with identical source. | All selected package bytes and modes match. Repeat reports `unchanged` and creates no backup. A missing reference or unmanaged collision refuses before any package write. | `StackTests.test_install_runs_packaged_driver_and_repeat_is_noop`, missing-reference and collision tests |
| Update and verify | Install, edit owned scratch content or a driver's executable bit, run verify and install. | Verification detects drift and ordinary update refuses it. Explicit replacement backs up the actual customization. | Drift and executable-mode tests |
| Retire previously owned tools | Update a manifest containing an omitted package. | Modified owned content refuses; unchanged files are removed with a backup. Restore returns the prior files and manifest. Unmanaged content remains untouched. | `StackTests.test_removed_owned_package_is_backed_up_and_restorable` |
| Restore | Use the backup identity from a changed installation. | Prior bytes, modes and manifest return; unrelated files remain. A later edit refuses restoration. Restore generates its own undo backup. | First-install restore and later-edit tests |
| Preserve persisted installer contracts | Read a saved schema-2 manifest and restore a saved schema-1 backup emitted before the data-model conversion. | Manifest bytes and private permissions stay exact. Absent, empty and binary files remain distinct; prior user permission bits return. | Baseline fixture and binary/empty restoration tests |
| Refuse malformed recovery records | Restore or recover with a wrong target, mismatched path sets, unsafe late path or malformed late snapshot. | Every entry is validated before managed writes. Existing bytes, modes and pending state remain intact. | Invalid transaction metadata/path and malformed late-snapshot tests |
| Preserve backup wire matching | Restore/recover records with equivalent noncanonical base64 spellings. | A noncanonical recorded after-state still refuses; an allowed canonical recovery alternative and noncanonical before-state remain accepted. | Noncanonical after/before and canonical-alternative tests |
| Recover interruption | Use an interrupted transaction's pending record. | Only before/after states can be recovered. Unexpected user edits are preserved with the pending record. Retry restores prior state. Ordinary write failure also rolls back completed writes. | Interrupted-install and partial-write tests |
| Coordinate writers | Another invocation owns the target's installer lock. | Second writer refuses without package writes. It succeeds after release. | Writer-lock test |
| Retire legacy files | Known old assets match `legacy.json`; select `--migrate-legacy`. | Matching files retire and can be restored. Modified legacy files stop the entire operation and remain unchanged. | Exact-identity legacy test |
| Land direct/queued work | Initialize a scratch repository lane with external acceptance scripts; submit immutable commits and run the direct or queued path. | Actual output files and linear mainline history match accepted candidates. Both paths share a lock. Failed candidates do not land; unrelated eligible work can continue. | `LandingTests` real CLI/Git journeys |
| Refuse unsafe/stale landing | Move a source branch, checker target, destination or verification HEAD; create dirty/ignored state, conflicts or hidden index changes. | Pins preserve the original subject. Stale or altered evidence refuses/blocks; source worktrees and destination work remain intact. | `LandingTests` drift, preservation, conflict and version cases |
| Recover interrupted landing | SIGKILL the CLI during submission, checking and before/after real Git landing. | Identical interrupted submission can resume. Surviving checks retain the lane lock. Attributed landing reconciles without duplicate commits; uncertain effects block until explicit operator resolution. | `LandingTests` interruption and contention cases |
| Build a versioned release | Export a committed mainline source twice with explicit version/notes. | Archive bytes and SHA-256 match across builds; dirty/replacement objects and private research cannot alter the export. Existing output and conflicting tags refuse. | `ReleaseTests` reproducibility, source and collision cases |
| Inspect and unpack releases | Verify expected checksum, manifest, paths and file types before writing a new directory. | Changed bytes, duplicate/unsafe members, links, malformed manifests and oversized payloads refuse; existing destinations remain intact. Truncated/corrupt gzip returns a JSON refusal for verify, unpack and qualify before output creation. | `ReleaseTests` archive rejection and damaged-gzip cases |
| Qualify and roll back a bundle | Run the actual archived installer in owned scratch targets for the complete skill catalog. Upgrade between two releases and restore. | Installed bytes/modes and helper launch work; repeat is a no-op; rollback restores the former distribution identity and preserves unrelated files. | `ReleaseTests` qualification and upgrade cases |

The suite drives the real Python CLI, writes real temporary files and executes
a packaged shell driver. The full-catalog test installs this checkout's actual
skill catalog, checks installed bytes and modes, runs the packaged landing
helper and restores the installation.
Landing tests invoke the real packaged Python CLI and Git on macOS. Git wrappers
only hold execution at an observed boundary; they still call real Git. These
tests do not qualify Linux execution, detached descendants, power loss,
network filesystems or a hosted/distributed merge queue.
The interruption test reconstructs a partial on-disk transaction; the write-fault
test injects a failing filesystem boundary. They do not simulate a power loss.

Canonical manifests and backups emitted by the prior installer are the persisted
compatibility contract. Manually edited noncanonical before-snapshot encodings
are decoded and serialized canonically by the new records. Byte-identical writes
may be omitted, and changed-file counts or subsequent undo behavior may differ
for those edited states. The exact recorded after-state comparison remains at
the persistence boundary; it is not replaced by decoded-byte equality.

## Follow one journey directly

Use an owned temporary root. From the checkout:

```bash
trial=$(mktemp -d)
python3 scripts/stack.py install --target "$trial/agent"
python3 scripts/stack.py verify --target "$trial/agent"
python3 scripts/stack.py install --target "$trial/agent"
```

Retain the install output and its `backup` identity. Inspect a documented
reference under `$trial/agent/skills/`. Add a line to an installed reference,
rerun verify and observe failure. Ordinary install must refuse the edit too.
Restore that line to its prior bytes before restoring the first installation,
or use explicit replacement and inspect its backup. Run:

```bash
python3 scripts/stack.py restore --target "$trial/agent" --backup BACKUP_ID
```

Check first-install files are absent and unrelated fixture files remain. Keep
logs outside the restored agent root so cleanup cannot erase the proof. Remove
only the trial root when its evidence is retained.

## Maintaining the packet

After behavior changes, source-trace and rerun affected journeys. A complete
audit covers every declared row and the required gate. Classify discrepancies
as documentation drift, harness defect, prerequisite gap or product regression.
Keep expected behavior intact when implementation fails. Record the candidate,
commands, exits, observations, skipped coverage and cleanup in the dated receipt.

File-package verification does not prove runtime discovery. Confirm `phi9t`
appears in a freshly refreshed Codex or TRAE session at the chosen target before
retiring the old installation. Windows and remote or
GPU execution are not qualified by this packet. Independent task trials test
whether the guidance is usable; they do not establish a controlled productivity
improvement over the old stack.
