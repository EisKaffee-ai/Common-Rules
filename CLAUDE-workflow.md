# Shared workflow rules

These rules are the shared contract for both Claude Code and Codex. The
workflow is consumer-neutral: Claude Code and Codex may expose different
commands or interfaces, but they follow the same ledger, tracker, handoff,
verification, and safety rules. References to a session, agent, tool, or host
name the capability or role involved, not a requirement to use one specific
consumer.

Common to every project under `apps/`. A project adopts them by
pointing here near the top of its own `CLAUDE.md` and layering its specifics
(test command, build command, repo name) on top — never by copying this text in.

Adopted: **finance-tracker** (2026-08-02), **pockets** (2026-08-02).

This file was 1,637 lines and is now under 300. The cut was made on 2026-08-05
after measuring four days of real sessions: two thirds of all spend went to
talking about work rather than doing it, and every merge conflict that day was
in a file these rules had invented. What survived is what the measurement showed
was load-bearing. Process about process is gone.

**Rules that can be enforced are not written here.** They live in
`bin/derecord`, which installs them into a project as git attributes and hooks.
A rule the AI cannot break needs no paragraph. Run it once per project:

```
common-rules/bin/derecord apps/<project>
```

---

## The warm-up standard is mandatory

Every project under `apps/` follows proposals 19, 20 and 21 —
one ledger shape, one card, one proposal shape, one way to ask another
session for something. Detail lives in `skills/standard/SKILL.md`; this is
only the pointer.

- **`/warmup`** opens every session, and runs again after a compaction.
- **The sponsor's `/standard`** is what adopts this for a project — typed
  by him, in that session, with his own authority there. A session does
  not wait to be told twice.
- **`bin/conformance --project <dir>`** will measure the 12-item checklist
  and report each item as holding, not holding, or waiting on
  common-rules, once it lands. Until then, `/standard` marks an item whose
  tool isn't in common-rules yet as "waiting on common-rules", never a
  substitute — re-checked at the next `/warmup`.
- **A later change to the standard is mandatory too.** A `CHANGELOG.md`
  entry here beginning `**Standard change (mandatory):**` is implemented
  before the next `rulecheck --align` — never the reverse.
- **Every new proposal** is created with `bin/new-proposal`, never drafted
  by hand.
- **Proposals are visual by default.** Before its Decisions list, a new
  proposal carries at least one table, diagram, or headline-figure block so
  the decision can be skimmed before its precise questions. Use the shared
  `.tk`, `.big`, `.stat`, `.verdict`, and `.ev` primitives from
  `templates/proposal.html`; `bin/proposalcheck` warns when the visual surface
  is missing. This is a warning-first rule for existing pages, not a
  retroactive failure gate.
- **Anything needed from another project's session** is a `requests`
  entry in the ledger, never prose; every blocked row carries an `owner`.
- **A lead ends at a boundary** — a milestone, day's end, or ~150k tokens
  of context — and hands over via the ledger, `tracker checkpoint` and
  `/warmup` (never a compaction summary; `templates/lead-prompt.md` §9).
  One tracker page per project, `docs/proposals/tracker/index.html`, until the sponsor asks for another, recorded in that ledger's `tracker` key.

---

## The four things that actually work

Measured across 30 sessions and 29.2M output tokens, the gain came from these
and almost nothing else. Do not trade them away.

1. **A worktree per task.** Separate folder, separate branch, always — including
   for this repo. Sessions sharing a checkout overwrite each other's work.
2. **Tool grants, not instructions.** Only `code-engineer` holds Edit and Write
   over code. The other roles are structurally unable to change it, so no rule
   is needed to stop them.
3. **A gate before merge.** Every change passes the tests and the project
   gate; risky work (see Ceremony) also gets `quality-manager` reading the diff
   against the acceptance criteria. It reports; it never fixes and never merges.
4. **Tests, run before landing.** `bin/land` refuses to merge a red branch.

---

## Git

Every chat gets its own branch and folder:

```
git worktree add -b <task-name> .worktrees/<task-name>
```

Never `git checkout -b` in a shared checkout — on 2026-08-05 that re-attributed
another session's uncommitted work mid-edit.

Commit as you go. Uncommitted work is invisible to every other session and to
`bin/whoelse`, which is how two branches end up building the same thing.

**Landing is automatic.** When a branch is done, run `bin/land`. It checks the
tree is clean, the branch is ahead, the merge is conflict-free, the tests are
green and nothing reserved was touched — then merges, through a PR where `main`
is protected. Nothing waits in a queue for the user to notice it. A project
that declares a staging branch lands there instead, and main moves only
through `bin/land --advance-staging` — full rule, and why, in the Tests
section below (proposal 31, O-08).

