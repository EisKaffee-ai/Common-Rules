"""Progress over time, computed from the ledgers' own git history -- no AI
updates (proposal 30, P-07).

The sponsor's words: "there should be a tracker which should plot a graph
over time of how many tickets are getting finished, how many tickets are
added ... This should not be manually updated by AI. So AI should be just
adding one log file or whatever and everything else should be handled by
backend scripts."

So this module never writes anything: it replays the ledgers as git already
recorded them. `series()` walks every calendar day from the first commit
that touched a ledger to today, and for a day with commits reads every
ledger JSON as of that day's *last* commit (`git show <sha>:<path>`) --
days without a commit carry the previous day's snapshot forward rather than
showing a false dip to zero.

A ticket is an item, or -- proposal 30 -- any of its lettered parts, at any
depth (a part with its own `parts` counts itself AND its parts; a nested
part such as W-10.A.1 counts too). Completion uses the same ticket
denominator as the status history: done tickets divided by all tracked
tickets, so nested work cannot make the percentage disagree with the graph.

Two counters beyond the totals-per-day diff: `added_ids`/`closed_ids` count
by comparing the day's ticket-id set against the previous day's, so a
ticket added and closed on the same day is not invisible to a plain
before/after total (which would show 0 net change).

Dates are calendar days in a fixed Europe offset (CET, UTC+1, no DST) --
deliberately not the system zoneinfo database, so the same commit always
lands on the same day on every machine this runs on.

Cache: `.cache/tracker-history.json` under the project root, if the
project's own .gitignore already ignores `.cache` -- else a file under the
system temp dir, keyed by the repo's absolute path, so nothing lands in the
repo uninvited. Snapshots are keyed by configured ledger directory and commit
sha, so two trackers in one repository cannot reuse each other's counts; a
rerun only computes new directory/sha pairs.

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import argparse
import datetime
import fnmatch
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tools.tracker import ledger as L
from tools.tracker import parts as P

# A fixed Europe offset, not a zoneinfo lookup -- see the module docstring.
TZ = datetime.timezone(datetime.timedelta(hours=1), "CET")

LEDGER_GLOB = "[0-9][0-9]*-*.json"


# ---------------------------------------------------------------- git -----

def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def _repo_root(project: Path) -> Path:
    return Path(_git(project, "rev-parse", "--show-toplevel").strip())


def _ledger_directory(project: Path, repo: Path) -> str:
    """Canonical ledger directory as a repository-relative Git path."""
    directory = L.directory(project).resolve()
    try:
        return directory.relative_to(repo.resolve()).as_posix()
    except ValueError:
        raise RuntimeError(f"tracker directory {directory} is outside repository {repo}") from None


def _ledger_commits(repo: Path, ledger_dir: str) -> list[tuple[str, datetime.datetime]]:
    """(sha, Europe-local commit datetime), oldest first, for every commit that
    touched a ledger file directly under the configured tracker directory."""
    out = _git(repo, "log", "--format=%H%x1f%cI", "--reverse", "--", f"{ledger_dir}/{LEDGER_GLOB}")
    commits = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        sha, iso = line.split("\x1f")
        when = datetime.datetime.fromisoformat(iso).astimezone(TZ)
        commits.append((sha, when))
    return commits


def _ledger_paths_at(repo: Path, sha: str, ledger_dir: str) -> list[str]:
    """Ledger file names (not full paths) directly under the tracker at
    `sha`, matching the same NN-*.json shape `ledger.find` uses -- a data
    file that happens to share the shape is filtered out below, once its
    contents are read, exactly as `ledger.find` does for the working tree."""
    try:
        out = _git(repo, "ls-tree", "--name-only", f"{sha}:{ledger_dir}")
    except RuntimeError:
        return []  # the configured tracker did not exist yet at this commit
    return [name for name in (line.strip() for line in out.splitlines() if line.strip())
            if fnmatch.fnmatch(name, LEDGER_GLOB)]


# ------------------------------------------------------------ tickets -----

def _tickets(node: dict):
    """Yield (id, done) for `node` and, recursively, every dict in its
    `parts` list at any depth. A part with its own `parts` is itself a
    ticket AND its parts are tickets (proposal 30): W-10 with parts W-10.A,
    W-10.B, and W-10.A itself split further into W-10.A.1, W-10.A.2, counts
    five tickets in total."""
    yield node.get("id"), node.get("status") == "done", node.get("status") or "not started"
    for part in node.get("parts") or []:
        if isinstance(part, dict):
            yield from _tickets(part)


def _snapshot_at(repo: Path, sha: str, ledger_dir: str) -> list[dict]:
    """Every item across every ledger at `sha`, as
    {"proposal": N, "completion": 0-100, "tickets": [[id, done], ...]}.
    One `git show` per ledger file found at that commit."""
    items = []
    for name in _ledger_paths_at(repo, sha, ledger_dir):
        path = f"{ledger_dir}/{name}"
        try:
            text = _git(repo, "show", f"{sha}:{path}")
            data = json.loads(text)
        except (RuntimeError, ValueError):
            continue
        if not isinstance(data, dict) or not isinstance(data.get("items"), list):
            continue
        proposal = data.get("proposal")
        for item in data["items"]:
            if not isinstance(item, dict):
                continue
            items.append({
                "proposal": proposal,
                "completion": P.completion(item),
                "tickets": [[tid, done, status] for tid, done, status in _tickets(item)],
            })
    return items


def _summarize(items: list[dict]) -> dict:
    """items -> {tickets_total, tickets_done, completion_pct, by_proposal,
    ids_all, ids_done}. `ids_all`/`ids_done` are internal -- callers use them
    to diff against the previous day and strip them before the row is
    returned."""
    total = 0
    done = 0
    ids_all: set = set()
    ids_done: set = set()
    by_proposal: dict = {}
    by_status = {key: 0 for key in ("done", "in progress", "in review", "in testing", "blocked", "not started", "deferred")}
    for it in items:
        prop = str(it["proposal"])
        agg = by_proposal.setdefault(prop, {"tickets_total": 0, "tickets_done": 0})
        for tid, tdone, status in it["tickets"]:
            total += 1
            agg["tickets_total"] += 1
            by_status[status if status in by_status else "not started"] += 1
            if tid is not None:
                ids_all.add(tid)
            if tdone:
                done += 1
                agg["tickets_done"] += 1
                if tid is not None:
                    ids_done.add(tid)
    for agg in by_proposal.values():
        agg["completion_pct"] = round(100 * agg["tickets_done"] / agg["tickets_total"], 1) if agg["tickets_total"] else 0.0
    completion_pct = round(100 * done / total, 1) if total else 0.0
    return {
        "tickets_total": total, "tickets_done": done, "completion_pct": completion_pct,
        "by_proposal": by_proposal, "by_status": by_status,
        "ids_all": ids_all, "ids_done": ids_done,
    }


# -------------------------------------------------------------- cache -----

def _gitignores(root: Path, rel: str) -> bool:
    gitignore = root / ".gitignore"
    if not gitignore.is_file():
        return False
    for line in gitignore.read_text(errors="replace").splitlines():
        stripped = line.strip()
        if stripped in (rel, rel.rstrip("/"), rel.rstrip("/") + "/"):
            return True
    return False


def _cache_path(project: Path) -> Path:
    root = _repo_root(project)
    if _gitignores(root, ".cache/"):
        return root / ".cache" / "tracker-history.json"
    key = hashlib.sha256(str(root).encode()).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / "common-rules-tracker-history" / f"{key}.json"


def _load_cache(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def _save_cache(path: Path, cache: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, sort_keys=True))
    tmp.replace(path)


def _snapshot_for(repo: Path, sha: str, ledger_dir: str, cache: dict) -> list[dict]:
    cache_key = f"{ledger_dir}\x1f{sha}"
    cached = cache.get(cache_key)
    # The ticket tuple gained a status field for the stacked chart. Discard
    # pre-status cache entries instead of letting an old cache make the page
    # silently omit its graph.
    if cached is not None and all(
        len(ticket) == 3
        for item in cached
        for ticket in item.get("tickets", [])
    ):
        return cached
    snap = _snapshot_at(repo, sha, ledger_dir)
    cache[cache_key] = snap
    return snap


# ------------------------------------------------------------- series -----

def _as_date(value) -> datetime.date | None:
    if value is None:
        return None
    if isinstance(value, datetime.date):
        return value
    return datetime.date.fromisoformat(str(value).split("T", 1)[0])


def _as_floor(value) -> datetime.datetime | None:
    """`since` as a local moment. A date means its local midnight; an ISO
    timestamp names the hour a project's story starts (Loom, 2026-09-26:
    its ledgers were consolidated at 20:00 on 25 Sept, and a date floor
    left the hourly chart showing the old counts -- "clear this history
    from the graph"). A naive timestamp is read in TZ."""
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        when = value
    elif isinstance(value, datetime.date):
        return datetime.datetime.combine(value, datetime.time.min, tzinfo=TZ)
    elif "T" not in str(value):
        return datetime.datetime.combine(datetime.date.fromisoformat(str(value)), datetime.time.min, tzinfo=TZ)
    else:
        when = datetime.datetime.fromisoformat(str(value))
    return when.replace(tzinfo=TZ) if when.tzinfo is None else when.astimezone(TZ)


