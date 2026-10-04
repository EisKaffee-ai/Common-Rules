# Visual proposal language

Use this reference when creating or substantially restructuring a Common Rules
proposal. The sponsor-facing page is a visual decision surface. The bottom Luna
implementation context is the precise handoff to the implementation agent.

## Choose the smallest visual that answers the question

| The decision asks… | Use | Must show |
|---|---|---|
| What changes? | before / after | old state, new state, important delta |
| Which option? | option cards plus a comparison table | trade-off, cost, verdict |
| How does data or control move? | flow | direction, authority, read/write boundary |
| What happens over time? | lifecycle or step rail | order, transitions, stop states |
| Who owns what? | hierarchy or boundary map | owner, dependency, forbidden writes |
| What is supported? | capability matrix | implemented, partial, missing, out of scope |
| How large, fast, or complete? | headline figures or bars | unit, baseline, source |
| What remains? | status board | stable ID, owner, status, dependency |

Do not add a diagram merely because a page has several sections. One primary
visual is normally enough. Add another only when it answers a different decision.

## Visual grammar

- Put the verdict before the evidence trail.
- Use two to four headline figures. Never decorate the page with meaningless
  numbers.
- Put evidence directly below the claim it supports. Name the source and what
  was not verified.
- Keep labels short. Move supporting prose into `details`.
- Use stable colors by meaning: positive, warning, blocked, neutral. Do not rely
  on color alone; repeat the state in text.
- Use CSS variables for inline SVG fills and strokes. Every meaningful SVG has a
  `title` and `desc`.
- Verify the page at a phone width and in both light and dark color schemes.

## Required proposal order

1. Identity and one-sentence outcome.
2. Sponsor ask quoted verbatim.
3. Decision at a glance: verdict, facts, and one primary visual.
4. Options or capability comparison when a real choice exists.
5. Stable decisions `D1`, `D2`, ….
6. `Decided`, with the sponsor's exact answer once accepted.
7. Expandable evidence and sources.
8. Luna implementation context as the final section.

The proposal stays the same file through exploration and acceptance. Do not
replace it with a second implementation plan that loses the visual rationale.

## Luna implementation context

“Luna” is the friendly handoff label. The contract is model-neutral: any agent
should be able to execute it from the accepted proposal and current repository.
Keep it in `<details class="agent-context" id="luna-context">` at the bottom so
human readers can stop at the decision while agents can read the full context.

Populate every field below. If a fact is not verified, write `Unresolved —` and
the reason. Do not infer support from a filename or architecture document.

### Outcome

One observable result. Name the user or system behavior that changes.

### Accepted decisions

Map every `D<n>` to the sponsor's accepted answer. Proposed decisions remain
explicitly unresolved and must not be treated as implementation authority.

### Scope in

Concrete capabilities and behaviors included in this proposal.

### Scope out

Explicit non-goals, deferred capabilities, and wire contracts that must not
change without approval.

### Repository ownership

For every repository, state its role and the paths it owns. Preserve separate
commits and compatible revisions when more than one repository is involved.

### Implementation map

Name verified files, symbols, entry points, and supporting tests. If the code has
not been inspected, say so instead of guessing paths.

### Contracts and data

Record protocols, schemas, formats, storage locations, authority boundaries,
limits, caching, concurrency, errors, persistence, and lifecycle behavior that
must remain compatible.

### Ordered implementation steps

Give the smallest dependency-ordered steps. Each step names its outputs and stop
condition. Do not hide a product decision inside an implementation step.

### Implementation verification

Describe the tests, commands, or manual observations the later implementation
must use. These are a future delivery contract, not work required to propose,
review, or accept the proposal. A proposal needs structural validation, visual
review, and sponsor acceptance; executable tests begin when implementation begins.
State what each verification proves and what it does not prove.

### Risks and refusals

Name destructive actions, data ownership boundaries, security/privacy concerns,
release gates, and conditions that require the agent to stop and ask.

### Dependencies and assumptions

Name required versions, services, fixtures, artifacts, compatible revisions, and
assumptions that were actually verified.

### Open questions

Only unresolved questions that can materially change implementation. Give each a
stable ID so an answer can be reconciled without rewriting the proposal.

### State management

Keep decision state and delivery state separate:

| Axis | Source of truth | Typical states | Transition authority |
|---|---|---|---|
| Decision | `proposal-status` and the verbatim `Decided` block | proposed → accepted → completed / completed in part; superseded is explicit | sponsor answer recorded in the proposal |
| Delivery | ledger items, parts, reviews, tests, and release receipts | not started → planned → building → verifying → released; deferred/blocked remain explicit | evidence-backed tracker transition by the owning workflow |

The visual state rail summarizes both axes but never becomes a third source of
truth. Record the current state, allowed next state, who may transition it, the
required evidence, and any deferred reason or superseding proposal.

### Completion evidence

State the exact receipts required before the item may be called done: tests,
review, traceability, screenshots or rendered pages, release artifacts, commits,
and compatible revisions. Acceptance of the proposal is not completion evidence.
