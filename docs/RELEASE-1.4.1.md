# EisKaffee.ai / Common Rules 1.4.1

## Changes

- Adopts the EisKaffee.ai / Common Rules identity while preserving original Emberline history and licenses.
- Includes the 1.3.0 development history and subsequent local tracker fixes.
- Adds `bin/install-agent-context` for AGENTS-first context in Codex and Claude.
- Installs warmup, reheat and preheat. Preheat aliases reheat; both refresh the same saved state.
- Preserves project instructions and refuses to overwrite unmanaged skills.
- Documents the explicit read order for design guidelines, templates and durable task state.

## Install into a project

Keep a pinned checkout inside `.common-rules/runtime` (ignored by the project), then run its `bin/install-agent-context --project .`. Record the resolved release commit in `common-rules.lock.json`. Installed skills use a relative path when the runtime is inside the project. Do not silently advance the runtime branch after installation.

A new Codex or Claude session may be required to discover newly installed skills. Warmup checks and hashes the declared files; the agent must still read them. Installation does not prove full historical conformance, approve architecture, or authorize website publication.

## Compatibility

Existing warmup/reheat usage remains supported. The historical full installer is unchanged; the agent-context installer is opt-in. Project-specific instructions and safety constraints remain authoritative for their project. No original repository has been deleted or transferred by this migration.

## Verification

Full local suite: 2,017 tests passed. Installer regression tests additionally cover shared baseline state and symlinked configuration, skill and state destinations. Review performed in two report-only rounds; findings addressed. GitHub CI remains the final remote check.