def series(project, since=None, granularity: str = "day") -> list[dict]:
    """Progress rows from the first ledger commit to now.

    The default is one row per calendar day. ``granularity="hour"`` keeps
    one row per local hour, preserving the same snapshot/carry-forward rules
    for a useful short-range zoom view.
    """
    if granularity not in {"day", "hour"}:
        raise ValueError("granularity must be 'day' or 'hour'")
    project = Path(project)
    repo = _repo_root(project)
    ledger_dir = _ledger_directory(project, repo)
    commits = _ledger_commits(repo, ledger_dir)
    if not commits:
        return []

    def bucket(when: datetime.datetime):
        if granularity == "hour":
            if isinstance(when, datetime.date) and not isinstance(when, datetime.datetime):
                return datetime.datetime.combine(when, datetime.time.min, tzinfo=TZ)
            return when.replace(minute=0, second=0, microsecond=0)
        return when if isinstance(when, datetime.date) and not isinstance(when, datetime.datetime) else when.date()

    last_sha_of_bucket = {}
    for sha, when in commits:
        last_sha_of_bucket[bucket(when)] = sha  # ascending order -> last write wins

    cache_path = _cache_path(project)
    cache = _load_cache(cache_path)
    dirty = False

    start_bucket = bucket(commits[0][1])
    now = datetime.datetime.now(TZ)
    end_bucket = bucket(now)
    since_at = _as_floor(since)
    if since_at is not None:
        start_bucket = max(start_bucket, bucket(since_at))

    # A zoom window commonly starts between commits. Seed its first bucket
    # with the latest snapshot at or before the requested start, then carry
    # that state forward until the next real commit.
    seed_sha = None
    for sha, when in commits:
        if bucket(when) <= start_bucket:
            seed_sha = sha
    if seed_sha is not None and start_bucket not in last_sha_of_bucket:
        last_sha_of_bucket[start_bucket] = seed_sha

    rows: list[dict] = []
    prev_ids_all: set = set()
    prev_ids_done: set = set()
    prev_total = 0
    last_summary: dict | None = None

    current = start_bucket
    step = datetime.timedelta(hours=1) if granularity == "hour" else datetime.timedelta(days=1)
    while current <= end_bucket:
        sha = last_sha_of_bucket.get(current)
        if sha is not None:
            cache_key = f"{ledger_dir}\x1f{sha}"
            if cache_key not in cache:
                dirty = True
            items = _snapshot_for(repo, sha, ledger_dir, cache)
            summary = _summarize(items)
            ids_all, ids_done = summary.pop("ids_all"), summary.pop("ids_done")
            added_ids = len(ids_all - prev_ids_all)
            closed_ids = len(ids_done - prev_ids_done)
            row = {
                "date": current.isoformat() if granularity == "hour" else current.isoformat(),
                "tickets_total": summary["tickets_total"],
                "tickets_done": summary["tickets_done"],
                "added": max(0, summary["tickets_total"] - prev_total),
                "closed": closed_ids,
                "added_ids": added_ids,
                "closed_ids": closed_ids,
                "completion_pct": summary["completion_pct"],
                "by_proposal": summary["by_proposal"],
                "by_status": summary["by_status"],
            }
            prev_ids_all, prev_ids_done = ids_all, ids_done
            prev_total = summary["tickets_total"]
            last_summary = row
        else:
            assert last_summary is not None  # start_day always has a commit
            row = dict(last_summary)
            row["date"] = current.isoformat()
            row["added"] = row["closed"] = row["added_ids"] = row["closed_ids"] = 0
        rows.append(row)
        current += step

    if dirty:
        _save_cache(cache_path, cache)

    # Rows begin at start_bucket, which is already at or after the floor.
    return rows


