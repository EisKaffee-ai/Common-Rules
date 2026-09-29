"""tracker render -- a ledger's page, generated (proposal 19, W-02).

  tracker render LEDGER.json [--out PATH] [--repo OWNER/NAME]
  tracker render LEDGER.json --check
  tracker published --project [DIR] --url URL [--by NAME]
                                         (proposal 22, T-03: the project's one page)
  tracker published LEDGER.json --url URL [--by NAME] [--page PATH]
                                         (proposal 20, V-09 and V-11; see published_main)

Writes docs/proposals/tracker/<ledger stem>.html beside the ledger. Two
reasons it is a subdirectory and not the proposal page itself:

  * the proposal page is authored prose -- decisions, reasoning, pictures --
    and a generator that owns it would erase exactly what makes it a
    proposal. The ledger page is the other half: the numbers, always current.
  * every checker that reads proposals globs docs/proposals/*.html:
    common-rules' proposalcheck (one number, one document), and the engine's
    build_proposal_index.py and check_proposals.py. A second file claiming the
    same number at that level would fail the first and pollute the other two.

The page carries a digest of the ledger's bytes, and `--check` compares that
rather than modification times: a checkout or a rebase resets mtimes, so a
timestamp test passes on a page rendered from a different ledger.

Output is deterministic -- no "generated at" clock -- so rendering an
unchanged ledger produces an unchanged file and a diff means something moved.

Exit codes: 0 rendered / fresh, 1 stale or invalid ledger, 2 unreadable.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

from tools.tracker import ledger as L

STATUS_ORDER = ("done", "in progress", "in review", "in testing", "blocked", "not started", "deferred")


def e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def slug(status: str) -> str:
    return "s-" + status.replace(" ", "-")


def digest(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def default_out(ledger_path: Path) -> Path:
    return ledger_path.parent / "tracker" / f"{ledger_path.stem}.html"


def infer_repo(ledger_path: Path) -> str | None:
    """owner/name from the ledger's own git remote, or None. Never guessed."""
    try:
        url = subprocess.run(["git", "-C", str(ledger_path.parent), "remote", "get-url", "origin"],
                             capture_output=True, text=True, check=True, timeout=5).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return None
    m = re.search(r"github\.com[:/]([^/\s]+/[^/\s]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else None


def bar(counts: dict, cls: str) -> str:
    total = sum(counts.values())
    if not total:
        return f'<div class="{cls}"><span class="seg s-empty" style="width:100%"></span></div>'
    segs = []
    for s in STATUS_ORDER:
        if counts[s]:
            segs.append(f'<span class="seg {slug(s)}" style="width:{counts[s] * 100 / total:.2f}%" '
                        f'title="{counts[s]} {e(s)}"></span>')
    return f'<div class="{cls}">{"".join(segs)}</div>'


def issue_cell(number, repo) -> str:
    if not number:
        return '<span class="dim">—</span>'
    if repo:
        return f'<a href="https://github.com/{e(repo)}/issues/{e(number)}">#{e(number)}</a>'
    return f"#{e(number)}"


def last_log(item: dict) -> str:
    """The last log entry: event and time, with its evidence on hover -- and
    in full when the item is blocked, because "blocked" without the reason
    is the one status a reader cannot act on."""
    log = item.get("log") or []
    if not log:
        return '<span class="dim">no entries</span>'
    last = log[-1]
    when = str(last.get("at", ""))[:16].replace("T", " ")
    evidence = last.get("evidence") or ""
    cell = f'<span title="{e(evidence)}">{e(last.get("event"))}</span> <span class="dim">{e(when)}</span>'
    if item.get("status") in ("blocked", "deferred") and evidence:
        why_class = "why deferred-why" if item.get("status") == "deferred" else "why"
        cell += f'<div class="{why_class}">{e(evidence)}</div>'
    return cell


def size_line(item: dict) -> str:
    """Proposal 25 and 26 sizing, one quiet line; nothing when none is set."""
    parts = []
    if item.get("value") is not None:
        parts.append(f"value {item['value']}")
    if item.get("points") is not None:
        parts.append(f"{item['points']} pts")
    if item.get("risk") is not None:
        parts.append(f"risk {item['risk']}")
    if item.get("cluster") is not None:
        parts.append(f"cluster {item['cluster']}")
    if item.get("impact") is not None:
        parts.append(f"impact {item['impact']}")
    if item.get("likelihood") is not None:
        parts.append(f"likelihood {item['likelihood']}")
    return f'<div class="dep size">{e(" · ".join(parts))}</div>' if parts else ""


def item_row(item: dict, repo, merged_waiting_ids=frozenset()) -> str:
    status = item.get("status", "")
    deps = L.as_list(item.get("depends"))
    dep = f'<div class="dep">after {e(" ".join(deps))}</div>' if deps else ""
    found = f'<div class="dep">from {e(item["discovered_from"])}</div>' if item.get("discovered_from") else ""
    owner = (f'<div class="dep">owner: {e(item.get("owner"))}</div>'
             if status == "blocked" and item.get("owner") else "")
    deferred = (f'<div class="dep">reason: {e(item.get("deferred_reason"))}</div>'
                if status == "deferred" and item.get("deferred_reason") else "")
    merged = ('<div class="dep">merged, awaiting evidence</div>'
              if item.get("id") in merged_waiting_ids else "")
    size = size_line(item)
    return (f'<tr class="item" data-id="{e(item.get("id"))}" data-status="{e(status)}">'
            f'<td class="id">{e(item.get("id"))}</td>'
            f'<td>{e(item.get("title"))}{dep}{found}{owner}{deferred}{merged}{size}</td>'
            f'<td class="tag">{e(item.get("tag") or item.get("cx"))}</td>'
            f'<td><span class="pill {slug(status)}">{e(status)}</span></td>'
            f'<td class="issue">{issue_cell(item.get("issue"), repo)}</td>'
            f'<td class="last">{last_log(item)}</td></tr>')


def phase_section(phase: dict, its_items: list, repo, merged_waiting_ids=frozenset()) -> str:
    counts = {s: 0 for s in STATUS_ORDER}
    for i in its_items:
        if i.get("status") in counts:
            counts[i["status"]] += 1
    head = (f'<section class="phase" data-phase="{e(phase.get("id"))}">'
            f'<h2>{e(phase.get("id"))} · {e(phase.get("name"))} '
            f'<span class="count">{counts["done"]}/{len(its_items)}</span></h2>')
    goal = f'<p class="goal">{e(phase.get("goal"))}</p>' if phase.get("goal") else ""
    exit_ = f'<p class="goal"><b>Exit:</b> {e(phase.get("exit"))}</p>' if phase.get("exit") else ""
    rows = "".join(item_row(i, repo, merged_waiting_ids) for i in its_items)
    table = ('<div class="scroll"><table class="items"><thead><tr><th>ID</th><th>Item</th><th>Tag</th>'
             f'<th>Status</th><th>Issue</th><th>Last</th></tr></thead><tbody>{rows}</tbody></table></div>'
             if its_items else '<p class="empty">No items in this phase.</p>')
    return head + goal + exit_ + bar(counts, "bar") + table + "</section>"


def asks_section(asks: list) -> str:
    if not asks:
        return ""
    rows = []
    for a in asks:
        owner = (f'<div class="dep">owner: {e(a.get("owner"))}</div>'
                 if a.get("state") == "open" and a.get("owner") else "")
        rows.append(
            f'<tr class="ask" data-id="{e(a.get("id"))}" data-state="{e(a.get("state"))}">'
            f'<td class="id">{e(a.get("id"))}</td><td>{e(a.get("kind"))}</td>'
            f'<td>“{e(a.get("quote"))}”</td><td>{e(a.get("became") or "—")}</td>'
            f'<td><span class="pill a-{e(str(a.get("state", "")).replace(" ", "-"))}">{e(a.get("state"))}</span>'
            f'{owner}</td></tr>')
    open_n = sum(1 for a in asks if a.get("state") == "open")
    return (f'<section class="asks"><h2>Asks <span class="count">{open_n} open</span></h2>'
            '<div class="scroll"><table class="items"><thead><tr><th>ID</th><th>Kind</th><th>In his words</th>'
            f'<th>Became</th><th>State</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>')


def readiness_section(r: dict | None) -> str:
    """Readiness (D8) as the page's headline number, its four parts --
    work/gates/floors/receipts -- beneath it (proposal 20, V-09; it was small
    grey text beside its label). Only when the ledger declares
    readiness_weights (L.readiness returns None otherwise), and never
    recomputed: r is exactly what L.readiness(ledger) gave."""
    if r is None:
        return ""
    parts = "".join(f"<li>{name} {e(r[name])}</li>" for name in ("work", "gates", "floors", "receipts"))
    return (f'<section class="readiness"><h2>Readiness</h2>'
            f'<p class="headline">{e(r["readiness"])}<span class="unit">%</span></p>'
            f'<ul class="parts">{parts}</ul></section>')


def gates_section(gates: list) -> str:
    if not gates:
        return ""
    rows = "".join(
        f'<tr><td class="id">{e(g.get("id"))}</td><td>{e(g.get("title") or g.get("name"))}</td>'
        f'<td><span class="pill {"s-done" if g.get("passed") else "s-not-started"}">'
        f'{"passed" if g.get("passed") else "not passed"}</span></td></tr>'
        for g in gates if isinstance(g, dict))
    return ('<section class="gates"><h2>Gates</h2><div class="scroll"><table class="items"><thead><tr>'
            '<th>ID</th><th>Gate</th><th>Passed</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></section>')


def floors_section(floors: list) -> str:
    if not floors:
        return ""
    rows = "".join(
        f'<tr><td>{e(f.get("title"))}</td><td><span class="pill {"s-done" if f.get("met") else "s-not-started"}">'
        f'{"met" if f.get("met") else "not met"}</span></td></tr>'
        for f in floors if isinstance(f, dict))
    return ('<section class="floors"><h2>Quality floors</h2><div class="scroll"><table class="items"><thead><tr>'
            '<th>Floor</th><th>Met</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></section>')


def requests_section(requests: list) -> str:
    """Open requests, both directions (D7) -- exactly L.open_requests(ledger),
    which already keeps only the open/in-progress ones."""
    if not requests:
        return ""
    rows = "".join(
        f'<tr class="request" data-id="{e(r.get("id"))}" data-state="{e(r.get("state"))}">'
        f'<td class="id">{e(r.get("id"))}</td><td>{e(r.get("from"))}</td><td>{e(r.get("to"))}</td>'
        f'<td><span class="pill">{e(r.get("state"))}</span></td>'
        f'<td>{e(" ".join(r.get("unblocks") or []))}</td></tr>'
        for r in requests)
    return ('<section class="requests"><h2>Open requests</h2><div class="scroll"><table class="items"><thead><tr>'
            '<th>ID</th><th>From</th><th>To</th><th>State</th><th>Unblocks</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></section>')


def waiting_section(ledger: dict) -> str:
    """Who is blocking whom (D4): every owner named on a blocked row or an
    open ask, with what L.waiting_on(ledger, owner) says they are waiting on."""
    owners = sorted({i.get("owner") for i in L.items(ledger)
                      if i.get("status") == "blocked" and i.get("owner")} |
                     {a.get("owner") for a in (ledger.get("asks") or [])
                      if a.get("state") == "open" and a.get("owner")})
    if not owners:
        return ""
    rows = "".join(
        f'<tr><td class="id">{e(owner)}</td><td>{e(", ".join(L.waiting_on(ledger, owner)))}</td></tr>'
        for owner in owners)
    return ('<section class="waiting"><h2>Waiting on</h2><div class="scroll"><table class="items"><thead><tr>'
            '<th>Owner</th><th>Items and asks</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></section>')


def switches_section(ledger: dict) -> str:
    """Switches the ledger records off (D5) -- on is the default and not
    worth a row; L.switch_on(ledger, name) decides off, never re-derived."""
    switches = ledger.get("switches")
    if not isinstance(switches, dict):
        return ""
    off = [name for name in L.SWITCHES if name in switches and not L.switch_on(ledger, name)]
    if not off:
        return ""
    rows = "".join(
        f'<tr><td class="id">{e(name)}</td><td>{e(switches[name].get("by"))}</td>'
        f'<td>{e(str(switches[name].get("at", ""))[:16].replace("T", " "))}</td></tr>'
        for name in off)
    return ('<section class="switches"><h2>Switches off</h2><div class="scroll"><table class="items"><thead><tr>'
            '<th>Switch</th><th>By</th><th>At</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></section>')


def changes_section(changes: list) -> str:
    if not changes:
        return ""
    rows = "".join(
        f'<tr><td class="last">{e(str(c.get("at", ""))[:16].replace("T", " "))}</td><td>{e(c.get("from"))}</td>'
        f'<td class="id">{e(c.get("item"))}</td><td>{e(c.get("change"))}</td><td>{e(c.get("state"))}</td></tr>'
        for c in changes)
    return ('<section class="changes"><h2>Proposed changes</h2><div class="scroll"><table class="items"><thead><tr>'
            '<th>At</th><th>From</th><th>Item</th><th>Change</th><th>State</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></section>')


def tiers_section(tiers: dict) -> str:
    if not tiers:
        return ""
    rows = "".join(
        f'<tr><td class="id">{e(k)}</td><td>{e(v.get("tier"))}</td><td>{e(v.get("model"))}</td>'
        f'<td>{e(v.get("effort", ""))}</td><td>{e(v.get("rule"))}</td></tr>'
        for k, v in tiers.items())
    return ('<section class="tiers"><h2>Classes</h2><div class="scroll"><table class="items"><thead><tr><th>Class</th>'
            '<th>Tier</th><th>Model</th><th>Effort</th><th>Rule</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></section>')


def priority_section(priority: dict) -> str:
    if not priority or not priority.get("order"):
        return ""
    order = " → ".join(e(x) for x in priority.get("order", []))
    who = e(priority.get("by", ""))
    return (f'<section class="changes"><h2>Priority</h2><p class="goal">{e(priority.get("instruction", ""))}</p>'
            f'<p class="goal"><b>Order:</b> {order} <span class="dim">· set by {who}</span></p></section>')


CSS = """
:root{--ground:#EEF0F2;--surface:#FAFBFC;--ink:#161A1E;--dim:#67707A;--rule:#CDD3D9;
--done:#2F855A;--prog:#D4531F;--block:#B23A48;--todo:#C3CAD1;
--mono:"SF Mono",ui-monospace,Menlo,monospace;--sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ground:#121619;--surface:#1A1F24;--ink:#E5E8EB;
--dim:#909AA4;--rule:#2E363E;--done:#5FB58A;--prog:#F0733E;--block:#D06A77;--todo:#3A434C}}
:root[data-theme="dark"]{--ground:#121619;--surface:#1A1F24;--ink:#E5E8EB;--dim:#909AA4;--rule:#2E363E;
--done:#5FB58A;--prog:#F0733E;--block:#D06A77;--todo:#3A434C}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font:15px/1.5 var(--sans)}
.wrap{max-width:1120px;margin:0 auto;padding:36px 22px 80px}
.head h1{font-size:30px;margin:4px 0 0;letter-spacing:-.01em;text-wrap:balance}
.eyebrow{font:12px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--dim);margin:0}
.status{margin-top:18px}
.line{font:600 15px var(--mono);margin:0 0 8px;font-variant-numeric:tabular-nums}
.overall,.bar{display:flex;height:10px;background:var(--todo);overflow:hidden;border-radius:2px}
.overall{height:14px}
.bar{margin:10px 0 12px}
.seg{display:block;height:100%}
.seg.s-done,.seg.s-deferred{background:var(--done)}.seg.s-in-progress{background:var(--prog)}
.seg.s-blocked{background:var(--block)}.seg.s-not-started{background:var(--todo)}.seg.s-empty{background:var(--todo)}
section{margin-top:34px}
h2{font-size:18px;margin:0}
.count{font:500 13px var(--mono);color:var(--dim);margin-left:6px}
.goal{color:var(--dim);margin:6px 0 0;max-width:80ch}
.scroll{overflow-x:auto}
.items{width:100%;border-collapse:collapse;background:var(--surface);font-size:14px}
.items th{text-align:left;font:600 11px var(--sans);letter-spacing:.06em;text-transform:uppercase;color:var(--dim);
padding:8px 10px;border-bottom:1px solid var(--ink)}
.items td{padding:8px 10px;border-bottom:1px solid var(--rule);vertical-align:top}
.id,.tag,.issue,.last{font-family:var(--mono);font-size:12.5px;white-space:nowrap}
.issue a{color:var(--prog)}
.dep{font:12px var(--mono);color:var(--dim);margin-top:2px}
.why{font:12px var(--sans);color:var(--block);white-space:normal;max-width:48ch;margin-top:3px}.deferred-why{color:var(--done)}
.dim{color:var(--dim)}
.empty{color:var(--dim);font-style:italic}
.pill{display:inline-block;font:600 11.5px var(--mono);padding:1px 7px;border-radius:9px;border:1px solid currentColor;white-space:nowrap}
.pill.s-done,.pill.a-became-item,.pill.a-answered{color:var(--done)}
.pill.s-in-progress,.pill.a-open{color:var(--prog)}
.pill.s-deferred{color:var(--done)}
.pill.s-blocked{color:var(--block)}
.pill.s-not-started,.pill.a-declined{color:var(--dim)}
.asks,.changes,.tiers,.phase{display:block}
"""

# Appended to CSS only on a page whose ledger declares readiness, so a page
# without it stays byte for byte what it was (tests/test_tracker_render.py
# TestBackwardCompatibility pins that).
READINESS_CSS = """.readiness{margin-top:22px;padding:18px 20px 16px;background:var(--surface);border-top:3px solid var(--done)}
.readiness h2{font:600 12px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--dim)}
.readiness .headline{font:700 72px/1 var(--sans);letter-spacing:-.02em;margin:6px 0 0;font-variant-numeric:tabular-nums}
.readiness .unit{font-size:36px;font-weight:600;color:var(--dim);margin-left:2px}
.readiness .parts{display:flex;flex-wrap:wrap;gap:4px 22px;list-style:none;padding:0;margin:12px 0 0;
font:500 14px var(--mono);color:var(--dim);font-variant-numeric:tabular-nums}
"""

# C-06: colours for "in review" and "in testing", appended only on a page
# that actually has an item in one of them -- a ledger with only the
# original four statuses renders byte for byte as it did before (pinned by
# tests/test_tracker_render.py TestBackwardCompatibility).
REVIEW_TESTING_CSS = """:root{--review:#6B4FBB;--test:#1D7A96}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--review:#A992E8;--test:#5FC2DE}}
:root[data-theme="dark"]{--review:#A992E8;--test:#5FC2DE}
.seg.s-in-review{background:var(--review)}.seg.s-in-testing{background:var(--test)}
.pill.s-in-review{color:var(--review)}.pill.s-in-testing{color:var(--test)}
"""


def render(data: dict, source: Path, repo: str | None) -> str:
    counts = L.counts(data)
    phases = list(data.get("phases") or [])
    known = {p.get("id") for p in phases}
    loose = [i for i in L.items(data) if i.get("phase") not in known]
    if loose:
        phases.append({"id": "", "name": "Unphased"})
    merged_waiting_ids = set(L.merged_waiting(data))
    sections = []
    for p in phases:
        its = [i for i in L.items(data) if (i.get("phase") == p.get("id")) or (p.get("id") == "" and i in loose)]
        sections.append(phase_section(p, its, repo, merged_waiting_ids))
    n, status, title = data.get("proposal"), data.get("status", ""), data.get("title", "")
    readiness = L.readiness(data)
    # C-06: only a page with an item actually in one of the two new buckets
    # carries their attributes and colours -- a ledger with only the
    # original four statuses renders byte for byte as it did before.
    in_review_testing = bool(counts["in review"] or counts["in testing"])
    status_extra = (f' data-in-review="{counts["in review"]}" data-in-testing="{counts["in testing"]}"'
                    if in_review_testing else "")
    if counts["deferred"]:
        status_extra += f' data-deferred="{counts["deferred"]}"'
    return (
        f"<!-- generated by bin/tracker render from {e(source.name)} -- edit the ledger, not this page -->\n"
        f"<title>{e(n)} · {e(status)} · {e(title)} · tracker</title>\n"
        f'<meta name="ledger-source" content="{e(source.name)}">\n'
        f'<meta name="ledger-digest" content="{digest(source)}">\n'
        f"<style>{CSS}{READINESS_CSS if readiness is not None else ''}"
        f"{REVIEW_TESTING_CSS if in_review_testing else ''}</style>\n"
        '<main class="wrap">'
        f'<header class="head"><p class="eyebrow">Proposal {e(n)} · {e(status)} · updated {e(data.get("updated", ""))}</p>'
        f"<h1>{e(title)}</h1></header>"
        + readiness_section(readiness)
        + f'<section class="status" data-done="{counts["done"]}" data-in-progress="{counts["in progress"]}" '
        f'data-blocked="{counts["blocked"]}" data-not-started="{counts["not started"]}"{status_extra}>'
        f'<p class="line">{e(L.status_line(data))}</p>{bar(counts, "overall")}</section>'
        + "".join(sections)
        + asks_section(data.get("asks") or [])
        + gates_section(data.get("gates") or [])
        + floors_section(data.get("quality_floors") or [])
        + requests_section(L.open_requests(data))
        + waiting_section(data)
        + priority_section(data.get("priority") or {})
        + changes_section(data.get("proposed_changes") or [])
        + tiers_section(data.get("tiers") or {})
        + switches_section(data)
        + "</main>\n"
    )


def freshness(ledger_path: Path, page: Path) -> str:
    """"ok", "missing", or "stale": does the page carry this ledger's digest?"""
    if not page.exists():
        return "missing"
    m = re.search(r'<meta name="ledger-digest" content="([0-9a-f]{64})">', page.read_text(errors="replace"))
    return "ok" if m and m.group(1) == digest(ledger_path) else "stale"


# ---------------------------------------------------------------------------
# tracker published (proposal 20, V-09, D1)
#
# An artifact is published only through a Claude session's Artifact tool; no
# hook or script can call it. So nothing here publishes. The session
# publishes the page, then runs `tracker published` to record what went out:
# a committed sidecar beside the page,
#
#   docs/proposals/tracker/<ledger stem>.published.json
#   {"at": "<real clock, with offset>", "by": "<name>" | null,
#    "digest": "<sha256 of the page file as published>",
#    "ledger_digest": "<sha256 of the ledger file's bytes>",      (V-11)
#    "page": "<path relative to the project root>",               (V-11, --page only)
#    "page_unchanged": true,                  (V-11 round 2, --page-unchanged only)
#    "url": "https://..."}
#
# Two modes. Without a declared plan_page the page is the tracker page, and
# bin/warmup names it when its bytes no longer match `digest`: a page that
# changed because the renderer did is also one the published copy no longer
# matches. With a declared plan_page (proposal 20, D9) the page is the file
# that project's own generator writes, named with --page, and bin/warmup
# compares `ledger_digest` instead -- the PhotoVault app's generator writes
# today's date into its page, so the page digest would move every day (V-11).
# A V-09 record without ledger_digest keeps working.

def published_path(ledger_path: Path) -> Path:
    return default_out(ledger_path).with_name(f"{ledger_path.stem}.published.json")


def _one_line_utf8(s: str) -> bool:
    try:
        s.encode("utf-8")
    except UnicodeEncodeError:           # a lone surrogate
        return False
    return not any(ord(c) < 32 or 127 <= ord(c) < 160 for c in s)


def _printable(value) -> str:
    """A value safe to print on one line in an error: bin/warmup's shown(),
    for the messages this module prints itself. C0, DEL, C1 and Unicode
    format characters (Cf, e.g. a U+202E bidi override) become visible
    escapes; a lone surrogate becomes U+FFFD."""
    import unicodedata
    out = []
    for ch in str(value):
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            out.append("�")
        elif cp < 0x20 or cp == 0x7F or 0x80 <= cp <= 0x9F:
            out.append({"\n": "\\n", "\r": "\\r", "\t": "\\t"}.get(ch, f"\\x{cp:02x}"))
        elif unicodedata.category(ch) == "Cf":
            out.append(f"\\u{cp:04x}" if cp <= 0xFFFF else f"\\U{cp:08x}")
        else:
            out.append(ch)
    return "".join(out)


def url_problem(url) -> str | None:
    """None for one line of https://host[:port]/..., else what is wrong --
    never echoing the value, which is untrusted and may carry a forged line.
    Refused as well (round 2): a Unicode format character, which can make one
    URL read as another; userinfo, which puts a lookalike in front of the real
    host; and a port that is empty, not a number, or outside 1-65535."""
    import unicodedata
    if not isinstance(url, str) or not url:
        return "url must be a non-empty string"
    if not _one_line_utf8(url) or any(c.isspace() for c in url):
        return "url must be one line of UTF-8 with no spaces or control characters"
    if any(unicodedata.category(c) == "Cf" for c in url):
        return "url must not contain a Unicode format character (such as a bidi override or zero-width space)"
    from urllib.parse import urlsplit
    try:
        parts = urlsplit(url)
        host = parts.hostname
    except ValueError:
        return "url is not a URL"
    if parts.scheme != "https" or not host:
        return "url must be https://<host>/..."
    if "@" in parts.netloc:
        return "url must not carry userinfo (user:password@) before its host"
    try:
        port = parts.port
    except ValueError:
        port = 0
    if parts.netloc.endswith(":") or port == 0:
        return "url port must be a number from 1 to 65535"
    return None


def _hex64(value) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


# ---------------------------------------------------------------------------
# T-06 repair (proposal 22): a published page's name is set once and never
# changes. Recording gained a `title` field (V-09/V-11 records have none --
# a sidecar with no recorded title has nothing to compare, is accepted, and
# gains one); comparing refuses a later publish whose page's own <title>
# differs from what the sidecar last recorded, unless --title-changed says
# the sponsor wants the rename recorded anyway.

def page_title(page: Path) -> str | None:
    """The page's own <title> text, HTML-unescaped, or None if it has none
    (a declared plan_page's own generator may not emit one -- V-11's
    AppProject fixture doesn't, and that is fine: nothing to compare)."""
    try:
        text = page.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.S)
    if not m:
        return None
    return html.unescape(m.group(1)).strip()


