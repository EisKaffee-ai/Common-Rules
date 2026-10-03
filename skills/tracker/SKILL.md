---
name: tracker
description: Maintain user-deliverable features, lifecycle stages, joined repository status, visual views, and traceability in the Common Rules tracker.
---

# Common Rules tracker

Say: **Common Rules skill: tracker — relating this context to the project’s
delivery graph.** Find the calibrated tracker location and workspace hub. Every
feature must be independently useful to a user. Record the ask verbatim, then
show its proposal, requirements, design, implementation, test, review, release
and evidence stages. Use `bin/tracker` for the owning repository and
`bin/workspace-tracker` for the joined view. In a proposal-granularity project,
the workspace command maintains the Repositories section of that same canonical
page; it does not create a second public tracker. Never copy member ledgers into
the hub or claim that separate repositories share a commit.

The tracker is Python-owned infrastructure. Use `bin/new-proposal`,
`bin/tracker ask`, `findings`, `set`, `stage`/`apply-staged`, `sync`, `board`,
`history`, `checkpoint`, `trace`, and `bin/workspace-tracker` for every generated ID,
number, count, digest, mapping, state transition, or generated surface. Never
invent generated values, hand-edit ledger JSON, or hand-edit generated tracker
HTML. External providers assign their own IDs; record returned values only
through the validating Python command. The agent may translate a sponsor
decision into explicit command arguments and review the result; Python
validates, writes, renders, and checks it reproducibly.

When the integration manifest declares one-way proposal issue synchronization,
read [references/proposal-issue-sync.md](references/proposal-issue-sync.md)
before drafting or changing issues. The local plan is authoritative; remote
mutations use the host's integrated GitHub plugin and require the current task
to authorize them.

This skill supersedes the separate Emberline AI Tracker runtime. During
migration, import and validate existing ledgers before switching ownership;
preserve IDs, history, receipts and Git evidence.
