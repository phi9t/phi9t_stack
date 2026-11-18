# Issue tracker

Issues and specs live in this repository as Markdown.

- Feature directory: `.scratch/<feature-slug>/`
- Spec: `.scratch/<feature-slug>/spec.md`
- Tickets: `.scratch/<feature-slug>/issues/<NN>-<slug>.md`,
  numbered from 01, with one file per ticket.
- Record triage state as a `Status:` line near the top.
  Use the vocabulary in `triage-labels.md`.
- Append discussion under `## Comments`.

When a skill says "publish to the issue tracker", create or update the
corresponding local file. When it says "fetch a ticket", read that file.
Preserve existing discussion when updating it.

For implementation, claim a spec or ticket with `Status: in-progress` and an
owner. Close completed work with `Status: resolved` and a `## Resolution` section
that records the accepted commit, verification evidence and remaining limits.
These execution states complement the five triage roles in `triage-labels.md`.
