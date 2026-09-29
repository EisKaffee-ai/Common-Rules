"""bin/tracker sync -- GitHub issues mirror the ledger, one way (proposal 19, W-04).

The ledger is the source of truth; issues are its public face (section I).
This module never reads the ledger's own opinion of "the truth" back into
itself except the one thing that has nowhere else to live: the issue number
a freshly created issue was given. Everything else -- create on in
progress/blocked/done with no issue yet, close on done, and report drift
rather than silently reopening or relabelling -- flows one way, ledger to
GitHub.

Every `gh` call goes through `run_gh` so tests can replace it with a fake
that never touches the network. `main(argv) -> int` follows bin/tracker's
exit codes: 0 in sync, 1 drift (or a write-back that could not be made
safely), 2 could not check at all (bad ledger, unreadable file, gh failed).

Proposal 20, D5: a ledger can record `switches.issues.on: false` -- a sponsor
decision to run without a GitHub mirror for that app. When it is off, sync
makes no gh call at all (not even a read), writes nothing back, prints one
sentence naming who switched it off and when, and exits 0.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from tools.tracker import ledger

CREATABLE_STATUSES = ("in progress", "blocked", "done")
TERMINAL_STATUSES = frozenset(("done", "deferred"))

_NEXT_ID = re.compile(r'"id":')


def run_gh(args: list[str]) -> str:
    """The one place a `gh` subprocess is ever started. Tests replace this."""
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return result.stdout


def _parse_issue_number(output: str) -> int:
    """`gh issue create` prints the new issue's URL; the number is its tail."""
    m = re.search(r"(\d+)\s*$", output.strip())
    if not m:
        raise ValueError(f"could not parse an issue number from: {output!r}")
    return int(m.group(1))


def _last_evidence(item: dict) -> str:
    log = item.get("log") or []
    if not log:
        return ""
    return str(log[-1].get("evidence") or "")


def _apply_writeback(text: str, item_id: str, number: int) -> tuple[str, str | None]:
    """Replace the one `"issue": null` in item_id's span with its new number.

    Returns (new_text, error). error is None on success; on failure the
    returned text is the input, unchanged, byte for byte.
    """
    marker = f'"id": "{item_id}"'
    start = text.find(marker)
    if start == -1:
        return text, f"`{marker}` not found in the ledger text"
    tail_start = start + len(marker)
    m = _NEXT_ID.search(text, tail_start)
    end = m.start() if m else len(text)
    span = text[start:end]
    old = '"issue": null'
    count = span.count(old)
    if count != 1:
        return text, f"expected exactly one `{old}` between {item_id} and the next item, found {count}"
    new_span = span.replace(old, f'"issue": {number}', 1)
    return text[:start] + new_span + text[end:], None


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="tracker sync", add_help=False)
    p.add_argument("ledger_path", metavar="LEDGER.json")
    p.add_argument("--repo")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    ledger_path = args.ledger_path
    repo_args = ["--repo", args.repo] if args.repo else []

    try:
        raw_text = Path(ledger_path).read_text()
    except OSError as exc:
        print(f"tracker sync: {ledger_path}: {exc}", file=sys.stderr)
        return 2

    try:
        data = ledger.load(ledger_path)
    except ValueError as exc:
        print(f"tracker sync: {exc}", file=sys.stderr)
        return 2

    problems = ledger.validate(data)
    if problems:
        print(f"tracker sync: {ledger_path}: {len(problems)} problem(s)", file=sys.stderr)
        for line in problems:
            print(f"  {line}", file=sys.stderr)
        return 2

    if not ledger.switch_on(data, "issues"):
        sw = data["switches"]["issues"]
        line = (f"sync {ledger_path}: issues switched off by {sw.get('by')} "
                f"at {sw.get('at')} — nothing synced")
        quote = sw.get("quote")
        if quote:
            line += f' "{quote}"'
        print(line)
        return 0

    proposal_n = data["proposal"]
    proposal_label = f"proposal:{proposal_n}"
    items = ledger.items(data)
    tier_labels = sorted({f"tier:{i['tier']}" for i in items if i.get("tier")})

    if not args.dry_run:
        try:
            for name in [proposal_label, *tier_labels]:
                run_gh(["label", "create", name, "--force", *repo_args])
        except (subprocess.CalledProcessError, OSError) as exc:
            print(f"tracker sync: gh label create failed: {exc}", file=sys.stderr)
            return 2

    try:
        out = run_gh([
            "issue", "list", "--label", proposal_label, "--state", "all",
            "--limit", "1000", "--json", "number,state,title", *repo_args,
        ])
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"tracker sync: gh issue list failed: {exc}", file=sys.stderr)
        return 2
    try:
        issues_by_number = {i["number"]: i for i in json.loads(out)}
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        print(f"tracker sync: gh issue list: could not parse output: {exc}", file=sys.stderr)
        return 2

    created = 0
    closed = 0
    drift_lines: list[str] = []
    writebacks: list[tuple[str, int]] = []

    for item in items:
        iid = item.get("id")
        status = item.get("status")
        issue_no = item.get("issue")
        tier = item.get("tier")

        if status in CREATABLE_STATUSES and issue_no is None:
            title = f"{iid} {item.get('title', '')}".rstrip()
            body = f"Tracked in {ledger_path}, row {iid}."
            if args.dry_run:
                print(f"would create: {title}")
            else:
                cmd = ["issue", "create", "--title", title, "--label", proposal_label]
                if tier:
                    cmd += ["--label", f"tier:{tier}"]
                cmd += ["--body", body, *repo_args]
                try:
                    out = run_gh(cmd)
                except (subprocess.CalledProcessError, OSError) as exc:
                    print(f"tracker sync: gh issue create failed for {iid}: {exc}", file=sys.stderr)
                    return 2
                try:
                    number = _parse_issue_number(out)
                except ValueError as exc:
                    print(f"tracker sync: {iid}: {exc}", file=sys.stderr)
                    return 2
                writebacks.append((iid, number))
            created += 1
            continue

        if issue_no is None:
            continue

        found = issues_by_number.get(issue_no)
        if found is None:
            drift_lines.append(f"DRIFT {iid} #{issue_no}: no such issue with label {proposal_label}")
            continue

        state = found.get("state")
        if status in TERMINAL_STATUSES and state == "OPEN":
            if args.dry_run:
                print(f"would close: #{issue_no} ({iid})")
            else:
                evidence = _last_evidence(item)
                comment = f"Closed by tracker sync: {iid} is {status} in {ledger_path}."
                if evidence:
                    comment += f" {evidence}"
                try:
                    run_gh(["issue", "close", str(issue_no), "--comment", comment, *repo_args])
                except (subprocess.CalledProcessError, OSError) as exc:
                    print(f"tracker sync: gh issue close failed for {iid}: {exc}", file=sys.stderr)
                    return 2
            closed += 1
        elif state == "CLOSED" and status not in TERMINAL_STATUSES:
            drift_lines.append(f"DRIFT {iid} #{issue_no}: issue closed, ledger says {status}")

    for line in drift_lines:
        print(line)

    if writebacks and not args.dry_run:
        new_text = raw_text
        for iid, number in writebacks:
            new_text, error = _apply_writeback(new_text, iid, number)
            if error:
                print(f"could not record issue #{number} for {iid}: {error}", file=sys.stderr)
                return 1
        Path(ledger_path).write_text(new_text)

    print(f"sync {ledger_path}: created {created} · closed {closed} · drift {len(drift_lines)}")

    return 1 if drift_lines else 0
