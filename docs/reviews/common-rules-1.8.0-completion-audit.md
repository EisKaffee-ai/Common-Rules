# Common Rules 1.8.0 completion audit

Prepared 3 October 2026 for independent review of Proposal 36, the accepted
implementation of Proposal 02.

## Candidate

- Repository: `EisKaffee-ai/Common-Rules`
- Branch: `codex/calibrated-setup-release`
- Audited implementation commit: `95a1722`
- Latest evidence commit when this audit was prepared: `eff3b61`
- Version: `1.8.0`

The implementation commit passed the full merge gate. Later commits contain
only ledger, generated tracker and review evidence. The remote migration check
confirms the published release branch matches its current local head.

## Outcome-by-requirement matrix

| Requirements | Evidence row | Outcome | Primary proof |
|---|---|---|---|
| CR36-R01–R04, R16–R17 | TR-01 / C-01 | implemented | preview/apply/doctor setup contract; project setup and declaration suites; live doctor green |
| CR36-R05–R08 | TR-02 / C-02 | implemented | committed workspace truth, local-path separation, compatible revisions and joined tracker; workspace suite and generated board check green |
| CR36-R09–R10 | TR-03 / C-03 | implemented | requirement/file/test/evidence graph and changed-file impact gate; 7 rows verified |
| CR36-R11–R15, R20 | TR-04 / C-04 | implemented | portable OpenAI and Claude manifests, 13 lifecycle skills, optional issue links and trusted hooks; package tests and Claude validator green |
| CR36-R18 | TR-05 / C-05 | verified | VERSION, changelog and manifests agree at 1.8.0; workflow stamp and version policy green; full gate green |
| CR36-R19 | TR-06 / C-06 | verified | 3 histories, 320 source files and 7 source tags preserved; old remote untouched; release branch matches HEAD |
| CR36-R21 | TR-07 / C-07 | implemented | current Common Rules landing, six accessible visual explainers, Codex/Claude setup, all 13 skills and three worked examples |

The authoritative mapping remains
`docs/proposals/36-calibrated-project-setup-and-workspace-tracker.json`. This
table is a reviewer index, not a second tracker.

## Reproducible gates

From the repository root:

```sh
./bin/project-setup --project . doctor
./bin/tracecheck --project .
./bin/proposalcheck --project .
./bin/tracker check --project .
./bin/tracker board --project . --check
./bin/version-check --check
./bin/workflow-stamp --check
claude plugin validate .
./bin/migration-check --remote
```

The full gate must use a modern Python with Pillow available to helper
subprocesses:

```sh
bin/quiet --label release-gate --jobs auto -- \
  python3 -m unittest discover -s tests -q
```

Recorded result for `95a1722`: `quiet: OK · 2042 tests · 186.3s`.

## Visual verification

The README references six current SVG explainers. Each has a title and
description, uses only the Common Rules identity and scales without horizontal
overflow. The skill map was changed from a wide desktop layout to a vertical
mobile-first layout after visual inspection. Companion HTML pages use responsive
single-column breakpoints and no longer reference the legacy tracker screenshot.

## Known non-blocking findings

`bin/proposalcheck` reports eight pre-existing visual warnings on proposals
21–24 and 30–33 because they do not put a table, diagram or headline figure
before their Decisions section. It reports no proposal violations. Those files
are outside Proposal 36 and were not changed to make this release appear green.

## Independent reviewer decision

The reviewer should record one of the following in the Proposal 36 ledger:

- **accept** — requirements, implementation, tests, visuals and migration proof
  agree; C-01 through C-07 may move from `in review` to `done`;
- **return** — name the requirement, file and reproducible contradiction; keep
  the affected item in review or move it back to testing.

The implementation author has not marked the items done and cannot supply the
independent decision.

## Publication boundary

Independent acceptance comes before sponsor merge. After acceptance, the
sponsor may merge the branch, choose or confirm the default branch and create
the `v1.8.0` tag/release. Publishing to OpenAI's universal Plugins Directory is
a separate account-bound submission and review process; it is not claimed by
this repository release evidence.
