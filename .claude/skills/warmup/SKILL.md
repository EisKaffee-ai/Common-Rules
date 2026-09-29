---
name: warmup
description: Warm up a FRESH session on the project's standard (common-rules proposal 19, and proposal 28's R-01/R-02). Reads HANDOFF.md, the operating rules, the ledger and the last checkpoint in a fixed order, checks the tools and the standard, queues what is pending, and prints the warm card before any work. Use at the start of a session. A session already running uses /reheat instead ("warm up", "what changed", "refresh the rules").
argument-hint: "one line of context for this session"
---

# /warmup: a fresh lead

The rules are already on disk. This skill loads them in the same order every
time, so the sponsor never has to type "reread the handoff", "are you using
ruflo" or "what is the current status" again. It asks nothing.

`RULES` below is `common-rules`, unless this project's
CLAUDE.md names a different common-rules checkout.

**A session already running does not use this skill again — it uses
`skills/reheat/SKILL.md` (`/reheat`)**, which asks only what moved since the
last warm-up or reheat, with the standard's own status carried along every
time. This skill is for the start of a session: a fresh lead, or a lead that
cannot tell whether it already warmed up.

## 1. Run it

`RULES/bin/warmup --project . --queue --state .claude/warmup/last.json`

- **`--queue`** records every non-holding standard item and every pending
  mandatory Standard change as a ledger item — owner `lead`, status
  `not started`, first in the queue — so what the card shows is also what the
  ledger already tracks. Running it again adds nothing for what is already
  queued: it is always safe to include.
- **`--state .claude/warmup/last.json`** saves this run's state, so `/reheat`
  has a baseline to compare against later in the session. `.claude/warmup/`
  is scratch state — never commit it.
- **Anything the sponsor typed after `/warmup` is context — pass it
  through.** `/warmup we are picking up the engine work` means
  `--context "we are picking up the engine work"`, in the same run, not a
  separate call and not dropped. This is the only place his words enter the
  card, so losing them is losing the one thing he asked the command to
  carry. Quote him as he typed it; do not summarise or tidy it.
- Picking up context he did not type on the command line (a handoff from
  another session, something said earlier in the conversation): same flag,
  `--context "<one line>"`. It is printed on the card and carried into the
  saved state.

The card now always includes `standard: N of 12 hold` and, under it, every
item that does not hold — the same twelve `bin/conformance` checks, run in
process. A split item's line shows its completion %, next open part, and a
group count line (finish now / back burner / waiting). What `--queue` wrote
is listed at the end, under `queue:`.

If `.common-rules.json` declares a `goal`, the card begins with its compact
outcome, constraints, and verification criteria. Keep that repository mirror
short and aligned with the host's native `/goal`: the host goal controls
long-running execution; the mirror makes the current intent inspectable after
handoff or compaction. The generated project tracker carries the same goal
and is stale until regenerated after a goal change.

## 2. Read, in the order the card names

The card ends with `Read in order:`. Read every file on that line, in that
order, before any other action: HANDOFF.md (which now folds in
docs/OPERATING-RULES.md — proposal 23, M-11) → this card itself → the latest
checkpoint → common-rules' CLAUDE-workflow.md. The card has already validated
and summarized every auto-discovered ledger; do not reopen every raw ledger
JSON. Open the full JSON only for the item currently being worked, unless the
project explicitly names a ledger in `.common-rules.json` `read_order`.

After a compaction the summary above is a paraphrase. The ledger is the
record. Quote a ruling from disk (the constraints file, the issue, the ledger
ask), never from the summary.

## 3. Act on the card

- **✗ lines are problems.** Fix each before new work — `tracker render`,
  `tracker checkpoint`, fill a placeholder — or record it in the ledger as
  `blocked` with the reason. Never start work over a red card silently.
- **Prohibitions** are verbatim from HANDOFF.md. Put them, word for word, in
  every agent brief.
