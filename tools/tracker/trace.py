"""tracker trace -- update traceability state through a validated Python command.

  tracker trace LEDGER TRACE_ID [--status S] [--receipt TEXT] [--owner O]
                                  [--requirement ID] [--implementation-file PATH]
                                  [--test-command COMMAND]

The row must already exist. Identity, requirement links, implementation links
and test commands are not rewritten by this lifecycle command. The complete
ledger validates before the write, and the proposal page is regenerated after
it, so an agent never needs to edit ledger JSON or generated HTML directly.
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

from tools.tracker import ledger as L
from tools.tracker import render as R


def _render(data: dict, path: Path) -> None:
    out = R.default_out(path)
    text = R.render(data, path, R.infer_repo(path))
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.read_text() != text:
        out.write_text(text)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="tracker trace", description=__doc__.splitlines()[0])
    parser.add_argument("ledger", type=Path)
    parser.add_argument("trace_id")
    parser.add_argument("--status")
    parser.add_argument("--receipt")
    parser.add_argument("--owner")
    parser.add_argument("--requirement", action="append", default=[])
    parser.add_argument("--implementation-file", action="append", default=[])
    parser.add_argument("--test-command", action="append", default=[])
    args = parser.parse_args(argv)
    say = "tracker trace:"
    if (args.status is None and args.receipt is None and args.owner is None
            and not args.requirement and not args.implementation_file and not args.test_command):
        print(f"{say} no traceability change was supplied -- nothing written", file=sys.stderr)
        return 1
    try:
        data = L.load(args.ledger)
    except (OSError, ValueError) as exc:
        print(f"{say} {exc}", file=sys.stderr)
        return 2
    row = next((entry for entry in data.get("traceability", [])
                if isinstance(entry, dict) and entry.get("id") == args.trace_id), None)
    if row is None:
        print(f"{say} {args.trace_id} is not a traceability row in {args.ledger} -- nothing written",
              file=sys.stderr)
        return 1
    changed = []
    for key, value in (("status", args.status), ("receipt_or_refusal", args.receipt), ("owner", args.owner)):
        if value is not None:
            row[key] = value
            changed.append(key)
    for key, values in (("requirement_ids", args.requirement),
                        ("implementation_files", args.implementation_file),
                        ("tests_commands", args.test_command)):
        if values:
            current = list(row.get(key) or [])
            row[key] = current + [value for value in values if value not in current]
            changed.append(key)
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
    print(f"{say} {args.trace_id} updated {', '.join(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
