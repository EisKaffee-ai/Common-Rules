# Emberline 1.2.0 — Visual proposals by default

This release makes proposal pages easier to scan before a sponsor reads the
precise decisions.

## What changed

- New proposal pages include reusable `.tk`, `.big`, `.stat`, `.verdict`, and
  `.ev` visual primitives before the Decisions list.
- `bin/proposalcheck` warns when a proposal has no table, inline SVG, or
  headline-figure block before Decisions. The warning does not fail existing
  pages, so adoption can happen progressively.
- The shared workflow now requires new proposals to be answerable from their
  visuals: verdicts are concise, evidence sits beside the claim, and prose is
  reserved for nuance.
- Inline SVG guidance uses the page CSS variables so diagrams remain legible
  in dark mode.

This is a mandatory standard change for projects that adopt or align to this
release. It does not require a chart library or screenshot assets.