- **Ruflo is mandatory.** The card shows where the CLI is; warm-up never runs
  it. For every item: `memory search` and `hooks route` before, `hooks
  post-task` and `memory store` after, run from the project root, then
  `daemon stop` for the daemon your calls started. Never kill it by name.
  **Never register Ruflo's full MCP tool set for this reason.** `bin/ruflo-item`
  is a CLI wrapper, not an MCP client — it shells out to the `claude-flow`/
  `ruflo` binary for `hooks pre-task`, `memory search`, `hooks route`,
  `memory store`, `hooks post-task`, `hooks worker dispatch --trigger
  testgaps`, `memory list` and `daemon stop`, so a session that only uses
  `bin/ruflo-item` (every item lead and builder, per this section) pays zero
  MCP tool-definition tokens: nothing here needs the 333-tool `claude-flow`
  MCP server on this project's `.claude.json`/`.mcp.json` at all (proposal 19's
  own finding was the same — the MCP server it tried once "connected but its
  tools [were] not exposed in the lead session[; it] fell back to the CLI").
  common-rules does not register that MCP server for itself today. If a
  session's `~/.agent-data.json` registers it anyway (for another project, or a
  future need this CLI wrapper doesn't cover), load only the tools this
  section already names above — `memory_store`, `memory_search`,
  `hooks_route`, plus `hooks post-task` and `daemon stop` — one call each via
  `ToolSearch`, batched, never the full 333-tool set, per proposal 23 M-03
  ("Ruflo's 333 MCP tools cost ~61.5k tokens of tool definitions per session
  ... load only the tools the item wrapper uses, or defer loading").
- **`RULES/bin/recall <words>`** searches every project's memory, LESSONS and
  operating rules. Put the hits for an item under CONTEXT in its brief.
- **`page changed since last publish: docs/proposals/tracker/index.html → <url>`**
  means the project's one tracker page — every ledger on one page — no longer
  matches what was last published to that URL. Republish it yourself, in the
  same turn, in this order:
  1. Finish and commit ledger edits first. Committing a ledger re-renders the
     page (derecord's pre-commit hook does it); if the card still shows the
     page as stale, run `tracker board --project .` and commit that.
  2. Publish that committed page file with your Artifact tool **to the same
     URL** the line names — update the existing artifact in place, never
     create a new one. **Its `<title>`, once set on first publish, never
     changes on a later republish** — not a differing `title` parameter, not
     by hand (`CLAUDE-workflow.md`, "Talking to the user", proposal 22 T-06 —
     stated once there, covering every maintained page, not restated here).
  3. Record it: `RULES/bin/tracker published --project . --url <url>`
     (add `--by <your session's name>`), then commit the sidecar on its own:
     `docs/proposals/tracker/index.published.json`, with nothing else in that
     commit.

  **A proposal the sponsor asked to track separately** — its ledger's
  `tracker` key records `{"own": true, ...}` — keeps a page and a record of its own:
  publish `docs/proposals/tracker/<stem>.html` and record it with
  `RULES/bin/tracker published docs/proposals/<stem>.json --url <url>`, then
  commit that sidecar on its own. For a ledger without that key the per-ledger
  command refuses and names `tracker published --project`: one tracker per
  project unless the sponsor asked for another.

  **When `.common-rules.json` declares `plan_page`**, the page of record is
  the file that project's generator writes, not the tracker page, and the
  line names that file: `page changed since last publish: <page> → <url>`.
  It speaks when the ledger moves, not when only a generated date does. Same
  order, with the page swapped in:
  1. Commit ledger edits first, then regenerate the page with the project's
     own generator (the `plan_page` command) and commit it.
  2. With your Artifact tool, publish that file in place to the same URL.
  3. Record it: `RULES/bin/tracker published docs/proposals/<stem>.json --url <url> --page <path>`,
     `<path>` being the committed file the generator wrote, relative to the
     project root; then commit the sidecar on its own. Without `--page`,
     `tracker published` refuses on such a project, and so does
     `tracker published --project`: the declared page is that project's
     tracker. The project page is still rendered and checked beside it — it is
     simply not the page that is published.

  `tracker published` refuses while the ledger it records has uncommitted
  changes — every ledger, for `--project` — and, with `--page`, when the
  page was last committed before the ledger changed
  — an old page recorded as current would keep the card silent for good.
  Only when a committed ledger change leaves the page's bytes identical, pass
  `--page-unchanged`; the sidecar records that you did.

  A republish is not logged as a ledger event. The sidecar's `at` and `by`,
  in git, are the record. This is the one exception to "every state change
  gets a log entry": a log entry would itself move the page, and the line
  would come straight back.

  A republish needs no sponsor prompt: when `switches.publish` is on (the
  default) — every ledger's, for the project page — republishing a changed
  page is part of keeping the ledger current, like rendering it. When any is
  switched off, nothing is published — the card prints no such line and
  `tracker published` refuses to record, naming that ledger. The line never
  fails `warmup --check`; it is a to-do, not a broken standard. Only a
  session's Artifact tool can publish; no hook or script does it for you.
- **A page published before it was recorded.** When the project's tracker page
  is published for the first time, or you find one already published (a URL in
  the handover, lead prompt or log) with no
  `docs/proposals/tracker/index.published.json`, record it at once with
  `tracker published --project . --url <url>`; from then on the card
  tells you when it moves. When the project declares `plan_page`, the page is
  the committed file its generator writes: record it with
  `RULES/bin/tracker published docs/proposals/<stem>.json --url <url> --page <path>`;
  for a proposal with a tracker of its own, `RULES/bin/tracker published docs/proposals/<stem>.json --url <url>`.
  The card gives no hint for a missing sidecar, because a project that never
  publishes must see nothing.

## 4. The first message to the sponsor

1. The card, as printed.
2. A steps list for the first item you will take, its ledger id on top.
3. Then start — spawn every unblocked C1/C2 item in one message, each in its
   own worktree with the five-heading brief from `RULES/templates/brief.md`;
   take the first C3 yourself.

While working, keep to one status line in the lead prompt's form:
`N done / N in progress / N blocked / N not started / N deferred · what changed · waiting on · yours:`

`deferred` is terminal, green, and reasoned; it is not active work or a
blocker. Reopen it only with `tracker set ... --status <non-terminal> --reopen`.

Every sponsor message that is not an answer to a question becomes an ask
row (`HANDOFF.md`, "Operating rules"), in the same turn.

## Moving a running project onto the standard

1. `RULES/bin/warmup --project . --migrate --dry-run` first. It writes nothing
   and lists what it would do: run derecord, import the plan into a ledger
   under the next free proposal number, supersede rules, point CLAUDE.md at
   the read order. Only rules `RULES/templates/supersedes.json` names are
   superseded -- nothing is guessed. Show the sponsor that list.
2. `RULES/bin/warmup --project . --migrate`. Each superseded rule moves,
   verbatim and dated, into `## Superseded` in docs/OPERATING-RULES.md; nothing
   is deleted. Nothing is committed.
3. CLAUDE.md is the sponsor's: land will not land a branch that touches it.
   Say that it changed and let him commit it.

The card afterwards lists what was superseded. When you catch yourself
following a rule on that list, stop: the line names what replaced it. When a
migration shows a rule the standard replaces that the list does not name, add
an entry to supersedes.json with where it was seen -- do not move it by hand.
