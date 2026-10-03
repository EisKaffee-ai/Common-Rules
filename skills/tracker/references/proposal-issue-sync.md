# Proposal issue synchronization

Use this mode only when `.common-rules.json` declares `issue_linking: one-way`,
`issue_granularity: proposal`, and `issue_sync_direction: ledger-to-github`.
The ledger is authoritative. This workflow never reads GitHub checkbox state
back into ledger status.

## 1. Preflight the complete set

Generate every desired issue before the first remote mutation:

```sh
bin/tracker sync --project . --output /tmp/common-rules-issue-plan.json
```

Inspect the plan's digest and preflight counts. Confirm that every configured
ledger appears once, every item ID appears once in its owning proposal, mapped
issue numbers are unique, and existing mappings are preserved. Stop on any
validation problem. Do not create a partial set and do not invent missing
feature rows.

## 2. Resolve the provider boundary

Confirm that the current user request authorizes GitHub issue mutations. Use
the host's integrated GitHub plugin or connected GitHub tool for search,
create, update, close, and reopen operations. This is portable across Codex
and Claude Code: tool names may differ, but the provider boundary does not.

Do not use `gh`, raw GitHub HTTP calls, or the github.com browser UI in
proposal mode. If an integrated GitHub provider is unavailable or lacks the
required operation, stop and report the missing capability. Do not silently
fall back to another mutation path.

## 3. Apply only the validated delta

Fetch mapped issues and search for unmapped plan titles in the configured
repository. A mapped issue always wins, even when its current title is old.
Refuse duplicate or ambiguous search matches.

Create or update issues from the exact plan title and body. Keep an issue open
while any ledger row is non-terminal or terminal evidence is incomplete. Close
only when the plan says `desired_state: closed`; reopen a closed issue when an
authoritative row is reopened and the plan says `desired_state: open`.

Manual checkbox edits are remote drift. Report them; reconciliation never
changes ledger status. Only an explicit, evidence-backed tracker update may
change the ledger, followed by regeneration of the issue body.

## 4. Record provider results explicitly

Immediately after a successful create or an unambiguous existing match, record
the returned identity in the owning repository:

```sh
bin/tracker sync --project . \
  --record content/proposals/08-engine-media.json \
  --issue-number 2 \
  --issue-url https://github.com/OWNER/REPOSITORY/issues/2
```

The record operation assigns the same identity to the proposal, its features,
and every item. It refuses a conflicting identity or a URL from another
repository. Regenerate the complete plan after recording all results and
reconcile provider title/body/state output before claiming synchronization.

Normalize fetched provider results as a JSON list of `number`, `title`, `body`,
and `state`, then run:

```sh
bin/tracker sync --project . --reconcile /tmp/common-rules-remote-issues.json
```

A nonzero drift result is a review finding, not permission to reverse-sync.