# ---------------------------------------------------------------- svg -----

def _esc(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


_SVG_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _short_date(value: str) -> str:
    if "T" in value:
        d = datetime.datetime.fromisoformat(value)
        return f"{d.day} {_SVG_MONTHS[d.month - 1]} {d.hour:02d}:00"
    d = datetime.date.fromisoformat(value)
    return f"{d.day} {_SVG_MONTHS[d.month - 1]}"


def _fmt_count(v: float) -> str:
    return f"{round(v):g}"


def _fmt_percent(v: float) -> str:
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return s + "%"


def _nice_ticks(lo: float, hi: float, n: int = 4) -> list[float]:
    """`n` evenly spaced ticks from `lo` to `hi` inclusive -- every one of
    them a value the line actually spans, never a padded or rounded axis
    the data never reaches. The sponsor's complaint about the old tracker
    was exactly this: "the percentage does not give me a right figure
    because 17%, I don't have the formula in my mind" -- a scaleless line
    repeats it."""
    if hi <= lo:
        return [lo]
    step = (hi - lo) / (n - 1)
    return [lo + step * i for i in range(n)]


def _x_tick_indexes(count: int, n: int = 4) -> list[int]:
    """Up to `n` row indexes, evenly spaced, always including the first and
    the last (P-08: "at minimum the first and last date")."""
    if count <= 0:
        return []
    if count == 1:
        return [0]
    n = max(2, min(n, count))
    seen: set = set()
    idxs = []
    for i in range(n):
        idx = round(i * (count - 1) / (n - 1))
        if idx not in seen:
            seen.add(idx)
            idxs.append(idx)
    return idxs


def _polyline(values: list[float], x, y) -> str:
    if not values:
        return ""
    return " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(values))


def _line_chart(width: int, height: int, series_list, dates: list[str], title: str, fmt) -> str:
    """One inline, responsive <svg> line chart: a title, a labelled y-axis
    (2-4 ticks with values the line actually reaches, plus a faint
    gridline each), a labelled x-axis (first date, last date, one or two
    between), a legend, and each line's own final value printed at its
    last point -- the number a reader actually reads (P-08). `width` /
    `height` size the viewBox; the element itself is `width="100%"` with a
    `preserveAspectRatio`, so it fills whatever card holds it rather than
    sitting in a fixed-size box with blank space around it. Colors --
    lines, axis text, gridlines, the title -- are all CSS custom
    properties with a fallback, so the chart follows the page's theme in
    light or dark mode, with no external stylesheet or script."""
    left, right, top, bottom = 42, 60, 40, 20
    plot_w = max(width - left - right, 1)
    plot_h = max(height - top - bottom, 1)

    all_values = [v for _, values, _ in series_list for v in values]
    lo, hi = (min(all_values), max(all_values)) if all_values else (0, 1)
    if hi == lo:
        hi = lo + 1
    n = max((len(values) for _, values, _ in series_list), default=0)
    span = max(n - 1, 1)

    def x(i):
        return left + plot_w * (i / span)

    def y(v):
        return top + plot_h - plot_h * ((v - lo) / (hi - lo))

    parts_svg = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" preserveAspectRatio="xMinYMin meet" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{_esc(title)}" '
        f'class="tracker-history-chart">',
        f'<title>{_esc(title)}</title>',
        f'<rect x="0" y="0" width="{width}" height="{height}" '
        f'fill="var(--tracker-chart-bg, transparent)"/>',
        f'<text x="{left}" y="14" font-size="12" font-weight="600" '
        f'fill="var(--tracker-chart-title, currentColor)">{_esc(title)}</text>',
    ]

    for tv in _nice_ticks(lo, hi, 4):
        ty = y(tv)
        parts_svg.append(
            f'<line x1="{left}" y1="{ty:.1f}" x2="{width - right}" y2="{ty:.1f}" '
            f'stroke="var(--tracker-chart-grid, currentColor)" stroke-opacity="0.15" stroke-width="1"/>')
        parts_svg.append(
            f'<text x="{left - 6}" y="{ty + 3:.1f}" font-size="10" text-anchor="end" '
            f'fill="var(--tracker-chart-axis, currentColor)" fill-opacity="0.75">{_esc(fmt(tv))}</text>')

    baseline_y = top + plot_h
    parts_svg.append(
        f'<line x1="{left}" y1="{baseline_y}" x2="{width - right}" y2="{baseline_y}" '
        f'stroke="var(--tracker-chart-axis, currentColor)" stroke-opacity="0.35" stroke-width="1"/>')
    for idx in _x_tick_indexes(len(dates)):
        tx = x(idx)
        anchor = "start" if idx == 0 else "end" if idx == n - 1 else "middle"
        parts_svg.append(
            f'<text x="{tx:.1f}" y="{height - 5}" font-size="10" text-anchor="{anchor}" '
            f'fill="var(--tracker-chart-axis, currentColor)" fill-opacity="0.75">'
            f'{_esc(_short_date(dates[idx]))}</text>')

    end_labels = []  # (label, lx, ly, color, text) -- placed after every
                      # polyline is drawn, then nudged apart so two series
                      # ending close together (P-14) don't print on top of
                      # each other.
    legend_x = left
    for label, values, color in series_list:
        points = _polyline(values, x, y)
        if points:
            parts_svg.append(
                f'<polyline points="{points}" fill="none" stroke="{color}" '
                f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round" '
                f'data-series="{_esc(label)}"/>')
            last_v = values[-1]
            lx, ly = x(len(values) - 1), y(last_v)
            parts_svg.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="2.5" fill="{color}"/>')
            end_labels.append([label, lx, ly, color, _esc(fmt(last_v))])
        parts_svg.append(
            f'<g transform="translate({legend_x},28)" data-legend="{_esc(label)}">'
            f'<rect x="0" y="-8" width="9" height="9" rx="2" fill="{color}"/>'
            f'<text x="13" y="0" font-size="10" '
            f'fill="var(--tracker-chart-axis, currentColor)">{_esc(label)}</text></g>')
        legend_x += 20 + 6 * len(label)

    for label, lx, ly, color, text in _spread_end_labels(end_labels, top, top + plot_h):
        parts_svg.append(
            f'<text x="{lx + 5:.1f}" y="{ly + 3:.1f}" font-size="11" font-weight="600" '
            f'fill="{color}" data-endlabel="{_esc(label)}">{text}</text>')

    parts_svg.append("</svg>")
    return "\n".join(parts_svg)


