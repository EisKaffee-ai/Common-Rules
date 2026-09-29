"""`tracker history` -- progress over time, from the ledgers' own git
history, no AI updates (proposal 30, P-07).

The sponsor asked for a graph of tickets finished, tickets added, and the
degree of completion over time, computed automatically in the background,
never hand-edited by AI. These tests build a small throwaway git repo,
commit ledgers on backdated days (some days get no commit at all, to check
carry-forward), and pin: daily counts, added/closed (including a same-day
add-and-close, which a plain before/after total would hide), carry-forward
on days without a commit, nested parts counted as their own tickets, cache
reuse (a rerun re-reads no ledger already seen), and that the SVG helper
renders two charts with no external URLs.

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.tracker import history  # noqa: E402

TRACKER = ROOT / "bin" / "tracker"


def _iso(day: datetime.date, hour: int = 10) -> str:
    return f"{day.isoformat()}T{hour:02d}:00:00+01:00"


class Repo:
    """A throwaway git repo with ledgers committed on chosen days."""

    def __init__(self, root: Path):
        self.root = root
        (root / "docs" / "proposals").mkdir(parents=True)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        (root / "README.md").write_text("seed\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "seed")

    def git(self, *args, env=None):
        return subprocess.run(["git", "-C", str(self.root), *args],
                              capture_output=True, text=True, check=True, env=env)

    def commit_ledger(self, name: str, data: dict, day: datetime.date, hour: int = 10):
        path = self.root / "docs" / "proposals" / name
        path.write_text(json.dumps(data, indent=2) + "\n")
        self.git("add", "-A")
        env = dict(os.environ)
        when = _iso(day, hour)
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
        self.git("commit", "-qm", f"update {name}", env=env)


def item(iid, status, parts=None, **extra):
    row = {"id": iid, "phase": "W", "cx": "C2", "title": iid, "status": status}
    if parts is not None:
        row["parts"] = parts
    row.update(extra)
    return row


def ledger19(items):
    return {"proposal": 19, "title": "Warm-up", "status": "accepted", "updated": "2026-09-14",
            "items": list(items)}


class TestHistorySeries(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Repo(Path(self._tmp.name) / "proj")

        today = datetime.datetime.now(history.TZ).date()
        self.day_a = today - datetime.timedelta(days=4)
        self.day_b = self.day_a + datetime.timedelta(days=1)
        self.day_c = self.day_a + datetime.timedelta(days=2)  # no commit
        self.day_d = self.day_a + datetime.timedelta(days=3)
        self.today = today

        # Day A: two items, one done, one not.
        self.repo.commit_ledger("19-warmup.json", ledger19([
            item("W-01", "done"),
            item("W-02", "not started"),
        ]), self.day_a)

        # Day B: W-02 closes, W-03 is added and already done (same-day
        # add-and-close for W-03 would need its own day -- here it just
        # exercises `added`).
        self.repo.commit_ledger("19-warmup.json", ledger19([
            item("W-01", "done"),
            item("W-02", "done"),
            item("W-03", "not started"),
        ]), self.day_b, hour=15)

        # Day C: no commit at all -- must carry Day B forward.

        # Day D: W-04 arrives with nested parts -- itself plus A, B, B.1,
        # B.2 all count as tickets; A and B.1 are done.
        self.repo.commit_ledger("19-warmup.json", ledger19([
            item("W-01", "done"),
            item("W-02", "done"),
            item("W-03", "not started"),
            item("W-04", "in progress", parts=[
                {"id": "W-04.A", "title": "A", "share": 50, "status": "done"},
                {"id": "W-04.B", "title": "B", "share": 50, "status": "in progress", "parts": [
                    {"id": "W-04.B.1", "title": "B1", "share": 50, "status": "done"},
                    {"id": "W-04.B.2", "title": "B2", "share": 50, "status": "not started"},
                ]},
            ]),
        ]), self.day_d, hour=17)

    def by_date(self, rows):
        return {r["date"]: r for r in rows}

    def test_one_row_per_calendar_day_from_first_commit_to_today(self):
        rows = history.series(self.repo.root)
        expected_days = (self.today - self.day_a).days + 1
        self.assertEqual(len(rows), expected_days)
        self.assertEqual(rows[0]["date"], self.day_a.isoformat())
        self.assertEqual(rows[-1]["date"], self.today.isoformat())

    def test_day_a_counts(self):
        rows = self.by_date(history.series(self.repo.root))
        r = rows[self.day_a.isoformat()]
        self.assertEqual(r["tickets_total"], 2)
        self.assertEqual(r["tickets_done"], 1)

    def test_day_b_added_and_closed(self):
        rows = self.by_date(history.series(self.repo.root))
        r = rows[self.day_b.isoformat()]
        self.assertEqual(r["tickets_total"], 3)
        self.assertEqual(r["tickets_done"], 2)
        self.assertEqual(r["added"], 1)          # 3 - 2
        self.assertEqual(r["added_ids"], 1)      # W-03
        self.assertEqual(r["closed"], 1)         # W-02 became done
        self.assertEqual(r["closed_ids"], 1)

    def test_day_c_carries_day_b_forward(self):
        rows = self.by_date(history.series(self.repo.root))
        b, c = rows[self.day_b.isoformat()], rows[self.day_c.isoformat()]
        self.assertEqual(c["tickets_total"], b["tickets_total"])
        self.assertEqual(c["tickets_done"], b["tickets_done"])
        self.assertEqual(c["completion_pct"], b["completion_pct"])
        self.assertEqual(c["added"], 0)
        self.assertEqual(c["closed"], 0)

    def test_day_d_counts_nested_parts_as_tickets(self):
        rows = self.by_date(history.series(self.repo.root))
        r = rows[self.day_d.isoformat()]
        # W-01, W-02, W-03 (3 tickets, 2 done) + W-04, .A, .B, .B.1, .B.2
        # (5 tickets, 2 done: .A and .B.1) = 8 tickets, 4 done.
        self.assertEqual(r["tickets_total"], 8)
        self.assertEqual(r["tickets_done"], 4)
        self.assertEqual(r["added_ids"], 5)
        self.assertEqual(r["closed_ids"], 2)

    def test_day_d_completion_pct_uses_the_same_ticket_denominator_as_statuses(self):
        rows = self.by_date(history.series(self.repo.root))
        r = rows[self.day_d.isoformat()]
        # Four of the eight tracked tickets are done. The percentage must use
        # this same denominator as the status history, not an average of the
        # four top-level item completion values.
        self.assertAlmostEqual(r["completion_pct"], 50.0)

    def test_by_proposal_matches_overall_when_theres_one_proposal(self):
        rows = self.by_date(history.series(self.repo.root))
        r = rows[self.day_d.isoformat()]
        self.assertIn("19", r["by_proposal"])
        bp = r["by_proposal"]["19"]
        self.assertEqual(bp["tickets_total"], r["tickets_total"])
        self.assertEqual(bp["tickets_done"], r["tickets_done"])
        self.assertAlmostEqual(bp["completion_pct"], r["completion_pct"])

    def test_since_filters_rows(self):
        rows = history.series(self.repo.root, since=self.day_d.isoformat())
        self.assertTrue(all(r["date"] >= self.day_d.isoformat() for r in rows))
        self.assertEqual(rows[0]["date"], self.day_d.isoformat())

    def test_hourly_zoom_returns_hour_buckets_and_carries_snapshots(self):
        rows = history.series(self.repo.root, since=self.day_a.isoformat(), granularity="hour")
        self.assertTrue(rows)
        self.assertTrue(all("T" in row["date"] for row in rows))
        self.assertEqual(rows[0]["date"], f"{self.day_a.isoformat()}T10:00:00+01:00")
        day_b_before = next(row for row in rows if row["date"] == f"{self.day_b.isoformat()}T14:00:00+01:00")
        day_b_at_commit = next(row for row in rows if row["date"] == f"{self.day_b.isoformat()}T15:00:00+01:00")
        self.assertEqual(day_b_before["tickets_total"], 2)
        self.assertEqual(day_b_at_commit["tickets_total"], 3)
        day_d = next(row for row in rows if row["date"] == f"{self.day_d.isoformat()}T17:00:00+01:00")
        self.assertEqual(day_d["tickets_total"], 8)
        self.assertEqual(day_d["by_status"]["done"], 4)

    def test_a_timestamp_floor_starts_the_hourly_chart_at_that_hour(self):
        """history_since may name an hour (Loom, 2026-09-26: "clear this
        history from the graph" -- a date floor left the old counts showing
        on the hourly chart)."""
        floor = f"{self.day_b.isoformat()}T15:00:00+01:00"
        rows = history.series(self.repo.root, since=floor, granularity="hour")
        self.assertEqual(rows[0]["date"], floor)
        self.assertEqual(rows[0]["tickets_total"], 3)
        self.assertTrue(all(r["tickets_total"] >= 3 for r in rows))

    def test_a_timestamp_floor_starts_the_daily_chart_on_its_day(self):
        rows = history.series(self.repo.root, since=f"{self.day_b.isoformat()}T15:00:00+01:00")
        self.assertEqual(rows[0]["date"], self.day_b.isoformat())

    def test_a_naive_timestamp_floor_is_read_in_local_time(self):
        rows = history.series(self.repo.root, since=f"{self.day_b.isoformat()}T15:00", granularity="hour")
        self.assertEqual(rows[0]["date"], f"{self.day_b.isoformat()}T15:00:00+01:00")

    def test_cache_reuse_reads_no_git_show_for_old_shas(self):
        history.series(self.repo.root)  # populates the cache

        calls = []
        real_git = history._git

        def counting_git(repo, *args):
            calls.append(args)
            return real_git(repo, *args)

        history._git = counting_git
        try:
            history.series(self.repo.root)
        finally:
            history._git = real_git

        show_calls = [a for a in calls if a and a[0] == "show"]
        self.assertEqual(show_calls, [], f"expected no `git show` on a cached rerun, got {show_calls}")

    def test_cache_file_is_written_and_not_inside_the_repo_unless_ignored(self):
        history.series(self.repo.root)
        cache_path = history._cache_path(self.repo.root)
        self.assertTrue(cache_path.is_file())
        # This throwaway repo's .gitignore (it has none) does not ignore
        # .cache/, so the cache must land outside the repo entirely.
        self.assertFalse(str(cache_path).startswith(str(self.repo.root)))

    def test_cli_table(self):
        r = subprocess.run([sys.executable, str(TRACKER), "history", "--project", str(self.repo.root)],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(self.day_a.isoformat(), r.stdout)
        self.assertIn(self.today.isoformat(), r.stdout)

    def test_cli_json(self):
        r = subprocess.run([sys.executable, str(TRACKER), "history", "--project", str(self.repo.root), "--json"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data[0]["date"], self.day_a.isoformat())


class TestHistorySvg(unittest.TestCase):
    def test_two_charts_no_external_urls(self):
        rows = [
            {"date": "2026-09-01", "tickets_total": 2, "tickets_done": 1, "completion_pct": 50.0,
             "added": 2, "closed": 0, "added_ids": 2, "closed_ids": 0, "by_proposal": {},
             "by_status": {"done": 1, "not started": 1}},
            {"date": "2026-09-02", "tickets_total": 3, "tickets_done": 2, "completion_pct": 66.7,
             "added": 1, "closed": 1, "added_ids": 1, "closed_ids": 1, "by_proposal": {},
             "by_status": {"done": 2, "not started": 1}},
        ]
        out = history.svg(rows)
        self.assertEqual(out.count("<svg"), 2)
        self.assertEqual(out.count("</svg>"), 2)
        # No fetched resource: no <script>, and the only URL allowed is the
        # SVG xmlns declaration itself (a namespace, not a network fetch).
        self.assertNotIn("<script", out)
        self.assertNotIn("href=", out)
        self.assertNotIn('src="http', out)
        non_xmlns_urls = [line for line in out.splitlines()
                          if ("http://" in line or "https://" in line) and "xmlns=" not in line]
        self.assertEqual(non_xmlns_urls, [])
        self.assertIn("var(--tracker-status-done", out)
        self.assertIn("var(--tracker-status-todo", out)
        self.assertIn("var(--tracker-line-completion", out)

    def test_empty_series_still_renders_two_empty_charts(self):
        out = history.svg([])
        self.assertEqual(out.count("<svg"), 2)
        self.assertNotIn("polyline", out)


def _rows_for_chart_content():
    """Five days of a spread-out series, so the axes have real ticks to
    check and the first/last dates differ (proposal 30, P-08 round 2 --
    the sponsor's "17%, I don't have the formula in my mind" complaint,
    repeated by a scaleless line)."""
    dates = ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-05"]
    totals = [2, 3, 4, 5, 6]
    dones = [1, 1, 2, 3, 5]
    completion = [10.0, 20.0, 40.0, 70.0, 90.0]
    return [
        {"date": d, "tickets_total": t, "tickets_done": dn, "completion_pct": c,
         "added": 0, "closed": 0, "added_ids": 0, "closed_ids": 0, "by_proposal": {},
         "by_status": {"done": dn, "not started": t - dn}}
        for d, t, dn, c in zip(dates, totals, dones, completion)
    ]


class TestHistorySvgContent(unittest.TestCase):
    """P-08 round 2 (the coordinator's own review of the first chart
    render): a labelled y-axis, a labelled x-axis, a legend, an
    end-of-line value per series, a visible title, and a responsive
    (width=100% + viewBox) svg -- on both the counts chart and the
    completion chart."""

    def setUp(self):
        self.rows = _rows_for_chart_content()
        self.out = history.svg(self.rows)
        self.counts, self.pct = self.out.split("</svg>", 1)

    def test_responsive_viewbox(self):
        self.assertEqual(self.out.count('width="100%"'), 2)
        self.assertEqual(self.out.count("viewBox="), 2)

    def test_visible_titles(self):
        self.assertIn(">Tasks by status over time<", self.out)
        self.assertIn(">Completion over time<", self.out)

    def test_y_axis_ticks_are_values_the_line_actually_reaches(self):
        # The status lines span their own observed values: one through five.
        for tv in history._nice_ticks(1, 5, 4):
            self.assertIn(f">{history._fmt_count(tv)}<", self.counts)
        # The completion chart spans its own data: 10..90, never a fixed
        # 0-100 the line rarely reaches.
        for tv in history._nice_ticks(10.0, 90.0, 4):
            self.assertIn(f">{history._fmt_percent(tv)}<", self.pct)

    def test_x_axis_shows_first_and_last_date_not_iso(self):
        self.assertIn(">1 Sep<", self.counts)
        self.assertIn(">5 Sep<", self.counts)
        self.assertNotIn("2026-09-01", self.out)
        self.assertNotIn("2026-09-05", self.out)

    def test_legend_has_an_entry_per_series(self):
        self.assertIn('data-legend="done"', self.counts)
        self.assertIn('data-legend="not started"', self.counts)
        self.assertIn('data-legend="completion"', self.pct)

    def test_end_of_line_labels_carry_the_final_value(self):
        self.assertIn('data-endlabel="done">5<', self.counts)
        self.assertIn('data-endlabel="not started">1<', self.counts)
        self.assertIn('data-endlabel="completion">90%<', self.pct)

    def test_gridlines_and_axis_text_use_theme_tokens(self):
        self.assertIn("var(--tracker-chart-axis", self.out)
        self.assertIn("var(--tracker-chart-grid", self.out)
        self.assertIn("var(--tracker-chart-title", self.out)

    def test_charts_stay_separate(self):
        self.assertEqual(self.out.count("<svg"), 2)

    def test_no_external_urls_or_script_still_holds(self):
        self.assertNotIn("<script", self.out)
        self.assertNotIn("href=", self.out)
        self.assertNotIn('src="http', self.out)
        non_xmlns_urls = [line for line in self.out.splitlines()
                          if ("http://" in line or "https://" in line) and "xmlns=" not in line]
        self.assertEqual(non_xmlns_urls, [])


def _end_label_positions(out: str) -> dict:
    """{series label: y} for every `data-endlabel` <text> in one chart's
    markup, parsed straight from the attributes -- no regex on the visible
    number, since P-08's own tests already pin that separately."""
    positions = {}
    for m in re.finditer(r'<text x="[\d.]+" y="([\d.]+)"[^>]*data-endlabel="([^"]+)">', out):
        y, label = m.groups()
        positions[label] = float(y)
    return positions


