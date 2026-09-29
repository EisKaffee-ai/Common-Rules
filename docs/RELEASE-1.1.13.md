# Emberline 1.1.13

This release adds a first-class `deferred` tracker state. Deferred items are
terminal and green, require a reason, stay visible in history, do not count as
active work or blockers, and can only be reopened explicitly.

Use:

```sh
bin/tracker set docs/proposals/NN-title.json ITEM-01 \
  --status deferred --reason "out of scope for this release"
```

To reopen one deliberately:

```sh
bin/tracker set docs/proposals/NN-title.json ITEM-01 \
  --status in progress --reopen
```

The repository is released under Apache-2.0 for code and CC BY 4.0 for
documentation and visual assets. See [`LICENSE`](../LICENSE),
[`LICENSE-DOCS`](../LICENSE-DOCS), and [`NOTICE`](../NOTICE).
