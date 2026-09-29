"""tracker set -- one-line ledger updates, in place of an inline `python3 -`
script that loads a ledger, changes one item and dumps it back (proposal 23,
lever L4, L-04). Proposal 30 (P-02) extends it to an item's lettered parts.

  tracker set LEDGER ITEM_ID [--status S] [--reason TEXT] [--reopen]
                              [--owner O] [--field KEY=VALUE ...]
                              [--event TEXT [--evidence TEXT]]
                              [--by NAME] [--at ISO8601]

Changes only what is given. `--field` values parse as JSON when the value is
valid JSON (so `--field weight=2` writes the number 2, `--field flag=true`
writes true), else they are stored as the string given; `--field` may not
touch `id`, `log` or `phase` -- those are this command's own business, or an
identity nothing should rewrite.

`--status` without `--event` appends a log entry whose event is the new
status; `--event` (with or without `--status`) appends a log entry with that
text instead. Either way, `--status` also stamps that log entry's own
`status` key with the new status (RF-01: bin/conformance item 9 finds an
item's own close date from a log entry's `status` key, not `event` --
`--event` is free text a lead writes, and 35 of 92 done items in the real
ledgers already close with an `--event` that is not literally "done"). `--by`
names who logged it (default "lead"); `--at` is the log entry's own time,
ISO 8601 with an offset (default: now, local, seconds precision).

Parts (proposal 30, P-01's shape, see tools/tracker/parts.py):

  tracker set LEDGER W-10.B --status done --event "..." [--field KEY=VALUE]
                             [--owner O] [--evidence TEXT] [--by NAME] [--at ISO]
                             [--waiting-until D]

An ITEM_ID with a `.LETTER` suffix targets that lettered part instead of the
item: the same --status/--owner/--event/--evidence/--by/--at handling
applies, but the log entry is appended to the *part's own* `log`, and
`--field` may only touch a part's `owner`, `waiting_until`, `risk`,
`risk_reason`, `title` or `share` (so `--field share=30` writes the int 30).

`--waiting-until` edits an item's or an already-existing part's own
`waiting_until` directly (proposal 30, P-13 -- previously the flag only took
effect with `--add-part`, so editing an existing wait needed the clumsier
`--field waiting_until=...`, which could set a date but not remove one).
`--waiting-until YYYY-MM-DD` sets the date; `--waiting-until none` (or
`--waiting-until now`) removes the `waiting_until` key entirely rather than
setting it to anything -- the tracker page's "pull forward" affordance
copies exactly this to clear a date-based wait.
When that change leaves every part of the item done, `set` also closes the
item: its `status` becomes "done" and an item-level log entry
{event: "all parts done", status: "done"} is appended. Setting an item
(not a part) to `--status done` while a part is still open is refused --
`ledger.validate()` reports it (P-01) and this command prints that finding
before refusing to write.

  tracker set LEDGER W-10 --add-part "title" --share N [--status S] [--owner O]
                           [--waiting-until D] [--risk R --risk-reason T]

Appends one new part to W-10, lettered after however many parts it already
has (A, B, C, ...). Repeat the command to add more; because every write is
validated first, shares must add up to 100 *after* the command that
completes them, so the lead adds the last part (or edits an existing
--field share=N) once the total is right.

  tracker set LEDGER W-10 --parts '[{"title": "...", "share": 40}, ...]'

The simpler way to give an item all its parts at once: replaces an item that
has no parts yet with the given list, letters assigned A.. in order. Refused
if the item already has parts.

The ledger is validated with the change already applied, before anything is
written: on any problem the problems are printed and the file is untouched
(exit 1). An unknown item id, unknown part, or a part reached without its
parent existing is the same -- exit 1, nothing written. On success the
ledger is written (indent=2, ensure_ascii=False, trailing newline -- the
format the engine's own ledgers already use), `updated` moves to today, and
the page is re-rendered with tools/tracker/render.py so the page never falls
behind the ledger it was set from. The one-line output names the part (or
item) changed and, when the item has parts, its new completion percent
(tools/tracker/parts.py's `completion`).

Exit codes: 0 written, 1 a finding (or nothing to check against), 2 could
not read the ledger.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

from tools.tracker import ledger as L
from tools.tracker import parts as PARTS
from tools.tracker import render as R

FORBIDDEN_FIELDS = frozenset({"id", "log", "phase"})
PART_FIELDS = frozenset({"owner", "waiting_until", "risk", "risk_reason", "deferred_reason", "title", "share"})
PART_ID = re.compile(r"^(.+)\.([A-Z])$")

# proposal 30, P-13: `--waiting-until` on an *existing* item or part previously
# only ever set a date (and only from `--add-part` -- editing an already-set
# part or item ignored the flag entirely, see below). The tracker page's
# "pull forward" button needs a command that actually clears a wait, so
# these two tokens mean "remove the date" instead of setting one.
CLEAR_WAITING_TOKENS = frozenset({"none", "now"})


def _now() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _apply_waiting_until(container: dict, value: str) -> str:
    """Set or clear `waiting_until` on an item or part dict, in place.
    Returns the human-readable change for the command's own output."""
    if value.strip().lower() in CLEAR_WAITING_TOKENS:
        had = container.pop("waiting_until", None)
        return "waiting_until cleared" if had is not None else "waiting_until already clear"
    container["waiting_until"] = value
    return f"waiting_until {value}"


