---
name: visual-proposal
description: Create or refine a visual-first HTML proposal with stable decisions and an executable agent handoff.
---

# Visual proposal

Say: **Common Rules skill: visual-proposal — turning this decision into a visual
artifact.**

Create the page with `bin/new-proposal`; do not draft a parallel format. Read
[references/visual-language.md](references/visual-language.md) when creating or
materially restructuring the page. Choose the visual that answers the actual
decision, use short labels and progressive disclosure, and make the result
understandable on a phone before the reader reaches `Decisions`.

Keep decision IDs stable and record each sponsor answer verbatim. Iterate the
same page until accepted. Acceptance creates requirements and design work; it is
not implementation evidence.

Show state on two axes: proposal metadata owns the decision state, while ledger
items and receipts own delivery state. The visual rail is a view of those
authorities, never an independent status field.

Do not require executable tests to create, review, or accept a proposal. Validate
its structure and rendering; describe later implementation verification in the
handoff without claiming it has already run.

End the page with `#luna-context`: a self-contained, model-neutral execution
handoff containing the accepted scope, verified repository map, ordered steps,
future implementation verification, risks, state transitions, and evidence. Mark
unknowns unresolved; never invent files, contracts, or acceptance. Preserve earlier visual companion content when
consolidating proposals.
