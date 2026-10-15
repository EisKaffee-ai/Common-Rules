---
name: land-handoff
description: Prepare independently committed repositories as one coherent Common Rules release and handoff without combining commits.
---

# Land and hand off

State the skill. Confirm every repository is clean, reviewed and at the revision
recorded by the hub. Update the compatible revision set only after member gates
pass. Generate the joined tracker, release evidence and next-session handoff.
Before selecting a version, fetch the component's current official stable
release evidence (all relevant pages and tag-prefix aliases), not its unshipped
local VERSION or highest tag. Apply SemVer based on changes since that official
release; use `bin/release-version` with the complete snapshot and combined
local/remote tag inventory. Each eligible record must include `published_at`
and a release URL matching the repository. Fetch all relevant API pages and
pass the explicit `--complete-evidence` acknowledgement; the tool cannot prove
the caller fetched everything or authenticate an offline snapshot.
Record the baseline URL, bump rationale, proposed
version, exact revision and preflight result. Missing evidence or a tag collision
refuses; never move an existing release/tag or silently advance past a collision.
Candidate/changelog checks alone do not establish official publication, and
this preflight does not replace independent verification or authorize release.
Separate repositories keep separate commits and pull requests; the hub revision
set is what proves they are correct together.
