# Proposal 36 requirements — calibrated project setup

Status: accepted · 2026-10-03

## User outcome

A project can adopt Common Rules without pretending every repository has the
same shape.  Each repository remains independently versioned, while an
optional workspace hub makes requirements, delivery state and cross-repository
impact visible as one coherent project.

## Requirements

- **CR36-R01 — Inspect before writing.** Setup discovers existing instruction,
  requirements, proposal, tracker, test and Git files without changing them.
- **CR36-R02 — Calibrate.** Setup classifies a repository as new or existing,
  single-repository or workspace member, and records unresolved choices.
- **CR36-R03 — Preview and consent.** The default is a preview. Files change
  only with an explicit `--apply`; existing content is preserved.
- **CR36-R04 — Repository manifest.** Every adopted repository owns a
  committed `.common-rules.json` naming its stable ID, role, requirements,
  tracker ledger location, issue-linking mode and workspace relationship.
- **CR36-R05 — Workspace truth.** A multi-repository project has one committed
  `docs/common-rules/workspace.json` in its hub. It names stable repository IDs,
  roles, remotes, manifest paths and the revision used for each joined view.
- **CR36-R06 — Local paths are not truth.** Checkout paths live only in the
  ignored `.common-rules/workspace.local.json`; they never enter the portable
  project contract.
- **CR36-R07 — Independent commits, coherent set.** Repositories are committed
  separately. The workspace manifest pins the compatible revisions and the
  checker refuses missing, dirty, unknown or mismatched members.
- **CR36-R08 — One tracker view.** The hub can generate a joined, mobile-safe
  HTML tracker from validated member ledgers without copying or rewriting them.
- **CR36-R09 — Traceability.** Requirement IDs connect proposal items,
  documentation, implementation files, verification commands and a receipt or
  refusal. Broken paths and incomplete rows fail deterministically.
- **CR36-R10 — Change impact.** When a linked implementation file changes, the
  same change set must update its requirement source, ledger evidence, or add an
  explicit owner-reviewed no-change receipt.
- **CR36-R11 — Feature lifecycle.** A user-deliverable feature moves through
  discovery, proposal, acceptance, requirements, design, build, test, review,
  release and evidence; incomplete stages remain visible.
- **CR36-R12 — Portable plugin.** The release provides a root `plugin.json`,
  narrowly described skills and optional trusted hooks. Skills explain their
  routing visibly; hooks check, remind or refuse but do not invent project truth.
- **CR36-R13 — Visual proposal loop.** A visual-proposal skill produces a
  mobile-first HTML decision artifact, records sponsor answers and iterates
  until accepted; acceptance precedes requirements and implementation.
- **CR36-R14 — Host boundaries.** ChatGPT web can use instructions and connected
  tools, but local commands and hooks require a local execution host. Installing
  a plugin never implies hook trust or remote write authority.
- **CR36-R15 — Issue links are optional.** Issue linking is `off`, `manual`, or
  `one-way`; two-way ownership is refused until a separate accepted design.
- **CR36-R16 — Compatibility.** Existing projects behave as before until they
  opt in. Setup and checks return named findings, never tracebacks.
- **CR36-R17 — Doctor and migration.** A read-only doctor reports missing,
  stale and unsafe configuration and gives exact recovery actions.
- **CR36-R18 — Release evidence.** The version, changelog, plugin manifest,
  focused tests, full gate and generated artifacts agree before publication.
- **CR36-R19 — Tracker consolidation.** Common Rules is the tracker plugin and
  supersedes the separate Emberline AI Tracker runtime. Migration preserves
  ledger IDs, history and evidence and never overwrites a remote until its
  destination branch is confirmed and the imported ledgers validate.

## Acceptance evidence

The proposal ledger maps every requirement above to design, implementation and
verification. A release is prepared only when `bin/project-setup doctor`,
`bin/tracecheck`, plugin-package tests, proposal checks, version checks and the
repository merge gate are green.
