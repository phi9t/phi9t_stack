# Architectural defaults

These are the user's shared preferences for arranging, explaining and running
programs. Apply them when designing a new system or changing an existing
boundary. Preserve the target's explicit contracts and supported compatibility;
an unrelated task does not authorize a repository-wide migration.

## 1. Semantic ownership

Directories express the concept or responsibility they own. Keep related
implementation, data contracts, tests and explanation near that owner. A concept
can span Python, Rust and native code. Build graphs and package managers project
onto the architecture rather than partitioning it by language or execution stage.

Give each invariant one owner and make dependency direction explicit. Prefer
cohesive modules with small interfaces over pass-through layers or arbitrary
file-size splits. Module tests belong beside their source; repository-policy and
cross-boundary integration tests may have a shared home. Keep established import
roots and public identities stable through a deliberate migration.

## 2. Insula execution

An Insula is the default unit for running a command. Most commands run in a
Linux Insula with explicitly captured tools, packages, dependencies, projections
and runtime policy. Use the target's supported launcher and admission path.

The native exceptions are Python running in a managed uv virtual environment and
native Rust binaries. For Rust builds, inspect free space and existing build/cache
sizes first, reuse compatible artifacts when safe and bound parallelism and
output growth. Preserve other tasks' state; cleanup targets only owned outputs.
Do not multiply large build trees merely to obtain another checkout.

Insula supports Linux. When required execution is unavailable on the current
host, use an authorized Linux route or report the specific missing capability.
A wrapper written in Python or Rust does not exempt an arbitrary payload from
its execution requirements.

| Term | Meaning |
|---|---|
| Insula | The complete bwrap-based hermetic/capsulated execution mechanism |
| Insula contract | The resolved specification for its inputs, projections and runtime policy |
| Insula instance | One live realization of that contract |
| Rootfs | The frozen base filesystem artifact |
| Estate | The filesystem layout/projection contract: backing, access, ownership, persistence and sharing |
| Hermetic/capsulated | Required tools and dependencies are explicitly captured; network access is a separate policy |

Insulas can align with program delivery boundaries and can nest. Declare each
child's dependencies, writable state, resources and lifecycle. One Insula may
host cooperating processes; a larger system may compose several Insulas. Choose
the arrangement around ownership, delivery and fault domains.

## 3. Program contracts

Prefer programs that compose through the data they accept and produce: CLI
requests/results, pipes, files, versioned artifacts or service contracts. A
consumer learns the provider's contract rather than importing private internals
or depending on the layout of its storage.

Make the high-level data model explicit: meaning, identity, valid states, errors
and compatibility. Keep state and failures within their owner; define how an
uncertain or failed result crosses the boundary. Data contracts support fault
isolation, but a schema alone does not contain processes or shared state.

Use a program boundary when it separates a meaningful responsibility, delivery
unit, lifecycle or fault domain. Ordinary internal functions need not become
CLIs or services. Shell and CLI entrypoints remain thin; substantive policy lives
in the owning importable modules.

## 4. MTS legibility

An MTS, a member of technical staff, should understand the architecture first
through its programs, CLIs, services and data models. Provide a newcomer map of
owners, inputs/outputs, execution boundaries and useful compositions. Trace one
real operation, including where failure is owned, before touring implementation.

Owner documentation explains contracts, invariants, entrypoints and tests. Keep
that map current with structural changes. Put accepted decisions, maintained
facts and historical run evidence in their distinct existing homes. Use the
project's glossary; detailed source remains discoverable beneath the map.

## 5. Unix composition and durable coordination

Start with focused programs that can work together. Ordinary pipes, CLI calls,
artifacts and service requests are sufficient for simple compositions.

Use durable workflow coordination when persisted progress, dependencies,
parallelism, retries, timers, cancellation or recovery are actual requirements.
Programs own the work, Insulas provide execution and workflows coordinate
progress. A unit of work declares its input, output, identity, effects, resources
and completion/failure behavior. Workflow and activity code can cross languages
through those contracts.

Recovery distinguishes completed, pending, failed and uncertain work. Reuse
recorded results where valid; give retries stable identities and reconcile or
deduplicate external effects. A result file's presence alone is not authoritative
completion. An activity attempt, an Insula instance and a logical work unit have
different identities. Specify their relationship rather than assuming one-to-one.