**Shared plan documents live on one branch, never in a feature branch.**
A project's milestone plan and the surfaces generated from it — for
finance-tracker that is `CLAUDE-milestones.json`, `CLAUDE-checklist.md`,
`docs/milestone-plan.html` and `docs/milestones.html` — are edited only on a
dedicated `plan` branch, landed on their own. A feature branch never touches
them, even to record its own row as done.

Two reasons, both measured on 2026-08-29. **They collide.** Every branch that
regenerates them rewrites the same handful of files, so three consecutive
rebases hit a conflict in one stamp file that no human had edited — the work
was identical, only the regeneration order differed. And **they go stale in
private.** A row marked done inside a feature branch is invisible to every
other session until that branch lands, so two sessions can each believe they
own the same row; nine rows sat stale for days for exactly this reason.

The rule is about the PLAN, not about every generated file. A document whose
gate is coupled to the code — the spec-book and open-book stamps, which fail
when the source they cite changes — must still be re-stamped by the branch
that moved that source. Those belong with the change; the plan does not.

**A project that has aligned before must stay aligned to keep landing.**
`bin/land` refuses when `.common-rules-version` names a version older than
current — the same signal `rulecheck` has printed all along, made load-bearing
instead of ignorable: a `SessionStart` hook's exit status does not stop a
session, so a stale project's every session got the failure and proceeded
anyway. Only a project that has actually run `rulecheck --align` at least once
is checked — pointing at this file from a `CLAUDE.md` alone is not the same
claim, so a project that never aligned is never blocked here. Fix it with
`rulecheck`, then `rulecheck --align` (which writes `.common-rules-version` but
does **not** commit it — commit it yourself), or, if the branch genuinely must
land first, `LAND_ALLOW_STALE_RULES=1`, recorded in the PR either way.

**The stamp is a `<commit-count>-<sha>`; `VERSION` is a semver beside it, not
instead of it** (proposal 32, V-01). The count-sha still settles which of two
versions is newer — two releases can share a semver while the repo has moved
on, and a sha alone says nothing about whether catching up is safe. `VERSION`
at the repo root is what says that. `rulecheck` reports both together
wherever it reports the version at all (`--version`, aligned, behind, no
stamp): `0.9.0 (187-5a62e87)`.

The bump is decided by the CHANGELOG entry that lands with it (proposal 32,
V-02), never guessed from prose:

- **MAJOR** — a change that breaks a project already following the rules: a
  tool removed or renamed, a declaration whose absence now fails a gate, a
  rule reversed. Declared explicitly in the entry (see `bin/version-check
  --help` for the marker) — never inferred, because a wrong guess here
  silently tells every adopting project a breaking change is safe to ignore.
- **MINOR** — any entry carrying `**Standard change (mandatory):**`. A
  project must now do something it did not have to before, but nothing it
  already does breaks.
- **PATCH** — everything else: a new tool nobody is required to use, a fix,
  wording.

`bin/version-check` reads the CHANGELOG entries since the last release and
prints the bump they require next to what `VERSION` says; `--check` exits
non-zero on disagreement and writes nothing. It runs in the merge gate
beside `bin/workflow-stamp --check`, so a `VERSION` that has drifted from
what the changelog actually shipped fails before the branch lands, not after.

Nothing sits unmerged more than about two hours of working time. Long-lived
branches are the whole cause of the collision class: on 2026-08-05 two branches
independently created the same new file and independently rewrote the same
renderer, purely because both had been alive for days.

**Record files never conflict.** `CHANGELOG.md`, `AGENT-LOG.md`, `LESSONS.md`
and the checklist are union-merged by `derecord`, so when two branches both
append, both win. Never hand-resolve them — hand-resolving them on 2026-08-05
is what put conflict markers into three Python files and broke `main`. Never
make a commit whose only content is a record entry; append alongside real work.

---

## Tests — the probe you ran is the test

**One command, everywhere.** Tests live in `tests/`, and every project runs

```
python3 -m unittest discover -s tests -q
```

`bin/land` runs it before landing and CI runs the identical string, so a test
written once is enforced in both without anybody wiring anything up. Do not
invent a second command, a second directory, or a second runner: two commands
wearing one name is how a test passes locally and never runs in CI. The one
sanctioned exception is a project's own declared `gates.quick`/`gates.merge`
split in its `.common-rules.json` (proposal 23, L-03) — a fast command for
routine work and a fuller one before landing, both named once in that file and
run through `bin/quiet -- {{TEST_COMMAND}}` (`templates/brief.md`), never
invented ad hoc inside a task.

