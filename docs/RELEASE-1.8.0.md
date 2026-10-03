# Common Rules 1.8.0 release candidate

## Outcome

Version 1.8.0 turns the accepted calibrated-project proposal into an opt-in
release surface:

- `bin/project-setup` discovers, previews, applies and diagnoses a repository
  manifest without erasing existing project declarations;
- `bin/workspace-tracker` creates one mobile joined view from separately
  committed repositories and their compatible revision set;
- `bin/tracecheck` validates requirement-to-file evidence and restricts
  no-change receipts to the lead or sponsor;
- `bin/migration-check` proves that the Emberline main, published development,
  local-only history, source files and tags survive the Common Rules cutover;
- root `plugin.json` for OpenAI, `.claude-plugin/plugin.json` and marketplace
  metadata for Claude Code, shared lifecycle skills and portable trusted-hook
  definitions make the workflow installable and its routing visible;
- the visual-proposal skill keeps decision artifacts mobile-first and iterates
  them until sponsor acceptance.
- the Common Rules landing page gives Codex and Claude Code native marketplace
  setup, maps every lifecycle skill to worked examples, and replaces legacy
  screenshots with current, accessible SVG explainers.

Common Rules is now the tracker plugin. It supersedes the separate Emberline AI
Tracker runtime while preserving its ledger data model and migration evidence.

## Upgrade

Existing projects do not change automatically. Preview first:

```sh
common-rules/bin/project-setup --project . preview --repository-id my-project --role combined
```

Apply only after reviewing the output, then run doctor and tracecheck. A
workspace hub additionally records its members in
`docs/common-rules/workspace.json`; local checkout paths go in the ignored
`.common-rules/workspace.local.json`.

## Boundaries

This release does not enable two-way issue synchronization, combine application
repository histories, rewrite the Emberline source, choose a default branch,
trust hooks automatically, or grant remote-write authority. ChatGPT web
requires a connected execution environment for local commands and hooks.

## Publication checklist

- Proposal 36 and its ledger validate.
- `bin/migration-check --remote` proves source history, files, branches, tags,
  and the published release-candidate revision agree.
- Focused setup, workspace, trace and plugin tests pass.
- Full tests, workflow stamp, version check and conformance pass.
- An independent reviewer signs off on this restricted-risk Common Rules
  change.
- The sponsor merges and publishes the version/tag.

Platform references: [plugins](https://learn.chatgpt.com/docs/plugins),
[skills](https://learn.chatgpt.com/docs/build-skills),
[packaging](https://developers.openai.com/plugins/build/plugins), and
[hooks](https://learn.chatgpt.com/docs/hooks).

Claude compatibility references: [Claude Code plugins](https://code.claude.com/docs/en/plugins),
[manifest](https://code.claude.com/docs/en/plugins-reference),
[skills](https://code.claude.com/docs/en/skills),
[hooks](https://code.claude.com/docs/en/hooks), and
[marketplaces](https://code.claude.com/docs/en/plugin-marketplaces).
