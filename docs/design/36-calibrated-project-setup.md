# Proposal 36 design — repository truth, workspace coherence

Status: accepted · 2026-10-03

## The model

```text
                         COMMITTED HUB REPOSITORY
                    docs/common-rules/workspace.json
                         compatible revision set
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
          business logic        interface          documentation
          repo manifest         repo manifest      repo manifest
          own commits           own commits        own commits
          own ledgers           own ledgers        own ledgers
                 └──────────────────┼──────────────────┘
                                    ▼
                         joined tracker + tracecheck
                    (a view; never a synthetic commit)
```

Each repository is authoritative for its code and ledger. The hub is
authoritative only for membership and the compatible revision set. Local paths
are a disposable map from stable IDs to checkouts.

## Repository declaration

The optional `integration` object in `.common-rules.json` is additive:

```json
{
  "integration": {
    "repository_id": "engine",
    "role": "business-logic",
    "requirements": ["docs/requirements"],
    "tracker": "docs/proposals",
    "issue_linking": "off",
    "workspace": {"id": "product", "role": "member", "hub": "docs"},
    "skill_receipts": true
  }
}
```

`role` is one of `business-logic`, `interface`, `documentation`, `assets`,
`operations`, or `combined`. A single repository uses `combined` and omits the
workspace object.

## Setup lifecycle

```text
DISCOVER ──► CLASSIFY ──► ASK ONLY GAPS ──► PREVIEW ──► APPLY ──► DOCTOR
 read-only     topology      locations        diff       opt-in     repeatable
```

`bin/project-setup` implements discovery, preview/apply and doctor. It never
overwrites an existing declaration. If configuration exists, it merges only
explicitly supplied values and shows the resulting manifest before writing.

## Trace and impact gate

```text
requirement ─► feature item ─► docs/design ─► files ─► tests ─► receipt
     ▲                              │            │
     └──────── update or reviewed no-change ◄───┘
```

`bin/tracecheck` validates the graph. Against a Git base it also computes the
changed paths. A changed linked implementation path requires a changed ledger,
a changed requirement source, or a `no-change:` receipt owned by `lead` or
`sponsor`. This is a deterministic gate; an agent may propose the relationship,
but cannot waive it.

## Joined tracker

`bin/workspace-tracker` reads the hub manifest and the local registry, checks
each checkout and revision, validates its ledgers, then emits one responsive
HTML page. The page identifies repository, feature, stage and revision. It
does not write into members. A missing checkout can be represented as
unavailable, but a publish/check operation refuses it.

## Plugin surfaces

The portable package follows OpenAI's plugin layout: root `plugin.json`,
`skills/`, and `hooks/hooks.json`. Skills carry judgement and sequence; hooks
enforce deterministic boundaries. Every routed response says which Common
Rules skill is active and why. The visual-proposal skill owns the iterative
decision artifact. Setup, intake, planning, verification, repair and handoff
skills own their lifecycle stages.

Hooks are optional local automation and require trust. The shared hook file
uses `CLAUDE_PLUGIN_ROOT`, which OpenAI hosts expose as a compatibility alias,
and never assumes a checkout path. ChatGPT web receives the skill behaviour but
cannot execute a local hook without a connected local execution environment.

Claude Code reads `.claude-plugin/plugin.json`, discovers `skills/` and
`hooks/hooks.json` from its standard plugin layout, and can install this
repository through `.claude-plugin/marketplace.json`. The separate root
`plugin.json` remains the portable/OpenAI manifest; both manifests carry the
same name and version and package the same skills and hooks.

Official platform references: [plugins](https://learn.chatgpt.com/docs/plugins),
[skills](https://learn.chatgpt.com/docs/build-skills),
[plugin packaging](https://developers.openai.com/plugins/build/plugins), and
[hooks](https://learn.chatgpt.com/docs/hooks).

## Release boundary

This release adds contracts and tools. It does not create a two-way issue
system, merge multiple repositories together, silently install hooks, or
authorize GitHub writes. Those require explicit project configuration and
user authority.
