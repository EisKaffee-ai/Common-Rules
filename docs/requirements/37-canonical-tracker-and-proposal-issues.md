# Proposal 37 requirements — canonical tracker and proposal issues

Status: accepted · 2026-10-03

## User outcome

A workspace hub publishes one canonical project tracker from its committed
ledgers. Architecture groups appear inside that tracker and mirror one way to
exactly one GitHub issue per proposal, while every repository keeps its own
commits and the ledger remains authoritative.

## Requirements

- **CR37-R01 — Discover the real tracker.** Setup recursively inspects the
  configured requirements locations and identifies an existing ledger
  directory and generated tracker before proposing any new tracker.
- **CR37-R02 — Optional proposal issue contract.** The project manifest accepts
  `integration.issue_repository`, `integration.issue_granularity` and
  `integration.issue_sync_direction`; proposal granularity is valid only with
  one-way, ledger-to-GitHub synchronization and an `owner/repository` target.
- **CR37-R03 — Backward compatibility.** Projects using `off`, `manual`, or the
  existing row-level one-way issue flow behave as before until they opt into
  proposal granularity.
- **CR37-R04 — One canonical page.** The configured ledger directory owns one
  generated `tracker/index.html`. A workspace view, traceability dataset, or
  website integration is a section or drill-down of that page, never a second
  public tracker.
- **CR37-R05 — Proposal draft identity.** Proposal issue drafts are deterministic
  and contain one stable record per ledger with proposal number, group title,
  namespace, layer, canonical ledger path, canonical tracker path and source
  revision.
- **CR37-R06 — Complete generated body.** Every issue body contains repository
  ownership, one checkbox per ledger item, current evidence, gaps,
  dependencies, next action, implementation/test/receipt links and related
  issue links without inventing missing requirements.
- **CR37-R07 — Stable checkbox mapping.** Each checkbox preserves its ledger
  item ID. `done` is checked; `deferred` is checked only with its reason; every
  other status is unchecked and named explicitly.
- **CR37-R08 — One issue per proposal.** Every item in one ledger maps to the
  same group issue. The tool refuses zero, duplicate, or conflicting issue
  mappings and never creates per-feature or per-row issues in proposal mode.
- **CR37-R09 — Plugin mutation boundary.** Common Rules generates and validates
  drafts locally. Issue creation and updates are performed by the integrated
  GitHub plugin, not github.com UI and not a hidden two-way daemon. Returned
  issue identities are recorded explicitly into the ledger.
- **CR37-R10 — Reconciliation, not reverse sync.** GitHub checkbox edits never
  change ledger status. Drift is reported and requires an explicit Common
  Rules reconciliation backed by evidence.
- **CR37-R11 — Lifecycle state.** A group issue closes only when every row is
  terminal and completion evidence is attached; reopening an authoritative row
  makes the generated plan request that the issue reopen.
- **CR37-R12 — Preflight before mutations.** The complete issue set is drafted
  and validated before the first remote mutation. Existing issue identities,
  including a pre-existing nonconforming title, are reused when mapped.
- **CR37-R13 — Tracker information architecture.** The canonical page exposes
  Overview, Product delivery, Architecture, Repositories and Evidence views.
- **CR37-R14 — Architecture cards.** Architecture groups are organized by
  layer. Each card shows proposal/title, issue, feature count, completed/total
  rows, approval, implementation classification, repository owners, blockers
  and next action.
- **CR37-R15 — Joined repository section.** The compatible status of workspace
  members appears in Repositories using committed member identities/revisions
  plus ignored local checkout mappings; member ledgers are never copied.
- **CR37-R16 — Evidence drill-down.** Feature traceability is reachable from
  architecture cards and the Evidence view. A generated traceability dataset
  remains supporting evidence, not an independent tracker.
- **CR37-R17 — Preserve project history.** Migration preserves ledger IDs,
  item IDs, logs, evidence and proposal order. Coordination-only rows appear as
  Project Operations rather than another published tracker.
- **CR37-R18 — Exact totals.** Ledger, tracker card and generated issue
  checkbox totals must agree; mismatches fail with the responsible proposal
  and item IDs.
- **CR37-R19 — Committed publication source.** Website publication identifies
  the committed Docs revision used to generate the canonical tracker and does
  not maintain a hand-edited copy.
- **CR37-R20 — Read-only project checks.** Setup preview, doctor, tracecheck,
  tracker validation and workspace validation can verify the contract without
  mutating another repository or GitHub.
- **CR37-R21 — Release evidence.** Version, changelog, both plugin manifests,
  skills, focused tests, full merge gate and generated artifacts agree before
  the new Common Rules version is published.
- **CR37-R22 — Measured context budget.** Before publication, the plugin reports
  idle skill-discovery text separately from invoked skill instructions,
  optional references, hook output and the full-package ceiling. The README
  publishes reproducible byte/token estimates, identifies them as context—not
  process RAM—and a release check caps idle discovery at 650 estimated tokens.
- **CR37-R23 — Fast full gate.** The full unittest gate retains every discovered
  test while sharding large files at class granularity on a cold checkout and
  reusing measured shard durations later. The release records both total test
  count and wall time; scheduling changes must preserve the aggregate verdict.
- **CR37-R24 — Mixed-ledger issue scope.** A hub may name
  `integration.issue_series` to limit proposal-level GitHub synchronization to
  one ledger series. Ledgers outside that series remain visible in the single
  tracker as Project Operations, are excluded from architecture totals and
  issue drafts, and are refused if they already carry an issue mapping.
- **CR37-R25 — Deterministic generated state.** Python commands shipped in the
  plugin own every generated value and repeatable tracker operation: proposal,
  ask and finding identifiers; counts and percentages; digests; issue drafts;
  provider-returned mapping write-back; ledger validation and state
  transitions; board rendering; history; checkpoints; workspace joins and
  freshness checks. Agents may supply explicit source text and invoke those
  commands, but must never invent generated identifiers or numbers, hand-edit
  generated tracker HTML, or directly rewrite ledger state.
- **CR37-R26 — Local cross-repository resolution.** Setup accepts explicit
  `repository_id=checkout` mappings and writes them only to the ignored local
  workspace manifest. Tracecheck resolves repository-qualified implementation
  references through that manifest, and workspace validation accepts absolute
  machine checkout paths without putting them in committed project truth.

## Vanilla acceptance fixture

The read-only acceptance fixture is the EisKaffee Vanilla Docs workspace:

- workspace `eiskaffee-vanilla`, hub repository `docs`;
- canonical ledgers at
  `content/proposal/delivery/docs/proposals` and canonical tracker at its
  `tracker/index.html`;
- 27 architecture groups, 59 features and 362 lifecycle items;
- issue repository `EisKaffee-ai/bean-engine`;
- Bean Engine issue #2 retained for Proposal 08;
- issue series `documentation-delivery`, so later operational proposals do not
  create extra architecture issues;
- five layer groups: Application 1,2,26,27; Runner 3–5; Engine 6,8–11,14,15;
  Memory 7,12,13,20–25; AI 16–19.

No Common Rules test writes into the Docs, Vanilla, Bean Engine or UI Assets
repositories. Remote mutation evidence is obtained through the integrated
GitHub plugin after the full draft set validates.

## Acceptance evidence

Focused tests cover manifest validation, recursive discovery, proposal drafts,
issue mapping, status/checklist rules, drift refusal, tracker sections,
workspace membership, exact totals and deterministic generated-page freshness.
The full merge gate, Docs read-only validation, Docs build evidence and GitHub
plugin reconciliation must all be recorded before release.
