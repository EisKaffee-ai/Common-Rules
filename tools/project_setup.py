"""Calibrated, opt-in Common Rules project setup (proposal 36)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath

from tools import project as declaration

ROLES = ("business-logic", "interface", "documentation", "assets", "operations", "combined")
ISSUES = ("off", "manual", "one-way")
ISSUE_GRANULARITY = ("proposal",)
ISSUE_SYNC_DIRECTIONS = ("ledger-to-github",)
WORKSPACE_ROLES = ("hub", "member")
LOCAL = ".common-rules/workspace.local.json"
DISCOVERY_EXCLUDES = frozenset({".git", ".common-rules", "build", "dist", "node_modules", "releases", "tracker"})


def _safe_id(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", value or ""):
        raise ValueError("IDs use lowercase letters, numbers, dot, underscore or hyphen")
    return value


def _inside(root: Path, rel: str) -> bool:
    p = PurePosixPath(rel)
    try:
        return bool(rel) and not p.is_absolute() and ".." not in p.parts and (root / rel).resolve().is_relative_to(root.resolve())
    except (OSError, ValueError, RuntimeError):
        return False


def _ledger_catalogues(root: Path) -> list[tuple[int, str]]:
    """Return source ledger directories, with the largest catalogue first."""
    counts: dict[Path, int] = {}
    for path in root.rglob("*.json"):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if any(part in DISCOVERY_EXCLUDES or part.startswith(".") for part in rel.parts[:-1]):
            continue
        try:
            data = json.loads(path.read_text())
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if (isinstance(data, dict) and isinstance(data.get("items"), list)
                and isinstance(data.get("title"), str) and "proposal" in data):
            counts[path.parent] = counts.get(path.parent, 0) + 1
    return sorted(((count, directory.relative_to(root).as_posix())
                   for directory, count in counts.items()),
                  key=lambda row: (-row[0], row[1]))


def discover(root: Path) -> dict:
    requirements = [p for p in ("docs/requirements", "requirements") if (root / p).is_dir()]
    trackers = [p for p in ("docs/proposals", "docs/tracker", "tracker") if (root / p).is_dir()]
    catalogues = _ledger_catalogues(root)
    return {"project_state": "existing" if any(root.iterdir()) else "new",
            "requirements": requirements or ["docs/requirements"],
            "tracker": catalogues[0][1] if catalogues else (trackers or ["docs/proposals"])[0],
            "ledger_count": catalogues[0][0] if catalogues else 0}


def _existing(root: Path) -> dict:
    path = root / ".common-rules.json"
    if not path.exists(): return {}
    data = json.loads(path.read_text())
    if not isinstance(data, dict): raise ValueError(".common-rules.json must be a JSON object")
    return data


def proposed(root: Path, args) -> dict:
    data = _existing(root)
    found = discover(root)
    integration = dict(data.get("integration") or {})
    integration.update({
        "repository_id": _safe_id(args.repository_id or integration.get("repository_id") or root.name.lower()),
        "role": args.role or integration.get("role") or "combined",
        "requirements": args.requirements or integration.get("requirements") or found["requirements"],
        "tracker": args.tracker or integration.get("tracker") or found["tracker"],
        "issue_linking": args.issue_linking or integration.get("issue_linking") or "off",
        "skill_receipts": True,
    })
    for key in ("issue_repository", "issue_granularity", "issue_sync_direction", "issue_series"):
        value = getattr(args, key, None)
        if value is not None:
            integration[key] = value
    if args.workspace_id:
        integration["workspace"] = {"id": _safe_id(args.workspace_id),
                                    "role": args.workspace_role or "member"}
        if args.hub_repository_id:
            integration["workspace"]["hub"] = _safe_id(args.hub_repository_id)
    problems = declaration._integration_problems(integration)
    if problems:
        raise ValueError("; ".join(problems))
    data["integration"] = integration
    return data


def _checkout_pairs(values: list[str]) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for raw in values:
        repository_id, sep, location = raw.partition("=")
        if not sep or not location.strip():
            raise ValueError(f"--checkout {raw!r} must be REPOSITORY_ID=PATH")
        pairs[_safe_id(repository_id)] = location.strip()
    return pairs


def _write(root: Path, data: dict, checkouts: dict[str, str] | None = None) -> None:
    (root / ".common-rules.json").write_text(json.dumps(data, indent=2) + "\n")
    ws = data["integration"].get("workspace")
    if not ws: return
    local_path = root / LOCAL
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_checkouts = {data["integration"]["repository_id"]: "."}
    local_checkouts.update(checkouts or {})
    local_path.write_text(json.dumps({"workspace_id": ws["id"], "checkouts": local_checkouts}, indent=2) + "\n")
    ignore = root / ".gitignore"
    text = ignore.read_text() if ignore.exists() else ""
    if LOCAL not in text.splitlines():
        ignore.write_text(text + ("" if not text or text.endswith("\n") else "\n") + LOCAL + "\n")
    if ws["role"] == "hub":
        path = root / "docs/common-rules/workspace.json"; path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            rid = data["integration"]["repository_id"]
            path.write_text(json.dumps({"schema": 1, "workspace_id": ws["id"], "hub_repository_id": rid,
                "members": [{"repository_id": rid, "role": data["integration"]["role"],
                             "remote": None, "manifest": ".common-rules.json", "revision": "WORKING"}]}, indent=2) + "\n")


def doctor(root: Path) -> int:
    problems = list(declaration.problems(root))
    try: data = _existing(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"✗ {exc}"); return 1
    integration = data.get("integration")
    if not isinstance(integration, dict): problems.append("integration declaration is missing")
    else:
        for rel in integration.get("requirements", []):
            if not _inside(root, rel) or not (root / rel).exists(): problems.append(f"requirements path does not exist: {rel}")
        rel = integration.get("tracker", "")
        if not _inside(root, rel) or not (root / rel).exists(): problems.append(f"tracker path does not exist: {rel}")
        if integration.get("role") not in ROLES: problems.append("role is not recognized")
        if integration.get("issue_linking") not in ISSUES: problems.append("issue_linking is not off, manual or one-way")
    problems = list(dict.fromkeys(problems))
    for p in problems: print(f"✗ {p}")
    if not problems: print("✓ Common Rules calibration is healthy")
    return 1 if problems else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="project-setup")
    ap.add_argument("--project", default=".")
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("preview", "apply"):
        p = sub.add_parser(name)
        p.add_argument("--repository-id"); p.add_argument("--role", choices=ROLES)
        p.add_argument("--requirements", action="append"); p.add_argument("--tracker")
        p.add_argument("--issue-linking", choices=ISSUES)
        p.add_argument("--issue-repository")
        p.add_argument("--issue-granularity", choices=ISSUE_GRANULARITY)
        p.add_argument("--issue-sync-direction", choices=ISSUE_SYNC_DIRECTIONS)
        p.add_argument("--issue-series")
        p.add_argument("--workspace-id"); p.add_argument("--workspace-role", choices=WORKSPACE_ROLES)
        p.add_argument("--hub-repository-id")
        p.add_argument("--checkout", action="append", default=[], metavar="REPOSITORY_ID=PATH")
    sub.add_parser("doctor")
    args = ap.parse_args(argv); root = Path(args.project).resolve()
    if args.command == "doctor": return doctor(root)
    try:
        data = proposed(root, args)
        checkouts = _checkout_pairs(args.checkout)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"project-setup: refused -- {exc}"); return 2
    if args.command == "apply":
        try: _write(root, data, checkouts)
        except ValueError as exc:
            print(f"project-setup: refused -- {exc}"); return 2
    print(json.dumps(data, indent=2))
    return 0