A Temporal-like model does not require Temporal infrastructure. Use an existing
coordinator when needed; a local single-binary/SQLite design is one possible
deployment, not a dependency every program must acquire. Documentation or a
design reference does not establish that a particular engine is production-ready.

## Python engineering

Python should meet a high standard of readability, correctness and maintainability.
Start with explicit data models and compose small functions and collaborating
objects around them. Prefer composition over inheritance. Use inheritance when
a genuine substitutable relationship or required framework contract justifies
it, rather than to share a few methods or create a configurable base class.
Avoid deep class hierarchies, mixin stacks and speculative extension frameworks.

Model domain concepts and valid states directly. Use typed records, dataclasses,
enums or the project's established modeling tools where they make the contract
clearer. Keep data structures proportionate to the problem; do not wrap every
value in a class. Use precise type annotations at meaningful interfaces and
keep unvalidated dictionaries or dynamic attributes at external boundaries.

Keep policy in cohesive modules and functions, with I/O and resource ownership
explicit. Pass dependencies directly instead of hiding them in mutable globals,
service locators or import-time effects. Make pure transformations easy to test.
Validate external data once at its boundary; catch specific exceptions where
recovery or useful context belongs. Use deterministic resource cleanup and
explicit cancellation/lifetime handling for concurrent work.

Use clear names, straightforward control flow and the repository's formatting,
linting and type-checking conventions. Test observable behavior, failure paths
and composed operations rather than incidental implementation shape. Run Python
in managed uv environments as specified above.

Follow standard Python conventions and the
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html),
subject to the user's explicit rules here. Use four-space indentation. Use
[PEP 420 implicit namespace packages](https://peps.python.org/pep-0420/) for
namespace layout; do not add boilerplate `__init__.py` files merely to make
directories importable. Configure package discovery and tooling for the actual
repository roots. Preserve intentional package initialization and public APIs
when changing existing code rather than deleting them mechanically.

Use [Ruff](https://docs.astral.sh/ruff/) for both formatting and linting, including
import ordering. Keep its configuration in the project's existing configuration
owner. Run `uv run ruff format --check .` and `uv run ruff check .` from the
repository root, or the repository's equivalent scoped check entrypoints.
Use `uv run ruff format` to apply formatting. Formatter output governs mechanical
layout; lint fixes must preserve behavior and the unconditional-import policy.
Do not enable competing formatters or lint rules that fight the formatter.

Use additional checks where they detect meaningful defects: the repository's
static type checker, security checks and dependency audits as appropriate.
Declare their dependencies through uv and integrate relevant checks into the
normal verification path. Reuse established tools and choose complementary
coverage instead of accumulating redundant linters or blanket suppressions.

Imports are unconditional and absolute, based on the repository root and its
established package roots. Do not use conditional imports, import fallbacks,
optional-dependency probes or `TYPE_CHECKING` import branches. Do not modify
`sys.path`, inject `PYTHONPATH` or use file-location import tricks to make code
load. Use uv to declare, resolve and install dependencies, including development
dependencies, and run through the repository's supported environment and entrypoints.
A missing dependency or broken package layout is a setup defect to fix at its
owner, not a reason to add an import workaround. This applies to scripts and
tests as well as production modules.

Exploratory recipes retain their
freedom of form; codification brings useful behavior up to this production bar
without imposing a class architecture on the original experiment.

## Bash engineering

Bash is an allowed implementation language. Follow conventional Bash coding
style and the repository's established conventions. Use an explicit Bash
shebang, clear names and functions, quoted expansions, and arrays for commands
and argument lists. Handle exit statuses deliberately; make pipeline failures,
temporary state and cleanup behavior explicit. Keep scripts readable and avoid
shell quoting tricks that hide data flow or change argument boundaries.

Lint Bash scripts with ShellCheck, using the repository's check entrypoint or
`shellcheck path/to/script.sh`. Resolve findings; keep any necessary suppression
narrow and explain its reason. Use existing shell formatting tools when the
repository provides them. Linting gives early feedback; exercise actual script
behavior and relevant failure paths before accepting executable changes.

Permission to write Bash does not change command execution policy: Bash scripts
and their payloads use the required Insula path unless an explicit exception
applies. Exploratory scripts retain freedom of form while preserving correct
quoting, argument handling and resource ownership.
