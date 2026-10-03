---
name: standard
description: Legacy alias for /warmup. Use when the sponsor asks to put the current session and project on the Common Rules standard.
---

# /standard

**As of proposal 28, `/standard` is part of `/warmup`.** `bin/warmup`'s plain
card already runs the standard's twelve checks (`bin/conformance`) and the
mandatory-pending check every time, and `--queue` writes what does not hold
into the ledger as items owned by `lead` — the "queue it first" step this
command used to spell out by hand. There is nothing left for `/standard` to
do that `/warmup` does not already do on every run.

**This command is kept only so far as the sponsor may still type it in an
existing session. It will be removed next release** — say so if he types it,
and point him at `/warmup` (a fresh lead) or `/reheat` (a running one)
instead.

Run the steps in `skills/warmup/SKILL.md` now, exactly as written there:

`RULES/bin/warmup --project . --queue --state .claude/warmup/last.json`

(`RULES` is `common-rules`, unless this project's
CLAUDE.md names a different checkout.) Read the card, fix or block every ✗
line, and carry on — `skills/warmup/SKILL.md` section 3 says how.
