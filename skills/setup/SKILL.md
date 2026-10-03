---
name: setup
description: Calibrate Common Rules for a new or existing repository. Use when adopting, installing, configuring, or diagnosing Common Rules, including single- versus multi-repository topology and tracker locations.
---

# Common Rules setup

Tell the user: **Common Rules skill: setup — calibrating this repository before writing.**

Run `"$PLUGIN_ROOT/bin/project-setup" --project . preview` with known choices.
Inspect the preview, ask only for unresolved business-logic/interface roles,
requirements or tracker locations, workspace hub and issue-linking mode. Never
infer remote-write authority. Show the final manifest and apply only after the
user authorizes adoption. Finish with `project-setup doctor`.
