# Common Rules 1.12.0 — visual proposals with Luna implementation context

## Outcome

Common Rules now creates one proposal artifact for two readers:

- the sponsor receives a visual-first decision page with short labels,
  comparisons, flows, measurements, evidence, and stable decisions;
- Luna or another implementation agent receives a structured execution handoff
  at the bottom of the same accepted page.

The handoff records outcome, accepted decisions, scope in/out, repository
ownership, implementation map, contracts and data, ordered steps, future
implementation verification, risks and refusals, dependencies, open questions,
and completion evidence. Unknown repository facts are labelled unresolved rather
than inferred.

Proposal state is explicit without duplicating authority: proposal metadata and
the Decided block own decision state; the ledger and receipts own delivery state.
The visual rail summarizes both. The Luna handoff records the current state,
allowed next state, transition authority, required evidence, and deferred or
superseded paths.

## Visual proposal contract

New pages keep the established compatibility marker and add the visual contract:

```html
<meta name="common-rules-template" content="proposal/21">
<meta name="common-rules-visual-contract" content="proposal/38">
```

The visual-proposal skill loads its detailed visual grammar only when invoked.
Authors choose the smallest useful visual for the decision: before/after,
options, flow, lifecycle, hierarchy, capability matrix, headline figures, or a
status board. Inline SVG is semantic, token-colored, and dark-mode safe.

The final section is:

```html
<details class="agent-context" id="luna-context">
  <summary>Luna implementation context · agent handoff</summary>
  ...fourteen stable fields, including state management...
</details>
```

The Luna label is friendly and recognizable; the content remains model-neutral.

## Compatibility

- Existing proposal/21 pages are not rewritten and remain valid.
- The Luna-field gate applies only to pages opting into proposal/38.
- Proposal status, decided-answer, ledger, tracker, and release contracts are
  unchanged.
- Acceptance remains a requirements/design authority boundary, not evidence that
  implementation, tests, review, or release has completed.
- Creating, reviewing, and accepting a proposal requires document validation,
  visual review, sources, and the sponsor's decision—not executable tests. The
  handoff's Implementation verification field governs later delivery work.

## Upgrade

Install or update the `common-rules` plugin to 1.12.0. New proposals created with
`bin/new-proposal` receive the visual/Luna contract automatically. Existing open
proposals may adopt it when materially reworked; historical accepted proposals do
not need migration.

## Verification

The release requires focused generator, proposal-lifecycle, package, template,
documentation, version, and context-budget checks; `bin/proposalcheck`; the full
Common Rules release gate; and independent review before merge, tag, and release.

Proposal 38 contains the accepted visual design and the complete implementation
context for this release.