def _parse_field(raw: str) -> tuple[str, object, str] | None:
    """"KEY=VALUE" -> (key, parsed value, the value text as given), or None
    when there is no `=`."""
    if "=" not in raw:
        return None
    key, _, value = raw.partition("=")
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, ValueError):
        parsed = value
    return key, parsed, value


def _deferred_transition(container: dict, status: str | None, reason: str | None,
                         reopen: bool) -> None:
    """Apply the explicit deferral/reopen contract to an item or part."""
    old = container.get("status")
    if reason is not None and status != "deferred":
        raise ValueError("--reason requires --status deferred")
    if reopen and (old != "deferred" or status in (None, "deferred")):
        raise ValueError("--reopen requires a deferred item and a new non-deferred --status")
    if status == "deferred":
        if old != "deferred" and not reason:
            raise ValueError("--status deferred requires --reason")
        if reason is not None:
            container[L.DEFERRED_REASON] = reason
    elif status is not None and old == "deferred":
        if not reopen:
            raise ValueError("a deferred item may only be reopened explicitly with --reopen")
        container.pop(L.DEFERRED_REASON, None)


def apply_change(data: dict, item_id: str, *, status: str | None = None, owner: str | None = None,
                  fields: list[tuple[str, object, str]] = (), event: str | None = None,
                  evidence: str = "", by: str = "lead", at: str | None = None,
                  waiting_until: str | None = None, reason: str | None = None,
                  reopen: bool = False) -> list[str] | None:
    """Apply one change to an already-loaded ledger `data` in place. Returns
    the human-readable parts on success, or None (nothing changed) when
    `item_id` is not in `data` -- the caller decides how to report that.
    Shared by `tracker set` (applies straight to a checked-out ledger) and
    `tracker apply-staged` (proposal 23, M-04 -- applies a builder's staged
    change on the dispatcher's behalf), so both take one path to a written
    ledger."""
    item = L.by_id(data).get(item_id)
    if item is None:
        return None

    parts = []
    _deferred_transition(item, status, reason, reopen)
    if status is not None:
        item["status"] = status
        parts.append(f"status {status}")
    if reason is not None:
        parts.append("deferred reason recorded")
    if owner is not None:
        item["owner"] = owner
        parts.append(f"owner {owner}")
    if waiting_until is not None:
        parts.append(_apply_waiting_until(item, waiting_until))
    for key, value, shown in fields:
        item[key] = value
        parts.append(f"field {key}={shown}")

    event_text = event if event is not None else status
    if event_text is not None:
        log_evidence = evidence or (reason if status == "deferred" else "")
        entry = {
            "at": at or _now(),
            "event": event_text,
            "by": by,
            "evidence": log_evidence,
        }
        if status is not None:
            # RF-01: the log entry's own `status` key is what bin/conformance
            # item 9 reads for an item's close date -- independent of
            # `event`, which is free text (an `--event` override, a lead's
            # own wording) that does not reliably spell "done".
            entry["status"] = status
        item.setdefault("log", []).append(entry)
        parts.append(f'log "{event_text}"')

    data["updated"] = datetime.date.today().isoformat()
    return parts


def split_target(item_id: str) -> tuple[str, str | None]:
    """"W-10" -> ("W-10", None); "W-10.B" -> ("W-10", "B")."""
    m = PART_ID.match(item_id)
    return (m.group(1), m.group(2)) if m else (item_id, None)


def _next_letter(n: int) -> str:
    letters = PARTS._LETTERS
    return letters[n] if n < len(letters) else f"#{n + 1}"


def add_part(item: dict, title: str, share: int, *, status: str | None = None, owner: str | None = None,
             waiting_until: str | None = None, risk: str | None = None, risk_reason: str | None = None,
             reason: str | None = None) -> str:
    """Append one new lettered part to `item`, in place. Returns its id."""
    ps = item.setdefault("parts", [])
    letter = _next_letter(len(ps))
    part_id = f"{item.get('id')}.{letter}"
    part = {"id": part_id, "title": title, "share": share, "status": status or "not started"}
    if owner:
        part["owner"] = owner
    if waiting_until:
        part["waiting_until"] = waiting_until
    if risk:
        part["risk"] = risk
        if risk_reason:
            part["risk_reason"] = risk_reason
    if reason is not None:
        part[L.DEFERRED_REASON] = reason
    ps.append(part)
    return part_id


