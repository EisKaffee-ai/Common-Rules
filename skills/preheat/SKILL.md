---
name: preheat
description: Refresh a running session using Common Rules reheat. Preheat is an alias, not a separate state or workflow.
---

Use the installed Common Rules path for this project. Run `bin/warmup --project . --reheat --no-pull --no-recall` from that installation. Then read the changed project files, especially AGENTS.md and declared guidelines/templates. If no saved baseline exists, read the full warm-up card first. Do not treat hashing a file as having read its instructions. Do not infer human approval from a successful check.

Install this alias for Codex and Claude with `bin/install-agent-context --project PATH`.