**Verification you performed lands as a test.** Measured on 2026-08-10:
**29% of every Bash call a session makes is a one-off verification probe** —
an inline script that proves something and dies with the session. There were
3,873 of them, against 106 from all eight agent roles combined. The proving is
already happening and the code is already being written; it is thrown away
afterwards.

So this is not a request to test more. When you write a snippet to check that a
bug exists, that a fix works, or that two things agree — **put it in `tests/`
instead of pasting it into a message.** It is the same code either way; only
the destination differs.

`bin/land` refuses a branch that changes code and touches no test. If a change
genuinely cannot be tested, say why and re-run with `LAND_ALLOW_UNTESTED=1` —
recorded either way.

**A builder's own gate runs only the tests its changed files touch** —
`python3 tools/affected_tests.py [--base REF]` prints them; `bin/quiet --jobs
N -- python3 -m unittest discover -s tests -q` shards the full suite across N
processes for the times you do want all of it locally. Either way, the one
full sequential run at integration (`bin/land`, CI) stays the gate that
decides a merge (proposal 23, M-01/M-02).

**A project can move that integration gate off main onto a staging branch**
(proposal 31, O-08 — mandatory Standard change). The sponsor: *"We can also
reduce the number of tests so we can have a development branch or a staging
branch where we can keep merging changes and then after a considerable
amount of changes are done, we can test in one go. Rather than testing again
and again in smaller batches. We can test larger batches."* Declare
`"staging_branch": "<name>"` in `.common-rules.json` (`tools/project.py`
documents the key) and `bin/land` merges a reviewed branch onto that branch
instead of main, creating it from main the first time it's needed, running
the exact same gate it always has run — this changes *where* a branch lands,
not what it's tested against. `main` then only ever moves through
`bin/land --advance-staging`, which re-runs the gate on staging itself and
fast-forwards main to staging's tip on a green verdict only; it refuses,
never guesses, when the gate is red, when staging is behind main (some
commit reached main another way), or when the verdict cannot be read at all
(no test suite declared) — an unreadable verdict is a refusal, exactly like
a red one, never a pass. **No test is deleted by any of this.** What goes
down is how often the full suite gates main, never what it covers — a
smaller suite would have been just as green and just as wrong: finance-tracker
once carried 1,753 green tests over 16 wrong-money defects, found only by the
negative cases nobody had cut. And batch by time, not by commit count: a
batch large enough that a red staging verdict can't be traced to which branch
caused it costs more to untangle than the runs it saved — bisecting several
already-merged branches is worse than testing each as it landed. A project
that never declares `staging_branch` is unaffected: `land` goes straight to
main, exactly as before this key existed.

**Run the gate in the foreground, one blocking call, read the verdict line in
the same turn** (proposal 31, O-03 — mandatory Standard change). A session
never backgrounds a gate and spends turns polling it, and never ends a turn
parked on a timer: one agent turn costs about 134,000 cache-read context
tokens to produce a few hundred written ones, measured this session, so cost
scales with the number of turns, not the work inside them — a poll that finds
nothing new re-sends the whole context to learn nothing. In practice "one
blocking call" means scoping the run to fit inside it: `python3
tools/affected_tests.py` before the full suite, not after. If the tool still
backgrounds the call on its own (the harness's own ~120s cutoff, not a choice
the session makes), read the output exactly once, the moment you are
notified, and act on it in that same turn — never check it again, and never
end a turn whose only purpose was to wait. If even a scoped run cannot finish
inside that window, that is a bug in the gate — `test_warmup.py` alone is
574.9s, a third of the suite, and caps sharding at 610s even with `--jobs 8`
(findings 23/F-06 and 23/F-07, O-01/O-02 track fixing it) — not a reason to
poll. `templates/brief.md` and `templates/lead-prompt.md` §2 state the same
rule for the builder and the lead.

**A guard nobody has watched fail is not known to be a guard.** Run a new test
against the broken state first and see it fail, then fix. Two tests written
this week passed against the very bug they existed to catch: one because a
`chdir` test ran from inside the directory it was checking, one because a
`grep -q "__pycache__"` matched a different line.

---

## AGENT-LOG.md — what a task cost

This one is not bookkeeping for its own sake: it is how the user sees where
spend goes, and the measurement that produced this rewrite came from it plus
the session transcripts.

**It is generated, never written by hand:**

```
common-rules/bin/spend agentlog --write
```

which reads the session transcripts and writes one row per task — when it ran,
what it cost, how many sessions, and which agents were invoked how many times.
Regenerate it after a task lands; never edit it. `bin/spend report` totals cost
per task, and `bin/spend report --by-agent` says which roles are expensive.

**Why generated, and not appended by hand.** The rule here used to be "append
one entry when the task lands", with `bin/spend log`. Ten entries were written
that way in finance-tracker and **not one carried the token figure the report
needed** — so `spend report` answered 0 for every row for a week, and nothing
noticed, because the tool had no test. A number that is only right when somebody
remembers to type it is not a measurement.

Generating it also takes the file off the merge surface. Every merge conflict on
2026-08-05 was in a record file this framework invented, and hand-resolving one
is what put conflict markers into `main.py` and left `main` unable to start.

`spend log` still exists for a hand-written note, but nothing reads its numbers.

---

## Autopilot — the operating mode

The user owns **features**. The AI owns **issues**.

Creating, scoping, prioritising and closing a *feature*, and saying yes to a
proposal, are the user's calls. Everything downstream — cutting issues,
sequencing them, resolving disagreements between sessions, choosing between
implementations, deciding what to research — is the AI's job, done without
asking.

**Every project keeps a feature register.** A `## Features` table in its
`CLAUDE-checklist.md`: one row per feature, linking the GitHub issue that *is*
the feature, with a state column. The Tower reads it — that table is the only
answer to "what is this product made of, and how much of it is done".