def set_parts(item: dict, spec_list: list) -> None:
    """Replace `item`'s (empty) parts with `spec_list`, in place, lettering
    A.. in order. Raises ValueError if `item` already has parts."""
    if PARTS.parts(item):
        raise ValueError(f"{item.get('id')}: already has parts -- --parts only replaces an item with none yet")
    new_parts = []
    for n, spec in enumerate(spec_list):
        if not isinstance(spec, dict):
            raise ValueError(f"--parts[{n}] is not an object")
        letter = _next_letter(n)
        part = {"id": f"{item.get('id')}.{letter}", "title": spec.get("title"), "share": spec.get("share"),
                "status": spec.get("status") or "not started"}
        for k in ("owner", "waiting_until", "risk", "risk_reason", L.DEFERRED_REASON):
            if spec.get(k) is not None:
                part[k] = spec[k]
        new_parts.append(part)
    item["parts"] = new_parts


def apply_part_change(data: dict, parent_id: str, letter: str, *, status: str | None = None,
                       owner: str | None = None, fields: list[tuple[str, object, str]] = (),
                       event: str | None = None, evidence: str = "", by: str = "lead",
                       at: str | None = None, waiting_until: str | None = None,
                       reason: str | None = None, reopen: bool = False) -> list[str] | None:
    """Apply one change to part `parent_id`.`letter`, in place. Returns the
    human-readable parts on success, or None when the item or the part is
    not found. Raises ValueError for a `--field` not allowed on a part.

    When this leaves every part of the item done, also closes the item
    itself (status "done", an item-level log entry {"event": "all parts
    done", "status": "done"}) -- proposal 30, P-02's roll-up rule."""
    item = L.by_id(data).get(parent_id)
    if item is None:
        return None
    ps = PARTS.parts(item)
    part_id = f"{parent_id}.{letter}"
    part = next((p for p in ps if p.get("id") == part_id), None)
    if part is None:
        return None

    changed = []
    _deferred_transition(part, status, reason, reopen)
    if owner is not None:
        part["owner"] = owner
        changed.append(f"owner {owner}")
    if waiting_until is not None:
        changed.append(_apply_waiting_until(part, waiting_until))
    for key, value, shown in fields:
        if key not in PART_FIELDS:
            raise ValueError(f"--field may not set {key!r} on a part -- allowed: {', '.join(sorted(PART_FIELDS))}")
        part[key] = value
        changed.append(f"field {key}={shown}")
    if status is not None:
        part["status"] = status
        changed.append(f"status {status}")
    if reason is not None:
        changed.append("deferred reason recorded")

    event_text = event if event is not None else status
    if event_text is not None:
        entry = {"at": at or _now(), "event": event_text, "by": by,
                 "evidence": evidence or (reason if status == "deferred" else "")}
        if status is not None:
            entry["status"] = status
        part.setdefault("log", []).append(entry)
        changed.append(f'log "{event_text}"')

    if ps and all(p.get("status") == "done" for p in ps) and item.get("status") != "done":
        item["status"] = "done"
        item.setdefault("log", []).append({
            "at": _now(), "event": "all parts done", "by": by, "evidence": "", "status": "done",
        })
        changed.append("item done (all parts done)")

    data["updated"] = datetime.date.today().isoformat()
    return changed


def _render(data: dict, path: Path) -> None:
    out = R.default_out(path)
    repo = R.infer_repo(path)
    text = R.render(data, path, repo)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.read_text() != text:
        out.write_text(text)


