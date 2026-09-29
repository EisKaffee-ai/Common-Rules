# common-rules — orientation for a session working in this folder directly

This folder is not a project — it's shared workflow rules referenced by
every project under `apps/` (see `README.md`). If you're
reading this, a session was started with this folder as its working
directory specifically to edit these rules.

**Read `CLAUDE-workflow.md` first** — that's the actual rules content
(git worktree-per-task, the pre-merge checklist shape, issue tracking,
and the issue lifecycle). `README.md` explains how a project adopts it.
`CHANGELOG.md` is the change history in plain language — read it before
`git log`, which records that something changed but not what it was for.
This folder is its own git repository (`github-owner/emberline-ai-tracker`,
private), separate from every project's.

**The one rule that matters most for a session here**: per
`CLAUDE-workflow.md`'s own "Changing these shared rules" section, edits
to any file in this folder are reserved for the user. Don't fix a typo,
add a gotcha, or reword anything on your own initiative — surface what
you noticed and ask, then only edit once the user has explicitly
directed the change in that conversation. When you do make a change,
add a `CHANGELOG.md` entry explaining why, and flag it if it actually
changes behavior for an already-adopted project (not just wording).

<!-- common-rules:warmup -->
## Warm-up (common-rules proposal 19)

Start every session with `/warmup`, and run it again after a compaction. Read, in order: AGENTS.md → HANDOFF.md → docs/OPERATING-RULES.md → the ledger(s) in docs/proposals/NN-*.json → the latest docs/handovers/*-checkpoint.md → common-rules' CLAUDE-workflow.md.

The ledger is the record. A compaction summary is a paraphrase: quote rulings from disk.
<!-- /common-rules:warmup -->