| # | Feature | State |
|---|---|---|

States: `in flight` · `next` · `blocked by #N` · `later` / `version N` · `built`
/ `completed`. Name the implementing issues as `issue #N` — that is what makes a
percentage computable, and it is read separately from `blocked by`, which is a
dependency and never progress. `completed` is the word for fully finished, and
is what to write from here on; `done` is a grandfathered synonym of it, not
mass-renamed where already written; `built` keeps its own narrower meaning —
shipped but not yet closed — and is never folded into `completed` (naming
history and dates: CHANGELOG, 2026-08-20). A worked example of this table is
in that CHANGELOG entry.

**This is not a per-task obligation.** It changes when the sponsor adds, renames
or closes a feature — which is rare, and is his act rather than a session's.
Nothing here asks a session to append anything when work lands: that was
proposal 08's logbook, and it was rejected for exactly that reason.

A project with no register is reported as **"no features declared"**, never as
0% — undeclared scope is a different statement from none of it done.

**And every project keeps a milestone plan.** A `## Milestones` table in the same
`CLAUDE-checklist.md`: the order of work, and — the column that earns the table —
**what each step proves**.

| # | Milestone | Proves | You get | State |
|---|---|---|---|---|

A worked example of this table is in the CHANGELOG entry for M-10.

Same states as the register — including `completed`/grandfathered `done` for a
milestone that is fully finished, not just `built` and shipped. The register
says what the product is made of; this says **what order, what each step
establishes, and when the sponsor gets something he can hold.**

**Three disciplines make it worth the row.** A milestone ends in something *proven*,
not something delivered — "the index builds" is a task, "retrieval is good enough to
build on" is a milestone. **The result that would stop the plan is written before the
work starts**; written afterwards it is a rationalisation of whatever the data
happened to say. And **every row states what the sponsor gets, including when the
answer is nothing** — a plan whose first four steps hand him nothing is a fine plan,
but he should be told that at the start rather than discover it in week three.

(Measured on `pocket-internet`, 2026-08-20 — CHANGELOG has the incident.)

**One optional column: `Track`.** A project running genuinely parallel work —
finance-tracker has correctness and surfaces moving at the same time — names a track
per row, and the picture below draws one lane per track instead of one rule. Leave it
out and nothing changes; a project with a single thread of work should not pay for the
concept. Tracks are drawn in the order the plan first mentions them, never sorted, and
each lane carries its own *here*: with parallel work there is no single front, and
collapsing them to one would assert an ordering between lanes the plan never claimed.

**And the plan has a picture, generated — `docs/milestones.html`.** `bin/milestones`
reads the table above and renders it: the lanes, the states, and a marker wherever
something reaches the sponsor's hands. Run it after any change to the plan; `bin/land`
refuses a project whose page is missing or stale, on the same opt-in guard as the other
gates.

The page is **generated, never written**. That is the whole design: a hand-maintained
second copy of the plan is the failure this rule already warns about, with extra steps —
the table and the picture drift, and the picture is the one people look at. Staleness is
checkable because the page carries a digest of the plan's content, so the check asks
"does the picture still show this plan" rather than comparing bytes, which a generation
timestamp would defeat. Anything typed into the page is lost on the next run, and that
is the point.

**It is a live document, kept current until the feature is done.** A milestone plan
that is not maintained is worse than none, because it asserts an order of work that
has stopped being true and nobody can tell which rows still hold. Three things move
it, and only three:

- a milestone's **state** changes;
- a milestone's **proof lands** — and if the result differs from what was predicted,
  the row records what actually happened rather than being quietly rewritten;
- the **order changes**, because a proof came back badly enough to reorder what
  follows.

**Still not a per-task obligation**, same guardrail as the register above:
those three events happen a handful of times across a whole feature, not once
per task. The test is simple: editing because a session *did* something is the
rejected proposal-08 logbook; editing because something is now *known* is the
plan, and right.

**A question to the user is a cost, not a safety move.** Before asking, check
whether the answer would change what gets built. If either answer leads to the
same work, pick one, say which you picked, and continue. A question about
coordination between two sessions is never the user's to answer.

Ask only when:
- it is a feature-level call (what to build, whether to ship, what it is for)
- it touches money, data loss, or something outward-facing
- the answer is genuinely reserved (below)

**When there is nothing to decide, show no buttons.** Do the work and report it.

**Reserved to the user, always** — the full list is canonical in
`HANDOFF.md`'s "Reserved to the sponsor, always" section; state it verbatim
whenever it applies.

---

**The accepted plan is the queue. Do not ask which row is next.**
Once the sponsor has accepted a milestone plan, its open rows in `Seq` order
are the work. Finish a row, land it, take the next one — immediately, without
checking in. A question asking which accepted row to do next re-asks something
already answered, and every interruption costs more than a wrong guess would.

Stop for exactly three things: work that is destructive or irreversible, work
genuinely outside the plan, and a decision the plan itself records as the
sponsor's. Say those in a sentence, not a menu of options.

Reporting is not asking. Say what landed and what was found; do not seek
permission to continue.

## Issues

Cut issues **vertically**. One capability end to end — never "backend for X"
and "UI for X" as two issues. That split produced the #30/#31 race: two
sessions, one capability, guaranteed conflict, and the user left as referee.

One issue in flight per **surface**, not per issue. Two issues that touch the
same file are one issue, or one queue.

**Small issues on the same surface are one bundle.** One agent, one worktree,
one commit per issue naming its id, one gate run, one PR closing all of them.
Parallel agents only for surfaces that do not touch. A fix that cannot stand
alone is still not finished — bundling does not relax that. Proposal 25's
catalogue supplies the clusters to bundle from.

**Batching is a cost rule for the lead too, not just for a bundle** (proposal
31, O-07 — mandatory Standard change): 72% of a project's spend went to lead
orchestration against 25% to implementing, measured this session, because a
lead that dispatches one brief per turn pays a full turn — about 134,000
cache-read tokens — for each one. `templates/lead-prompt.md` §3 states the
rule in full: every unblocked brief goes out in one message, branches are
reviewed in one pass, and a lead with six things to say to six agents says
them in one message, never a turn at a time.

Record dependencies when issues are created, not when they collide.

### Working with GitHub

**`gh` truncates silently.** `gh issue list` and `gh pr list` default to **30 rows**
and say nothing about the ones they dropped. A backlog reported as "30 open" was
the page size, not the total. Always pass `--limit` — and when you report a count
to the user, it came from a command that had one.

**Check what your branch actually contains before opening a PR:**

```
git log --oneline origin/main..HEAD
```

If a line there is not yours, stop and rebase. A branch cut from a local `main`
that was ahead of `origin` carries the unpushed commits too, and a squash merge
collapses them all under your title. On 2026-08-07 a PR described as a one-line
docs change landed **25 files and 1,109 insertions** of another session's work,
and published a real corpus identifier doing it. `bin/land` now prints the
subjects it is about to land for the same reason.

**Say `closes` / `fixes` / `resolves` when you mean it, and only then.**
`bin/land` writes the `Closes #N` trailer from your commit messages, so an issue
closes with its fix instead of outliving it. The word *issue* is deliberately not
a keyword: "unlike issue #700" closed the live bug it named, twice in one day.

**An issue carries priority, type and area labels.** They are how the Tower and
every `--label` query find anything. Currently 17 of 88 open issues in
finance-tracker carry fewer than two.

**Never paste real data into an issue, a PR body or a commit message.** They go
to the remote, and a push does not unpublish. Real corpus identifiers reached
`origin` this way and the history still carries them.

---

### The project's own context has a budget too

These shared rules were cut from 1,637 lines to under 600 because a bloated
instruction file gets ignored rather than followed. That cut works only if the
project file does not absorb the difference — and it has:

| loaded into every session | lines |
|---|---:|
| finance-tracker `CLAUDE.md` + checklist | **2,218** |
| pockets `CLAUDE.md` + checklist | 1,128 |
| these shared rules | 594 |

