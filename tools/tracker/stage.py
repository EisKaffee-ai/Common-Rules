"""tracker stage -- record an intended ledger change without touching the
ledger (proposal 23, M-04: one writer for ledger and tracker files).

  tracker stage LEDGER ITEM_ID [--status S] [--reason TEXT] [--reopen]
                                [--owner O] [--field KEY=VALUE ...]
                                [--event TEXT [--evidence TEXT]]
                                [--by NAME] [--at ISO8601]

Same flags as `tracker set`, but nothing is read from or written to the
ledger itself: the change is written as its own file under
docs/proposals/.staging/, named so two builders' staged changes never
collide (each carries its own item id and timestamp) even when merged from
different branches. An item lead or builder never runs `tracker set` or
hand-edits ledger JSON -- it stages here, and the dispatcher applies every
staged file with `tracker apply-staged` when it merges that branch in.

`.staging/` is committed like any other file in the branch; nothing here
touches the ledger's `updated` date, its items, or its rendered page.

Exit codes: 0 written, 1 a bad `--field`, 2 the staging directory could not
be written to.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

from tools.tracker.set import FORBIDDEN_FIELDS, _now, _parse_field

STAGING_DIRNAME = ".staging"


def staging_dir(ledger: Path) -> Path:
    return ledger.parent / STAGING_DIRNAME


def stage_path(ledger: Path, item_id: str, at: str) -> Path:
    stamp = at.replace(":", "").replace("+", "_").replace(" ", "T")
    return staging_dir(ledger) / f"{ledger.stem}__{item_id}__{stamp}__{uuid.uuid4().hex[:6]}.json"


def main(argv) -> int:
    ap = argparse.ArgumentParser(prog="tracker stage", description=__doc__.splitlines()[0])
    ap.add_argument("ledger", type=Path)
    ap.add_argument("item_id")
    ap.add_argument("--status")
    ap.add_argument("--reason")
    ap.add_argument("--reopen", action="store_true")
    ap.add_argument("--owner")
    ap.add_argument("--field", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--event")
    ap.add_argument("--evidence", default="")
    ap.add_argument("--by", default="lead")
    ap.add_argument("--at")
    args = ap.parse_args(argv)
    say = "tracker stage:"

    fields: list[list] = []
    for raw in args.field:
        parsed = _parse_field(raw)
        if parsed is None:
            print(f"{say} --field {raw!r} is not KEY=VALUE -- nothing staged", file=sys.stderr)
            return 1
        key, value, shown = parsed
        if key in FORBIDDEN_FIELDS:
            print(f"{say} --field may not set {key!r} -- nothing staged", file=sys.stderr)
            return 1
        fields.append([key, value, shown])

    at = args.at or _now()
    record = {
        "item_id": args.item_id,
        "status": args.status,
        "reason": args.reason,
        "reopen": args.reopen,
        "owner": args.owner,
        "fields": fields,
        "event": args.event,
        "evidence": args.evidence,
        "by": args.by,
        "at": at,
    }

    out = stage_path(args.ledger, args.item_id, at)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"{say} {exc}", file=sys.stderr)
        return 2

    parts = []
    if args.status is not None:
        parts.append(f"status {args.status}")
    if args.reason is not None:
        parts.append("deferred reason recorded")
    if args.reopen:
        parts.append("explicit reopen")
    if args.owner is not None:
        parts.append(f"owner {args.owner}")
    for key, _, shown in fields:
        parts.append(f"field {key}={shown}")
    event_text = args.event if args.event is not None else args.status
    if event_text is not None:
        parts.append(f'log "{event_text}"')
    print(f"{say} {args.item_id} staged at {out} -- " + " · ".join(parts) if parts else
          f"{say} {args.item_id} staged at {out} (no change requested)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
