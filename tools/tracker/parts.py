"""Lettered parts of an item (proposal 30, P-01).

An item that cannot reach 100% in one go is split into parts named after it:
W-10.A, W-10.B, ... Each part is a tracked sub-ticket with its own status and
a share of the item. The sponsor's words: "I like the naming convention with
ABC. That should be standardized as the standard approach. And each ticket
should be tracked in the tracker or sub-ticket."

A part:
  {"id": "W-10.A", "title": "...", "share": 20, "status": "done",
   "owner": "lead" | "sponsor" | "session:<name>",       optional
   "waiting_until": "YYYY-MM-DD",                         optional
   "risk": "high" | "medium" | "low", "risk_reason": "...",  optional, reason required with risk
   "log": [{"at", "event", "by", "evidence", "status"?}]}  optional

Rules, decided 2026-09-17 ("go with your recommendations", D1-D5):
  completion  the sum of the done parts' shares; an item with no parts is one
              part worth 100 carrying the item's own status.
  groups      done         every part done;
              waiting      every open part is owned by another project's
                           session or waits for a date after today;
              finish now   under 80% complete, or an open part is high risk;
              back burner  80% or more complete, no open part high risk.
  risk        the lead's call, with a stated reason (D3).
Shares are whole percents set by the lead when splitting (D2) and add up to
100. Letters run in order from A and are never reused.

Parts nest ("if there are more sub sub items", the sponsor, 17 Sep 2026): a
part may carry its own `parts`, named after it with numbers at the second
level (W-10.A.1, W-10.A.2) and lowercase letters at the third (W-10.A.1.a).
Sub-part shares add up to 100 within their parent; a part with sub-parts is
as complete as its done sub-parts' shares, and may only be done when they all
are.
"""
from __future__ import annotations

import datetime
import re

STATUSES = ("not started", "in progress", "in review", "in testing", "blocked", "done", "deferred")
TERMINAL_STATUSES = frozenset(("done", "deferred"))
RISKS = ("high", "medium", "low")
CUT = 80
GROUPS = ("finish now", "back burner", "waiting", "done")
_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def parts(item: dict) -> list[dict]:
    value = item.get("parts")
    return [p for p in value if isinstance(p, dict)] if isinstance(value, list) else []


def _label(depth: int, n: int) -> str | None:
    """The n-th sub-id at `depth` (0: A.., 1: 1.., 2: a..)."""
    if depth == 1:
        return str(n + 1)
    alphabet = _LETTERS if depth == 0 else _LETTERS.lower()
    return alphabet[n] if n < len(alphabet) else None


def validate_parts(item: dict, _depth: int = 0) -> list[str]:
    """Every problem with `item`'s parts (at every depth), as sentences naming the part."""
    value = item.get("parts")
    if value is None:
        return []
    iid = item.get("id") or "item"
    if _depth > 2:
        return [f"{iid}: parts nest at most three levels (W-10.A.1.a)"]
    if not isinstance(value, list) or not value:
        return [f"{iid}: `parts` must be a non-empty list"]
    problems: list[str] = []
    total = 0
    for n, p in enumerate(value):
        if not isinstance(p, dict):
            problems.append(f"{iid}: parts[{n}] is not an object")
            continue
        label = _label(_depth, n)
        expected = f"{iid}.{label}" if label else None
        pid = p.get("id")
        name = pid or f"{iid} parts[{n}]"
        if pid != expected:
            problems.append(f"{name}: part {n + 1} must be named {expected} "
                            f"({'letters from A' if _depth == 0 else 'numbers from 1' if _depth == 1 else 'letters from a'}, in order)")
        if not isinstance(p.get("title"), str) or not p["title"].strip():
            problems.append(f"{name}: missing `title`")
        share = p.get("share")
        if type(share) is not int or not 1 <= share <= 100:
            problems.append(f"{name}: `share` must be a whole percent from 1 to 100")
        else:
            total += share
        if p.get("status") not in STATUSES:
            problems.append(f"{name}: status {p.get('status')!r} is not one of {', '.join(STATUSES)}")
        if p.get("status") == "deferred":
            reason = p.get("deferred_reason")
            if not isinstance(reason, str) or not reason.strip() or any(ord(c) < 32 or 0x7f <= ord(c) <= 0x9f for c in reason):
                problems.append(f"{name}: deferred requires a non-empty one-line `deferred_reason`")
        elif "deferred_reason" in p:
            problems.append(f"{name}: `deferred_reason` is only valid while status is deferred")
        owner = p.get("owner")
        if owner is not None and (not isinstance(owner, str) or not owner.strip()):
            problems.append(f"{name}: `owner` must be a non-empty string")
        wait = p.get("waiting_until")
        if wait is not None and not _is_date(wait):
            problems.append(f"{name}: `waiting_until` must be a YYYY-MM-DD date")
        risk = p.get("risk")
        if risk is not None:
            if risk not in RISKS:
                problems.append(f"{name}: risk {risk!r} is not one of {', '.join(RISKS)}")
            if not isinstance(p.get("risk_reason"), str) or not p["risk_reason"].strip():
                problems.append(f"{name}: a risk needs a `risk_reason`")
        if p.get("log") is not None and not isinstance(p["log"], list):
            problems.append(f"{name}: `log` must be a list")
        if p.get("parts") is not None and pid == expected:
            problems.extend(validate_parts(p, _depth + 1))
    if not any("share" in x for x in problems) and total != 100:
        problems.append(f"{iid}: part shares add up to {total}, not 100")
    if item.get("status") in TERMINAL_STATUSES and any(p.get("status") not in TERMINAL_STATUSES for p in parts(item)):
        if item.get("status") == "done":
            problems.append(f"{iid}: status done while a part is still open")
        else:
            problems.append(f"{iid}: status deferred while a part is still open")
    return problems


