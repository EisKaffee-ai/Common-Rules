"""Writes a checkpoint from the open ledger(s) under a project (proposal 19,
W-07 / D8): the record a PreCompact or Stop hook leaves on disk before a
compaction's summary is made, so what survives the cut is the ledger's own
state, not a paraphrase of it (proposal 19 section K).

    python3 -m tools.tracker.checkpoint [--project DIR] [--out PATH]
                                         [--reason precompact|stop|manual]
                                         [--if-changed]

A checkpoint is a snapshot: the default output path is dated to the day, and
a second run on the same day overwrites it. `--if-changed` skips the rewrite
when the ledger content driving it has not moved, so a Stop hook firing every
turn does not touch the file on every ordinary turn.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from tools.tracker import ledger
from tools.tracker import parts as PT  # proposal 30, P-04

DIGEST_RE = re.compile(r"<!--\s*ledger-digest:\s*([0-9a-f]{64})\s*-->")


def _is_open(items: list[dict]) -> bool:
    """A ledger is open when it has items and at least one is non-terminal."""
    return bool(items) and not all(i.get("status") in ledger.TERMINAL_STATUSES for i in items)


def open_ledgers(project) -> list[tuple[Path, dict]]:
    """Every ledger under `project` whose items are not all done, in
    `ledger.find` order. A ledger file that fails to parse is skipped with a
    warning on stderr rather than aborting every other ledger's checkpoint."""
    out: list[tuple[Path, dict]] = []
    for p in ledger.find(project):
        try:
            d = ledger.load(p)
        except ValueError as exc:
            print(f"checkpoint: skipping {p}: {exc}", file=sys.stderr)
            continue
        if _is_open(ledger.items(d)):
            out.append((p, d))
    return out


def latest_checkpoint(project) -> Path | None:
    """The most recently dated checkpoint already on disk, or None."""
    handovers = Path(project) / "docs" / "handovers"
    if not handovers.is_dir():
        return None
    found = sorted(handovers.glob("*-checkpoint.md"))
    return found[-1] if found else None


def digest_of(paths: list[Path]) -> str:
    """sha256 of the concatenated raw bytes of every ledger file, in order --
    the fingerprint `--if-changed` compares against."""
    h = hashlib.sha256()
    for p in paths:
        h.update(Path(p).read_bytes())
    return h.hexdigest()


def git_info(project) -> tuple[str | None, str | None]:
    """(branch, short HEAD), or (None, None) outside a git repo / on any
    git failure -- never raises."""
    try:
        branch = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        head = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if branch.returncode != 0 or head.returncode != 0:
            return None, None
        return branch.stdout.strip(), head.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None, None


def _last_log_field(item: dict, field: str, fallback: str) -> str:
    log = item.get("log") or []
    if not log:
        return fallback
    return str(log[-1].get(field) or fallback)


def _bullets(lines: list[str]) -> str:
    return "\n".join(lines) if lines else "- none"


def _in_progress_section(items: list[dict]) -> str:
    lines = [
        f"- {i.get('id')} · {i.get('tag', '')} · {i.get('title', '')} · "
        f"{_last_log_field(i, 'event', 'no log entry yet')}"
        for i in items if i.get("status") == "in progress"
    ]
    return _bullets(lines)


def _blocked_section(items: list[dict]) -> str:
    lines = [
        f"- {i.get('id')} · {_last_log_field(i, 'evidence', 'no log entry yet')}"
        for i in items if i.get("status") == "blocked"
    ]
    return _bullets(lines)


def _open_asks_section(d: dict) -> str:
    lines = [f'- {a.get("id")} · "{a.get("quote", "")}"' for a in ledger.open_asks(d)]
    return _bullets(lines)


def _next_unblocked_section(d: dict) -> str:
    lines = [
        f"- {i.get('id')} · {i.get('tag', '')} · {i.get('title', '')}"
        for i in ledger.unblocked(d)
    ]
    return _bullets(lines)


