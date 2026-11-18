# Codex adapter

Use the tools exposed in the current session. Prefer built-in file edits,
managed worktrees, connectors and native agent coordination where available.
Inspect repository instructions before changes. Use the configured model and
reasoning defaults unless the user or an applicable instruction chooses them.

Skills are native directories with SKILL.md and relative supporting resources.
This repository installs the same packages into the selected agent root's
skills/ directory. Select a root the current runtime actually discovers; the
shared user root is ~/.agents and a project root is <repo>/.agents. Installation
does not modify Codex settings, credentials, approvals, hooks or AGENTS.md.

Tool availability does not establish authority. A user-owned chat is not an
implementation worker; use the session's subagent mechanism for delegated work.
Keep a child brief specific and inspect its actual output before accepting it.

Official skill format reference:
https://learn.chatgpt.com/docs/build-skills
