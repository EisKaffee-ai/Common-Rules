"""Revision/configuration-bound receipts for the three verification levels."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path

from tools import project as P

LEVELS = ("development", "checkpoint", "release")


def _git(project: Path, *args: str, text: bool = True):
    return subprocess.run(["git", "-C", str(project), *args], capture_output=True,
                          text=text, check=False)


def command_for(project: Path, level: str) -> str:
    return P.quick_command(project) if level == "development" else P.test_command(project)


def fingerprint(project: Path) -> str:
    """Bind a receipt to HEAD and every tracked or untracked worktree byte."""
    digest = hashlib.sha256()
    head = _git(project, "rev-parse", "HEAD").stdout.strip()
    digest.update(head.encode("utf-8", "surrogatepass"))
    diff = _git(project, "diff", "--binary", "HEAD", "--", text=False)
    digest.update(diff.stdout)
    untracked = _git(project, "ls-files", "-o", "--exclude-standard", "-z", text=False).stdout
    digest.update(untracked)
    for raw in sorted(p for p in untracked.split(b"\0") if p):
        rel = os.fsdecode(raw)
        path = project / rel
        digest.update(raw)
        try:
            if path.is_symlink():
                digest.update(os.readlink(path).encode("utf-8", "surrogatepass"))
            elif path.is_file():
                digest.update(path.read_bytes())
        except OSError as exc:
            digest.update(type(exc).__name__.encode())
    return digest.hexdigest()


def receipt_path(project: Path) -> Path:
    result = _git(project, "rev-parse", "--git-path", "common-rules-gate-receipts.json")
    value = result.stdout.strip()
    path = Path(value) if value else project / ".git" / "common-rules-gate-receipts.json"
    return path if path.is_absolute() else project / path


def _load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {"schema": 1, "receipts": {}}
    if not isinstance(data, dict) or not isinstance(data.get("receipts"), dict):
        return {"schema": 1, "receipts": {}}
    return data


def _key(level: str, command: str) -> str:
    material = f"{level}\0{command}".encode("utf-8", "surrogatepass")
    return hashlib.sha256(material).hexdigest()


def reusable(project: Path, level: str, command: str, worktree: str) -> dict | None:
    receipt = _load(receipt_path(project))["receipts"].get(_key(level, command))
    if not isinstance(receipt, dict):
        return None
    if (receipt.get("level") != level or receipt.get("command") != command
            or receipt.get("worktree") != worktree or receipt.get("status") != "green"):
        return None
    return receipt


def record(project: Path, level: str, command: str, worktree: str) -> dict:
    path = receipt_path(project)
    data = _load(path)
    receipt = {
        "level": level,
        "command": command,
        "worktree": worktree,
        "head": _git(project, "rev-parse", "HEAD").stdout.strip(),
        "status": "green",
        "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    data["receipts"][_key(level, command)] = receipt
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return receipt