def _recorded_title(sidecar: Path) -> str | None:
    """The <title> a sidecar last recorded, or None -- a missing sidecar, one
    that cannot be read as a JSON object, or a record from before this check
    existed (no 'title' key) all mean nothing to compare."""
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError):
        return None
    if not isinstance(data, dict):
        return None
    title = data.get("title")
    return title if isinstance(title, str) and title else None


def _title_check(sidecar: Path, page: Path, override: bool) -> tuple[str | None, bool, str | None]:
    """(the page's own <title> or None, whether a change was recorded by
    override, a refusal message or None).

    None/None/None when the page has no <title>, or the sidecar has nothing
    recorded yet, or the titles match: nothing to refuse, and the title (if
    any) is recorded going forward. A changed title is refused by default
    (proposal 22, T-06: "a published page's name is set once and never
    changes"); --title-changed records the new name and that the change was
    deliberate."""
    new_title = page_title(page)
    if new_title is None:
        return None, False, None
    old_title = _recorded_title(sidecar)
    if old_title is None or old_title == new_title:
        return new_title, False, None
    if override:
        return new_title, True, None
    return new_title, False, (
        f"{_printable(page)}'s <title> has changed since {_printable(sidecar)} last recorded it -- "
        f"was {_printable(old_title)}, now {_printable(new_title)} -- proposal 22 T-06: a published page's "
        "name is set once and never changes -- pass --title-changed to record the new name anyway -- "
        "nothing recorded")


