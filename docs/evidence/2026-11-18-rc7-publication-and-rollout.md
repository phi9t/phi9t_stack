# rc.7 publication and local rollout — 2026-11-18

Release source: `3e82d90d6ed7992793451f8a1982b4ee760c4020`. This receipt is committed after the frozen
release source; it does not rebuild or retag that version.

Archive SHA-256: `6b8e5f77c62b9ed89b6c22182fd61831b1af5881bd33bd9cd9b0f6d5fcedb689`.
Published prerelease: [0.1.0-rc.7](https://github.com/phi9t/phi9t_stack/releases/tag/v0.1.0-rc.7).
The machine-readable [release record](../../releases/0.1.0-rc.7-record.json)
binds all six asset identities, the source tree, qualification and runtime results.

## What was delivered

The implementation branches were already incorporated into the preserved
pre-public release lineage. Current public main contains the native methods and
pinned vendor packages, plus native-only release fixtures, hermetic behavioral
tests and atomic vendor sync. The divergent absorption research contains no
implementation. The owner chose to publish the current stack and keep the
router/worker-role redesign separate. Existing research and historical branches
were preserved; private history and research were not merged into public main.

The release preparation was delivered through `phi9t-land`'s direct path using
a clean integration checkout and an externally pinned acceptance script. The
source gate passed all 69 tests in the task worktree and on the exact integration
candidate before fast-forward landing. The existing source-checkout environment
was preserved. A new external managed uv environment was bootstrapped with the
locked dependencies. Its first download attempt failed certificate validation;
using the system trust store resolved setup without disabling verification.

Two exports of the same frozen commit produced identical archive bytes. Actual
`verify`, `qualify`, and `unpack` calls passed. Qualification exercised bundled
installation, bytes/modes, repeat no-op, helper launch and restore while preserving
an unrelated file. An annotated version tag and main were pushed together. Six
assets were published, downloaded again and compared byte for byte. Public
qualification commands redact local execution paths; source and digest fields
are unchanged.

The downloaded bundle was installed into the shared Codex/TRAE user root and
Claude Code's separate user root. Both `verify` calls checked 197 managed files;
both repeated installs returned `unchanged`. Each update retained an installer
backup. Private backup identities and profile/configuration snapshots remain
outside the repository. No `--replace-modified` or legacy migration was used.

## Discovery and preservation

The catalog has 17 top-level packages: fifteen native methods, `phi9t-pstack`,
and `phi9t-pocock`. It contains 86 entrypoint files including nested vendor
resources; registering the 17 package routers does not prove every nested
method's instruction quality or automatic registration.

Fresh Codex 0.167.0-alpha.4.1 and TRAE CLI 0.215.0 app-server processes used their
actual `skills/list` interface with `forceReload`. In a scratch Git project,
project packages were absent, installed from the exact qualified bundle,
discovered at exact project paths, restored, and confirmed absent by fresh
processes. Neither runtime reported discovery errors. Codex enabled all 17
scratch packages. TRAE discovered all 17 but inherited the live policy for the
14 disabled focused native methods; the router and both vendor routers were
enabled. The all-enabled TRAE expectation was not met and was not forced.

Fresh live-profile checks discovered all 17 packages in the shared user root.
Both runtimes preserved the previous native-method enablement: the main router
is enabled, 14 focused methods remain disabled, and both new vendor routers are
enabled. No runtime permission or enablement settings were edited. A fresh
Claude Code 2.1.327 CLI initialization listed all 17 package commands; inference
tools and MCP servers were disabled for that catalog probe. This is discovery
evidence, not a Claude method-quality trial.

A private before/after inventory covered 7,583 existing profile files and
symlinks. Outside managed package paths, the only changed pre-existing file was
Claude's runtime cache/usage state; only cache/experiment/plugin-usage keys
changed. That state was retained. Runtime settings files, unrelated skill files
and customized legacy TRAE commands were preserved. Existing sessions may need
a refresh or restart to load the expanded catalog.

## Product-surface accounting

This is a release and rollout qualification, not complete dogfood acceptance.

| Surface | Outcome and limit |
| --- | --- |
| Engineering methods | **Not run** as a complete fresh set. This delivery used the router, landing and verification methods; it does not establish all method behavior. |
| Routing and composition | **Not run** for the proposed redesign. Existing composition shipped unchanged. |
| Installer | **Verified** for the real source suite, qualified bundle, scratch restore and both live upgrades/no-ops. Modified global customizations were not replaced. |
| Release | **Verified**: two identical builds, static verification, trusted qualification, verified unpack, six published/downloaded asset comparisons. Source tests also cover malformed/refused inputs. |
| Local landing | **Verified** on macOS through the source suite and actual guarded fast-forward delivery. |
| Salvage and actual integration | **Verified**: branch/worktree inventory, preservation of separate research, and actual mainline delivery of the release candidate. |
| Source development | **Verified**: fresh managed environment, locked sync, format/lint/type/shell checks and 69 tests on the frozen integration candidate. Extra fresh stale-lock/style-fault bootstrap trials were **not run**. |
| Codex discovery | **Verified** scratch absent/install/discover/restore/absent and live discovery, with existing live enablement preserved. |
| TRAE discovery | **Verified** registration lifecycle and live discovery with policy preserved; the full all-enabled variant is **blocked** by the existing disabled-method policy, which this task preserves. |
| Execution and portability | **Verified** for local macOS arm64, managed Python 3.13.15 and admitted native Git/runtime tools. Linux, Windows and remote machines were **not run**. |
| Distribution and promotion | **Verified**: authorized public prerelease, annotated frozen tag, downloaded-byte integrity, local installations and retained rollback backups. |

The release remains a prerelease. Its archive remains bound to the frozen source
above even when this receipt advances mainline. Follow `docs/releases.md` for
rollback; do not move the tag or replace the archive.
