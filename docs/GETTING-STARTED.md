# Getting started

EisKaffee.ai / Common Rules supplies a shared workflow for Claude Code and Codex projects.
The repository name and existing paths remain `common-rules`.

## Install the plugin

Codex can register this repository as a marketplace source:

```sh
codex plugin marketplace add EisKaffee-ai/Common-Rules
```

Restart the ChatGPT desktop app, install `common-rules` from the
**EisKaffee.ai Common Rules** source in the Plugins Directory, then ask Codex
to use the Common Rules setup skill.

Claude Code uses the same repository:

```sh
claude plugin marketplace add EisKaffee-ai/Common-Rules
claude plugin install common-rules@eiskaffee-common-rules
```

Run `/common-rules:setup` in the adopting project. On either host, review the
calibration preview before authorizing the manifest write. Installation does
not imply hook trust or GitHub write access.

## Session commands

In an adopting project's chat, use `/warmup` for a fresh session and `/reheat` or `/preheat`
to refresh a running session. These are chat commands, not shell commands.
They read and check the repository record; tracker tools generate the page.

See the [warm-up skill](../skills/warmup/SKILL.md),
[reheat skill](../skills/reheat/SKILL.md),
[preheat alias](../skills/preheat/SKILL.md), and
[shared workflow](../CLAUDE-workflow.md) for setup and the operating contract.

For the legacy AGENTS-first context-only setup on both hosts, run
`bin/install-agent-context --project PATH`. This includes the preheat alias and
preserves existing rules. The plugin setup above is the current full tracker
adoption path.

## Keep the native goal and repository record aligned

Use the host's `/goal` for the durable execution objective. If the project
needs the objective to remain visible after a handoff or compaction, add this
small optional mirror to `.common-rules.json`:

```json
{
  "goal": {
    "outcome": "Ship the smallest useful release",
    "constraints": ["Preserve existing behavior"],
    "verification": ["Run the merge gate", "Review the generated tracker"]
  }
}
```

Warm-up and the generated project tracker print this contract. A goal change
also makes the tracker page stale until it is regenerated, so the published
view cannot silently carry old acceptance criteria. Keep it short and update
it when the outcome or completion test changes; the native goal remains the
execution control, while the repository contract is the handoff and
verification view.

Warm-up validates every discovered ledger to build its compact status card, but
does not ask the session to reopen every raw ledger JSON. Open the full ledger
only for the item being worked, unless the project explicitly lists a ledger
in `read_order`.

## Repository tools

From this repository:

```sh
./bin/warmup --project . --check
./bin/tracker board --project .
python3 -m unittest discover -s tests -q
```

## What is stored

[Proposal ledgers](proposals/) hold decisions, tasks, owners, asks, findings,
and evidence. The [tracker](proposals/tracker/index.html) is generated from
those records. Edit the records through the supported tools, then regenerate
the tracker; do not hand-edit the generated page.

Tree, Kanban, Board, and List provide different views of the same work.
Search and filter by status, owner, work group, and tier. Progress charts
describe recorded task history; a completion projection is an estimate.
`deferred` is a green terminal state that requires a reason, stays in history,
and is excluded from active-work and blocker counts. Reopen it only with
`tracker set ... --status <non-terminal> --reopen`.

## Boundaries

The tracker is a generated snapshot, not automatic synchronization of all
chat activity. Durable decisions must be recorded. It does not replace human
acceptance, repository tests, or issue tracking. Features and integrations
depend on the project's adoption of the standard.

Keep accepted slices small and land them through the repository's required
review and test gates. Preserve Git history. See [VERSION](../VERSION) and
[CHANGELOG](../CHANGELOG.md) for the current release and changes.
