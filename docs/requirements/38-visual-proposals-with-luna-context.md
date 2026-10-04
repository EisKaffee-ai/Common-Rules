# Proposal 38 requirements — visual proposals with Luna implementation context

Status: accepted · 2026-10-04

## User outcome

Every proposal created by Common Rules is understandable from its visuals before
the sponsor reads detailed prose. The same HTML page ends with a structured,
self-contained implementation context that a lower-cost implementation agent such
as Luna can execute after the sponsor accepts the decisions.

## Requirements

- **CR38-R01 — One canonical generator.** `bin/new-proposal` continues to create
  the proposal HTML and ledger together from the shipped Common Rules template.
- **CR38-R02 — Visual first.** Before `Decisions`, every generated page contains
  a compact visual story: recommendation, headline facts, the relevant comparison
  or flow, and evidence immediately adjacent to the claim it supports.
- **CR38-R03 — Visuals match the question.** Common Rules documents when to use a
  before/after comparison, option cards, a flow, a lifecycle, a hierarchy, a
  capability matrix, headline figures, or a status board. Authors do not add a
  diagram when prose or one number communicates the decision more clearly.
- **CR38-R04 — Minimal reading burden.** The sponsor-facing surface uses short
  labels, diagrams, cards, tables, and progressive disclosure. Long evidence and
  implementation detail stay below the decision surface or inside `details`.
- **CR38-R05 — Stable decisions.** Decisions keep stable `D1`, `D2`, … identities,
  and accepted pages preserve the sponsor's answer verbatim in `Decided`.
- **CR38-R06 — Luna implementation context.** The bottom of every generated page
  contains one section with `id="luna-context"` and a clear “Luna implementation
  context” label. It is available to any implementation agent, not coupled to one
  model API.
- **CR38-R07 — Executable handoff schema.** The Luna section records outcome,
  accepted decisions, scope in/out, repository ownership, implementation map,
  contracts and data, ordered steps, future implementation verification, risks
  and refusals, dependencies, open questions, state management, and completion evidence.
- **CR38-R08 — Self-contained context.** An implementation agent can act from the
  accepted proposal and repository state without needing the design conversation.
  Paths, symbols, commands, invariants, authority boundaries, and unresolved facts
  are explicit; missing information is labelled rather than invented.
- **CR38-R09 — Acceptance boundary.** A proposed page may prepare the Luna context,
  but it must label unaccepted decisions as unresolved. Acceptance authorizes
  requirements and design work; it does not itself prove implementation complete.
- **CR38-R10 — Accessible rendering.** The template remains mobile-first,
  keyboard-readable, semantic, and legible in light and dark mode. Inline SVG uses
  CSS variables and carries an accessible title and description.
- **CR38-R11 — Backward compatibility.** Existing proposal/21 pages remain valid.
  Newly generated pages add a proposal/38 visual-contract marker without changing
  old proposal status or ledger semantics.
- **CR38-R12 — Skill routing.** The `visual-proposal` skill stays concise and
  routes authors to an on-demand visual-language reference containing the detailed
  element and Luna-handoff guidance.
- **CR38-R13 — Tooling validation.** Because this release changes executable
  Common Rules tooling, focused tests prove the generated page contains the
  visual primitives before `Decisions`, the Luna section after `Decided`, all Luna
  fields, accessible SVG guidance, and no unexpanded generator placeholders.
- **CR38-R14 — Documentation.** The README and proposal user guide explain the
  visual-first/Luna-handoff workflow and make clear that the ledger remains the
  delivery source of truth.
- **CR38-R15 — Release coherence.** The Common Rules semantic version, both plugin
  manifests, pinned version test, changelog, release notes, focused tests, context
  budget, and release gate agree before publication.
- **CR38-R16 — Proposal state management.** Every new visual proposal shows a
  lifecycle rail while keeping two explicit authorities: `proposal-status` and
  the `Decided` block own decision state; ledger items and receipts own delivery
  state. The handoff records current state, allowed next state, transition
  authority, required evidence, and deferred or superseded reasons.
- **CR38-R17 — Proposal-stage verification boundary.** Creating, reviewing, and
  accepting a proposal requires structural validation, visual inspection,
  sources, and sponsor acceptance, but no executable implementation tests. The
  Luna handoff describes future implementation verification; those checks become
  required only when accepted scope enters implementation.

## Acceptance criteria

1. A new proposal generated in a scratch repository passes `proposalcheck` and
   ledger validation unchanged.
2. Its sponsor-facing portion is scannable before the decisions, and its final
   section is a complete Luna implementation-context scaffold.
3. The template and skill reference explain which visual primitive to choose for
   common proposal questions.
4. The proposal can be accepted without executable tests; the Common Rules
   tooling implementation remains covered by its existing lifecycle tests.
5. The plugin release gate passes at the new version and produces release evidence.
