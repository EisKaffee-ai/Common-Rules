"""tracker apply-staged -- the dispatcher applies every builder's staged
change to a ledger, one at a time (proposal 23, M-04: one writer for ledger
and tracker files).

  tracker apply-staged LEDGER

Reads every file under LEDGER's sibling `.staging/` directory named
`<ledger stem>__*.json` (a `tracker stage` record), oldest first by its own
`at` field, and applies each with the same validated write `tracker set`
uses -- one item at a time, so two staged changes to the same item apply in
the order they were staged rather than racing. A staged file that applies
cleanly is deleted; one that fails (unknown item, or the ledger would not
validate after the change) is left in place and reported, and the run
still applies the rest.

This is meant to run only in the dispatcher's own worktree, against the
integration branch, after merging in a builder's branch -- never in an item
lead's own worktree.

Exit codes: 0 every staged file applied (or none were pending), 1 at least
one staged file failed and was left in place, 2 the ledger could not be
read.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from tools.tracker import ledger as L
from tools.tracker.set import _render, apply_change
from tools.tracker.stage import staging_dir


def pending(ledger: Path) -> list[Path]:
    d = staging_dir(ledger)
    if not d.is_dir():
        return []
    prefix = f"{ledger.stem}__"
    files = [p for p in d.iterdir() if p.is_file() and p.name.startswith(prefix) and p.suffix == ".json"]

    def sort_key(p: Path):
        try:
            rec = json.loads(p.read_text())
            return (rec.get("at") or "", p.name)
        except (OSError, ValueError):
            return ("", p.name)

    return sorted(files, key=sort_key)


def main(argv) -> int:
    ap = argparse.ArgumentParser(prog="tracker apply-staged", description=__doc__.splitlines()[0])
    ap.add_argument("ledger", type=Path)
    args = ap.parse_args(argv)
    say = "tracker apply-staged:"

    files = pending(args.ledger)
    if not files:
        print(f"{say} nothing staged for {args.ledger}")
        return 0

    try:
        data = L.load(args.ledger)
    except (OSError, ValueError) as exc:
        print(f"{say} {exc}", file=sys.stderr)
        return 2

    applied: list[str] = []
    failed: list[str] = []
    for f in files:
        try:
            rec = json.loads(f.read_text())
        except (OSError, ValueError) as exc:
            print(f"{say} {f.name}: unreadable -- {exc}, left in place", file=sys.stderr)
            failed.append(f.name)
            continue

        # Apply to a copy, never to `data` itself: a change that mutates an item
        # and only then fails validation must leave nothing behind, or the rest
        # of this run validates against a ledger the failed file already
        # poisoned -- every later staged file would then be refused on its
        # problem, and any of its own mutations a later file happened to make
        # valid again would land in the written ledger under a name this run
        # reported as "left in place".
        candidate = copy.deepcopy(data)
        fields = [(k, v, shown) for k, v, shown in rec.get("fields") or []]
        parts = apply_change(candidate, rec["item_id"], status=rec.get("status"), owner=rec.get("owner"),
                              fields=fields, event=rec.get("event"), evidence=rec.get("evidence", ""),
                              by=rec.get("by", "lead"), at=rec.get("at"),
                              reason=rec.get("reason"), reopen=bool(rec.get("reopen")))
        if parts is None:
            print(f"{say} {f.name}: {rec['item_id']} is not an item in {args.ledger} -- left in place",
                  file=sys.stderr)
            failed.append(f.name)
            continue

        problems = L.validate(candidate)
        if problems:
            print(f"{say} {f.name}: would not be well-formed after this change -- left in place:", file=sys.stderr)
            for p in problems:
                print(f"  {p}", file=sys.stderr)
            failed.append(f.name)
            continue

        data = candidate
        f.unlink()
        applied.append(f"{rec['item_id']} (" + " · ".join(parts) + ")")

    if applied:
        args.ledger.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        _render(data, args.ledger)
        for line in applied:
            print(f"{say} applied {line}")

    if failed:
        print(f"{say} {len(failed)} staged file(s) left in place: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
