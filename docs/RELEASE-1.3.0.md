# Emberline 1.3.0 — Guide and architecture traceability

This release makes the relationship between user-facing documentation,
architecture, implementation, and verification visible in the tracker.

## What changed

- Added optional, validated `traceability` rows to proposal ledgers.
- Each row records requirement IDs, guide and architecture sections,
  implementation files, tests or commands, a receipt or refusal, owner, and
  status.
- Added a first-class Traceability table to the generated project tracker.
- Added proposal 35 to Emberline's own tracker as a working example based on
  the Loom maintenance rule.

The schema is additive: existing ledgers remain valid without rows. Projects
that adopt this standard change should add rows for implementation-facing
capabilities and keep them current through warm-up, review, and release.
