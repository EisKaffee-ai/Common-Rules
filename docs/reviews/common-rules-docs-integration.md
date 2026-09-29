# Common Rules migration and documentation-session review

Reviewed 29 September 2026 from a fresh clone of codeDEXTER/emberline-ai-tracker.

## Source status

- GitHub main: 03e56ee, VERSION 1.1.12.
- GitHub w10-measured: b8a8b41, VERSION 1.3.0; five commits ahead of main, 52 changed files.
- Existing local installation: w10-measured at 7aefa56, four further commits beyond the published development branch.
- Do not silently replace the existing installation with the older main branch. Preserve the development branch and local commits during migration; review them before selecting a default baseline.
- EisKaffee-ai/Common-Rules was created private. The initial history push was rejected because the active OAuth credential lacks workflow scope. No source history was removed and no original repository was transferred/deleted.

## Does it support the desired session flow?

Partly. tools/project.py supports a project-owned .common-rules.json read_order. bin/warmup gathers those files, checks their existence and hashes their contents (lines 691–715 in inspected main). The warm card lists the files to read. --reheat uses saved state to report changes. The agent still has to actually read and follow the files: listing/hashing them is not a guarantee of comprehension.

Default read_order is HANDOFF.md and docs/OPERATING-RULES.md, not AGENTS.md. It can be overridden; tests/test_project_declaration.py includes an app-shaped configuration that runs without HANDOFF.md. This is the right extension point for the docs project.

The docs repository currently has no .common-rules.json, tracker ledger, installed Common Rules skills or hooks. Its AGENTS.md and UI guidelines exist, but they are not yet registered with Common Rules.

## Gaps found

1. bin/derecord installs warmup/reheat into .claude/skills only. Codex .agents/skills parity is missing in both inspected branches.
2. The existing command is reheat, implemented as bin/warmup --reheat. There is no preheat command. Add preheat as a compatibility alias rather than another state mechanism.
3. Root AGENTS.md names Codex-workflow.md, which is absent. The actual shared file is CLAUDE-workflow.md. Adopt a host-neutral canonical name with compatibility pointers rather than duplicating rules.
4. Declared file lists are explicit; an AGENTS.md link does not automatically register every referenced template for change detection. Include each template/UI standard or introduce a validated scoped context manifest with deterministic expansion.
5. Existing warmup can fetch/pull shared rules. For versioned documentation sessions, default to the installed/pinned rules revision; report available updates without silently changing the accepted authoring standard.
6. Several project state and conformance items remain open. A new repository name must not be represented as completion of those tasks.

## Recommended docs configuration

read_order should begin with AGENTS.md, then UI-UX-GUIDELINES.md, versions.json, REVIEW-STATUS.md, and the five templates. Register the approved UI revision and publication state in a durable ledger. Agents read that record at warmup and resume the next unfinished item; no separately composed chat handoff is required.

Warmup should display: rules version/commit, docs tooling version, content revision and dirty state, accepted UI baseline, unapproved content changes, next task, required reading and test commands. Reheat/preheat should identify exactly which files changed and require rereading them. Neither command should claim to have updated source from remote unless it actually fetched it.

## Implementation sequence

1. Complete the non-destructive GitHub migration after workflow scope is available. Preserve main, development branch and tags; account explicitly for local-only commits. Rename public-facing identity to Common Rules, retaining licenses, attribution and old command compatibility.
2. Add and test a host-neutral, idempotent installer: preserve project AGENTS.md; install .agents/skills and .claude/skills; resolve the installed rules path; provide warmup/reheat/preheat aliases.
3. Add an AGENTS-first docs profile using existing read_order and gates. Avoid installing broad hooks that rewrite unrelated project files merely to satisfy adoption.
4. Register the docs project and validate fresh-session, resumed-session, changed-template, missing-file and stale-version cases with disposable test repositories.
5. Start a fresh agent session in docs and verify its warmup identifies the guidelines, accepted baseline and next work without conversational history. Existing sessions may need reopening before newly installed skills appear.

No human UI acceptance should be inferred from tests. The user's acceptance of the current EisKaffee.ai Docs UI should be recorded as a layout decision, separately from product-release compatibility and permission to publish.

## Validation

Fresh-clone project declaration suite passed: 74 tests in 116.805 seconds using Python 3.12.4 (`python -m unittest discover -s tests -p test_project_declaration.py -q`). This verifies declaration behaviours covered by that suite; it does not certify installation into the docs repository or cross-host skill discovery.
