# The tracker and proposals

The tracker is generated from proposal ledgers. A ledger is the durable record
of what was proposed, decided, assigned, measured, and left for later.

## What the tracker can and cannot know

The host's native goal keeps a long-running chat oriented and helps it choose
the next task. Emberline does not infer completed work or sponsor instructions
from chat text alone. A completed task must have a ledger row with `status:
done` and a log/evidence entry; a sponsor instruction must be recorded as an
ask or deliberately linked to the item it became. Then regenerate the project
page. Chat steers execution; the ledger proves what happened.

An item may also be `deferred`. Deferral is terminal for the current plan,
green on the tracker, and requires a non-empty `deferred_reason`. It stays in
the ledger and history, but is excluded from active-work and blocker counts.
Reopening is deliberately explicit: use `tracker set LEDGER ITEM --status
in progress --reopen` (or another non-terminal status) so a deferred decision
cannot silently become active work.

For a project using the optional goal contract, the same outcome, constraints,
and verification criteria appear on the warm-up card and at the top of the
generated tracker. Editing the contract makes the page stale until it is
regenerated, exposing drift instead of silently publishing an old goal.

Warm-up validates every ledger to produce the summary, but its `Read in order:`
list intentionally excludes auto-discovered raw ledger JSON. This keeps chat
context small while preserving every ledger's status, open work, and
validation result on the card. Open a ledger only when its item is active.

## What a proposal contains

A proposal normally records:

- the outcome the work is trying to produce;
- items with stable IDs, owners, tags, value, and risk;
- dependencies and current status;
- asks, decisions, findings, and evidence;
- the next item that should be worked.

### Visual by default

A proposal is a decision page, not a transcript. Put a compact visual summary
before `Decisions` so the sponsor can understand the recommendation without
reading every paragraph. Choose the smallest form that answers the question:

- before / after for a change in state;
- option cards and `.tk` for a choice;
- a flow for data, control, or authority movement;
- a lifecycle for transitions and stop states;
- a hierarchy for ownership;
- a capability matrix for supported, partial, missing, and out-of-scope work;
- `.big` / `.stat` for measured size, speed, cost, or coverage;
- a status board for stable IDs, owners, dependencies, and remaining work.

`bin/new-proposal` includes these primitives in every new page. Run
`bin/proposalcheck --project .` to receive a warning when a page has no table,
inline SVG, or headline-figure block before `Decisions`. The warning is
advisory for existing pages; no chart library or screenshot is required.
Inline SVG uses the page's CSS variables, plus a semantic `title` and `desc`, so
it remains readable in dark mode and accessible without the drawing.

### Luna implementation context

The final section of a new proposal is `#luna-context`. It is collapsed for the
normal decision review, but it carries the deeper execution context that Luna or
any other implementation agent needs after acceptance:

```text
outcome + accepted decisions
scope in / scope out
repository ownership + implementation map
contracts and data + ordered steps
future implementation verification + risks and refusals
dependencies + open questions + completion evidence
```

The page also shows proposal state on two axes. The decision axis comes from
`proposal-status` plus the verbatim `Decided` block. The delivery axis comes
from ledger items, tests, review, and release receipts. The lifecycle rail is a
visual summary of those sources, not another field an agent may set independently.
The Luna context records the current state, allowed next state, transition
authority, required evidence, and any deferred or superseded reason.

The section is not a second proposal and not a transcript. It must agree with the
visual decision surface, name only repository facts that were verified, and mark
missing facts as `Unresolved — reason`. Proposed decisions are not implementation
authority. Proposal acceptance authorizes requirements and design work; it does
not prove that code, tests, review, or a release exists.

Creating, reviewing, and accepting the proposal itself does not require
executable tests. The proposal needs structural validation, a readable render,
sources, and the sponsor's recorded decision. Its Implementation verification
field describes the tests or observations that become due only after accepted
scope enters implementation; it does not claim those checks already ran.

The detailed authoring guide ships on demand with the `visual-proposal` skill at
`skills/visual-proposal/references/visual-language.md`.

