"""Deterministic requirement-to-code traceability gate (proposal 36)."""
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path, PurePosixPath
from tools.tracker import ledger as L


def _path(text: str) -> str:
    return text.split("#", 1)[0]


def _safe(root: Path, rel: str) -> bool:
    p = PurePosixPath(rel)
    try: return bool(rel) and not p.is_absolute() and ".." not in p.parts and (root / rel).resolve().is_relative_to(root.resolve())
    except (OSError, ValueError, RuntimeError): return False


def _workspace_checkouts(root: Path) -> dict[str, Path]:
    path = root / ".common-rules/workspace.local.json"
    if not path.is_file(): return {}
    try: data = json.loads(path.read_text())
    except (OSError, ValueError): return {}
    values = data.get("checkouts") if isinstance(data, dict) else None
    if not isinstance(values, dict): return {}
    found = {}
    for repository_id, location in values.items():
        if not isinstance(repository_id, str) or not isinstance(location, str) or not location:
            continue
        raw = Path(location).expanduser()
        target = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
        if raw.is_absolute() or target.is_relative_to(root.resolve()):
            found[repository_id] = target
    return found


def _workspace_revisions(root: Path) -> dict[str, str]:
    path = root / "docs/common-rules/workspace.json"
    if not path.is_file(): return {}
    try: data = json.loads(path.read_text())
    except (OSError, ValueError): return {}
    members = data.get("members") if isinstance(data, dict) else None
    if not isinstance(members, list): return {}
    return {row["repository_id"]: row["revision"] for row in members
            if isinstance(row, dict) and isinstance(row.get("repository_id"), str)
            and isinstance(row.get("revision"), str) and row.get("revision")}


def _resolve_reference(root: Path, value: str, checkouts: dict[str, Path]) -> tuple[Path | None, str | None]:
    repository_id, sep, relative = value.partition(":")
    if sep:
        if repository_id not in checkouts:
            return None, f"repository checkout is not mapped for {value}"
        checkout = checkouts[repository_id]
        if not _safe(checkout, relative): return None, f"unsafe path {value}"
        return (checkout / relative).resolve(), None
    if not _safe(root, value): return None, f"unsafe path {value}"
    return (root / value).resolve(), None


def _changed(root: Path, base: str | None) -> tuple[set[str], str | None]:
    if not base: return set(), None
    run = subprocess.run(["git", "diff", "--name-only", base, "--"], cwd=root,
                         text=True, capture_output=True)
    if run.returncode: return set(), run.stderr.strip() or f"git diff {base} failed"
    return {line.strip() for line in run.stdout.splitlines() if line.strip()}, None


def _workspace_changed(root: Path, checkouts: dict[str, Path], hub_repository_id: str) -> tuple[set[str], str | None]:
    changed: set[str] = set()
    revisions = _workspace_revisions(root)
    for repository_id, checkout in checkouts.items():
        revision = revisions.get(repository_id)
        if not revision:
            continue
        base = "HEAD" if revision == "WORKING" else revision
        paths, why = _changed(checkout, base)
        if why:
            return set(), f"workspace member {repository_id}: {why}"
        changed.update(f"{repository_id}:{path}" for path in paths)
        if repository_id == hub_repository_id:
            changed.update(paths)
    return changed, None


def check(root: Path, *, base: str | None = None) -> tuple[int, list[str]]:
    findings, count = [], 0
    changed, why = _changed(root, base)
    if why: return 2, [why]
    try: declaration = json.loads((root / ".common-rules.json").read_text())
    except (OSError, ValueError) as exc: return 2, [f"cannot read .common-rules.json: {exc}"]
    integration = declaration.get("integration") if isinstance(declaration, dict) else None
    if not isinstance(integration, dict): return 1, ["integration declaration is missing"]
    tracker = integration.get("tracker")
    if not isinstance(tracker, str) or not _safe(root, tracker): return 1, ["integration.tracker is unsafe or missing"]
    checkouts = _workspace_checkouts(root)
    workspace_changed, why = _workspace_changed(
        root, checkouts, str(integration.get("repository_id") or "")
    )
    if why: return 2, [why]
    changed.update(workspace_changed)
    for path in sorted((root / tracker).glob("*.json")):
        try: data = L.load(path)
        except (OSError, ValueError) as exc: findings.append(str(exc)); continue
        # Proposed work is not yet a project contract. Its links may point at
        # artifacts the proposal itself is asking permission to create.
        if data.get("status") == "proposed":
            continue
        problems = L.validate(data)
        if problems: findings.extend(f"{path.relative_to(root)}: {p}" for p in problems); continue
        for row in L.traceability(data):
            count += 1
            document_values = [_path(row["guide_section"]), _path(row["architecture_section"])]
            for value in document_values:
                target, problem = _resolve_reference(root, value, checkouts)
                if problem: findings.append(f"{row['id']}: {problem}")
                elif target is not None and not target.is_file(): findings.append(f"{row['id']}: {value} does not exist")
            for value in row["implementation_files"]:
                target, problem = _resolve_reference(root, value, checkouts)
                if problem: findings.append(f"{row['id']}: {problem}")
                elif target is not None and not target.exists(): findings.append(f"{row['id']}: {value} does not exist")
            receipt = row["receipt_or_refusal"].strip().lower()
            if receipt.startswith("no-change:") and row.get("owner") not in ("lead", "sponsor"):
                findings.append(f"{row['id']}: no-change receipt requires owner lead or sponsor")
            touched = changed.intersection(row["implementation_files"])
            if touched:
                evidence_changed = str(path.relative_to(root)) in changed or _path(row["guide_section"]) in changed
                reviewed_no_change = receipt.startswith("no-change:") and row.get("owner") in ("lead", "sponsor")
                if not evidence_changed and not reviewed_no_change:
                    findings.append(f"{row['id']}: {', '.join(sorted(touched))} changed without requirement, "
                                    "ledger, or reviewed no-change evidence")
    if not count: findings.append("no traceability rows found")
    return (1 if findings else 0), findings or [f"{count} traceability row{'s' if count != 1 else ''} verified"]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tracecheck"); ap.add_argument("--project", default="."); ap.add_argument("--base")
    args = ap.parse_args(argv); code, lines = check(Path(args.project).resolve(), base=args.base)
    for line in lines: print(("✗ " if code else "✓ ") + line)
    return code
