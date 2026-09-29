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
reading every paragraph:

- `.verdict` for the one-line recommendation;
- `.big` containing `.stat` blocks for headline figures;
- `.tk` for comparisons, with a single-word verdict column such as `TAKE`,
  `LEAVE`, or `OPEN`;
- `.ev` directly beneath the claim it supports.

`bin/new-proposal` includes these primitives in every new page. Run
`bin/proposalcheck --project .` to receive a warning when a page has no table,
inline SVG, or headline-figure block before `Decisions`. The warning is
advisory for existing pages; no chart library or screenshot is required.
Inline SVG should use the page's CSS variables so it works in dark mode.

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
