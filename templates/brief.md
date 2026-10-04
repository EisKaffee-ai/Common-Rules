[ruflo · {{TIER}} · {{MODEL}}] {{ITEM_ID}} {{TITLE}}

For a lettered part, {{ITEM_ID}} is the part id (e.g. W-10.B), not the item's.

CONTEXT
{{RECALL_HITS}}
{{CONTEXT_PACK}} -- written by the Haiku scout, templates/scout-brief.md, before this brief is sent.

Bundle form for small issues on one surface: one row per issue below, empty for a single-item brief.
ITEMS
{{BUNDLE_ITEMS}}

OWNS
{{OWNED_FILES}}

MUST
{{MUST_1}}
Reach {{VERIFY_LEVEL}} from the project's verification ladder ({{VERIFY_TOOL}}).
Read a file with the Read tool (`offset`/`limit`), never `cat` or `sed -n`.
Run the project's development level (`bin/gate development --project .`) while building. Run checkpoint/release verification only at those boundaries; an unchanged same-level receipt is reused. The declared gate uses `bin/quiet`, never a raw test runner. Never run the full merge gate after each small edit. Gates stay in the foreground, one blocking call, with the verdict read in the same turn. Never background it and poll.
This item's own gate is unchanged by whether the project declares a staging branch -- `bin/land` (the lead's call, not yours) decides where the branch lands; you never pass `--advance-staging` yourself (proposal 31, O-08; full rule in CLAUDE-workflow.md's gate section).
Stage ledger updates with `tracker stage` -- never `tracker set`, never `tracker ask`, never hand-editing its JSON. You never write the ledger or its page directly; the lead applies every staged change with `tracker apply-staged` when it merges your branch in (proposal 23, M-04).
In a bundle: one commit per issue, naming its id, one gate run, one PR closing all of them. A restricted item is never in a bundle -- it goes alone, on its own branch, with its own reviewer and its own gate run (proposal 26 C-02/C-03).
For visual work, collect the open review's comments before changing code, reconcile the complete interaction, then make one preview build for that feedback batch. Do not rebuild after each comment.

MUST NOT
{{MUST_NOT_1}}
Size the work yourself: this brief never carries the item's points (proposal 25, D3); `tracker route` is the lead's.
Hand-append AGENT-LOG.md or HANDOFF.md -- use `bin/spend agentlog --write` and `bin/remember`.
Run `tracker apply-staged` yourself, for any ledger, ever -- staging is as far as you go; applying staged changes is the lead's alone, even when no one else appears to be touching the same ledger right now (proposal 23, M-04).

OUTPUT
{{OUTPUT_1}}
Last line, exactly: HANDOFF: status=<done|blocked> commit=<sha> needs=<what the lead must do>

EFFORT
{{EFFORT_NOTE}}