def main(argv) -> int:
    ap = argparse.ArgumentParser(prog="tracker set", description=__doc__.splitlines()[0])
    ap.add_argument("ledger", type=Path)
    ap.add_argument("item_id")
    ap.add_argument("--status")
    ap.add_argument("--reason", help="required with --status deferred; records why it was deferred")
    ap.add_argument("--reopen", action="store_true", help="explicitly reopen a deferred item or part")
    ap.add_argument("--owner")
    ap.add_argument("--field", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--event")
    ap.add_argument("--evidence", default="")
    ap.add_argument("--by", default="lead")
    ap.add_argument("--at")
    ap.add_argument("--add-part", metavar="TITLE")
    ap.add_argument("--share", type=int)
    ap.add_argument("--waiting-until", help="YYYY-MM-DD to set, or 'none'/'now' to clear (P-13)")
    ap.add_argument("--risk")
    ap.add_argument("--risk-reason")
    ap.add_argument("--parts", metavar="JSON")
    args = ap.parse_args(argv)
    say = "tracker set:"

    fields: list[tuple[str, object, str]] = []
    for raw in args.field:
        parsed = _parse_field(raw)
        if parsed is None:
            print(f"{say} --field {raw!r} is not KEY=VALUE -- nothing written", file=sys.stderr)
            return 1
        key, value, shown = parsed
        if key in FORBIDDEN_FIELDS:
            print(f"{say} --field may not set {key!r} -- nothing written", file=sys.stderr)
            return 1
        fields.append((key, value, shown))

    try:
        data = L.load(args.ledger)
    except (OSError, ValueError) as exc:
        print(f"{say} {exc}", file=sys.stderr)
        return 2

    parent_id, letter = split_target(args.item_id)

    if args.add_part is not None or args.parts is not None:
        if letter is not None:
            print(f"{say} --add-part/--parts take an item id, not a part id ({args.item_id}) -- nothing written",
                  file=sys.stderr)
            return 1
        item = L.by_id(data).get(args.item_id)
        if item is None:
            print(f"{say} {args.item_id} is not an item in {args.ledger} -- nothing written", file=sys.stderr)
            return 1

    if args.add_part is not None:
        if args.parts is not None:
            print(f"{say} --add-part and --parts are alternatives -- nothing written", file=sys.stderr)
            return 1
        if args.share is None:
            print(f"{say} --add-part needs --share -- nothing written", file=sys.stderr)
            return 1
        if args.risk and not args.risk_reason:
            print(f"{say} --risk needs --risk-reason -- nothing written", file=sys.stderr)
            return 1
        new_wait = None if (args.waiting_until and args.waiting_until.strip().lower() in CLEAR_WAITING_TOKENS) \
            else args.waiting_until
        if args.reopen:
            print(f"{say} --reopen cannot be used with --add-part -- nothing written", file=sys.stderr)
            return 1
        if args.status == "deferred" and not args.reason:
            print(f"{say} --status deferred requires --reason -- nothing written", file=sys.stderr)
            return 1
        part_id = add_part(item, args.add_part, args.share, status=args.status, owner=args.owner,
                            waiting_until=new_wait, risk=args.risk, risk_reason=args.risk_reason,
                            reason=args.reason)
        data["updated"] = datetime.date.today().isoformat()
        result = [f"added {part_id}", f"share {args.share}"]
        if args.status:
            result.append(f"status {args.status}")
        if args.owner:
            result.append(f"owner {args.owner}")
        target_item = item
    elif args.parts is not None:
        try:
            spec_list = json.loads(args.parts)
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"{say} --parts is not valid JSON: {exc} -- nothing written", file=sys.stderr)
            return 1
        if not isinstance(spec_list, list) or not spec_list:
            print(f"{say} --parts must be a non-empty JSON list -- nothing written", file=sys.stderr)
            return 1
        try:
            set_parts(item, spec_list)
        except ValueError as exc:
            print(f"{say} {exc} -- nothing written", file=sys.stderr)
            return 1
        data["updated"] = datetime.date.today().isoformat()
        result = [f"{len(spec_list)} part(s) added"]
        target_item = item
    elif letter is not None:
        try:
            result = apply_part_change(data, parent_id, letter, status=args.status, owner=args.owner,
                                        fields=fields, event=args.event, evidence=args.evidence,
                                        by=args.by, at=args.at, waiting_until=args.waiting_until,
                                        reason=args.reason, reopen=args.reopen)
        except ValueError as exc:
            print(f"{say} {exc} -- nothing written", file=sys.stderr)
            return 1
        if result is None:
            print(f"{say} {args.item_id} is not a part in {args.ledger} -- nothing written", file=sys.stderr)
            return 1
        target_item = L.by_id(data).get(parent_id)
    else:
        result = apply_change(data, args.item_id, status=args.status, owner=args.owner, fields=fields,
                               event=args.event, evidence=args.evidence, by=args.by, at=args.at,
                               waiting_until=args.waiting_until, reason=args.reason, reopen=args.reopen)
        if result is None:
            print(f"{say} {args.item_id} is not an item in {args.ledger} -- nothing written", file=sys.stderr)
            return 1
        target_item = L.by_id(data).get(args.item_id)

    problems = L.validate(data)
    if problems:
        print(f"{say} {args.ledger} would not be well-formed after this change -- nothing written:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    args.ledger.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    _render(data, args.ledger)
    if target_item is not None and PARTS.parts(target_item):
        result.append(f"completion {PARTS.completion(target_item)}%")
    result.append("page rendered")
    print(f"{say} {args.item_id} " + " · ".join(result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
