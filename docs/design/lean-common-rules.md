# Lean Common Rules design

## Ownership

- Common Rules repository owns command behavior, skills, templates, tests,
  changelog, version and release evidence.
- Proposal 33 owns the accepted requirements and completion receipts.
- Each adopting repository owns its local alignment commit and uncommitted
  work. The release session only sends instructions and reads receipts.

## State model

Warm-up state is keyed by project identity, project revision, Common Rules
revision, relevant declaration digest and ledger/checkpoint digest. An equal
key is idempotent. Reheat compares the previous key and reports only changed
components plus current non-holding standard items.

An open sponsor review carries one stable review identity. Additional feedback
received before that review is accepted or closed is appended to it. Intake
creates another ask only when classification or scope changes.

Gate receipts bind the gate level, command digest, repository revision and
declared inputs. Stronger boundaries may consume weaker receipts as supporting
evidence but must run their own required gate.

Ruflo stores bundle lifecycle state. `note` and `ready` are non-terminal.
`checkpoint` is the verified completion boundary. `land` is the release
boundary. `done` delegates to `checkpoint` for compatibility.

## Expected implementation surfaces

- `bin/warmup`, `skills/warmup`, `skills/reheat`, hooks and warm-up tests;
- tracker ask/handover intake and their tests;
- project gate resolution, receipt storage and tests;
- `bin/ruflo-item`, Ruflo tests and command documentation;
- lead/brief templates and Common Rules workflow guidance;
- Proposal 33, generated tracker/checkpoint, changelog and version manifests.

## Failure behavior

- Missing or malformed state never suppresses a required warm-up.
- A stale or mismatched gate receipt is ignored, never repaired silently.
- `ready` cannot mark a ledger item done.
- `checkpoint` and `land` refuse when their required gate is absent or red.
- Feedback coalescing never discards verbatim sponsor text.
- Rollout never writes through dirty adopting worktrees from this repository.