def page_path_problem(value) -> str | None:
    """None for a one-line relative path with no `..` part, else what is wrong
    -- never echoing the value. Whether it resolves inside the project, through
    a symlink, is asked of the file system by the caller (V-11)."""
    from pathlib import PurePosixPath
    if not isinstance(value, str) or not value.strip():
        return "page must be a non-empty path"
    if not _one_line_utf8(value):
        return "page must be one line of UTF-8 with no control characters"
    p = PurePosixPath(value)
    if p.is_absolute() or Path(value).is_absolute():
        return "page must be relative to the project root, not absolute"
    if ".." in p.parts:
        return "page must not have a '..' part"
    return None


def _record_field_problems(record: dict) -> list[str]:
    """url, digest, at and by -- the four fields every publish record carries,
    checked once for the per-ledger record and the project page's."""
    out = []
    for key in ("url", "digest", "at", "by"):
        if key not in record:
            out.append(f"no {key!r}")
    if "url" in record and url_problem(record["url"]):
        out.append(url_problem(record["url"]))
    if "digest" in record and not _hex64(record["digest"]):
        out.append("digest must be 64 lowercase hex characters")
    if "at" in record:
        import datetime
        at = record["at"]
        try:
            ok = (isinstance(at, str) and _one_line_utf8(at)
                  and datetime.datetime.fromisoformat(at).tzinfo is not None)
        except ValueError:
            ok = False
        if not ok:
            out.append("at must be an ISO 8601 time with its offset")
    if "by" in record and record["by"] is not None and not (
            isinstance(record["by"], str) and record["by"].strip() and _one_line_utf8(record["by"])):
        out.append("by must be null or a one-line name")
    return out