def completion(item: dict) -> int:
    """Percent complete, rolled up through nested parts: each part contributes
    its share times its own completion; a part without sub-parts is 100 when
    done and 0 otherwise. An item without parts is 100 or 0."""
    ps = parts(item)
    if not ps:
        return 100 if item.get("status") in TERMINAL_STATUSES else 0
    total = 0.0
    for p in ps:
        share = p.get("share") if type(p.get("share")) is int else 0
        total += share * completion(p) / 100
    return int(round(total))


def tree(item: dict) -> dict:
    """{id, title, status, share, completion, parts: [...]} at every depth --
    what a drill-down view renders."""
    return {"id": item.get("id"), "title": item.get("title"), "status": item.get("status"),
            "share": item.get("share"), "owner": item.get("owner"),
            "deferred_reason": item.get("deferred_reason"),
            "waiting_until": item.get("waiting_until"), "risk": item.get("risk"),
            "risk_reason": item.get("risk_reason"), "completion": completion(item),
            "parts": [tree(p) for p in parts(item)]}


def open_parts(item: dict) -> list[dict]:
    ps = parts(item)
    if item.get("status") in TERMINAL_STATUSES:
        return []
    if not ps:
        return [_implicit(item)]
    return [p for p in ps if p.get("status") not in TERMINAL_STATUSES]


def next_part(item: dict) -> dict | None:
    """The first open part, in letter order."""
    ops = open_parts(item)
    return ops[0] if ops else None


def is_waiting(part: dict, today: datetime.date | None = None) -> bool:
    """Owned by another project's session, or waiting for a date after today."""
    today = today or datetime.date.today()
    owner = part.get("owner")
    if isinstance(owner, str) and owner.startswith("session:"):
        return True
    wait = part.get("waiting_until")
    return _is_date(wait) and datetime.date.fromisoformat(wait) > today


def group(item: dict, today: datetime.date | None = None) -> str:
    """One of GROUPS, by the rules in this module's docstring."""
    ops = open_parts(item)
    if not ops:
        return "done"
    if all(is_waiting(p, today) for p in ops):
        return "waiting"
    if completion(item) < CUT or any(p.get("risk") == "high" for p in ops):
        return "finish now"
    return "back burner"


def _implicit(item: dict) -> dict:
    """An item without parts, seen as its one part worth 100."""
    part = {"id": item.get("id"), "title": item.get("title"), "share": 100,
            "status": item.get("status") or "not started"}
    if item.get("owner"):
        part["owner"] = item["owner"]
    if item.get("deferred_reason"):
        part["deferred_reason"] = item["deferred_reason"]
    return part


def _is_date(value) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True
