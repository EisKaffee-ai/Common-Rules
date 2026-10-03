# Common Rules 1.10.3 release candidate

## Outcome

Version 1.10.3 adds an optional canonical-project mode without changing older
projects:

- a configured nested ledger catalogue owns one generated tracker page;
- Overview, Product delivery, Architecture, Repositories, and Evidence are
  views of that page rather than competing trackers;
- `tracker sync --project` produces a deterministic, whole-set-validated issue
  plan with one GitHub issue per proposal and one stable checkbox per item;
- the ledger stays authoritative and GitHub drift is reconciled explicitly;
- the installed GitHub provider performs authorized mutations—Common Rules
  does not use browser automation, `gh`, hidden HTTP calls, or reverse sync;
- Codex and Claude Code receive the same portable manifest and lifecycle
  skills.
- mixed architecture and operational ledger series remain on one page while
  only the configured architecture series receives GitHub issues;
- shipped Python commands own every generated tracker identifier, count,
  digest, mapping, state transition, history row, checkpoint and HTML surface.

Existing row-level issue workflows and manifests without proposal granularity
retain their current behavior.

Agents may supply explicit source text and invoke the commands. They do not
invent generated IDs or numbers, directly rewrite ledger JSON, or hand-edit
generated HTML. External providers assign their own IDs; Common Rules records
the returned value through a validating Python command.

That write-back preflights the complete issue set, validates an atomic ledger
write, and regenerates both the proposal and canonical tracker pages. Setup
doctor applies the full integration contract, and setup validates every local
checkout argument before writing. Proposal-mode workspace checks resolve every
mapped member and verify its pinned Git revision; tracecheck diffs qualified
implementation paths against those revisions instead of checking existence
alone.

## Context footprint

The release measures prompt context separately from process memory. Both Codex
and Claude Code progressively load skills: discovery metadata is visible first,
then a selected `SKILL.md`, then only the references that workflow needs.

<!-- context-budget:start -->
| Surface | UTF-8 bytes | Estimated tokens | What actually loads |
|---|---:|---:|---|
| Idle skill discovery (13 names, descriptions, paths) | 2,505 | 627 | Every session/request |
| All `SKILL.md` files combined | 25,751 | 6,438 | Not together; only the selected skill is loaded |
| Optional references | 3,225 | 807 | Only when the selected workflow needs one |
| Full skill-package ceiling | 28,976 | 7,244 | Comparison ceiling; never the default load |
| Hook configuration and scripts | — | 0 idle | Execute outside context; returned output is the only cost |
<!-- context-budget:end -->

The discovery estimate is 26% below 1.9.0 (849 → 627 tokens). The detailed
proposal-issue procedure is an on-demand tracker reference, and the release
gate refuses discovery above 650 estimated tokens. Reproduce the receipt with:

```sh
./bin/context-budget --compare-ref 7ce6ff2  # Common Rules 1.9.0
./bin/context-budget --json --check
```

Counts use the documented, tokenizer-independent estimate of UTF-8 bytes / 4,
rounded up. They are not process RAM or provider billing telemetry.

## Test-gate performance

The first parallel run no longer waits for one whole slow file merely to learn
its duration. Large files are split by test class on a cold checkout and later
runs reuse measured shard timings. On the release host, all 124 warmup tests
completed in 174.6 seconds versus the previously documented 575-second floor,
about 70% faster. The final release gate passed all 2,088 tests in 189.6 seconds. The aggregate runner still reports the complete test count, failures
and errors and preserves the underlying exit code. `bin/quiet --receipt`
writes a digest-bound machine record of the exact command and result;
`bin/release-evidence` accepts only the full merge-gate discovery receipt and
refreshes both public documents and the canonical ledger. Release measurements
are not entered by an agent.

## Acceptance fixture

The read-only EisKaffee Vanilla catalogue contains 27 proposal groups, 59
features, and 362 lifecycle rows. The local plan preserves Proposal 08's
mapping to Bean Engine issue #2; the connected GitHub repository exposes
exactly 27 `[Architecture NN/27]` issues. The configured workspace check
confirms one canonical tracker page.

Downstream Docs adoption remains independently committed. Publication requires
its final manifest, traceability, website build receipt, and exact issue-plan
reconciliation to pass without this Common Rules session writing into Docs.

## Upgrade

Preview the optional settings before applying them:

```json
{
  "integration": {
    "tracker": "path/to/canonical/ledgers",
    "issue_linking": "one-way",
    "issue_repository": "owner/repository",
    "issue_granularity": "proposal",
    "issue_sync_direction": "ledger-to-github",
    "issue_series": "documentation-delivery"
  }
}
```

Then run `project-setup doctor`, generate the complete issue plan, inspect it,
and authorize the installed GitHub provider only when the proposed remote
delta is correct.

## Publication checklist

- Context budget, version sync, workflow stamp, plugin manifests, focused tests,
  and the full unit suite pass.
- The real Docs catalogue passes read-only setup, tracker, workspace,
  traceability, and build checks at its own committed revision.
- The 27-issue remote set reconciles exactly with the ledger-generated plan.
- Independent review and CI pass before merge, tag, and public release.

Platform references: [OpenAI skill loading](https://developers.openai.com/plugins/concepts/skills),
[OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins),
and [Claude Code context costs](https://code.claude.com/docs/en/features-overview#understand-context-costs).