def project_published_problems(record) -> list[str]:
    """What is wrong with docs/proposals/tracker/index.published.json, without
    echoing any value (proposal 22, T-03).

    The project page's record carries the four fields every record carries and
    `ledgers`: the page's own ledger-digests line, so the record says which
    ledgers the published page showed. A per-ledger key -- `page`,
    `page_unchanged`, `ledger_digest` -- belongs to a ledger's record, never to
    this one: a record shaped like the other kind is the false record proposal
    20 V-11 exists to stop."""
    if not isinstance(record, dict):
        return ["not a JSON object"]
    out = _record_field_problems(record)
    if "ledgers" not in record:
        out.append("no 'ledgers'")
    elif not (isinstance(record["ledgers"], str) and record["ledgers"].strip()
              and _one_line_utf8(record["ledgers"])):
        out.append("ledgers must be one line of UTF-8 -- the page's own ledger-digests content")
    for key in ("page", "page_unchanged", "ledger_digest"):
        if key in record:
            out.append(f"{key!r} belongs to a ledger's record, not the project page's")
    return out


def published_problems(record) -> list[str]:
    """What is wrong with a sidecar's contents, without echoing any value.
    `ledger_digest` (V-11) is optional -- a V-09 record has none -- but a
    record that names its `page` must carry it, because that is what the card
    compares for a declared page."""
    if not isinstance(record, dict):
        return ["not a JSON object"]
    out = _record_field_problems(record)
    if "ledger_digest" in record and not _hex64(record["ledger_digest"]):
        out.append("ledger_digest must be 64 lowercase hex characters")
    if "page" in record:
        problem = page_path_problem(record["page"])
        if problem:
            out.append(problem)
        if "ledger_digest" not in record:
            out.append("a record with 'page' must carry 'ledger_digest'")
    if "page_unchanged" in record:
        if record["page_unchanged"] is not True:
            out.append("page_unchanged must be true when present")
        if "page" not in record:
            out.append("page_unchanged belongs only to a record with 'page'")
    return out


