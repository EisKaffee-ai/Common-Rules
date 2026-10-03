"""Deterministic, project-owned requirement and architecture traceability.

The generic engine owns validation, repository scanning, state calculation and
HTML generation. Projects own the reviewed JSON manifest and machine-local
checkout mapping. No generated value or accepted mapping comes from AI state.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import html
import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


MANIFEST = "docs/common-rules/traceability.json"
LOCAL = ".common-rules/workspace.local.json"
TEMPLATE = Path(__file__).resolve().parent.parent / "templates/traceability.html"
ID_PREFIXES = {
    "feature": "FEAT-",
    "requirement": "REQ-",
    "workflow node": "WFN-",
    "workflow edge": "WFE-",
    "code anchor": "CODE-",
    "test case": "TEST-",
    "test report": "REPORT-",
    "issue": "ISSUE-",
    "receipt": "RECEIPT-",
    "mapping": "MAP-",
}
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")


@dataclass
class Repository:
    id: str
    root: Path | None
    revision: str
    files: set[str] = field(default_factory=set)


@dataclass
class Analysis:
    manifest: dict[str, Any]
    digest: str
    repositories: dict[str, Repository]
    features: list[dict[str, Any]]
    findings: list[str]
    scanned_files: int


def _canonical(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _safe_rel(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _objects(value: Any) -> list[dict[str, Any]]:
    return [row for row in _list(value) if isinstance(row, dict)]


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, str(exc)
    if not isinstance(data, dict):
        return None, "root must be an object"
    return data, None


def _checkouts(project: Path) -> dict[str, Path]:
    path = project / LOCAL
    data, _ = _load_json(path)
    if data is None:
        return {}
    rows = data.get("checkouts")
    if not isinstance(rows, dict):
        return {}
    found: dict[str, Path] = {}
    for key, value in rows.items():
        if not isinstance(key, str) or not isinstance(value, str) or not value:
            continue
        raw = Path(value).expanduser()
        found[key] = raw.resolve() if raw.is_absolute() else (project / raw).resolve()
    return found


def _head(root: Path) -> str | None:
    run = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True
    )
    return run.stdout.strip() if run.returncode == 0 else None


def _matches(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) or PurePosixPath(path).match(pattern) for pattern in patterns)


def _scan(root: Path, include: list[str], exclude: list[str]) -> set[str]:
    files: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        if _matches(rel, include) and not _matches(rel, exclude):
            files.add(rel)
    return files


def _record_id(
    findings: list[str], seen: dict[str, str], kind: str, row: dict[str, Any]
) -> str | None:
    value = row.get("id")
    prefix = ID_PREFIXES[kind]
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        findings.append(f"{kind} id is missing or malformed")
        return None
    if not value.startswith(prefix):
        findings.append(f"{kind} id {value} must start with {prefix}")
    if value in seen:
        findings.append(f"{value}: duplicate id (already used as {seen[value]})")
    else:
        seen[value] = kind
    return value


def _refs(
    findings: list[str], row_id: str, row: dict[str, Any], field_name: str,
    valid: set[str], required: bool = True,
) -> set[str]:
    values = row.get(field_name)
    if not isinstance(values, list) or (required and not values) or any(not isinstance(v, str) for v in values):
        findings.append(f"{row_id}: {field_name} must be a{' non-empty' if required else ''} list of ids")
        return set()
    result = set(values)
    for value in sorted(result - valid):
        findings.append(f"{row_id}: unknown {field_name} reference {value}")
    return result


def _symbol_found(text: str, symbol: str) -> bool:
    escaped = re.escape(symbol)
    patterns = (
        rf"(?m)^\s*(?:async\s+)?def\s+{escaped}\b",
        rf"(?m)^\s*(?:class|struct|enum|protocol)\s+{escaped}\b",
        rf"(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+{escaped}\b",
        rf"(?m)^\s*(?:func|fn)\s+{escaped}\b",
        rf"(?m)^\s*(?:const|let|var)\s+{escaped}\s*=",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _anchor(
    findings: list[str], repositories: dict[str, Repository], row: dict[str, Any]
) -> tuple[str, str]:
    anchor_id = str(row.get("id") or "code anchor")
    repository_id = row.get("repository")
    repo = repositories.get(repository_id) if isinstance(repository_id, str) else None
    if repo is None or repo.root is None:
        findings.append(f"{anchor_id}: repository {repository_id or '<missing>'} is unavailable")
        return "broken", "unknown"
    if row.get("revision") != repo.revision:
        findings.append(f"{anchor_id}: revision does not match repository {repo.id}")
    rel = row.get("path")
    if not _safe_rel(rel):
        findings.append(f"{anchor_id}: path is missing or unsafe")
        return "broken", "unknown"
    path = (repo.root / rel).resolve()
    try:
        if not path.is_relative_to(repo.root.resolve()):
            raise ValueError("outside checkout")
    except (OSError, ValueError):
        findings.append(f"{anchor_id}: path is outside repository {repo.id}")
        return "broken", "unknown"
    if rel not in repo.files:
        findings.append(f"{anchor_id}: {repo.id}:{rel} is not in the configured repository scan")
    if not path.is_file():
        findings.append(f"{anchor_id}: {repo.id}:{rel} does not exist")
        return "broken", "unknown"
    modes = [name for name in ("symbol", "region", "whole_file") if row.get(name)]
    if len(modes) != 1:
        findings.append(f"{anchor_id}: choose exactly one of symbol, region, or whole_file")
        return "broken", "unknown"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        findings.append(f"{anchor_id}: cannot read {repo.id}:{rel}: {exc}")
        return "broken", modes[0]
    mode = modes[0]
    if mode == "symbol":
        symbol = row.get("symbol")
        if not isinstance(symbol, str) or not symbol or not _symbol_found(text, symbol):
            findings.append(f"{anchor_id}: symbol {symbol} not found in {repo.id}:{rel}")
            return "broken", "symbol"
        return "strong", "symbol"
    if mode == "region":
        region = row.get("region")
        start = region.get("start") if isinstance(region, dict) else None
        end = region.get("end") if isinstance(region, dict) else None
        if not isinstance(start, str) or not start or not isinstance(end, str) or not end:
            findings.append(f"{anchor_id}: region requires explicit START and END markers")
            return "broken", "region"
        if text.count(start) != 1 or text.count(end) != 1 or text.index(start) >= text.index(end):
            findings.append(f"{anchor_id}: explicit START/END region is missing, repeated, or reversed")
            return "broken", "region"
        return "strong", "region"
    if row.get("whole_file") is not True:
        findings.append(f"{anchor_id}: whole_file must be true")
        return "broken", "whole file"
    return "weak", "whole file"


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else None
    except ValueError:
        return None


def analyze(project: Path, manifest_path: Path | None = None) -> Analysis:
    path = manifest_path or project / MANIFEST
    manifest, problem = _load_json(path)
    if manifest is None:
        return Analysis({}, "", {}, [], [f"cannot read {path}: {problem}"], 0)
    findings: list[str] = []
    if manifest.get("schema_version") != 1:
        findings.append("schema_version must be 1")
    reviewed = manifest.get("reviewed")
    if not isinstance(reviewed, dict) or reviewed.get("status") != "accepted" or not reviewed.get("by") or not _parse_time(reviewed.get("at")):
        findings.append("manifest is not reviewed and accepted")

    checkouts = _checkouts(project)
    repositories: dict[str, Repository] = {}
    seen: dict[str, str] = {}
    for row in _objects(manifest.get("repositories")):
        repository_id = row.get("id")
        if not isinstance(repository_id, str) or not repository_id:
            findings.append("repository id is missing")
            continue
        if repository_id in repositories:
            findings.append(f"repository {repository_id} is duplicated")
            continue
        revision = row.get("revision")
        if not isinstance(revision, str) or not revision:
            findings.append(f"repository {repository_id} has no revision")
            revision = ""
        root = checkouts.get(repository_id)
        repo = Repository(repository_id, root, revision)
        repositories[repository_id] = repo
        if root is None:
            findings.append(f"repository {repository_id} has no configured checkout")
            continue
        if not root.is_dir():
            findings.append(f"repository {repository_id} checkout does not exist")
            continue
        current = _head(root)
        if revision != "WORKING" and current != revision:
            findings.append(f"repository {repository_id} checkout is at {current or 'no git revision'}, expected {revision}")
        scan = row.get("scan")
        include = scan.get("include") if isinstance(scan, dict) else None
        exclude = scan.get("exclude", []) if isinstance(scan, dict) else []
        if not isinstance(include, list) or not include or any(not isinstance(v, str) or not v for v in include):
            findings.append(f"repository {repository_id} scan.include must be a non-empty list")
            continue
        if not isinstance(exclude, list) or any(not isinstance(v, str) or not v for v in exclude):
            findings.append(f"repository {repository_id} scan.exclude must be a list")
            continue
        repo.files = _scan(root, include, exclude)

    features: list[dict[str, Any]] = []
    for source in _objects(manifest.get("features")):
        before = len(findings)
        feature_id = _record_id(findings, seen, "feature", source) or "feature"
        title = source.get("title") if isinstance(source.get("title"), str) else feature_id
        requirements = _objects(source.get("requirements"))
        workflow = source.get("workflow") if isinstance(source.get("workflow"), dict) else {}
        expected_nodes = _objects(workflow.get("expected_nodes"))
        expected_edges = _objects(workflow.get("expected_edges"))
        actual_nodes = _objects(workflow.get("actual_nodes"))
        actual_edges = _objects(workflow.get("actual_edges"))
        anchors = _objects(source.get("code_anchors"))
        test_cases = _objects(source.get("test_cases"))
        reports = _objects(source.get("test_reports"))
        issues = _objects(source.get("issues"))
        receipts = _objects(source.get("receipts"))
        mappings = _objects(source.get("mappings"))

        ids: dict[str, set[str]] = {}
        for kind, rows in (
            ("requirement", requirements), ("workflow node", expected_nodes),
            ("workflow edge", expected_edges), ("code anchor", anchors),
            ("test case", test_cases), ("test report", reports),
            ("issue", issues), ("receipt", receipts), ("mapping", mappings),
        ):
            ids[kind] = {value for row in rows if (value := _record_id(findings, seen, kind, row))}

        anchor_view = []
        for row in anchors:
            strength, mode = _anchor(findings, repositories, row)
            anchor_view.append({**row, "strength": strength, "mode": mode})

        expected_node_ids = ids["workflow node"]
        expected_edge_ids = ids["workflow edge"]
        accepted_nodes: set[str] = set()
        accepted_edges: set[str] = set()
        for kind, rows, valid, accepted in (
            ("node", actual_nodes, expected_node_ids, accepted_nodes),
            ("edge", actual_edges, expected_edge_ids, accepted_edges),
        ):
            for row in rows:
                row_id = row.get("id")
                if row_id not in valid:
                    findings.append(f"{row_id or 'actual workflow row'}: actual workflow {kind} is not expected")
                    continue
                _refs(findings, str(row_id), row, "code_anchor_ids", ids["code anchor"])
                if row.get("status") == "accepted":
                    accepted.add(str(row_id))
                elif row.get("status") == "proposed_ai":
                    findings.append(f"{row_id}: proposed AI mapping does not count as accepted evidence")
                else:
                    findings.append(f"{row_id}: actual workflow {kind} status must be accepted or proposed_ai")
        for row in expected_nodes:
            row_id = row.get("id")
            if row_id not in accepted_nodes:
                findings.append(f"{row_id}: expected workflow node has no accepted implementation")
        for row in expected_edges:
            row_id = row.get("id")
            if row.get("from") not in expected_node_ids or row.get("to") not in expected_node_ids:
                findings.append(f"{row_id}: workflow edge endpoints must name expected nodes")
            if row_id not in accepted_edges:
                findings.append(f"{row_id}: expected workflow edge has no accepted implementation")

        for row in test_cases:
            row_id = str(row.get("id") or "test case")
            _refs(findings, row_id, row, "requirement_ids", ids["requirement"])
            _refs(findings, row_id, row, "code_anchor_ids", ids["code anchor"])

        report_view = []
        for row in reports:
            row_id = str(row.get("id") or "test report")
            repo = repositories.get(row.get("repository"))
            if repo is None or repo.root is None:
                findings.append(f"{row_id}: repository {row.get('repository')} is unavailable")
            else:
                if row.get("revision") != repo.revision:
                    findings.append(f"{row_id}: revision does not match repository {repo.id}")
                rel = row.get("path")
                report_path = (repo.root / rel).resolve() if _safe_rel(rel) else None
                if report_path is not None and not report_path.is_relative_to(repo.root.resolve()):
                    findings.append(f"{row_id}: report path is outside repository {repo.id}")
                elif not _safe_rel(rel) or rel not in repo.files or report_path is None or not report_path.is_file():
                    findings.append(f"{row_id}: report path is missing from the configured repository scan")
            generated = _parse_time(row.get("generated_at"))
            if generated is None:
                findings.append(f"{row_id}: generated_at must be an ISO timestamp")
            results = _objects(row.get("results"))
            if not results:
                findings.append(f"{row_id}: results must name visible test-case evidence")
            for result in results:
                if result.get("test_case_id") not in ids["test case"]:
                    findings.append(f"{row_id}: unknown test case {result.get('test_case_id')}")
                if result.get("status") not in ("passed", "failed", "skipped"):
                    findings.append(f"{row_id}: test result status must be passed, failed, or skipped")
            report_view.append({**row, "_time": generated})

        accepted_mapping_ids: list[str] = []
        accepted_coverage = {kind: set() for kind in (
            "requirement", "workflow node", "workflow edge", "code anchor",
            "test case", "test report", "issue", "receipt",
        )}
        fields = {
            "requirement": "requirement_ids", "workflow node": "workflow_node_ids",
            "workflow edge": "workflow_edge_ids", "code anchor": "code_anchor_ids",
            "test case": "test_case_ids", "test report": "test_report_ids",
            "issue": "issue_ids", "receipt": "receipt_ids",
        }
        for row in mappings:
            row_id = str(row.get("id") or "mapping")
            status = row.get("status")
            if status == "proposed_ai":
                findings.append(f"{row_id}: proposed AI mapping does not count as accepted evidence")
            elif status != "accepted":
                findings.append(f"{row_id}: mapping status must be accepted or proposed_ai")
            for kind, field_name in fields.items():
                refs = _refs(findings, row_id, row, field_name, ids[kind])
                if status == "accepted":
                    accepted_coverage[kind].update(refs)
            if status == "accepted":
                accepted_mapping_ids.append(row_id)
        for kind in accepted_coverage:
            for missing in sorted(ids[kind] - accepted_coverage[kind]):
                findings.append(f"{missing}: {kind} has no accepted end-to-end mapping")

        latest = max(
            report_view,
            key=lambda row: row["_time"].timestamp() if row.get("_time") else float("-inf"),
            default=None,
        )
        feature_findings = findings[before:]
        features.append({
            "id": feature_id, "title": title, "requirements": requirements,
            "expected_nodes": expected_nodes, "expected_edges": expected_edges,
            "actual_nodes": actual_nodes, "actual_edges": actual_edges,
            "anchors": anchor_view, "test_cases": test_cases, "reports": report_view,
            "issues": issues, "receipts": receipts, "mappings": mappings,
            "latest_report": latest, "findings": feature_findings,
            "conformance": "conformant" if not feature_findings else "gaps",
            "accepted_mapping_ids": accepted_mapping_ids,
        })

    if not _objects(manifest.get("repositories")):
        findings.append("no repositories configured")
    if not _objects(manifest.get("features")):
        findings.append("no features configured")
    return Analysis(
        manifest, _digest(manifest), repositories, features, findings,
        sum(len(repo.files) for repo in repositories.values()),
    )


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _pills(values: Iterable[Any]) -> str:
    return "".join(f'<span class="pill">{_e(value)}</span>' for value in values)


def _feature_html(feature: dict[str, Any]) -> str:
    latest = feature.get("latest_report")
    latest_html = '<span class="muted">No test report</span>'
    if latest:
        results = latest.get("results") if isinstance(latest.get("results"), list) else []
        result_labels = (
            f"{row.get('test_case_id')}: {row.get('status')}"
            for row in results if isinstance(row, dict)
        )
        latest_html = (
            f'<strong>{_e(latest.get("id"))}</strong> · {_e(latest.get("generated_at"))}'
            f'<div><code>{_e(latest.get("repository"))}@{_e(latest.get("revision"))}:{_e(latest.get("path"))}</code></div>'
            f'<div>{_pills(result_labels)}</div>'
        )
    expected_nodes = {row.get("id"): row.get("label", row.get("id")) for row in feature["expected_nodes"]}
    flow = []
    for edge in feature["expected_edges"]:
        flow.append(
            f'<span class="pill">{_e(expected_nodes.get(edge.get("from"), edge.get("from")))}</span>'
            f'<span class="arrow">→</span><span class="pill">{_e(expected_nodes.get(edge.get("to"), edge.get("to")))}</span>'
        )
    anchor_rows = []
    for row in feature["anchors"]:
        if row.get("mode") == "symbol":
            locator = f"symbol {row.get('symbol')}"
        elif row.get("mode") == "region" and isinstance(row.get("region"), dict):
            locator = f"{row['region'].get('start')} … {row['region'].get('end')}"
        else:
            locator = "complete file"
        strength_class = "warn" if row.get("strength") == "weak" else "ok" if row.get("strength") == "strong" else "bad"
        anchor_rows.append(
            f'<tr><td><code>{_e(row.get("id"))}</code></td>'
            f'<td><code>{_e(row.get("repository"))}@{_e(row.get("revision"))}:{_e(row.get("path"))}</code></td>'
            f'<td>{_e(locator)}</td><td class="{strength_class}">{_e(row.get("mode"))} · {_e(row.get("strength"))}</td></tr>'
        )
    anchors = "".join(anchor_rows)
    actual_nodes = {row.get("id"): row for row in feature["actual_nodes"]}
    actual_edges = {row.get("id"): row for row in feature["actual_edges"]}
    workflow_rows = []
    for row, kind, actual in (
        *((row, "Node", actual_nodes.get(row.get("id"))) for row in feature["expected_nodes"]),
        *((row, "Edge", actual_edges.get(row.get("id"))) for row in feature["expected_edges"]),
    ):
        accepted = isinstance(actual, dict) and actual.get("status") == "accepted"
        evidence = actual.get("code_anchor_ids", []) if isinstance(actual, dict) else []
        workflow_rows.append(
            f'<tr><td>{_e(kind)}</td><td><code>{_e(row.get("id"))}</code></td>'
            f'<td>{_pills(evidence)}</td><td class="{("ok" if accepted else "bad")}">'
            f'{"Accepted implementation" if accepted else "Missing accepted implementation"}</td></tr>'
        )
    issue_links = "".join(
        f'<a class="pill" href="{_e(row.get("url"))}">{_e(row.get("id"))}</a>'
        for row in feature["issues"]
    )
    findings = "".join(f'<li class="finding">{_e(value)}</li>' for value in feature["findings"]) or '<li class="ok">No gaps</li>'
    return f'''<article class="feature" id="{_e(feature['id'])}">
      <h3>{_e(feature['title'])} <code>{_e(feature['id'])}</code></h3>
      <p class="{('ok' if feature['conformance'] == 'conformant' else 'bad')}"><strong>{_e(feature['conformance'])}</strong></p>
      <div class="flow">{''.join(flow) or '<span class="muted">No expected workflow edges</span>'}</div>
      <details open><summary>Expected versus actual implementation</summary><table><thead><tr><th>Type</th><th>Expected</th><th>Actual code evidence</th><th>State</th></tr></thead><tbody>{''.join(workflow_rows)}</tbody></table></details>
      <details open><summary>Requirements and accepted mappings</summary><p>{_pills(row.get('id') for row in feature['requirements'])}</p><p>{_pills(feature['accepted_mapping_ids'])}</p></details>
      <details open><summary>Code evidence</summary><table><thead><tr><th>Anchor</th><th>Repository revision and path</th><th>Locator</th><th>Evidence strength</th></tr></thead><tbody>{anchors}</tbody></table></details>
      <details open><summary>Test cases</summary><p>{_pills(row.get('id') for row in feature['test_cases'])}</p><p><strong>Latest test report:</strong> {latest_html}</p></details>
      <details><summary>Issues and receipts</summary><p>{issue_links}</p><p>{_pills(row.get('id') for row in feature['receipts'])}</p></details>
      <details {('open' if feature['findings'] else '')}><summary>Conformance findings</summary><ul>{findings}</ul></details>
    </article>'''


def render(analysis: Analysis) -> str:
    compliant = sum(feature["conformance"] == "conformant" for feature in analysis.features)
    total = len(analysis.features)
    anchors = sum(len(feature["anchors"]) for feature in analysis.features)
    strong = sum(row.get("strength") == "strong" for feature in analysis.features for row in feature["anchors"])
    reports = sum(len(feature["reports"]) for feature in analysis.features)
    body = f'''<header><h1>Overall traceability</h1><p class="lede">Reviewed, revision-bound evidence across every configured repository. Generated deterministically; AI proposals are never accepted evidence.</p></header>
    <section class="grid" aria-label="Overall dashboard">
      <div class="card"><div class="stat">{compliant}/{total}</div><div class="label">Conformant features</div></div>
      <div class="card"><div class="stat">{len(analysis.repositories)}</div><div class="label">Configured repositories</div></div>
      <div class="card"><div class="stat">{analysis.scanned_files}</div><div class="label">Files scanned</div></div>
      <div class="card"><div class="stat">{strong}/{anchors}</div><div class="label">Strong code anchors</div></div>
      <div class="card"><div class="stat">{reports}</div><div class="label">Test reports</div></div>
      <div class="card"><div class="stat">{len(analysis.findings)}</div><div class="label">Broken or missing evidence</div></div>
    </section><h2>Feature drill-down</h2>{''.join(_feature_html(feature) for feature in analysis.features)}'''
    public = {
        "digest": analysis.digest,
        "counts": {"features": total, "conformant": compliant, "repositories": len(analysis.repositories), "scanned_files": analysis.scanned_files, "findings": len(analysis.findings)},
        "features": [{"id": row["id"], "conformance": row["conformance"]} for row in analysis.features],
    }
    template = TEMPLATE.read_text(encoding="utf-8")
    return (template.replace("{{DIGEST}}", analysis.digest)
            .replace("{{TITLE}}", "Overall feature traceability")
            .replace("{{BODY}}", body)
            .replace("{{DATA}}", _canonical(public).replace("<", "\\u003c")))


def _output(project: Path, manifest: dict[str, Any]) -> tuple[Path | None, str | None]:
    rel = manifest.get("output")
    if not _safe_rel(rel):
        return None, "output path is missing or unsafe"
    path = (project / rel).resolve()
    try:
        if not path.is_relative_to(project.resolve()):
            return None, "output path is outside project"
    except (OSError, ValueError):
        return None, "output path is outside project"
    return path, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="traceability")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "check"):
        command = sub.add_parser(name)
        command.add_argument("--project", default=".")
        command.add_argument("--manifest")
    args = parser.parse_args(argv)
    project = Path(args.project).resolve()
    manifest_path = Path(args.manifest).resolve() if args.manifest else project / MANIFEST
    analysis = analyze(project, manifest_path)
    output, output_problem = _output(project, analysis.manifest)
    if output_problem:
        analysis.findings.append(output_problem)
    expected = render(analysis) if analysis.manifest else ""
    if args.command == "build":
        if analysis.findings:
            for finding in analysis.findings:
                print(f"✗ {finding}")
            return 1
        assert output is not None
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(expected, encoding="utf-8")
        print(f"✓ wrote {output.relative_to(project)} · {len(analysis.features)} feature{'s' if len(analysis.features) != 1 else ''} · {analysis.scanned_files} files scanned")
        return 0
    if output is not None:
        if not output.is_file():
            analysis.findings.append(f"generated output is missing: {output.relative_to(project)}")
        elif output.read_text(encoding="utf-8") != expected:
            analysis.findings.append(f"generated output is stale: {output.relative_to(project)}")
    if analysis.findings:
        for finding in analysis.findings:
            print(f"✗ {finding}")
        return 1
    print(f"✓ {len(analysis.features)} feature{'s' if len(analysis.features) != 1 else ''} · {len(analysis.repositories)} repositories · {analysis.scanned_files} files scanned · output current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
