# Common Rules 1.10.1 release candidate

## Outcome

Version 1.10.1 adds an optional canonical-project mode without changing older
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

Existing row-level issue workflows and manifests without proposal granularity
retain their current behavior.

## Context footprint

The release measures prompt context separately from process memory. Both Codex
and Claude Code progressively load skills: discovery metadata is visible first,
then a selected `SKILL.md`, then only the references that workflow needs.

| Surface | Bytes | Estimated tokens | Load behavior |
|---|---:|---:|---|
| 13 skill names, descriptions, and paths | 2,505 | 627 | idle discovery |
| all `SKILL.md` files | 24,620 | 6,155 | one selected skill at a time |
| optional references | 3,068 | 767 | only when explicitly needed |
| full skill-package ceiling | 27,688 | 6,922 | never the default load |
| hook configuration/scripts | — | 0 idle | only returned output enters context |

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
about 70% faster. The aggregate runner still reports the complete test count,
failures and errors and preserves the underlying exit code.

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
    "issue_sync_direction": "ledger-to-github"
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
