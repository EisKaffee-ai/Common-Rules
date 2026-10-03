---
name: setup
description: Calibrate Common Rules for a new or existing repository. Use when adopting, installing, configuring, or diagnosing Common Rules, including single- versus multi-repository topology and tracker locations.
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