def _git(root: Path, *args: str) -> subprocess.CompletedProcess | None:
    """git run in the project root, with every path relative to it and every
    pathspec taken literally: a --page of "*.html" names that file, never a
    glob matching some other tracked one."""
    try:
        return subprocess.run(["git", "--literal-pathspecs", *args], cwd=str(root),
                              capture_output=True, text=True, check=False, timeout=30)
    except (subprocess.SubprocessError, OSError):
        return None


def project_root(ledger_path: Path) -> tuple[Path, bool]:
    """(the project root, whether it is inside a git work tree).

    Round 2 ruling (E6): the root is the folder that holds docs/proposals,
    which published_main has already required -- not the git top, which for an
    app kept in a subdirectory of its repository is the wrong folder and reads
    the wrong .common-rules.json. git only answers questions about files."""
    root = ledger_path.resolve().parent.parent.parent
    r = _git(root, "rev-parse", "--is-inside-work-tree")
    return root, r is not None and r.returncode == 0 and r.stdout.strip() == "true"


def declared_plan_page(root: Path) -> tuple[str | None, list[str]]:
    """(the declared plan_page command, or None) · (problems that block recording).

    Round 2 ruling: only a declaration that cannot be read (not valid JSON, not
    an object) or a plan_page key that is present and fails validation blocks
    -- either would drop plan_page to its default of None, and recording the
    tracker page then is the very false record V-11 exists to stop. A missing
    read_order or safety_rules file, or a bad gate, is warmup --check's to name."""
    from tools import project as P
    data, why = P._raw(root)
    if why:
        return None, P.problems(root)
    if data is None or "plan_page" not in data:
        return None, []
    command, problem = P._command("plan_page", data["plan_page"])
    return command, ([problem] if problem else [])


