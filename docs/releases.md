# Release phi9t_stack

Release one version of the shared skills, required resources and installer. Runtime permissions and discovery settings stay outside the bundle.
The release tool prepares local artifacts; it never tags, pushes, publishes,
installs into a user-global agent root.

The release CLI emits JSON. Successful operations exit 0; an operational
refusal exits 1 with `status: "refused"` and a reason. Invalid command syntax
uses argparse's exit 2. These statuses belong to this program's contract; the
landing helper has its own exit conventions.

## Version and freeze

Change `VERSION` and add `releases/<version>.md` in a task worktree. Use semantic
versions: patch for compatible corrections, minor for compatible new methods or
capabilities, major for incompatible names, contracts or installation behavior.
Describe material instruction changes as well as executable changes. Use `-rc.N`
while qualification gaps remain. The initial version is `0.1.0-rc.1`.

One published version identifies one commit and archive digest. Never move its
tag or replace its artifact. A tagged version cannot be built from another
commit. Unpublished candidate builds can repeat in new output directories;
qualification always binds the exact digest.

## Prepare and qualify

1. Review the complete change. Run `uv sync --locked`, then `./scripts/verify.sh`
   for pinned format/lint/type/shell checks and the behavior suite. Substantial method changes need realistic
   task evidence beyond package metadata.
2. Land on mainline through the normal guarded process. Freeze the release commit.
3. Build from that exact commit into a new output directory:

   ```bash
   python scripts/release.py build --repo . --mainline main \
     --ref RELEASE_COMMIT --output /absolute/new-release-directory
   ```

   Use the actual mainline name. The source must be reachable from it. Export
   ignores dirty/untracked files and Git replacement objects, and refuses active
   legacy Git graft overrides. The reproducible
   tar.gz is accompanied by `SHA256SUMS`, `release.json` and release notes.
   Research, historical evidence, tests, credentials, agent state and private
   machine inventories are excluded. Retained third-party notices are included.
4. Verify and qualify those bytes:

   ```bash
   python scripts/release.py verify --archive /absolute/bundle.tar.gz \
     --sha256 EXPECTED_SHA256
   python scripts/release.py qualify --archive /absolute/bundle.tar.gz \
     --sha256 EXPECTED_SHA256 --output /absolute/new-qualification-directory
   ```

   `verify` is static. `qualify` explicitly executes trusted bundle code in
   scratch state: unpack, skill installation, byte/mode checks, repeated
   install no-op, helper launch and restore with unrelated files preserved.
   `qualification.json` binds source commit and archive digest. This does not
   replace source tests or establish runtime discovery or instruction quality.
5. Review notes, source-gate evidence, qualification and checksums together. Keep
   deliverables outside a worktree that will be reclaimed. Record their exact
   identities in the project's release record. Committing the record does not
   change the frozen release source; do not rebuild from a newer tip by accident.

## Promote and publish

Use existing owner/publication authority. Artifact preparation does not authorize
a remote push or public release. Once authorized, create an annotated
`v<version>` tag on the frozen commit and publish the archive, checksum, notes
and receipt through the configured hosting service. Check downloaded bytes
against the recorded SHA-256. Do not invent a remote or select a new upload service.

Stable claims must name qualified platforms and runtime versions. Current
evidence covers macOS local file and landing operations. Linux landing, Windows,
hosted queues and runtime discovery need separate qualification.
Keep prerelease labels and explicit gaps until those claims are supported.
Failed required gates block promotion; changing a version does not make them pass.

## Roll out and recover

Obtain the archive and expected SHA-256 from a trusted source. Hashes establish
integrity against that value, not publisher authenticity by themselves. `unpack`
verifies paths, file types, inventory, modes and hashes before writing a new root:

```bash
python scripts/release.py unpack --archive /absolute/bundle.tar.gz \
  --sha256 EXPECTED_SHA256 --output /absolute/new-package-directory
```

Use its `scripts/stack.py install --target AGENT_ROOT`, then `verify` on the
same target. Refresh the runtime and check discovery. The bundle README
contains standalone instructions. Installed
`phi9t/references/distribution.json` identifies version and source; development
checkout installations need not carry release metadata.

Retain the backup ID, previous bundle and `.phi9t/backups` until rollout is
accepted. Roll back with `stack.py restore --target AGENT_ROOT --backup ID`;
later user edits still refuse replacement. For interrupted installation, use
`recover` rather than deleting metadata or blindly reinstalling. Supersede a bad
published release with a new version and advisory, never a rewritten version.
