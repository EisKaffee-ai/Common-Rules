# Getting started

EisKaffee.ai / Common Rules supplies a shared workflow for Claude Code and Codex projects.
The repository name and existing paths remain `common-rules`.

## Session commands

In an adopting project's chat, use `/warmup` for a fresh session and `/reheat`
to refresh a running session. These are chat commands, not shell commands.
They read and check the repository record; tracker tools generate the page.

See the [warm-up skill](../skills/warmup/SKILL.md),
[reheat skill](../skills/reheat/SKILL.md), and
[shared workflow](../CLAUDE-workflow.md) for setup and the operating contract.

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

## Boundaries

The tracker is a generated snapshot, not automatic synchronization of all
chat activity. Durable decisions must be recorded. It does not replace human
acceptance, repository tests, or issue tracking. Features and integrations
depend on the project's adoption of the standard.

Keep accepted slices small and land them through the repository's required
review and test gates. Preserve Git history. See [VERSION](../VERSION) and
[CHANGELOG](../CHANGELOG.md) for the current release and changes.