A project's `CLAUDE.md` holds what is **specific and load-bearing**: test and
build commands, repo name, labels, gitignored files a worktree needs, and the
gotchas that have actually bitten. Anything that is history belongs in
`LESSONS.md`, anything that is a decision belongs in a numbered proposal, and
anything true of every project belongs here instead. If a section has not
changed what a session did in a month, it is costing attention rather than
buying it.

---

## Working alongside other sessions

Before starting, run `bin/whoelse`. It reports every worktree, what is
uncommitted in it, and how far ahead it is.

**Overlap is a stop, not a note.** If another session is on your surface, do not
proceed in parallel and do not ask the user which of you should win. Message it
with `mcp__ccd_session_mgmt__send_message`, agree who holds the surface, and the
other one queues.

A finding on another task's surface is a **handover**, not a note in a file: the
session that found it tells the session that owns it, and stops.

**A lead sweeps finished worktrees before they pile up.** Run
`bin/worktree-sweep --project . --apply` when a session ends, and again after
landing a batch. It removes only worktrees that are clean, merged (ancestry,
a merged GitHub PR, or a squash merge caught by `git cherry`), and idle — it
never touches uncommitted, unmerged, or active work, and it never touches the
main checkout.

---

## The agent roles

Defined in `agents/*.md`, registered from `~/.agent-data/agents`. Invoke with the
Agent tool and an explicit type — naming the type is the whole mechanism:

```
Agent(subagent_type: "code-engineer", prompt: "...")
```

| role | for |
|---|---|
| `research-agent` | before a direction exists: precedent, options, tradeoffs |
| `requirements-engineer` | a chosen direction written down as testable criteria |
| `design-explorer` | several structurally different concepts, early |
| `design-engineer` | one locked direction turned into a buildable spec |
| `code-engineer` | building it — the only role that may write code |
| `test-engineer` | validating against the criteria, raising bug reports |
| `quality-manager` | the pre-merge review for risky work; reports, never fixes, never merges |
| `proposal-auditor` | how far requirements and design drifted from the proposal |

A role never certifies its own work. The code engineer does not decide it is
done; the gate does. The gate does not merge; `bin/land` does.

**Escalation is bounded.** Code engineer and test engineer negotiate through at
most two rounds of bug reports. If they still disagree, the gate decides.

---

## Ceremony is opt-in

The full chain — research, requirements, design, proposal audit, L2 — runs only
on work the **user has flagged as a feature they care about**. It is not the
default, and never applies to every issue.

Everything else goes: issue → `code-engineer` → gate → `land`.

**A separate reviewer runs only for risky work — decided by `tracker route`
(`bin/tracker route LEDGER ITEM_ID`, proposal 25 Z-02, proposal 26 C-02),
never a fixed category list here.** `route` reads the item's own `risk`, or
classifies its files against the project's declared `risk_paths` /
`risk_always` (`tools/tracker/risk.py`) — money, user data, secrets,
releases and any common-rules change are what a project's own
`.common-rules.json` names `restricted`; common-rules itself declares
`risk_always: restricted`, so every item in this repo always routes that
way. `restricted` gets a separate reviewer whose result the sponsor sees,
never bundled; `elevated`, or `value high` with `points >= 5`, gets a
separate reviewer on its own branch; everything else goes
build → gate → land, no reviewer. This replaces reviewing every item —
the project's own receipt-reading and UI-verification rules are unchanged.

**This is measured, not preference.** Five arms built one frozen spec under five
process weights. All five scored 22/22; the arm running exactly this default did
it 2.4×–22.7× cheaper than the rest, and the heaviest arm was the slowest of all.
Argue for more process against that, not against a taste.
(`experiments/pockets-core/RESULTS.md`, branch `experiment/results`.)

**The light path (proposal 23, M-05).** An item small enough (points 1, risk
`standard`) skips more than just the separate reviewer above — it skips the
scout and the per-item ledger ceremony too: one commit, one gate run, one log
line, nothing else. Routing (proposal 25, Z-02) is what decides an item
qualifies; `templates/brief.md` carries the short form once it does. A finding
triaged and decided small the same way (proposal 26, C-05) takes this same
named path, batched with others from its cluster. **Common-rules items are
never light** — every change here is already `restricted` under the risky-work
list above, so the light path never applies inside this repository, only to
the projects that follow this standard.

The chain, when it does run:

1. A proposal, delivered as an HTML artifact, then a decision (below).
2. On acceptance: requirements, then design — never straight to code.
3. `proposal-auditor` measures the drift from what was accepted.
4. The project manager grants L2, or escalates to the user if the drift is
   material. The auditor measures; it does not decide.

