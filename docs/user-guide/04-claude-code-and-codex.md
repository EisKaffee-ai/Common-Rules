# Claude Code and Codex

Common Rules is consumer-neutral. Claude Code and OpenAI Codex may expose
different commands, skills, or tools, but they can use the same project record
and follow the same operating contract.

## Adoption path

1. In Codex, add `EisKaffee-ai/Common-Rules` with
   `codex plugin marketplace add` and install `common-rules` from the desktop
   Plugins Directory. In Claude Code, use `claude plugin marketplace add`
   followed by `claude plugin install common-rules@eiskaffee-common-rules`.
2. Ask Codex to use the Common Rules setup skill, or run
   `/common-rules:setup` in Claude Code.
3. Review discovery and the proposed calibration. Confirm requirements,
   tracker and workspace locations before applying the project manifest.
4. Start a fresh work session with `/warmup` and confirm the tracker is valid.
5. Use `/reheat` or `/preheat` when the same session needs a delta.

`bin/install-agent-context --project PATH` remains available for legacy
AGENTS-first context-only adoption. It does not replace the calibrated plugin
setup for the full tracker lifecycle.

See [Getting started](../GETTING-STARTED.md) for the short path and
[`CLAUDE-workflow.md`](../../CLAUDE-workflow.md) for the full contract.

## What is shared

The shared parts are the record shape, proposal lifecycle, handover rules,
verification gates, and the meaning of warm-up and reheat. The adapter layer
can differ: a host can expose a skill, a hook, or a shell wrapper as long as
it preserves the same durable behavior.

## Human responsibility

The agent may prepare a proposal, update evidence, and render a tracker. The
sponsor or maintainer still accepts scope, resolves ambiguous decisions, and
approves changes to shared rules.

## Goals

Use the host's native `/goal` when work spans multiple turns. Make it express
an outcome, constraints, and a verifiable end state. For projects that need
that intent visible to the next session, mirror the same compact contract in
`.common-rules.json` under `goal.outcome`, `goal.constraints`, and
`goal.verification`. Warm-up shows it on the card so the agent does not need
to reconstruct the objective from chat history; the generated tracker shows
the same contract and becomes stale when the goal mirror changes.