def _next_part_note(item: dict, today) -> str:
    """` · next W-10.A (waiting ...)`, or "" for an item with no open part."""
    nxt = PT.next_part(item)
    if nxt is None:
        return ""
    note = f" · next {nxt.get('id')}"
    if PT.is_waiting(nxt, today):
        owner = nxt.get("owner")
        if isinstance(owner, str) and owner.startswith("session:"):
            note += f" (waiting on {owner[len('session:'):]})"
        elif nxt.get("waiting_until"):
            note += f" (waiting {nxt['waiting_until']})"
    return note


def _groups_section(items: list[dict], today) -> str:
    """Open items (proposal 30, P-04), grouped by PT.group -- `done` items
    are not open work and are left out, same as the flat sections above.
    Short by design: one line per open item, its completion % and next
    part, under the group it falls in."""
    by_group: dict[str, list[str]] = {g: [] for g in PT.GROUPS if g != "done"}
    for i in items:
        g = PT.group(i, today)
        if g not in by_group:
            continue
        # An item without `parts` has no real "next part" to point at --
        # PT.next_part would name the item itself, which says nothing.
        note = _next_part_note(i, today) if i.get("parts") is not None else ""
        by_group[g].append(f"- {i.get('id')} {PT.completion(i)}%{note}")
    sections = [f"**{g}**\n" + "\n".join(lines) for g in ("finish now", "back burner", "waiting") if (lines := by_group[g])]
    return "\n".join(sections) if sections else "- none"


def _exact_next_action(ledgers: list[tuple[Path, dict]]) -> str:
    if not ledgers:
        return "none open"
    _, first = ledgers[0]
    items = ledger.items(first)
    in_progress = [i for i in items if i.get("status") == "in progress"]
    if in_progress:
        i = in_progress[0]
        return f"{i.get('id')} · {i.get('tag', '')} · {i.get('title', '')}"
    unblocked = ledger.unblocked(first)
    if unblocked:
        i = unblocked[0]
        return f"{i.get('id')} · {i.get('tag', '')} · {i.get('title', '')}"
    return "none open"


def render(ledgers: list[tuple[Path, dict]], digest: str, reason: str,
           project, now: datetime) -> str:
    branch, head = git_info(project)
    if branch and head:
        info_line = f"Reason: {reason} · branch: {branch} · HEAD: {head}"
    else:
        info_line = f"Reason: {reason} · HEAD unknown"

    parts = [
        f"# Checkpoint — {now:%Y-%m-%d} {now:%H:%M}",
        info_line,
        f"<!-- ledger-digest: {digest} -->",
    ]
    today = now.date()
    for path, d in ledgers:
        items = ledger.items(d)
        parts.append(f"## Proposal {d.get('proposal')} · {d.get('title', '')}")
        parts.append(ledger.status_line(d))
        parts.append("### In progress")
        parts.append(_in_progress_section(items))
        parts.append("### Blocked, and why")
        parts.append(_blocked_section(items))
        parts.append("### Open asks")
        parts.append(_open_asks_section(d))
        parts.append("### Next unblocked")
        parts.append(_next_unblocked_section(d))
        # Proposal 30, P-04: open work by group, short -- completion % and
        # the next open part, instead of scanning every item's own line for it.
        parts.append("### Open work by group")
        parts.append(_groups_section(items, today))
    parts.append("## Exact next action")
    parts.append(_exact_next_action(ledgers))
    return "\n\n".join(parts) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="checkpoint")
    parser.add_argument("--project", default=".")
    parser.add_argument("--out")
    parser.add_argument("--reason", choices=("precompact", "stop", "manual"), default="manual")
    parser.add_argument("--if-changed", action="store_true")
    args = parser.parse_args(argv)

    project = Path(args.project).resolve()
    ledgers = open_ledgers(project)
    if not ledgers:
        print(f"checkpoint: no open ledger under {project}")
        return 0

    digest = digest_of([p for p, _ in ledgers])
    now = datetime.now()
    out = Path(args.out) if args.out else project / "docs" / "handovers" / f"{now:%Y-%m-%d}-checkpoint.md"

    if args.if_changed and out.exists():
        existing = out.read_text()
        m = DIGEST_RE.search(existing)
        if m and m.group(1) == digest:
            print("checkpoint: unchanged")
            return 0

    content = render(ledgers, digest, args.reason, project, now)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content)
    print(f"checkpoint: wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
