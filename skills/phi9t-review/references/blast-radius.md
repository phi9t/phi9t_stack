# Prove the safety assumption

Name the fact that must be true for this change to be safe. Examples: a callback
cannot outlive its owner, all wire-format consumers accept the new representation,
a dependency interprets a flag as expected, or a rejected input writes nothing.

Trace indirect consumers, persisted data, lifecycle order, pinned dependency
implementations and failure cleanup. Grep finds direct references; it cannot
establish the whole contract. Run the smallest real caller or dependency probe
that could disprove the fact. Compare expected and observed output and effects.

Bind evidence to the candidate and dependency version. Check a meaningful bad
case as well as the valid path where rejection matters. Report exactly which
boundary remains untested. A hypothetical concern is a research question until
source or execution shows a concrete consequence.