def _status_line_chart(width: int, height: int, rows: list[dict]) -> str:
    """Plot one line per status; separate lines keep status changes readable
    without the visual occlusion of a stacked area/bar chart."""
    keys = ("done", "in progress", "in review", "in testing", "blocked", "not started", "deferred")
    colors = {
        "done": "var(--tracker-status-done, #2FB170)",
        "in progress": "var(--tracker-status-progress, #D97706)",
        "in review": "var(--tracker-status-review, #8B5CF6)",
        "in testing": "var(--tracker-status-testing, #0891B2)",
        "blocked": "var(--tracker-status-blocked, #E05263)",
        "not started": "var(--tracker-status-todo, #64748B)",
        "deferred": "var(--tracker-status-deferred, #EAB308)",
    }
    dates = [r["date"] for r in rows]
    series = []
    for key in keys:
        values = [(r.get("by_status") or {}).get(key, 0) for r in rows]
        if any(values):
            series.append((key, values, colors[key]))
    return _line_chart(width, height, series, dates, "Tasks by status over time", _fmt_count)


def _spread_end_labels(end_labels, y_min, y_max, min_gap=14.0):
    """Nudge each end-of-line label's y away from its neighbours' when two
    series finish within `min_gap` px of each other (P-14: the engine's 73
    and 69 collided and became unreadable). Placement only -- every label
    stays beside its own point (x never moves) and inside [y_min, y_max];
    none is dropped.

    Sorted by y, each label is pushed down at least `min_gap` past the one
    above it; if that runs the last label past `y_max`, the whole sorted
    stack is shifted up just enough to fit back inside the plot area.
    """
    if len(end_labels) < 2:
        return end_labels
    ordered = sorted(end_labels, key=lambda e: e[2])
    prev_y = None
    for entry in ordered:
        y_val = entry[2]
        if prev_y is not None and y_val - prev_y < min_gap:
            y_val = prev_y + min_gap
        entry[2] = y_val
        prev_y = y_val
    overflow = ordered[-1][2] - y_max
    if overflow > 0:
        for entry in ordered:
            entry[2] -= overflow
    underflow = y_min - ordered[0][2]
    if underflow > 0:
        for entry in ordered:
            entry[2] += underflow
    return ordered