class TestEndOfLineLabelsDoNotCollide(unittest.TestCase):
    """P-14: on PhotoVault/engine's own page the `total` and `done` lines
    ended at 72 and 69 -- close enough, out of a 0-72 range, that their
    end-of-line value labels printed on top of each other and both became
    unreadable. The fix is placement (nudge apart, keep each beside its own
    line), never dropping a label -- pinned here on the labels' own computed
    y positions, not on rendered pixels."""

    def test_close_final_values_are_pushed_apart(self):
        dates = ["2026-09-01", "2026-09-02", "2026-09-03"]
        series_list = [
            ("total", [0.0, 50.0, 72.0], "blue"),
            ("done", [0.0, 40.0, 69.0], "green"),
        ]
        out = history._line_chart(640, 210, series_list, dates, "Tickets", history._fmt_count)
        positions = _end_label_positions(out)
        self.assertEqual(set(positions), {"total", "done"})
        self.assertGreaterEqual(abs(positions["total"] - positions["done"]), 14.0)

    def test_neither_label_is_dropped_and_each_keeps_its_own_value(self):
        dates = ["2026-09-01", "2026-09-02", "2026-09-03"]
        series_list = [
            ("total", [0.0, 50.0, 72.0], "blue"),
            ("done", [0.0, 40.0, 69.0], "green"),
        ]
        out = history._line_chart(640, 210, series_list, dates, "Tickets", history._fmt_count)
        self.assertIn('data-endlabel="total">72<', out)
        self.assertIn('data-endlabel="done">69<', out)

    def test_far_apart_final_values_are_left_where_they_land(self):
        dates = ["2026-09-01", "2026-09-02", "2026-09-03"]
        series_list = [
            ("total", [0.0, 50.0, 100.0], "blue"),
            ("done", [0.0, 5.0, 5.0], "green"),
        ]
        out = history._line_chart(640, 210, series_list, dates, "Tickets", history._fmt_count)
        positions = _end_label_positions(out)
        # top=40, plot_h=150, range 0-100 -- "total" ends at the very top of
        # the plot (point y=40) and "done" close to the bottom (point
        # y=182.5), each label offset +3 below its own point: nothing to
        # spread apart, so each sits exactly beside its own line.
        self.assertAlmostEqual(positions["total"], 43.0, places=1)
        self.assertAlmostEqual(positions["done"], 185.5, places=1)

    def test_three_series_ending_close_together_are_all_spread_out(self):
        dates = ["2026-09-01", "2026-09-02"]
        series_list = [
            ("a", [0.0, 50.0], "red"),
            ("b", [0.0, 51.0], "green"),
            ("c", [0.0, 52.0], "blue"),
        ]
        out = history._line_chart(640, 210, series_list, dates, "X", history._fmt_count)
        positions = _end_label_positions(out)
        self.assertEqual(set(positions), {"a", "b", "c"})
        ys = sorted(positions.values())
        self.assertGreaterEqual(ys[1] - ys[0], 14.0)
        self.assertGreaterEqual(ys[2] - ys[1], 14.0)
        # still inside the plot area (top=40, bottom edge = 40+150=190),
        # each label's own +3 y-offset from its point included
        for y in ys:
            self.assertGreaterEqual(y, 40.0)
            self.assertLessEqual(y, 193.0)


