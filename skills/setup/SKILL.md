---
name: setup
description: Adopt or diagnose Common Rules in a new or existing single- or multi-repository project, including tracker locations.
---

# Common Rules setup

Tell the user: **Common Rules skill: setup — calibrating this repository before writing.**

Run the installed plugin command using the host's plugin root:
`"${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}/bin/project-setup" --project . preview`
with known choices. Claude Code substitutes `CLAUDE_PLUGIN_ROOT`; OpenAI hosts
substitute or export the compatible plugin-root variables.
Inspect the preview, ask only for unresolved business-logic/interface roles,
requirements or tracker locations, workspace hub and issue-linking mode. Never
infer remote-write authority. Show the final manifest and apply only after the
user authorizes adoption. Finish with `project-setup doctor`.

For an optional proposal-level GitHub mirror, collect and preview all four
fields together: `issue_linking: one-way`, `issue_repository: owner/name`,
`issue_granularity: proposal`, and
`issue_sync_direction: ledger-to-github`. Never offer or infer reverse or
two-way synchronization. These settings describe a plan; they do not authorize
issue creation. Codex and Claude Code use the same manifest and commands.
