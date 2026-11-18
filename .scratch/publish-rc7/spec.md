# Publish and roll out the current stack

Status: resolved
Owner: Codex integration owner

User authorized landing relevant active work, publishing, and updating agents.
Baseline public main: ff9e247726117646ca289a2b2b1da9be6d95b595.
All implementation branches are contained in the preserved private release
lineage. Public main retains their runtime implementation and adds three
hardening commits. No dirty active worktree was found. The divergent absorption
research branch contains proposals only and remains preserved; its unimplemented
router/worker-role design is outside this release candidate.

Deliver rc.7 through phi9t-land, qualify the exact deterministic archive, publish
an immutable prerelease, verify downloaded bytes, install into the discovered
shared and Claude roots without replacing modifications, then check discovery.
Retain local backup identities and report every dogfood surface explicitly.
Do not import private research/history or change runtime permissions/enablement.

## Resolution

Release source `3e82d90d6ed7992793451f8a1982b4ee760c4020` landed through
phi9t-land, passed the full 69-test gate, and was published as annotated
`v0.1.0-rc.7` with a qualified reproducible archive. Six downloaded assets matched
the originals. Shared Codex/TRAE and separate Claude installations verified 197
files each and repeated as no-ops. Fresh processes discovered all 17 packages.
Existing enablement and modified legacy commands were preserved. The redesign
remains separate, as the user selected.

The dated docs/evidence receipt and releases/0.1.0-rc.7-record.json retain public
identities and qualification limits. Local installer state and the private rollout
receipt retain the backup IDs. Full-method dogfood and other platforms remain
unqualified. The frozen release is not rebuilt from the later evidence commit.
