# 1.10.4 — Reviewed holistic traceability — 3 October 2026

Adds an opt-in, deterministic `bin/traceability` toolchain. Projects keep a
reviewed manifest and repository-specific scan configuration; Common Rules
validates stable typed requirement, workflow, code-anchor, test-case,
test-report, issue, receipt and mapping IDs. The engine scans every configured
checkout, resolves revision-bound symbol and explicit START/END anchors,
labels whole-file evidence as weak, and checks expected workflow nodes and
edges against accepted implementation evidence.

The generated responsive page leads with an overall dashboard and then shows
per-feature workflow, code, test-case, latest-report, issue and receipt
evidence. AI-proposed mappings never contribute accepted coverage. Python owns
all states, counts, digests and output, and check mode refuses broken evidence
or stale generated HTML. There is no runtime AI dependency. Existing projects
are unchanged until they add a reviewed manifest and invoke the command.

Independent review added fixed-revision dirty-worktree refusal, actual-edge
topology comparison, report-file/result verification, latest-report coverage,
complete evidence-chain validation, receipt-reference validation, and safe
HTTP(S)-only issue links before release.

# 1.10.3 — Canonical project tracker and proposal issues — 3 October 2026

Versions 1.10.0 through 1.10.2 were internal candidates. The class-level
cold-gate scheduler landed after the first marker, its final 2,065-test
evidence landed after the second, and mixed-ledger plus deterministic-plugin
hardening landed after the third. Version 1.10.3 is the publishable candidate
rather than rewriting release history.

Common Rules now validates an optional proposal-level GitHub issue contract:
`issue_repository`, `issue_granularity: proposal`, and
`issue_sync_direction: ledger-to-github` are declared together with one-way
issue linking. Reverse or partial contracts are refused. Setup discovers
nested source-ledger catalogues, excludes generated and vendored copies, and
prefers the largest real catalogue instead of proposing a duplicate
`docs/proposals` tracker. Existing manifests without the optional contract
retain their prior behavior.

An optional `integration.issue_series` now limits proposal issue management to
one ledger series. This lets a single canonical tracker contain 27 architecture
ledgers plus later operational ledgers without creating a 28th architecture
issue: excluded ledgers stay visible as Project Operations, architecture totals
stay scoped to the selected series, and any excluded ledger carrying an issue
mapping is refused rather than silently orphaned.

`tracker sync --project` now produces one deterministic, whole-set-validated
issue plan per proposal without calling GitHub. Generated bodies preserve
stable item IDs, status-aware checkboxes, repository ownership, evidence,
gaps, dependencies and revision-bound implementation/test references. A
narrow `--record` operation assigns one returned issue identity to the group,
its features and every item; `--reconcile` reports remote body/title/state
drift without changing ledger status. Legacy row-level `tracker sync LEDGER`
behavior remains available for projects that have not opted in.

The canonical board now follows a configured nested tracker directory and
writes its single page beside those ledgers. Calibrated catalogues gain five
mobile-friendly information views—Overview, Product delivery, Architecture,
Repositories, and Evidence—without removing the established Tree, Kanban,
Board, and List delivery layouts. Architecture cards group proposals by
layer, show group issue and lifecycle state, and expand to feature gaps and
traceability; declared workspace members appear as revision-bound repository
cards inside the same page rather than as a second public tracker.

Tracker history now replays the same configured nested ledger directory as the
board and namespaces cached snapshots by that directory. The current header
also refuses a historical denominator that differs from the current ledgers.
Architecture catalogues describe their hierarchy explicitly as layers,
architecture groups, features and lifecycle steps, preventing an unrelated
parent-project total from appearing as the catalogue's task count. The goal
contract remains a freshness input and warm-up control but is not rendered as
a large prose panel in the public tracker.

The release now has a reproducible context-footprint gate. Common Rules keeps
detailed issue-sync guidance in an on-demand tracker reference and shortens
skill discovery descriptions while preserving their trigger conditions. The
conservative idle discovery estimate falls from 849 to 627 tokens (26%); the
README separates that cost from invoked instructions, optional references,
hook output and the never-default full-package ceiling. `bin/context-budget
--json --check` enforces the 650-token discovery budget and explicitly reports
context estimates rather than process RAM.

The parallel unittest gate now accelerates its first run as well as warmed
runs. Large files are split by test class before duration data exists, and an
older coarse cache is refined into class-level timings. The 124-test warmup
hotspot fell from the previously documented 575-second floor to 174.6 seconds
on the release host. After those named environment/checkpoint findings were
resolved, the final release gate passed all 2,088 tests in 189.6 seconds. Coverage and
aggregate failure detection are unchanged.

Tracker generation is now an explicit Python-owned boundary. Shipped commands
assign proposal, ask and finding identifiers; calculate counts, percentages and
digests; validate and mutate ledger state; generate issue plans; validate
provider-returned mappings; render pages, history and checkpoints; and check
freshness. Agents supply explicit inputs and invoke those commands, but do not
invent generated values or hand-edit ledger JSON or generated tracker HTML.

Release-review hardening makes that boundary transactional and
cross-repository: proposal issue mapping preflights the complete set, validates
an atomic ledger write, and refreshes both rendered surfaces; proposal-mode
workspace checks validate local member checkouts and pinned revisions;
tracecheck diffs qualified member paths against those revisions; setup doctor
applies the full declaration contract; and setup parses every checkout argument
before any file is written. `bin/quiet --receipt` emits a digest-bound machine
record of the exact gate command and result. The shipped `bin/release-evidence`
command accepts only the full merge-gate discovery receipt and updates both
public documents and the canonical ledger rather than relying on agent-authored
numbers.

The Common Rules plugin repository no longer ships its duplicated
`.claude/settings.json` or project-local warmup/reheat skill copies. Claude Code
loads the canonical root skills and portable `hooks/hooks.json`; that manifest
now includes SessionStart, PreCompact, Stop and Agent/Task PostToolUse lifecycle
hooks. `derecord` continues to install project-local copies for adopter
repositories that need the legacy direct-checkout path.

# 1.9.0 — Common Rules tracker plugin for OpenAI and Claude — 3 October 2026

**Standard change (mandatory):** projects can now opt into a calibrated
`.common-rules.json` integration manifest, visual joined tracking across
independently committed repositories, deterministic requirement-to-file
traceability, and the portable Common Rules plugin lifecycle. Setup previews
before writing and preserves existing declarations; local checkout paths stay
uncommitted. Added visible setup, calibration, intake, planning, visual
proposal, review, repair and handoff skills plus optional trusted hooks. No
project is silently upgraded and no remote-write authority is inferred.
Common Rules is the tracker plugin and supersedes the separate Emberline AI
Tracker runtime; migrations preserve ledger IDs and evidence before cutover.
The same release now includes Claude Code's `.claude-plugin/plugin.json` and
marketplace catalog, uses the shared Claude/OpenAI plugin-root hook variable,
and validates both manifests against version 1.9.0. A new read-only
`migration-check` proves the source main, published development and local-only
histories are ancestors of the release, no source file disappeared, source
tags and branches are present at the destination, and the published candidate
is the reviewed revision. Versions 1.5.0 through 1.7.0 were internal candidates
and were not published.

The repository landing page now presents Common Rules rather than the legacy
product identity. It includes current Codex and Claude Code marketplace setup,
the calibrated first-use path, a complete skill catalog with worked examples,
and six accessible SVG explanations for the plugin model, installation, skill
routing, session continuity, delivery lifecycle, traceability and joined
multi-repository tracking. The companion HTML review surfaces use the same
current identity and visuals. Added an OpenAI repo marketplace alongside the
Claude Code marketplace. This documentation and discoverability work is part
of the same mandatory Common Rules release contract. A reviewer-ready
completion audit maps all 21 accepted requirements to the authoritative ledger,
reproducible gates and remaining publication boundary.

Versions 1.8.0 and 1.8.1 were internal candidates. The reviewer-audit
documentation was added after the 1.8.0 marker, and the mandatory Standard
change requires a minor release, so 1.9.0 is the publication candidate.

# 1.4.1 — Release verification and installer safety — 29 September 2026

Includes the Common Rules migration prepared as 1.4.0, plus the release-gate corrections and installer containment/shared-state fixes below. Version 1.4.0 was an unreleased candidate; 1.4.1 is the publication candidate after its verification fixes.

# 1.4.0 — EisKaffee.ai / Common Rules — 29 September 2026

Adds an opt-in AGENTS-first context installer for Codex and Claude, with warmup, reheat and preheat aliases. Preserves existing project instructions, reads declared guidelines and templates, and refuses to overwrite unmanaged skills. Carries forward the existing 1.3.0 development history and local tracker improvements. Existing projects are not silently upgraded. No architecture or publication approval is inferred from installation.

Release verification correction: restored the explicit “card, not the raw ledger JSON” wording in warmup while preserving declared read-order exceptions. No command behaviour changes.

Release verification fixes: pin the intended 1.4.0 version in its regression test; freeze waiting-date fixtures; retain terminal deferred filtering coverage; use the current Python interpreter for fake renderer tests; align the read-order expectation with summarized auto-discovered ledgers; add the missing in-progress traceability part without claiming completion. Reflowed existing visual-proposal guidance without changing its words.

Installer review fixes: reject symlinked installation destinations before writing and save an explicit shared warmup/reheat/preheat baseline. Regression tests first reproduced both defects in disposable projects.

# Migration development note — 29 September 2026

Unreleased: Common Rules migration adds an opt-in `bin/install-agent-context` for AGENTS-first Codex/Claude skills, with preheat as a reheat alias. It preserves project rules and hooks and does not claim full tracker conformance. Corrected the nonexistent Codex-workflow.md pointer. Existing installations are unchanged until explicitly installed.
## 1.3.0 · Guide and architecture traceability · 2026-09-20

## 2026-09-26 · `history_since` may name an hour

`"history_since"` in `.common-rules.json` now also takes an ISO timestamp
(`"2026-09-25T20:00:00+01:00"`; a naive one is read in the tracker's local
time). A date still means that day's midnight. Loom consolidated its ledgers
at 20:00 on 25 September, so a date floor left the hourly chart showing the
old counts, and the sponsor said "clear this history from the graph". Not a
Standard change: a project regenerates its page with `tracker board`.

## 2026-09-26 · Both progress charts, and no two status lines alike

The sponsor asked to fix "multiple progress lines"; the status chart was
removed, and he then said "one graph is missing from the tracker". Both
charts are back ("Tasks by status over time" and "Completion over time").
What stays fixed: `deferred` has its own colour instead of `done`'s green,
so no two status lines look the same. Not a Standard change: a project
regenerates its page with `tracker board`.

## 2026-09-25 · `history_since`: the progress graph starts where the project's story does

`.common-rules.json` may declare `"history_since": "YYYY-MM-DD"`; the tracker
board's two progress charts then start at that date instead of the first
commit. Optional; nothing changes for a project that does not declare it.
Loom asked for it after consolidating 25 ledgers into two: the old counts
made the graph read as a collapse, and the sponsor said "reset the old data
from the graph". History stays in git; only the page's window moves.

**Standard change (mandatory):** projects can now keep a validated
requirement-to-evidence traceability row in each proposal ledger:
requirement IDs → guide section → architecture section → implementation files
→ tests/commands → receipt or refusal → owner → status. The generated tracker
renders these rows as a first-class Traceability table so a task is not complete
while its documentation, implementation, verification, and evidence disagree.

## 1.2.0 · Visual proposals by default · 2026-09-20

**Standard change (mandatory):** a proposal must be answerable from its
visuals. New proposal pages should place at least one table, diagram, or
headline-figure block before the Decisions list; verdicts should be single
coloured words in their own column; evidence should sit under the claim it
supports. `bin/proposalcheck` warns when a page has none, without failing
existing pages, and `templates/proposal.html` now ships `.tk`, `.big`, `.stat`,
`.verdict`, and `.ev` so projects stop hand-rolling them.

## 1.1.13 · First-class deferred state · 2026-09-20

Added the first-class `deferred` item state. It is terminal and green,
requires a reason, is excluded from active-work and blocker counts, remains in
history, and can only be reopened explicitly.

Added an optional `.common-rules.json` goal contract with an outcome,
constraints, and verification criteria. Warm-up now shows that compact
repository-side mirror of the host's native `/goal`, so sessions can recover
the current intent without reconstructing it from chat history. Existing
projects are unchanged unless they opt in; the native goal remains the
execution control. When opted in, the generated project tracker shows the
same contract and detects goal edits as page-staleness.

Warm-up now validates and summarizes auto-discovered ledgers without adding
every raw ledger JSON file to the session read order. A project may still name
a ledger explicitly in `read_order`; otherwise a lead opens only the ledger
for the item being worked, reducing repeated context without hiding status.


## 1.1.12 · Release pin synchronization · 2026-09-19

Synchronized the literal release-version regression test with the README
adoption-prompt release so the public Ubuntu merge gate verifies the current
version contract.

## 1.1.11 · Copy-and-paste project adoption · 2026-09-19

Added a ready-to-paste project-chat instruction set to the public README so
Claude Code and Codex projects can understand Emberline, review their existing
rules, adopt the shared workflow safely, and report their integration gaps.

## 1.1.10 · Release pin synchronization · 2026-09-19

Synchronized the intentionally literal release-version regression test with
the hourly tracker fix release so the public CI gate checks the current
version contract.

## 1.1.9 · Accurate hourly tracker history · 2026-09-19

Fixed the hourly progress graph: tracker history now preserves each ledger
commit's local timestamp and buckets hourly snapshots at the real commit hour
instead of reducing every update to midnight. Added regression coverage for
intraday snapshot changes.

## 1.1.8 · Release pin synchronization · 2026-09-19

Synchronized the intentionally literal release-version regression test with
the published patch version so the Ubuntu merge gate exercises the same
release contract as the working tree.

## 1.1.7 · CI release follow-up · 2026-09-19

Followed the public 1.1.6 release with the final CI release boundary: the
workflow now installs its renderer dependency explicitly, and the release
version advances past the preparation commit so the merge gate can verify a
new published patch release.

## 1.1.6 · Pipeline, user guide, and discoverability · 2026-09-19

Repaired the merge gate's stale workflow stamp and synchronized the release
version with the shipped changelog. Added the renderer dependency required by
the workflow-stamp tests and fixed the milestone renderer's missing standard
library import. Added a guided `docs/user-guide/` for the product model,
session commands, tracker, integrations, repository layout, and search
discoverability. Documented why operational root files and
`.github/workflows/` remain in their conventional locations.
Updated the release-version test pin, refreshed the public tracker and
checkpoint after recording the release lock, and restored the README's tested
adoption path.

## 1.1.5 · Public repository cleanup · 2026-09-19

Removed tracked warm-up session state and three orphaned presentation pages
that were not referenced by the product, workflow, tests, or public docs.
Ignored future warm-up snapshots so machine-local session state cannot return
to the repository. Retained proposal-cited research evidence, runtime tools,
tests, tracker pages, handovers, and the story snapshot because they remain
part of the workflow or historical audit surface.

## 1.1.4 · GitHub discoverability pass · 2026-09-19

Clarified the README's search-facing introduction around open-source AI agent
memory, session context, project tracking, Claude Code, and OpenAI Codex.
Applied focused GitHub repository topics and a descriptive repository summary.
Added a concise documentation map so the public story, getting-started guide,
live tracker evidence, and maintainer reference surfaces are easy to find
without moving contract-sensitive workflow paths.

## 1.1.3 · Public release licensing · 2026-09-19

Added Apache-2.0 licensing for code, CC BY 4.0 terms for documentation and
visual assets, and a NOTICE file crediting Aashish Sud. Reserved the Emberline
name and logo against implied endorsement.

## 1.1.2 · Emberline public presentation · 2026-09-19

Frozen the public presentation as version 1.1.2. The release keeps the actual
tracker snapshot with cleaned Proposal 1–15 labels, removes the proposal-
architecture image from public surfaces, and records the verified README and
HTML review pages. No remote publication or repository rename is included.

Sponsor accepted the presentation and requested publishing preparation. Finalized
the public display name as Emberline — Shared Memory & Delivery Tracker for AI
Agents across the README, HTML and diagrams. Recorded acceptance and a publishing
handoff with licensing/privacy/name-clearance gates. No license adopted, repository
renamed, or remote publication performed; operating behavior is unchanged.

Removed the proposal-architecture image from the public README and HTML surfaces
at the sponsor's request. The source asset remains available but is no longer part
of the public story.

Replaced internal-ID tracker captures with a lightly edited snapshot of the actual
tracker, using a coherent Proposal 1–15 sample set. Kept the real UI, charts and
layout intact; added the proposal-architecture map separately as the concept visual.
Replaced the unreliable local marketing-page iframe in the sponsor review with a
rendered preview and direct link to the HTML page.

Following sponsor feedback, reduced the README to a short marketing story and
moved commands and detailed boundaries into `docs/GETTING-STARTED.md`.
Reworked the HTML highlight page into the same brief visual story, with
real tracker panels and links to the supporting documentation.
Proposed Agent Project Memory as the public display name and added a readable
mobile introduction and full-size visual links. Repository paths are unchanged.
Added `docs/public-review.html` as the durable review entry point, embedding the
current marketing page and linking the current sources instead of old previews.
Saved the complete Markdown-derived README rendering as a portable local review
artifact and embedded it in the sponsor review page.

Recorded the sponsor's expanded acceptance criteria and remaining review gaps
in `docs/PUBLIC-EXPERIENCE-BRIEF.md`. Corrected the reheat card's overflowing
text and labelled the generated workspace image as a concept illustration.
These are presentation changes; the operating standard is unchanged.

Added a product-overview hero explaining session continuity, the shared record,
and generated tracking for Claude Code and Codex. The complete README preview
is now generated from Markdown. Added a focused List screenshot and constrained
the mobile image so it no longer stretches across its gallery column.

The public front door is now named **Common Rules — Session Context & Delivery
Tracker** so the product's purpose is clear to a new Claude Code or Codex
reader. Reworked `README.md` and `docs/warmup-reheat.html` around the actual
problem — chats lose decisions, state, and a safe next step — then tell the
solution as one story: warm-up for a fresh session, reheat for a running
session, and the generated tracker and proposal ledgers as the evidence
surface. The first fold leads with an editorial overview photograph, followed
by the corrected non-overlapping warm-up/reheat diagram and authentic tracker
captures for overview, Kanban, Board, List, and responsive views.

The public guidance also calls out the sponsor's commit-and-push cadence:
accepted slices should land on `origin/main` regularly so the review surface
stays small, with `7cd1d49` recorded as the recent Loom engine example.

## 1.1.1 · Claude/Codex workflow parity · 2026-09-18

Updated the cookbook with one host-neutral workflow for Claude Code and Codex,
including the shared warmup/reheat, routing, implementation, review/testing,
merge and tracker-recording contract. Clarified that review/test log evidence
does not change a task's tracker state unless the item is explicitly moved to
`in review` or `in testing`.

## 1.1.0 · Cross-Agent Project Operating Standard · 2026-09-18

The shared tracker now uses one nested-task denominator across its header,
status controls, proposal summaries, completion tiles, and history graph. It
also shows a velocity-based completion projection, uses a true completion bar
in expanded task rows, and separates work-group and task-status badges for
readability. The generated tracker is kept aligned for both Claude Code and
Codex consumers.

## 2026-09-18 · the board template's dropdown/heading defects, seen on a project with one proposal (P-14)

The sponsor: "also the dropdowns created by app and engine are not visually
correct. is it the problem of the template" -- yes: `tools/tracker/board.py`
and `tools/tracker/history.py` are shared by every project, so a defect in
either lands on every project's page. common-rules' own page, with thirteen
proposals, hides these; PhotoVault/engine's, with one, showed all five
starkly. Fixed on the engine's page (rendered read-only to a scratch
directory, never written back into that project) and re-checked on
common-rules' own, at 1400px and 430px, light and dark:

1. The clusters heading's count ran into the word ("TOUCHED0"): the shared
   `margin-left:6px` rule named `.chip .n`, `.col h2 .n` and
   `.attention h2 .n` but not `.clusters h2 .n`. Checked every other `<h2>`
   carrying a count on the page (every status column, "Waiting for an
   answer", and the clusters heading itself) -- those three were already
   all the rule needed to cover, now it does.
2. Two chart lines ending close together (the engine's `total`=72 and
   `done`=69) printed their end-of-line value labels on top of each other.
   `history._line_chart` now computes every series' end-label position,
   then a new `_spread_end_labels` nudges any that would collide at least
   14px apart (never off either end of the plot), keeping each beside its
   own line -- a placement fix, no label dropped.
3. `.charts{max-width:760px}` left roughly half of a 1400px page blank.
   Replaced with `max-width:min(100%,1040px)` -- a real upper bound, still
   using most of the page's own width.
4. The folded "By urgency" summary (`.cgroups`) floated as bare text
   between cards -- the shared card-surface rule named `.clusters` and
   `.lanes` but not `.cgroups`. Now all three share it.
5. The proposal filter nav below the charts is a genuine feature with more
   than one proposal (it narrows the Board/Kanban/List views, something
   the Proposals tree above cannot do), but with exactly one it had nothing
   to filter among and only repeated the tree's own completion line for
   that lone proposal. It is now omitted when there is only one, kept
   otherwise -- checked common-rules' own 15-proposal page still shows it.

Extended `tests/test_tracker_board_clusters.py`, `tests/test_tracker_board_completion.py`,
`tests/test_tracker_board_progress.py` (the old `760px` pin replaced) and
`tests/test_tracker_history.py` (new `_spread_end_labels` and end-label
collision coverage).

## 2026-09-18 · 1.0.0 — the first baseline of the standard

`VERSION` moves 0.9.0 -> 1.0.0 and the commit is tagged `v1.0.0`. A project
adopting the standard now has a fixed target instead of a moving `main`,
which is the whole point: finding 21/F-02 recorded that the standard had
outrun every project following it, with 16 to 21 mandatory changes queued
per repo and not one ready card.

Cut on a green main: 1,966 tests in 219.6s through the parallel gate, all
twelve conformance checks holding, the card reading ready, 122 of 128 ledger
items done.

`docs/RELEASE-1.0.0.md` says what a project gets and, as plainly, what is
not in it: L-07 at 80% on the back burner with its failing measurement
quoted (the sponsor ruled "L7 will remain on back burner"), adoption
excluded because this repo is prohibited from writing into another project,
and V-03's lock deferred to 1.1.0 -- `.common-rules-version` still holds the
bare `<count>-<sha>`.

## 2026-09-18 · VERSION: a semver beside the stamp, and a changelog that keeps it honest (proposal 32, V-01/V-02)

The sponsor: "Can you version the common rule and release a baseline when the
pending tasks are done. Use semantic version version and change Lock to
maintain it going ahead."

`VERSION` at the repo root now holds a semver, starting at `0.9.0` --
deliberately not `1.0.0`, which proposal 32's V-04 cuts separately, on a
green main, once nothing is pending. The `<commit-count>-<sha>` stamp
`rulecheck` has always computed is kept exactly as it was: two releases can
share a semver while the repo has moved on, and the count-sha is still what
settles which is newer. `rulecheck` now reports both together wherever it
names the current version at all -- `--version`, aligned, behind, no stamp --
as `0.9.0 (187-5a62e87)`.

The bump is never typed by hand or guessed from prose -- it is read out of
the CHANGELOG. `bin/version-check` (`tools/version_check.py` holds the
logic, the same split `bin/workflow-stamp` and `tools/workflow_stamp.py`
use) finds the commit that last set `VERSION` to its current value --
VERSION's own git history is the release marker, not a tag or a heading,
because VERSION already changes exactly when a release happens, so there is
nothing separate to forget to update. It then reads what the CHANGELOG
added since: any entry carrying `**Standard change (mandatory):**` (the
existing marker, proposal 21 S-09) forces at least a MINOR bump; an entry
that also carries a new `**Breaking change (major):**` line forces MAJOR --
declared, never inferred, because a wrong guess there would silently tell
every adopting project a breaking change is safe to ignore; everything else
that shipped is PATCH. `--check` exits non-zero when `VERSION` disagrees
(too small a bump, or none at all) and writes nothing either way. It is
wired into `.common-rules.json`'s `gates.merge`, beside
`bin/workflow-stamp --check`, mirrored byte-identically in
`.github/workflows/ci.yml`.

The bump rule itself is written into `CLAUDE-workflow.md`'s existing
version-stamp section ("A project that has aligned before must stay aligned
to keep landing"), not a new top-level one.

**Not a Standard change.** Nothing here asks an adopting project to do
anything it did not have to before: `.common-rules-version`, the stamp a
project writes and `bin/land` compares, is untouched -- it still holds only
the count-sha, exactly as before. `bin/version-check` and its gate are
common-rules' own `.common-rules.json` and `ci.yml`, not a project's. The
only visible change to a project is that `rulecheck`'s human-readable text
now shows a semver alongside the count-sha it already showed.

`VERSION`, `bin/rulecheck` (`current_semver()`, `version_label()`),
`bin/version-check`, `tools/version_check.py`, `tests/test_version.py` (23
cases), `CLAUDE-workflow.md`, `.common-rules.json`, `.github/workflows/ci.yml`.
## 2026-09-18 · pull a waiting part forward from the tracker page (P-13)

The sponsor: "make a button in the tracker where I can trigger the tasks to
be uh, completed sooner. Instead of on 23rd September or things like that."
The published tracker is a static page that can run nothing on his Mac, so
every part that `tools/tracker/parts.py`'s `is_waiting()` calls waiting --
a `waiting_until` date, or an owner of the form `session:<name>` -- now
carries a "Pull forward" row: what it is waiting for, in text; a button
labelled "Copy the command that pulls this forward"; and, once clicked, a
confirmation that states plainly nothing has run yet and shows the exact
command to paste into a session for this project. `navigator.clipboard`
copies it, with a `document.execCommand("copy")` fallback. The page still
reads correctly with JavaScript off -- the waiting reason stays visible as
text, the button is just inert.

The command needed `tracker set` to actually clear a date, which it could
not do before this: `--waiting-until` only ever took effect from
`--add-part`, so editing an already-waiting part or item silently ignored
it. `--waiting-until` now edits an existing item's or part's own
`waiting_until` directly, and `none` (or `now`) removes the key instead of
setting it to anything -- `tools/tracker/set.py`'s `_apply_waiting_until()`,
covered in `tests/test_tracker_set.py`. A session-owned wait has no date to
clear, so its command reclaims the part with `--owner lead` instead --
honest about what it can do (say the ledger no longer waits on that
session), not about making that session act.

Assessed and deliberately not built: a `db`-capability queue on the page
itself, so a pull-forward request is recorded for a session to read at
warm-up instead of needing to be pasted by hand. Left for the sponsor to
weigh against a clipboard button that always works and never rots silently
unread.

## 2026-09-18 · what the sponsor types after /warmup or /reheat is context

**Standard change (mandatory):** both skills now say that anything typed
after the command is passed through as `--context "<his words>"` in the same
run, quoted as typed. A project whose sessions drop it loses the one thing
that command carries of his.

The sponsor: "when I try to create a new session uh, I am not able to add
context after the warm up or reheat". `bin/warmup --context` has existed and
worked all along -- the flag is implemented, documented in `--help`, printed
on the card and saved into the state file. What neither skill said was what
to do with words typed after the slash command, so a session read
`/warmup we are picking up the engine work`, ran the bare command from the
skill body, and dropped the sentence.

Both skills keep the second case too -- context that was not typed on the
command line, from a handoff or from earlier in the conversation.

## 2026-09-18 · workflow.html's stamp is generated, not hand-typed (O-12)

`docs/README.md`'s rule is that any PR changing the shared rules updates
`docs/workflow.html` and its version stamp in the same PR. Three merges on
17 Sep did none of it, main went red on `tests/test_workflow_stamp.py`, and
the stamp got hand-typed twice in one evening because every rules merge
bumps the number it must match again.

`bin/workflow-stamp` writes the stamp from git and regenerates
`docs/workflow.png`, folding the headless-Chrome recipe (the load-bearing
`--headless=old`, then the trailing-blank crop) into the script so nobody
types it by hand. `--check` reports drift without writing anything.
`tools/workflow_stamp.py` now holds `rules_version()` and friends, imported
by both the tool and `tests/test_workflow_stamp.py`, so the two can never
independently drift on what the required stamp is. The tool does not write
the prose describing a rules change — that still needs a human sentence on
the page; this only removes the bookkeeping around it.

**Wiring, and what was rejected.** `derecord`'s pre-commit hook regenerates
a project's tracker pages whenever a ledger is staged — the same shape
looked natural here, but it is the wrong scope for this: that hook fires on
every commit that touches a ledger, which is most commits, while
`rules_version()`'s whole point (see its docstring) is that a commit which
does *not* touch `CLAUDE-workflow.md` must be a no-op for the required
stamp. Hooking png regeneration to ledger commits would burn a 5MB
rewrite — and a `--headless=old` Chrome launch — on commits that never
touched the rules at all. Instead: `bin/workflow-stamp --check` is now the
first thing `.common-rules.json`'s `gates.merge` runs (and the identical
`ci.yml` step, kept byte-equal by `tests/test_ci_matches_land.py`), so a
stale stamp fails fast, before the full suite, rather than sixty-some
tests deep into `test_workflow_stamp.py`'s own assertion.

Not a Standard change: nothing here changes what any other project must do
differently — `docs/workflow.html` is common-rules' own page, and the gate
addition is to common-rules' own `.common-rules.json`.

`bin/workflow-stamp`, `tools/workflow_stamp.py`,
`tests/test_workflow_stamp.py` (12 new cases, real Chrome never run —
`FAKE_CHROME_MODE` stands in for the capture step), `.common-rules.json`,
`.github/workflows/ci.yml`, `docs/README.md`.
## 2026-09-18 · `ruflo-item` records several items in one invocation (O-11, finding 31/F-05)

Every `ruflo-item` call stops the Ruflo daemon in a `finally` -- correctly,
since it spawns headless Claude sessions that burn tokens until told to stop
-- so the *next* call cold-starts it again: one call measured 3.3s, and ten
items recorded one at a time (twenty invocations) did not finish in 500s.
This item was found backfilling conformance check 9 for fourteen items
closed without their Ruflo records: fourteen `start`+`done` pairs, one call
at a time, took about eight minutes.

`start` and `done` now each accept a repeatable `--item ID:TEXT` flag
(split on the first `:`, so TEXT may itself contain colons) instead of the
positional `<ID> "<task>"` / `<ID> [<ID> ...] "<summary>"` form -- several
ids, each with its own text, in one process: one binary resolution, one
daemon start, one stop, whatever happens (a crash, Ctrl-C, a signal, or one
id in the batch failing its memory store). Chose the flag form over a
single-line-per-id summary because argparse cannot unambiguously split a
flat list of ids from a shared trailing summary once both are optional --
`--item` sidesteps that, and reads no worse for a lead typing two or three
ids than the existing positional form does for one. The positional form is
untouched: a plain single-id call behaves exactly as before, and existing
callers (`bin/warmup`, the templates, every brief) need no changes.

`ruflo-item from-ledger LEDGER [--since DATE]` is the same idea driven by a
ledger file: it loads LEDGER once, finds every item with status "done" whose
closed date (`tools/tracker/ledger.py`'s new `closed_date()`, shared with
`bin/conformance` check 9's own reading of "when did this item close") is on
or after DATE, and records `item:<ID>:start` / `item:<ID>:done` directly
from each item's own `title`. It does **not** re-run the project's merge
gate or call hooks pre-task/route/post-task/testgaps -- this is a memory
*record* of history, not a re-run of it, and every stored value says so
outright ("... -- backfilled 2026-09-18T..., originally closed 2026-09-17;
recorded after the fact, not logged as the work happened"), so nothing
reading Ruflo memory later mistakes it for a live start/done pair. This is
what turns a fourteen-item backfill from eight minutes into one call, and
what conformance check 9 now sends the next lead to.

Not a Standard change: no existing call's behaviour moved, so no project is
out of conformance for not adopting the batch form. It is available to every
project on the standard the moment it pulls this change, and a lead closing
several items at once should reach for it, but conformance does not (and
should not) fail a project for still calling `start`/`done` one id at a
time -- that path costs time, not correctness.

`bin/ruflo-item`, `tools/tracker/ledger.py` (`closed_date()`, shared with
`bin/conformance`), `tests/test_ruflo_item.py`.
## 2026-09-18 · one filter bar at the top, governing every view (P-11)

The sponsor: "right now there are filters board list and there should be
another filter and then basically I should be able to filter all types of
views the drop down the board and other things so I have a common set of
filters there on top so it's possible for me to just in the drop down list
as well uh, filter the pending items". The bar used to sit under the Details
heading and govern only the board and list; P-10's Tree/Kanban switch had
been added into that same bar, so the switch for the page's top views was
buried mid-page.

The bar now sits directly under the header totals, above the tiles, and is
sticky. Its view switch is one group of four -- Tree, Kanban, Board, List,
Tree the default -- and every filter (status, owner, tier, group, search)
applies identically to whichever is showing. The part most likely to have
been done shallowly: the bar now reaches inside the Proposals tree's own
dropdowns. A non-matching item or part is hidden; a proposal left with no
matching items is hidden entirely; a surviving proposal shows how many
matched ("3 of 16 items") beside its real done-count, which a filter never
changes. A matching proposal, and a matching item down to its parts,
auto-expands under an active filter -- he is filtering in order to see the
matches -- and only Clear ever collapses it back, never the filtering itself
mid-session.

A first-class Pending control -- not a status chip -- shows only work that
is not done, at every level. Rather than a second switch that could disagree
with the existing "Show finished" toggle, Pending reuses its "hide
group=done" rule and forces it off (and disables it) while Pending is on;
the page states this rule in one sentence next to the two controls. Chip and
"N shown" counts key off one CSS class per view (item-row / kcard / card /
row), so switching views can never double- or under-count the same
underlying items. View, every filter, the search text and Pending persist
per viewer in `localStorage`, every read and write wrapped in `try/catch`;
the page still renders correctly, unfiltered on Tree, when storage throws or
is empty.

`tools/tracker/board.py`, its CSS and inline script, and
`tests/test_tracker_board_filters.py` (new) plus extensions to
`tests/test_tracker_board_progress.py`. Not a Standard change -- this is the
tracker's own page, not a rule every project must adopt.

## 2026-09-18 · two decisions the lead was asked to make itself (31/A-02)

The sponsor: "make the decisions yourself for the pending items and complete
the work." and "I will run the pilots myself."

**Who merges a rule change here (finding 31/F-03) — no contradiction after
all, and no file changed.** CLAUDE.md line 18 governs *initiative*: a session
never starts a change to these rules of its own accord, and that line stands
exactly as written. The ruling of 14 Sep 2026 governs *mechanics*: a change
the sponsor directed, once its gate is green and its review has passed, is
merged by the lead rather than handed back as a `gh pr merge` command.
`bin/land` keeps refusing to land automatically inside common-rules, for the
reason written beside that guard — landing automatically would let the AI
change the rules it operates under without anyone saying yes. A reviewed PR
merged by the lead is not that, because the change was directed and the
review happened.

**common-rules does not declare a `staging_branch` (O-08).** Three reasons.
`bin/land` refuses inside this repo, so `--advance-staging` could never run
here and the mechanism would sit inert. The merge gate is now 201.5s, so the
red-main insurance a staging branch buys is already affordable by running the
gate. And a feature that has only ever run against fixture repos should not
debut on the repo every other project depends on. It ships available and
undeclared; the sponsor pilots it where he chooses, in his words: "I will run
the pilots myself."

## 2026-09-18 · the proposal tree is the top view, and a Kanban view sits beside it (P-09, P-10)

The sponsor: "at the top, there should be like proposal nineteen. And when I
expand it, then there should be P1, P2, P3. And then when I expand P1, then
there should be P1, A, B, C, D" and "there could be a second button which can
switch to the Kanban style." `tools/tracker board`'s drill-down (P-08) already
did the first part, but it sat under the finish-now/back-burner/waiting
grouping, so the first thing the page showed was items sorted by urgency, not
his proposals.

P-09: the page now reads header totals, tiles, progress charts, the proposal
tree, then that old grouping folded into a closed `<details>` below it --
same pattern as the existing Lanes "Advanced" block, not a new one invented
for this. A title long enough to break a row (an item title that is an
entire conformance error dump, live on P19) is clamped to two lines in CSS
(`-webkit-line-clamp` plus a plain `max-height` fallback) and carried in full
in a `title` attribute -- never truncated in Python.

P-10: two buttons, Tree and Kanban, sit beside the Details filters. Kanban
columns are `tools/tracker/ledger.py`'s own status order (not the board's
attention order), one column per status including empty ones, one card per
item with its id, title, proposal, completion % and bar; a card whose item
has parts shows "N of M parts done" and expands in place to list them. Both
views are rendered server-side into the same page; the inline script only
toggles which `hidden` -- no reload, no round trip -- and remembers the
choice per viewer in `localStorage` (`tracker-topview`), wrapped in
try/catch, defaulting to Tree when it throws or returns nothing.

tools/tracker/board.py, tests/test_tracker_board_completion.py,
tests/test_tracker_board_progress.py.

## 2026-09-17 · the merge gate runs in parallel, and the suite is four times faster (O-02)

**Standard change (mandatory):** a project's `gates.merge` runs its suite
through `bin/quiet --jobs auto`, and its CI workflow runs the identical
command. Declare it in `.common-rules.json` and change the workflow file in
the same PR; `tests/test_ci_matches_land.py` fails if the two drift.

Measured on one commit, back to back, machine load 4.7-7.7:

| run | wall clock |
|---|---|
| serial | 965.6s |
| `--jobs auto`, cold shard cache | 410.7s |
| `--jobs auto`, warm cache | 245.8s |

Then the full suite on merged main, through the new gate: OK, 1853 tests,
**201.5s**. Proposal 23's M-01 promised this in September and was closed
without measuring it (finding 23/F-07); this entry exists so the next person
can check the claim rather than trust it.

Three changes compound to get there, none of them sufficient alone: warm-up
stopped spawning 23 subprocesses to measure conformance (O-09, 1.9s -> 2.1s
under load but half its former cost on a quiet machine), shards now split
*within* a slow file instead of only between files (O-10 -- the cold-to-warm
jump from 410.7s to 245.8s is that split), and the slowest file's fixture is
built once and copied (O-01, worth 7%, which is also the record that my first
diagnosis was wrong).

# Changelog — common-rules

## 2026-09-17 · warm-up stops shelling out 23 times to measure conformance (O-09)

31/F-01 measured `bin/warmup`'s own cost: 1.9s on a quiet machine, of which
1.21s was `bin/conformance measure()` running 23 subprocesses -- two of
them a whole extra Python interpreter (`bin/warmup --check` and
`bin/proposalcheck`, each re-importing and re-compiling every module they
touch from scratch, since conformance's subprocess env sets
`PYTHONDONTWRITEBYTECODE=1`). Every session pays this at startup and after
every compaction; `tests/test_warmup.py` pays it 122 times, which is most
of that file's 575s.

Two changes, same verdicts:

- `check_card` (item 12) and `check_proposals` (item 7) now import
  `bin/warmup` and `bin/proposalcheck` and call their `main(argv)`
  in-process (`run_inprocess()`), capturing stdout/stderr into the same
  `subprocess.CompletedProcess` shape the rest of the code already expects,
  instead of spawning `sys.executable` on each. This cut the interpreter
  spawns from 2 to 0 (measured with a `subprocess.run` counter): the
  remaining subprocess calls are all `git`. `_load()` now registers the
  loaded module in `sys.modules` before `exec_module()`, which
  `bin/proposalcheck`'s `@dataclass` needs (it looks its own module up
  there; loaded by path, without this it wasn't present) -- the same reason
  `Result` above is a `NamedTuple`, not a `@dataclass`.
- The twelve checks only read the repo, so `measure()` now runs them
  concurrently in a thread pool. `ThreadPoolExecutor.map` returns results
  in the order its iterable was given, not completion order, so the
  card's text is identical run to run -- proved by diffing
  `bin/conformance`'s and `bin/warmup`'s full output before and after
  against the same commit (empty diff both ways). `Context.ledgers()` gained
  a lock, since two checks racing its `_ledgers is None` cache would
  otherwise compute and overwrite it twice; `run_inprocess()` gained one
  too, since `contextlib.redirect_stdout`/`redirect_stderr` swap the
  process-global `sys.stdout`/`sys.stderr`, not a thread-local, and two of
  the twelve checks (7 and 12) call it.

Measured on the same commit, machine under load (`vm.loadavg` ~5.7-7.3, not
quiet): `bin/warmup --project . --no-recall --no-pull` 3.7-4.2s before, 2.1s
after, three runs each; `bin/conformance --project .` 3.7s before, 2.1s
after. A pure speed-up, not a Standard change -- no project has to do
anything differently.
## 2026-09-17 · a staging branch, so main is never red (O-08)

**Standard change (mandatory):** a project can declare `"staging_branch":
"<name>"` in `.common-rules.json`. Once it does, `bin/land` merges a
reviewed branch onto that branch instead of main -- creating it from main
the first time it's needed -- running the exact same gate it always has:
this changes *where* a branch lands, never what it's tested against. `main`
then only ever moves through `bin/land --advance-staging`, which re-runs
the gate on staging itself and fast-forwards main to staging's tip on a
green verdict only. It refuses, never guesses, when the gate is red, when
staging is behind main (a commit reached main some other way), or when the
verdict cannot be read at all -- no declared test suite is a refusal, same
as a red one, never a pass. A project that never declares `staging_branch`
is unaffected: `land` goes straight to main, exactly as before this key
existed. No project under `apps/` declares it yet -- the switch is the
sponsor's to throw.

The sponsor, this session: *"We can also reduce the number of tests so we
can have a development branch or a staging branch where we can keep
merging changes and then after a considerable amount of changes are done,
we can test in one go. Rather than testing again and again in smaller
batches. We can test larger batches."* What this reduces is how often the
full suite runs against main, never what it covers -- **no test is
deleted**. A smaller suite would have been just as green and just as
wrong: finance-tracker once carried 1,753 green tests over 16 wrong-money
defects, and only the negative cases nobody had cut ever found them. And
batch by time, not by commit count -- a batch big enough that a red
staging verdict can't be traced to the branch that caused it costs more to
untangle than the runs it saved; bisecting several already-merged branches
is worse than testing each as it landed.

`tools/project.py` documents and validates the key (`staging_target()`);
`bin/land` carries its own self-contained reader, the same pattern as its
`gates.merge` reader (`test_cmd()`/`test_command()`). Full rule in
`CLAUDE-workflow.md`'s Tests section, pointed to from the Git section, from
`templates/lead-prompt.md` §3 and from `templates/brief.md`'s MUST section.
`tests/test_land_staging.py` covers: a branch lands on staging and not on
main, staging created from main when missing, `--check` changes nothing, a
green staging verdict fast-forwards main, a red one leaves main untouched,
an unreadable verdict refuses rather than passing, staging behind main
refuses, and a project without the declaration behaves exactly as today.

## 2026-09-17 · pr-body and item-notes draft bookkeeping prose from recorded facts (O-05, O-06)

Proposal 31 measured a lead re-composing the same facts into prose three
times per item -- the PR body, the `ruflo-item done` summary, and the
`tracker set --event` text -- each a full model turn (~134k cache-read
tokens, measured) spent on words, not decisions.

`tools/itemfacts.py` gathers the facts once (the ledger item and its parts
via `tools/tracker/ledger.py`/`parts.py`, the diff and the branch's commits
via git) for both new scripts to read. `bin/pr-body [--project DIR] --item
ITEM_ID [--ledger LEDGER] [--base REF] [--title-only]` prints a PR title
and a body skeleton: the item's what/done/parts, the diff against --base
(default `origin/main`) with insertion/deletion counts and a test-file
count, the branch's commits, an unfilled `Gate:` line, and the trailer.
`bin/item-notes [--project DIR] --item ITEM_ID [--ledger LEDGER] [--commit
SHA] [--pr N]` prints a `ruflo-item done` summary and a `tracker set
--event` sentence from the same facts, in the voice real log entries
already use.

Per proposal 31's Decided section (D4): these scripts draft bookkeeping
prose from recorded facts. Neither decides whether work is done, whether to
merge, or what tier something is -- both print a draft to stdout and write
nothing, anywhere; the lead's own edits are what lands. Not a Standard
change -- available to any project that wants them, not required.
## 2026-09-17 · a gate runs in the foreground, briefs go out in one message (O-03, O-07)

**Standard change (mandatory):** every project on the standard runs its gate
in the foreground, in one blocking call, and reads the verdict line in the
same turn -- never backgrounded and polled, never a turn ended parked on a
timer. If a gate is too slow to sit through, that is a bug in the gate, not a
reason to poll. And every unblocked brief a lead has to send goes out in one
message, never one per turn; branches ready for review are read and decided
in one pass, not one turn each.

Measured this session: one agent turn costs about 134,000 cache-read context
tokens to produce a few hundred written tokens, so cost scales with the
number of turns, not the work inside them -- a poll that finds nothing new
still re-sends the whole context to learn nothing. 72% of the project's spend
went to lead orchestration, 25% to implementing. Two builders backgrounded a
16-minute test suite and spent turns checking on it that same day.

The sponsor's words, accepting proposal 31 in full: "Implement all the five
recommendations with the recommended decisions." D3 (O-03) and D5 (O-07) are
adopted as recommended.

Fixed: the rule is stated once in `CLAUDE-workflow.md` (the existing gate
paragraph, and the Issues section for batch dispatch) and in
`templates/lead-prompt.md` (§2 for the gate, §3 for batch dispatch), and
`templates/brief.md` restates the gate half of it for the builder who runs
one. No new top-level section was added to any of the three files.
## 2026-09-17 · `bin/commit-if-green`: gate, commit and push in one call (O-04)

Proposal 31, D4: a builder finishing a task spent three model turns on a
mechanical sequence after the gate -- `git add`, `git commit`, `git push` --
and the OK/FAILED call itself was read by the model from raw gate output
rather than checked by code. HANDOFF.md's operating rules (S3) record the
day that went wrong: a `grep ... && git commit` chain shipped a failing
test because grep exits 0 on a line containing "FAILED".

Added `bin/commit-if-green [--project DIR] [--message MSG | --message-file
FILE] [--push] [--timeout SECONDS] [--gate CMD...]`. It runs the gate through
`bin/quiet` (`--timeout`, default 600s: the gate is killed and nothing is
committed if it has not produced a verdict by then, with the log path
printed either way -- found while building this, when the full
affected-tests set ran into this very harness's 120s auto-background limit
and left no way to tell "still running" from "hung" without re-polling) --
default is the standard's own affected-tests gate (`tools/affected_tests.py
--base origin/main`, mapped to bare module names, `python3 -m unittest
<mods> -q` from `tests/`; falls back to the full suite when nothing is
affected) -- and commits (`git add -A` then `git commit`) only when quiet's
own verdict line starts `quiet: OK` **and** quiet's own exit code is 0.
FAILED, a nonzero exit, and an empty or unrecognised verdict line are all
treated as failure, never as success; it never re-parses the gate's raw
output itself, only quiet's one line. Refuses before running anything
(exit 2): bad usage, `--push` while on `main` (never pushed), a merge or
rebase already in progress, or nothing staged and nothing to stage. `--push`
uses `--force-with-lease` when the branch already tracks a remote branch of
the same name, otherwise `-u origin <branch>`. Appends the
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` trailer if not
already present. Exit codes: 0 committed, 1 gate failed, 2 refused before
the gate ran.

`tests/test_commit_if_green.py` (16 cases) runs it against throwaway git
repos with a fake gate: commits on green, commits nothing on red, the
FAILED-while-exit-0 grep trap, an unrecognised verdict from a stub
`bin/quiet`, a slow gate hitting `--timeout`, every pre-flight refusal
above, attribution added once and not twice, and both push shapes -- never
the real suite, never the real repo.

This is not a Standard change: the tool is available for a builder to use,
not yet required.

## 2026-09-17 · lettered parts are the standard way to split an item (P-06)
## 2026-09-17 · `tests/test_warmup.py` builds its seeded fixture once; `bin/quiet --jobs` dispatches longest-known-shard-first (M-01)

The sponsor asked why the suite needs so many tokens and whether it can run
locally. Measured: 1566 tests, ~16 minutes single-process; `tests/test_warmup.py`
alone was 575s for 122 tests (4.7s/test) -- a third of the whole suite in one
file. Its `Case.setUp` built a fresh `Project(seeded=True)` per test: `git
init` plus three git commands plus three separate `python3 bin/tracker`
subprocesses (render, board, checkpoint) -- about 5 interpreter starts per
test, before the test's own `bin/warmup` subprocess even ran.

Fixed: `tests/test_warmup.py`'s `Project` now builds that seeded fixture once
per test process (`_seeded_template()`) and gives each test its own
`shutil.copytree` (`.git` included) into a fresh temp dir -- a directory copy
is milliseconds, the five subprocesses were seconds. `Project(seeded=False)`
is unchanged. No test's assertions changed; same test count.

Also (M-01's own `done` criterion -- suite wall-clock measured before/after,
merge gate and land use it -- was never finished): `bin/quiet --jobs` sharded
one `unittest discover` process per file, but only balanced work by *count* of
files across a thread pool, not by each file's known runtime -- so one slow
file among several fast ones gave no wall-clock win if it happened to be
submitted last. `bin/quiet` now keeps a small cache of each shard file's last
measured duration (same placement rule as `tools/tracker/history.py`'s own
cache: `.cache/quiet-shard-durations.json` when the project already
gitignores `.cache/`, else system temp keyed by the repo's absolute path) and
dispatches longest-known-first, so the slow file starts at t=0 instead of
last; a cold cache still runs every file (round-robin). `--jobs auto` (or a
bare trailing `--jobs`) now resolves to `os.cpu_count() - 2`, floor 2.
`bin/quiet`'s verdict-line shape is unchanged.

Not a Standard change: neither `.common-rules.json`'s `gates.merge` nor
`bin/land` pass `--jobs` today -- confirmed by reading `bin/land`'s
`test_cmd()`, which reads `gates.merge` verbatim
(`python3 -m unittest discover -s tests -q`, sequential, no `--jobs`).
Wiring `--jobs` into the merge gate is the sponsor's call, not made here.

**Standard change (mandatory):** every item that cannot reach 100% in one
piece is split into lettered parts, ITEM.A, ITEM.B, ... (letters in order,
never reused). Each part is a tracked sub-ticket with its own status, owner,
share (whole percents adding to 100), optional `waiting_until` and risk with
reason, and log. An item's completion is the sum of its done parts' shares;
the item closes when its last part closes. Projects split their open
multi-part items at the next warm-up.

The sponsor's words: "I like the naming convention with ABC. That should be
standardized as the standard approach. And each ticket should be tracked in
the tracker or sub-ticket."

Fixed: `bin/tracker set LEDGER ITEM.X --status ... --event ...` updates a
part and closes the item when the last part closes; `bin/tracker set LEDGER
ITEM --parts '[{"title": ..., "share": ...}, ...]'` splits an unsplit item,
lettering A, B, C automatically. The tracker page shows an overview (tiles:
finish now / back burner / waiting, each item's parts) and a filterable
details section below, with the old Lanes view kept folded as "advanced".
The warm-up and reheat cards show each item's completion % and next open
part, and a group count line.

## 2026-09-17 · `tracker ask` can close an existing ask (ASK-01)

`tools/tracker/ask.py` only ever created A-nn rows. Nothing could move one
from `open` to `answered`/`became-item`/`declined` except hand-editing
ledger JSON, which the rules forbid -- so answered asks stayed `open` on
the card forever. Found 2026-09-17 by the lead closing A-29/A-30 in
`docs/proposals/23-eight-levers-for-token-spend.json`.

Fixed: `tracker ask LEDGER --close A-nn --state answered|became-item|declined
[--became ITEM-ID] [--note TEXT] [--by NAME] [--at ISO]` finds the ask,
sets its state, sets `became` when given (required for `became-item`, and
the item id must exist in that ledger), appends `--note` to any existing
note (joined with " · "), and records `answered_at`/`answered_by`
(mirroring the `answered_by` requests already carry, P20 D7; `--by`
defaults to "lead" when closing). Refuses, nothing written: `--close`
together with `--quote`/`--kind`; an unknown ask id; `--state open`;
`became-item` without a real `--became`; closing an ask that is not
currently `open`, unless `--force`. Validates the whole ledger before
writing, same as the create path.

## 2026-09-17 · the mandatory Ruflo loop actually runs: binary discovery, a declared namespace, and conformance on real evidence (RF-01)

**Standard change (mandatory):** projects declare `ruflo_namespace` in
`.common-rules.json` (the namespace their existing memories use), and run
`bin/ruflo-item start`/`done` around every item; conformance item 9 now
fails on items closed without Ruflo records.

Investigation: Ruflo is not on PATH on this machine, only in npm's npx
cache (`~/.npm/_npx/<hash>/node_modules/.bin/{claude-flow,ruflo}`, several
versions at once). `bin/ruflo-item` only ever looked at `$RUFLO` then PATH,
so every call since 15 Sep 14:12 exited 2 "no Ruflo binary found" and leads
carried on regardless -- the mandatory loop never actually ran. Separately,
`bin/warmup`'s card kept printing a binary path it found by globbing the
cache (mtime order, a second copy of the same logic), so a session's warm
card looked fine while the loop itself was broken; and neither tool knew
about a project's existing memory namespace (common-rules' own 90 entries
sit in `patterns`, not `common-rules`, the directory-name default), so even
a working binary would have read and written the wrong one. Conformance's
item 9 checked only that `.swarm/` existed -- "a proxy" its own docstring
admitted -- so common-rules read 12 of 12 while recording nothing per item:
33 `item:*:start` and 15 `item:*:done` keys against 92 closed items.

Fixed: `tools/ruflo.py` is the one binary/namespace resolver, imported by
`bin/ruflo-item`, `bin/warmup` and `bin/conformance` -- never two copies.
Binary resolution order: `$RUFLO` (a full command line, split with `shlex`),
then `claude-flow`/`ruflo` on PATH, then the npx cache, picking the HIGHEST
version by each candidate's own nearest `package.json` (never mtime or glob
order -- this machine's cache alone holds 3.38.21 and 3.41.4 at once).
Namespace resolution order: `--namespace`, then `$RUFLO_NAMESPACE`, then
`.common-rules.json`'s new `ruflo_namespace` key (`tools/project.py`
validates it: a non-empty, one-line string), then the project directory's
own name. `bin/warmup`'s card now shows the resolved binary and namespace on
its `ruflo` line; `bin/ruflo-item` prints which binary it used on every run,
like the namespace already was, and a missing binary now names all three
places searched. common-rules' own `.common-rules.json` declares
`"ruflo_namespace": "patterns"`.

Conformance item 9 no longer accepts a non-empty `.swarm/` as proof. It now
reads `.swarm/memory.db` read-only, straight with `sqlite3`
(`file:...?mode=ro`, table `memory_entries`, columns `key` and `namespace`
-- never through the CLI, which auto-starts Ruflo's daemon), and requires
both `item:<ID>:start` and `item:<ID>:done` under the resolved namespace for
every item, across every ledger, whose status is "done" and whose own close
date -- a log entry's `status` key equal to "done", else (older rows) the
last entry whose `event` is exactly "done" -- is dated on or after
**2026-09-17** -- the date this entry lands, so history before the fix is
reported ("N item(s) closed before 2026-09-17 have no Ruflo record (not
counted)"), never failed. A missing ledger or a missing/unreadable
`.swarm/memory.db` still fails item 9, as before. An id shared by two
ledgers (a collision) needs only one record -- Ruflo memory is keyed by id
alone, so it counts for both.

Review round: `_done_log_date` originally matched only a log entry whose
`event` is literally "done", but `tracker set --status done --event "<free
text>"` -- the normal way a lead closes an item -- writes that free text as
`event`; 35 of 92 done items in the real ledgers have no `event` reading
"done". `tracker set` (and `apply-staged`, which shares its code through
`apply_change()`) now also stamps the log entry's own `status` key with the
new status whenever `--status` changes one, independently of `--event`'s
wording; item 9 prefers a `status`-keyed close date, falling back to the
`event` match only for older rows that never wrote one.

Tests: `tests/test_ruflo_item.py` (unchanged behaviour, now routed through
the shared module -- a real Ruflo binary is never called, only a stubbed
`claude-flow` on PATH); a new `tests/test_ruflo.py` for `tools/ruflo.py`
(cache discovery with `$HOME` pointed at a temp dir holding fake
`node_modules/.bin/{claude-flow,ruflo}` trees and `package.json`s at
several versions -- the highest wins; `$RUFLO` still wins over all of it;
namespace precedence including `.common-rules.json`); `tests/
test_project_declaration.py` (`ruflo_namespace` validation, and the state's
pinned key set); `tests/test_conformance.py`'s `TestItem9Ruflo`, rewritten
against a temp sqlite `memory_entries(key, namespace)` table -- passes with
both records present after the cutoff, fails naming missing ids, ignores
(while counting) items closed before it, and prefers a `status`-keyed close
date over an `event` match, falling back to `event` for a row with no
`status` key; `tests/test_tracker_set.py`'s `TestLogEntryStatusKey` (`--status`
stamps the log entry's `status` key regardless of `--event`'s wording,
`--event` alone never does, and the ledger still validates).

Verified read-only against the real repo (`bin/conformance --project
common-rules`'s item 9 line, and `bin/warmup --project
common-rules --no-recall --no-pull | grep -i ruflo`) --
never against a real Ruflo binary or a write to the real `.swarm/`.

## 2026-09-17 · `bin/ruflo-item` works from worktrees; `bin/spend` subcommands answer `--help` without running (P23 F-03, F-04)

Two ledger findings from proposal 23's backlog.

**F-03**: `bin/ruflo-item` resolved the Ruflo/`.swarm/` cwd as
`project_root()` -- the current project's own toplevel. From a linked
worktree that is the worktree itself, not the main checkout where `.swarm/`
actually lives, so every `hooks`/`memory` call there failed with "Database
not initialized" and the mandatory Ruflo loop silently recorded nothing for
worktree work. `ruflo-item` now resolves `git rev-parse
--git-common-dir`'s parent -- the main checkout's own root -- for every
Ruflo/daemon call, while `done`'s merge gate still runs in the actual
worktree; the main checkout's own behaviour is unchanged, since there the
two paths are already the same. Separately, the `memory store` call that
actually persists `item:<ID>:start`/`done`/`note` is no longer folded into
the same best-effort `|| true` as pre-task/route/search telemetry: a failed
store now exits `ruflo-item` nonzero with a one-line message instead of
looking like success.

**F-04**: `spend calibrate --help` (and every other `spend` subcommand's
`--help`) fell straight through to the real command -- `spend calibrate
--help` ran a real calibration against the default worklog dir, which wrote
a false `last_calibrated_at` into the real repo on 16 Sep. Every `spend`
subcommand now checks `-h`/`--help` in its own args before doing any work,
printing that subcommand's usage line and exiting 0.

Tests: `tests/test_ruflo_item.py` (`TestWorktreeRufloCwd`,
`TestRequiredMemoryStore`) and `tests/test_spend.py` (`TestHelp`) --
red-then-green against a temp repo + linked worktree and a stubbed `ruflo`,
and against a temp calibration `--out` dir; no real Ruflo binary or `.swarm/`
is ever called, and `spend calibrate`'s worker function is mocked to raise
if it is ever invoked at all.

## 2026-09-16 · `bin/worktree-sweep` cleans up finished worktrees (WT-01)

**Standard change (mandatory):** common-rules alone had grown ~54 worktrees
-- agent worktrees under `.claude/worktrees/agent-*`, lead worktrees under
`.worktrees/<name>`, and `claude --bg --worktree` sessions -- with nothing
removing the finished ones. Most had gone through a squash-merged GitHub PR,
so their branch commits were never ancestors of `origin/main` even though
the work was long since merged: ancestry alone cannot answer "is this
merged", which is why the new checker asks it four ways (ancestor of
`origin/main`, nothing committed beyond `origin/main`, a merged GitHub PR
for the branch's head, or `git cherry origin/main <branch>` showing every
patch already landed) before ever calling a worktree removable.

`bin/worktree-sweep --project DIR [--apply] [--json] [--idle-hours N]`
prints one line per worktree with a verdict and reason, dry-run by default;
`--apply` removes only worktrees that are clean, merged by one of the four
checks above, and idle (nothing touched in `--idle-hours`, default 2, no
running `claude` background session and no OS process with its cwd inside
it). Anything uncommitted, unmerged, or active is kept, with the first
failing reason. `git worktree prune` runs alongside it and reports any
administrative entry whose directory is already gone. The main checkout is
never a candidate. Three guards were added in review, each after a real case
in common-rules' own first dry run: a merged PR counts only when its head is
the branch's tip (commits made after the merge are unmerged work); a
worktree registered outside the project directory (one lived in another
app's folder) is never removed; and a worktree that contains another
worktree is kept, since deleting its directory would delete the inner one.

Projects: run `bin/worktree-sweep --project . --apply` when a session ends
and after landing a batch, so finished worktrees stop piling up.
`CLAUDE-workflow.md`, "Working alongside other sessions", carries the rule.

## 2026-09-16 · Findings are distinguishable across ledgers and never land unsized (P26 F-01)

**Standard change (mandatory):** C-05's first real use exposed two defects
in `tools/tracker/findings.py`. Finding ids are per-ledger (`F-01`, `F-02`,
...), so the cross-ledger queue the feature exists to provide -- `tracker
findings lanes`, and board.py's file-overlap clusters, both of which combine
every ledger's findings into one list -- showed four different proposals'
findings as four indistinguishable `F-01` rows; worse, `cluster.py`'s
`_UnionFind` keyed by bare id silently collapsed two different ledgers'
`F-01` onto one key and could cluster findings that share no file at all.
And `tracker findings add` wrote `value`/`points` only when given, with
nothing requiring them, so every finding landed unsized and the lane
ranking C-05 was built for had nothing to rank.

A finding's id is now proposal-qualified (`26/F-01`) wherever it can be
confused with another ledger's same-numbered finding -- `tracker findings
lanes`'s combined queue and `not_taken_rows()`'s rows for the board's
clusters -- via the new `ledger.qualify_finding_id()`. An item's id is
untouched; it already avoids the collision. Stored ids are never
renumbered, and single-ledger uses (`decide`/`defer`/`decline`/`triage`,
`light_eligible`) still take and return the plain id.

`tracker findings add` now refuses without `--value` and `--points`,
naming both, unless `--unsized` is passed -- which records `unsized: true`
on the row instead. An existing finding with neither sizing fields nor the
new flag (catalogued before this fix) still validates. At your next
`/warmup`, any script or brief that calls `tracker findings add` without
sizing must add `--value`/`--points` or `--unsized`.

`tests/test_tracker_findings.py` and `tests/test_tracker_cluster.py` were
red on the old code (bare `F-01` colliding across ledgers, and `add`
succeeding with nothing to rank) and are green on the new.
## 2026-09-16 · `rulecheck --align` refuses while a mandatory Standard change is pending (P21 F-01)

**Standard change (mandatory):** `rulecheck --align` wrote the stamp
unconditionally -- it never called `mandatory_pending()` first, so nothing
technically stopped a session aligning past an unimplemented mandatory
Standard change. Only the card's own failure (and the docs saying not to)
made that visible, and neither one is a refusal. Now, with a pending
mandatory entry (`mandatory_pending()` state "behind" or "no stamp" with
entries), `--align` alone writes nothing, prints each entry's title, and
exits 1. Once they are implemented, `rulecheck --align --implemented` aligns
and prints what was acknowledged ("aligned past N mandatory change(s),
declared implemented: ..."), so the declaration is on record in the session
output. `--align` with only information entries pending, or none, needs no
flag and behaves as before. A stamp that is "unresolvable" (its commit left
the rules history, as a squash merge can do) counts every mandatory entry as
pending, so it needs `--implemented` too -- and gets through with it, since
aligning is the only way to repair such a stamp. When rulecheck "could not
check" at all, it refuses, `--implemented` included.
Projects: after implementing a pending mandatory Standard change, align with
`rulecheck --align --implemented`, not `rulecheck --align` alone.

## 2026-09-16 · Rows `warmup --queue` writes are routed, and common-rules holds 12 of 12 again

**Standard change (mandatory):** `tools/tracker/queue.py` wrote every queued
row with `cx: C2` and no `tier`, `model` or `tag`, so any project that ran
`warmup --queue` -- which the standard makes routine at every warm-up --
failed conformance item 6 on the very rows the standard had just asked it to
record. Queued rows now take tier, model and tag from the ledger's own `tiers`
row for their `cx`, never a hardcoded model. At your next `/warmup`, give any
existing row with a `queue_source` and no `tag` its route with
`tracker set <ledger> <id> --field tier=... --field model=... --field 'tag=[ruflo · <tier> · <model>]'`.

Found by common-rules reheating itself: conformance read 10 of 12. Item 4 --
its pre-commit hook was stale; `bin/derecord` reinstalled it, and in passing
corrected a stale `.claude/skills/warmup/SKILL.md` and installed the missing
`.claude/skills/reheat/SKILL.md`. Item 10 -- two per-ledger publish sidecars
(P21, P23) for ledgers with no tracker of their own, removed under proposal
22's one-tracker rule. Queuing those two fixes then broke item 6, which is how
the queue defect surfaced. `tests/test_tracker_queue_routing.py` is red on the
old writer and green on the new.
## 2026-09-16 · `spend calibrate` no longer credits one item with another's tokens (P25 Z-05)

`tools/calibrate.py` summed worklog tokens by bare item id, and bare ids are
not unique. A real collection of 2,023 transcripts showed it: common-rules'
S-06 and S-03 were credited with PhotoVault's own S-06 and S-03, and W-01
names both proposal 19's item and proposal 27's in this very repo. A
calibration run on that data would have flagged items for costs that were
never theirs.

Two rules now. A worklog row counts toward a project only when its session
started in that project's directory or in one above it (a session opened in
`apps/` that worked on common-rules still counts; one started in
`apps/PhotoVault` does not). An id that appears in more than one of the
project's own ledgers is left out of the calibration and named in
`skipped_ambiguous`, since its tokens cannot be split between the two.

Not a Standard change: nothing for a project to do. Known and not fixable
retroactively: a brief whose first line names a bundle rather than an item
(`BUNDLE-K M-08, C-03, R-04`) credits its tokens to the git branch, so those
items show no cost at all. The brief template's own first line,
`[ruflo · tier · model] ITEM-ID title`, attributes correctly -- use it.

## 2026-09-16 · `tracker published` refuses a changed title -- T-06's missing half (P22 T-06)

**Standard change (mandatory):** T-06 ("a published page's name is set once
and never changes") was closed with only half its done-when built: the rule
stated in CLAUDE-workflow.md, and a test pinning that `render.py`'s own
`<title>` is a pure function of the project name -- but no runtime check.
`tracker published` recorded `{url, digest, ledgers, by, at}` (or the
per-ledger equivalent) and never read, stored or compared a page's
`<title>` at all, so a session could republish a page under a different
name and nothing would refuse it.

`tools/tracker/render.py`'s `published_project_main` and `published_main`
now extract the page's `<title>` (via the new `page_title()`) and record it
in the sidecar. A later publish of the same URL whose page's `<title>`
differs from what the sidecar last recorded is refused, naming both
titles and proposal 22 T-06, unless `--title-changed` says the rename is
deliberate (recorded as `title_changed: true`, mirroring `--page-unchanged`'s
precedent for a recorded override). A sidecar with no recorded title --
every one committed before this change -- has nothing to compare: it is
accepted and gains a title going forward, so no existing sidecar under
`docs/proposals/tracker/` is invalidated. A page with no `<title>` at all
(a declared `plan_page` generator need not emit one) has nothing to record
or compare either.

Every project on the standard that calls `tracker published` should expect
this refusal the first time a page's title actually moves between publishes,
and pass `--title-changed` only when the rename is intentional.
## 2026-09-16 · The lead runs on Opus, at low or medium effort (P23 A-22)

**Standard change (mandatory):** the `C4` row of every project's `tiers`
table now reads `"model": "opus", "effort": "low or medium"`, replacing the
`"lead model"` placeholder that named no model at all. At your next
`/warmup`, update your ledger's own `tiers` table to match, and retag any
`C4` item still carrying `model: "lead model"` (its `tag` becomes
`[ruflo · lead · opus]`). A ledger-wide tier change invalidates every `C4`
item at once, so `tracker set` cannot repair them one at a time — each
intermediate state fails validation. Change the tier and its items in one
write, then validate.

The sponsor's ruling, in his words: *"and i think leads should be atleact
Opus with low of medium effort"*, with the reason he gave in the same
breath: *"we are finding too many gaps if sonnet is the lead"*.

The reason is the rule's scope. It followed a review of proposals 19-29 by
five independent reviewers, which found the build work broadly sound — the
80% cut maths, C-06's byte-identical additive rendering, the worklog
double-counting and mis-pricing fixes, warmup's recursion fix, and
`rules_pull`'s three conditions all held up under verification — while nine
items had been closed with the measurement or proof half of their own
`done` criteria never performed. Those were judgment calls made at the
moment of closing an item, which is lead work, not defects in what the
subagents built.

This does not touch the older ruling above it in `HANDOFF.md`, that no
subagent a lead dispatches uses Opus (proposal 21, A-12). The two now read
as one rule with two halves: subagents stay Haiku and Sonnet by tier; the
lead or dispatcher session that plans, merges, reconciles and closes runs
on Opus. Where a session cannot run Opus, it says so rather than silently
closing items on a lower model.

## 2026-09-15 · The dispatcher starts the next item lead itself, no click needed (P28 R-04)

`templates/lead-prompt.md`'s Dispatcher form now says explicitly what
happens the moment an item lead passes its own closing check
(`bin/handover --check`, proposal 24 H-01): the dispatcher starts the next
unblocked item lead itself, `claude --bg -p "<substituted lead prompt>"
--worktree <name> --name "bg · <project> · lead · P<nn> <item ids>"` (the
mechanism proposal 24's H-03 research recommended, and the naming
`bin/handover --check`'s H-04 check already enforces), whose first message
is `/warmup <item id> [context]`. The session id is recorded in the ledger
against the bundle it started, the same place every other running agent is
recorded. Not a restructure — the Dispatcher/Item-lead form headings and
the bullets other bundles already added are untouched; this adds one
bullet.

Not a Standard change: this describes the dispatcher's own behaviour, not
something a project must declare or implement.

## 2026-09-15 · One gate per bundle, not per item: `ruflo-item done` takes several ids (P26 C-03)

**Standard change (mandatory):** `bin/ruflo-item done` now takes one or more
item ids followed by one shared summary —
`ruflo-item done ID1 ID2 ID3 "<summary>"` — and runs the project's merge
gate exactly once for the whole call, not once per id. `hooks post-task`
and the `item:<ID>:done` memory store still run once per id (each item
still needs its own done record), and `hooks worker dispatch --trigger
testgaps` now runs once per call rather than once per id. A single-id call
still works exactly as it did before this change. Every project that calls
`ruflo-item done` from more than one item in a bundle should now make one
call naming every id, not one call per id — the old one-call-per-id
pattern still works item by item but re-runs the gate once per item, which
is exactly what this change and `templates/brief.md`'s "one gate run" per
bundle exist to stop paying for.

`templates/lead-prompt.md` §2 and `templates/brief.md` now say explicitly
that a bundle or batch gets one full suite and at most one review, and that
a `restricted` item is never bundled — it goes alone, on its own branch,
with its own reviewer and its own gate run (the same rule
`tools/tracker/lanes.py`'s `ALONE` threshold already enforces for risk 9
and over, proposal 26 C-02).

## 2026-09-15 · The six-category review list is gone: `tracker route` decides now (P23 M-08)

CLAUDE-workflow.md's "Ceremony is opt-in" section and `templates/lead-prompt.md`
§3 used to carry the same fixed list twice — "money or financial data; real
user data stores; authentication, credentials or secrets; release, install
or packaging; cross-cutting changes to shared modules; and any change to
common-rules itself" — deciding by hand what proposal 25's Z-02 and proposal
26's C-02 (`tracker route`, `tracker lanes`) now decide from each project's
own `.common-rules.json` (`risk_paths`, `risk_always`) plus `value` and
`points`. Both files now name `tracker route` as the one place that
decision is made, instead of duplicating the list beside it. Nothing about
what actually gets reviewed changes for a project already declaring
`risk_paths`/`risk_always` — the mechanism was already live from proposal
26's C-02; this closes the gap between what the tool decides and what the
prose still told a reader by hand.

Not a Standard change: no project's `.common-rules.json` needs to change —
`tracker route` already reads what proposal 26 required projects to
declare, and a project that has not declared `risk_paths` still gets
`standard` risk for everything but `risk_always`, exactly as before this
bundle.
## 2026-09-15 · The Stop hook's worklog collect, and its separate nightly commit (P27 W-03)

`hooks/stop` now also runs `tools.worklog.collect()` on every turn --
best-effort telemetry, not a gate: any exception (including
`worklog.StateTrustError`) is caught inside `_collect_worklog` itself, and
the call never blocks the hook past `WORKLOG_COLLECT_TIMEOUT` seconds
(default 5) -- it runs in a daemon thread the hook does not wait out past
that budget, since `collect` scans every transcript on the machine and a
first pass (or heavy concurrent activity) can run long; an abandoned run's
un-persisted offset can cause a later run to re-add the same bytes once,
a self-correcting over-count, never a hang or corruption. **A session never
commits `worklog/` itself** -- that is the new, separate `bin/worklog-nightly`
script's job: a fuller collect, then at most one commit of `worklog/` per
calendar day however many times it runs that day (`worklog/.nightly-state.json`
records the last date committed). Not wired into any system cron or
launchd on this machine -- that scheduling is an operational step for
whoever administers the host, left undone here on purpose.

## 2026-09-15 · Point-class cost calibration (P25 Z-05)

`bin/spend calibrate`: after every 20 closed (done) ledger items across
every ledger under a project, groups their measured cost (from
`tools/worklog.py`'s transcript-derived totals, keyed by item id) by the
item's `points` class (proposal 25's Z-01 field) and flags any item costing
over 2x its class's median -- `tools/calibrate.py`, with
`worklog/.calibration-state.json` tracking the closed-item count as of the
last calibration (same atomic-write shape as `worklog/.state.json`) and
`worklog/calibration-log.jsonl` recording one line per run, naming every
item flagged. Deliberately does not auto-stage a change into a flagged
item's own ledger: this can run unattended, on ledgers several other
bundles own at once, and the ledger stays single-writer (proposal 23,
M-04) -- a lead who acts on a flagged item stages that decision itself,
quoting the log.

## 2026-09-15 · The rules-file cluster: dedupe, a merged mandatory read, the light path named, and published titles never move (P23 M-05, M-06, M-07, M-09, M-11; P22 T-06)

A rules-conflict review this session ran across HANDOFF.md,
docs/OPERATING-RULES.md, CLAUDE-workflow.md, skills/warmup/SKILL.md and
templates/lead-prompt.md found seven items touching the same small set of
files; landed together as one bundle to avoid merge conflicts on the same
paragraphs. M-10 (CLAUDE-workflow.md's dated rationale) has its own entry
above; this one covers the rest.

**M-09 — five rules, one canonical home each.** `ruflo-mandatory` lives only
in `skills/warmup/SKILL.md`; `the-ledger-has-one-writer`,
`checkpoint-before-stopping` and `every-sponsor-message-gets-an-ask-row` now
live only in `HANDOFF.md` (folded there by M-11, below); `reserved-to-the-
sponsor` lives only in `HANDOFF.md`'s new "Reserved to the sponsor, always"
section. Every other file that used to restate one of these in full now
carries a one-line pointer naming where it actually lives. No rule's content
was cut, only its duplicates.

**M-11 — the mandatory read, restructured.** `docs/OPERATING-RULES.md`'s
content folded into `HANDOFF.md` under "Operating rules, learned the hard
way"; the standalone file still exists, nearly empty, only because
`.common-rules.json`'s `read_order` and `CLAUDE.md` (both reserved to the
sponsor) still name its path — it now just points to `HANDOFF.md`. Every
read-order line in `HANDOFF.md`, `skills/warmup/SKILL.md` and
`templates/lead-prompt.md` that used to say "the ledger(s)" now says the
warmup card instead — the card is the compressed form (~1,061 words against
~37,672 for the raw JSON across 11 proposals, measured 2026-09-15); a
ledger's full JSON is opened only for the item currently being worked.
Target was 3,000 words for the fresh-lead mandatory read
(CLAUDE.md + HANDOFF.md + card + checkpoint + CLAUDE-workflow.md); measured
after this bundle and M-10 together, the static four files alone are still
several thousand words over that, dominated by CLAUDE-workflow.md, which
carries process rules for every project on the standard, not just
common-rules. The sponsor's own ruling settles the tradeoff: *"the priority
is on the word limit that we do not miss anything important"* — nothing was
cut to force the number down; the checkpoint, both prohibitions and every
rule this bundle touched are still in the mandatory read, and the real count
is reported here rather than hidden by further trimming.

**M-06 — `templates/lead-prompt.md` §4 names its tool.** §4 ("Keep the
ledger current") now says the lead uses `tracker set` for status/field
changes and `tracker ask` for ask rows, and never hand-edits the ledger JSON
— matching what `templates/brief.md` already states for a builder (which
instead uses `tracker stage`, since it does not hold the pen — proposal 23,
M-04). The two sections another bundle added after §9 (`## Dispatcher form`,
`## Item-lead form`) are untouched.

**M-07 — the quick/merge gate split is a named exception.** CLAUDE-workflow.md's
"one command, everywhere" rule now carries one sentence: a project's own
declared `gates.quick`/`gates.merge` split in its `.common-rules.json`
(proposal 23, L-03) is the one sanctioned second command, run through
`bin/quiet -- {{TEST_COMMAND}}` — never a command invented ad hoc inside a
task.

**M-05 — the light path is a real, named thing.** CLAUDE-workflow.md's
"Ceremony is opt-in" section now names it: an item small enough (points 1,
risk `standard`) skips the scout, the separate reviewer, and the per-item
ledger ceremony — one commit, one gate run, one log line. Routing (proposal
25, Z-02) decides eligibility; `templates/brief.md` carries the short form.
Proposal 26's C-05 findings-triage work can now cite "the light path" as a
real, defined thing. **Common-rules' own items are never light** — every
change here is already `restricted` under the risky-work list, so this only
applies to the projects that follow the standard, not to this repository.

**T-06 — a published page's `<title>` is set once, never changed.**
CLAUDE-workflow.md's "Talking to the user" section states it once, covering
every maintained page (the tracker/board, a per-proposal tracker page, the
cookbook, or any future one) — not a differing `title` parameter on a later
publish, not by hand, not a regenerating rebuild that emits the tag
differently. `skills/warmup/SKILL.md` §3 points back to this statement
rather than restating it. Nothing was actually broken by this — the Artifact
tool's own rule already makes a page's own `<title>` win over a publish-call
`title` parameter — but the sponsor's ruling makes it explicit and
mandatory: *"don't change the name of the tracker again and again that
should also be a mandatory rule"*, later broadened to *"make it a mandatory
rule not to rename the artifacts like cookbook and a trackers again and
again."*

**Standard change (mandatory):** every project on the standard — when
publishing or republishing any maintained page (a tracker, a board, a
cookbook, or any future one) — never changes that page's `<title>` after its
first publish, for any reason (T-06). The light path (M-05) is available to
any project on the standard for points-1/risk-standard items; using it is
not required, but the definition above is now the one a project should point
to rather than inventing its own.

## 2026-09-15 · CLAUDE-workflow.md's Autopilot and Talking-to-the-user sections trimmed of dated rationale (P23 M-10)

Proposal 23, M-10. The two sections carried roughly 230 lines of dated,
proposal-specific rationale — grandfather clauses, sample register and
milestone rows, and citations to one-off measurements — sitting beside the
actual rules a session needs to follow. Table shapes and the rules
themselves are unchanged; the worked examples and the measurement history
that justified each date move here, one line plus a pointer left in
`CLAUDE-workflow.md`.

**Feature register, worked example** (`## Features` table): what used to sit
in the file as sample rows —

| # | Feature | State |
|---|---|---|
| [#2](…/issues/2) | Capture a document and see it filed | **in flight** — issue #1 |
| [#3](…/issues/3) | Import the backlog | blocked by #2 |
| [#8](…/issues/8) | Get it onto the second phone | version 2 |

**Naming history:** `completed` is the word for fully finished, written from
here on; `done` is a grandfathered synonym of it, not mass-renamed where
already written; `built` keeps its own narrower meaning — shipped but not
yet closed — and is never folded into `completed` (same convention as
proposal-status's own `built` → `completed`, decided 2026-08-20).

**Milestone plan, worked example** (`## Milestones` table):

| # | Milestone | Proves | You get | State |
|---|---|---|---|---|
| 1 | One corpus indexed, answering a question | retrieval is good enough to build on | nothing to hold | completed |
| 2 | The model timed on the real phone | the felt speed, and so the retrieval budget | nothing to hold | in flight |
| 3 | The first real screen, on the device | the design survives contact with a hand | **an app you can use, one corpus** | next |

**Measured on `pocket-internet`, 2026-08-20:** the first milestone was five
cheap verifications named in advance. Three ran — two confirmed an estimate
and one corrected a verdict that had already propagated into two proposals.
Twenty minutes, and it changed a conclusion that eleven passes of reading
had not.

**Why the proposal-decisions rule exists, measured in finance-tracker
(issue #584), 2026-08-19:** 11 proposals `accepted`, 9 carrying a decision
date (`<meta name="proposal-decided">`), only 3 recording what was actually
decided — and those three were hand-written the day the gap was noticed. A
date says *when*; it says nothing about *what*, and `proposal-auditor` has
nothing to measure a build against without the answers.

**The 2026-08-19 grandfather's measurement:** undated reads the same as
"decided before this rule existed," not a loophole to leave the meta off
going forward — finance-tracker alone has 8 accepted proposals whose
answers are unrecoverable; inventing them would misstate history worse than
the gap does, and a test that fails on day one against documents nobody can
fix gets disabled. `bin/proposalcheck` reported 0 blocked proposals across
finance-tracker, mac-explorer, pockets and pip at the time; finance-tracker
had 4 that would have failed without the floor (proposals 20, 23, 24, 25),
all dated before it, so enforcement is forward-only from there.

**Why the lead-vs-section rule was made explicit, 2026-08-20:** six
parallel spending-UI concepts from one design-explorer run (finance-tracker)
had nowhere to go but loose, unnumbered `claude.ai` links until this was
written down — `NN-<type>-<slug>.html` already had a real answer (make each
its own numbered section of one lead proposal).

**The 2026-08-20 floor's grandfathering, at the time it was written:**
`bin/proposalcheck` reported 0 blocked: pockets carried one lead with a
typo'd status (`superseded-by 14` for `superseded by 14`, decided
2026-08-04) and pip carried two undated leads with no status at all — both
grandfathered the identical way an undated or pre-floor proposal already is
above, not specially cased.

**The bake-off measurement behind "ask before code, in one batch":** the arm
that batched and defaulted logged six open questions, received no answers,
and still finished; the control arm asked two and silently resolved nine,
which it happened to get right.
## 2026-09-15 · Findings are ledger rows too: `tracker findings` (P26 C-05)

Proposal 26, C-05. A review's or a test's finding -- from quality-manager,
any reviewer, test-engineer's bug reports, or a failing/red-first test not
yet fixed -- is now a row in a ledger's own top-level `findings` array, not
only prose in a report: id (`F-NN`, distinct in shape from an item's
`PHASE-NN`), `source` (`review`|`test`), `file`[`:line`], `severity`, and
`state` (`catalogued`|`decided`|`deferred`|`declined`). It shares proposal
25/26's value, points, risk, cluster, impact and likelihood fields with
items, checked the same way, all optional -- a ledger with no `findings`
validates exactly as before.

`bin/tracker findings add|decide|defer|decline LEDGER ...` catalogues a
finding and moves it through its lifecycle, writing straight to the ledger
like `tracker set`/`tracker ask` already do (an item lead still stages
ledger changes through `tracker stage` per proposal 23's M-04 -- this is
the write primitive for a new kind of row, the same way `set`/`ask` are for
items and asks).

`bin/tracker findings lanes LEDGER...` shapes every finding like an item
row and hands the combined queue to `tools/tracker/lanes.py`'s `lanes()`
unchanged, so items and findings sort into the one share/risk/80%-cut
queue -- a catalogued finding gets a lane and stays visible, unworked,
until the sponsor decides it. `bin/tracker findings triage LEDGER --batch
ID...` groups a batch of decided-small findings by their shared `cause`
before it is worked, one line per group; a duplicate is `declined` with
`duplicate_of` naming the survivor and dropped from the count. A decided
finding is light-path eligible (proposal 23 M-05, built in a parallel
bundle) when it is not alone (restricted, or risk 9+) and 1-3 points --
`light_eligible()`, reusing the one shared `lanes()` run.

## 2026-09-15 · `bin/handover --check`: the closing check before a lead's turn ends (P24 H-01, H-02, H-03)

Proposal 24, H-01 to H-03. A new `bin/handover --check --project DIR` runs four
checks a lead should pass before it stops, and exits non-zero naming what is
missing rather than 0 on a silent gap: every sponsor message since the
session (or `--since`) has an `A-nn` ask row; every worktree ahead of
`origin/main` for the project is named in some ledger log, found from the
main checkout's `.claude/worktrees/`/`.worktrees/`, not only from inside the
worktree itself; the latest `docs/handovers/*-checkpoint.md` digest matches
the open ledgers; `bin/warmup --project DIR --check` reads ready. `--transcript`
matches sponsor messages to asks one-to-one -- first by a normalised quote
match, then by nearest unused ask within ten minutes -- so one covered ask
can no longer make an unrelated message look answered.

`templates/lead-prompt.md` gains two new sections after its existing nine,
`## Dispatcher form` (holds only ledgers, asks and routing; never reads
diffs, logs or images; kept under roughly 150k tokens of context) and
`## Item-lead form` (builds one bundle, merges, closes on `bin/handover
--check`) -- proposal 24's autonomy split between a cheap, long-lived
dispatcher and short, disposable item leads. `docs/OPERATING-RULES.md` names
`bin/handover --check` as the closing check.

H-03 is research only: `docs/research/starting-item-leads.md` compares the
mechanisms a dispatcher could use to start an item lead with no sponsor
click (`claude --bg -p`, the desktop session-management tools, a scheduled
task) and recommends `claude --bg -p`. No session was started to write it;
the proof run -- one item lead started and finished with no sponsor action,
recorded by session id -- is still open.

**Standard change (mandatory):** every project adds `bin/handover --check`
as its closing check, the same way `bin/warmup --check` already is one.

## 2026-09-15 · Sizing, risk and routing on the ledger: `tracker route` and `tracker lanes` (P25 Z-01–Z-04, P26 C-01, C-02)

Proposals 25 and 26, decided. Ledger items may now carry `value`
(high|medium|low), `points` (Fibonacci, 1 to 13), `risk`
(standard|elevated|restricted), `cluster`, `impact` (1 to 4) and
`likelihood` (1 to 3) -- every field optional, so every ledger that
declares none of them, including the PhotoVault engine's, still validates
unchanged.

`.common-rules.json` gains `value_defaults` (a value per surface, an item's
own value always wins), `risk_paths` (glob lists that classify a changed
path as restricted or elevated) and `risk_always` (a floor no path can
lower -- common-rules declares `restricted`, per proposal 25's D4).

`bin/tracker route LEDGER ITEM` prints how one item is reviewed and bundled:
restricted is never bundled and goes to a separate reviewer the sponsor
sees; elevated, or high value with five or more points, gets a separate
reviewer on its own branch; everything else is gate-and-tests only, with
one to three points bundling by cluster. Points are never put in a
builder's brief (proposal 25, D3) -- `templates/brief.md` says so.

`bin/tracker lanes LEDGER...` sorts the open queue by share (value weight
times points, over the queue's total) and cuts at 80% cumulative -- the
item that crosses the line is included in `Now` -- with the tail lane set
by risk (impact times likelihood, forced to at least 9 for anything
restricted): `Daily` at 6 or more, `Weekly` at 3 to 5, `When touched` at 1
to 2. Risk 9 and over never bundles, in whichever lane it lands. An item
missing value or points is listed as unsized, never guessed a share.

Not a Standard change: no ledger is required to declare these fields, and
nothing existing changes behaviour until a project chooses to use them.

## 2026-09-15 · `bin/worklog collect` and `bin/worklog day`: a central token/time record (P27 W-02, W-04)

Proposal 27, decided 15 September 2026 (D1-D6): a folder revisioned under
common-rules, one JSON-lines file per day, updated incrementally, task named
from the brief tag then the branch then the session, active time with gaps
over five minutes left out.

`bin/worklog collect [--projects DIR] [--out DIR] [--state FILE]` reads every
transcript's new lines since its last run — lead and subagent alike — and
merges input, cache-read, cache-write and output tokens, list-price cost and
active time into `worklog/<YYYY-MM-DD>.jsonl`, one line per (day, project,
session, agent, model, item). It is incremental by byte offset per
transcript and, within a transcript, by `message.id`: a message that grows
across two collector runs (still streaming when `collect` last ran)
contributes only the delta the second time, so a re-run never double-counts
and a day file rewrites byte-identical when nothing changed. Nothing it
writes ever carries transcript prose — every field is drawn from a fixed
whitelist, and the only text ever inspected (the first user prompt, to look
for a leading item tag) is discarded with the record it came from.

`bin/worklog day [--date D] [--html FILE]` renders that day as a
self-contained HTML page (tasks, sessions, projects, lead vs. agent split,
the four token kinds, cost, active time) and a plain-text summary on
stdout; every value it writes is `html.escape`d, since a git branch name or
a brief tag reaching that markup is as untrusted as any other input.
`bin/worklog yesterday-line` prints a one-line summary for a future
`/warmup` card to shell out to (that wiring, and the nightly/Stop-hook
collection cadence, are W-03/the card change — not built here).

`tools/worklog.py` holds the shared primitives (`list_transcripts`,
`dedupe_messages`, now also `collect`, `derive_item_id`, `render_day_html`)
so `bin/spend` and `bin/worklog` read the same transcript shape once.
`tests/test_worklog.py` covers task naming, active-time gaps, idempotent
re-run after a transcript grows, and that no output ever carries transcript
text.

**Behaviour change:** none for existing tools — this adds `bin/worklog` and
`worklog/` (gitignored state file only) without touching `bin/spend`'s own
behaviour further. A project adopting the daily collection needs to run
`bin/worklog collect` itself for now; automatic scheduling is W-03.

## 2026-09-15 · W-01: `spend` read subagent transcripts and deduped streamed usage (P27)

`bin/spend` undercounted and overcounted the same session in opposite
directions: `_sessions()` globbed `<project>/*.jsonl` only, so every
subagent transcript at `<project>/<session>/subagents/*.jsonl` was never
read at all, and `_read()` summed `usage.output_tokens` across every record
in a transcript, though a streamed response writes the same `message.id`
several times as usage grows (about 3.6 records per message, measured
2026-08-07) -- so the fraction that *was* read was overstated by roughly
that factor.

`tools/worklog.py` is now the one place that knows the transcript shape
(`list_transcripts`, `iter_records`, `dedupe_messages` -- last record per
`message.id` wins) so `bin/worklog` (W-02/W-04, following) shares it rather
than duplicating. `bin/spend` reads through it. `report` and `today` gained
input, cache-read and cache-write columns alongside the existing output
column; `agentlog` and `log` are unchanged in shape.

**Behaviour change:** `spend report`/`today`/`agentlog` totals now include
subagent transcripts and are deduped by `message.id` — existing figures for
any project will move (down, for the dedupe fix; up, for subagents).
`tests/test_spend.py` adds `TestSubagentsAndDedupe` and updates the
zero-total regression guard for the new columns.
## 2026-09-15 · warmup gains --reheat and --queue; both run the standard (P28 R-01)

Proposal 28, R-01 (decided, option A). Two commands now cover the whole lead
lifecycle: `warmup` for a fresh lead, `warmup --reheat` for one already
running -- `--reheat` is `--since` against a state file warmup keeps for
itself (default: inside the project's own git directory), with the
standard's own status (conformance's twelve items, plus every pending
mandatory Standard change) appended every time, not only when it changed.
Both now run conformance and the mandatory-pending check on every call; with
`--queue`, each item that does not hold becomes a ledger item -- owner
`lead`, status `not started`, first in that ledger's own `items` list
(`tools/tracker/queue.py`, new) -- idempotent, so a second `--queue` adds
nothing for a source already queued.

**Behaviour change:** a plain `warmup` (no flags) now also runs
`bin/conformance`'s twelve checks and rulecheck's mandatory-pending check in
process every time, which is measurably slower than the card alone
(conformance item 12 itself spawns a nested `warmup --check`) -- gather()
computes conformance only for the plain card and `--reheat`, never for
`--check` itself, to avoid that nested call recursing into conformance a
second time. `--queue` writes to the project's first ledger under
`docs/proposals`; a project with several ledgers keeps everything else about
them untouched.

## 2026-09-15 · SessionStart and Stop hooks dispatch to warmup/reheat (P28 R-03)

Proposal 28, R-03 (decided, option A). `hooks/sessionstart` now runs
`bin/warmup` (plain card, no `--queue`: a hook never writes) on `startup`,
and `bin/warmup --reheat` on `compact` or `resume` -- always with
`--no-pull`, keeping this hook's own read-only, no-network contract even
though warmup's plain card and `--reheat` otherwise fast-forward the rules
checkout (R-05). `clear`, or no source at all, keeps the pre-R-03 one-line-
per-ledger summary outright. Every dispatch is bounded by a hard timeout
(`WARMUP_TIMEOUT`, default 8s, overridable only via
`COMMON_RULES_HOOK_TIMEOUT` for tests) and falls back to that same one-line
summary on any failure or timeout -- never to a failed session.
`hooks/stop` now also compares the shared rules checkout's current HEAD
(`git rev-parse`, never a fetch) against the `rules_head` warmup's own state
file recorded, and prints `rules moved -- run /reheat` when they differ; the
same timeout override applies to that check.

Measured end to end (subprocess start to exit): common-rules' own checkout,
startup/resume/compact ~2.0s each; a small fixture project, ~1.6s each;
`hooks/stop`'s rules-moved check, ~0.4s. All well under the 8s default and
the 10s ceiling this item asked for.

**Behaviour change:** a SessionStart hook that used to print one line per
open ledger on `startup` and `resume` now prints warmup's or reheat's full
card/delta instead (more text, more subprocess and git work per session
start) -- bounded by the timeout above, and unchanged for `clear` or a
missing source.

## 2026-09-15 · /standard folds into /warmup; /reheat is new (P28 R-02)

Proposal 28, R-02 (decided, option A). New `skills/reheat/SKILL.md` for a
session already running (`bin/warmup --reheat --queue`); `skills/warmup/
SKILL.md` rewritten for a fresh one, both `--queue`d by default and both
accepting `--context TEXT` for one free-text line the sponsor gave that
would otherwise have nowhere to go. `skills/standard/SKILL.md` is now a
short shortcut pointing at `/warmup` -- `/standard` used to walk a lead
through "queue every pending mandatory Standard change by hand"; `warmup
--queue` (R-01) now does that on every run, so there is nothing left for
`/standard` to do. It says it will be removed next release.
`bin/derecord` installs both `/warmup` and `/reheat` alongside each other
(previously only `/warmup`).

**Behaviour change:** a project already on the standard gets a second
installed skill (`.claude/skills/reheat/SKILL.md`) the next time `derecord`
runs, and `/standard`, if a session still types it, now only points at
`/warmup` instead of walking the old twelve-item checklist inline.

## 2026-09-15 · warmup fast-forwards the shared rules checkout when it is safe (P28 R-05)

Proposal 28, R-05 (decided, option A). `bin/warmup`'s plain card now checks the
shared rules checkout (wherever `bin/warmup` itself lives) and fast-forwards it
with `git pull --ff-only` when it is on `main`, has no tracked changes, and
`origin/main` is strictly ahead after a short `git fetch` -- never merge,
rebase, stash or reset. Anything else (dirty, diverged, not on main, no
`origin`, a fetch that times out or fails) is left alone and named on one card
line instead. `--no-pull` skips the check entirely; `--check`, `--json`,
`--since` and `--migrate` never trigger it, since those are queries, not the
moment to move a checkout under whoever is reading it. New `tools/rules_pull.py`
carries the pure check, testable against temp clones without ever touching a
real checkout's git state.

**Behaviour change:** a plain `warmup` (no flags) can now write to the rules
checkout's ref (a fast-forward only) and reach the network (one `git fetch`,
short timeout). Anything invoking `bin/warmup` from a context where a network
call or a moving HEAD is unwanted -- CI, a read-only hook -- must pass
`--no-pull`.

## 2026-09-15 · One tracker per project, written where sessions read it (P22 T-04)

The sponsor, 15 September 2026: "Please maintain a single tracker for common
rules. And also add that as a common rule to maintain a single tracker up until
I have asked to create another tracker. Per project." Proposal 22's T-02 and T-03
built it; this states it in `CLAUDE-workflow.md`, `skills/standard`,
`skills/warmup` and `templates/lead-prompt.md`: one tracker per project,
`docs/proposals/tracker/index.html` published at one stable URL, and another
tracker only when the sponsor asks for one, recorded with the ledger's `tracker`
key. `tests/test_one_tracker_rule.py` pins the wording in all four files.

**Behaviour change:** no new one. The T-02/T-03 entry below already carries the
Standard change line for what projects must do.

## 2026-09-15 · One tracker per project: the chain and publishing move onto it (P22 T-02, T-03)

The sponsor, 15 September 2026: "Please maintain a single tracker for common
rules. And also add that as a common rule to maintain a single tracker up until
I have asked to create another tracker. Per project." Proposal 22's T-01 built
the one page; this lands T-02 and T-03, built by the Common Rules chat v1
session and taken over under proposal 29 (K-01).

What changed:
- **The chain reads the project page (T-02).** derecord's pre-commit hook
  renders `docs/proposals/tracker/index.html` whenever a ledger is staged. A
  per-proposal page is rendered only for a ledger that declares a tracker of its
  own (the new `tracker` key: `own`, `by`, `at`, `quote`, for a proposal the
  sponsor asked to track separately). The warm card, conformance item 2 and
  `new-proposal` follow the same rule.
- **Publishing records the project page (T-03).** `tracker published --project
  [DIR] --url URL` records `docs/proposals/tracker/index.published.json`; the
  card's "page changed since last publish" line and conformance item 10 read it.
  `tracker published LEDGER.json` now refuses a ledger with no tracker of its
  own. A project that declares `plan_page` keeps publishing that page.

Not yet: the rule's wording in `CLAUDE-workflow.md`, the skills and the lead
prompt (T-04, proposal 29 K-02), and PhotoVault's move (T-05, K-03).

**Behaviour change:** yes, for every project on the standard: which page the
pre-commit hook renders, what the card and conformance call stale, and which
page is published and recorded.

**Standard change (mandatory):** each project re-runs `bin/derecord` so its
pre-commit hook renders the one project page, renders it with `bin/tracker
board --project .` and commits it, publishes that one page to a single stable
URL and records it with `bin/tracker published --project . --url <url>`, and
stops publishing per-proposal tracker pages unless the sponsor asked for one
(recorded as the ledger's `tracker` key). Then `rulecheck --align`.

## 2026-09-15 · Token budget: the eight levers in the standard (P23 L-01 to L-07)

The sponsor directed: "Implement the eight levers of uh, token spending. to
optimize token utilization. In the standards". Proposal 23 recorded his picks
after a transcript measurement of three sessions: leads carried about 500k
tokens into every call (56–67% of lead spend above 500k), cache re-reads were
68–79% of lead spend, and items needing more than one agent carried 79–98% of
subagent spend.

What changed:
- **Fresh leads (L-01).** A lead ends at a milestone, at the end of a day, or
  past about 150k tokens of context, and hands over through the ledger,
  `tracker checkpoint` and `/warmup`. Lead prompt section 9.
- **Review only risky work (L-02).** A separate reviewer runs for money, real
  user data, auth and secrets, release and packaging, cross-cutting changes,
  and every change to common-rules. Everything else: build, gate, land. The
  gate in "the four things that actually work", the roles table and lead
  prompt section 3 now say the same.
- **Quiet gates (L-03).** New `bin/quiet -- CMD`: full output to a log file,
  one verdict line, the command's exit code.
- **One-line ledger updates (L-04).** New `tracker set` and `tracker ask`:
  validate, write, re-render, print one line.
- **Bundles by surface (L-05).** Small issues on one surface go to one agent,
  one commit per issue, one gate, one PR.
- **Scout (L-06).** New `templates/scout-brief.md`: a read-only Haiku scout
  writes the CONTEXT pack before a builder starts.
- **Existing tools, not inline copies (L-07).** Briefs name the Read tool,
  `bin/quiet`, `tracker set` and `tracker ask` in place of `cat`/`sed -n`, raw
  runners and hand-edited ledger JSON.

Kept as they are, by the sponsor's pick: the lead reads receipt images itself
(L7), and model routing (L8, pending proposal 25).

**Behaviour change:** yes, for every session on the standard: when a lead
stops, who reviews, how gates and ledger updates are run, and what a brief
carries.

**Standard change (mandatory):** each project regenerates section 9 "Token
budget" of its lead prompt from `templates/lead-prompt.md`, briefs its agents
from the new `templates/brief.md` (and `templates/scout-brief.md` for scouts),
runs its gates through `bin/quiet`, records ledger changes with `tracker set`
and sponsor messages with `tracker ask`, and applies the risky-work review list
from `CLAUDE-workflow.md`. Then `rulecheck --align`.

## 2026-09-15 · Proposals 23, 24 and 25 accepted: token spend, autonomy, sizing

The sponsor asked why building simple features costs so many tokens: "analyze
where the tokens are getting spent and why it's getting so expensive to build
simple features. I would like to optimize things." A measurement of the
PhotoVault App, PhotoVault Engine and Common Rules chat v1 transcripts found
most spend is leads re-reading a context of about 500k tokens on every call,
and most subagent spend is on items that needed more than one agent.

He decided on two pages, and the answers are recorded in three proposals:
- **23 · Eight levers for token spend.** Fresh leads per milestone or day,
  review only risky work, quiet builds, one-line tracker commands, bundling
  small issues by surface, a Haiku scout for context. Screenshots and models
  kept as they are. Items L-01 to L-07.
- **24 · Autonomous work without missing anything.** A thin dispatcher that
  never ends, short item leads, a four-point closing check before any lead
  stops, the dispatcher starts the next lead, and today's stop list unchanged.
  Items H-01 to H-03.
- **25 · Sizing items by value, points and risk.** Value set per surface by the
  sponsor, points kept from builders, a risk class from paths with every
  common-rules change restricted, calibration every 20 items, and a catalogue
  of issues clustered by files touched. Items Z-01 to Z-06.

An independent re-check confirmed the context and cache-read figures and found
PhotoVault proposal 79's token totals count each streamed response about 3.6
times.

**Behaviour change:** none yet. These are decisions and ledger items only; each
item that changes what projects must do will carry its own Standard change
line when it lands.

## 2026-09-14 · `tracker board`: one tracker page per project (P22 T-01)

The sponsor asked: "Can we make the tracker a little bit visually readable
with some filters or something like that? Like, a top level, uh, you know,
where it filters everything, and I can see things in block, maybe visually
appealing a little bit? Also, per project, there should be one tracker unless
and until specified for a proposal if I need another tracker."

`bin/tracker board [--project DIR] [--check]` renders every ledger in
`docs/proposals` into one page, `docs/proposals/tracker/index.html`:
- the project's totals, and one block per proposal (click one to filter the
  page to it);
- a filter bar that stays in view: search, status, owner, tier, and Board or
  List;
- open asks and requests, then the board, one column per status, with each
  item's full log a click away; the list; and the answered asks.

The page is deterministic and carries each ledger's digest; `--check` is
stale when any ledger changes, is added or is removed. The filters run in the
page's own script, with no external script.

**Behaviour change:** none yet. The per-proposal pages, derecord's hook, the
card, conformance and publishing are unchanged until T-02 and T-03; proposal
22 moves them onto this page, and that entry carries the Standard change line.

## 2026-09-14 · common-rules is on its own standard (P21 S-10)

The sponsor asked for common-rules itself to follow the standard: "Common rules
also works with the same workflow. So I would like you to maintain the same
processes what we are implementing in other projects." The same steps a
project runs under `/standard` were run on this repository:
- derecord installed the pre-commit hook (the old conflict guard is kept as
  `pre-commit.local` and chained), the checkpoint and Agent hooks, the Ruflo
  ignore lines and `/warmup`. `.gitattributes` now matches the shared rules.
- `.common-rules.json` declares the read order (CLAUDE.md, HANDOFF.md,
  docs/OPERATING-RULES.md), the safety rules (HANDOFF.md, Prohibitions) and
  both gates.
- `HANDOFF.md`, `docs/OPERATING-RULES.md` and `docs/handovers/lead-prompt.md`
  are written for common-rules. The operating rules record what this session
  learned the hard way on 14 Sep.
- Proposal 21 has its page, from `bin/new-proposal --page-for`, accepted with
  its four decisions.

`bin/conformance --project .` now reads 11 of 12. The remaining item is the
CLAUDE.md warm-up pointer, which waits for the sponsor, because CLAUDE.md is
his.

Seeding this repository exposed two template defects, fixed here:
- **templates/lead-prompt.md** closed with "take the first C3 item yourself",
  which contradicts its own section 3 (C3 runs in parallel; the lead merges,
  reconciles and decides).
- **templates/OPERATING-RULES.md** still carried the rule proposal 19
  replaced, "One plan, updated in place", so every seeded project had it
  superseded on the spot by migrate.

**Behaviour change:** a project seeded from now on gets the current plan rule
and the corrected lead prompt closing. Already-seeded projects keep their own
files; `/standard` item 5 regenerates the lead prompt when they refactor.

## 2026-09-14 · `bin/conformance`: the 12 items, measured (P21 S-04)

Sessions report "standard: N of 12 hold". The number now comes from a tool
rather than from the session saying so.

`bin/conformance --project DIR [--json]` prints one line per item of
`/standard`'s checklist: ✓ holds, ✗ does not hold (with why and the fix), or
… waiting on common-rules. It exits 0 when no item fails, 1 when one does, and
2 when it cannot run. It is read-only; a byte-and-mtime snapshot test holds it
to that.

The rules each item checks:
- **Rules:** the stamp is committed and no mandatory Standard change is pending.
  A stamp truly ahead of the rules holds; one that cannot be resolved fails.
- **Migrated:** every ledger is valid and its page matches.
- **Declared:** read order, safety rules and both gates.
- **Installed:** derecord's exact pre-commit hook, the hooks resolving into
  common-rules, the Ruflo ignore lines decided by `git check-ignore`, and no
  tracked runtime files.
- **Lead prompt:** it carries the template marker.
- **Common language:** valid owners on blocked rows and open asks, tags
  agreeing with each row's tier and model, one routing table, and valid
  requests.
- **Proposals:** `proposalcheck` is clean.
- **No hand-kept ledger twins.**
- **Ruflo:** a real memory database, or ruflo-item, post-task or memory-store
  evidence.
- **Publish records:** well-formed.
- **CLAUDE.md pointer:** committed, not symlinked, and matching the declared
  order.
- **Card:** `warmup --check` is ready.

Items 5, 6, 8 and 9 are proxies, and the docstring says so.

Two review rounds closed seven ways a project could fake a pass. The lead fixed
the final round's one finding: a committed CRLF stamp read "not committed".

**Where the projects stand today:** PhotoVault app 5 of 12, engine 4 of 12,
common-rules 7 of 12. Each fixes the rest when it refactors under `/standard`.

## 2026-09-14 · The templates and the workflow say the standard is mandatory (P21 S-06)

Every session reads its project's lead prompt and this repository's
`CLAUDE-workflow.md`. Neither said the standard is mandatory, how proposals are
made, or how sessions ask each other for things. Now:
- **`CLAUDE-workflow.md`** opens with "The warm-up standard is mandatory": run
  `/warmup` at every start and after compaction; the sponsor's `/standard`
  adopts the standard; `bin/conformance` will measure the 12 items once it lands;
  implement `**Standard change (mandatory):**` entries before aligning; proposals
  come from `bin/new-proposal`; cross-session asks are `requests`; blocked rows
  carry owners.
- **`templates/lead-prompt.md`** carries the marker
  `<!-- common-rules:lead-prompt proposal/21 -->` (bin/conformance reads it) and
  a section 8, "Proposals, requests and owners". Owners are written in the forms
  the ledger accepts: `sponsor`, `lead` or `session:<name>`.
- **`README.md`**: adoption now starts with the sponsor running `/standard`.
- **`docs/workflow.html` and its PNG** are regenerated, stamp 397.

Two review rounds. The lead fixed the final one's finding (0d99f87): round 2
had stamped the page 385 in the same commit that edited the rules file again,
and its report said the suite passed when the stamp test failed.

**Behaviour change:** a lead prompt regenerated from the template now carries
the marker. Projects already on the standard pick it up when they refactor
under `/standard` (checklist item 5); derecord never overwrites an existing
prompt.

## 2026-09-14 · An unimplemented Standard change fails the card (P21 S-09)

The sponsor ruled that every later improvement to the standard is mandatory
(proposal 21, A-03). An entry here that carries a column-0
`**Standard change (mandatory):**` line must be implemented before a project's
`.common-rules-version` stamp moves. Until now, "behind" was only information.

`rulecheck --project DIR --mandatory` lists the entries whose requirement
paragraph changed since the stamp.
- Exit codes: 0 means nothing to do, 1 means pending, 2 means the rules
  repository or its CHANGELOG cannot be read.
- Adding, rewording or deleting any line of the requirement paragraph counts.
  An unchanged entry that only moved does not.
- Markers inside closed code fences are ignored. A fence never spans a dated
  entry heading, so an unclosed fence cannot hide a requirement.
- A stamp that cannot be resolved (bad form, or a commit the rules do not have)
  counts every mandatory entry.
- A stamp on a diverged commit (a side branch, or history rewritten) is compared
  tree to tree.
- Only a stamp truly ahead of the rules checkout reads "ahead". Plain
  `rulecheck` exits 0 for that stamp.
- A stamp's sha reaches git only when it is hex. This closes an injection where
  a crafted stamp made `git diff` write a file.

`warmup`'s card shows "rules behind · N mandatory Standard change(s) to
implement first", naming each. `--check` fails while any is pending. Entries
without the line stay informational and never fail.

Two review rounds, then the lead fixed the final round's findings (7746c80): a
diverged stamp misread as ahead, an unclosed fence, `--check` naming the
entries, and deleted requirement lines.

**Behaviour change:** every project with a `.common-rules-version` stamp fails
`warmup --check` from now on until it implements the mandatory entries since its
stamp and runs `rulecheck --align`. The PhotoVault app does today, for "Later
changes to the standard are mandatory too" and the proposal 21 entries. That is
the sponsor's ruling doing its job.

## 2026-09-14 · Sessions that start above their projects get the card (P21 S-05)

The PhotoVault app and engine sessions start in `PhotoVault/`, the folder above
`app/` and `engine/`. It is not a git repository, and Claude Code loads
`.claude/settings.json` hooks from the folder a session starts in. So the hooks
derecord installed inside each project never ran, and neither session got a
card at start or after a compaction.

When the start folder has no ledger of its own, `hooks/sessionstart` now:
- lists the child projects one level below, up to 10 sorted by name, each with
  its counts and `/warmup --project <path>`, then "+N more";
- skips unreadable children;
- uses the compaction wording after a compact;
- stays read-only and fast (0.06 s with 200 children).

A start folder that has its own ledger behaves exactly as before.

`bin/derecord --parent DIR` installs only that SessionStart hook into
`DIR/.claude/settings.json`. It refuses when `DIR` is a git repository, has no
child projects, or has malformed settings. It is idempotent and prints how many
child projects it found.

**Behaviour change:** none until `derecord --parent` is run on a folder. The
lead runs it on `apps/PhotoVault` with the sponsor's approval.

## 2026-09-14 · A new proposal page must carry its status (P21 S-03)

`proposalcheck` only inspected pages that already carried a status, so a
proposal written without the meta passed unchecked (the PhotoVault app's 72–76
and the engine's 77 did). Now:
- A numbered lead page with no status is a violation when it was first
  committed on or after 2026-09-14. The date is the committer date of the page's
  newest add, so `git commit --date` cannot backdate it, and a page deleted and
  re-added counts as new. An uncommitted page counts as new.
- Older pages are grandfathered.
- A shallow clone skips this rule and says so.
- A page made from the template that reaches a decision status (accepted,
  completed, completed in part, built) without a `proposal-decided` date is a
  violation.
- A self-closed `<meta ... />` tag is read.
- A git history that cannot be read is named as a violation, never treated as
  "new".

Two review rounds, all findings reproduced and re-verified.

**Behaviour change:** a project that adds a proposal page from 14 Sep 2026
without a status now fails `proposalcheck`. Today that is the PhotoVault app's
uncommitted 73, 74, 75 and 76. The app has to fix them when it refactors under
`/standard`.

## 2026-09-14 · Proposals are created from one template: `bin/new-proposal` (P21 S-02)

There was nothing to create a checked proposal from. Now there are two tools:

`templates/proposal.html` carries:
- the status meta and `proposal-id`;
- `<meta name="common-rules-template" content="proposal/21">`;
- sections for the ask, what was found, the options, and an
  `<ol class="decisions">`;
- a Decided section giving the literal date and status lines to copy.

It holds no empty `id="decided"` block: `proposalcheck` only looks for the
attribute, and an empty block would let a page reach accepted with nothing
recorded.

`bin/new-proposal "Title"` writes the page, its ledger and its tracker page in
one step, and keeps none of them if any checker rejects the result.
- It never overwrites.
- It numbers only names that start with 1–3 digits.
- A race or collision is refused, naming the file.
- Exit 2 means "could not run". There are no tracebacks.
- `--page-for LEDGER` writes the page for an existing ledger. A `.md` twin or
  an assets folder does not block it, and a missing tracker page is rendered.
- A project that shares proposal numbers with a sibling (the PhotoVault app and
  engine interleave theirs) declares `proposal_series` in `.common-rules.json`.
  Numbers are then taken across both.
  - A series declared on only one side cannot run, since both repos would take
    the same number.
  - A folder inside the project is not a sibling.
  - Bidi, invisible and line-separator characters are refused, in titles and in
    series entries.

The lead fixed the final review's findings (6b66b58): the `.md` twin race, the
one-sided series, the read-only tracker directory, and the tracker page for
`--page-for`.

**Standard change (mandatory):** create every new proposal with
`bin/new-proposal`, or with `--page-for` for a ledger that has no page. A
project that shares proposal numbers with a sibling declares `proposal_series`
in both projects' `.common-rules.json`.

## 2026-09-14 · Later changes to the standard are mandatory too

The sponsor added to his ruling: "if I improve something in the common rules in
the future regarding warm up or reheat, then the project should prioritize that
and implement it. It's not optional. It needs to be implemented always,
mandatory."

From now on, an entry here that changes the standard carries a line beginning
`**Standard change (mandatory):**` that says what each project must do.
`/standard`, section 3, makes every session:
1. queue each such entry as its next ledger item, right after the item in
   flight;
2. implement it;
3. only then run `rulecheck --align`.

Aligning the stamp past an unimplemented Standard change is forbidden. Your
user-level CLAUDE.md block says the same for sessions that were never given
`/standard`. Making `warmup --check` fail while such an entry is unimplemented is
proposal 21's S-09.

**Standard change (mandatory):** a project that has adopted the standard reads
the entries since its stamp at each `/warmup`, and implements every Standard
change entry, first, before aligning.

## 2026-09-14 · `/standard`: the sponsor's command that makes the standard mandatory

The sponsor asked why the PhotoVault app and engine were not creating
proposals in the new format or following the rules. The reasons, all measured:
- There was no proposal template or command to create one.
- Both lead prompts predated proposal 20; derecord never overwrites an existing
  one.
- Both sessions start in `PhotoVault/`, above the projects, so the installed
  hooks never loaded.
- Both CLAUDE.md pointers were uncommitted.
- Proposal 20's features went unused: no owners on blocked rows, requests kept
  as prose.

His ruling: "This is mandatory. It's not optional." Both sessions must follow
the same structure. Each tells him at which stage, once current tasks finish,
it will refactor. And it must be "a standard way of proceeding ahead for other
projects as well… once I use the command, I want the sessions to accept it".

`skills/standard/SKILL.md` is linked at user level, so `/standard` works in every
session. The sponsor types it himself, so it is his ruling in that session. A
project whose rules reject rulings relayed by another session still accepts it.
The session:
- replies with what is in flight and the exact stage at which it will refactor,
  and records both in its ledger;
- at that stage, refactors to one 12-item checklist shared by every project:
  - rules read
  - migrated
  - declared
  - hooks installed
  - lead prompt regenerated
  - owners and requests in the ledger
  - proposals from the template
  - no hand-kept duplicates
  - Ruflo around items
  - publishes recorded
  - CLAUDE.md pointer
  - card ready

Items whose tool is still being built, a proposal template with
`bin/new-proposal`, `bin/conformance`, a legacy floor for `proposalcheck`, and
hooks for parent start folders (proposal 21, S-02 to S-06), are reported as
"waiting on common-rules". Nothing is invented in their place.

**Behaviour change:** none until the sponsor runs `/standard` in a session.

## 2026-09-14 · A declared plan page is the page that gets published (V-11)

The PhotoVault app recorded its first publish the day proposal 20 shipped.
`tracker published` recorded the common-rules tracker page. The app's sponsor
publishes a different file: the page its own generator writes, which
`.common-rules.json` declares as `plan_page`. So the record claimed a publish
that never happened, and the card would have compared against the wrong file.
The app caught it and removed the record. D9 had already decided that a
declared page stays authoritative; V-09 had not built that part.

When a project declares `plan_page`, `tracker published` now requires
`--page <path>`. The page must be inside the project, a regular file,
tracked, and committed. The sidecar records that file's digest and the
ledger's digest. For such a page the card compares the ledger, not the file:
the app's generator stamps today's date into its page, so comparing the file
would ask for a republish every day.

A record also has to be true when it is made. `tracker published` refuses
when the ledger has uncommitted changes. With `--page`, it also refuses when
the page was last committed before the ledger changed, because an old page
recorded as current would leave the card silent for good. `--page-unchanged`
is the explicit override for a ledger change that leaves the page's bytes
identical, and the sidecar records it. Only an unreadable declaration or a bad
`plan_page` blocks recording; other declaration problems are left to
`warmup --check`.

**Behaviour change:**
- For a project that declares `plan_page`, `tracker published` without
  `--page` refuses.
- For every project, `tracker published` refuses while the ledger has
  uncommitted changes. Commit the ledger first, the order V-09 already gave.
- Existing sidecars keep working; new ones also carry `ledger_digest`.

## 2026-09-14 · Proposal 20 built: a project declares itself, the ledger carries the rest

The build of proposal 20 (`20-proposal-warmup-from-the-app.json`, V-00 to
V-10). Every piece ran in its own worktree, with a report-only reviewer of at
most the same tier for at most two rounds (D10); every review finding and every
ruling is in the ledger's log.

- **`.common-rules.json` (V-00, D9).** A project declares its read order,
  safety-rules section, quick and merge gates, plan checker and plan page.
  `land` runs `gates.merge`, then `.common-rules-test`, then its guess. The
  card, `--check` and the migration pointer follow the declared order. Every
  value is untrusted: a malformed or wrong-type declaration, a command that is
  not one line, or a path outside the project refuses in `land`, fails
  `--check`, and stops migrate writing the pointer.
- **Ledger contract v2 (V-01, D2 and D4–D8), every addition optional.** It
  checks a row's model against `tiers` unless the row gives
  `model_override_reason`. It adds `owner`, `switches`, `requests` (RQ-NN),
  verify levels against a declared ladder, evidence keys, gates, quality
  floors, receipts and merged shas. Readiness is computed with the PhotoVault
  app's own `build_plan.py` formula, and a test holds both to the same number
  on the app's real ledger. That test caught a first version that said 30%
  where the app says 26%. Ids, owners, switch and request text must be one
  line, and every problem `validate` returns is printable.
- **Tracker page v2 (V-03)** draws readiness, gates, floors, open requests,
  owners, switches that are off, and merged rows still awaiting evidence.
- **`tracker sync` honours `switches.issues` (V-04):** with issues switched
  off it makes no `gh` call and says who switched it off, and when.
- **Agent tag reminder (V-05, D3, changed by PC-01):** a PostToolUse hook, not
  PreToolUse, which can only allow, deny or ask. After an untagged Agent spawn
  that names a ledger id, it adds the row's `[ruflo · tier · model]` tag.
- **`bin/ruflo-item` (V-06, D11):** `start | done | note | recall` around an
  item. `done` runs the declared merge gate before `post-task`. The daemon
  stops on every exit, including SIGTERM. `RUFLO` takes a command such as
  `npx -y ruflo@latest`, and `RUFLO_NAMESPACE` keeps a project's existing
  memories.
- **derecord v2 (V-07, D12, D13).** The pre-commit hook regenerates and stages
  the page and checkpoint whenever a ledger is staged. Runtime state is
  ignored, config stays tracked, and already-tracked runtime files are
  reported with the `git rm --cached` command. The PostToolUse hook is
  installed with matcher `Agent|Task`.
- **The warm card v2 (V-02):** readiness, merged rows awaiting evidence, the
  sponsor's own items on the yours line, switches that are off, open requests
  both ways, and the project's routing table as declared -- each line only when
  the ledger or declaration has the data. Every printed value goes through one
  escaping function, and so does `--check`'s report: a ledger value carrying a
  newline cannot forge a line such as "warmup --check: ready". A declared
  safety-rules heading that is not in its file fails `--check`.
- **Publishing is recorded, and the card says when a page has moved (V-09, D1).**
  Only a session's Artifact tool can publish, so nothing publishes by itself.
  `tracker published <ledger> --url <url>` records the page's digest in a
  committed `<stem>.published.json`. The card then says "page changed since last
  publish" whenever the page differs; that line never fails `--check`.
  `/warmup` and the lead prompt republish the page in place and record it again.
  No sponsor prompt is needed, and nothing is published when
  `switches.publish` is off. A page that was already published is recorded at
  once. The order is: commit the ledger edits, publish the committed page, then
  commit the sidecar on its own. A republish is not logged in the ledger, because
  a log entry would move the page again. The page shows readiness as its
  headline number.
- **Templates (V-08, D10):** high-tier items run in parallel on disjoint files,
  each with a report-only reviewer. A brief carries its verify level.

**Behaviour changes for an adopted project**, all from re-running `derecord`
or adding a declaration:
- A project that adds `.common-rules.json` changes what `land` runs.
- After `derecord`, a commit that stages a ledger also carries its page and
  checkpoint.
- That commit is refused when the ledger, its page or the checkpoint has
  unstaged edits.
- A project's own pre-commit hook is kept as `pre-commit.local` and chained.
  derecord refuses if that name is taken, and refuses a malformed
  `.claude/settings.json` without changing anything.

Ledgers that declare none of the new keys validate as before; the PhotoVault
app's 70 and engine's 71 both do.

## 2026-09-14 · Proposal 20: Warm-up, from the app — accepted

`docs/proposals/20-proposal-warmup-from-the-app.html`. A second pass on the
warm-up standard, read from the PhotoVault app's session and repository after
proposal 19 was lifted from the engine: 22 sponsor turns, 5 of them "publish the
tracker" or "update the plan"; 0 of 83 agent prompts carrying the tier tag;
model routing written in five places; a ledger that already refuses done
without evidence and computes readiness. Thirteen decisions, all accepted by
the sponsor ("proposal 20 accepted", 14 Sep 07:12). The build is
`20-proposal-warmup-from-the-app.json`, items V-00 to V-10. Nothing built yet.
Unlike 19, this document carries its decisions in the `<ol class="decisions">`
and `id="decided"` shape `proposalcheck` actually checks.

## 2026-09-14 · Both PhotoVault projects are on the warm-up standard

The engine ran `warmup --migrate` at its checkpoint after E1-09 merged: both
superseded rules replaced in place with the kept substance, the originals
under `## Superseded`, its sandboxed merge gate declared in
`.common-rules-test` and honestly red until E0-08, the tracker page and a
digest-carrying checkpoint committed. The lead verified it read-only; its card
reads ready. The pilot (W-10) moves to in progress, not done: its exit
conditions include a measured pilot week, and pockets and mac-explorer are not
migrated yet.

## 2026-09-13 · The PhotoVault app is on the warm-up standard

The app's own session converted its Proposal 70 ledger to the standard shape
(48 items, now validating) and ran the migration; the lead verified it
read-only, and the app's warm card reads ready. W-13 is done. What it taught,
recorded for proposal 20: the warm-up pointer migrate writes assumes HANDOFF.md
comes first, which contradicts a project whose CLAUDE.md is its entry point;
generated checkpoints create a commit per ledger batch; and a project tracking
Ruflo's runtime files has a dirty tree after every Ruflo call. The engine's
migration (W-10) is still to run at its checkpoint.

## 2026-09-13 · The PhotoVault app's dry run: plain-bullet rules and lead prompts anywhere

Asked to migrate the PhotoVault app too, dry run first. The dry run said
"nothing to supersede", and that was false: the app writes its rules as plain
`- ` bullets, and migrate only read `- **bold**` ones, while the app's section 1
opens with the very rule the standard replaces ("One plan, updated in place").
A plain bullet's first sentence is now read as its lead. `derecord` also looked
for an existing lead prompt only in `docs/handovers/`; the app keeps
`docs/proposals/70-lead-prompt.md`, so it now looks three levels under `docs/`.
Nothing was written to the app. Its ledger uses its own vocabulary and fails
validation 138 times; migrating it waits on the sponsor's decision (W-13).

## 2026-09-13 · A project declares its test gate: `.common-rules-test`

`bin/land`'s `test_cmd()` guessed the suite from the tree -- `tests/*.py`
means unittest, `package.json` means `npm test` -- and `/warmup`'s card reports
the same answer. The PhotoVault engine's gate is pytest with markers, so both
named the wrong one, found when the engine rehearsed its migration; proposal
18 B had named the gap ("derecord carries each project's test command").

A project now declares it in `.common-rules-test` at its root, beside
`.common-rules-version`: the first line that is neither blank nor a comment is
the command. Declare the merge gate -- the one `land` runs before landing.

**Behaviour change for a project that creates the file:** `land` runs the
declared command instead of its guess. No project has the file today, so
nothing changes until one adds it.

## 2026-09-13 · Migration keeps the rule that still holds

The PhotoVault engine, asked to migrate onto proposal 19, reviewed the dry run
and did not apply it: superseding a rule moved the whole rule into
`## Superseded` and left only a one-line summary in a heading, and a project
that already has its own `docs/OPERATING-RULES.md` gets nothing seeded -- so
the engine would have lost "never a new plan document, never scrap old
content" and its definition of done ("merged with tests run here"). Each
`templates/supersedes.json` entry now carries a `replacement` rule that migrate
puts where the old rule stood; the old wording still moves, verbatim and
dated. `derecord` also stops seeding a generic lead prompt beside a project's
own dated one. Nothing had been written to the engine.

## 2026-09-13 · Proposal 19's ledger timestamps corrected

The lead wrote estimated clock times into proposal 19's ledger instead of
reading the clock: 47 of 52 log entries and all three proposed changes were dated
later than the commits that recorded them, some past midnight, written
before 22:05. Each now carries the author time of the commit that first
recorded it; entries that were not future-dated are unchanged. The seven
asks carry the time the sponsor's message arrived in the session transcript,
and three evidence sentences that stated estimated times now cite commits.
The rule is recorded in the ledger's `execution.timestamps_corrected`. The
entry below was also dated the 14th; it was the 13th. Order, hashes and
evidence were right; only the times were not.

## 2026-09-13 · Ruflo's runtime files are ignored

Running the mandatory Ruflo loop from this checkout while building proposal 19
left twenty untracked files: `.claude-flow/` (daemon, policy, logs, neural,
metrics), `.swarm/` (two memory databases and their WAL files), `ruvector.db`,
and two `proven-config` files under `.claude/`. All machine-local runtime
state. `.gitignore` now covers them; under `.claude/` only Ruflo's own files are
ignored, so a committed `.claude/settings.json` or `.claude/skills/` -- what
`derecord` installs -- is still seen. No behaviour change for any project.

## 2026-09-13 · Proposal 19 building: the ledger toolkit, templates, recall and hooks

Built on the integration branch `p19-foundation`, in the order proposal 19's
own ledger (`docs/proposals/19-proposal-warmup.json`, the first written in
the shape it proposes) sets. Seven of eleven items done; each verified by the
lead in a clean worktree at its pushed tip, not by the agent that wrote it.

- **`bin/tracker`** — one tool, one module per command in `tools/tracker/`:
  `validate` (the ledger contract; the PhotoVault engine's proposal 71
  ledger validates unchanged), `render` (a generated page in
  `docs/proposals/tracker/`, digest-checked, deterministic), `check` (did the
  ledger move with the code), `sync` (GitHub issues mirror the ledger one
  way, drift shown), `checkpoint` (writes `docs/handovers/<date>-checkpoint.md`).
- **`templates/`** — HANDOFF, OPERATING-RULES, ledger.json, lead-prompt,
  checkpoint, and the five-heading brief.
- **`bin/recall`, `bin/remember`** — recall over every project's memory,
  LESSONS, operating rules and ledger logs; remember writes one fact file.
- **`hooks/`** — PreCompact and Stop write the checkpoint (Stop only when
  the ledger changed); SessionStart after a compaction says the summary is a
  paraphrase and names the files to re-read.

**Behaviour change for adopted projects:** `bin/land` gains a gate. A branch
whose commits name a ledger item and do not move that item's row is refused;
override `LAND_ALLOW_UNLOGGED_ITEM=1`. It applies only to a project with
`.common-rules-version` and a ledger under `docs/proposals/`, which today is
none of them -- the templates and hooks reach projects through `derecord`
in W-08.

**Later the same evening: `/warmup` and `derecord` seeding.** `bin/warmup`
prints the warm card and `--check`s a project; `skills/warmup/SKILL.md` is the
chat side. `derecord` now seeds HANDOFF.md, docs/OPERATING-RULES.md and the
lead prompt (three files, not D2's six -- recorded for the sponsor) and
installs the PreCompact, Stop and SessionStart hooks. Run read-only on the
PhotoVault engine, the first card printed three wrong lines about the project
the standard came from; each was fixed test-first, and two were defects in
earlier items (`ledger.find` read a data file as a ledger; `tracker check`
crashed on a JSON array, which `land` would have reported as a refusal). The
engine's warm-up reads ~195 KB (~49k tokens) -- measured, not guessed.

**Then `tracker import` and `warmup --migrate`.** Import turns an existing
milestone plan into a ledger (finance-tracker's CLAUDE-milestones.json, or a
`## Milestones` table read with `bin/milestones`' own parser). Migrate moves a
running project onto the standard: derecord, import, and each rule the
standard replaces moved verbatim into a dated `## Superseded` block -- only
rules `templates/supersedes.json` names; nothing guessed, nothing deleted --
plus a CLAUDE.md pointer left for the sponsor to commit. Dry-run on the three
real projects: the engine would supersede exactly the two rules the list was
written from; pockets and finance-tracker would gain ledgers of 25 and 78 rows.
`bin/milestones` was deliberately left unchanged: its digest hashes whole rows,
so adding a field would have staled every project's milestone page at once.

Found while building: an installed `tools` package on the shared interpreter
(`Sangam/Sangam-engine/tools`) shadowed this repo's `tools/`, fixed with a
package marker; the mandatory Ruflo loop errored for one agent (W-06) while
working for three others, recorded in its row and unattributed; and the lead
built W-03 without moving its row to in progress -- the exact slip the W-03
gate refuses, caught by a script and recorded rather than back-dated.

## 2026-09-13 · Proposal 19: Warm-up — proposed and accepted the same day

`docs/proposals/19-proposal-warmup.html`. Analysed the PhotoVault engine
sessions of 6–13 September (160 sponsor turns, 3,321 tool calls, 257
agents) for what a cold chat has to be told and what it then does well. The
proposal lifts the engine's working shape — HANDOFF, dated operating rules,
a JSON ledger rendered to HTML, complexity classes deciding tier and model,
a lead prompt and a checkpoint — into one standard with a `/warmup` skill,
templates seeded by `derecord`, a `bin/tracker` renderer and gate, an ask
ledger so sponsor input in chat is catalogued (three of five asks on 9 Sep
were not), and a five-heading brief that carries tier, effort and scope,
not only a model name. Eleven decisions asked and all answered on 13 September: D3 = Ruflo mandatory ("i want ruflo to be mandatory"), every other decision accepted ("D1 accept, D2 accept, D4 to D11 accept"). Status moves to `accepted`. Nothing built yet; D6 sets the pilot order — PhotoVault engine, pockets, finance-tracker, mac-explorer. Section H checks the design against three independent research passes and folds in six additions.

## 2026-09-13 · Baseline: main green again, before the rules are rewritten

main had been red since 2026-08-30. f9ed133 deliberately stopped `land`
treating the word "issue" as a closing keyword (it had closed a live
finance-tracker bug from a proposal's prose), but `tests/test_land.py` still
asserted the old behaviour in three places. The tests now assert the new
rule; `bin/land` is unchanged.

Also ignores `.worktrees/` and `.claude/worktrees/`: fourteen stale
worktrees had collapsed into one untracked directory in `git status`.

Everything retired in the cleanup is kept as tags under
`archive/2026-09-13/` on origin: 68 of them, covering every branch tip that
was not on main, the uncommitted `bin/tower` multi-lane arc, a stray
`AGENTS.md`, and the old stash.

## 2026-09-01 · Proposal 18 answered — and it cut its own biggest item

The sponsor's decisions are recorded in
`docs/proposals/18-proposal-cross-project-standard.html`, which moves to `accepted`.

**Focus is four projects: pockets, finance-tracker, photo-vault, mac-explorer.**
No new adoptions. `pip` drops out of focus; `geospatial-analytics`,
`activity-manager` and `idea-lab` stay unadopted.

**CI is local-first, not GitHub Actions.** Measured while answering: `ai-sangam`
is a **private** repo, so minutes are billed, and it ran **100+ workflow runs in
seven days** — with `ci.yml` triggering on both `push` and `pull_request`, so
every merge pays for the same suite twice. `bin/land` already runs the suite
before landing on this machine, for free. That is the standard.

**The status-tracking ask turned out to be mostly already built.** Numbering
(`NN-<type>-<slug>.html`), the `proposed → accepted → completed` lifecycle, and
`proposalcheck` enforcing recorded decisions all exist and are in use in four
projects. So the proposal's own section C — build a weekly status report — was
cut rather than accepted: **the gap is not reporting, it is that proposals never
leave `accepted`.** 35 accepted across three projects; 6 ever reached
completed/built; pockets has 13 accepted and **zero** completed, some since
4 August. A weekly page listing 35 accepted proposals would restate that rather
than fix it.

Checking before building is what saved the work here, and it is worth the
sentence: three of the four things asked for already existed.

**Amended the same day, on review.** Three objections, one of them a
contradiction introduced in the drafting:

- **Section B contradicted D2 inside one document.** It said `derecord` should
  install a workflow running "on push and pull request" — written before the
  cost was measured, and not reconciled when D2 answered that hosted CI is
  billed. Implementing it would have rolled that cost out to three *more*
  projects. Rewritten local-first: `bin/land` already runs the suite for free
  and *is* the CI; what `derecord` should carry is each project's own test
  command. A hosted workflow is opt-in and never fires on both triggers.
- **Section A's second half is struck.** `land` already *refuses* a stale
  project, which is stronger than a Tower column. The two stale projects are
  dormant, not uninformed. A column nobody reads is `spend agentlog` again.
- **Section D is held.** It is prose, and prose measured 1-in-7 compliance here.

And the proposal now carries **its own exit condition**, because it diagnosed
that 35 proposals sit accepted against 6 completed and then became another
accepted proposal. Three checkable conditions, two of them tests. The
accepted-proposal backlog itself is named but deliberately not fixed here —
that needs its own numbered proposal, and bolting it on would repeat the
mistake that got section C cut.

**Section E added: one GitHub vocabulary.** The proposal covered GitHub only as
a cost, never as a standard — the sponsor caught that. Measured across the four
focus projects, the label taxonomies have diverged far enough that a
cross-project question cannot be asked: `priority:*` exists in two of four,
photo-vault calls a bug a `defect`, mac-explorer has nothing but GitHub's stock
labels, and finance-tracker writes `ui` where pockets writes `area:ui`. The
Tower reads every project and cannot filter them alike.

The standard is taken from what already works rather than invented: three axes
— `priority:now|next|later` (both mature projects already use it), one type from
finance-tracker's existing five, and pockets' `area:<name>` namespacing. Stock
GitHub labels stay and are ignored. It is a floor, not a ceiling —
photo-vault's `approved`/`decision` labels encode something the others lack and
are kept. `gh label edit --name` carries existing issues with the rename, so the
migration is one command per project rather than a re-triage.

## 2026-09-01 · Rules for GitHub, for the project's own context budget, and for deprecating old app copies

Three additions, each from something measured rather than imagined.

**A `### Working with GitHub` section.** `gh issue list` and `gh pr list` default
to **30 rows** and say nothing about what they dropped — a backlog reported here
as "30 open" was the page size, not the total, and a later count of 40 was
actually 45. Always pass `--limit`. Alongside it: check
`git log --oneline origin/main..HEAD` before opening a PR, because a branch cut
from a local `main` that was ahead of `origin` carries the unpushed commits too
and a squash collapses them under your title — on 2026-08-07 a PR described as a
one-line docs change landed 25 files and 1,109 insertions of another session's
work, and published a real corpus identifier doing it. `bin/land` now prints the
commit subjects it is about to land, so that is visible before the merge instead
of after; `tests/test_land_shows_what_it_lands.py` covers it and was run against
the old script first, where all 3 cases failed.

**A context budget for the project's own `CLAUDE.md`.** These rules were cut
from 1,637 lines to under 600 because a bloated instruction file gets ignored
rather than followed. That cut only works if the project file does not absorb
the difference, and it has: finance-tracker loads **2,218 lines** of
`CLAUDE.md` + checklist into every session, pockets 1,128, against 594 here.
History belongs in `LESSONS.md`, decisions in a numbered proposal, anything
universal in the shared rules.

**Deprecating superseded app copies.** "One installed app per project" was
already the rule and `bin/appcheck` already detects violations — but nothing
removes anything, and `appcheck` is consumed by no gate (0 references in
`bin/land`). So the deprecation step is now written down: run `appcheck` after
every `--install`, delete a worktree's development build when its task ends,
clear the LaunchServices ghost when a bundle is removed, and never touch
`/Applications` by hand.

## 2026-08-20 · Milestones and proposals reach the Tower (proposal 15)

Handed over from another session, at the sponsor's request, once every
supporting piece existed: the Tower should track each project's milestone
plan and list its proposals/decision articles, with a push to make the
Tower simpler while doing it, not just bigger.

**MILESTONES sits directly under REPORT**, reading the same `## Milestones`
table `milestonecheck` (#112) already validates — `parse_milestones()` reads
every column by its header, never positionally. That specific caution
wasn't theoretical: `milestonecheck` originally read State from `cells[-1]`,
and finance-tracker's real table on `origin/main` carries an optional
`Track` column between `You get` and `State` that a positional read would
have silently swapped — since fixed in the same #114 that added Track
support, `milestonecheck` now looks State up by header too. Order is
preserved exactly as written, not grouped by state — BOARD already answers
"what's built"; this answers "in what order, and when is there something to
hold," a different question over the same vocabulary.

**PROPOSALS sits at the foot of the page**, reading each project's
`docs/proposals/*.html` the same way `proposalcheck` (#111) already does —
`<meta name="proposal-*">` fields, the lead/part-of distinction. The title
cleanup needed more care than expected: measured live across five projects,
proposal `<title>` tags turned out to use four different conventions, not
one, and the first regex (tuned to common-rules' own shape) mangled the
other three. Fixed by splitting on the last `·` and keeping that segment
generically, rather than hardcoding a shape per project.

**The concrete simplification**: PROPOSALS caps to the most recent 8 leads
with a `"+N more, older"` note, the same pattern `QUEUED` already
established (#82) — finance-tracker alone has 38 proposal documents, and
all of them on one project page was measured, not assumed, to be too much.
Whether BOARD and MILESTONES should merge (both now carry the same state
vocabulary over overlapping rows) is named in proposal 15 rather than
decided there — that reshapes what BOARD means, and is the sponsor's call.

**MILESTONES got a picture, mid-build, on request**: the sponsor pointed at
the pocket-internet exploration's own milestone timeline
(`idea-lab/ideas/pocket-internet/09-timeline.html`) and asked for that
visual language. Ported the two ideas that carry across into Tower's own
dark, auto-refreshing screen rather than its editorial serif one: a single
horizontal arc (`render_milestone_arc`) with one dot per milestone —
state-coloured, a diamond wherever `milestone_delivers()` finds a real
You-get rather than a written-out "nothing to hold", "you are here" at the
first in-flight step — and a four-card meter (`render_milestone_meter`:
proven / in flight / in your hands / next you get) styled like REPORT's own
`.rcard` grid. Both server-rendered and static per collect, deliberately
without the source page's client-side lens buttons and expand/collapse —
that state would silently reset on Tower's 10-second auto-refresh, the same
failure mode that killed DOM-based tab state once already (#82).

Both parsers were run against every adopting project's real files before
either was wired into `render_project`, which is how the Track-column case
and the four title conventions were actually found. `test_tower_render`
stayed green throughout (99/99) — no new fetches: milestones parse from the
same `register_source()` text the feature register already reads, and
proposals are local file reads with no `git` or `gh` call at all.
## 2026-08-20 · The workflow bake-off becomes proposal 17

The collision the check above found, fixed. `08` was claimed by two documents
since 2026-08-07 and the ambiguity has been live ever since.

**Which one keeps 08 was read, not chosen.** `08-proposal-work-packages.html`
("The Tower keeps the record") was added 2026-08-06 in #37; the bake-off
followed a day later in #47. More decisive than the dates: **ten passages in
`CLAUDE-workflow.md` and this changelog say "proposal 08", and every one of
them means the work-packages document** — "not proposal 08's logbook, which was
rejected for exactly that reason", "no forecast of any kind (proposal 08
refused an ETA)". That document says *logbook* twelve times; the bake-off says
it zero times. So the number has effectively belonged to one of them in prose
for two weeks, and moving the other one breaks no reference anywhere in the
repo.

**The bake-off had been invisible, and the collision is why.**
`docs/proposals/README.md` is keyed by number and carries one row for `08` —
the work-packages one. The bake-off has never appeared in the index at all. It
is the proposal behind "Ceremony is opt-in", whose measurement (five arms, one
frozen spec, 22/22 for all five, 2.4×–22.7× cost spread) is the evidence that
rule tells people to argue against. Findable now.

**Its Decided cell reads `—` rather than a date.** The document carries no
`<meta name="proposal-decided">`, and the index's own header says the documents
win where the two disagree. Writing 2026-08-07 there because that is when the
PR merged would assert a decision date the record does not carry.

**A test that cannot skip.** `test_this_repo_is_free_of_collisions` names
`ROOT` directly instead of resolving through `apps_dir()`, because this is the
repository the suite lives in: always present, so it can never quietly pass by
finding nothing. That matters here more than elsewhere — common-rules carries
no `.common-rules-version`, so every gate in `bin/land` skips it, and the rules
repo is the one place a violation of its own rules cannot be refused. A test is
the only mechanism that reaches it. Verified by restoring the old number: the
new test fails, alone.

**Two things left alone, and named rather than quietly fixed.** The index still
stops at 14 — proposals 15 and 16 are missing from it too, and it claims to be
"derived from the documents" while no generator exists to derive it. Its status
vocabulary line is also behind the rules it points at (`draft`, `rejected`,
`superseded-by NN` with a hyphen; no `completed` or `completed in part`). Both
are real, both are wider than a renumber, and backfilling them under cover of
this change would put unreviewed edits in a records file.

Suite: 249 tests.

## 2026-08-20 · A proposal number is claimed by exactly one document

"Number every proposal" has said *"numbered sequentially per project, never
reused"* since it was written. Nothing checked the second half.

**Three collisions already existed and were found by accident.** Auditing four
projects for the lead/section rule turned up finance-tracker ids 14, 15 and 20,
each claimed by two different documents — surfaced only because somebody was
reading every proposal for an unrelated reason. `proposalcheck` validated that
decisions were recorded and that a lead carried a status, and passed both
documents of every colliding pair. A fourth is live in this repo today: `08` is
claimed by both `08-proposal-work-packages.html` and
`08-proposal-workflow-bakeoff.html`.

**A collision is worse than an ordinary violation because it breaks every
reference *to* a proposal at once.** `proposal-part-of` names an id, the shared
rules cite proposals by number, and the Tower groups a topic's pages by it.
When two documents answer to "14", each of those is ambiguous and nothing says
so.

**Not grandfathered, and the difference is in kind rather than in leniency.**
Every other rule here is date-floored because a proposal's history cannot be
honestly reconstructed — inventing the answers would misstate it worse than the
gap does. A collision is a live ambiguity, not a missing record, and
renumbering fixes it exactly. Blast radius, measured: **zero collisions across
finance-tracker, pockets, pip and mac-explorer; one in common-rules itself** —
which `bin/land` does not gate, because this repo carries no
`.common-rules-version`. So the one violation the new check finds is in the one
place the gate cannot fire, which is proposal 16's *Where D5 lands* happening
in real time rather than in the abstract.

**Absent is not a value.** A document with no `proposal-id` does not
participate. pip's `02a`/`02b` are two sections carrying none, and bucketing
them together would have failed a project on day one for a rule about *reuse* —
which is how a check gets disabled. Pinned by a test.

**Real sections settled a design question the fixtures had hidden.** All 14 of
finance-tracker's sections carry their *own* id and point at the lead through
`part-of` — 33 through 38 all sit `part-of 32`. So a lead and its sections
never share a number, and the check needs no exemption for them. This surfaced
because `tests/test_proposal_lifecycle.py`'s `proposal()` helper hardcoded
`content="01"` for every document it built, which made every two-document
fixture a collision the moment collisions became checkable. The helper takes a
`pid` now; the answer came from measuring the real files rather than deciding
what a section ought to do.

**The summary line now says what was looked at.** It read *"every proposal that
asked decisions recorded them"* whatever it had examined — and across
pockets' nineteen proposals, pip's four and mac-explorer's one, **not one
carries a decisions list at all**, and common-rules' sixteen carry exactly one
— proposal 16, merged hours ago. That sentence has been vacuously true for
those three projects for the tool's whole life while reading as a clean pass,
and was true of this repo too until today. Only finance-tracker has ever
really given it anything to check: 7 of 38. The
exit code already separated "checked and clean" from "could not check" (2); the
line a person reads did not separate "checked and clean" from "there was
nothing to check". It now reports both counts. Reporting only — the exit code is
unchanged, because a vacuous pass is not a violation.

Verified by reverting `bin/proposalcheck`: 5 of the 10 new tests fail.
`tests/test_proposal_ids.py` (10). Suite: 248 tests.

## 2026-08-20 · The real-project checks stop skipping where they are run

**Follow-up, same PR: the third instance is fixed too.**
`test_rulecheck.RealProjectsStillCheck` — raised in #113, left unfixed there,
and named as out of scope when this branch opened — now takes the same
`apps_dir()`. It carried a second bug the resolution had been hiding: its
`skipTest` sat *outside* the `subTest`, so the first absent project aborted the
whole test and the remaining three were never looked at even when present.
Since `ROOT.parent` made the first one always absent, that was every run.

**The helper is one module, not a copy in each.** `tests/projects.py`, imported
by both, with `tests/test_projects.py` pinning it. Two copies of a path rule is
how the two drift, and this is the rule that has now been got wrong three times
in two days. It is not named `test_*.py`, so `discover` does not collect it;
both callers put `tests/` on `sys.path` explicitly so the suite runs the same
way under `discover -s tests` and under an explicit `tests.test_x` module path.

**The structural guard widened with it** — it now scans every `*.py` in `tests/`
rather than only its own file, which is what makes it catch a regression in a
module other than the one it lives in. Verified: reverting `test_rulecheck`
alone gives `FAILED (failures=1, skipped=1)`, the failure naming
`test_rulecheck.py:196` from a guard in `test_projects.py`.

**The suite now has no skips at all.** It reported `OK (skipped=1)` for as long
as this bug existed, and that skip was the bug describing itself.


`tests/test_proposal_lifecycle.py` resolved the projects it reads as
`ROOT.parent` — `apps` from the main checkout, and
`.worktrees/` from a task worktree, where it holds no projects at all. So
both blast-radius checks found nothing and passed.

**That is both places the suite is actually run.** `bin/land` tests the
branch worktree; CI checks out a repo with no siblings. The checks could
only ever fail in the one place nobody runs them — the same sentence
#113 wrote about `test_rulecheck`'s copy of this bug, still true a day
later in a second file.

**One of the two was worse than a skip.** The pockets/pip loop used
`continue`, not `skipTest`, so it ran zero assertions and reported `ok` —
indistinguishable from a run that had actually read both projects. The
finance-tracker one at least announced itself. Both now skip out loud,
per project, inside their `subTest`.

**The resolution is read, not assumed.** `apps_dir()` asks
`git rev-parse --git-common-dir`, which names the *main* checkout's `.git`
from inside a worktree as readily as from the checkout itself. This is the
corrected form of what `ROOT.parent` was reaching for, not a new policy —
`bin/milestones` and `bin/pulse` name `apps` outright and
are right to: `--all` has to find every project on this Mac, which is a
claim about the machine. A test needs the projects beside *this* checkout,
which is a fact about the repo. Outside a git repository it returns None
and the callers skip rather than resolve something arbitrary.

**Asserting that the checks pass proves nothing — they pass hardest when
they are skipping.** So the guard is structural, in the shape #116 used for
its baked-in home directory: no `ROOT`+`.parent` on any line of the file.
The forbidden token is assembled at runtime so the guard is not a hit for
itself, and backticked prose is exempt so the docstrings can explain the
bug they guard against. Alongside it, a hermetic test builds its own
`<apps>/<repo>/.worktrees/<name>` layout and asserts the answer from both
ends, rather than depending on this Mac having one — a regression test that
needs the real machine stops testing the moment it runs anywhere else,
which is the bug.

**Verified by reverting**, and the numbers say it exactly: reverted, from a
worktree, the file reports `FAILED (failures=1, skipped=1)` — the guard
fails and the vacuity shows as the skip. Fixed, it reports 27 tests, **0
skipped**, having genuinely read finance-tracker, pockets and pip from a
worktree for the first time.

**The third instance is untouched and is now the suite's only skip.**
`test_rulecheck.RealProjectsStillCheck` (`ROOT.parent`, raised in #113 and
never fixed) takes the same `apps_dir()` in one line. It is left out of
scope deliberately rather than swept in; the full run reports
`OK (skipped=1)` and that skip is it. Suite: 236 tests.
## 2026-08-23 · A milestone that explains why it hands nothing over is no longer counted as a delivery

*Ask, verbatim: "fix the milestones count bug."*

Found while piloting proposal 16 against finance-tracker's real plan.
`bin/milestones` decided whether a row hands something to the sponsor by
testing the You-get cell for **equality** against a fixed refusal vocabulary
(`^(nothing( to hold| yet)?|none|no|n/?a|—|-)$`). A row that merely *said*
"nothing to hold" passed. A row that said **why** did not.

So the meter answering "when do I get something" was inflated by exactly the
rows that were most careful about saying they gave nothing. finance-tracker's
money-correctness row — the one row whose entire point is that the sponsor
holds nothing until the figures are trusted — reads `nothing to hold — this is
the floor everything else stands on`, and has been counted as a deliverable for
the whole life of that plan. Measured: its 13-row plan reported `13 hand
something over`, and now reports 12; the 16-row pilot plan reported 16 and now
reports 13.

The rule requires the column be written rather than left blank *precisely so
that "no" can be said out loud*. Punishing a row for saying it well inverts the
rule it was built to serve.

**The fix is a prefix match, not a wider vocabulary**: a refusal word, then
either the end of the cell or a punctuation mark introducing the explanation.
The punctuation requirement is the whole safety of the widening — it is what
keeps a genuine deliverable that merely *starts* with one of those words ("no
more waiting for the book to open") from being swallowed as a refusal. Both
cases are pinned by tests, and the explained-nothing test was confirmed red
against the old regex before the fix.

**Two consequences worth stating.**

The digest hashes the parsed rows, and `deliver` is one of them — so every
adopting project's committed `docs/milestones.html` is now stale and
`bin/land`'s `--check` gate will say so until it is regenerated. That is the
gate working: a page showing the wrong count should fail loudly rather than
pass quietly.

`bin/tower`'s `milestone_delivers()` carries the **same bug by an independent
route** — set membership against the same vocabulary, with a docstring
describing precisely the case it gets wrong. The sponsor asked for the two to
match. **They cannot be made to match from a clean branch**: that function
exists only in `ac3d3f4`, an unpushed commit in the shared
`common-rules` checkout, under a further 130 uncommitted
lines of in-progress work. It is absent from `origin/main` entirely. Editing
it means editing an unreconciled working tree, which would put real
in-progress work at risk to fix a dormant bug.

So the matching is set up rather than done. `hands_something_over()` is now a
**public function** in `bin/milestones` — the one definition of this predicate.
When that Tower work is reconciled and pushed, `milestone_delivers()` should
call it (`bin/tower` already loads `bin/pulse` and `bin/spend` this way, so the
pattern is established) rather than get a second corrected copy of the
vocabulary. Two independent implementations is exactly how one predicate came
to be wrong in two places, each with a comment describing the case it missed.

## 2026-08-20 · The milestone/feature vocabulary gets `completed`, matching proposal-status

*Ask, verbatim: "I think we need some sort of that vocabulary that tells if a
proposal has been completed or not in the end. Right now, it shows... but it
doesn't show completed."*

The register/milestone vocabulary (`in flight` / `next` / `blocked by #N` /
`later` / `version N` / `built` / `done`) never had a word matching
proposal-status's own `completed` — the two systems drifted onto different
terminal words for the same idea (`done` here, `completed` there), and `built`
carries different meanings in each: a grandfathered synonym for `completed` in
proposal-status, but a genuinely distinct "shipped, not yet closed" state in the
milestone/feature vocabulary (finance-tracker's own tracks generator already
labels it "built, not closed").

**The fix mirrors the one already applied to proposal-status.** `completed` is
now the word for a milestone or feature fully finished; `done` is a
grandfathered synonym, not mass-renamed where it's already written (this
session's own finance-tracker milestone plan uses it), but write `completed`
from here on. `built` keeps its own narrower meaning and is not folded into
`completed` — collapsing the two would erase a distinction the tracks generator
already draws on purpose.

`bin/milestonecheck`'s `STATES` set gained `completed`;
`tests/test_milestonecheck.py` gained a test pinning both `completed` and the
grandfathered `done` as accepted, alongside the existing full-vocabulary test.
`CLAUDE-workflow.md`'s register and milestone-plan sections both restate the
vocabulary and the `done`→`completed` migration note.
## 2026-08-20 · rulecheck locates itself instead of guessing a home directory

`bin/rulecheck`'s rules-repo default was the literal string
`common-rules` — correct on exactly one machine. On a CI
runner that path does not exist, so `git -C <missing>` fails,
`current_version()` returns `None`, and `--version` exits 2. That errored
**11 gate tests** across `test_land_alignment`, `test_land_proposalcheck` and
`test_land_milestonecheck` on every CI run since CI existed.

It surfaced only today because Actions had been blocked at the billing gate;
the first run that actually executed after the account moved to Pro failed on
this immediately. A correction to what this session said earlier: these errors
were called "a CI-environment divergence, not a code bug". They were a code
bug.

**The default is now `Path(__file__).resolve().parent.parent`** — a script
always knows where it lives. `COMMON_RULES_DIR` still wins when set, which is
how tests and projects point it at a particular checkout.

**One deliberate behaviour change.** Run from a task worktree, `--version` now
reports *that worktree's* version rather than the main checkout's. That is the
honest answer — the version should describe the rules actually being run — but
it changes what every gate compares against inside a worktree, which is where
`bin/land` does all its checking. Raised before the change rather than
discovered after.

**The test's shape is the point, and it is the reason this survived.** Asserting
`--version` merely succeeds proves nothing: on the developer's Mac the
hardcoded path resolves and the broken version passes too. So the test runs a
*copy* of the script from a *different* repository and asserts it reports that
repository's version — something only a self-located default can do. Verified
by reverting the fix: 3 of the 4 new tests fail, including the structural guard
that no home directory is baked into the default.

**Third variant of one mistake, all found today**, and worth naming as a class:
`RealProjectsStillCheck` resolving projects as `ROOT.parent` (skips everywhere
it is run), `bin/milestones` deriving `APPS` the same way (silently found
nothing from a worktree), and this. Each derived a path from an assumption
rather than from something true at runtime, and each was invisible precisely
where it was wrong.

**And it exposed a second bug underneath it: CI has always cloned shallow.**
The rules version *is* `git rev-list --count HEAD`, and `actions/checkout`
defaults to depth 1 — so on a runner HEAD counts as commit 1, and
`test_stamp_is_not_from_the_future` reads "stamp claims 163, but HEAD is only
at 1". This could never have been seen before today: `rulecheck --version`
exited 2 on a runner, so the version was never successfully computed there at
all. One bug was standing in front of the other. `fetch-depth: 0` now, which
`rulecheck`'s changelog diffing needs for the same reason.

Suite: 231 tests.

## 2026-08-20 · The milestone plan gets a picture, and it is generated

Asked for directly, after seeing `pocket-internet`'s timeline: *"each project
should have a live document like this with a graph"*, then *"I want the same
structure in every project. And this should be the common rule. And every
project should speak the same language as a standard template."*

**`bin/milestones` renders `docs/milestones.html` from the `## Milestones`
table** — the same table `bin/milestonecheck` validates. Lanes, states, a
marker wherever something reaches the sponsor's hands, and four meters. One
template, so four projects' plans read the same way.

**Generated, never written, and that is the whole design.** A hand-maintained
second copy of the plan is precisely the drift the plan rule already warns
about — "a milestone plan that is not maintained is worse than none" — with
extra steps, because the table and the picture separate and the picture is the
one people look at. The page has no data of its own, so it cannot disagree.

**Staleness is checkable via a digest, not a byte comparison.** The page stamps
its own generation time, so comparing files would call every page stale the
moment the clock moved. Instead the page carries a 16-char hash of the plan's
content and `--check` recomputes it, asking the only question that matters:
does this still show this plan. Pinned by a test that rewrites the timestamp
and asserts the check stays clean.

**Parallel work gets lanes — an optional `Track` column.** Added the same day,
on the follow-up: *"some projects have parallel milestones... in financial
tracker there is a quality thing going on, and then there is a UI thing going
on."* A project naming tracks gets one lane per track instead of one rule;
omit the column and nothing changes. Three decisions worth recording:

- **Lanes are drawn in the order the plan first mentions them**, never sorted —
  same rule as the rows.
- **Each lane carries its own "here."** With parallel work there is no single
  front, and one marker would assert an ordering between lanes the plan never
  claimed.
- **Lane length is information.** All lanes share one step, so a one-milestone
  track draws a stub rather than a full-width rule. The first cut stretched
  each lane to full width independently, which drew a lane with one milestone
  as though work continued along it.

**A positional read became a bug the moment the column existed.**
`bin/milestonecheck` took the state from `cells[-1]`, which was correct only
while State happened to be last. A `Track` column to its right had every row's
track read as its state, and a valid plan was refused for a vocabulary it never
used. State is now found by header, falling back to the last cell only when no
State column is declared. Three tests pin it, including one asserting a
genuinely bad state is still caught when Track sits last — a fix that stops
catching real violations is not a fix.

**The tenth gate.** `bin/land` refuses a project whose page is missing or
stale, `LAND_ALLOW_STALE_MILESTONE_PAGE=1` to override. Separate from the ninth
rather than folded into it, and separately overridable: one wants the plan
*written*, this one wants a command *run*, and a single refusal covering both
would name the wrong fix half the time. Wired in the same PR as the renderer,
for the reason the last three entries all give.

**Two things the first cut got wrong, found by running it.**
`--check` returned 1 for a project with no `## Milestones` at all, so `land`
refused twice — once in the plan gate's words and once in an empty message from
this one. It now returns 2: no plan means no picture to be stale, and that
finding belongs to the gate that owns it. And `--all` silently found nothing
from a worktree, because `APPS` was derived as `RULES.parent` — the same
resolution trap that let `test_rulecheck`'s real-project subtests skip
everywhere they were actually run (#113), three hours earlier, in this repo.
`bin/pulse` names the path; so does this now.

`tests/test_milestones_page.py` (15) covers the renderer, the digest and the
gate. Suite: 225 tests.

## 2026-08-20 · `bin/land` now consumes `bin/milestonecheck` — the ninth gate

The milestone-plan rule landed the same day (`## Milestones` in
`CLAUDE-checklist.md`, with a **Proves** column and a **You get** column) and
landed *advisory*: nothing read it, so nothing enforced it.

**The checker and its caller ship in one PR this time, on purpose.** That is the
third instance of the same gap and the first one caught before it opened. #106
shipped `bin/proposalcheck` with nothing calling it and #107 had to come back a
day later to connect it. `rulecheck --quiet` sat in a `SessionStart` hook whose
exit status stops nothing until the 2026-08-18 alignment gate made it
load-bearing. Both times the rule was a suggestion for as long as the two halves
were separated by a PR boundary. Splitting them is what creates the gap, so they
are not split.

**What is checked — structure only.** A `## Milestones` section exists and holds
a table; the header carries a Proves column and a You-get column; every row fills
both; states come from the register's vocabulary.

**What is deliberately not checked.** Not freshness — "in flight for N days"
fires on every genuinely slow milestone and trains everyone to ignore the
checker, so staleness stays a judgement for `bin/pulse`, where a person sees it,
rather than an exit code. Not truth — nothing here can know whether "retrieval is
good enough to build on" was actually proven.

**"Nothing to hold" is a valid You-get and is pinned by a test.** The column may
not be blank, but it may say no. A checker that rejected "nothing to hold" would
push people to invent a deliverable per milestone, which is the exact failure the
column exists to prevent.

**Blast radius, measured 2026-08-20, and it is not zero — it is everything.**

| project | `## Milestones` | verdict |
|---|---|---|
| finance-tracker | absent | blocked |
| pockets | absent | blocked |
| pip | absent | blocked |
| mac-explorer | absent | blocked |

All four adopting projects are refused until each writes a plan. This is the
opposite of #107's reading, where `proposalcheck` reported 0 blocked in all four
and the gate cost nothing to turn on. **`LAND_ALLOW_NO_MILESTONES=1` therefore
matters more here than its three siblings do**, and it is recorded in the PR
either way. Writing four short milestone tables is a one-off of maybe ten minutes
each; whether to do that before or after this lands is the user's call and is
being asked rather than assumed.

**Exit codes follow proposalcheck's reading, not rulecheck's.** Only 1 refuses. A
2 means "no `CLAUDE-checklist.md` under this project" — for an *adopting* project
that is a malformed project, but it is the checklist rule's violation to report,
not this gate's; folding it in would have this gate reporting someone else's rule
in its own words.

`bin/pulse` grows a second chip beside the alignment chip — its own, not folded
in, because the two fail for unrelated reasons and are fixed in different files,
and one chip reading "not ok" for either would send a session to the wrong one.
It reads `no milestone plan` for all four projects today.

`tests/test_milestonecheck.py` (12) and `tests/test_land_milestonecheck.py` (7)
pin the checker and the gate separately, the second mirroring
`tests/test_land_proposalcheck.py`'s throwaway-repo harness. Suite: 195 tests.

**Depends on the milestone rule itself (PR #109) being in `main` first.** This
gate enforces a rule whose text is still on a branch; landing it first would
refuse four projects on the authority of a paragraph nobody can read yet.
## 2026-08-20 · rulecheck's tests stopped reading its evidence as its verdict

Three subtests of `test_rulecheck.RealProjectsStillCheck` have been failing in
the `main` checkout — pockets, pip and mac-explorer — and the projects were
never the problem.

`rulecheck` prints a verdict, then, for a stale project, **quotes the changelog**
under "What changed since (N changelog lines)". The changelog is prose about
these rules, and one entry contains the sentence *"common-rules does not adopt
itself."* The assertion was `assertNotIn("does not adopt", r.stdout)` — searching
the verdict and the evidence as one string. Three adopting projects were
correctly recognised and correctly reported stale, and the test called them
skipped because the changelog it had just been shown contained the words it was
grepping for.

**The fix is scoping, not rewording.** A new `verdict()` helper cuts stdout at
the dump heading, and every "does not adopt" assertion now reads only
rulecheck's own words. Rewording the changelog entry would have worked today and
broken again the next time anyone wrote that phrase.

This is the same failure the render tests already guard against:
`test_tower_render.test_no_forecast_in_the_data_rows` scopes its search to the
data rows precisely because the page's own disclaimer contains the forecast
words it bans. That guard existed and was documented; this file did not have it.

**`TheChangelogIsEvidenceNotVerdict` pins it, hermetically.** It builds its own
two-commit rules repo whose changelog delta carries the poisoned phrase, rather
than relying on the real `CHANGELOG.md` still containing that sentence — a
regression test that depends on the prose it guards against stops testing the
moment someone rewords an entry. A second test pins the dump heading itself,
because if that wording changes, `verdict()` silently stops cutting and every
assertion goes back to searching the whole dump, passing and testing nothing.
Verified by neutralising `verdict()`: 4 failures, including the new one.

**Why this survived so long, and it is not fixed here.** `RealProjectsStillCheck`
resolves the projects as `ROOT.parent`, which is `apps` only from
the main checkout. From any task worktree it resolves to `.worktrees/`, finds no
projects, and **skips**. So the test is vacuous everywhere it is normally run:
`bin/land` tests the branch worktree, and CI checks out a repo with no sibling
projects at all. It can only fail in the one place nobody runs the suite. That is
a real gap in what `land` and CI actually verify, it is wider than this fix, and
it is being raised rather than quietly patched.

## 2026-08-20 · A document is either a proposal or an artifact

Asked for directly, in conversation, while a finance-tracker session was adding six
parallel spending-UI concepts from one design-explorer run — they had nowhere to go
but loose, unnumbered `claude.ai` links, because nothing said a document with no
decision of its own (an exploration, several concepts shown side by side before a
direction is picked) was allowed to be numbered without also claiming a status.

**The rule was already half-written and never said out loud.** `docs/proposals/README.md`'s
own generated index already had a lead+sections shape (`proposal-part-of`, "a topic's
supporting pages... carry no status of their own") — three finance-tracker sections
and two pip proposals were already living this way, correctly, by convention alone.
What was missing was the mechanical half: nothing checked that a **lead** (no
`part-of`) actually carried a status, or that a **section** (has `part-of`) carried
none.

**Both directions matter, and the second one caught something real.** Auditing
finance-tracker/mac-explorer/pockets/pip to find the zero-blocking floor surfaced
three genuine, pre-existing proposal-number collisions in finance-tracker (ids 14, 15
and 20, each reused by two different documents) — unrelated to this rule, fixed
separately in that project — and one real vocabulary typo in pockets: `superseded-by
14` instead of the documented `superseded by 14` (hyphen for space), sitting unchecked
since 2026-08-04. Both were only found because someone finally asked "does every lead
actually have a status" instead of assuming the convention held.

**`bin/proposalcheck` gains two checks**, its own floor (`STATUS_EFFECTIVE_DATE`,
2026-08-20 — a different rule than the decisions-recorded one above, written a day
later, so it gets its own date rather than reusing that one): a lead with no
`proposal-status`, or one that matches none of the known vocabulary
(`proposed`/`accepted`/`completed`/`completed in part`/`built`/`amends NN`/`superseded
by NN`), fails; a section that also claims its own status fails the mirror way. 0
blocked today across every adopting project — pockets' typo'd lead and pip's two
undated leads are grandfathered the same way an undated or pre-floor proposal already
is under the rule above, not specially cased.

**Not wired into `bin/land` in this PR.** The decisions-recorded rule shipped
advisory-only for a full day (#106) before a session actually hit the gap and #107
wired it in — this PR ships the check and its tests only; wiring it into `land`'s exit
code (the same eighth-gate shape #107 added) is a separate, smaller follow-up once
this lands, not bundled in to keep the diff reviewable.
## 2026-08-20 · Every project keeps a milestone plan, beside the feature register

Asked for directly (`ASKS.md`, 2026-08-20) after seeing a phased plan for the
`pocket-internet` idea: *"make a common rule that all projects should maintain a
common milestone plan like this."*

**Why the feature register was not already enough.** It answers "what is this
product made of, and how much of it is done" — and the Tower reads it for exactly
that. It does not answer "in what order, and what does each step establish", which
is the question that decides what to do next. Two different views; the register
carries one of them.

**The addition is a `## Milestones` table** in the same `CLAUDE-checklist.md`,
sharing the register's state vocabulary, with one column the register has no
equivalent of: **Proves**.

**Three disciplines, and they are the whole point of the rule.** A milestone ends in
something *proven* rather than delivered — "the index builds" is a task, "retrieval
is good enough to build on" is a milestone. The result that would stop the plan is
written *before* the work starts; written afterwards it is a rationalisation of
whatever the data happened to say. And **every row states what the sponsor gets,
including when the answer is nothing** — added the same day on his follow-up, *"add
checkpoint when will I get what feature in user end"*, which is the question a
proves-only plan silently refuses to answer.

**The evidence is one day old and it is the reason this is worth a row.** The
`pocket-internet` plan opened with five cheap verifications named in advance. Three
ran. Two confirmed an estimate; one corrected a claim about a German timetable feed
that had already propagated into two proposals and would have reached the build.
Twenty minutes of network time overturned a conclusion that eleven research passes
of reading had not — because the check had been written down as a thing to prove
rather than left as a thing to assume.

**And it is a live document.** Asked for in the same conversation: *"this doc should
always be a live doc maintained till feature completion."* The guardrail against it
becoming proposal 08's logbook is a test rather than a prohibition — **a session that
edits the plan because it *did* something is writing a logbook and is wrong; a
session that edits because something is now *known* is maintaining the plan and is
right.** Three events move it: a state change, a proof landing (recording what
actually happened when it differs from the prediction), and a reorder forced by a
proof. All three are rare across a feature.

**Honest note on the cost.** This is an *addition*, and this file's own rule is that
a new rule must either replace something or be enforceable by `derecord`. It does
neither. The argument for it is that it extends a section that did not reach far
enough rather than opening a new front, and that it inherits the register's
guardrail verbatim: **not a per-task obligation**, changing only when the order of
work changes. It is deliberately not proposal 08's logbook, which was rejected for
being exactly that.

**Effect on adopted projects.** `finance-tracker` and `pockets` have adopted these
rules; `mac-explorer` and `pip` carry a version file. None has a `## Milestones`
table today, so all four are now behind this rule until one is added. Nothing
enforces it — no `derecord` attribute, no `land` gate — so it is advisory in the
way `rulecheck --quiet` was before 2026-08-18. If it should have teeth, that is a
second change and a separate PR.
## 2026-08-20 · The Tower's progress tests no longer depend on what day it is

`tests/test_tower_render.py` has been red on `main` since **2026-08-15**, and
every branch cut from it inherited the failure. The cause is not the assertion
that broke; it is the shape of the fixture behind it.

`velocity()` measures a window computed from `datetime.date.today()`. The
fixture it was measured against was dated absolutely —
`2026-08-03 / 08-05 / 08-07`. An absolute fixture read through a relative
window is a time bomb whose fuse is exactly the length of the window: green in
review, green in CI that afternoon, red a week later with no commit to blame.
Nobody changed anything on 08-15. The calendar did.

**This is the second time the same test has broken this way.** `ee141e2`
(2026-08-10, "Fix velocity()'s window fallback; test_tower_render green again")
re-dated the fixture forward. That reset the fuse; it did not remove it, and it
went off again five days later. So the fix here is not a third re-dating: the
fixtures are now anchored to today via a new `_ago(days)` helper, and dated to
land inside the window by construction. There is no date in them left to age.

**Two more fixtures carried the same trap** and are anchored the same way.
`CostIsPairedWithMovement.HIST` was the interesting one — it asserts
`"completed in the last 7 days"` and has been **passing only by accident**,
via the out-of-window fallback described below. It would have started failing
the moment that fallback was corrected, in a PR that had nothing to do with it.

Verified by running the class at simulated dates of today +0, +1, +3, +7, +14,
+30, +90 and +365 days: 6 tests, 0 failures at every offset. The same harness
run against the pre-fix file fails at every offset, so it is measuring
something.

**Found while fixing this, deliberately NOT fixed here** — `velocity()`
mislabels stale data rather than declining to report it. When no point falls
inside the window it falls back to `points[-2:]` and reports that diff under
the window's label. Points dated 08-01 and 08-02, read on 08-20, render as
`9 item(s) completed in the last 7 days` — a sentence about the last 7 days
built from data 18 days old. The fallback was added deliberately in `ee141e2`
to fix a real problem (a length-1 window silently diffing against itself), so
correcting it is a judgement about what the Tower should say when a project
has gone quiet, not a typo. That is the user's call and is being asked
separately.

## 2026-08-19 · `bin/land` now consumes `bin/proposalcheck`'s exit code

Reported cause: issue #107 asked to "wire the checker into `land`". The real
cause is the one from 2026-08-18 repeating itself one day later: `bin/land`
was not modified in the same PR that added `bin/proposalcheck` (#106), so the
rule it enforces — a proposal that asked numbered decisions records the
answers, or a `completed in part` names its exceptions — was advisory in
every project it governs, exactly the way `rulecheck --quiet` sat unconsumed
in a `SessionStart` hook until yesterday's alignment gate gave it teeth. A
checker with no caller is a suggestion wearing the shape of a rule.

**The eighth gate in `land_one()`**, same guard and shape as the seventh
(alignment): only a project carrying `.common-rules-version` is checked — one
that never opted in never claimed to be governed by a rule that lives inside
these rules. `LAND_ALLOW_UNRECORDED_DECISIONS=1` is the named escape hatch,
recorded in the PR either way, alongside `LAND_ALLOW_UNTESTED` and
`LAND_ALLOW_STALE_RULES`.

**Exit 2 is deliberately not treated the way the alignment gate treats
`rulecheck`'s exit 2.** `rulecheck`'s 2 means "could not check at all" and is
folded into "refuse" there. `proposalcheck`'s 2 means "no `docs/proposals/`
under this project" — an ordinary shape for a project with no proposals yet,
not an error — and treating it as a failure would block every proposal-less
adopting project on a gate with nothing to say. Only exit 1 (an actual
violation) refuses; exit 2 lands same as exit 0. The two checkers' 2s cannot
collide in practice, because the `.common-rules-version` guard already
excludes the only case (a non-adopting project) that makes `rulecheck` return
its 2.

`tests/test_land_proposalcheck.py`, mirroring `tests/test_land_alignment.py`,
pins: no stamp → not blocked; a compliant proposal → lands; a proposal with
no `docs/proposals/` at all → lands (the exit-2 case, above); an unanswered
proposal → refused, naming the offending file; the override → lands.

Blast radius measured against the four adopting projects today:
`bin/proposalcheck` reports 0 blocked in each of finance-tracker,
mac-explorer, pockets and pip — the same reading #106's own changelog entry
already recorded, unchanged since nothing in any of their proposals crossed
the 2026-08-19 grandfather floor in the interim. `mac-explorer`, `pockets` and
`pip` remain blocked from landing regardless, by the alignment gate, for the
unrelated reason of being behind on `rulecheck --align`.

`docs/workflow.html` updated to name the eighth gate and its override, stamp
unchanged (`CLAUDE-workflow.md` itself did not change — this completes a rule
already written into it on 2026-08-19), PNG regenerated to match.


## 2026-08-19 · a proposal must record its answers, and reach a terminal state

Prompted by a measured gap in finance-tracker (its issue #584), not a taste
call: 11 proposals there are `accepted`, 9 carry a decision date
(`<meta name="proposal-decided">`), and only 3 record what was actually
decided — and those three were hand-written on the day the gap was noticed.
The date says *when*; it never says *what*, so `proposal-auditor` had nothing
to measure a build against beyond "was there a date". The concrete cost:
proposal 18 was accepted 2026-08-12, and six days later a review filed
sixteen defects against what it authorised, with no way to tell whether the
build drifted from the agreement or the agreement was never that specific.

**Two additions to the proposal rule in `CLAUDE-workflow.md`:**

1. **A proposal that asked numbered decisions must record the answers.**
   Scoped mechanically, not by size — "did it ask?" is checkable, "is it big?"
   is not. A proposal carrying a non-empty `<ol class="decisions">` list must
   carry the answers in the same document, in an `id="decided"` block, before
   it reaches `accepted`/`completed`/`completed in part`/the grandfathered
   `built`. Proposal 18 (portfolio-pdf) already does this by hand — the rule
   just makes it checkable rather than a habit that lapses.

2. **A proposal now reaches a terminal state.** `completed` replaces `built`
   as the vocabulary going forward (`built` stays valid — two proposals
   already use it, not mass-renamed). New: `completed in part`, which
   requires an `id="exceptions"` block beside the decisions naming what was
   not built and why. A partial-completion status naming nothing is
   indistinguishable from quietly marking something done.

**Both are grandfathered by decision date, not by a hand-maintained list.**
Nothing decided before **2026-08-19** — the day this landed — is checked, and
a proposal with no `proposal-decided` date at all reads the same way.
finance-tracker alone has 8 accepted proposals whose answers are
unrecoverable; inventing them would misstate history worse than the gap does,
and a test that fails on day one against documents nobody can fix gets
disabled. The floor is stated here, in the rule, and in `bin/proposalcheck`'s
own docstring, so the exemption is legible rather than silent.

**`bin/proposalcheck --project <dir>`** is the mechanical form of both rules
plus the grandfather. Run today against the four adopting projects: 0 blocked
in every one. finance-tracker has 4 proposals that would fail without the
floor (20, 23, 24, 25 — all decided 2026-08-17/18), so this rule is
enforcement-going-forward only, not a retroactive block. `mac-explorer`,
`pockets` and `pip` have no proposal using the `<ol class="decisions">` shape
yet, so the rule currently has nothing to flag there either way — those three
are also still behind on `rulecheck --align` (2026-08-18 entry) and blocked
from landing regardless.

`tests/test_proposal_lifecycle.py` pins both requirements and the
grandfather, including that finance-tracker's real proposals are 0-blocked
today (guards against a fix that quietly re-tightens the floor and starts
failing history it was supposed to leave alone).

`docs/workflow.html` updated with the new status vocabulary and the
decisions-recorded requirement, stamp bumped, PNG regenerated.


## 2026-08-18 · `bin/land` refuses a stale project, and `rulecheck` stops calling "I couldn't check" a pass

Measured today: `mac-explorer` is on `127-efefb00`, `pockets` on `124-7f4fbc2`,
`pip` on `103-06012ae` against current `154-d60140c` — 27, 30 and 51 versions
behind. All three already have `rulecheck --quiet` installed as a
`SessionStart` hook, so `derecord` was not the gap. `rulecheck --quiet` was
**already exiting 1** for every one of those sessions; nothing consumed it,
because a `SessionStart` hook's exit status does not stop a session. The
signal existed and fired every time and changed nothing.

This session made the mistake the change exists to prevent, and it is the
clearest evidence for why exit code mattered here. It ran `rulecheck` from
inside `common-rules` itself at the start, got `common-rules is the rules
themselves — nothing to align against.` at **exit 0**, and moved on having
verified nothing. The friendly sentence and the "nothing wrong" exit code were
indistinguishable from an actual pass.

**Two changes, one root cause: a signal that could be gotten without being
acted on.**

1. **`rulecheck` gives "could not check" its own exit status (2).** Before,
   both "run inside common-rules itself" and "run in a project that never
   adopted the rules" printed a friendly sentence and exited 0 — the same
   code as "verified, and aligned". Now: `0` verified aligned · `1` verified
   and stale · `2` nothing was verified. Checked every caller: the
   `SessionStart` hook (`rulecheck --quiet`) never reads the exit code, so
   it keeps working unchanged; `bin/derecord` only installs that hook string
   and does not branch on rulecheck's exit either. Nothing else shells out to
   it. `tests/test_rulecheck.py` pins the new contract, including the two
   assertions that used to expect 0 and now expect 2.

2. **`bin/land` refuses to land from a project that is stale on
   `.common-rules-version`.** This is the enforcement point that was missing
   — the actual harm is merging work produced under rules nobody read, and
   `land` already refuses for exactly this class of reason (a code change
   with no test). Only a project that has *actually run* `rulecheck --align`
   at least once is checked — pointing at `CLAUDE-workflow.md` from a
   `CLAUDE.md` alone does not count, so a project that never opted in is never
   blocked. `common-rules` itself was already structurally exempt (it refuses
   to land at all, always, before this check would ever run). The refusal
   names both versions and the exact commands, including the gotcha that
   `rulecheck --align` writes `.common-rules-version` but does not commit it.
   Escape hatch, same shape as `LAND_ALLOW_UNTESTED`: `LAND_ALLOW_STALE_RULES=1`,
   recorded in the PR either way. `tests/test_land_alignment.py` covers all
   four cases (no stamp, aligned, stale, override) and was run against the
   unguarded script first — it failed on the stale and override cases exactly
   as expected.

**Behaviour change for three projects that are not the current focus:**
`mac-explorer`, `pockets` and `pip` cannot land through `bin/land` until
someone runs `rulecheck` and `rulecheck --align` in each — that is the point,
but it stops real work in those projects until it happens, so it is called out
here rather than left to be discovered as a landing failure.

`docs/workflow.html` updated with this change, stamp at 155, PNG regenerated —
required by the same rule this PR is now stating explicitly in
`CLAUDE-workflow.md`.


## 2026-08-16 · land died silently on any commit that named no issue

Reported by a finance-tracker session that hit it twice in one night: `land`
printed `tests green` and then stopped. No error, no message, never reaching the
push or the PR. Every branch whose commit message is plain description rather
than `Fixes #N` hit it — which is most of them.

`grep` exits 1 when it matches nothing, and no-issue is the *common* case. Under
`set -euo pipefail` that failed the pipeline inside `closes_trailer`, which
failed the `closes="$(…)"` assignment, which killed the script. `|| true` at the
end of the pipeline fixes it: **no match is an answer, not a failure.**

**The reported cause was wrong, and it matters.** The report named the following
line, `[ -n "$closes" ] && body=…`, on the theory that a failing test under
`set -e` kills the script. Bash exempts a failing command in a `&&` list, and a
minimal repro of that line exits 0 — verified before changing anything. Applying
the suggested fix would have left the bug in place while looking like it had
worked. The symptom was reported exactly right; the diagnosis was one line off.

`tests/test_land_closes_trailer.py` covers it, and was run against the unfixed
script first: 3 of 5 failed. It calls the function under land's own
`set -euo pipefail`, because without those flags the failing pipeline is
harmless and the bug is invisible.

**Why the existing land tests missed it:** every one of them drives
`land --check`, which returns before this code runs. A guard that only exercises
the early-exit path proves nothing about the rest.

## 2026-08-16 · Proposals carry their number and status in the title

The sponsor asked for a rule after receiving two unnumbered proposals in one
session and having no way to tell where they sat in the sequence — or whether
either had been decided.

`finance-tracker` already numbered its proposals (`docs/proposals/NN-...`,
eighteen of them, with status tracked in a `<meta>` tag and rendered into a
generated index). The convention existed and worked; it simply was not written
down anywhere shared, so a session working from `common-rules` alone had no way
to know it applied. This records it.

**The rule**: `docs/proposals/NN-<type>-<slug>.html`, numbered sequentially per
project and never reused, with the visible heading and the `<title>` both
reading `NN · status · Title`.

**Behaviour change for adopted projects**: yes, but only for new proposals.
`finance-tracker`'s existing eighteen already satisfy the file-naming half; what
changes is that the number and status must now also appear in the visible
heading and `<title>`, which most of them do not do yet. Nothing needs
retro-fitting — the index at `docs/proposals/README.md` already derives status
correctly from the `<meta>` tag, and that mechanism is unchanged.

Added to "Talking to the user" beside "Show, don't summarise", where the
artifact rule already lives.

`docs/workflow.html` carries it too, with the stamp at 153 and the page regenerated — required by the rule that any PR changing the shared rules updates the bird's-eye view in the same PR. `tests/test_workflow_stamp.py` refused this branch until it did, which is the first time that guard has caught anything but its own author.

## 2026-08-10 · The probe you ran is the test, and CI runs what land runs

Three changes so a test written once is enforced everywhere, and so the
verification sessions already do stops being thrown away.

**1 · This repo has CI.** It had 128 tests and no workflow, which is how `main`
stayed red from 8 to 10 August while four merges landed on top of it. The new
`.github/workflows/ci.yml` runs on push and pull request. Its command is
byte-identical to what `bin/land`'s `test_cmd()` emits, and
`tests/test_ci_matches_land.py` fails if the two ever drift — it sources the
function rather than parsing the file, so a changed `if` branch cannot slip past.

**2 · One command, written down.** `tests/` plus
`python3 -m unittest discover -s tests -q`, in `CLAUDE-workflow.md`. Both land
and CI use it, so a test an agent writes reaches CI with no wiring.

**3 · `bin/land` refuses a branch that changes code and touches no test.**
Measured the same day: **29% of every Bash call a session makes is a one-off
verification probe** — 3,873 inline scripts that proved something and died with
the session, against 106 from all eight agent roles combined. The proving is
already happening and the code is already written; only the destination is
wrong. Docs, HTML and config do not trip it. `LAND_ALLOW_UNTESTED=1` overrides
it deliberately.

`code-engineer`, `test-engineer` and `quality-manager` each gain a short section
pointing at the rule. The other five roles never touch tests and are unchanged.
`test-engineer` holds no `Write` tool by design, so its section asks it to spell
out the test that should exist — file, case and failing assertion — rather than
describe a defect in prose that someone must re-derive.

**Behaviour change for adopted projects:** `bin/land` will now refuse a
code-only branch. Expect it on the first tooling change after this lands.

Note on what this exposes: `main` is red as of this entry (`test_tower_render`,
handed to the session holding `bin/tower`, and tracked in #99). Adding CI makes
that visible on every push rather than only to whoever thinks to run the suite.
That is the intent, not a side effect.

## 2026-08-10 · `land` says which issue a PR closes, so the issue doesn't outlive its fix

Found while landing finance-tracker's issue #362. The fix merged, and the
issue stayed open — because `bin/land` wrote a **fixed** PR body ("Landed by
`common-rules/bin/land`: N commit(s), tests green…") with no `Closes #N` in
it. finance-tracker's `CLAUDE.md` has carried the rule for a while — *"a PR
that finishes one says `Closes #N` in the body, not just the title, or the
issue silently outlives its fix (that habit gap left four finished issues
open on 2026-08-07 alone)"* — but the tool every session is told to land
with could not follow it. A rule the tooling structurally cannot obey is not
a rule; it is a reminder to be human about, which is how four issues stayed
open in a day.

`closes_trailer()` now reads the branch's own commit subjects **and bodies**
(`main..$branch`, `%s%n%b`) and appends one `Closes #N` line per issue named.

**What it deliberately does not match is the point.** Only an explicit intent
word counts — `issue #N`, `fixes #N`, `closes #N`, `resolves #N`. A bare
`(#N)` is ignored, because the entry directly above this one measured what
that trailing number actually is on the repos consuming these rules: usually
the **PR** number, on a range that overlaps the issue numbers, so keying on
it would close an unrelated issue roughly six times out of seven. Same
principle as `worktree_issue()` — *no match means unlinked, not guessed* —
and the same reason the coupling graph refused the grep approach. A landed PR
that names nothing simply carries no trailer, exactly as before.

**A second wrong-issue trap, found by running the new code against its own
branch.** A commit legitimately cites *another repo's* issue — this very
change's commit explains itself by naming finance-tracker's issue #362 — and
the first version of this happily emitted `Closes #362` into a common-rules
PR, where #362 is a different and unrelated issue. Same failure class as the
bare `(#N)`, arrived at from the other direction. `issue_here()` now filters
every candidate through `gh issue view` against the *current* repo before it
is written; without `gh` there is no way to check, so nothing is claimed.
On this branch the trailer is correctly empty.

**Behaviour change for adopted projects** (finance-tracker, pockets): a
branch whose commits say `issue #N`, where #N resolves in that project's own
tracker, now closes #N automatically on merge. Nothing else about `land`
moves — same refusal conditions, same squash, same output. A branch that
names no issue behaves identically to today.

`tests/test_land.py` is new (8 tests) and pins both directions, including
`"Add shared test-support modules (#389)"` → no trailer. It extracts the
real function out of `bin/land` rather than copying the regex, since the
script runs `land_one` at import and so cannot simply be sourced — a copied
regex would only ever test the copy. One test asserts the helper is actually
*called*: a `closes_trailer()` nothing wired up would pass every other test
and still leave every issue open, which is the exact bug being fixed.

Pre-existing and untouched: 4 `test_tower_render` failures on `main`
(`bin/tower` is being rewritten on `rulecheck-adoption`), plus a stray
untracked `.common-rules-version` stamp in this repo dated 2026-08-08
(`144-008c5cc`) that fails `test_common_rules_never_acquires_a_stamp`.
Neither is related to this change.
## 2026-08-10 · `test_tower_render` was red for two days; `velocity()` had a real bug in it

Handed over from another session: `origin/main` had been red on
`test_tower_render` since 08-08, worsening across four separate merges,
because `bin/land`'s red-suite guard was being routed around by direct
`gh pr merge`. Diagnosed and fixed rather than reverting anything —
every failure traced to an intentional change from this session, and
three of the four were stale test fixtures. The fourth was not.

**`velocity()`'s window fallback had a real, dormant defect.**
`window = [p for p in points if p[0] >= cutoff] or points[-2:]` only
falls back to the last two points when the filtered window is *empty* —
not when it has exactly one point. When one point survives the cutoff,
`window[-1]` and `window[0]` are the same element, so the reported
movement is silently **0** even when real progress happened just before
the cutoff. It was dormant because it takes wall-clock time actually
passing to trigger: a fixture dated 08-02/08-07 read correctly right up
until today (08-10) pushed the 08-02 point outside the 7-day window,
leaving only 08-07 to diff against itself. Fixed by falling back
whenever the window has fewer than two points, not only when it's empty.

The other three: two test fixtures built their own `data` dict by hand
rather than through `collect()` and were missing the `"coupling"` key
COUPLING's own commits added — `render_project` now reads it
unconditionally, so a hand-built fixture that skipped it raised
`KeyError` rather than silently passing. Added. The fourth asserted the
literal string "enough checklist history", which this session's
REPORT/PROGRESS merge deliberately reworded to "enough history" (the
message now covers both the GitHub-sourced and checklist-fallback
paths, not just the latter) — the assertion was stale, not the code.

Also found and cleared: a stray, untracked `.common-rules-version` in
this repo's own root, a side effect of running `bin/tower` locally
during today's testing, was independently failing
`test_common_rules_never_acquires_a_stamp`. Removed; not committed to
begin with.

`test_rulecheck.py` still fails three cases
(`RealProjectsStillCheck.test_the_adopting_projects_are_still_recognised`
for pockets/pip/mac-explorer) — a different tool's surface
(`bin/rulecheck`, not `bin/tower`), checking real live project state
unrelated to anything touched here. Left for whoever holds that surface,
per the handover's own principle.

## 2026-08-10 · Coupling rolls up to feature level, from GitHub's own linkage

Asked directly, after reviewing finance-tracker's real feature register: does
COUPLING actually make feature-level tracking better, and can it consolidate
to the feature? As shipped it couldn't — the graph was file-level only, with
nothing connecting a coupled pair back to which feature owns that risk.

**The obvious approach — grep commit messages for `#N` and match against a
feature's cited issues — was measured and rejected before writing it.** Only
13% of finance-tracker's commits carry an unambiguous `issue #N` reference;
the rest end in a bare `(#N)` that's the PR number, not necessarily the
issue, and PR numbers there (49–373) directly overlap the range feature
issues live in (#3–#257). Text-matching would misattribute roughly six times
out of seven — worse than not building it, and exactly the "confident wrong
answer" this codebase already refuses elsewhere (`worktree_issue()`: *"no
match means ungrouped, not guessed"*).

**`feature_touched_files()` uses GitHub's own linkage instead**:
`gh issue view --json closedByPullRequestsReferences` finds the real PR that
closed an implementing issue, `gh pr view --json files` gets its actual
touched-file list. Real data, not a guess — parallelized across a feature's
closed issues (`fan_out`), and across projects in `_coupling_now`.

**Honest finding once it ran for real: coverage is sparse.** Only 25 of 131
closed issues (19%) in finance-tracker's tracker were closed via a properly
linked PR. Of the register's 10 features, only one — #254, Spending — had
enough linked closures to attribute any files at all. `render_coupling` says
this plainly rather than rendering a quietly-empty section: *"no declared
feature has a closed issue with a linked PR yet."*

**What the 19% that did work found**: feature #254's own files are
internally coupled — `projections.py ↔ test_projections.py` (6),
`flows.py ↔ test_flows.py` (5) — a real, feature-scoped signal
(`feature_coupling_summary`), not file-level noise. The other nine features
show nothing, correctly, because there's nothing to attribute them from yet.

## 2026-08-08 · A coupling graph, read straight from git (proposal 14)

Asked directly for "git analytics" and "graph analytics" for finance-tracker.
REPORT and PROGRESS already answer *how much, how fast*; neither says where
the risk concentrates — which files a change to one thing has, historically,
dragged along with it. That's a graph question, and it's now on every
project's page as **COUPLING**, below PROGRESS.

Built from a plain `git log --name-only` walk, all-time (a structural
question, not a this-week one, per the proposal): every pair of files touched
by the same commit gets a weighted edge. Two noise corrections, one proposed
in advance and one found while building. Proposed: a commit touching more
than 18 files (a mass reformat) is skipped outright rather than contributing
`n·(n-1)/2` near-meaningless edges from one event. Found live against
finance-tracker's real history: several commits touch 11–13 files under
`docs/proposals/` at once — an index or README regenerated alongside the doc
it lists — all under the 18-file cap, and they filled **21 of the top 28
edges** with documentation cross-links before `docs/` was excluded wholesale.
Caught by inspecting the first real graph before wiring it into the page, not
by assuming the collector was right because it ran without error.

The layout itself is a hand-written Fruchterman-Reingold spring embedder —
`math` and `random` only, no `networkx`, no `numpy`, per this repo's own
stdlib-only rule for the Tower — seeded deterministically so the graph
doesn't visibly rearrange itself on every 10-second auto-refresh. Computed
once per 40-minute window (`GRAPH_TTL`, alongside `HISTORY_TTL`/`COST_TTL`)
and cached, never recomputed on a request.

What it found on finance-tracker, once the doc noise was gone: `main.py`,
`theme.py`, `session.py`, `pages/ledger.py` and `reports.py` co-change 7–15
times with each other — five files that read as separate hotspots by churn
count alone turn out to function as one unit. `money.py`, the actual currency
arithmetic, sits apart from the cluster entirely.

## 2026-08-08 · REPORT loses its own chart, gains PROGRESS as a neighbor

Looked at the REPORT tab just shipped and it had three problems, not one:
its own burnup chart rendered as a bare, unlabelled line stretched across
the full width with no gridlines or dates -- it read as broken, not as a
chart. It also duplicated the existing PROGRESS chart lower on the same
page, same project, same data, two different treatments of one story. And
the project header above it still printed checklist-item completion
(`24/58 items · 41%`) right next to REPORT's feature-register completion
(`9%`) -- the same two-numbers-disagree failure the previous entry fixed
for DONE vs 7-DAY, reintroduced one section up.

Fix was subtraction, not more chart code: REPORT dropped its own sparkline
entirely, PROGRESS moved up to sit directly under REPORT's counters instead
of after BOARD, and the header's checklist-items figure now only prints
when a project has no feature register to compute REPORT's number from.
One burnup chart per project page, one completion percentage, and it is the
one with gridlines, date labels, and a note explaining what moved.

## 2026-08-08 · 7-DAY reads GitHub now, and REPORT is a live tab

Asked directly: *"why do you measure checklist, why can't you use git to
measure progress"* — and separately, that the one-off narrative completion
reports written for a few projects should be "in the app... tracked live."

**7-DAY was still checklist ticks after DONE moved off them.** The previous
entry fixed the DONE bar to score feature completion from issue closures, but
PROGRESS's 7-DAY figure kept reading the git log of hand-ticked `- [x]` boxes
in `CLAUDE-checklist.md` — a session could tick a box with no issue behind it,
or close an issue and never touch the checklist, and the two numbers on the
same screen told different stories about the same project. `7-DAY` now builds
its burnup from the register's own implementing issues' `closedAt`: the same
denominator `project_completion` already scores DONE from, so the two cannot
drift apart. A project whose register has no closed implementing issue yet
still falls back to the checklist history — labelled `checklist` on screen,
never blended silently with GitHub-sourced numbers.

**REPORT is a new section on every project's page**, sitting above BOARD:
completion %, features closed, features naming an issue, issues open, issues
closed in the last 7 days (with an unclaimed-issues callout), velocity, and
weekly token cost, plus the burnup chart. It costs no new fetches — every
figure is a rollup of what BOARD and PROGRESS already collect — so it
refreshes on the same cadence as the rest of the screen.

What it deliberately does not do: the narrative half of those one-off reports
(a wrong metric caught, dead code found, a missing test named) came from a
session actually reading code. That is investigation, not a query, and
nothing in a 5-second collector can re-run it unattended. REPORT says so in
its own footer rather than implying it replaces the written reports — those
stay as the historical record; REPORT is the thing that stays current.

## 2026-08-08 · The bar follows features now, and unclaimed closures are visible

Reported: *"in financial tracker i am closing issue, but the progress bar does
not increase."* Two separate causes, and fixing only one would not have
satisfied the report.

**The bar showed checklist ticks.** Closing a GitHub issue moves a feature's
percentage and never ticks a `- [x]` box in `CLAUDE-checklist.md`, so the most
prominent number on the row measured something the sponsor was not doing. It
now shows feature completion — the same arithmetic `whole_product` uses across
the estate, computed once in `project_completion` so the two cannot drift apart.
Checklist ticks remain the fallback for a project with no register, labelled
`% items` so it is never read as the same number.

**Measured before fixing anything**, because a bar reading the right thing
would still barely move: **18 issues closed on finance-tracker in a day, and 17
of them belong to no declared feature.** Only #127 was inside the register.
That is why the bar moved to 1% and stayed there — it was correct, and silent
about almost everything that happened.

So the estate view now says how much work the register does not cover:
`44 issue(s) closed in the last 7 days that no declared feature claims`. Neither
this proposal nor this fix decides whether those 44 belong inside a feature or
are legitimately excluded housekeeping — that is the sponsor's call, per
`CLAUDE-workflow.md`, and it could not be made while the number was invisible.

One test guards the render path specifically, not just the arithmetic: the unit
test on `project_completion` passed even when the bar was reverted to checklist
ticks, because nothing forced `render_all`'s actual HTML to use it. A second test
against the rendered output catches that regression — verified red before the
fix, green after.

## 2026-08-08 · Cap the strip, not the table

The previous fix capped `.cell.wide` to stop the sessions strip crowding out the
estate table. Both regions are wide, so it capped the table as well — the ALL
view then rendered **3 of 6 projects above a large empty gap**, which is worse
than the inverted priority it was meant to fix.

A CSS selector matching more than intended fails silently and looks like a
layout decision. The strip now carries its own class, and a test asserts the
bare `.cell.wide` rule constrains no height — verified by putting the over-broad
cap back and watching it go red.

Third fix in a row on the same screen, and the third one that only a screenshot
could have caught.

## 2026-08-08 · Fits the window it actually ships in

Opening the app — properly, at its real size, for the first time — showed three
more defects that every check I had run was blind to. The window is roughly
1180x760 of content; I had designed and verified everything at 1280x900.

**The estate table rendered 3 of 6 projects.** The sessions strip took ~240px
while the table showing every project got ~80px, so mac-explorer, pip and
pockets were simply not on screen — on the view whose entire job is "which app
is stuck". The priority was exactly inverted: the strip is a footnote and was
being treated as content. It is capped now and the table gets what is left.

**The header said `NEEDS YOU · 8` above five rows**, because drift was still
counted per project after being consolidated into one line. A header that
disagrees with the thing directly under it is worse than no header: it makes the
reader distrust both, which is roughly what "I don't know what to do" sounds
like.

**A band row was sliced mid-word** — "worst is pip at 34" cut in half at the
cap. Smaller cap.

None of this was visible to `curl`, to the test suite, or to rendering the same
HTML at a size the app never uses. The only thing that found it was looking at
the window.

## 2026-08-08 · The screen was working and useless, which is not the same thing

the sponsor: *"this app doesnt work. i dont know what to do."*

I had verified every change with `curl` and never once opened the window. It
renders fine. It is also useless, in three specific ways, all of which I built.

**The headline read `0% of declared scope`** while four features were declared
**done**. Completion came only from closed implementing issues, and a `built`
feature names none — the work predates the register. Proposal 05 already settles
this: the sponsor closes features and his State column is the authority. It now
reads **13%**. This was the first number on the screen and the one he asked for
by name.

**The NEEDS YOU band held 8 items, of which 1 was a decision.** The rest were
rules-drift rows and contested notes. Worse, the drift was largely
self-inflicted: every merge to common-rules bumps the version, so a day of work
in this repo pushed every project 28–31 versions behind and the band filled with
nagging about a number I had moved. #75 capped it at two rows plus a count,
which was not nearly enough. Drift is a *state*, the header already carries it,
and one line here says how bad it is and what to run.

That is the second time this exact failure has been built and the second time it
had to be measured on a live screen to be seen — a signal that never resolves
becomes wallpaper, and I keep re-creating it one level up.

**A footnote was being sliced in half** by the scrolling region's boundary,
which reads as a rendering fault. It also cited a closed issue number, which is
developer chatter on the sponsor's screen. Shortened.

The lesson is not any of the three fixes. It is that "the tests pass and curl
returns 200" answered a different question from "is this screen any use", and I
reported the first as though it settled the second, repeatedly, for a day.

## 2026-08-07 · rulecheck reads whether a project adopts the rules instead of assuming it (#61)

`bin/rulecheck` treated every directory under `apps/` as a project that follows
these rules. `idea-lab` does not, and says so in its own words: it is **v2**,
governing what happens *before* anything is agreed, and `LAB-RULES.md` opens
with "deliberately separate from `../common-rules/`" while `CLAUDE.md` adds
"no gates, no worktrees, no issues here — ideas are cheap on purpose."

So rulecheck reported `idea-lab has NEVER recorded a rules version` and would
have gone on reporting it forever. Two costs, and the second is the one that
matters:

- **Every session had to re-derive that it was a false alarm** and dismiss it.
  A permanent warning that is always wrong trains sessions to skim the warnings
  that are right.
- **The only remedy it offered was `--align`, which would have written a false
  record.** The stamp is load-bearing *because* it is trusted without
  re-checking — the next session inherits it and skips reading the rules. A
  wrong stamp is therefore worse than a missing one, and `--align` on a
  non-adopting project now refuses and says why rather than complying.

**Adoption is read from the declaration that already exists.** `README.md`,
"How a project adopts this", says a project adopts by adding a pointer to
`CLAUDE-workflow.md` near the top of its own `CLAUDE.md`. That pointer is now
the check. Deriving it means there is no second roster to drift — and drift is
not hypothetical: `CLAUDE-workflow.md:7` still reads "Adopted: **finance-tracker**
(2026-08-02), **pockets** (2026-08-02)" after `pip` and `mac-explorer` had also
adopted. A hand-maintained list of who follows the rules had already stopped
being true. *(Left alone in this PR — that line is prose in the rules file and
changing it is the user's call, not a side effect of a tool fix. Flagged in the
PR body.)*

Mentioning `common-rules` is deliberately **not** enough to count. idea-lab's
CLAUDE.md names it in order to disown it; a substring match on the folder name
would have kept the false alarm exactly as it was.

Two cases the naive version got wrong and this one does not:

- **An existing stamp counts as adoption on its own.** Rewording a project's
  CLAUDE.md must not silently un-adopt a project that has aligned before.
- **common-rules does not adopt itself.** Running rulecheck inside this repo —
  the usual way this was hit — reported the rules as never having recorded a
  version *of themselves*. It now says so plainly and exits 0.

`tests/test_rulecheck.py` covers all of it: the idea-lab case, `--align`
refusing to write the stamp (asserted on the filesystem, not on the message),
the stamp-implies-adoption rule, `--quiet` staying silent for a non-adopter so
the SessionStart hook does not print, common-rules never acquiring a stamp, and
a guard that the four real adopting projects are still checked — so a fix that
quietly stops checking everything fails the suite.

Exit codes now read: 0 aligned **or not an adopting project** · 1 behind · 2
cannot tell.
## 2026-08-07 · A feature stops being counted as a ticket too

Implements #93, reported as the feature and issue lists being inconsistent —
which they were, because the same thing was in both.

A feature **is** a GitHub issue; that is how the register identifies it. So every
declared feature also appeared in the pipeline's queued list. Measured: **32 of
103 open issues were features**, and `QUEUED` read **95** when the real queue was
63. Per project it was every single one — 9 of 9, 9 of 9, 7 of 7, 7 of 7.

`pipeline_data` now excludes them from queued, merged and the in-flight mapping.
`QUEUED` reads 64 (not 63 — filing #93 itself added one, which is the count
moving correctly).

This is the defect proposal 10 removed once already, arriving from the other
direction. `IN FLIGHT · 19` counted eighteen git ahead-counts as work; this
counted features as tickets. **A feature is not a ticket to work — it is the
thing tickets roll up into**, and listing it as queued invites picking it up as
one.

The exclusion depends on `collect()` computing features *before* the pipeline, so
the keys exist to pass in. That ordering is load-bearing and invisible, so a test
reads the source and asserts it — verified by swapping the order and watching it
go red. Swapped back silently, nothing else would fail: the queue would just
quietly grow by 32 again.

## 2026-08-07 · The register is read from main, not from whatever the checkout is parked on

Implements #91. All four registers were merged; the Tower reported three.

pip's register was on `origin/main` while its working checkout sat a commit
behind, with another session mid-work in it. `feature_data` read
`proj["path"]/CLAUDE-checklist.md` — the working file — saw no table, and
reported **"no features declared"** for a project that had declared nine.

**A feature is declared when its register is merged.** Whether a particular
working copy has pulled is an accident of who is working where, and the answer
to "what is this product made of" must not move because of it. Same class of
defect as #73: an answer that quietly depends on local state it does not
mention.

`origin/main` first, then `main`, then the working file. The order matters and
is commented, because a *local* main can itself be behind — which is exactly the
case that produced this. The working file is a last resort rather than an error:
degrading to *less* scope than exists is the failure mode here, so an
unreachable remote must not drop a project to zero.

Reading from git also means an uncommitted register edit does not count yet.
That is correct rather than unfortunate, and it matches the rule the State
column already follows.

The estate now reports **32 features in 4 of 6 projects**, with pip's checkout
untouched — the overlap rule says do not reach into a surface another session
is holding, and fixing the Tower was the better answer than fixing their
checkout.

**One inconsistency is left open deliberately.** `checklist_progress` — item
counts, and so the burnup — still reads the working file, so a project can now
show features from `main` and item counts from a checkout that is behind.
Aligning them would make declared scope wholly a merged fact; leaving items on
the working tree keeps them a live signal of what a session is doing. That
changes what the burnup measures, so it is recorded on #91 for the sponsor
rather than decided in passing.

## 2026-08-07 · workflow.html catches up with the feature-register rule

#88 changed `CLAUDE-workflow.md` and did not update `docs/workflow.html` in the
same PR, which is exactly what `docs/README.md` requires and what
`tests/test_workflow_stamp.py` exists to enforce. **It merged red**: the stamp
said version 104 against rules at 130.

That test was written this morning, in this repo, for this failure mode — and
the rule it protects was still broken by the next rules change, by me, hours
later. The test did its job; the process around it did not, because the PR was
merged without the suite being run against the merge result rather than against
the branch.

The page now describes the register rule and is stamped 130.

## 2026-08-07 · Every project keeps a feature register, and the board stops losing features

Two things, found together because landing the first real registers is what
exposed the second.

**The rule.** `CLAUDE-workflow.md` now requires a `## Features` table in every
project's `CLAUDE-checklist.md`, in the shape pockets already used and the Tower
already parses. It is the only answer to "what is this product made of, and how
much of it is done" — a question the sponsor asked by name and which the estate
could answer for one project in six.

Worth being explicit about the tension, because it looks like a rule that was
already refused: **this is not proposal 08's logbook.** That was rejected for
imposing a per-task append on every session. A register changes when the sponsor
adds, renames or closes a feature — rare, and his act rather than a session's.
Nothing here asks a session to write anything when work lands. A project with no
register still reports "no features declared", never 0%.

**The bug.** Landing the registers immediately showed the board undercounting:
pockets declares **7** features and the board rendered **6**. The `version 2` one
parsed as kind `later`, there was no LATER column, and the grouping dropped it —
silently, since #70 merged. Any state the parser produced without a matching
column disappeared the same way, and a state the register did not spell out fell
through to `declared`, which had no column either.

There is now a LATER column, an unstated state parses as `next` rather than into
nothing, and an unrecognised state is parked in NEXT rather than lost — a
register can be hand-edited, so an unexpected value is something to correct, not
a reason for a feature to stop existing. Verified across all four registers:
7 + 9 + 9 + 7 declared, 32 rendered.

A quiet undercount is worse than a wrong column: the board is meant to answer
what the product is made of, and an undercount makes it a wrong answer that
looks right. The guard is verified by removing the LATER column and watching it
go red.

## 2026-08-07 · The heavy collectors stop blocking the first page too

Follow-on to #86, found by merging #76's cost work into it and measuring the
combination rather than assuming the two composed.

#86 stopped a render waiting for a *recollect*, but the **first** render is
deliberately synchronous — a page with no data is worse than a slow first page.
With cost added, that first page took **57 seconds**. The app looked hung on
launch, which is a worse defect than the one #86 fixed.

So the three collectors with their own long TTLs — `staleness` (fetches),
`history_data` and `cost_data` (walk git and every transcript, 26.8s cold) —
now go through `cached_async`: return whatever is cached immediately, refresh in
the background. They return None on the very first call, which every one of
their renderers already treats as absence: no staleness line, no history yet, no
cost note.

Cold first page: **57s → 5.2s**. Warm: ~2ms. History appears at ~24s, cost at
~56s, and the window is responsive the whole time. A region arriving a few
seconds late is far better than a window that will not open.

Their private cache blocks were removed rather than left alongside — two caches
over one value is how a number ends up stale in a way nobody can reproduce.

One test failure here was the test's fault, not the code's: the single-refresh
assertion saw two because the previous test's background thread was still alive.
Fixed with a release event and a join in `tearDown`, since a test that fails
from its own leftovers teaches the next person to distrust the suite.

## 2026-08-07 · Cost is per week, because per feature attributes nothing

Implements #76, rescoped by measurement rather than by preference.

**Per feature attributes 0%.** Measured across the estate: of 67,393,007 tokens,
**96.8%** sit in `(main checkout)` and `(management)` pseudo-tasks and **3.1%**
in worktrees that have since been deleted. Zero was attributable to a declared
feature. Two structural reasons, neither fixable in the Tower: most work never
happens in a task worktree at all, and the ones that do have their key —
the worktree directory — destroyed by the act of landing. Built as originally
specified, #76 would have shipped a column of dashes and a footer holding all
the spend. That was reported before writing any of it.

So the unit is the week. **"What did this week cost, and what moved"** sits on
one line of the PROGRESS section beside the burnup, and a 7-DAY COST column on
`ALL` makes it comparable across projects. On the live estate that immediately
reads: finance-tracker **27.6M tokens for +14 items**, common-rules **18.2M**
against no checklist to move at all.

**`spend` now carries per-day tokens through `tasks_for`.** `_read` already
counted them and the aggregation dropped them. This matters more than it looks:
summing whole task totals for tasks that merely *touch* the window overstates
the estate's week by **4,492,100 tokens — 7.1%** — because a task spanning the
boundary gets counted entire. That is a wrong answer rather than a rounded one,
and it was measured by building the tempting version and comparing.

A test asserts **no cost appears against any individual feature**, which is the
number the data cannot support and therefore the one most likely to be added
back by someone who has not seen the 0%.
## 2026-08-07 · A render never waits for a collection

Implements #86, reported by the sponsor as *"this app is slow and time
non-responsive. it also shows outdated data."*

**The slowness was real and reproducible.** Measured against the running app:
every recollect blocked the HTTP response for **~4 seconds**, and with a 5s
cache against a 10s auto-refresh that meant the window froze for four seconds
out of every ten.

**The "outdated data" was not.** Checked against ground truth, the rules stamp,
the decision count and the absent staleness line were all correct. What was
wrong was *lateness*: the visible page ran up to 14s behind because each refresh
took 4s to arrive. It read as stale because it was late — a useful distinction,
because the fix for one is not the fix for the other.

`collect()` now serves the cached snapshot immediately and refreshes in a
background thread, one at a time. Requests went from ~4s every other hit to
**~2ms**, warm or cold. The first render still waits, deliberately: a page with
no data at all is worse than a slow first page.

The cost of not blocking is that a snapshot can be a cycle old, so **the page
now states its own age** — `data is current` or `data is 9s old · refreshing in
the background`. A number whose age is visible is honest; a number that is
silently late is the thing that was reported.

**A far worse defect turned up while measuring.** In the unmerged #76 branch,
`cost_data` declared `COST_TTL`, `_cost_lock` and `_cost` and never referenced
them, so it rescanned every transcript on every 5-second collect. Cold, that
call takes **26.8 seconds**. It would have shipped with #85 and made the app
close to unusable. Fixed on that branch, and it is the honest argument for
measuring rather than reviewing: nothing about reading the code made it obvious,
and the app being slow is what led to it.

The no-blocking guarantee is pinned by tests, verified by reinjecting the old
inline collect and watching them go red — including one asserting only a single
background refresh runs at a time, since otherwise a slow sweep spawns a thread
per request and does the same expensive work many times over.

## 2026-08-07 · The Tower switches by project

Implements #81. The tab bar is the project list now — `ALL · pockets ·
finance-tracker · …` — and a project page carries everything about that app at
once: its features by state, its burnup and velocity, its queued and merged
work, its sessions. No second click, no filtering by eye.

**The lenses are retired rather than re-cut.** BOARD / LEDGER / PROGRESS
answered a real constraint — six projects' data does not fit in 900px. One
project's does, so changing the axis removes the need for the split entirely.
`render_ledger` is deleted with them: a cross-project feature table is exactly
what a project-first screen does not want.

**NEEDS YOU stays above the tabs and is never filtered**, and that is enforced
rather than intended: `render_needs_you` takes no project argument, so it cannot
be filtered by construction. A decision waiting in an app the sponsor is not
looking at must still reach him, and filtering the band is the tempting
simplification that would make the screen actively worse. Verified by
reinjection — adding a `project` parameter turns the guard red.

**The whole-product figure moved from the retired LEDGER to `ALL`.** A statement
about every project cannot sit on a page showing one.

`?project=` is URL-borne for the reason `?view=` was: the page re-requests
itself every 10s and DOM state does not survive it. Verified in a browser again
here — the stamp advanced 20:33:36 → 20:34:21 through a real reload with pockets
still selected.

Two things worth recording about the build. Deleting `render_ledger` also took
`sparkline` with it, because that function sat between it and `render_progress`
— caught by the tests immediately, restored from main, and a reminder that
cutting by line range between two named functions is only safe if nothing has
been inserted between them since.

And the screen reported on itself mid-build: the staleness line from #73 read
*"running 55cbe16 · main is 4 ahead"* while another session's spend work landed.
That is exactly what #73 was for, and it prompted the merge before this was
committed rather than a conflict at PR time.

## 2026-08-07

- **`spend` was hiding 88% of what it measured, and now counts management
  separately.** Reported as "pockets shows zero tasks"; the cause was much
  wider. Attribution read the **first** `cwd` in a transcript — the launch
  directory — and a management session launches from `apps/` and only enters a
  project later via `EnterWorktree`. Every one of them was therefore dropped
  from every project. `spend today` had been saying management chats are 88% of
  all spend the whole time; the per-project figures simply excluded them.
  Measured: pockets reported **0 tasks** on a day it spent 836k output tokens
  across four agents; finance-tracker reported **4M** against a real **31.7M**.

  Two fixes were tried and rejected before this one, and both are recorded
  because the reasoning matters more than the patch. *Any cwd inside the
  project* counts a one-line `cd` in a bash command as a session's work — it
  put five sessions in two projects at once. *The dominant cwd* stops the
  double-counting but silently loses a task, because a session that spent more
  records elsewhere stops being that task at all.

  The accepted split is the sponsor's call: **task rows measure worktree
  sessions only, and orchestration gets its own row.** A session that spent all
  its time in exactly one worktree is that task; one that never left the main
  checkout stays `(main checkout)` as before; one that moved between worktrees
  is `(management)`. The point is that no single label is honest for a session
  that legitimately spans ten worktrees — charging it to one over-claims that
  task and hides nine others.

  What this does not do: split a management session's cost across the tasks it
  served. That would make every task row a fraction with no session behind it,
  and it was rejected for the same reason the hand-written log was — a number
  nobody can trace is not a measurement. Management cost is now visible and
  attributed to a project; which task inside it consumed what is still unknown.
## 2026-08-07 · The Tower switches by project, not by lens

Proposal 13, from the sponsor looking at what had just been built: *"rather than
switching board, ledger and progress, I should be able to switch between
projects with all details."*

He is right, and the interesting part is why the lenses existed at all. BOARD /
LEDGER / PROGRESS answered a real constraint — six projects' features, history
and flow do not fit in 900px, so the estate view had to be cut three ways. But
**one project's data fits easily**: the largest is pockets at 7 features, 6
sessions and 9 history points; finance-tracker is 3 sessions and 21 history
points. Change the axis to project and the split stops being necessary at all,
rather than needing re-cutting per project. The lenses were the answer to a
volume problem that disappears when the question changes from "show me a way of
looking" to "show me one app".

So the tab bar becomes the project list, a project page composes everything that
already exists filtered to one app, and `ALL` becomes a one-line-per-project
estate summary.

**NEEDS YOU stays above the tabs and is never filtered.** It is the autopilot's
blocking state: a decision waiting in an app the sponsor is not currently
looking at must still reach him, and filtering it is the one change that would
make the screen actively worse rather than better.

Worth recording plainly: the `ALL` page is almost exactly the **Portfolio**
option from proposal 11 — the one recommended then and turned down in favour of
Ledger and Board. That recommendation was wrong *at the time*: as the only view
it hid individual features behind an expand, and with one register declared it
had nothing to compare. As a summary above per-project pages it is the right
shape, because comparison is what a top level is for. Rejecting it as the answer
and adopting it as the roof are both correct, a day apart.

The costs are stated in the document rather than discovered later: the
cross-project feature table goes, "everything blocked anywhere" becomes six tab
visits, and the tab bar grows with the estate — six fit, twelve would need
grouping.

Cut as #81. #76 (cost per feature) was unblocked by #78 the same hour and
immediately re-queued behind #81, because cost is a column on a feature list and
#81 moves where that list lives.

## 2026-08-07 · spend can be asked about a project by path

Implements #78, which exists only to unblock #76 (cost per feature on the
Tower).

`bin/spend` measured everything through `_tasks_here()`, which derived the repo
root from the **current working directory** and took no path. The Tower cannot
use that: its collectors run in a thread pool, and a process-global `chdir`
there is the kind of race that produces a wrong number occasionally rather than
an obvious failure — the worst way for a cost figure to be wrong.

So `_repo_root()` takes an optional path, `tasks_for(path=None)` is the public
form, and `_tasks_here()` is now a thin wrapper over it. **An access change, not
a measurement one**: task grouping, token counting and the CLI are untouched.
Checked project by project — the path form and the CLI agree on all five,
including finance-tracker's 4,018,382 tokens and the two that legitimately have
none.

**The first version of the no-chdir test was useless and passed anyway.** It
called `tasks_for(repo)` from inside that same repo, so a reinjected `chdir` to
that directory changed nothing observable and the guard went green against the
exact bug it existed to catch. It now runs from outside the project, and
reinjecting the chdir turns it red.

## 2026-08-07 · The Tower's whole open queue, in one pass

Implements #73, #74, #70, #71, #75, #66 and #63 — every open Tower issue but
one. All seven touch `bin/tower`, so they went through as a queue on one branch
rather than as parallel branches racing on a single surface.

**The two corrections came first, and not because they were small.** A screen
that can be silently stale and an amber warning that is wrong three times in
five undermine every other number on it.

`#73` — Tower.app runs a pinned checkout refreshed only by
`build_towerapp.sh --install`, so it falls behind on every merge. Against the
live pinned copy it was **5 commits behind**; two days behind before today's
rebuild, serving the pre-proposal-09 screen while every session reported those
problems fixed. The header says so now, and says nothing when current — a
permanent line would be the wallpaper problem #75 exists to fix. A checkout
*ahead* of main is not stale: that is a session working, and warning there would
put the line on the screens most likely to be read.

`#74` — three of five contested pairs were `AGENT-LOG.md`, which carries
`merge=ours`. A file with a merge driver cannot conflict; that is the point of
#44, #45 and #57. It asks `git check-attr` rather than parsing `.gitattributes`,
so glob rules work and the answer is the one git will use at merge time. A
failure degrades to warning rather than silence: over-warning is recoverable,
under-warning hides a real collision.

**PIPELINE is gone, replaced by BOARD / LEDGER / PROGRESS tabs** (#70, #71, #66,
#63). It replaces rather than joins: PIPELINE was already a board of work by
state, and a board of *features* by state beside it would have been two boards
of one shape at different altitudes.

The tabs are links, not CSS state, because the page re-requests itself every
10 seconds and the DOM does not survive that — measured, then verified in a
browser by watching the timestamp advance through a real reload with LEDGER
still selected.

`PROGRESS` is a third tab rather than a sixth region, because the screen is
900px and detail belongs behind a tab. It draws a burn**up** — two lines, done
and total — from each checklist's own git log. No new record file and no
revival of proposal 08's rejected logbook. The gap between the lines is the
whole point: finance-tracker really went `4/24 → 18/51`, completing 14 items
in seven days while its percentage fell, because scope grew faster. Nothing is
smoothed or clamped monotonic — mac-explorer's total genuinely went 8 → 5, and
a dip is a re-scoping, which is information. Velocity names its window; there is
no ETA, no projection, no "on track", by the rule proposal 08 set.

**Two things were found by looking rather than by reasoning.** Escalating rules
drift put *five* rows in the band, because every project is 8–18 versions
behind — recreating the wallpaper one level up, which is the exact failure #75
was meant to fix. The worst two get rows and the rest is a count. And
`project_tag` shortened names into the prose: "idea has never recorded a rules
version". The tag is built for compact chips, so the band uses full names.

**One test was wrong and the test was fixed, not the code.** A branch name typed
into the sponsor's own State column is his prose, and rendering it is faithful;
the defect #65 fixed was the Tower *deriving* labels from directory names. The
guard now asserts the board and ledger take no worktree argument at all — they
cannot leak a name by construction.

**#76 is deliberately not implemented, and the reason is recorded in the code.**
Cost per feature needs `bin/spend`, whose `_tasks_here()` derives the repo root
from the *current working directory* and takes no path. Reaching it from a
collector would mean a process-global `chdir` inside a server that fans
collectors across threads — the kind of race that yields a wrong number
occasionally rather than an obvious failure. #76 puts changing `spend` out of
scope and says it is its own issue, so that is where this stops. The join it
needs already exists: spend keys tasks by worktree name, and `feature_of_issue`
maps a worktree's issue to a feature.

Tests: 34 → **73 passing**. The new guards were verified by reinjection —
putting the staleness line back on permanently, and removing the contested
filter — not by trusting a green run.

## 2026-08-07 · Five things the Tower should know, and doesn't

Proposal 12. Every finding came from using the screen for a day rather than from
thinking about dashboards, and two of them sharpened under checking.

**The Tower cannot tell you it is stale, and it is stale constantly.** Tower.app
runs `bin/tower` from a pinned checkout refreshed only by
`build_towerapp.sh --install`. Measured two hours after a rebuild: the app on
`208c789`, main on `cd19f10`. It falls behind on every merge. Before that
rebuild it had been two days behind, serving the pre-proposal-09 screen — the
truncated names, the 310px void — while every session reported those fixed. A
status screen that is confidently wrong with no hint that it might be is the
worst defect one can have, so this is a correction rather than a feature (#73).

**Three of five contested warnings are false by construction.** All three are on
`AGENT-LOG.md`, which carries `merge=ours` — confirmed in pockets and
finance-tracker. A file with a merge driver cannot conflict; that is the entire
point of #44, #45 and #57. `contested_pairs()` is `whoelse`'s logic, predates
the merge drivers, and has never been told they exist. Three in five is enough
to teach a person to ignore amber, which costs the two that are real (#74).

**Four million tokens are measured and none reach the screen.** `bin/spend`
reports 4,018,382 across 8 finance-tracker tasks. Note how it labels them —
`adoring-euler-ba942f`, `compassionate-bassi-fd5327` — which is exactly the
branch-name noise proposal 10 removed, and exactly why cost has never been
useful here. Cost per worktree is trivia; cost per *feature* is a decision.
#65's register plus `worktree_issue()` is the join that turns one into the
other (#76).

**A warning that never resolves is wallpaper.** `5 behind: finance-tracker,
idea-lab, mac-explorer +2` sat unchanged in the header through a dozen merges,
four proposals and six issues. Against version 114 the real spread is pip 11
behind, mac-explorer 9, finance-tracker 8, pockets 2, idea-lab never stamped —
and the screen renders all of them identically. It has to be able to escalate or
it will be tuned out again within a week (#75).

**The decision queue is under-reported.** Open PRs reach NEEDS YOU only when
they belong to a worktree with a mapped issue, so a PR from an unmapped branch
is invisible. How many decisions are waiting, and how long the oldest has
waited, is the number that says whether the autopilot can keep going without the
sponsor. The age is the part that matters: four things waiting ten minutes is a
working autopilot, four waiting two days is a stalled one (#75).

Three things are ruled out in the document rather than left to drift back in:
no new region (900px is already tight and #70 is about to take PIPELINE's
space), no forecast of any kind (proposal 08 refused an ETA on four days and #63
held the line on six — cost and drift both invite "at this rate…"), and no new
bookkeeping, since every figure above is derivable today and the logbook was
rejected once already.
## 2026-08-07 · Three ways to show the features, and the two he picked

Proposal 11, a design exploration rather than a proposal with one answer.
Building #65 is what made it necessary: the information was right and the
layout it landed in was the one the deleted regions left behind. Measured on
the running screen — five "no features declared" lines shouting over the one
project with real features, every feature title truncating because the region
sits in the 2fr half of a 3fr/2fr split despite being the spine, blocked
features drawing an empty bar that reads as 0%, and no whole-product figure
anywhere.

Three structurally different answers were drawn, not three skins: **A** a
cross-project feature ledger, **B** a board with columns by state, **C** a
portfolio of one line per project with the whole-product figure first.

**the sponsor chose A and B.** Recorded plainly, because it went against the
recommendation: the paper argued for C first with A later, and argued against
building B at all on the grounds that it has no home for a completion
percentage and three of its four columns are empty on today's data. He read
that and chose otherwise. It is his screen. The original reasoning is left
unedited in the document so the disagreement stays visible rather than being
tidied into agreement after the fact.

Taking both raised two questions the options paper never had to answer, and
both are settled in the document rather than left to be discovered mid-build.
**The completion figure lives in A's header** — taking A alongside B resolves
the objection to B instead of overriding it, and B gets no bolted-on figure.
**The two views do not share one screen**: B is the region on the main screen,
because "what is running, what is done" answered by position is the job that
screen exists to do, and **A becomes its own `/features` route**, which is the
same move the Tower already makes with `/pulse` and `/session/<id>`. A gets
better as registers land without ever making the main screen taller, and the
900px budget from #56 is untouched.

Three fixes land with whichever option, since they are corrections rather than
choices: a blocked feature gets no bar at all, the features region moves to the
wider column, and undeclared projects collapse to one grouped statement.

**Drawing the merged screen changed one of the two issues before either was
built.** Assembled, A and B collide in two ways neither had alone. The board and
the existing PIPELINE are the same widget at different altitudes — one counting
issues by state, one counting features by state — which is the noise this
redesign set out to remove, reintroduced somewhere new. And four columns in the
wider half of a 3fr/2fr split are ~150px each, so titles would truncate *worse*
than they do now, which is the defect #70 exists to fix.

Both have one answer: **the feature board replaces PIPELINE rather than sitting
beside it.** It follows from the ask — features, not issues, not branches — and
it gives the board the full width four columns need. Issue-level flow moves to
`/features`, where it is detail rather than noise. #70 was rewritten to say so
before any code was written against it.

**Then the sponsor chose tabs, and a measurement decided how to build them.**
Both views now live in one full-width region where PIPELINE was, switched by a
tab — and the obvious dependency-free implementation is broken here. The Tower
re-requests itself every 10 seconds, and CSS tabs (hidden radios plus a
`:checked` sibling) hold their state in a DOM that every reload destroys. Tested
against a 3-second refresh: selecting LEDGER came back on BOARD, while a
`?view=ledger` query string survived intact.

So the tabs are **links**, and the server renders the chosen view —
`/?view=board` and `/?view=ledger`. The meta refresh re-requests the current URL
including its query string, so the choice sticks, and no JavaScript is involved,
which keeps proposal 09's rule that the Tower's only interaction is a link. It
also retires the separate `/features` route drafted an hour earlier: a query
string already is one.

Worth recording as a near miss. Building CSS tabs would have produced a screen
that silently flipped back to BOARD every ten seconds, and the blame would have
landed on the tab rather than on a refresh nobody was thinking about.
## 2026-08-07 · The Tower reads the features register, and names no branches

Implements issue #65, the core of proposal 10. The screen's spine is now each
project's declared `## Features` table. Nothing is inferred.

**What was actually wrong.** Three sources, all of them the wrong thing:
worktree directory names, issue title prefixes (`title.split(":")[0]` — two
issues shared a "feature" only if somebody typed the same words before a
colon), and `##` headings, which in three of four projects are priority
buckets. `Now` is not a feature and never finishes.

**No worktree or branch name is rendered anywhere now** — not in a label, not
in a hover, not in a disclosure. `tests/test_tower_render.py` pins it across
every renderer that takes a worktree, verified by reinjecting a name into the
strip's hover and watching the guard go red. The `<details>` listing 18
worktree names from #51 is a count instead: a worktree with no mapped issue has
nothing to identify it *by* except its directory.

**The parsing subtlety that would have corrupted every percentage.** A register
row reads either `in flight — issue #1` or `blocked by #2`. Those are opposite
facts. Reading every `#N` in the row would have made each blocked feature
inherit its blocker's progress, so `IMPLEMENTS` and `BLOCKED_BY` are separate
patterns and only the first ever reaches a figure. On the live register that is
the difference between "0/1 issues" and five features silently claiming
Milestone 0's completion.

**Completion is split, per proposal 05.** The percentage is derived from issues
— a measurement nobody maintains. **Done** comes only from the sponsor's State
column. A feature whose tickets are all shut but which he has not closed reads
`100% · awaiting your close`, which is the honest state and a useful prompt.

**Undeclared scope is still not zero.** Only pockets has a register, so
finance-tracker, pip and mac-explorer read "no features declared — 18/54
checklist items ticked, against no product definition". Proposal 08's rule, and
it binds harder here because a completion figure is the thing the sponsor asked
for by name: a number over an invented denominator would be worse than none.
`feature_data` calls `PULSE.checklist_progress` rather than counting ticks with
a local regex, specifically so the "lines that look like items but could not be
parsed" warning survives instead of being quietly dropped.

**Deleted:** `compute_hulls` (dead since #52), `burnup_data`, `render_burnup`
and the per-package bars, and the `groups`/`prefix_total` payload that existed
only to feed the hulls. `AT THE WALL` also went — it named worktrees and said a
second time what the NEEDS YOU band says first and larger.

Fixed on the way, having been recorded on this issue during #64: the sessions
summary did not sum. `22 · 0 active, 1 needs you, 4 idle` left 17 of 22
sessions in no bucket, because the contested branch assigned a class and
counted nothing. Every session now lands in exactly one bucket and the line
reads `11 · 1 needs you, 5 contested, 5 idle`.

Also fixed: `graph_err` included `hulls_err`, so a failure inside a collector
rendered nowhere would have blanked both NEEDS YOU and SESSIONS.

## 2026-08-07 · Handovers and the commit ticker come off the Tower

Implements issue #64, the first of proposal 10's queue. Two regions gone:
HANDOVERS was two AI sessions coordinating, the EVENT TICKER was commit
subjects. Neither is something the sponsor needs at a glance — *"I don't want
to know what internal communication is going on."*

**The point was the space.** At 1280×900 the two regions were 453px and 186px.
Removing them, and correcting a row template that still declared a row for them,
**doubled the pipeline's visible height from 211px to 425px** — the region that
had room for about four rows since #56. Work packages went from 211px to 425px
against 478px of content, so it now very nearly fits without scrolling at all.

**What was deliberately kept.** `/session/<id>` survives: it is reached from the
sessions strip, and it still shows what a session last said *and what was handed
to it*, so the cross-session-message parsing (`_XSM`, `_first_sentence`,
`resolve_cwd`) stays. Only the region that listed those messages is gone. This
was checked rather than assumed — the issue asked for exactly that check, and
`_first_sentence` turned out to be shared between `message_edges` and
`session_digest`.

**What went with them, which is worth naming.** `collapse_repeats()`, `times()`,
`_epoch` and `DEDUP_WINDOW` — the byte-identical de-duplication built in #52 —
had no subject left once both regions went, so they are deleted. That is #52's
work being removed two commits after it landed, deliberately: the regions it
made honest are not on the screen any more. Git keeps it if #66 wants it back.
`session_owner_dirs()` also went; it had already been dead on main.

**Test coverage was retargeted rather than dropped.** The de-duplication tests
are gone with their subject, but the escaping test — which happened to use
`render_handovers` — now runs against `render_strip` and `render_needs_you`
with a payload that also tries to break out of a `title` attribute. Losing that
guard because the renderer it happened to be written against was deleted would
have been the quiet kind of regression.

Found while verifying, not fixed here: `render_strip`'s summary line does not
sum (`22 · 0 active, 1 needs you, 4 idle`) because the contested branch
increments no counter. Mine, from #52, invisible until many worktrees were
contested at once. Recorded on #65, which rewrites that function.

## 2026-08-07 · Proposal 10: the Tower has been reporting the plumbing

the sponsor, on the screen proposal 09 had just finished: *"it doesn't help when you
are saying some random branch name. What features are done, what is the degree of
completion of the whole product, and what things are running. I don't want to
know what internal communication is going on."*

He is right, and the cause is that the Tower reads three things that are all the
wrong thing: **worktree directory names**, **issue title prefixes**
(`title.split(":")[0]` — two issues share a "feature" only if someone typed the
same words before a colon), and **`##` headings in `CLAUDE-checklist.md`**, which
in three of four projects are priority buckets. `Now` is not a feature and never
finishes.

**Features already exist as a first-class idea in these very rules** — "the user
owns features, the AI owns issues" — and **pockets already declares seven** in a
register with states and linked issues. The Tower has never read it. That is the
whole diagnosis: not a labelling bug, a wrong source.

**The honest blocker, and it is not the Tower's.** "Degree of completion of the
whole product" is a fraction, and the denominator exists for **one of four**
active projects. finance-tracker, pip and mac-explorer have never declared what
their features are, and there are no GitHub milestones anywhere. A percentage
across the estate would be a number over an invented denominator — the same lie
proposal 08 refused when it insisted a project with no checklist reads "no
declared scope", never 0%. So those three render "no features declared" until
their registers land.

Draft registers for all three were written the same day and are with the sponsor
for correction. Creating and scoping features is reserved to him, so they are
proposals: 9 candidates for finance-tracker, 9 for pip, 7 for mac-explorer, each
listing the open issues that roll up into it — which is what makes a percentage
computable, and also the honest test of whether a feature is real.

**Progress does not need the logbook proposal 08 rejected.** The history is
already on disk and unread: the tick count at any past commit is recoverable from
`git log` of each checklist, and the register's issues carry real close
timestamps. finance-tracker has 20 such revisions, pockets 9, pip 11.

Two decisions taken in-role rather than asked. **A feature's percentage comes
from its issues; "done" comes only from the sponsor's State column** — proposal 05
already says he closes features, so a feature whose tickets are all shut reads
"100% · awaiting your close". And **the per-package bars are dropped**: with
features as the spine they measure the filing structure again.

Cut into a queue on one surface — #64 (handovers and ticker off, pure removal),
#65 (features as the spine, no branch names anywhere), #66 (what moved today) —
plus #63 for burnup and velocity, which is independent of all of it.

## 2026-08-07 · derecord corrects a changed rule instead of freezing it (#57)

`bin/derecord` installed `.gitattributes` rules by asking *"is there a line for
this path?"* and nothing more. Once a pattern was present its value was frozen
forever: changing a rule in `gitattributes-for-projects` silently failed to
reach any project that had already adopted, **and the script reported success**.

Its own header called it "Idempotent: run it as often as you like." That was
true in the weak sense — running twice added nothing twice — and false in the
sense the header invites you to rely on, which is that running it makes the
project match the shared rules.

**It had already bitten.** `AGENT-LOG.md` moved from `merge=union` to
`merge=ours` earlier the same day, because the log became generated output and
union-merging generated output interleaves two tables into a file that is
neither side's truth. finance-tracker was corrected by hand; **pockets was still
on `merge=union`**, and `derecord` on it printed `0 record rule(s) added` and
`is done`.

The check is now "is there a line for this path *with this value*?", and a stale
value is rewritten in place. Local rules for patterns the shared file says
nothing about are never touched. The output says `added` / `corrected` /
`already matches the shared rules` rather than only ever counting additions.

`tests/test_derecord.py` covers it: a stale value is corrected, missing rules
are still added, unrelated local rules survive, a second run is a genuine no-op,
and the success wording cannot come back. Verified by running the new tests
against the **old** script first — two failed, which is the only way to know a
guard guards anything.

**Behaviour change for adopted projects:** re-running `derecord` now rewrites a
record-file merge strategy that has drifted from the shared rules. Run it once
per project to pick up the `AGENT-LOG.md` change.

## 2026-08-07 · Proposal 09 is built

Status flip only, no behaviour: `accepted` → `built`, in the document's
`<meta>`, its visible chip, and the index row — the README derives the index
from the documents, so all three have to agree or the table is lying.

All four issues are merged to main: #50 (d00ecd5 lineage), #51 and #52 (dd8dd0e),
#56 (d00ecd5). `built` is the first use of that status in this folder; the
vocabulary has carried it since the index was written and nothing had earned it
until now.

The chip is `--accent` rather than the `--gain` an accepted proposal gets, so
built and accepted are distinguishable at a glance on the proposals index —
otherwise the only difference is a word in a table cell.

## 2026-08-07 · The Tower fits its window, and stops growing with the tree

Implements issue #56, which finishes proposal 09. **The page now fits 1280×900
exactly** — verified in a browser at 900px, and again at 820px where the caps
must *not* apply.

**The issue was filed on a diagnosis that turned out to be wrong, and that is
the useful part of this entry.** It said the pipeline was "the last 780px
between the screen and one glance" and that collapsing two of its lists would
get under budget. Measured by hiding whole regions and re-reading the page
height, at 1280 wide:

| state | height |
|---|---|
| before | 1,792px |
| **entire pipeline region deleted** | **1,196px** |
| pipeline *and* handovers deleted | 912px |

Deleting the whole pipeline still overshot by 296px. The reasoning error was
forgetting the grid: the page is
`header + band + max(pipeline, work-packages) + max(handovers, ticker) + strip`,
so work packages (472px) and handovers (453px) set a floor that no amount of
pipeline cutting reaches. Once the pipeline drops below 472px every further chip
removed buys exactly nothing.

**So the fix is not a cut at all.** The regions are capped and scroll inside
themselves. Nothing is dropped, nothing is hidden behind a disclosure, and the
page fits by construction rather than by tuning.

That last part is the real point. The page height was a *function of how much
work exists* — it went 1,721 → 1,792px during the hour #51 and #52 were being
built, purely because worktrees were added. Any fix that works by cutting
content would have gone out of budget again on its own the next busy week.
the sponsor chose this over cutting content for that reason.

**Two CSS rules do all the load-bearing work, and both were wrong first.**
`align-items:start`, inherited from the uncapped layout, makes a grid item size
to its content and overflow its track — so the cap never binds and the scrollbar
lands back on the page, looking exactly like the cap "not working". Same net
effect if `min-height:0` is missing. `tests/test_tower_render.py` pins both,
verified by reinjecting `align-items:start` and watching it go red, because
either one reads as harmless in review.

The band is capped too, at 22vh. Unbounded, three waiting items took 28% of the
screen and squeezed the pipeline to 165px — it is the most important region and
still must not own the window.

Below 1001px none of this applies: a narrow window is a browser being read, not
the wall screen, and locking that to the viewport would squash six regions into
nothing. It stays a normally scrolling single column.

No behaviour change for any adopted project: this is `bin/tower` and its tests.

## 2026-08-07 · What needs you is first on the Tower, and the graph is retired

Implements issues #51 and #52, the last two of proposal 09. Built as one branch
rather than two: both re-cut the same surface, and `CLAUDE-workflow.md` says two
issues that touch the same file are one issue or one queue — running them in
parallel is the #30/#31 collision class.

**The two things that needed him used to be two circles among 23.** They are a
band at the top now, in words, at 17px: the issue title, the project, why, and
how long it has waited. When nothing needs him it collapses to one line and
gives its height back — reserving empty space is the failure mode this proposal
exists to fix, so the empty state had to be a line and not a box.

**`IN FLIGHT · 19` was an 18x overstatement.** One of those nineteen was a
mapped issue; eighteen were git ahead-counts wearing the same chip. In flight
means a mapped issue now, and the ahead-of-main worktrees collapse into a
`<details>` that expands in place — collapsed, not hidden, and no JavaScript.

**The graph from concept 07 is retired, not deferred**, on the sponsor's call. 615px
bought 23 labels in a 4-column grid where position was enumeration order, size
and fill were constant, and one edge ever rendered. It is a 117px strip of state
dots — measured, against the ~118px the proposal estimated. Every worktree is
still reachable: the hover carries the name, the mapped issue and the age *in
full*, because a title attribute has no width to fit and so cannot truncate. The
six worktrees that have a transcript link through to `/session/<id>`; the other
21 have no session to open and render as plain dots rather than dead links.

The one contested pair the graph ever drew — as a 470px diagonal with its
caption floating unanchored at the midpoint — is a row in the band now, which is
where an actionable collision belongs.

**Repeated events collapse, and only byte-identical ones.** Four of nine ticker
lines were the same event recorded by four agent logs a minute apart. The window
is 900s and the count is always shown. A row differing by one character stays
its own row: the claim is "this is literally the same event N times", and
anything looser hides real events. `_epoch` returns 0.0 on an unparseable stamp,
which puts a row outside every window and leaves it *uncollapsed* — the safe
direction, and `tests/test_tower_render.py` pins it, because the tempting
implementation folds two junk-stamped rows together on the strength of both
being equally unparseable.

**One collector change, and it is the same shape as #50's.** `needs_input` was a
set of names, so the reason and the wait were computed and thrown away — the
screen could say "needs you" but never why or for how long, which is most of
what the band is for. It is a dict now. Same two conditions, same inputs,
nothing new collected.

**The no-scroll budget still is not met, and this says so rather than claiming
it.** The page is **1,721px at 1280 wide**, down from 2,283px after #50 and
2,241px before any of this. The target is 900. What remains is the pipeline
column at 780px — eight queued chips, four merged, and the wall — which neither
of these issues touches. Closing the rest means cutting the queued list, and
that is a content decision nobody has taken yet, not something to slip in here.

No behaviour change for any adopted project: this is `bin/tower` and its tests.

## 2026-08-07 · The Tower is HTML now, and stops cutting words in half

Implements issue #50, the first of proposal 09's three. The page was one
hand-positioned SVG: every `render_*` had the shape
`(data, x0, y0, width) -> (svg, bottom_y)` and `render_page` threaded `bottom`
forward to stack regions. That is a layout engine missing text measurement,
intrinsic sizing and reflow — and all three absences were visible on the live
screen. It is CSS grid now. **198 absolute `x=` coordinates became 0.**

**Nothing is cut mid-word any more.** Eight hardcoded `[:n]` slices existed only
because SVG `<text>` cannot wrap; they produced `arm-f-filin`, `arm-b-contr`,
and a pipeline row that stopped one character short of "lines". Fitting is CSS's
job now — the card clamps visually and keeps the whole string in a `title`
attribute, of which there are **85 where there were none**.

**One collector change, and it was asked for rather than assumed.** Issue titles
were cut to 22 characters inside `collect()`, so no amount of CSS would have
shown them in full — "Tower: the screen fits its window..." rendered as "the
screen fits its…". That cut existed because the label had to fit inside a
25px-radius circle. the sponsor agreed to move it to CSS; nothing about what is
*collected* changed, and `truncate_words` is gone with its only caller.

**The 310px void is structurally impossible now, not merely fixed.** It came
from `main_bottom = max(graph_bottom, pipe_bottom)` padding the shorter of two
independently laid out columns. Column heights are a grid concern now. Work
packages also moved under the sessions rather than full-width below both, because
the pipeline column runs ~1.7× the sessions column and a two-column row is only
as short as its taller cell — that left ~600px of empty column. Balanced: 1250 /
1416.

**`tests/test_tower_render.py` is new**, and the guard that matters is not the
happy path: it fails if a `[:n]` ever reappears *inside an f-string
interpolation*, which is the exact shape every old truncation had
(`{e(w["short"][:11])}`). A plain `behind[:3]` choosing how many project names to
list is not that bug, and the first version of the check could not tell the
difference — it flagged it, which is how the distinction got drawn. Verified by
reinjecting the bug: red with it, green without.

**The no-scroll budget did not land here and was never going to.** "Fits
1280×900" was written on #50 where the 615px session grid it depends on belongs
to #52; it has moved there. The page measures **2,283px at 1280 wide**, against
2,241px at 1200 wide before — the same order, because #50 cuts nothing. What it
does is make the screen reflow (single column below 1000px, where the old page
clipped), stop lying about names, and stop reserving empty space.

No behaviour change for any adopted project: this is `bin/tower` and its tests.
## 2026-08-07 · Proposal 09: the Tower is drawing the right data the wrong way

the sponsor asked for a proposal on the Tower's UI — "the ui is not clean". Measured
against the live tree rather than read off the source: `tower --port 8893`, 23
worktrees across 6 projects, numbers read back out of the rendered DOM.

**Nearly every symptom has one cause.** Every `render_*` function has the shape
`(data, x0, y0, width) -> (svg, bottom_y)` and `render_page` threads `bottom`
forward to stack regions. That is a hand-rolled layout engine missing the three
things a real one gives free — text measurement, intrinsic sizing, reflow — so it
truncates, voids and overflows instead:

- The SVG renders **1200 x 2241** into a window that opens at **1280 x 900**
  (`tools/tower_window/towerwin.swift:168`). About 40% of a glanceable screen is
  visible at a time.
- **310px of empty black** down the left column, because
  `main_bottom = max(graph_bottom, pipe_bottom)` pads two independently laid out
  columns to the taller one.
- Eight hardcoded `[:n]` caps exist only because SVG `<text>` cannot wrap. `[:11]`
  produced `arm-f-filin`, `arm-b-contr`, `m0-stage2-v`; the pipeline's top row cut
  one character short of "lines".
- Of 23 session nodes exactly **two** carried state. The other 21 were identical
  grey circles at identical weight. `IN FLIGHT - 19` counted 18 `worktree - N ahead`
  git counts alongside one real mapped issue.

**The collectors are not the problem and are not touched.** Everything above line
780 of `bin/tower` — the hard part — stays exactly as it is, which is what keeps
this a two-to-three day job rather than a rewrite.

**The graph from concept 07 is retired, not deferred.** the sponsor decided on
2026-08-07 to compress the session grid to a strip. That is the honest reading of a
measurement this repo already had: `message_edges()` (proposal 08) found handover
edges almost never have both ends on screen, and today exactly one edge renders
across 23 nodes. A graph whose edges do not exist is a grid with extra ceremony.
Retiring his own concept was his call to make, so it was asked rather than assumed.

Cut into a dependency-ordered queue — #50 (the page becomes HTML/CSS), then #51
(needs-you band, in-flight redefinition) and #52 (session strip, de-duplication),
both blocked by #50. One queue rather than three parallel branches because all
three touch the same surface, which is the collision class the worktree rule
exists to prevent.

## 2026-08-07 · The workflow.html stamp is checkable now, not remembered

`docs/workflow.html` claimed **rules version 62** while the rules were at
**102** — forty versions of drift on a page whose own README says a drifted
bird's-eye view is worse than none, because it is trusted at a glance and read
without suspicion. `rulecheck` surfaced it while implementing proposal 08.

The first correction was wrong too: it predicted the count the PR would land at,
two PRs merged, and the stamp landed one behind again. **A stamp defined against
HEAD can never name the commit it is written in** — every correction lands one
short and needs correcting.

So the definition changed rather than the number. **The stamp names the version
at which `CLAUDE-workflow.md` last changed**, not the current HEAD count. A
commit that only touches the page leaves the target still, so the regress
disappears. It now reads 104, which is where the rules actually are.

`tests/test_workflow_stamp.py` enforces three things: the page is not older than
the rules it describes, the stamp is not from the future (one ahead is legal — a
stamp is written for a commit that does not exist yet), and `workflow.png` was
not committed before the last change to `workflow.html`. Verified by running it
against the drift first: it failed with `103 not greater than or equal to 104`
before the fix, and passes after.

## 2026-08-07 · AGENT-LOG.md is generated now, and forced delegation is not adopted

Implements proposal 08 (`docs/proposals/08-proposal-workflow-bakeoff.html`),
accepted after five workflow architectures built one frozen spec and all five
scored 22/22 while cost varied 17×.

**`AGENT-LOG.md` stops being hand-written.** The rule was "append one entry when
the task lands" via `spend log`. Ten entries were written that way in
finance-tracker and **none carried the token figure the report reads**, so
`spend report` answered 0 for every row for a week — a number that is only right
when somebody remembers to type it is not a measurement. `bin/spend report` and
the new `bin/spend agentlog [--write]` now read `~/.agent-data/projects/*/*.jsonl`
directly, group sessions into tasks by the worktree they ran in, and count agent
dispatches from the actual `Agent` calls. finance-tracker reports 3,004,419
output tokens across 8 tasks and 38 dispatches where it reported nothing.

**`tests/test_spend.py` is the first test in this repo** — the other half of the
lesson, since `spend` shipped without one. It fails if a report over transcripts
carrying real usage ever comes back zero. Writing it immediately found a second
defect: `_task_of` compared paths as strings, and macOS symlinks `/var` to
`/private/var`, so a session's recorded `cwd` and git's toplevel could name one
directory two ways and silently drop the task. Both sides are realpath'd now.

**`AGENT-LOG.md` moves from `merge=union` to `merge=ours`** in
`gitattributes-for-projects`. Union merge is right for an append-only record and
wrong for generated output — it would interleave two generated tables into a
file that is neither side's truth. Take ours, then regenerate.

**Forced delegation is not adopted, and removes nothing.** The six-day review
proposed a driving session holding no `Edit`/`Write`, structurally required to
delegate all code. Two arms ran it; both scored the same 22/22 as a 37-line
control at many times the cost. It was never written into these rules, so the
retraction is a record rather than a deletion. Scope: this does **not** touch
tool grants as applied to the *roles* — `quality-manager` having no write access
is untested here and stays. What failed was extending the mechanism to the
driving session.

**Also fixes the `workflow.png` recipe in `docs/README.md`.** Plain `--headless`
now resolves to Chrome's new headless mode, which ignores `--screenshot` and
never exits — it hangs until killed, writing no file and printing no error. The
documented command had silently stopped working; `--headless=old` restores it.
The crop step, previously a pointer to a changelog entry, is now written out and
was run verbatim to confirm it produces the committed image.

Behaviour change for adopted projects: **regenerate `AGENT-LOG.md`, do not edit
it.** Existing hand-written logs stay valid until regenerated; the first
regeneration replaces the prose narrative with the measured table, so anything
in there worth keeping should move to `LESSONS.md` first.

## 2026-08-06 · The bake-off finished, and it mostly says keep the rules as they are

Five arms built one frozen Swift spec — 22 EARS criteria, a fixed public API —
in isolated worktrees, scored by a sealed suite written before any arm started
and which none of them saw. **All five scored 22/22.** Cost ranged from 5.4
minutes to 122.8, and 66,816 output tokens to 209,355.

The cheapest arm was the *control*: read the spec, build it, run the tests, no
requirements document, no design document, no agent dispatch, no gate. It is
also, near enough, what "Ceremony is opt-in" already prescribes. So the headline
change here is a citation rather than a rule — the default was asserted from 30
sessions of general experience, and now has a controlled result under it.

**The pattern that failed is the one the six-day review proposed**: a driving
session holding no `Edit`/`Write`, structurally forced to delegate all code to
`code-engineer`. Two arms ran it. They cost 2.4–3.1× the tokens and 11–23× the
wall-clock of the control and returned nothing the suite could see. It is not
adopted. Note the scope carefully: this does **not** touch "tool grants, not
instructions" as applied to the *roles*, which the bake-off never tested. What
failed was extending that mechanism to the driving session.

Cost also turned out not to track process weight, which round 1 had concluded
from three arms. The heavier of the two delegating arms was the *cheaper* one,
by 47,928 tokens and 62 minutes — its up-front partition let five branches merge
with zero conflicts, while the lighter arm found its defects late and burned two
serial fix rounds. Round 1's headline is annotated as superseded rather than
rewritten.

**One rule is added, and it replaces the question-asking paragraph rather than
sitting beside it**: ask before code, in one batch, and proceed on documented
defaults. The evidence is that arms doing this did not stall — one logged six
questions, received no answers, and still finished — while the control asked two
and silently resolved nine by judgement. It got all nine right. Whether that
holds when a silent guess is *wrong* is the question no round tested, because
the suite catches wrong guesses before they can reach scoring. That is recorded
as open, and it is the only thing that would overturn any of this.

What the experiment produced that outlasts it: five isolated arms, unable to
read each other, converged on the same three defects in the spec. When several
independent readers ask the same question about a specification, the
specification is wrong — and that costs nothing to exploit.

Full numbers and the proposal are on branch `experiment/results` under
`experiments/pockets-core/`. Nothing is merged to `pockets/main`.

Also corrects a factual error in `README.md`. It claimed agent definitions
"register at session start, so a definition added or changed mid-session doesn't
take effect until a new one." **They register immediately** — measured today,
when an agent dropped into `agents/` became invokable in a running session with
no restart. The wrong sentence cost this experiment a planned restart it never
needed. What *is* fixed at session start is which directories get searched.
## 2026-08-06 · derecord says what to do next, instead of leaving a trap

Installing the union rules is not enough to make the next merge work, and the
failure looks exactly like the rules being broken.

git reads `.gitattributes` **as of the merge's starting state**. A merge that is
itself delivering `.gitattributes` therefore runs without it, so the first merge
after installing still conflicts on `CHANGELOG.md`. Hit on 2026-08-06 bringing a
long-lived branch up to date, immediately after the rules had been fixed and
installed everywhere — the obvious read was that the fix had not worked.

Measured both ways on a scratch repo: with the file riding the merge, 1 conflict
and markers left behind; with the file committed first, 0 conflicts and a clean
union keeping both sides. Same repo, same commits, only the ordering different.

`derecord` now prints the fix when it applies, and only then — if it leaves
`.gitattributes` uncommitted, it says to commit it on its own before merging and
gives the command. A repo where the file is already committed and unmodified
gets nothing, because a standing warning is just something to scroll past.

The trap is one sentence in the script's header too, since the person reading it
later is not necessarily the person who ran it.

## 2026-08-06 · derecord was breaking the merges it existed to protect

Ran `derecord` across every project, as asked, and testing it first found two
defects — one inert, one actively harmful.

**`merge.union.name` made record-file merges fail outright.** The script set it
as a cosmetic label. It is not cosmetic: defining `merge.union.*` declares a
*custom* driver named `union` that shadows git's built-in one, and a custom
driver with no `.driver` command makes git abort with `fatal: custom merge
driver union lacks command line`. So the line meant to help turned every merge
touching CHANGELOG.md into a hard failure. It was live in **finance-tracker** —
the only project that had derecord installed — so the one project with this
"protection" could not merge its own changelog. derecord now unsets it, and
repairs any repo that already carries it.

**`merge=ours` never worked at all.** Unlike `union`, `ours` is not built in and
needs a driver. Without one the attribute silently degrades to a normal merge:
demonstrated on a throwaway repo, two branches each writing
`.common-rules-version` left `<<<<<<< HEAD` in it — the exact failure these
rules exist to prevent, in the file that records which rules you are on. Fixed
with `merge.ours.driver true`.

Both were found by testing the mechanism on a scratch repo rather than trusting
that installing it had worked. The rule has been written down since 2026-08-05;
it has never actually held.

common-rules also carries `.gitattributes` now. The repo that ships derecord had
never run it on itself, which is why its CHANGELOG conflicted during an ordinary
merge earlier today.

## 2026-08-06 · The Tower shows who told what to whom

Issue #22, concept 07's step 3 and the last of the Tower feature. A HANDOVERS
region lists every cross-session message — sender, receiver, when, and the
message's opening line — and each row links to `/session/<id>`, which shows
what that session last said and what was handed to it. A handover can now be
reconstructed from the screen without opening a chat.

**They are a list, not edges on the graph, and that is a measurement.** Concept
07 drew green dashed edges between session nodes. Against the real corpus:
15 messages, every one with a worktree at the *receiving* end, and **not one
with a drawn node at both ends** — senders were either management sessions
running at the apps root (not a worktree, so no node) or sessions whose
transcript is already gone. Edges would have rendered almost never. The drawing
was right about the information and wrong about the shape.

The same measurement decided how a sender is named: **from the message tag, not
by resolving its id.** Only 6 of 15 senders still had a transcript on disk, and
the `name="..."` attribute outlives the session, so a handover stays readable
after the session that sent it no longer exists. Resolving ids would have lost
nine of fifteen — and would have gone on losing more, since transcripts are on
a delete timer.

Two bugs found by looking at real output rather than fixtures:

- The one-line summary stripped `[*_`#>]` everywhere, which ate the characters
  carrying the meaning: "issue #35" became "issue 35" and "nicegui_app" became
  "niceguiapp" — the two things a handover is most likely to be about. Only
  leading markdown markers are stripped now.
- The session panel reconstructed a cwd by replacing "-" with "/", which turned
  `idea-lab` into `idea/lab`. The flattening is lossy and cannot be inverted,
  so the path is matched against directories that actually exist and falls back
  to the raw slug rather than a confident wrong answer.

`/session/<id>` refuses anything that is not an id shape before touching the
filesystem, and reads only the transcript named by it — never a glob over the
corpus.

## 2026-08-05 · An installed Tower reads its own checkout, not whichever branch is parked

Found by installing for the first time, minutes after #27 merged. The bundle is
a wrapper: it `cd`s to a repo and runs `bin/tower` from there. Pointed at the
shared checkout, that repo was on another session's experiment branch — three
commits behind main, with no work-packages region and no `build_towerapp.sh` at
all. The app would have silently served an old screen, and would break outright
on any branch where `bin/tower` does not exist. Nothing was wrong with the
build; the design tied a Dock app to a working directory that sessions
legitimately repoint.

An installed app now gets **its own checkout**, at
`~/Library/Application Support/Tower/repo`, detached at `origin/main` and
refreshed on every `--install`. Detached rather than on the `main` branch, so it
can never collide with `main` being checked out somewhere else. Outside the repo,
so no session's worktree cleanup can remove it.

`bin/tower` skips worktrees outside the project directory, because the pinned
checkout is registered like any other worktree and was drawing itself as a
session node on the very screen it serves — visible as `repo · 1 ahead` in the
first installed run.

The "refused, you are in a worktree" guard added with #27 is gone, and its
reason with it: it existed because the installed app pointed at the build
directory. It no longer does. Building from a worktree and installing is now
safe — the bundle's compiled shim and icon come from wherever you built, and the
code it runs always comes from the pinned checkout.

## 2026-08-05 · The Tower opens from the Dock

Issue #27, his Look-3 ask: "easier for me to track and restart". The one window
he wanted always available was the most fragile thing on his screen — a browser
tab pointed at a port that only existed while some session happened to be
running it. `./build_towerapp.sh` now produces `Tower.app`.

It is a wrapper bundle, not a frozen binary, same tradeoff as
finance-tracker's `build_macapp.sh`: it launches `bin/tower` from this repo, so
the app can never serve a stale screen sealed in at build time.

**The window is Swift, not pywebview.** The precedent in `build_macapp.sh` is
pywebview, but it is not installed here and the Tower is deliberately
stdlib-Python with no dependencies (concept 07). A ~200-line AppKit + WKWebView
shim compiled from source at build time adds a window without adding a
dependency — the same compile-from-source, commit-no-binaries philosophy as
finance-tracker's `docr.swift`.

Each of the issue's guarantees lives in code rather than in a habit:

- **Clean quit** — the shim spawns `bin/tower` as its own child and kills it in
  `applicationWillTerminate`, plus on SIGINT/SIGTERM. There is no path where
  the window closes and the server survives. Measured: quit leaves 0 processes
  and releases the port.
- **Exactly one copy** — it checks `NSRunningApplication` for its own bundle id
  at startup and activates the existing window instead of starting a second
  server. Holds even against `open -n`, which is the case macOS does not
  handle for you.
- **Loopback survives the wrapper** — `bin/tower` binds 127.0.0.1
  unconditionally and takes no host flag; the shim passes only `--port`. The
  wrapper cannot widen the bind by construction, not by policy. ATS is opened
  with `NSAllowsLocalNetworking`, never `NSAllowsArbitraryLoads`.
- **A free port, asked for not guessed** — it binds :0 and reads back what the
  OS assigned, so opening the Dock app while a session runs a Tower on 8890
  does not collide. Verified: they ran side by side, untouched.
- **Its own icon** — `assets/icon-tower.svg`, a tower silhouette in the Tower
  screen's own palette. Reserved for this app, not borrowed: Sangam's gold
  confluence and this green tower are not confusable at Dock size. Rasterised
  by `sips` (macOS 26 reads SVG directly), so no PNG is committed and no
  third-party renderer is needed.

`--install` is refused from a worktree. The bundle runs `bin/tower` from the
repo it was built in, and a worktree disappears when its branch merges — which
would leave a permanently broken app in `/Applications`. Build from the main
checkout to install.

Measured end to end: quit, click, and the window is showing current data in
**2.5 seconds**. `bin/appcheck` reports 43 bundles, every identifier unique.

## 2026-08-05 · The Tower says how much of each app is done

Issue #38, proposal 08 step 1b. The sponsor accepted this step explicitly
without the rule changes that came with the rest of that proposal — so this
adds a region and changes no rule, imposes no checklist shape, and creates no
standing obligation on any other session.

It reads what the projects already write. `CLAUDE-checklist.md` was already a
work-package register — `##` headings are packages, `- [x]`/`- [ ]` is the
completion state — in four of six apps, kept current by hand and read by
nothing. Parsing it as-is gives finance-tracker 17/44 (39%, 7 packages),
pockets 5/14 (36%), pip 3/13 (23%), mac-explorer 1/8 (12%), with the package
split beneath each.

Three things this deliberately does not do:

- **An app with no checklist reports "no declared scope", never 0%.**
  common-rules and idea-lab are that case. No declared scope and none of it
  done are different statements, and the second one would be a lie.
- **A line that looks like an item but does not parse is counted and
  reported**, not dropped. A silently skipped line lowers a denominator and
  moves a bar — proposal 08's own limit about making a prose file
  load-bearing, honoured by the parser that made it load-bearing.
- **No ETA column.** That needs the logbook, which was proposed and not
  accepted; a forecast drawn through four active days is a slope through
  noise.

Also done, and independent of all of the above: `cleanupPeriodDays` is now set
in `~/.agent-data/settings.json`. It was unset, so the 30-day default applied and
the 31 July transcripts — the start of the whole experiment — were going to be
hard-deleted around 30 August.

## 2026-08-05 · The Tower's pipeline sees every app, not one

The user asked the Tower's own question -- "what's pending in the pipeline" --
and the honest answer was that it could not tell him. `pulse`'s `PROJECTS` was
a hardcoded two-entry list, and the second entry carried `repo: None`, so
exactly one project's issues ever reached the screen: 25 of 38 open issues
shown, 13 invisible across pockets, mac-explorer and common-rules. The four
missing from common-rules were the Tower's own open tickets -- the window on
the autopilot could not see the work being done on itself.

The live graph and the event ticker were already machine-wide, which made the
screen internally inconsistent: a session node for a worktree whose issue the
pipeline beside it did not list.

`PROJECTS` is gone. Projects are discovered from `~/apps` at collect time,
each repo slug read from that checkout's own `origin` remote, so no entry can
drift to `None` again and an eighth app needs no code change. Six projects
found, 39 open issues on screen, common-rules #22/#24/#25/#27 among them.

Three things that fell out of doing it:

- **Issue numbers are only unique within a repo.** `common #27` (launch the
  Tower from the Dock) and `finance #27` (person dossier) were both on screen
  the first time it ran. Everything downstream is keyed on `(project, number)`
  now, never the bare number -- the in-flight match, the node labels, the
  feature hulls -- and every chip carries a project tag. Same class of bug as
  issue #24, one level up: a number that means nothing without its scope.
- **Six projects serially would have overrun the 5s collect.** The per-project
  `gh` calls are independent, so they fan out across a thread pool; collection
  measures 1.2s against all six.
- **common-rules was reporting itself "never aligned"** -- it carries no
  `.common-rules-version` stamp because it *is* the rules. A false alarm the
  old two-project list never got close enough to surface. It is excluded from
  the alignment chips, and the header names at most three behind projects
  before collapsing to a count, since six names overran the line.

## 2026-08-05 · appcheck looks at LaunchServices, not just the disk

The user still saw several Sangam copies after every duplicate bundle had been
removed, while `appcheck` reported "every identifier unique". Both were true:
only one bundle existed on disk, and LaunchServices still listed six, pointing
at worktrees deleted days earlier. Removing a bundle does not unregister it, so
the entries survive in Spotlight and Launchpad -- which is where a person
actually experiences "two copies".

The tool was checking the thing that was fine and not the thing he was looking
at. It now reports GHOST registrations too, scoped to the roots being checked
so another app's leftovers (Spotify's updater cache) don't bury the real ones,
and `--clear-ghosts` unregisters them one at a time rather than forcing a full
`lsregister -kill -r` rebuild of the whole database.

## 2026-08-05 · Install from main at the end of every feature

The user's rule, and it reverses an earlier one: `build_macapp.sh --install`
was previously forbidden outright. The installed app is what he actually
opens, so a feature that is merged but not installed is a feature he cannot
see -- today's app was four days old while three PRs sat merged on main.

Installing is now the closing step of a feature: check out main, pull, run
the suite, install. Never install a red build; an old working app beats a new
broken one.

Two things fixed alongside it, both found by doing it:

- `--install` staged into `dist/` and left the copy there, so every install
  produced two bundles carrying `local.wealthtracker`. With installing now a
  standing step, that duplicate would recur every time rather than once.
  Fixed in finance-tracker (PR #52): the staged copy is removed after a
  successful install. Non-install builds keep `dist/` untouched.
- `bin/land` reported "merge blocked" on a PR that had merged seconds
  earlier. `gh pr merge --delete-branch` exits non-zero when a worktree still
  holds the branch -- the normal case, since every task runs in one -- and
  land treated that as the merge failing. It now asks the remote for the PR's
  actual state instead of trusting an exit code that conflates merging with
  cleanup. A false "not merged" is the worst kind of wrong here: it tells a
  session to retry work that is already done.

## 2026-08-05 · apprun looks, instead of only remembering

The user found two app servers running that `apprun list` could not see: the
installed copy on :8502 and a worktree copy on :8600, both launched directly by
sessions (`python3 -m nicegui_app.main`) rather than through `apprun start`.
The registry only ever knew what it was told, so `stop` and `sweep` were
structurally blind to them and reported a clean machine. A registry that is
silently incomplete is worse than none, because it reads as authoritative.

Every command now also *looks*: any process listening on a local port whose
working directory is under the apps root, and which no open entry covers, is
reported as UNREGISTERED. Having no owning session, those are orphans by
construction — visible to `sweep`, refused by `stop`, closable only with the
user's yes. A copy running from a worktree path is never classified stable,
whatever port it landed on.

Discovered entries are never written to the registry. They are observed on each
run, so they cannot go stale the way a written record can.

New: `apprun adopt --port N` claims a copy started outside apprun for the
current session, making it that session's to stop at the end of its task.
Starting a server by hand is not the problem; leaving it unclaimed is.

## 2026-08-05 · The cut — 1,637 lines to 298, and four rules turned into code

Measured 30 sessions and 29.2M output tokens before changing anything. The
findings, and what each one changed:

- **Two thirds of all spend (68.6%) went to management chats, not to worktrees
  writing code.** Ceremony is now opt-in: the research/requirements/design/
  audit/L2 chain runs only on work the user has flagged as a feature. Everything
  else goes issue → code-engineer → gate → land.
- **Every merge conflict on 2026-08-05 was in a file these rules invented**
  (CHANGELOG, AGENT-LOG, LESSONS, the checklist, the version stamp). Hand-
  resolving them is what put conflict markers into three Python files and broke
  finance-tracker's main. `bin/derecord` now union-merges them, so two branches
  appending both win and neither conflicts.
- **Branches that live for days collide.** Two branches independently created
  the same new file and independently rewrote the same renderer. `bin/land`
  merges a branch as soon as it is green, without waiting to be noticed.
- **1,637 lines went unread.** Cut to 298. What survived is what measurement
  showed was load-bearing: worktree-per-task, tool grants, the pre-merge gate,
  and tests. A rule that can be enforced now lives in `derecord` as a git
  attribute or a hook, not as a paragraph.

Also, from the same day's asks:

- **AGENT-LOG stays, and now carries cost.** `bin/spend log <task>` writes one
  entry per task with the agents invoked, the tokens spent and the commits
  landed; `bin/spend report` and `bin/spend today` total it. The user asked to
  keep it specifically to see where spend goes.
- **Verification moves to the Browser pane.** The old pre-merge step 3 said to
  build and open the `.app` — which opens a real WebKit window and leaves
  another bundle on disk. That is now reserved for packaging changes only.
- **One installed app per project.** `bin/appcheck` finds bundles sharing a
  CFBundleIdentifier; four `Sangam.app` bundles were found claiming
  `local.wealthtracker`.

New in `bin/`: `derecord`, `land`, `spend`, `appcheck`.
Deleted from the rules: the record-file ceremony, proposal numbering/
immutability/traceability, the story section, ceremony tiers as a default,
the rulecheck prose (now a SessionStart hook installed by `derecord`).

Every change to a file in this folder gets an entry here — same convention
as a project's own `CHANGELOG.md`: newest first, one or two lines, why not
just what. This folder is its own git repo (see `README.md`), but `git log`
only records that something changed; this file records what it was for, and
is the thing to read first.

## 2026-08-05

- **A finished session doesn't linger — it offers to close** (his ask). "Leave
  nothing running" covered app instances; nothing covered the sessions
  themselves, and they pile up for the same reason — the work ends, nobody says
  so, and a done session looks exactly like a thinking one. Measured across ten
  worktrees the same day: `issue-27-person-dossier` holding a finished commit,
  idle **50 hours**; `proposals-status-refactor` clean and idle **29 hours**;
  `m0-stage2-v5-decomposed` idle **51 hours**; `proposal-register` on **20
  finished commits** with no live session at all. None abandoned — all *done*,
  none of them saying so.

  So a finished session states it plainly and offers to close, as the last line
  of its final report. **Closing stays his call** (same class as clearing an
  orphan — the session judged finished may be the one he was about to reopen);
  what is mandatory is the offer. A deliberate carve-out from "a question is a
  cost", allowed because he asked and because closing is already reserved to him;
  one line at the end of finished work is not decision spam. On the way out the
  session also exits its worktree, stops what it started, and completes its
  `AGENT-LOG.md` entry. **Paused is not finished** — waiting, blocked or
  mid-review stays open, and a session still holding uncommitted work has
  mistaken "stopped" for "finished".

- **`bin/tower`: live-graph nodes show what he's tracking, not git mechanics**
  (issue #25, from the sponsor at Look 3: "it's showing branch names, it doesn't
  mean anything to me… I'm tracking features and what features are working,
  which requires my input. And then I can look at, okay, which issue number,
  which chat I need to go to."). Node label order inverted: primary is now
  the issue title (prefix stripped when the node sits inside that feature's
  hull, truncated ~22 chars on a word boundary), secondary is `#<number>`,
  and the worktree name — how he actually finds the chat — moves to a small
  dim third line rather than being replaced. A worktree with no mapped issue
  still shows only its own name, the same honest mapping as #24 rather than
  a guess.

  Feature hulls widened: previously required >=2 mapped nodes, which is why
  none rendered at all despite Desktop Clerk having #41 active alongside
  #32/#33 open. A single mapped node now also draws a hull, labelled
  `FEATURE · <NAME> · <n> tickets, 1 active`, when its feature has other open
  issues not currently in flight — a feature with exactly one ticket and
  nothing else open still renders hull-less, since there's nothing else on
  it to show.

  Added the marking he's actually scanning for: a node gets the purple
  accent stroke (`#A98FD6`) plus a small "needs you" tag when it's a wall
  item, or its mapped issue's branch has an open, non-draft PR (a new
  `open_gate_branches()` collector — "awaiting a merge decision" read
  literally as what an open PR already means, nothing invented beyond that).
  A legend line now sits under the graph heading: green active · grey idle ·
  amber contested · purple needs you.

  Verified on spare port 8895 against live ground truth: all ten node
  primary labels are issue titles or worktree names, zero branch-name
  strings anywhere in the page; the Desktop Clerk hull rendered as `3
  tickets, 1 active`; the one wall item (`proposals-status-refactor`) is the
  one purple-marked, "needs you"-tagged node.

- **`bin/tower`: fixed false IN FLIGHT matches** (issue #24, found by the sponsor
  on the live screen — #2, #5, #7, #8, #9 shown as in flight when only #27
  actually was). Root cause was matching issue numbers as bare digit
  substrings of branch names: `"stage2"` matched `#2`, `"v5"` matched `#5`,
  hex worktree-name suffixes matched the rest. Deleted that matching
  entirely; `worktree_issue()` (first `"#<digits>"` in
  `git log main..HEAD --pretty=%s`, already used by the feature hulls) is
  now the single mapping for both. A worktree genuinely ahead of main with
  no mapped issue renders as its own dim, worktree-named row in IN FLIGHT,
  never as an invented issue chip; QUEUED is open issues minus the mapped
  in-flight set.

- **Worktree-per-task applies to common-rules too — the old rule said the
  opposite and was wrong.** It read "No worktree needed for this repo… four
  markdown files and a directory of agent definitions have no build and no test
  suite to collide over. A branch is enough." The reasoning mistook *what*
  worktrees protect: not a build, a **working directory**. A branch is a label;
  the checkout is the shared thing, and `git checkout` moves it under everyone
  standing in it.

  Disproven the same day, by this session: the project manager ran
  `git checkout -b` here while a code engineer was mid-edit on another branch in
  the same checkout, silently re-attributing its uncommitted work. The engineer
  recovered — stopped, verified nothing was corrupted, stashed, switched back,
  popped, re-verified — but it recovered **by noticing**, which is not a
  mechanism, and git warned neither party. Worth recording that the session which
  wrote proposal 02 committed the exact collision proposal 02 exists to prevent,
  in the one repo it had exempted.

  The folder is also no longer "four markdown files": four executables, a docs
  tree, and routinely two or more sessions at once. `EnterWorktree` first, here
  as everywhere; read-only exploration stays exempt, because reading cannot move
  anyone's checkout.

- **`bin/tower`, step 2 of concept 07** (issue #21) — the screen itself, not
  just `pulse` behind a port. Four regions on one loopback page: a header
  (rules version, per-project alignment chips, a live "THE WALL" count), a
  live graph — one node per worktree of finance-tracker and pockets, grid
  laid out, green/grey by session freshness from transcript mtimes, amber
  when it holds an uncommitted file another worktree also holds (`whoelse`'s
  logic, one dashed note per contested pair naming one file), dashed feature
  hulls grouping nodes whose ahead-of-main commits name the same issue
  (`git log main..HEAD --pretty=%s`, first `#<digits>` match — no invented
  mapping, ungrouped stays ungrouped), a pipeline built from `gh issue list`
  grouped like `pulse`'s feature groups (in flight / queued / merged today /
  "at the wall — yours"), and an 8-row event ticker merging `git log` across
  all three repos with one event per `AGENT-LOG.md` (its last `##` heading)
  across every main checkout and worktree. Wall items are a heuristic — a
  session's newest transcript tail containing `AskUserQuestion` and stale
  over 5 minutes — and labelled as one on screen, per the concept's own
  honesty rule about what a wall item can and can't prove. `/pulse` serves
  the existing page from memory (`pulse.render(write=False)`, loaded via
  `importlib.machinery.SourceFileLoader`) — a GET writes nothing, `pulse`'s
  CLI behaviour is unchanged. Every region collects independently and
  renders an "unavailable" note in its own place on failure — no region can
  500 the page. Loopback only, same rule as `pulse --serve`: this reads
  private transcripts. Self-registers with `apprun` as a `--demo` proto copy
  when run inside an agent session (`CLAUDE_CODE_SESSION_ID` set), and
  deregisters on shutdown; a plain-terminal run says registration was
  skipped, since apprun refuses an ownerless entry by design. Message edges
  and click-through (step 3) stay out of scope, as the issue says.

  Two real bugs surfaced against live data, both fixed in the same pass that
  found them. First: `run()`'s `.strip()` (copied from `pulse`'s helper)
  strips the whole `git status --porcelain` blob rather than each line,
  eating the leading space off a `" M file"` line and truncating the
  filename by one character — `AGENT-LOG.md` rendered as `GENT-LOG.md`.
  `whoelse`'s own `git()` helper already avoids this with `rstrip("\n")`
  only; `touched_files()` here does the same instead of calling the shared
  `.strip()`-based `run()`. Second, found writing the apprun
  self-registration: the SIGTERM handler was reentrant. `apprun stop`'s
  `terminate()` sends this exact pid a redundant self-targeted SIGTERM as
  its first move, which re-entered the handler *while still blocked inside
  the first call*, spawning a second `apprun stop`, which sent a third
  SIGTERM, recursing without bound — confirmed as an unbounded nested
  subprocess spawn via a 164KB traceback that never let the registry write
  land. Fixed by ignoring SIGTERM the moment shutdown starts
  (`signal.signal(SIGTERM, SIG_IGN)` before the blocking call); apprun's own
  8s SIGTERM-then-SIGKILL timeout still ends the process deterministically,
  since SIGKILL can't be ignored — shutdown is correct but takes that long,
  an artifact of reusing `apprun stop`'s kill-and-close semantics for a
  process closing its own entry, not a defect at this call site.

- **The Tower** (concept 07, accepted same day — all three steps). His ask: "a
  live app that's feeding off of these sessions and showing me how the autopilot
  is handling things." Concept drawn with the day's real sessions: a live graph
  whose message edges are real (cross-session messages verified observable in
  transcripts), holding patterns from contested surfaces, purple edges to the
  wall with wait ages, a per-surface pipeline with an "at the wall" row that is
  exactly his to-do list, an event ticker, and the day's question count in the
  header. Local-only by rule — it reads private transcripts.

  Step 1 built the same hour: `pulse --serve` — the pulse page on a loopback
  port, re-rendered every 10s, auto-refreshing. Steps 2 (the Tower screen) and
  3 (message edges + click-through) cut as vertical issues for the autopilot.

- **A question to the user is a cost — and Autopilot** (enacts proposal 04,
  decided by instruction). the sponsor: sessions were all asking him whether to
  message the other issue — "this is something that's not my problem"; and:
  "these things should run automatically with minimum input from my side."

  Diagnosed by measurement, not intuition: **52 questions across five
  finance-tracker sessions** (one asked 29). Every category traced to a rule
  that mandated asking or to the absence of any rule pricing a question. The
  worst was our own: proposal 02's resolution required his yes before any
  cross-session message — written the day *before* proposal 05 made issue
  coordination the AI's job. The sessions were obeying the rules exactly.
  **No new agent needed; an agent on top of ask-mandating rules would also ask.**

  Fixes: the approval requirement on cross-session coordination is corrected in
  place (send, log in AGENT-LOG.md, tell him in the digest); a single test now
  gates every question (would the answer change what he sees at a look, or is it
  reserved — else decide, record one line, proceed); the requirements engineer's
  "ask the sponsor rather than assume" is retired for "reason it out" (it was
  the largest single source); the design engineer's route-to-sponsor now stops
  at the requirements engineer; and the quality manager counts unnecessary
  questions at the gate — three across tasks is an instructions-are-wrong
  finding, the same mechanism as recurring lessons. Proposal 04 is marked
  accepted with his words recorded as the decision; the PR carrying this is
  the correction point if that reading is wrong.

  Baseline recorded for re-measurement: 52 questions / 5 sessions on
  2026-08-05. The target is not zero — it is zero *unnecessary*.

- **The Idea Lab** (research 06, accepted same day; direction: the funnel with a
  tournament heart). the sponsor's ask: "I can just tell the idea. It should run
  multiple iterations to make the idea finer and finer, and then let me know" —
  a v2, kept deliberately separate from these rules. Deep research first, per
  the research-in-management-sessions rule.

  The finding that shapes the design: **an idea polishing itself gets worse, not
  finer.** Models cannot reliably detect their own mistakes without external
  signals (they can correct a flagged one — a different skill); refinement
  plateaus in 3–5 rounds; iteration anchors on the first framing; and generated
  ideas grow more similar over generations, not more diverse. So the design
  question is where the external signal enters each round. Surveyed: critic
  loops (the floor), persona panels (diversity bounded by who is in the room),
  Google's Co-Scientist tournament (pairwise Elo + evolution, Nature-validated —
  the strongest published pattern), and Sakana's AI Scientist as the cautionary
  tale (42% failure rate, novelty checks fooled by keyword search).

  Accepted shape: expand the idea into 8–12 genuinely different interpretations;
  ground each with real fetched-and-read research (the one unskippable stage);
  select pairwise, keeping an archive of interesting losers; evolve winners
  until two rounds change nothing; then one document back — the refined idea,
  its two strongest rivals, and what was killed and why.

  Built the same day as `../idea-lab/` — its own folder and repo, LAB-RULES.md
  as the whole rulebook, no remote yet. One touchpoint with v1: the Lab's
  output is proposal-shaped and enters at L1. It replaces the blank page, not
  the pipeline. First trial waits for a real idea, which is his to bring.

- **The user owns features; the AI owns issues** (proposal 05, accepted same
  day). the sponsor: "at the end of the day I am worried about the feature, not the
  issue — issues are there to have parallel task, divide and conquer. It's not to
  increase my overhead that I have to trigger each and every issue." He also
  reported refereeing race conditions between finance-tracker's #30 and #31.

  Researched rather than assumed, and the finding is that **the collision was
  created at decomposition time, months before either session started.** #30 is
  "Desktop Clerk: Ask **backend**" and #31 is "Desktop Clerk: Ticket Rail + seam
  + Ask **dock layout**" — the server side and the screen side of one capability,
  labelled `backend` and `ui`. Four of the 25 open issues are one feature, cut
  backend/ui/backend/ui. That is **horizontal slicing**, and the literature is
  unambiguous about it: such slices "can't deliver value without interaction or
  integration with other layers" and make dependency management intricate by
  construction. Vertical slices — end to end, screen through to store — stay
  independent and testable.

  The overhead is also arithmetic, not temperament: coordination paths grow as
  **n(n−1)/2**, so six issues in flight is fifteen possible collisions, and he
  was the only node that could see all six. Every one resolved through him. The
  counter-intuitive half is that limiting work in progress *raises* throughput.

  So: **this narrows the whole 2026-08-02 issue-lifecycle section from issues to
  features** — a deliberate reversal, flagged rather than slipped in. Creating,
  sequencing, handing off and closing issues moves to the AI; proposing,
  approving, seeing and closing *features* stays his. Issues are cut vertically,
  one in flight per surface, with dependencies recorded at decomposition rather
  than discovered on collision.

  **He asked whether this needs a ninth agent. It doesn't** — decomposition and
  sequencing are already the project manager's job by definition; it had no
  authority because the rules gave every issue decision to him. Adding an agent
  to do work the project manager is defined to do but forbidden from doing would
  treat the symptom. What is genuinely missing is a *view*: nothing shows a
  feature and its issues together, which is why #30 and #31 were invisible.

  Also, separately: **stop labelling rules with codes.** "if you're telling me
  this d one, d two, some jargons need to be figured out, I cannot figure them
  out." Proposal 05 is written entirely as sentences; codes belong in the files,
  not in what reaches him.

## 2026-08-04

- **Loops, research triggers, and where parallel is safe** (proposal 03, accepted
  same day). the sponsor asked what loops back, when research fires, and where
  parallel work is possible. Reading the rules for *return* paths rather than
  forward ones found the workflow documented as almost one-directional: **three
  loops stated here, four buried in agent definitions the project manager never
  reads, six that should exist and didn't.**

  The worst: **every failure routed to the code engineer.** "This approach is
  wrong" and "this line is wrong" were procedurally identical, both landing with
  the person whose job is to make the code pass — which is how a wrong approach
  gets patched until it passes. The gate now names its destination (`code`,
  `design`, `research`), recommends rather than authorises, and every loop is
  bounded at two returns.

  **Research had no trigger at all** — "optional and run only when the task needs
  them", with the tier and the agent each citing the other. Four checkable
  triggers now. But the real finding is structural: **a task session is created
  *from* an accepted proposal**, so by the time one exists the direction is
  already chosen and the only honest thing left is writing down what was decided.
  That is why requirements work is visible and research isn't. Measured:
  management sessions had made **three specialist agent calls in their entire
  history, against thirty in task sessions**. Research now belongs to the
  management session, before a proposal exists.

  **Parallelism needed no new principle** — the tool grants already answered it.
  Read-only roles fan out freely; writing roles run one per *artifact*, not per
  task; sequence is set by dependency, not ceremony.

  Stepping back on the sponsor's review added the class that the first pass missed
  entirely: **learning loops**, which correct the system rather than the work.
  A recurring lesson escalates on the third occurrence (the quality manager
  counts, it cannot fix — agent definitions are his); promotion is a return to
  requirements, not a checklist; the outermost loop from shipped software to a
  finding is drawn at last; and — found by checking pockets, whose register held
  **3 accepted, 11 proposed, 0 built** — an accepted proposal that was never
  built now resurfaces, because `accepted` looks like *done* and means *owed*.

  Thirteen loops are drawn in `docs/workflow.html`, coloured by class, with a key.
  The page no longer shows a straight line, which was a picture of a workflow
  nobody has.

- **Working alongside other sessions** (proposal 02, accepted same day) — plus
  `bin/whoelse`. the sponsor asked how to stop parallel sessions reaching different
  conclusions and conflicting later. Measuring finance-tracker before answering
  changed the answer: **43 uncommitted files across seven parallel worktrees,
  none of them ahead of `main`**, and **seven files held by more than one
  session** — `nicegui_app/pages/ledger.py` by four. Four different uncommitted
  rewrites of one screen. The collision is already built; it just hasn't landed.

  Nobody did anything wrong. The worktree rule worked exactly as designed and
  stopped them overwriting each other live — **it was never designed to stop them
  diverging**, and no step anywhere asked *who else is working here*.

  Six rules. Look before you start; **overlap is a stop, not a warning** (a file
  another session holds is not yours to edit, same principle as a port you didn't
  start); inform the owning session rather than duplicating it; **commit or it
  doesn't exist**; parallelism granted **per surface, not per issue** — four
  issues touching `ledger.py` were never four parallel tasks, they were one queue
  nobody drew; and R6, added when the sponsor reviewed the draft and caught that
  *informing is not handover*: a finding landing on another task's surface gets
  responsibility assigned explicitly — finder keeps it, owner takes it, or
  neither — recorded against both issues. That closes silent absorption and
  mutual drop, which were both wide open.

  `bin/whoelse` reads the three places that already knew and nobody consulted:
  `git worktree list`, a `git status` in each, and whether any of it is ahead of
  `main`. Three of the four capabilities this needed already existed — listing
  sessions, messaging a session, per-worktree status — and had never been run.
  The gap was a step in the workflow that says *look*.

  Four open questions were not answered separately, so the document's stated
  positions were applied and recorded in it: overlap **blocks**; the handover
  message is **drafted for him to approve**, since it arrives in his name
  elsewhere; R5 compares surfaces **per batch**, before sessions are opened; and
  **he assigns** an R6 handover, since it is a scope change and those escalate.

  The 43 files were left untouched on his instruction. `whoelse --contested` now
  reports that state on demand rather than requiring someone to go looking.

- **`docs/workflow.html` — the whole workflow on one page, and a rule that keeps
  it true.** the sponsor asked for a bird's-eye view. `CLAUDE-workflow.md` is now
  long and reads in the order it was *written*, not the order work *happens* —
  which is fine as an authority and useless as a map. The page walks idea →
  merged in actual sequence, colour-coded by who acts (you / project manager /
  gate), then: who decides what, the eight agents with their real tool grants,
  the ceremony tiers, the run-identity ports, where every record gets written and
  by whom, and the two tools' commands. A full-page PNG sits beside it, per the
  existing report rule.

  The maintenance half is the part that matters, and it is now a rule rather than
  an intention: **the page is derived from `CLAUDE-workflow.md`** — where they
  disagree that file wins — and **any PR that changes the shared rules updates
  this page and its version stamp in the same PR.** Not as a follow-up. A
  bird's-eye view that has quietly drifted is worse than none, because it is
  trusted at a glance and read without suspicion; a stale map is the version that
  gets believed.

  Every tool-grant row was checked against the agent files' frontmatter rather
  than written from memory. PNG: headless Chrome at 2× into a 20000px-tall
  window, then a PIL crop that scans upward for the last row differing from the
  page background — the window height is a ceiling, not a measurement, so
  cropping is what makes it a page rather than a page plus a mile of empty.

- **How a proposal is delivered — artifact, then buttons** (proposal 01,
  accepted same day; `docs/proposals/` starts here). the sponsor's report: in pockets
  he had to ask for the rendered view and the decision buttons **every single
  time**; in finance-tracker he never did. Checking the two explained it, and it
  wasn't care or effort — finance-tracker has `docs/proposals/`, 13 numbered
  committed HTML files with statuses and an index. **Pockets has none.** Its
  three key proposals are `claude.ai` artifact URLs pasted into `CLAUDE.md`, and
  **two of the three have no local copy at all** — so the app's entire product
  direction depends on links that can rot, and the repo would not notice. With no
  convention, delivery had to be negotiated each time, and being the convention
  himself is what made it feel like work.

  Four rules now: a proposal is a rendered HTML artifact, never chat prose; the
  **committed copy exists before the artifact is shown** (the artifact is the
  view, the repo is the record — rule 1 without this just makes prettier things
  that still vanish); delivery is followed immediately by a decision prompt with
  buttons; and one decision per prompt, since a bundled question gets a bundled
  answer. A default button set is fixed — Accept / Amend / Reject / Show me
  first — so the options aren't reinvented vague each time.

  Two of his three answers refined or overrode the recommendation. **Buttons
  appear even when there is nothing to decide yet**, option "noted" if need be —
  and his reasoning is better than mine was: an absent prompt is ambiguous, and
  he should never have to work out whether he is being asked something.
  **Reports, findings and gate results get the artifact but not the prompt** —
  that restraint is what keeps buttons meaningful rather than something to click
  past. And **pockets backfills all three** existing proposals rather than
  applying the convention only to new work, which is the only thing that protects
  what is already there. That backfill is pockets' work, raised as a draft issue,
  not done from here.

- **Cleanup is now scoped by ownership**, in `CLAUDE-workflow.md`'s "Leave
  nothing running" section (retitled "— and stop only what you started").
  Two halves. The first restates the existing rule at **session** scope rather
  than per-agent: agents within a task can share a running copy, but the task
  does not end with it still up, and the project manager is accountable for
  that. The second is the new half and the reason the sponsor asked: **an agent
  stops only what its own session started.** Anything else running belongs to
  someone — the user reviewing a build, or a parallel session mid-validation —
  and killing it takes their work away silently. So cleanup is targeted (by
  recorded PID and port), never a sweep: no `pkill -f`, no `killall`, no
  clearing a port range on principle, and a port in your own range that you
  didn't start is a collision to report rather than to reclaim.

  This also demotes the stable copy from an exception to a *case* of the rule —
  no session started it, so no session stops it. Behaviour change for adopted
  projects: previously a tidy-minded agent could have justified killing a stray
  server it found; now that is explicitly wrong, and leaving a stranger's copy
  running is the correct outcome.

  The same wording went into the three agent definitions that actually start
  instances — `code-engineer`, `test-engineer`, `quality-manager` — because all
  three still carried "the one exception is the stable copy", which the rule
  above demotes. An agent reading only its own file would otherwise have kept
  the framing this change exists to replace.

- **`bin/rulecheck` — a session checks it is on the current rules before doing
  anything.** the sponsor's ask, and the reason is in the ask: he kept having to say
  "check common rules" again. These rules changed **five times today alone**, so
  a session working from what it read earlier is following a version that no
  longer exists, and nothing told it so.

  The version is `<commit-count>-<short-sha>` — the count orders it, the sha
  identifies it exactly. A project records the one it last aligned with in
  `.common-rules-version` at its root, **committed**, so a worktree checkout
  carries it automatically and needs no stamp of its own. Exit 0 aligned, 1
  behind, 2 cannot tell — and "cannot tell" means re-read in full, not "probably
  fine".

  The part that makes it worth running rather than just informative: it prints
  **what changed**, by diffing `CHANGELOG.md` between the two commits, not merely
  that something did. A session then reads the sections those touch. `--align`
  is deliberately a separate act after reading — it is a claim that this session
  knows the current rules, and a false claim there is worse than no stamp, since
  the next session inherits it and skips the check.

  Documented with a `SessionStart` hook per project (`rulecheck --quiet`),
  because the rule as written still relies on a session remembering — which is
  the exact weakness it exists to remove. Adding that hook is per-project work
  and hasn't been done. Neither project has ever recorded a version, so both read
  as never-aligned until they do.

- **`proposal-auditor`, an eighth agent — so L2 isn't the project manager's own
  opinion.** the sponsor's question, and it went straight at the weakness flagged in
  the L2 rule below: the project manager would be approving output from a
  pipeline it commissioned itself. So the comparison is done by someone else.

  The auditor reads the accepted proposal, `REQUIREMENTS.md` and the design spec,
  and classifies **every** divergence: `faithful`, `elaboration` (detail the
  proposal implied — what this work is *for*, and L2's to approve), `drift`
  (something the proposal decided, now changed — the sponsor's), `silent
  decision` (a decision the proposal never made — also the sponsor's), and `gap`
  (a proposal decision the requirements don't cover — back to requirements, and
  not ready for L2 at all). Two of those map onto two of the four escalation
  triggers below, which turns L2 from a judgment call into something acted on
  evidence.

  **Deliberately not the quality manager**, which was the tempting answer. That
  agent would approve the criteria at L2 and then gate the built work against
  those same criteria — marking its own homework where independence matters most.
  The principle already written for agent definitions carries over: an agent that
  approved the specs it reviews against is no longer an independent check. The
  two questions also differ in kind — the gate runs the thing and checks the
  outcome; this compares two documents against a third and judges fidelity of
  intent.

  Read-only (`Read`, `Grep`, `Glob` — no `Bash`, no `Write`), decides nothing,
  approves nothing. Its definition names the three quiet ways it fails:
  summarising instead of quoting both sides, looking only at what was *added*
  rather than what was silently dropped, and inventing a reading where the
  proposal was ambiguous — when the ambiguity is itself the finding.

  Costs, stated: an eighth agent against this file's own warning that
  full-ceremony pipelines can reduce correctness — mitigated by scoping it to
  post-acceptance work only, so a small fix pays nothing. And it cannot catch a
  proposal that was vague to begin with; it can only report that it was.

- **After acceptance: requirements, then design, then L2 — never straight to
  code.** the sponsor's rule, and it **corrects the paragraph merged a few hours
  earlier** which said a complete brief meant the upstream roles could be skipped
  and the tier was small-fix. Wrong, and the correction is stated in place rather
  than quietly edited: **an accepted proposal is not settled requirements.** It
  is a decision about direction, argued in prose — the input to requirements
  work, not a replacement for it.

  So acceptance now starts a fixed sequence: `requirements-engineer` →
  `design-engineer` → **L2** → code, test, gate. **L1 is the sponsor accepting the
  proposal; L2 is the project manager accepting the requirements and design
  produced from it** — two decisions about two artifacts. Collapsed, the second
  is never made by anyone; it gets inferred one file at a time by whoever writes
  the code.

  His reasoning, and it is the right one: the code agent will not expand
  requirements and design properly. Not a flaw in that agent — it is being asked
  to do two jobs whose instincts conflict, so given a gap it fills it in passing,
  in whatever shape is easiest to build. The decision then exists only as code,
  with nothing written down for the test engineer to check or the gate to hold it
  to. **An inferred requirement is an invisible one.**

  Four things escalate past L2 to him, and none are judgment calls: the work
  contradicts what the proposal decided; scope moves; a decision surfaces the
  proposal never made; or it turns out materially larger than implied. Skipping
  design for work with no visible surface is allowed and must be **said out loud
  and recorded in `AGENT-LOG.md`**, like a skipped gate — silence is what makes a
  skip indistinguishable from an oversight.

  He pointed at **issue #31** and it is worth keeping, because the cost was
  total. Its brief went from proposal 07 straight to "Implement" for the most
  design-dependent task in the batch — a rail, a seam and a dock whose entire
  point was that the boundary between confirming a write and asking a question be
  obvious at a glance. No `REQUIREMENTS.md`, no screen spec, a layout problem
  handed over as prose. The session built all of it itself over 256 messages;
  the sponsor intervened; the session replied *"You're right, I broke the rule that
  matters most here"* and **reverted all seven of its changes**. A whole session
  discarded. And the rework still ran only `code-engineer` — being told to use
  the agents did not produce requirements or design work, because nobody had said
  the proposal wasn't already the requirements.

  Enforced where it bites rather than only in prose: `code-engineer` now refuses
  to start from a proposal and must say what is missing; `requirements-engineer`
  states when its output is post-acceptance and that L2 is still owed;
  `design-engineer` must name anything belonging to the sponsor rather than to
  L2. The brief template was rewritten — it previously said "Tier: small fix" and
  named only the code engineer and gate, which would have reproduced #31 exactly.

- **Named the dispatch mechanism, and fixed the briefs that bypassed it.**
  the sponsor asked why finance-tracker's issue sessions weren't using the agents.
  They weren't: **#30, #31, #32, #35, #36 and #37 made zero agent calls** and
  implemented everything with `Edit` and `Bash` — which means **six merged
  features never saw a pre-merge gate.** The same project's open-ended session
  (`issue-27-person-dossier`) made eighteen calls across all six roles, so the
  definitions, the symlink and registration were never the problem. All six read
  this file first. They read the rule and did not follow it.

  Three causes, and the first is embarrassing: **this file named the roles and
  never named the mechanism.** Exact commands for `EnterWorktree` and `apprun`,
  and for the one behaviour the whole structure depends on, a table. `Agent` and
  `subagent_type` appeared zero times. Now they appear, with the invocation
  written out and a behavioural test that can be applied mid-task: *if this
  session is calling `Edit`, it is no longer the project manager.*

  Second, **the brief is the trap.** "Implement issue #36 … acceptance criteria:
  …" *is* a code-engineer task brief, and a session handed one executes it,
  because the live instruction beats a file it was told to go read. The fix is at
  the source: a session brief now opens "Project-manage", states the tier and
  names the agent set before any task detail. A complete brief is a reason the
  *upstream* roles can be skipped, never a reason to skip the gate — settled
  requirements make the work more checkable, not less.

  Third, **the step existed here and not in the artifact that starts the work.**
  The rules already said the PM names which agents run; none of the six briefs
  did. A rule that only lives in a file nobody consults at the deciding moment
  is not in force.

  Also fixed: those briefs pointed at `../common-rules/CLAUDE-workflow.md`, which
  **does not resolve from a worktree** — and a worktree is the first action on
  any project repo. The sessions recovered by hunting for the absolute path,
  which is luck. Absolute paths now, and it is logged as a gotcha alongside a
  second one this investigation produced: `~/.agent-data/projects/` directories start
  with `-`, so a glob'd `grep` reads them as flags, finds nothing, and does not
  error — it briefly produced a confident and completely wrong conclusion about
  which sessions had read this file.

  **Not fixed here, because it isn't this repo's file**: finance-tracker's own
  `CLAUDE.md` says "the sponsor is project manager here, **the AI is the developer**"
  — singular, and it is the file that auto-loads, while this one is read only
  when a prompt asks. It reads as permission for exactly the behaviour above.
  Raised separately as an issue draft.

- **`ASKS.md` — track what he asks for, propose the pattern.** His point, and it
  is a fair one: almost every rule in `CLAUDE-workflow.md` started as him asking
  for something in a chat, and most were asked more than once, in different
  projects, before anyone noticed they were the same ask. The rule existed as a
  pattern in his instructions long before it existed as a rule, and until then
  every session had to be told again.

  So sessions log instructions about *how work is done* — not what to build; an
  export button is a requirement, "show me a mockup first" is an ask — and
  corrections especially, since a reversal says more about what he wants than
  the original instruction did. When entries rhyme, propose it: not on a count,
  but when the general form fits in one sentence and covers two or more distinct
  entries. **Amending an existing rule is usually the right shape**, because most
  patterns turn out to be a rule that didn't reach far enough, and a second
  section saying nearly the same thing is how this file becomes unreadable.

  Written with its own failure mode stated in the text, because it is a real
  one: the rule rewards finding patterns, and a session wanting to look useful
  can manufacture one from any two instructions. Those rules have no felt problem
  behind them and are the ones followed literally and wrongly. A pattern nobody
  was hurt by is not worth a rule.

  Backfilled with 15 entries from this changelog and the common-rules session,
  and two patterns fell straight out — both of which the file argues should be
  *amendments*, not new sections. First: **he wants the state of things visible
  at a glance** (the diagnostic log, run badges, one stable copy, closing
  instances, a clean copy, a reserved icon, approving a PR without opening git —
  seven entries across four surfaces, each ruled individually, the general form
  never written down, which is exactly why each new surface needed its own ask).
  Second: **show him the thing, don't describe it** (mockups early, an image of
  the doc page, a demo before approval, and the surviving half of the deprecated
  PR #6 rule) — already stated in three places that don't reference each other.

- **Offer a demo before asking for the yes.** A draft issue is a paragraph of
  text, and approving it from text alone means deciding about a screen that
  hasn't been looked at in weeks. So the project manager now offers to *show*
  the thing first — of a draft issue, and of any proposal about an existing
  surface. The demo is of what is there now, not of the fix; nothing is built
  yet, and its job is to put the sponsor in front of the real screen so he decides
  against it rather than against a description.

  Deliberately **an offer, not a gate**: "just approve it" is a complete answer,
  and the rule is satisfied by having given the choice. Two things make an offer
  worth taking — navigation click by click in the app's own words ("Sidebar →
  Ledger, Subscriptions tab, the Safeguard row"), and **no new window where the
  clean copy will do**, since starting a second copy to show what the first one
  already shows rebuilds the exact pile he complained about an hour earlier.

  This collides with the cleanup rule directly, so the carve-out is explicit and
  mechanical: a copy started **for the user** is marked `--demo` in the registry,
  survives a blanket `apprun stop --all`, and prints a line telling the session
  to say in its report that it left it up and where. Closing the window someone
  is still reading is precisely the failure the ownership rules exist to prevent,
  and end-of-task cleanup is the easiest place to commit it by reflex.

- **`bin/apprun`, a run registry — and the reason it exists.** the sponsor reported
  still seeing a lot of windows open despite the rule above. Checking the
  machine explained why: it was *clean* — one server (stable, :8502), one Safari
  window on it, nothing in the test or proto ranges. The sessions had stopped
  their servers correctly. **The windows aren't the servers.** Every rule we had
  talked about processes and ports; a NiceGUI launch opens a browser window, and
  killing the server leaves it there, dead, still titled like the app. Ten
  compliant sessions leave ten windows. So cleanup now closes the window too,
  matched on the exact `127.0.0.1:<port>` of the instance being stopped.

  Two further gaps the same check exposed. **Ownership was unenforceable** —
  nothing recorded who started what, so an agent could believe it was following
  "stop only what you started" while the pile grew. And **the ownership rule made
  orphans permanent**: when a session dies its instances belong to nobody, so
  under the rule as written nothing could ever stop them. Both are fixed by the
  registry: entries carry `CLAUDE_CODE_SESSION_ID` and that session's pid, so
  ownership is a lookup and "is the owner still alive" is a `kill -0` — exact,
  not a heuristic. An orphan is the one category a stranger may close, and only
  with the sponsor's explicit yes, because one of those windows may be the one he is
  looking at. `stop` declines a live stranger's copy, an orphan, and the stable
  copy, each with the reason.

  Judgment call worth flagging: this is the first executable in a folder that has
  only ever held rules. Written because "each agent hand-rolls the bookkeeping"
  is precisely how the drift returns — but it is a widening of what this repo is,
  and reversible if the sponsor would rather it lived in a project.

- **There is always a clean copy to open.** Protecting the stable copy is not the
  same as guaranteeing one exists, and only the second helps when he just wants
  to open the app. His call on timing: **refreshed from `main` after a feature
  merges** — the moment the work is integrated, gated and merged, so a rebuild
  carries the new feature and nothing half-finished. Not at session start, not
  mid-task. A merge that leaves the installed app on last week's build has
  finished the git work and not the task. `apprun sweep` says `NO CLEAN COPY
  RUNNING` outright, because that failure is otherwise silent until he goes to
  open the app and finds nothing there.

- **The final app gets its own reserved icon.** Badges and window titles only
  help once a window is open and being read; the Dock and Cmd-Tab show an icon,
  and if every build shares one, he is back to guessing which of five identical
  tiles is real. So one icon is reserved for the installed stable copy and used
  by nothing else, with test and proto builds visibly different at Dock size. His
  prompt was that the current one doesn't sit well — and it is worse than a taste
  problem: finance-tracker's `icon-512.png` is a gold **W**, left over from
  "Wealth Tracker", a name the app hasn't had since it became Sangam in Jul 2026.
  The one tile that should be unmistakable currently says the wrong thing.
  Drawing the replacement is design work belonging to finance-tracker, not here;
  what this file adds is the rule that the reserved icon exists and that stale
  branding on it is a finding, not something to live with.

## 2026-08-03

- **SUPERSEDED, same day, by the proposal framework below.** Kept because the
  failure it was written from is real and the replacement has to keep covering
  it. The gap it named: requirements and design artifacts need a sponsor yes,
  not just the initial scope agreement. Found on
  finance-tracker's `person-dossier` task: a design-engineer's screen spec
  went straight to a code-engineer with no pause, so the sponsor only saw
  what had been designed after it was already built. Agreeing an issue is
  worth working on is a different decision from approving the specific
  requirements or design spec produced for it, and the second one had no
  gate. This is the project manager's job specifically — only it has a
  channel to the sponsor, so a rule written into the agent files alone would
  have nothing to act on — but `requirements-engineer.md`/`design-engineer.md`
  now each close their report format with an explicit statement that their
  artifact isn't self-approving, reinforcing the checkpoint at the point
  it's easiest to skip. A small, already-approved revision (a typo fix)
  doesn't need to go back through this — same judgment as the re-gate
  policy above.

  **Why it was superseded within the hour**: it gated every role transition,
  which would have meant four sequential approvals per feature — and the sponsor's
  call was one proposal per task instead. His reasoning, and the research
  agrees: a chain of gates a single sponsor approves in sequence decays into
  rubber stamps, and the defence large organisations use for that (a different
  approver at each stage) doesn't exist here. It was also incomplete — it added
  checkpoints without any of the tracking around them: no status, no
  traceability, nothing about what happens after a yes. The single-gate rule
  still prevents the exact failure this was written from, and keeps its better
  half: relaying means showing the artifact, not summarising that one exists.

- **A proposal framework**, adopted by every project referencing this file.
  Prompted by finance-tracker, where 7 numbered proposals carried no status at
  all — and where researching it turned up that tracking was already being
  improvised in three places that disagreed: proposal 06 printing "Proposal 08"
  on its own page, status smuggled into brand lines with no field to hold it,
  `CLAUDE-checklist.md` keeping its own parallel record, and proposal 04 having
  reversed its own conclusion by editing itself.

  The load-bearing decision is the sponsor's, and it went against what was
  proposed: **one proposal per topic, not one per role — and not one per
  session.** A proposal stays open across conversations, gaining sections,
  until he decides; "one per task" was the first wording and it invited
  treating each new chat as a new task, which quietly rebuilds the four-proposal
  chain the rule exists to prevent. However many agents
  run, they contribute sections and the user decides once. The four-stage
  chain was rejected because stage-gate research is consistent that a gate
  which isn't a real decision point is worse than none — and the defence large
  organisations use, a different approver per stage, is unavailable to a single
  sponsor. One gate can't rubber-stamp itself.

  The rest: six statuses each naming an action (no `deferred`, no
  `partly-accepted` — both decay); status in the document with the index
  regenerated from it, never the reverse; one number sequence with type as a
  field; conclusions immutable while labels and links stay fixable;
  traceability one-way from the cheap-to-edit side. On acceptance a draft issue
  is written for the user and a session is *offered* — named
  `<app> - <no> - <description>` — never started, since picking what to work on
  is his call.

- **Three amendments from the first day of real use**, all from things that
  actually happened rather than anticipated ones. (1) **The user can merge a
  PR from the chat** — the AI summarises what's in it and merges on the word,
  so visiting github.com is optional; it still never merges unprompted, and
  must summarise first or "merge it" becomes a rubber stamp. (2) **`LESSONS.md`
  now has a specified format**, because two sessions created the file
  independently in the same project on the same day and produced incompatible
  layouts — the rule had named the entry types but never the shape. Existing
  entries in the old layout stay as they are; append-only means not
  reformatting someone else's record either. (3) **A fix commit must touch a
  record file**, added to `code-engineer`: a commit that changes behaviour and
  updates nothing leaves the changelog asserting something false, and no test
  run can catch it. That gap recurred one commit after a gate named it, which
  is the signal it belongs in the agent's standing instructions rather than in
  another one-off correction.

- **Recorded the biggest caveat on the first task's result** in the story
  snapshot: none of the thirteen passes used the actual agent definitions.
  They were written mid-session and register at session start, so every pass
  ran as a general-purpose agent with the role's instructions pasted in. That
  preserved fresh context and the written boundaries, but not the tool
  grants — the real inspector cannot edit files at all, whereas a
  general-purpose agent is merely told not to. The shape was proven; the
  machinery that enforces it was not.

- **Added `docs/` and a running story**, with a **low-priority** rule adopted
  by every project referencing this file. the sponsor is a project manager by
  profession and wants to present this experience to fellow managers in a few
  weeks — the arc from a single chat doing everything, through building an
  agent team, to measuring and trimming it. `docs/story/README.md` holds the
  narrative in chapters, `docs/story/snapshots/` holds point-in-time records
  with real measured numbers, and `docs/` holds plain-language reports for
  someone who wasn't in the room (`ai-working-team.md` is the standard to
  match). Explicitly low priority: it never blocks a task, delays a merge, or
  justifies an extra agent pass — the raw facts already live in `AGENT-LOG.md`
  and the changelogs, so a snapshot can be written later from those. It lives
  here rather than in a project because the story is about the way of working,
  not about any one app. The rule requires snapshots to carry the parts that
  went badly and the mundane interruptions: a record of only smooth runs is
  useless for a presentation and worse than useless for learning.

- **Scoped the pull-request rule to this repo only** — projects keep
  worktree, checklist, merge on approval, with no PR. the sponsor's
  decision, made when the question came up on the first project branch
  after the PR rule landed. Written down explicitly because project
  sessions read `CLAUDE-workflow.md` too, and "every change goes
  through a pull request" reads as universal without the qualifier.

- **Rule changes here now go via branch and pull request**, with the sponsor
  merging — the AI never merges its own rule change. Prompted by noticing
  that the first batch of changes went straight to `main`, contradicting
  the no-direct-to-main rule stated in this same file. Worth the overhead
  on a solo repo because a diff reviews better than a chat summary, and
  because a bad rule here reaches every project silently. It also turns
  the reserved-for-the-user rule into a mechanism rather than a habit.
  No worktree for this repo — worktrees prevent build collisions and
  there is no build here. **One honest limit recorded with it**: because
  `~/.agent-data/agents` symlinks into `agents/`, an agent definition is live
  the moment it is saved, so for those files the PR is a record and a
  review surface, not a gate. Copy-on-merge would gate it but bring back
  the two-copies drift the symlink was adopted to remove.

- **First corrections from real use** — the improve-the-agents loop firing
  for the first time, on evidence from the `run-identity-badges` task in
  finance-tracker rather than on theory:
  - `code-engineer` must now **commit before reporting**. The gate found
    that branch at zero commits, having spent a full pass verifying work
    that existed only in a working tree, with every build stamped to a
    commit predating the change. No brief had said to commit — a process
    gap, so it becomes a standing rule instead of a per-task instruction.
  - `code-engineer` now treats **any value reaching generated code as
    untrusted**, branch names and labels included. A run-label written
    unquoted into a generated `.app` launcher gave arbitrary command
    execution on every launch, and was reported as working until an
    independent pass found it.
  - `quality-manager` now checks **commit state and merge-compatibility
    first**, not as a closing item — they cost seconds, and skipping them
    wasted an entire gate.
  - Added a **re-gate policy**: behaviour changes require another gate,
    documentation and commit-only changes do not, and `AGENT-LOG.md` must
    record when one was skipped. "The gate passed" and "the gate passed an
    earlier version of this branch" are different claims.
  - Not made a rule, but recorded: two of the four things that went wrong
    were the project manager's briefs, not the agents — a criterion written
    wrongly, and a missing instruction. The standing fix is to let
    `requirements-engineer` write criteria rather than the project manager
    improvising them.

- **This folder is now its own git repository** —
  `github-owner/emberline-ai-tracker` (private), created by the sponsor and adopted at
  his direction. It reverses the earlier "deliberately not a git
  repository" note, and the three places that asserted it (`README.md`,
  `CLAUDE.md`, and the closing section here) were corrected in the same
  change so they don't contradict reality. What has *not* changed is the
  reason the folder sits outside every project: these rules belong to none
  of them individually, and `apps/` still isn't a repo. `CHANGELOG.md`
  keeps its job — `git log` records that something changed, this file
  records what it was for, and it's still the thing to read first.

- Add **`AGENT-LOG.md`** — a per-project record of which agents ran, in
  what order, what each returned, and what it cost, written by the project
  manager because it is the only role that sees the whole sequence
  (agents cannot see each other). Directed by the sponsor, who wants to be
  able to look back and analyse how a task was actually run without
  reading a transcript. Two payoffs beyond the record itself: it is the
  evidence base for the improve-the-agents loop — a role whose findings
  keep getting disputed, or a gate that keeps missing the same class of
  problem, shows up here and nowhere else — and it makes the cost of
  ceremony legible, which is what tells you when a lighter tier would
  have done. Entries must include the parts that went badly; a log of
  only clean runs is worthless for analysis. Every entry names its project
  explicitly even though the file lives inside that project — tasks run
  from worktrees so the location isn't self-evident while writing, entries
  get pasted elsewhere, and collating several projects' logs to compare
  how tasks ran only works if each entry stands on its own. Each agent
  row also carries its own token count, tool-use count and wall-clock
  duration, plus a total row — the figures arrive in the agent's
  completion notification and are only visible at that moment, so they
  get written down as each agent returns rather than reconstructed
  afterwards from memory.

- **The seven agent definitions now live in `agents/` here**, with
  `~/.agent-data/agents` symlinked to it. They were sitting in `~/.agent-data/`,
  which has no version control — so the rules governing the agents had
  history while the agents themselves had none, which is precisely the
  gap this repo was created to close. Editing a file in `agents/` now
  edits the live agent, and the same reserved-for-the-user rule covers
  both. Worth remembering: they are machine-global, and they register at
  session start, so a mid-session change to one is invisible until the
  next session (found the hard way — the first attempt to invoke
  `code-engineer` failed because it had been written minutes earlier).

- Add **"Leave nothing running"** to the run-identity section, directed by
  the sponsor after watching the first real task go through the agents: any
  agent that starts an app instance must stop it before reporting, on the
  failure path included. Badges say which copy is which but do nothing to
  stop copies piling up, so without this the identity work only manages a
  mess it should have prevented. The stable copy is the deliberate
  exception — it stays up so there is always something to review. Mirrored
  into the `code-engineer`, `test-engineer` and `quality-manager`
  definitions, since those are the roles that actually start things.

- Add four sections to `CLAUDE-workflow.md`, all directed by the sponsor after
  reviewing two proposals and a decision register in the same conversation:
  **the agent roles and who improves them**, **project phases**, **telling
  running copies apart**, and **findings become well-formed issue drafts**.
  The short version of why: one session that plans, builds, tests and then
  certifies its own work has no independent check anywhere in it, and the
  published research on multi-agent development is consistent that a
  separate reviewer catches what a self-certifying implementer misses.
  Seven specialist agents now live in `~/.agent-data/agents/` and are governed
  by the same reserved-for-the-user rule as this folder, since an agent
  definition changes behaviour for every project at once.
- Three things in there are deliberate departures worth remembering:
  **there is no `project-manager.md`** (a subagent can't talk to the user,
  and deciding what escalates *is* that role's job, so it has to be the
  main session); **design is two roles** rather than one, because
  exploration and specification hold opposite stances and a single prompt
  holding both comes out timid; and **light ceremony is the default**,
  because full role pipelines measurably *reduced* correctness for most
  models tested — the tiers are a correction, not an efficiency measure.
- Honest caveat recorded at the time of writing: these rules describe
  something plausible, not something proven. No task had run through the
  agents when this was written. finance-tracker and pockets are the two
  pilots; expect the gate's checks and the artifact handoffs to be the
  first things that need correcting.

## 2026-08-02

- Add `CLAUDE.md` — a short pointer file so a session started with
  this folder as its own working directory (the sponsor wants to keep working
  on these rules directly, in a session separate from any one project)
  orients itself automatically: read `CLAUDE-workflow.md` first, and the
  edits-are-reserved-for-the-user rule applies here too.
- Expand "Confirmation gates" into "Issue lifecycle — the user is project
  manager, the AI is the developer": creating an issue is now reserved
  for the user (not just confirmed), scope and priority must be agreed
  before work starts, picking an issue is the user's call alone (the AI
  advises when asked "what's next" rather than self-selecting), added an
  explicit one-issue-at-a-time rule with an align-first exception for
  work that spans multiple issues, and closing stays reserved for the
  user. Also adds a new rule, directed by the user in the same
  conversation: editing any file in this folder (`CLAUDE-workflow.md`,
  `README.md`, this file) is itself reserved for the user — the AI
  surfaces what it noticed and asks, never edits here unprompted, since a
  change here silently affects every adopting project at once.
- **pockets** adopted `CLAUDE-workflow.md` (second adopter) — new repo
  created today with the pointer in its `CLAUDE.md` from the first
  commit, plus its own specifics (M0 harness commands, `data/` privacy
  rule, `worktree.baseRef: "head"` since it has no remote). Only the
  "Adopted so far" line changed here; no rule text was modified.
- Extracted `CLAUDE-workflow.md` from `finance-tracker/CLAUDE.md`'s "Git
  workflow" / "Issue tracking" / "Confirmation gates" sections — those
  rules turned out to be genuinely project-independent (worktree-per-task,
  the pre-merge checklist shape, the checklist-vs-issues mirror direction,
  the three confirmation gates), so keeping them duplicated inline in every
  project's `CLAUDE.md` would have meant hand-syncing every future change
  across projects. `finance-tracker/CLAUDE.md` now points here and keeps
  only its own specifics (test/build commands, its repo name, its `.env`/
  `finance_data/` gotchas). No other project has adopted this file yet.
## 2026-09-18 · 1.0.2 — state the Claude Code and Codex consumer boundary

The sponsor asked for the shared rules to be usable by both Claude Code and
Codex without two drifting interpretations. This patch release adds an
explicit consumer-neutral statement to `README.md` and
`CLAUDE-workflow.md`: the ledger, tracker, handoff, verification, and safety
contract is shared, while commands and UI are allowed to differ by consumer.

The PhotoVault tracker-template review remains a shared-template fix, not an
application-specific workaround. The five visual defects recorded in P30/P-14
are present as fixed in the current renderer and the regenerated Common Rules
tracker was checked in the browser.

This is not a Standard change: adopting projects do not gain a new required
workflow step; the distinction prevents Claude Code and Codex from reading the
same standard as two different rule sets.
## 2026-09-18 · 1.0.3 — responsive expanded tracker rows

Patch release for the shared tracker renderer.

- Keep tracker item IDs on one line so short identifiers do not break into
  vertical fragments.
- Allow long titles and `next:` guidance to wrap within their row instead of
  clipping at the right edge.
- Use a responsive flex fallback below 900px so expanded trees remain legible
  in narrow Claude Code and Codex browser panes.
- Regenerated and visually verified the PhotoVault app tracker with P70
  expanded.
## 2026-09-18 · 1.0.4 — tracker reading order and priority clarity

Patch release for the shared tracker information hierarchy.

- Move proposal scope controls next to the filter bar instead of leaving them
  after the history charts as a detached duplicate.
- Put the actionable priority queue immediately after the proposal tree and
  before historical progress charts.
- Rename “By urgency” to “Priority queue” and explain its grouping rule.