def _inside(root: Path, path: Path) -> bool:
    try:
        return Path(path).resolve().is_relative_to(root)
    except (OSError, ValueError, RuntimeError):
        return False


def _tracked(root: Path, rel: str) -> bool:
    # -z: a non-ASCII name is printed as-is, not C-quoted, so it compares equal.
    listed = _git(root, "ls-files", "-z", "--error-unmatch", "--", rel)
    return listed is not None and listed.returncode == 0 and listed.stdout == rel + "\0"


def _clean(root: Path, rel: str) -> bool:
    diff = _git(root, "diff", "--quiet", "HEAD", "--", rel)
    return diff is not None and diff.returncode == 0


def _page_after_ledger(root: Path, ledger_rel: str, page_rel: str) -> bool:
    """The ledger's last commit is the page's last commit or an ancestor of it:
    the page was committed with, or after, the ledger it shows (round 2, D1)."""
    last = [_git(root, "log", "-1", "--format=%H", "--", rel) for rel in (ledger_rel, page_rel)]
    if any(r is None or r.returncode != 0 or not r.stdout.strip() for r in last):
        return False
    ledger_commit, page_commit = (r.stdout.strip() for r in last)
    r = _git(root, "merge-base", "--is-ancestor", ledger_commit, page_commit)
    return r is not None and r.returncode == 0


def page_problem(root: Path, raw: str) -> tuple[str | None, str | None]:
    """(the page's plain relative path, None) or (None, what is wrong with --page).
    Each message names the value through _printable (V-11, rule 3)."""
    import stat
    from pathlib import PurePosixPath
    shown_ = _printable(raw)
    problem = page_path_problem(raw)
    if problem == "page must be relative to the project root, not absolute":
        return None, f"--page {shown_} is absolute -- a page is a path relative to the project root {_printable(root)}"
    if problem == "page must not have a '..' part":
        return None, f"--page {shown_} has a '..' part -- a page is a path inside the project, relative to its root"
    if problem:
        return None, f"--{problem} (got {shown_})"
    rel = str(PurePosixPath(raw))
    target = root / rel
    if not _inside(root, target):
        return None, f"--page {shown_} resolves outside the project {_printable(root)} -- it is not read"
    try:
        mode = target.lstat().st_mode
    except FileNotFoundError:
        return None, f"--page {shown_} does not exist under {_printable(root)} -- regenerate the page first"
    except OSError as exc:
        return None, f"--page {shown_} could not be read ({type(exc).__name__})"
    if not stat.S_ISREG(mode):
        return None, f"--page {shown_} is not a regular file (a directory or a symlink is not a published page)"
    if not _tracked(root, rel):
        return None, f"--page {shown_} is not tracked by git -- commit the generated page, publish it, then record it"
    if not _clean(root, rel):
        return None, f"--page {shown_} has uncommitted changes -- commit the regenerated page, publish that " \
                     "committed file, then record it"
    return rel, None


