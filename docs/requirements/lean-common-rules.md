# Lean Common Rules requirements

Approved by the sponsor on 4 October 2026. Proposal 33 item R-04 is the
authoritative delivery row; this file makes its acceptance contract easy to
review against code and tests.

## LR-01 — Session initialization

A fresh session performs one full warm-up. A running session uses reheat only
after compaction, resume, an explicit repository switch, or a relevant saved
state change. Repeating either command against the same project revision,
rules revision and ledger digest must return a compact unchanged result rather
than repeating the mandatory read and queue work.

## LR-02 — Review feedback and asks

Feedback given while one feature is awaiting sponsor review is an answer to
that open review. It updates the existing ask or review record instead of
creating a new ask row for every annotation. Genuinely new scope and decisions
still receive their own verbatim ask rows.

## LR-03 — Verification levels and receipts

Verification has three explicit levels:

1. development — formatting and affected/focused tests;
2. checkpoint — a coherent feature batch and its declared checkpoint gate;
3. release — the full merge/release gate and required independent evidence.

An unchanged repository revision plus an unchanged gate definition may reuse a
successful revision-bound receipt. A changed revision, gate definition or
declared input invalidates the receipt. PR, merge and release claims may never
reuse weaker development evidence.

## LR-04 — Ruflo lifecycle

Ruflo remains mandatory for meaningful feature bundles, delegated work,
cross-repository changes and releases. Micro-edits and individual review
comments do not become Ruflo items. The supported lifecycle is:

- `note`: store progress without a gate or worker dispatch;
- `ready`: run or record development evidence without the merge gate;
- `checkpoint`: run the checkpoint/merge gate once for the bundle, then store
  completion evidence and dispatch `testgaps` once;
- `land`: require release evidence and dispatch `testgaps` once at the release
  boundary.

Legacy `done` remains compatible but maps to `checkpoint`, is documented as a
compatibility alias, and never causes more than one gate for a bundled call.

## LR-05 — Review and communication batching

Visual review guidance requires related annotations to be reconciled into one
accepted behavior delta before implementation. Preview regeneration and live
verification happen once per coherent batch. Sponsor updates report milestones,
decisions, blockers and verified results rather than narrating every command.

## LR-06 — Compatibility and rollout

Existing projects retain their current gates and ledgers until they align to
the new release. Alignment must not overwrite uncommitted work. The three
running EisKaffee chats receive explicit rollout instructions naming their
current project/worktree and the new batching behavior. Other repositories are
updated by their owning sessions, never by the Common Rules release session.

## LR-07 — Release evidence

The change is not complete until focused tests, traceability/coherence checks,
an independent restricted-risk review, the full merge gate, a merged pull
request, a public semantic release and rollout receipts for the three target
chats are recorded.