class TestSpreadEndLabelsHelper(unittest.TestCase):
    """Unit-level coverage of `_spread_end_labels` itself, isolated from
    SVG rendering -- the placement rule P-14 actually asked for."""

    def test_a_single_label_is_returned_unchanged(self):
        labels = [["a", 500.0, 50.0, "red", "5"]]
        self.assertEqual(history._spread_end_labels(labels, 0.0, 100.0), labels)

    def test_labels_already_far_apart_are_untouched(self):
        labels = [["a", 500.0, 20.0, "red", "1"], ["b", 500.0, 90.0, "blue", "2"]]
        out = history._spread_end_labels([list(e) for e in labels], 0.0, 100.0)
        self.assertEqual(sorted(e[2] for e in out), [20.0, 90.0])

    def test_colliding_labels_end_at_least_min_gap_apart(self):
        labels = [["a", 500.0, 50.0, "red", "1"], ["b", 500.0, 52.0, "blue", "2"]]
        out = history._spread_end_labels([list(e) for e in labels], 0.0, 100.0, min_gap=14.0)
        ys = sorted(e[2] for e in out)
        self.assertGreaterEqual(ys[1] - ys[0], 14.0)

    def test_pushed_stack_stays_inside_the_plot_bounds(self):
        labels = [["a", 1.0, 92.0, "x", "1"], ["b", 1.0, 94.0, "y", "2"], ["c", 1.0, 96.0, "z", "3"]]
        out = history._spread_end_labels([list(e) for e in labels], 0.0, 100.0, min_gap=14.0)
        for e in out:
            self.assertGreaterEqual(e[2], 0.0)
            self.assertLessEqual(e[2], 100.0)

    def test_x_is_never_touched_only_y(self):
        labels = [["a", 12.0, 50.0, "x", "1"], ["b", 34.0, 51.0, "y", "2"]]
        out = history._spread_end_labels([list(e) for e in labels], 0.0, 100.0)
        xs = {e[0]: e[1] for e in out}
        self.assertEqual(xs, {"a": 12.0, "b": 34.0})


if __name__ == "__main__":
    unittest.main()
