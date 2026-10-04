# Proposal 38 design — visual decision surface plus executable agent context

Status: accepted · 2026-10-04

## Page architecture

```text
PROPOSAL HTML
├─ identity · proposal number, status, title, date
├─ sponsor ask · exact quote
├─ state rail · decision state + ledger-derived delivery state
├─ visual decision surface
│  ├─ recommendation / verdict
│  ├─ 2–4 headline facts
│  ├─ one primary visual chosen for the question
│  ├─ options or capability comparison
│  └─ evidence beside each important claim
├─ stable decisions · D1, D2, …
├─ decided · exact sponsor answers
├─ expandable evidence / sources
└─ Luna implementation context · structured execution handoff
```

The visual surface is for human comprehension. The Luna context is for precise
execution. They describe the same accepted scope and must not contradict one
another.

## Visual selection

The shipped template provides reusable CSS classes, while
`skills/visual-proposal/references/visual-language.md` explains selection:

| Question | Primary visual | Required content |
|---|---|---|
| What changes? | before/after pair | state, delta, consequence |
| Which option? | option cards + comparison table | trade-off and verdict |
| How does it move? | flow diagram | authority, direction, read/write |
| What happens over time? | lifecycle / step rail | transition and stop state |
| Who owns what? | hierarchy / boundary map | ownership and forbidden writes |
| What is supported? | capability matrix | supported, partial, out of scope |
| How large or fast? | headline figures / bars | units, source, limitation |
| What remains? | status board | stable IDs, owner, state, dependency |

One primary visual is normally enough. Secondary visuals are added only when they
answer a different decision.

## Template contract

`templates/proposal.html` retains the proposal/21 compatibility marker and adds:

```html
<meta name="common-rules-visual-contract" content="proposal/38">
```

The template contains reusable semantic classes for before/after panels, flows,
chips, a status rail, evidence blocks, and agent-context fields. It includes a
small accessible SVG scaffold as an example, not a mandated architecture.

The Luna section appears after `Decided` and supporting evidence:

```html
<details class="agent-context" id="luna-context">
  <summary>Luna implementation context · agent handoff</summary>
  ...stable labelled fields...
</details>
```

It is collapsed for ordinary human reading but remains in the document for an
agent or parser. “Luna” is the friendly handoff label; the content is model-neutral.

## Luna field contract

The context contains these stable field labels:

1. Outcome
2. Accepted decisions
3. Scope in
4. Scope out
5. Repository ownership
6. Implementation map
7. Contracts and data
8. Ordered implementation steps
9. Implementation verification
10. Risks and refusals
11. Dependencies and assumptions
12. Open questions
13. State management
14. Completion evidence

Each field carries placeholders in a new proposal. Before implementation, the
author replaces them with concrete values or `Unresolved — <reason>`. The handoff
must name exact files/symbols only when verified from the current repository.

Proposal acceptance requires document validation and sponsor review, not
executable tests. The Implementation verification field is a forward-looking
contract for delivery. Its checks become due when accepted scope enters
implementation and must not be represented as already run during proposal work.

## State model

```text
decision authority                    delivery evidence
proposal-status + Decided             ledger items + receipts
        │                                      │
        └────────── visual state rail ──────────┘
                         view only
```

The decision axis moves from proposed to accepted only with a recorded sponsor
answer. Completed, completed in part, deferred, amended, or superseded outcomes
retain their existing Common Rules meanings. The delivery axis summarizes the
ledger as planned, building, verifying, or released. A blocked/deferred state
names its reason; a superseded state names its replacement. No manually typed
rail value can override proposal metadata or ledger evidence.

## Skill and documentation

The short `visual-proposal` skill owns the invariant workflow and routes to the
visual-language reference when creating or materially restructuring a proposal.
The reference owns the detailed visual grammar and Luna schema, keeping idle skill
context small. The user guide explains the human/agent split; the README advertises
the outcome without duplicating the reference.

## Tooling verification

This release changes the generator and checker, so focused implementation tests
generate a proposal in a temporary Git repository and assert:

- compatibility and proposal/38 visual-contract metadata;
- visual primitives precede `Decisions`;
- `Decided` precedes the Luna context;
- all stable Luna field labels exist;
- accessible SVG and dark-mode token guidance remain in the template;
- the skill links its reference and the reference exists in the plugin package.

The full release gate then checks proposal lifecycle, plugin packaging, version
coherence, context budget, and every existing Common Rules test.

## Release ownership

This is a mandatory standard improvement and therefore a minor semantic release.
Version 1.12.0 updates `VERSION`, both plugin manifests, the pinned version test,
README release link, changelog, and release notes in one coherent change.
