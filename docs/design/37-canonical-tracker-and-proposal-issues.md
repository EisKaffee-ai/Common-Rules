# Proposal 37 design — one tracker, proposal-level issue mirror

Status: accepted · 2026-10-03

## Authority model

```text
                 COMMITTED WORKSPACE HUB
        canonical ledger directory + compatible revisions
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
  canonical tracker     issue draft plan    traceability data
  one published page    deterministic JSON  evidence drill-down
          │                   │
          │                   ▼
          │          integrated GitHub plugin
          │          create/update/close/reopen
          │                   │
          └──────────────► group issue links

Ledger status flows right. GitHub state never flows left without an explicit,
evidence-backed reconciliation.
```

## Manifest extension

```json
{
  "integration": {
    "repository_id": "docs",
    "role": "documentation",
    "requirements": ["docs/architecture", "content", "templates"],
    "tracker": "content/proposal/delivery/docs/proposals",
    "issue_linking": "one-way",
    "issue_repository": "EisKaffee-ai/bean-engine",
    "issue_granularity": "proposal",
    "issue_sync_direction": "ledger-to-github",
    "workspace": {"id": "eiskaffee-vanilla", "role": "hub"},
    "skill_receipts": true
  }
}
```

The three new keys are optional. When `issue_granularity` is `proposal`, all
four issue fields form one contract and invalid combinations fail early.
Existing manifests remain valid.

## Setup and discovery

Setup searches only inside declared requirements roots. A directory qualifies
as the canonical tracker source when it contains validated proposal ledgers;
its generated page is `<ledger-directory>/tracker/index.html`. Discovery ranks
an existing configured directory above conventional defaults and reports all
alternatives without creating any of them.

```text
discover roots → find ledgers → validate candidates → select configured source
              → preview one manifest → explicit apply → doctor
```

## Proposal issue plan

Proposal mode is a deterministic plan, not a network client. `tracker sync`
reads the project manifest and emits a complete proposal issue plan containing:

- repository and sync direction;
- canonical tracker and committed source revision;
- one group record per ledger;
- title, body, desired open/closed state and stable item mappings;
- preflight counts and a content digest.

The plan is validated as a whole before mutation. The tracker skill then uses
the installed GitHub plugin to fetch existing issues, preserve explicit
mappings, and create or update only the delta. Plugin results are written back
through a narrow Common Rules command that assigns one issue identity to the
proposal and every item. The legacy row-level `tracker sync LEDGER` flow stays
available for projects that did not opt in.

## Generated body

```text
[Architecture NN/TT] Layer · Group title
  Architecture group identity and namespace
  Canonical tracker, ledger and source revision
  Repository ownership
  Feature heading
    [x]/[ ] stable item ID · title · explicit state
  Evidence, gaps, dependencies and next action
  Implementation, tests, receipts and related issues
  Ledger-authority and reconciliation notice
```

An item without `feature` belongs under Scope definition. No synthetic six-row
feature is created. Deferred items must include their reason before appearing
checked.

## Reconciliation state machine

```text
ledger non-terminal ──► issue open
ledger all terminal + completion evidence ──► issue closed
closed issue + reopened ledger row ──► requested reopen
GitHub checkbox differs ──► DRIFT, never ledger mutation
```

Issue #2 or any other pre-existing issue may have a historical title. An
explicit proposal mapping wins over title matching, so migration updates it
instead of creating a duplicate.

## Canonical tracker sections

The existing delivery layouts remain inside Product delivery. A new top-level
section switcher exposes:

1. **Overview** — goal, totals, active blockers and compatible revision set.
2. **Product delivery** — the existing tree, Kanban, board and list layouts.
3. **Architecture** — proposal cards grouped by layer with issue and lifecycle
   coverage.
4. **Repositories** — workspace members, roles, revisions, cleanliness and
   availability.
5. **Evidence** — traceability coverage, receipts, gaps and drill-down links.

The board reads the configured ledger directory rather than assuming
`docs/proposals`. Workspace information is rendered into the same HTML file;
`workspace-tracker` may still create an internal intermediate fragment for
validation, but it is not another public page.

## Repository ownership

- **Common Rules:** manifest schema, setup discovery, proposal issue-plan
  generator/link validator, canonical tracker sections, skills and tests.
- **Docs:** canonical ledgers, website build integration, architecture sources
  and the generated traceability dataset.
- **Vanilla:** application, SDK and UI implementation evidence.
- **Bean Engine:** business logic, Runner evidence and the one GitHub issue home.
- **UI Assets:** shared visual asset evidence.

Each repository commits independently. This Common Rules change reads the
other repositories only for validation and never edits their files.

## Release boundary

The release adds optional proposal-level issue synchronization and canonical
tracker sections. It does not add two-way synchronization, infer implementation
from paths, fabricate missing feature rows, copy member ledgers, or authorize a
local command to impersonate the integrated GitHub plugin.

## Context budget

Both supported hosts use progressive skill loading. The always-discovered
surface is the skill name, description and (conservatively) path. Full
`SKILL.md` instructions load only for the selected workflow; references load
only when that workflow points to them. Hook code runs outside model context
and contributes only the text it returns.

`bin/context-budget` measures those surfaces independently using a transparent
UTF-8-bytes/4 token estimate, emits Markdown or JSON, compares a Git revision,
and fails release verification above the idle discovery budget. The proposal
issue mutation playbook remains a tracker reference so setup, warmup, and
ordinary tracker sessions do not pay for it.
