---
name: reheat
description: Reheat a RUNNING session on the project's standard (common-rules proposal 28, R-01/R-02). Prints only what moved since the last /warmup or /reheat, plus the standard's own status every time, and queues what is pending. Use mid-session, after a compaction, or on resume ("what changed", "reheat", "catch me up").
argument-hint: "one line of context, or what he just asked for"
---

# /reheat: a running lead

A session already warmed up asks a different question than a fresh one: not
"what is the state" but "what changed". This skill is `--since` against the
state `/warmup` (or the last `/reheat`) already saved, with the standard's own
status appended every time — a running lead needs to be told what it did not
just ask about.

`RULES` below is `common-rules`, unless this project's
CLAUDE.md names a different common-rules checkout.

**A session that has not warmed up in this run, or cannot tell whether it
has, uses `skills/warmup/SKILL.md` (`/warmup`) instead** — the plain card,
not a delta against nothing.

## 1. Run it

`RULES/bin/warmup --project . --reheat --queue --state .claude/warmup/last.json`

- With no state at `.claude/warmup/last.json` yet, this prints the full card
  once (same as `/warmup`) and saves it — the natural fallback when a session
  reheats before it ever warmed up.
- **`--queue`** is the same idempotent write `/warmup` makes: every
  non-holding standard item and every pending mandatory Standard change
  becomes a ledger item, owner `lead`, status `not started`, first in the
  queue. Safe to include every time.
- **Anything the sponsor typed after `/reheat` is context — pass it
  through**, in the same run: `/reheat the sponsor wants the gate wired`
  means `--context "the sponsor wants the gate wired"`. Quote him as he
  typed it. Dropping it loses the only words of his the card carries.
- Picking up new context he did not type on the command line (something he
  said earlier this turn, a request answered by another session): same
  flag, `--context "<one line>"`.
- `--state` is written again after every run, so the next `/reheat` compares
  against this one.

## 2. Read only what moved

The output is a delta: new or changed ledger items (a split item's
completion %, next open part, and group count line among them), asks,
requests, a page that changed since it was last published, a checkpoint
that moved — then `standard: N of 12 hold` and every item that does not
hold, shown every time
(never only when it changed, since a running lead needs the current answer,
not just the news). `queue:` lists what `--queue` wrote, or says there was
nothing new.

The delta uses the same warm card as `/warmup`; when the project has a
`.common-rules.json` `goal` contract, that card carries its compact outcome,
constraints, and verification criteria forward as well. Keep the mirror
aligned with the host's native `/goal` when the objective changes. The
generated project tracker also becomes stale until regenerated after that
change.

`no change since the last warm-up · <status>` means exactly that: read
nothing further, keep working.

## 3. Act on it

Same as `/warmup` section 3: fix a ✗ line or record it `blocked` with the
reason; prohibitions are still verbatim from HANDOFF.md; Ruflo is still
mandatory around every item; a `page changed since last publish` line still
needs the same three-step republish `/warmup` describes. This skill changes
when and what is read, not what a lead does about it.
