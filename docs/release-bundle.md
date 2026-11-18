# phi9t_stack installation bundle

This bundle contains the shared native skill directories for Codex and TRAE CLI,
their complete resources, the reversible installer and release notes. `release.json` identifies the version, exact source commit/tree,
file hashes and modes. The installed core also carries its distribution identity
in `skills/phi9t/references/distribution.json`.

Use Python 3.9+ in a managed uv virtual environment on a POSIX host. From this
extracted directory, choose the agent root your runtime discovers:

```bash
python scripts/stack.py check
python scripts/stack.py install --target "$HOME/.agents"
python scripts/stack.py verify --target "$HOME/.agents"
```

Refresh runtime skill discovery after installation;
file verification alone does not establish runtime discovery or instruction quality.

Updates use the same installer from the chosen newer bundle. Unmanaged collisions
and edited owned files refuse replacement. Preserve and inspect customizations
before considering `--replace-modified`. Legacy retirement is a separate,
explicit `--migrate-legacy` operation; it removes only exact known old identities.
Retain the printed backup ID and the target's `.phi9t/backups` directory.

To undo an installation, use the installer with its target and backup ID:

```bash
python scripts/stack.py restore --target "$HOME/.agents" --backup BACKUP_ID
python scripts/stack.py recover --target "$HOME/.agents"
```

Recovery handles an interrupted installation and refuses unexpected later edits.
Keep old bundles and installation backups until the new version is accepted.
The source checkout is needed for the full test suite; this is a curated install
bundle, not a copy of local research, tests or execution state.

Compare the archive SHA-256 with a value obtained through a trusted publication
channel before unpacking or executing it. Hashes detect changed bytes; they do
not authenticate a publisher by themselves. `scripts/release.py verify` checks
archive structure and file identity without executing bundled code. Its `unpack`
command verifies before writing into a new directory. Its `qualify` command
explicitly executes the bundled installer in scratch state.

Read this version's notes under `releases/` and the retained third-party notice
in `docs/provenance.md`. Release-candidate labels and platform limitations remain
part of the release contract.
