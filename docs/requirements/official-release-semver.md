# Official release baseline — sponsor-directed P32 follow-up

Accepted direction, 2026-10-15: calculate release increments from the official
published version, not a sequence of unreleased local candidate bumps. Use
Semantic Versioning. This does not authorize publishing or moving existing tags.

## Requirements

1. Select the highest stable, non-draft, non-prerelease officially published
   release for the named repository/component from supplied GitHub API evidence.
   Require explicit published_at and a repository-matching release URL. Local
   VERSION files, commits, tags, drafts and prereleases cannot become the stable
   baseline. Missing/malformed/ambiguous evidence refuses rather than guesses.
2. Compute exact MAJOR/MINOR/PATCH SemVer increments, resetting lower numbers.
   Fixes/internal compatible refactoring normally use PATCH; compatible new
   functionality MINOR; breaking public contracts MAJOR. A documented pre-1.0
   policy may specify MINOR for breaking changes; the caller records rationale.
3. Check the proposed release identity against explicitly supplied local AND
   remote tag inventories. A collision refuses, never moves a tag, silently
   skips a number or treats the colliding tag as official publication. Existing
   version aliases for a component must be checked together.
4. A deterministic read-only CLI accepts a complete release-list snapshot,
   repository, allowed tag prefixes, bump class, and a combined local/remote tag
   inventory. Emit baseline URL/version/tag, proposed version/tag, evidence hash
   and change class. Require an explicit complete-evidence acknowledgement;
   snapshots remain caller-supplied evidence, not independently authenticated.
   No automatic networking, product/third-party package import, Git mutation,
   release or installation. Evidence files are regular non-symlink files,
   at most 8 MiB each; refuse
   non-regular or changing inputs before parsing rather than block on a pipe.
5. Preserve the existing version-check candidate/changelog consistency gate,
   but explicitly remove its claim to prove official publication. Release
   handoff must use official evidence and retain all independent review,
   clean-tree, compatibility, privacy and immutable-release gates.

## Design and ownership

Common Rules owns tools/release_version.py, bin/release-version and
tests/test_release_version.py (code engineer). Lead owns this brief, the shared
workflow release paragraph, land-handoff skill, version-check documentation,
CHANGELOG and tracker events. Distinct reviewer is report-only. Other projects
are not modified by this task; no change to Bean version/tags or public history.

The helper is an offline SemVer preflight, not a publication certificate.
GitHub API snapshots must include all relevant pages and released component
aliases; caller attestation and source URL are explicit evidence limits.
Tests use synthetic records and temporary files, observing red-before-green;
cover local0.8.8/official0.8.1 -> patch0.8.2, draft/prerelease exclusion,
major/minor/patch resets, numeric ordering, aliases and collisions, missing or
malformed publication evidence and read-only CLI failures. No live product data.

The shared-rule change is mandatory at the release boundary, not at every
development commit. Updating an installed plugin or publishing Common Rules
requires a separate verified release; this task prepares a reviewable branch.

Review follow-up ownership: code engineer also owns bin/version-check and the
focused tests/test_version.py CLI assertion so its printed candidate marker
cannot be mistaken for the last official release. Preserve all return values
and candidate/changelog semantics; only correct the public wording/disclaimer.
