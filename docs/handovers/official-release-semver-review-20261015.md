# Official-release SemVer follow-up — reviewed implementation checkpoint

Sponsor-directed P32/V-02.A, 2026-10-15. This is a focused implementation
checkpoint, not a Common Rules or Bean release certificate.

The new offline release-version preflight chooses the highest numeric stable
official published release from complete caller-supplied GitHub evidence;
local candidates do not influence it. Explicit publication timestamps, exact
repository/tag URLs, component aliases and local/remote tag inventories are
required. It computes exact patch/minor/major increments and refuses collisions.
Stable build metadata is allowed but does not affect precedence. All evidence
files are bounded regular/no-follow/nonblocking stable reads. Snapshot origin
and completeness remain caller-attested, not authenticated by this tool.

Independent review found and confirmed repairs for raw Git-ref/peeled-line
collision masking and valid build-metadata rejection. Further hardening added
bounded evidence reads and clarified the candidate version-check wording. Each
new regression was observed red before its fix. Initial missing CLI:21 tests,
41 subtest failures. Review repair:26 tests,34 subtest failures. File-safety
red:27 tests,2 failures/1error (the timeout killed/reaped only its own child).
Literal-plus URL red:28 tests,1failure. Candidate wording red:26 tests,2failures.

Final lead verification:

- release-version:28/28 pass,4.6s, through bin/quiet.
- existing version-check:26/26 pass,3.7s, through bin/quiet.
- independent release repeat:28/28 pass,4.586s.
- independent synthetic version repeat:22/22 pass,3.931s; four read-only
  real-checkout tests intentionally omitted by that reviewer, included by lead.
- tracecheck:17 rows verified. Context discovery budget:623 estimated tokens,
  below650. Diff whitespace check passed.

All independent source hashes and base HEAD6ffdaef remained stable:

| Source | SHA-256 |
|---|---|
| tools/release_version.py | 8191ec3129568c928c0062403bbee5ae298afca96452406c96259d8b7adb8bf6 |
| bin/release-version | 73a164f305d045489ccc99eceb0e6c1dccd97e2df12dbf0587378c52b0632e4f |
| tests/test_release_version.py | 3d7776ca200da581dbd11ec652343f2e0bb6a1d0c46831a4839f90742c2eb439 |
| bin/version-check | 2343fc2eb1615bb208793d8bc4826471745b6118ebc24c9b0809d76bfc501412 |
| tests/test_version.py | 153ba47877f6a7b4ba2c4c8c1c056ac4183beb7cc577f39f017cb3271a5ff670 |

Conservative limitation: literal bare tag names beginning refs/ are unsupported
and refuse, rather than risk accepting raw ref inventories as bare names.

Not performed: full suite/merge gate, release/version-tag publication, plugin
installation, Bean release, Bean branch push, or Vanilla installed acceptance.
Mandatory changelog changes still require selecting Common Rules' own candidate
from official evidence and refreshing generated workflow views before landing.
No VERSION or immutable tag was changed. Worktree conformance lacks an installed
pre-commit hook and Ruflo memory; tooling was unavailable, not invented or installed.

The separate Bean goal/manifest and Docs P31 now prioritize Photos/Vanilla:
finish relevant structure and ownership, verify release, integrate exact
Bean/Runner/app tuple. Pocket/Sangam-only work is outside that first delivery
unless a shared risk. Bean calibration doctor passed; its14 historical trace
link failures remain explicit. No other-project data or product code executed.
