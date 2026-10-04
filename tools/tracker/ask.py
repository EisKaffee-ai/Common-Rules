"""tracker ask -- record a sponsor ask as A-nn, in place of an inline
`python3 -` script that loads a ledger, appends an ask and dumps it back
(proposal 23, lever L4, L-04). Also closes an existing ask (ASK-01): moving
it from "open" to "answered"/"became-item"/"declined" otherwise meant
hand-editing ledger JSON, which the rules forbid.

  tracker ask LEDGER --kind KIND --quote TEXT [--state STATE] [--by NAME]
                      [--at ISO8601] [--owner O] [--became ITEM]
                      [--source TEXT] [--note TEXT] [--review ITEM]

  tracker ask LEDGER --close A-nn --state answered|became-item|declined
                      [--became ITEM] [--note TEXT] [--by NAME] [--at ISO8601]
                      [--force]

Every sponsor message that is not an answer becomes an ask (docs/OPERATING-
RULES.md section 1), quoting his words exactly -- `--quote` is stored as
given, with no trimming beyond a single trailing newline, typos and quote
marks and all.

The new id is the next free A-nn, zero-padded to the width the ledger's
existing asks already use (or two digits, for the first one). `--state`
defaults to "open", `--by` to "sponsor".

`--close A-nn` moves an existing ask out of "open" instead of creating one.
It sets `state`; sets `became` when given (required for "became-item", and
the item id must name a real item in the same ledger); appends `--note` to
the ask's existing `note` (joined with " · "), or sets it when there was
none; and records `answered_at`/`answered_by` (mirroring the `answered_by`
requests already carry -- P20 D7) from `--at`/`--by` (`--by` defaults to
"lead" when closing, since the ask's own `by` already names who asked).
Refuses, nothing written: `--close` together with `--quote`/`--kind`; an
unknown ask id; `--state open`; `--state became-item` without a `--became`
that names a real item; closing an ask that is not currently `open`, unless
`--force`.

Validated with the change already applied, before anything is written: on
any problem the problems are printed and the file is untouched (exit 1). On
success the ledger is written (indent=2, ensure_ascii=False, trailing
newline) and its page is re-rendered.

Exit codes: 0 written, 1 a finding, 2 could not read the ledger.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

from tools.tracker import ledger as L
from tools.tracker import render as R

ASK_NUM = re.compile(r"^A-(\d+)\Z")


def _now() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _next_id(data: dict) -> str:
    asks = data.get("asks") or []
    nums = []
    width = 2
    for a in asks:
        m = ASK_NUM.match(str(a.get("id", "")))
        if m:
            nums.append(int(m.group(1)))
            width = max(width, len(m.group(1)))
    n = (max(nums) + 1) if nums else 1
    return f"A-{n:0{width}d}"


def _render(data: dict, path: Path) -> None:
    out = R.default_out(path)
    repo = R.infer_repo(path)
    text = R.render(data, path, repo)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.read_text() != text:
        out.write_text(text)


def _find_ask(data: dict, ask_id: str) -> dict | None:
    for a in data.get("asks") or []:
        if isinstance(a, dict) and a.get("id") == ask_id:
            return a
    return None


def _create(args, say: str) -> int:
    if args.kind is None or args.quote is None:
        print(f"{say} --kind and --quote are required -- nothing written", file=sys.stderr)
        return 1

    try:
        data = L.load(args.ledger)
    except (OSError, ValueError) as exc:
        print(f"{say} {exc}", file=sys.stderr)
        return 2

    quote = args.quote[:-1] if args.quote.endswith("\n") else args.quote

    if args.review is not None:
        if args.review not in L.by_id(data):
            print(f"{say} --review {args.review} is not an item in {args.ledger} -- nothing written",
                  file=sys.stderr)
            return 1
        at = args.at or _now()
        by = args.by or "sponsor"
        for existing in data.get("asks") or []:
            if (isinstance(existing, dict) and existing.get("review") == args.review
                    and existing.get("state") == "open"):
                feedback = list(existing.get("feedback") or [])
                feedback.append({"at": at, "by": by, "quote": quote})
                existing["feedback"] = feedback
                data["updated"] = datetime.date.today().isoformat()
                problems = L.validate(data)
                if problems:
                    print(f"{say} {args.ledger} would not be well-formed after this change -- nothing written:",
                          file=sys.stderr)
                    for problem in problems:
                        print(f"  {problem}", file=sys.stderr)
                    return 1
                args.ledger.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
                _render(data, args.ledger)
                print(f"{say} {existing['id']} review {args.review} coalesced ({len(feedback)} feedback)")
                return 0

    new_id = _next_id(data)
    ask = {
        "id": new_id,
        "at": args.at or _now(),
        "by": args.by or "sponsor",
        "kind": args.kind,
        "quote": quote,
        "became": args.became,
        "state": args.state,
    }
    if args.owner is not None:
        ask["owner"] = args.owner
    if args.source is not None:
        ask["source"] = args.source
    if args.note is not None:
        ask["note"] = args.note
    if args.review is not None:
        ask["review"] = args.review
        ask["feedback"] = [{"at": ask["at"], "by": ask["by"], "quote": quote}]

    asks = list(data.get("asks") or [])
    asks.append(ask)
    data["asks"] = asks
    data["updated"] = datetime.date.today().isoformat()

    problems = L.validate(data)
    if problems:
        print(f"{say} {args.ledger} would not be well-formed after this change -- nothing written:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    args.ledger.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    _render(data, args.ledger)
    print(f"{say} {new_id} {args.kind} {args.state}")
    return 0


def _close(args, say: str) -> int:
    if args.kind is not None or args.quote is not None:
        print(f"{say} --close may not be combined with --kind/--quote -- nothing written", file=sys.stderr)
        return 1
    if args.state not in L.ASK_STATES or args.state == "open":
        print(f"{say} --close needs --state answered|became-item|declined (not {args.state!r}) -- nothing written",
              file=sys.stderr)
        return 1

    try:
        data = L.load(args.ledger)
    except (OSError, ValueError) as exc:
        print(f"{say} {exc}", file=sys.stderr)
        return 2

    ask = _find_ask(data, args.close)
    if ask is None:
        print(f"{say} {args.close} is not an ask in {args.ledger} -- nothing written", file=sys.stderr)
        return 1

    if ask.get("state") != "open" and not args.force:
        print(f"{say} {args.close} is not open (state {ask.get('state')!r}) -- use --force to override -- "
              f"nothing written", file=sys.stderr)
        return 1

    if args.state == "became-item":
        if not args.became:
            print(f"{say} --state became-item needs --became ITEM-ID -- nothing written", file=sys.stderr)
            return 1
        if args.became not in L.by_id(data):
            print(f"{say} --became {args.became} is not an item in {args.ledger} -- nothing written", file=sys.stderr)
            return 1

    ask["state"] = args.state
    if args.became is not None:
        ask["became"] = args.became
    if args.note is not None:
        existing = ask.get("note")
        ask["note"] = f"{existing} · {args.note}" if existing else args.note
    ask["answered_at"] = args.at or _now()
    ask["answered_by"] = args.by or "lead"
    data["updated"] = datetime.date.today().isoformat()

    problems = L.validate(data)
    if problems:
        print(f"{say} {args.ledger} would not be well-formed after this change -- nothing written:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    args.ledger.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    _render(data, args.ledger)
    print(f"{say} {args.close} closed -> {args.state}")
    return 0


def main(argv) -> int:
    ap = argparse.ArgumentParser(prog="tracker ask", description=__doc__.splitlines()[0])
    ap.add_argument("ledger", type=Path)
    ap.add_argument("--kind")
    ap.add_argument("--quote")
    ap.add_argument("--state", default="open")
    ap.add_argument("--by")
    ap.add_argument("--at")
    ap.add_argument("--owner")
    ap.add_argument("--became")
    ap.add_argument("--source")
    ap.add_argument("--note")
    ap.add_argument("--review", metavar="ITEM_ID",
                    help="coalesce this comment into the open review ask for ITEM_ID")
    ap.add_argument("--close", metavar="ASK_ID")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    say = "tracker ask:"

    if args.close:
        return _close(args, say)
    return _create(args, say)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
