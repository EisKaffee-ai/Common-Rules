# Common Rules migration evidence

Recorded 3 October 2026 for the Common Rules 1.6.0 release candidate.

## Outcome

The migration is a non-destructive consolidation, not a force replacement.
The Emberline source repository remains untouched. Common Rules contains the
source main branch, the published `w10-measured` development branch, the
local-only development history, the source files, and the historical tags.

```text
upstream/main              03e56ee ─┐
upstream/w10-measured      b8a8b41 ─┼─► Common Rules 1.6.0 candidate
local-source/w10-measured  7aefa56 ─┘
```

## Repeatable proof

`bin/migration-check` verifies locally that all three histories are ancestors
of the candidate and that every file from `upstream/main` remains present.
`bin/migration-check --remote` additionally compares the upstream and origin
refs, requires every source tag and the named source branches at origin, and
requires `origin/codex/calibrated-setup-release` to match the candidate.

The checker is deliberately read-only. It does not push, delete, force-update,
merge, select a default branch, create a release, or change either repository.

## Current evidence

- All three required histories are ancestors of the candidate.
- All 320 files from `upstream/main` are present in the candidate.
- Local-only commits `7aefa56`, `20416de`, `0f97289`, and `2eef657` are
  preserved in the candidate ancestry.
- Historical source tags were copied to the Common Rules destination without
  rewriting source refs.
- The Common Rules release branch is published for independent review.

## Remaining publication boundary

Independent review, sponsor merge, default-branch choice, and the `v1.6.0`
release tag remain publication actions. This evidence does not claim that any
of them has happened.