**Research is triggered by conditions, not by taste.** Run `research-agent`
when: no direction has been chosen yet; the same problem has been solved twice
differently; a proposal names an unfamiliar technology; or the user asks
"should we build X". A task session created *from* a proposal has already had
its direction chosen — it does not re-research it.

---

## Talking to the user

**Show, don't summarise.** A proposal, a design or a result goes to the user as
a rendered HTML artifact, not a wall of text in chat. The user reviews by
looking. Do not ask them to read requirements prose.

**A published page's name is set once, and never changes (proposal 22, T-06,
mandatory).** The tracker/board, a per-proposal tracker page, the cookbook, or
any future maintained page — once its `<title>` is set on first publish, no
later republish edits it: not a differing `title` parameter, not by hand, not
a regenerating rebuild that emits the tag differently. Stated once, here; it
covers every maintained page, not just the tracker (`skills/warmup/SKILL.md`
§3 points back here rather than restating it).

**The cookbook (`docs/cookbook.html`, proposal 28 R-06) regenerates with the
rules it shows, the way the tracker page regenerates with its ledger.** A
`**Standard change (mandatory):**` entry touching warmup, reheat, or a rule
shown there regenerates its committed source in that commit and republishes
it to its existing url — never a new artifact, and not license to touch the
title rule above.

**Number every proposal, and lead with the number.** Proposals live in
`docs/proposals/` as `NN-<type>-<slug>.html`, numbered sequentially per project,
never reused. The visible heading and the `<title>` both read
`NN · status · Title` — so the sequence and where a thing stands are legible
before a word is read. Status is one of `proposed`, `accepted`, `completed`,
`completed in part`, `amends NN`, `superseded by NN`, and lives in
`<meta name="proposal-status">`. `built` is a grandfathered synonym for
`completed` — two proposals already use it and are not mass-renamed, but write
`completed` from here on. An unnumbered proposal is not a proposal; it is a
sketch.

**A proposal that asked numbered decisions must record the answers,** in the
same document, in a block a reader can find (`id="decided"`) — scoped
mechanically: a proposal whose `<ol class="decisions">` list asked something
must carry the answers before it reaches `accepted`, `completed`, `completed
in part`, or the grandfathered `built`. A proposal that asked nothing needs
nothing. (Why this rule exists, measured in finance-tracker: CHANGELOG,
2026-08-19.)

**A proposal reaches a terminal state — `completed`, or `completed in part`
with its exceptions named.** `completed in part` requires an `id="exceptions"`
block beside the decisions: what was not built, and why — the block is what
keeps a partial-completion claim honest.

**Grandfathered by decision date, not by list.** Both requirements above bind
proposals decided on or after **2026-08-19**; a proposal decided before that
date, or carrying no `proposal-decided` date at all, is exempt.
`bin/proposalcheck --project <dir>` is the mechanical form of both rules and
this grandfather. (The measurement behind the date and the cutover: CHANGELOG,
2026-08-19.)

**A document is either a proposal or an artifact, and the difference is
whether it carries a status.** A **lead** — a document with no
`<meta name="proposal-part-of">` — is the one thing in its topic asking for
a decision, and must carry a `proposal-status` from the vocabulary above. A
**section** — `part-of` some lead — is supporting material with nothing of
its own to decide (an exploration, a findings run, a design-explorer's
parallel concepts shown side by side before a direction is picked): it
carries no status at all, because there is only ever one decision per topic,
and the lead is where it lives. (What made this explicit: CHANGELOG, 2026-08-20.)

**Grandfathered the same way, a separate floor.** This binds proposals
touched on or after **2026-08-20** — its own day, not reused from the floor
above. (CHANGELOG, 2026-08-20, has which projects it grandfathered.)

**Then, if a decision is genuinely needed**, ask with buttons
(`AskUserQuestion`) — one question, options that differ in what gets built. If
no decision is needed, skip the buttons entirely.

**Ask before code, in one batch, and do not wait.** Collect what the spec leaves
undetermined, put it in one message, then pick a default for each and keep
working — recording what you picked and what it blocks. A question that blocks
nothing is recorded, not asked. (The bake-off measurement behind this: CHANGELOG,
2026-08-20.)

**Offer a demo before asking for a yes**, and before closing a feature. Say what
to open and what to click. The user should see the thing working, not read that
it works.

**When a session is finished, offer to close it.** Do not leave it idling.

---

## Verifying a change — in the browser pane, not in a real app

**Verify against the dev server in the in-app Browser pane.** It is DOM-aware,
gives console and network access, opens no window on the user's desktop, and
touches neither Safari nor Chrome. `preview_start` with the project's launch
config, then read the page, the console and the network calls.