def svg(series_rows: list[dict], width: int = 640, height: int = 210) -> str:
    """Two inline SVG line charts: one line per non-empty ticket status,
    then the completion line. Counts and percentage stay separate units;
    each chart uses its own observed range.

    2026-09-26: the sponsor first asked to fix "multiple progress lines" and
    the status chart was removed; he then said "one graph is missing from
    the tracker", so both charts are back. What stays fixed: `deferred` no
    longer shares `done`'s green, so no two status lines look alike."""
    dates = [r["date"] for r in series_rows]
    completion = [r["completion_pct"] for r in series_rows]
    counts = _status_line_chart(width, height, series_rows)
    pct = _line_chart(
        width, height,
        [("completion", completion, "var(--tracker-line-completion, #B15EFF)")],
        dates, title="Completion over time", fmt=_fmt_percent)
    return counts + "\n" + pct


# ---------------------------------------------------------------- CLI -----

def main(argv) -> int:
    ap = argparse.ArgumentParser(prog="tracker history", add_help=True)
    ap.add_argument("--project", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--since")
    args = ap.parse_args(argv)

    try:
        rows = series(Path(args.project), since=args.since)
    except RuntimeError as exc:
        print(f"tracker history: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(rows, indent=2))
        return 0

    if not rows:
        print("tracker history: no ledger commits found")
        return 0

    print(f"{'date':10}  {'total':>5}  {'done':>5}  {'added':>5}  {'closed':>6}  {'compl%':>7}")
    for r in rows:
        print(f"{r['date']:10}  {r['tickets_total']:5d}  {r['tickets_done']:5d}  "
              f"{r['added']:5d}  {r['closed']:6d}  {r['completion_pct']:7.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
