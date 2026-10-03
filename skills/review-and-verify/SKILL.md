---
name: review-and-verify
description: Verify a feature against accepted requirements, design, traceability, tests, and cross-repository coherence before release.
---

# Review and verify

State the active skill. Run the focused checks, tracecheck, workspace coherence
check and merge gate. Review changed linked files against requirements. Record
evidence or findings in the ledger. Never let an implementation session certify
its own restricted-risk work; keep the feature in review until independent
evidence exists.

For proposal-granularity issue linking, verify the full-set plan before any
remote write: one issue per proposal, one stable checkbox per ledger item,
unique issue identities, matching ledger/checkbox totals, and explicit close or
reopen intent. Reconcile remote title/body/state drift as a finding; the ledger
remains authoritative and GitHub checkbox edits never complete tracker rows.