def published_project_main(args) -> int:
    """`tracker published --project` -- record the project's one tracker page
    (proposal 22, T-03).

    The sponsor asked for "per project, there should be one tracker" (A-01),
    so what is published is docs/proposals/tracker/index.html, a page of every
    ledger, and the record beside it carries the page's digest and the page's
    own ledger-digests line. Nothing here publishes: only a session's Artifact
    tool can, which is why this exists at all.

    It refuses, writing nothing and naming the reason, exactly as the
    per-ledger flow does: publishing switched off in any ledger, a bad url or
    --by, a page missing or stale against the ledgers, any ledger or the page
    uncommitted or untracked, a symlinked tracker directory, page or sidecar,
    and a project that is not inside a git repository. A project that declares
    plan_page publishes that page instead (D5): the project page is rendered
    and checked beside it, never published in its place."""
    from tools.tracker import board as B   # board imports render, so never at module load
    say = "tracker published:"
    root = Path(args.project).resolve()
    paths = B.ledger_paths(root)
    if not paths:
        print(f"{say} no ledger under {_printable(root / 'docs' / 'proposals')} -- the project page is a page of "
              "its ledgers; nothing recorded", file=sys.stderr)
        return 2
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, RecursionError) as exc:
            print(f"{say} {_printable(path)} could not be read as a JSON ledger ({type(exc).__name__}) "
                  "-- nothing recorded", file=sys.stderr)
            return 2
        if not isinstance(data, dict):
            print(f"{say} {_printable(path)} is not a ledger: not a JSON object -- nothing recorded",
                  file=sys.stderr)
            return 2
        if not L.switch_on(data, "publish"):
            sw = data["switches"]["publish"]
            print(f"{say} publish is switched off in {_printable(path.name)} by {_printable(sw.get('by'))} "
                  f"at {_printable(sw.get('at'))}, and the project page shows that ledger too -- nothing "
                  "recorded, and nothing should have been published", file=sys.stderr)
            return 1
    problem = url_problem(args.url)
    if problem:
        print(f"{say} {problem} (got {_printable(args.url)}) -- nothing recorded", file=sys.stderr)
        return 1
    if args.by is not None and not (args.by.strip() and _one_line_utf8(args.by)):
        print(f"{say} --by must be a one-line name (got {_printable(args.by)}) -- nothing recorded", file=sys.stderr)
        return 1

    from tools import project as P
    command, broken = declared_plan_page(root)
    if broken:
        print(f"{say} {_printable(root / P.FILE)} cannot say whether this project declares plan_page "
              "-- nothing recorded:", file=sys.stderr)
        for problem in broken:
            print(f"  {_printable(problem)}", file=sys.stderr)
        return 1
    if command:
        # D5: the declared page is this project's tracker (proposal 20, V-11).
        print(f"{say} this project declares plan_page ({_printable(command)}); that page is its tracker -- "
              "publish it and record it with: tracker published <ledger> --url <url> --page <the file it "
              "writes> -- nothing recorded", file=sys.stderr)
        return 1

    page, sidecar = B.default_out(root), B.published_path(root)
    for what, target in (("the project page", page), ("the record", sidecar)):
        if not _inside(root, target):
            print(f"{say} {what} {_printable(target)} resolves outside the project {_printable(root)} "
                  "(a symlinked tracker directory) -- nothing recorded", file=sys.stderr)
            return 1
    if sidecar.is_symlink() or sidecar.parent.is_symlink():
        print(f"{say} {_printable(sidecar)} is a symlink, or its tracker directory is -- a record is written "
              "only to a real file in the project -- nothing recorded", file=sys.stderr)
        return 1
    if page.is_symlink():
        print(f"{say} {_printable(page)} is a symlink -- a published page is a regular file -- nothing recorded",
              file=sys.stderr)
        return 1
    if page.exists() and not page.is_file():
        print(f"{say} {_printable(page)} is not a regular file -- nothing recorded", file=sys.stderr)
        return 1

    r = _git(root, "rev-parse", "--is-inside-work-tree")
    if not (r is not None and r.returncode == 0 and r.stdout.strip() == "true"):
        print(f"{say} {_printable(root)} is not inside a git repository -- a record is made only of a committed "
              "page -- nothing recorded", file=sys.stderr)
        return 1
    fresh = B.freshness(paths, page)
    if fresh != "ok":
        print(f"{say} {_printable(page)} is {fresh} against the project's {len(paths)} ledger(s) -- render "
              f"first: tracker board --project {_printable(root)}, publish that page, then record it",
              file=sys.stderr)
        return 1
    for path in paths:
        if not _inside(root, path):
            print(f"{say} {_printable(path)} resolves outside the project {_printable(root)} "
                  "(a symlinked ledger) -- a ledger is read only from within the project -- nothing recorded",
                  file=sys.stderr)
            return 1
        rel = path.resolve().relative_to(root).as_posix()
        if not (_tracked(root, rel) and _clean(root, rel)):
            print(f"{say} {_printable(rel)}: the ledger has uncommitted changes -- commit it first "
                  "-- nothing recorded", file=sys.stderr)
            return 1
    page_rel = page.resolve().relative_to(root).as_posix()
    if not (_tracked(root, page_rel) and _clean(root, page_rel)):
        print(f"{say} {_printable(page_rel)}: the project page has uncommitted changes -- commit the rendered "
              "page, publish that committed file, then record it -- nothing recorded", file=sys.stderr)
        return 1

    new_title, title_changed, problem = _title_check(sidecar, page, args.title_changed)
    if problem:
        print(f"{say} {problem}", file=sys.stderr)
        return 1

    import datetime
    record = {"url": args.url, "digest": digest(page), "ledgers": B.page_digests(page), "by": args.by,
              "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    if new_title is not None:
        record["title"] = new_title
    if title_changed:
        record["title_changed"] = True
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"recorded {sidecar} · {args.url} · commit it")
    return 0


