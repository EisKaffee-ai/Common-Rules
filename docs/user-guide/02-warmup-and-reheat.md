# Warm-up, reheat and preheat

There are three command names and two behaviours. `/warmup` establishes a fresh session. `/reheat` and `/preheat` refresh an existing session and share the same baseline.

## Fresh session

Run `/warmup`. Read the files in the reported order, beginning with the project's AGENTS.md when using the agent-context installer. The card checks declared context, ledgers and checkpoint and identifies pending work. It does not inject the full contents of every file into the agent automatically.

## Refresh a running session

Run `/reheat` or `/preheat`. Both show changes since the last saved baseline. Read changed instructions and source evidence before continuing. With no saved baseline, establish the full context first. If a compaction leaves you unsure what has been read, use `/warmup` again.

## Install the commands

```sh
./bin/install-agent-context --project /path/to/project
```

This preserves AGENTS.md and installs all three skills into `.agents/skills` and `.claude/skills`. It does not replace hooks or certify full tracker conformance. A new host session may be needed to discover installed skills.

The existing full installer `bin/derecord` retains its historical warmup/reheat installation. Use the agent-context installer for the new cross-host preheat alias.

## Shell equivalents

```sh
./bin/warmup --project /path/to/project --no-pull --no-recall
./bin/warmup --project /path/to/project --reheat --no-pull --no-recall
```

There is no separate bin/reheat executable. Preheat uses the second command too. The flags keep this session on its installed rules revision and avoid optional recall while reconstructing project context.

## Durable state

Record decisions and next work in the project ledger and generate its checkpoint. These are repository state that agents read independently; a manually composed chat handoff is not required by the AGENTS-first configuration. Configuration and evidence remain the source of truth, not conversational recollection.
