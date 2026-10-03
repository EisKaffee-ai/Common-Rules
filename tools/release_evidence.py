"""Refresh release measurements from a machine-verifiable full-gate receipt."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
from pathlib import Path

from tools.tracker import board, ledger as L, render as R

RUN = re.compile(r"^Ran (?P<count>\d+) tests in (?P<seconds>\d+(?:\.\d+)?)s$", re.MULTILINE)
SENTENCE = re.compile(
    r"final (?:release )?gate (completed|passed) all\s+[\d,]+ tests in\s+\d+(?:\.\d+)?\s+seconds"
)
EVIDENCE = re.compile(r"final [\d,]+-test evidence")


def measurement(receipt: Path) -> tuple[int, float, dict]:
    data = json.loads(receipt.read_text())
    command = data.get("command") if isinstance(data, dict) else None
    expected = ["-m", "unittest", "discover", "-s", "tests", "-q"]
    if (data.get("kind") != "common-rules-quiet-gate" or data.get("label") != "merge-gate"
            or data.get("status") != "OK" or not isinstance(command, list)
            or command[1:] != expected):
        raise ValueError("receipt is not a successful full merge-gate unittest discovery")
    log = Path(data.get("log", ""))
    text = log.read_text()
    if hashlib.sha256(text.encode()).hexdigest() != data.get("log_sha256"):
        raise ValueError("receipt log digest does not match")
    matches = list(RUN.finditer(text))
    if not matches or not re.search(r"^OK\s*$", text[matches[-1].end():], re.MULTILINE):
        raise ValueError("log has no final successful aggregate unittest result")
    found = matches[-1]
    count, seconds = int(found.group("count")), float(found.group("seconds"))
    if data.get("tests") != count or data.get("test_seconds") != seconds:
        raise ValueError("receipt measurements do not match its log")
    return count, seconds, data


def updated_text(path: Path, count: int, seconds: float) -> str:
    text = path.read_text()
    replacement = f"final release gate \\1 all {count:,} tests in {seconds:.1f} seconds"
    changed, sentence_count = SENTENCE.subn(replacement, text)
    changed, evidence_count = EVIDENCE.subn(f"final {count:,}-test evidence", changed)
    if sentence_count + evidence_count == 0:
        raise ValueError(f"{path}: no release evidence marker found")
    return changed


def update(path: Path, count: int, seconds: float) -> None:
    changed = updated_text(path, count, seconds)
    if changed != path.read_text():
        path.write_text(changed)


def updated_ledger(path: Path, item_id: str, trace_id: str, count: int,
                   seconds: float, receipt: dict) -> dict:
    data = L.load(path)
    item = next((row for row in data.get("items", []) if row.get("id") == item_id), None)
    trace = next((row for row in data.get("traceability", []) if row.get("id") == trace_id), None)
    if item is None or trace is None:
        raise ValueError(f"{path}: release item or trace row is missing")
    digest = str(receipt["log_sha256"])
    item["release_gate"] = {
        "status": "OK", "tests": count, "seconds": round(seconds, 1),
        "receipt_sha256": digest,
    }
    event = {
        "at": datetime.date.today().isoformat(),
        "event": "machine release receipt refreshed",
        "by": "bin/release-evidence",
        "evidence": f"full merge gate: {count:,} tests in {seconds:.1f} seconds; receipt sha256 {digest}",
        "status": item.get("status", "in progress"),
    }
    logs = item.setdefault("log", [])
    if logs and isinstance(logs[-1], dict) and logs[-1].get("event") == event["event"]:
        logs[-1] = event
    else:
        logs.append(event)
    trace["receipt_or_refusal"] = (
        f"Machine release receipt: {count:,} full-suite tests pass in {seconds:.1f} seconds; "
        f"sha256 {digest}; independent review and CI pending"
    )
    data["updated"] = datetime.date.today().isoformat()
    problems = L.validate(data)
    if problems:
        raise ValueError(f"{path}: generated release ledger is invalid: {'; '.join(problems)}")
    return data


def _project_root(ledger: Path) -> Path:
    for parent in ledger.resolve().parents:
        if (parent / ".common-rules.json").is_file():
            return parent
    raise ValueError(f"{ledger}: cannot find project root")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="release-evidence")
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--write", action="append", type=Path, required=True)
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--item", default="T-06")
    ap.add_argument("--trace", default="TR-06")
    args = ap.parse_args(argv)
    try:
        count, seconds, receipt = measurement(args.receipt)
        rendered = [(path, updated_text(path, count, seconds)) for path in args.write]
        ledger_data = updated_ledger(args.ledger, args.item, args.trace, count, seconds, receipt)
        for path, text in rendered:
            if text != path.read_text():
                path.write_text(text)
        temporary = args.ledger.with_name(args.ledger.name + ".tmp")
        temporary.write_text(json.dumps(ledger_data, indent=2, ensure_ascii=False) + "\n")
        temporary.replace(args.ledger)
        root = _project_root(args.ledger)
        if R.main([str(args.ledger)]) != 0 or board.main(["--project", str(root)]) != 0:
            raise ValueError("generated release ledger could not be rendered")
    except (OSError, ValueError) as exc:
        print(f"release-evidence: refused -- {exc}")
        return 2
    print(f"release-evidence: {count:,} tests in {seconds:.1f} seconds -> {len(args.write)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
