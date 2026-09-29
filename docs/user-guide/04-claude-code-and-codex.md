# Claude Code and Codex

Emberline is consumer-neutral. Claude Code and OpenAI Codex may expose
different commands, skills, or tools, but they can use the same project record
and follow the same operating contract.

## Adoption path

1. Copy or reference the shared rules from the adopting project.
2. Seed the handoff, operating, proposal, and checkpoint files with
   `bin/derecord` where appropriate.
3. Install the session hooks for the chosen host.
4. Start with `/warmup` and confirm the tracker is valid.
5. Use `/reheat` when the same session needs a delta.

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
