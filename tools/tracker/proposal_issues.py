"""Deterministic proposal-level issue plans; remote mutation stays in the GitHub plugin."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from tools import project as declaration
from tools.tracker import ledger

TERMINAL = frozenset(("done", "deferred"))


def _ordered(values) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if value not in (None, "")))


def _revision(root: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else "UNVERSIONED"


def _issue_value(value, repository: str) -> tuple[int, str | None] | None:
    if value is None:
        return None
    if isinstance(value, int) and value > 0:
        return value, None
    if isinstance(value, dict):
        number = value.get("number")
        mapped_repo = value.get("repository", repository)
        if mapped_repo != repository:
            raise ValueError(f"issue mapping names {mapped_repo}, expected {repository}")
        if isinstance(number, int) and number > 0:
            url = value.get("url")
            return number, url if isinstance(url, str) else None
    raise ValueError("issue mappings must be a positive number or an issue identity object")


def _group_issue(data: dict, repository: str) -> dict | None:
    found: list[tuple[int, str | None]] = []
    for value in [data.get("issue"),
                  *(feature.get("issue") for feature in data.get("features", []) if isinstance(feature, dict)),
                  *(item.get("issue") for item in data.get("items", []) if isinstance(item, dict))]:
        parsed = _issue_value(value, repository) if value is not None else None
        if parsed:
            found.append(parsed)
    numbers = {number for number, _url in found}
    if len(numbers) > 1:
        raise ValueError(f"proposal {data.get('proposal')} has conflicting issue mappings: {sorted(numbers)}")
    if not found:
        return None
    number = found[0][0]
    url = next((url for mapped, url in found if mapped == number and url), None)
    return {"repository": repository, "number": number,
            "url": url or f"https://github.com/{repository}/issues/{number}"}


def _workspace_owners(root: Path, integration: dict) -> list[dict]:
    path = root / "docs/common-rules/workspace.json"
    if path.is_file():
        try:
            data = json.loads(path.read_text())
            members = data.get("members")
            if isinstance(members, list):
                return [{"repository_id": row.get("repository_id"), "role": row.get("role"),
                         "revision": row.get("revision")}
                        for row in members if isinstance(row, dict) and row.get("repository_id")]
        except (OSError, UnicodeError, json.JSONDecodeError):
            pass
    return [{"repository_id": integration["repository_id"], "role": integration["role"],
             "revision": _revision(root)}]


def _feature_name(feature: dict) -> str:
    return str(feature.get("key") or feature.get("id") or feature.get("name") or "Scope definition")


def _reason(item: dict) -> str:
    reason = item.get("deferred_reason")
    return reason.strip() if isinstance(reason, str) and reason.strip() else ""


def _evidence(item: dict) -> list[str]:
    return [str(row.get("evidence")) for row in item.get("log", [])
            if isinstance(row, dict) and row.get("evidence")]


def _checkbox(item: dict) -> tuple[str, bool]:
    status = item.get("status", "unknown")
    reason = _reason(item)
    checked = status == "done" or (status == "deferred" and bool(reason))
    detail = status
    if status == "deferred":
        detail += f" — {reason}" if reason else " — reason missing"
    return f"- [{'x' if checked else ' '}] `{item.get('id')}` — {item.get('title', '')} · {detail}", checked


def _body(root: Path, ledger_path: Path, data: dict, integration: dict, issue: dict | None,
          owners: list[dict], revision: str) -> tuple[str, list[dict], str]:
    items = data.get("items", [])
    features = [feature for feature in data.get("features", []) if isinstance(feature, dict)]
    by_key = {_feature_name(feature): feature for feature in features}
    grouped: dict[str, list[dict]] = {key: [] for key in by_key}
    for row in items:
        key = row.get("feature") or "Scope definition"
        grouped.setdefault(str(key), []).append(row)

    tracker_rel = integration["tracker"].rstrip("/") + "/tracker/index.html"
    ledger_rel = ledger_path.relative_to(root).as_posix()
    lines = [
        f"# {data.get('title')}", "",
        f"- Architecture group: **{data.get('proposal')}**",
        f"- Namespace: `{data.get('namespace', 'not declared')}`",
        f"- Layer: **{str(data.get('title', '')).split(' · ', 1)[0]}**",
        f"- Canonical tracker: [`{tracker_rel}`]({tracker_rel})",
        f"- Architecture source: [`{ledger_rel}`]({ledger_rel})",
        f"- Source revision: `{revision}`", "", "## Repository ownership", "",
    ]
    for owner in owners:
        lines.append(f"- **{owner.get('repository_id')}** — {owner.get('role')} · `{owner.get('revision') or 'unresolved'}`")
    lines += ["", "## Delivery checklist", ""]
    mappings = []
    checked_count = 0
    for key, rows in grouped.items():
        feature = by_key.get(key, {})
        lines += [f"### {key}", ""]
        if feature.get("name"):
            lines += [str(feature["name"]), ""]
        for row in rows:
            line, checked = _checkbox(row)
            lines.append(line)
            checked_count += int(checked)
            mappings.append({"item_id": row.get("id"), "feature": None if key == "Scope definition" else key})
        lines.append("")

    evidence = sorted({entry for row in items for entry in _evidence(row)})
    gaps = [str(feature.get("gap")) for feature in features if feature.get("gap")]
    dependencies = sorted({str(dep) for row in items for dep in row.get("depends", [])})
    next_row = next((row for row in items if row.get("status") not in TERMINAL
                     or (row.get("status") == "deferred" and not _reason(row))), None)
    lines += ["## Evidence, gaps and next action", "",
              "**Evidence**", *(f"- {entry}" for entry in evidence or ["No completion evidence attached."]), "",
              "**Gaps**", *(f"- {entry}" for entry in gaps or ["No explicit gap recorded."]), "",
              "**Dependencies**", *(f"- `{entry}`" for entry in dependencies or ["None recorded."]), "",
              f"**Next action:** {next_row.get('title') if next_row else 'Attach final completion evidence and close.'}", ""]

    implementations = []
    tests = []
    for feature in features:
        for ref in feature.get("affectedCode", []):
            if isinstance(ref, dict) and ref.get("path"):
                implementations.append(f"{ref.get('repository', 'repository')}@{ref.get('revision', 'unversioned')}:{ref['path']}")
        tests.extend(str(test) for test in feature.get("tests", []) if test)
    lines += ["## Implementation, tests and related issues", "",
              *(f"- Implementation: `{entry}`" for entry in sorted(set(implementations)) or ["No implementation link recorded."]),
              *(f"- Test: `{entry}`" for entry in sorted(set(tests)) or ["No test link recorded."])]
    related_values = []
    for feature in features:
        refs = feature.get("relatedIssues") or []
        related_values.extend([refs] if isinstance(refs, str) else refs if isinstance(refs, list) else [])
    related = _ordered(related_values)
    lines.extend(f"- Related issue: {ref}" for ref in related)
    lines += ["", "> The canonical ledger is authoritative. GitHub checkbox edits do not update it; reconcile drift with evidence through Common Rules.", ""]

    all_terminal = bool(items) and all(row.get("status") in TERMINAL and
                                       (row.get("status") != "deferred" or _reason(row)) for row in items)
    evidence_complete = all(bool(_evidence(row)) for row in items) if items else False
    desired_state = "closed" if all_terminal and evidence_complete else "open"
    return "\n".join(lines), mappings, desired_state


def build_plan(project: Path | str) -> dict:
    root = Path(project).resolve()
    integration = declaration.load(root).get("integration")
    if not isinstance(integration, dict):
        raise ValueError("project has no valid integration declaration")
    if (integration.get("issue_linking"), integration.get("issue_granularity"),
            integration.get("issue_sync_direction")) != ("one-way", "proposal", "ledger-to-github"):
        raise ValueError("project has not opted into one-way proposal issue synchronization")
    repository = integration["issue_repository"]
    tracker = (root / integration["tracker"]).resolve()
    if not tracker.is_relative_to(root) or not tracker.is_dir():
        raise ValueError("configured tracker is not a directory inside the project")
    paths = sorted(path for path in tracker.glob("*.json") if path.is_file())
    if not paths:
        raise ValueError("configured tracker contains no proposal ledgers")

    records = []
    seen_proposals = set()
    revision = _revision(root)
    owners = _workspace_owners(root, integration)
    for path in paths:
        data = ledger.load(path)
        problems = ledger.validate(data)
        if problems:
            raise ValueError(f"{path}: {len(problems)} ledger problem(s): {'; '.join(problems)}")
        number = data["proposal"]
        if number in seen_proposals:
            raise ValueError(f"duplicate proposal number {number}")
        seen_proposals.add(number)
        issue = _group_issue(data, repository)
        records.append((path, data, issue))

    issue_owners: dict[int, int] = {}
    for _path, data, issue in records:
        if not issue:
            continue
        prior = issue_owners.get(issue["number"])
        if prior is not None:
            raise ValueError(f"issue #{issue['number']} maps to proposals {prior} and {data['proposal']}")
        issue_owners[issue["number"]] = data["proposal"]

    total = max(data["proposal"] for _path, data, _issue in records)
    groups = []
    item_total = 0
    feature_total = 0
    for path, data, issue in sorted(records, key=lambda row: row[1]["proposal"]):
        body, mappings, desired_state = _body(root, path, data, integration, issue, owners, revision)
        item_total += len(mappings)
        feature_total += len(data.get("features", []))
        groups.append({
            "proposal": data["proposal"], "namespace": data.get("namespace"),
            "layer": str(data["title"]).split(" · ", 1)[0],
            "title": f"[Architecture {data['proposal']:02d}/{total:02d}] {data['title']}",
            "ledger": path.relative_to(root).as_posix(), "issue": issue,
            "desired_state": desired_state, "body": body, "mappings": mappings,
        })
    plan = {
        "schema": 1, "repository": repository, "direction": "ledger-to-github",
        "granularity": "proposal", "tracker": integration["tracker"],
        "tracker_page": integration["tracker"].rstrip("/") + "/tracker/index.html",
        "source_revision": revision, "groups": groups,
        "preflight": {"groups": len(groups), "features": feature_total,
                      "items": item_total, "checkboxes": item_total},
    }
    canonical = json.dumps(plan, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    plan["digest"] = hashlib.sha256(canonical).hexdigest()
    return plan


def record_mapping(project: Path | str, ledger_path: Path | str, number: int, url: str) -> None:
    root = Path(project).resolve()
    integration = declaration.load(root).get("integration") or {}
    repository = integration.get("issue_repository")
    tracker = (root / integration.get("tracker", "")).resolve()
    path = Path(ledger_path)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not path.is_relative_to(tracker) or path.parent != tracker:
        raise ValueError("mapping target must be a ledger in the configured tracker directory")
    if not isinstance(number, int) or number < 1:
        raise ValueError("issue number must be positive")
    expected_url = f"https://github.com/{repository}/issues/{number}"
    if url != expected_url:
        raise ValueError(f"issue URL must be {expected_url}")
    data = ledger.load(path)
    existing = _group_issue(data, repository)
    if existing and existing["number"] != number:
        raise ValueError(f"proposal already maps to issue #{existing['number']}")
    identity = {"repository": repository, "number": number, "url": url}
    data["issue"] = identity
    for feature in data.get("features", []):
        if isinstance(feature, dict):
            feature["issue"] = identity
    for row in data.get("items", []):
        row["issue"] = number
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def reconcile(plan: dict, remote: list[dict]) -> list[str]:
    by_number = {row.get("number"): row for row in remote if isinstance(row, dict)}
    drift = []
    for group in plan.get("groups", []):
        issue = group.get("issue")
        if not issue:
            drift.append(f"PENDING proposal {group.get('proposal')}: issue must be created")
            continue
        number = issue["number"]
        found = by_number.get(number)
        if not found:
            drift.append(f"DRIFT proposal {group.get('proposal')} #{number}: mapped issue is missing")
            continue
        if found.get("title") != group.get("title"):
            drift.append(f"DRIFT proposal {group.get('proposal')} #{number}: title differs")
        if found.get("body") != group.get("body"):
            drift.append(f"DRIFT proposal {group.get('proposal')} #{number}: body differs; ledger remains authoritative")
        if str(found.get("state", "")).lower() != group.get("desired_state"):
            drift.append(f"DRIFT proposal {group.get('proposal')} #{number}: state differs")
    return drift


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="tracker sync")
    parser.add_argument("--project", required=True)
    parser.add_argument("--output")
    parser.add_argument("--reconcile")
    parser.add_argument("--record")
    parser.add_argument("--issue-number", type=int)
    parser.add_argument("--issue-url")
    args = parser.parse_args(argv)
    try:
        if args.record:
            if args.issue_number is None or not args.issue_url:
                raise ValueError("--record requires --issue-number and --issue-url")
            record_mapping(args.project, args.record, args.issue_number, args.issue_url)
            print(f"recorded issue #{args.issue_number} for {args.record}")
            return 0
        plan = build_plan(args.project)
        if args.reconcile:
            remote = json.loads(Path(args.reconcile).read_text())
            if not isinstance(remote, list):
                raise ValueError("reconciliation input must be a JSON list of issues")
            drift = reconcile(plan, remote)
            for line in drift:
                print(line)
            return 1 if drift else 0
        rendered = json.dumps(plan, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            Path(args.output).write_text(rendered)
        else:
            print(rendered, end="")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"tracker sync: refused -- {exc}", file=sys.stderr)
        return 2