### Guide-to-architecture traceability

When an item changes a supported capability, add a traceability row to its
proposal ledger. The row is deliberately explicit:

```text
requirement IDs → guide section → architecture section → implementation files
→ tests/commands → receipt or refusal → owner → status
```

The generated tracker renders these rows in its Traceability table. This makes
it possible to start from a user-facing promise, inspect the architecture
boundary and implementation, then verify the result or understand the named
refusal. A row is not a prose note: `bin/tracker validate` checks every link
field, the owner, the status, and the item it belongs to.

Keep the ledger as the source of truth. Use the supported tracker commands to
validate or render it rather than editing generated HTML by hand.

### Holistic feature and architecture traceability

`bin/traceability` is the stricter, project-wide view. It does not replace the
proposal ledger row above. It reads a reviewed project manifest at
`docs/common-rules/traceability.json`, scans every repository declared there,
checks the evidence, and generates one overall dashboard with a drill-down for
each feature.

The split is deliberate:

- Common Rules owns the Python validator, state calculations, freshness check,
  and HTML template.
- Each project owns its reviewed manifest, repository scan patterns, expected
  workflow, accepted implementation mappings, and evidence references.
- Machine checkout locations stay in the ignored
  `.common-rules/workspace.local.json` `checkouts` map, keyed by repository ID.

Stable IDs make every layer referable: `REQ-` for requirements, `WFN-` and
`WFE-` for workflow nodes and edges, `CODE-` for code anchors, `TEST-` and
`REPORT-` for test cases and reports, `ISSUE-` for issues, `RECEIPT-` for
receipts, and `MAP-` for end-to-end mappings. IDs are globally unique in the
manifest.

A code anchor names a repository, revision, path, and exactly one locator:

- `symbol` is strong evidence when the named declaration exists;
- `region` is strong evidence when its explicit START and END markers each
  exist exactly once and in order;
- `whole_file: true` is accepted but visibly labelled weak evidence.

Expected workflow nodes and edges conform only when their actual rows are
`accepted` and point to valid code anchors. A `proposed_ai` workflow row or
mapping remains visible as a finding and never contributes accepted coverage.
Test reports name their test-case results, source repository, source revision,
path, and timestamp; the latest report is shown for each feature. The referenced
report is JSON with the same `id` and `results` as its manifest row. For a fixed
revision, a dirty code or report path is refused instead of being mistaken for
committed evidence. Every test case in an accepted mapping must have a result
in the latest report.

Each feature carries the complete chain: requirements, expected and actual
workflow nodes and edges, code anchors, test cases and reports, issues,
receipts, and accepted mappings. Receipt `evidence_ids` must resolve to typed
evidence in that feature. Issue links are limited to HTTP(S).

Build and then enforce the view with:

```sh
bin/traceability build --project .
bin/traceability check --project .
```

`check` is read-only and fails when the manifest is unreviewed, a configured
checkout or scan is incomplete, an ID/reference/anchor/report is broken, the
expected and actual graphs differ, or the generated page is missing or stale.
It has no runtime AI dependency. See `tests/fixtures/traceability` for the
smallest complete manifest.

## The four views

- **Tree** shows the proposal hierarchy and dependencies.
- **Kanban** groups work by status, including the green terminal **Deferred**
  column.
- **Board** gives a card-oriented view of the current plan.
- **List** is the compact inspection view for filtering and scanning details.

Open the [live tracker](../proposals/tracker/index.html) to see the current
public record.

## A safe update loop

1. Identify the proposal and item you own.
2. Record the decision or status change in the ledger.
3. Run the relevant tracker validation.
4. Regenerate the tracker page.
5. Run the tests and review the diff.
6. Commit the ledger and generated page together.

To defer an item safely:

```sh
bin/tracker set docs/proposals/NN-title.json ITEM-01 \
  --status deferred --reason "out of scope for this release"
```

Generated pages are valuable evidence, but they are outputs. The JSON ledgers
and the workflow rules remain the authoritative inputs.