def published_main(argv) -> int:
    ap = argparse.ArgumentParser(prog="tracker published",
                                 description="record the page a session just published with its Artifact tool")
    ap.add_argument("ledger", type=Path, nargs="?",
                    help="the ledger whose own tracker page was published (proposal 22, T-03: only a ledger "
                         "that records `tracker.own`, or a declared plan_page with --page)")
    ap.add_argument("--project", type=Path, nargs="?", const=Path("."),
                    help="record the project's one tracker page, docs/proposals/tracker/index.html "
                         "(default: the current directory)")
    ap.add_argument("--url", required=True, help="the artifact's URL, https, one line")
    ap.add_argument("--by", help="who published it (default: recorded as null)")
    ap.add_argument("--page", help="the declared plan_page's output, relative to the project root "
                                   "(required when .common-rules.json declares plan_page; refused otherwise)")
    ap.add_argument("--page-unchanged", action="store_true",
                    help="with --page: record a page last committed before the ledger's last change, for a "
                         "ledger change that leaves the page's bytes identical; the sidecar records it")
    ap.add_argument("--title-changed", action="store_true",
                    help="override: record a page whose <title> differs from the one last recorded published "
                         "-- proposal 22 T-06 says a published page's name is set once and never changes; "
                         "the sidecar records that the change was deliberate")
    args = ap.parse_args(argv)
    say = "tracker published:"

    if args.project is not None:
        # One page or the other, never both in one record (proposal 22, T-03).
        if args.ledger is not None:
            ap.error("--project records the project's one tracker page; it takes no ledger argument")
        if args.page is not None or args.page_unchanged:
            ap.error("--page and --page-unchanged belong to a ledger's record (a declared plan_page), "
                     "not to --project")
        return published_project_main(args)
    if args.ledger is None:
        ap.error("name a ledger, or --project for the project's one tracker page")

    where = _printable(args.ledger)
    folder = args.ledger.resolve().parent
    if not (folder.name == "proposals" and folder.parent.name == "docs"):
        # Round 2, finding 5: the sidecar is the page's, and the page of
        # record lives under docs/proposals/tracker/.
        print(f"{say} {where} is not in a docs/proposals directory -- only a ledger of record is "
              "published; nothing recorded", file=sys.stderr)
        return 1
    if not args.ledger.is_file():
        print(f"{say} no ledger at {where} -- nothing recorded", file=sys.stderr)
        return 2
    try:
        data = json.loads(args.ledger.read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError) as exc:   # UnicodeDecodeError is a ValueError
        print(f"{say} {where} could not be read as a JSON ledger ({type(exc).__name__}) -- nothing recorded",
              file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print(f"{say} {where} is not a ledger: not a JSON object -- nothing recorded", file=sys.stderr)
        return 2
    if not L.switch_on(data, "publish"):
        sw = data["switches"]["publish"]
        print(f"{say} publish is switched off in {_printable(args.ledger.name)} by {_printable(sw.get('by'))} "
              f"at {_printable(sw.get('at'))} -- nothing recorded, and nothing should have been published",
              file=sys.stderr)
        return 1
    problem = url_problem(args.url)
    if problem:
        print(f"{say} {problem} (got {_printable(args.url)}) -- nothing recorded", file=sys.stderr)
        return 1
    if args.by is not None and not (args.by.strip() and _one_line_utf8(args.by)):
        print(f"{say} --by must be a one-line name (got {_printable(args.by)}) -- nothing recorded",
              file=sys.stderr)
        return 1

    # V-11 (D1 with D9): a project that declares plan_page publishes the page
    # its own generator writes, not the tracker page. The PhotoVault app's
    # record claimed the tracker page's digest for a publish that never
    # happened; so a declaration without --page refuses, naming the command.
    #
    # Round 2: a record must be true when it is made. The ledger it names is
    # committed (both modes); a declared page was committed with or after the
    # ledger's last change, unless --page-unchanged says, on the record, that
    # the change left the page's bytes identical.
    from tools import project as P
    if args.page_unchanged and args.page is None:
        print(f"{say} --page-unchanged is an override for --page, a declared plan_page's record -- nothing recorded",
              file=sys.stderr)
        return 1
    root, in_git = project_root(args.ledger)
    command, broken = declared_plan_page(root)
    if broken:
        print(f"{say} {_printable(root / P.FILE)} cannot say whether this project declares plan_page "
              "-- nothing recorded:", file=sys.stderr)
        for problem in broken:
            print(f"  {_printable(problem)}", file=sys.stderr)
        return 1
    if command and args.page is None:
        print(f"{say} this project declares plan_page ({_printable(command)}); pass --page <the file it writes> "
              "-- nothing recorded", file=sys.stderr)
        return 1
    if not command and args.page is not None:
        print(f"{say} no plan_page is declared; the tracker page is recorded by default -- nothing recorded",
              file=sys.stderr)
        return 1
    if not command and args.page is None and not L.own_tracker(data):
        # Proposal 22, T-03: the sponsor asked for one tracker per project, so
        # a per-ledger page -- and a per-ledger record -- exists only where he
        # asked for one (`tracker.own`). Anything else is the project's page.
        print(f"{say} {_printable(args.ledger.name)} records no tracker of its own, so it has no page of its "
              f"own to publish -- the project's one page is recorded with: tracker published --project "
              f"{_printable(root)} --url <artifact url> -- nothing recorded", file=sys.stderr)
        return 1
    if not _inside(root, published_path(args.ledger)):
        # Round 2 (from V-09): a symlinked docs/proposals/tracker, or sidecar,
        # would have the record written outside the project.
        print(f"{say} {_printable(published_path(args.ledger))} resolves outside the project {_printable(root)} "
              "(a symlinked tracker directory or sidecar) -- nothing recorded", file=sys.stderr)
        return 1
    sidecar_path = published_path(args.ledger)
    if sidecar_path.is_symlink() or sidecar_path.parent.is_symlink():
        # V-11 final review: a symlink pointing inside the project was followed,
        # and a sidecar linked to the ledger had the record overwrite the ledger.
        print(f"{say} {_printable(sidecar_path)} is a symlink, or its tracker directory is -- a record is "
              "written only to a real file in the project -- nothing recorded", file=sys.stderr)
        return 1
    if not in_git:
        print(f"{say} {_printable(root)} is not inside a git repository -- a record is made only of a committed "
              "ledger -- nothing recorded", file=sys.stderr)
        return 1
    ledger_rel = args.ledger.resolve().relative_to(root).as_posix()
    if not (_tracked(root, ledger_rel) and _clean(root, ledger_rel)):
        print(f"{say} {_printable(ledger_rel)}: the ledger has uncommitted changes -- commit it first "
              "-- nothing recorded", file=sys.stderr)
        return 1

    import datetime
    sidecar = published_path(args.ledger)
    if args.page is not None:
        rel, problem = page_problem(root, args.page)
        if problem:
            print(f"{say} {problem} -- nothing recorded", file=sys.stderr)
            return 1
        if not args.page_unchanged and not _page_after_ledger(root, ledger_rel, rel):
            print(f"{say} {_printable(rel)} was last committed before the ledger changed -- regenerate and commit "
                  "it first -- nothing recorded", file=sys.stderr)
            return 1
        new_title, title_changed, problem = _title_check(sidecar, root / rel, args.title_changed)
        if problem:
            print(f"{say} {problem}", file=sys.stderr)
            return 1
        record = {"url": args.url, "digest": digest(root / rel), "page": rel}
        if args.page_unchanged:
            record["page_unchanged"] = True
    else:
        page = default_out(args.ledger)
        fresh = freshness(args.ledger, page)
        if fresh != "ok":
            print(f"{say} {_printable(page)} is {fresh} against {_printable(args.ledger.name)} -- render first: "
                  f"tracker render {_printable(args.ledger)}, publish that page, then record it", file=sys.stderr)
            return 1
        new_title, title_changed, problem = _title_check(sidecar, page, args.title_changed)
        if problem:
            print(f"{say} {problem}", file=sys.stderr)
            return 1
        record = {"url": args.url, "digest": digest(page)}
    if new_title is not None:
        record["title"] = new_title
    if title_changed:
        record["title_changed"] = True
    record.update({"ledger_digest": digest(args.ledger), "by": args.by,
                   "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
    # V-11: a project that publishes only its declared page may never have
    # rendered the tracker page, so docs/proposals/tracker/ may not exist yet.
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"recorded {sidecar} · {args.url} · commit it")
    return 0


def main(argv) -> int:
    ap = argparse.ArgumentParser(prog="tracker render", description=__doc__.splitlines()[0])
    ap.add_argument("ledger", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--repo", help="owner/name for issue links (default: the ledger's git remote)")
    ap.add_argument("--check", action="store_true", help="exit 1 if the page is missing or stale; write nothing")
    args = ap.parse_args(argv)

    try:
        data = L.load(args.ledger)
    except (OSError, ValueError) as exc:
        print(f"tracker render: {exc}", file=sys.stderr)
        return 2
    out = args.out or default_out(args.ledger)

    if args.check:
        fresh = freshness(args.ledger, out)
        if fresh == "missing":
            print(f"stale: {out} is missing -- run: tracker render {args.ledger}")
            return 1
        if fresh == "stale":
            print(f"stale: {out} was rendered from a different {args.ledger.name} -- run: tracker render {args.ledger}")
            return 1
        print(f"ok {out} matches {args.ledger.name}")
        return 0

    problems = L.validate(data)
    if problems:
        print(f"tracker render: {args.ledger} is not well-formed; a page of it would show numbers nobody can trust:",
              file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    repo = args.repo or infer_repo(args.ledger)
    out.parent.mkdir(parents=True, exist_ok=True)
    text = render(data, args.ledger, repo)
    if not out.exists() or out.read_text() != text:
        out.write_text(text)
    print(f"rendered {out} · {L.status_line(data)}")
    return 0