**Do not build and open a `.app` to check ordinary work.** That was the old
pre-merge step 3 and it was wrong: `build_macapp.sh` produces a real macOS
window (WebKit — the Safari engine), so every verification left a window on the
user's screen and another bundle on disk. Four `Sangam.app` bundles accumulated
this way, all claiming the same identity.

Build a `.app` only when the change *is* the packaging — the native window, the
icon, the bundle, the launch path. Then build with a mode
(`RUN_MODE=dev ./build_macapp.sh`) so it gets its own identity, and delete the
bundle when done. Never `open` a URL on macOS from a session: that launches the
user's default browser.

---

## Running apps — one copy, one icon

`bin/apprun` owns every running copy, keyed on `CLAUDE_CODE_SESSION_ID`:

```
apprun start <project>      apprun list      apprun stop      apprun sweep
```

A session stops only what it started. `apprun sweep` clears dead entries.

**Start servers through `apprun`, or adopt them.** Every command also looks for
app processes running out of `apps/` that no entry covers, and shows them as
UNREGISTERED — they have no owner, so they are orphans and only the user may
clear them. If you started one by hand, `apprun adopt --port N` makes it yours
to stop when your task ends. Starting a server directly is not the problem;
leaving it unclaimed is. Before this, `list` reported a clean machine while two
copies were up, because the registry only knew what it had been told.

**Install from `main` at the end of every feature.** When a feature is done —
not each issue, the feature — check out `main`, pull, run the suite, and install:

```
git checkout main && git pull
python3 -m unittest discover -s tests -q     # or the project's own command
./build_macapp.sh --install
```

The installed app is what the user actually opens, so a feature that is merged
but not installed is a feature they cannot see. Never install a red build: if
the suite fails, an old working app beats a new broken one — say so and stop.

**One installed app per project, ever.** There is exactly one bundle in
`/Applications` for a project, and it is built from `main`. A worktree build is
a *development* copy: it carries a distinct name and identifier, and
`--install` is refused from anywhere but a stable build. Two bundles claiming
one identifier is a bug — macOS keys on `CFBundleIdentifier`, so that is not two
copies but one identity with two bodies, and which one opens is undefined.
`bin/appcheck` finds them; it should always report every identifier unique.

**A superseded copy is removed, not left beside the new one.** `appcheck` only
*reports*; nothing deletes for you, so deprecation is a step someone has to
take:

- **After every `--install`, run `bin/appcheck`.** It should say *every
  identifier unique*. If it does not, the previous bundle survived the install
  and both now answer to the same identifier — which one opens is undefined.
- **A worktree's development build is deleted when its task ends.** It exists to
  be looked at once. `dist/` is regenerable build output and can be cleared
  freely.
- **A renamed or replaced app's old bundle goes too**, along with its
  LaunchServices registration — `appcheck --clear-ghosts`. A `rm` alone leaves a
  ghost, which is why Spotlight and Launchpad keep offering copies that no
  longer exist.
- **Never touch `/Applications` by hand.** `--install` is the only path in, and
  it is refused from anywhere but a stable build from `main`.

The standing state is one bundle per project, built from `main`, and nothing
else. Four `Sangam.app` bundles accumulated on 2026-08-05 precisely because
verifying ordinary work built a `.app` each time and none of them were cleaned
up.

Never touch `/Applications` by hand — `--install` is the only path in, and it
removes its own staged copy from `dist/` so the install cannot leave a duplicate
behind.

---

## Seeing the state

- `bin/pulse` — snapshot page: features, issues, worktrees, rules alignment
- `bin/tower` — live view: session graph, pipeline, event ticker
- `bin/spend` — what tasks and agents have cost
- `docs/workflow.html` — the bird's-eye map

`pulse` and `tower` bind to **127.0.0.1 only**. They render private session data
and are never published as an artifact.

---

## Changing these rules

Reserved for the user. The AI surfaces a proposed change and opens a PR; the
user merges. Never edit `common-rules/` unprompted, including `agents/`.

`ASKS.md` logs process asks. When the same ask appears three times, propose a
rule — once, as a PR.

Adding to this file is a cost. It was cut from 1,637 lines because its length
was making it go unread. A new rule must either replace something, or be
enforceable by `derecord` — in which case it belongs in code, not here.

---

## Known gotchas on this Mac

- Plain `git` is broken pending an Xcode licence. Use
  `/Library/Developer/CommandLineTools/usr/bin/git`.
- Directories under `~/.agent-data/projects/` start with `-`, so a globbed `grep`
  reads them as flags and silently finds nothing. Use Python `glob`.
- Temp files go to the session scratchpad, never to `apps/`.
  Verify the `cd` succeeded — a failed one writes into the repo.
