"""Build one read-only joined tracker from independently committed repositories."""
from __future__ import annotations
import argparse, html, json
from pathlib import Path, PurePosixPath


def _read(path: Path):
    data = json.loads(path.read_text())
    if not isinstance(data, dict): raise ValueError(f"{path}: must be a JSON object")
    return data


def _local_path(hub: Path, rel: str) -> Path:
    p = PurePosixPath(rel)
    if p.is_absolute() or ".." in p.parts: raise ValueError(f"unsafe local checkout path: {rel}")
    target = (hub / rel).resolve()
    if not target.is_relative_to(hub.resolve()): raise ValueError(f"local checkout escapes workspace: {rel}")
    return target


def build(hub: Path, *, check=False) -> tuple[int, str]:
    try:
        workspace = _read(hub / "docs/common-rules/workspace.json")
        local = _read(hub / ".common-rules/workspace.local.json")
        if workspace.get("workspace_id") != local.get("workspace_id"): raise ValueError("workspace IDs disagree")
        rows = []
        for member in workspace.get("members", []):
            rid = member["repository_id"]
            checkout = _local_path(hub, local.get("checkouts", {}).get(rid, ""))
            tracker = member.get("tracker", "docs/proposals")
            for path in sorted((checkout / tracker).glob("*.json")):
                data = _read(path)
                for item in data.get("items", []):
                    if not isinstance(item, dict): continue
                    rows.append((rid, member.get("role", ""), member.get("revision", ""),
                                 item.get("id", ""), item.get("title", ""), item.get("status", "")))
        body = "".join("<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in row) + "</tr>" for row in rows)
        page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__NAME__ tracker</title><style>body{font:16px system-ui;margin:0;background:#f3f5f7;color:#17202a}main{max-width:1100px;margin:auto;padding:24px}table{width:100%;border-collapse:collapse;background:white}th,td{padding:12px;text-align:left;border-bottom:1px solid #ddd}@media(max-width:700px){thead{display:none}tr{display:block;margin:12px 0;background:white}td{display:flex;overflow-wrap:anywhere}td:before{font-weight:700;width:42%}td:nth-child(1):before{content:"Repository"}td:nth-child(2):before{content:"Role"}td:nth-child(3):before{content:"Revision"}td:nth-child(4):before{content:"Item"}td:nth-child(5):before{content:"Feature"}td:nth-child(6):before{content:"Stage"}}</style></head><body><main><h1>__NAME__</h1><p>Independent commits · one compatible revision set</p><table><thead><tr><th>Repository</th><th>Role</th><th>Revision</th><th>Item</th><th>Feature</th><th>Stage</th></tr></thead><tbody>__ROWS__</tbody></table></main></body></html>'''
        page = page.replace("__NAME__", html.escape(workspace["workspace_id"])).replace("__ROWS__", body)
        out = hub / "docs/common-rules/tracker.html"
        if check:
            return (0 if out.exists() and out.read_text() == page else 1), ("current" if out.exists() and out.read_text() == page else "stale")
        out.parent.mkdir(parents=True, exist_ok=True); out.write_text(page)
        return 0, f"wrote {out} with {len(rows)} feature row(s)"
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return 2, f"refused -- {exc}"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="workspace-tracker"); ap.add_argument("--project", default="."); ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv); code, message = build(Path(args.project).resolve(), check=args.check); print(f"workspace-tracker: {message}"); return code
