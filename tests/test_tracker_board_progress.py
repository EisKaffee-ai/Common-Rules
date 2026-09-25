"""`tracker board`'s Progress charts and Features drill-down (proposal 30,
P-08).

The sponsor asked for "a tracker which should plot a graph over time of how
many tickets are getting finished, how many tickets are added" -- computed
automatically, never hand-updated by AI (P-07, tools/tracker/history.py) --
and, separately, "a feature level graph where I can drop down and it can show
me what sub action items and action items are there ... once I expand the
drop down then it can show me what sub items are there and if there are more
sub sub items".

These tests pin:
  * the Progress block appears when the project has ledger-touching git
    history, and is quietly omitted when it does not (no git repo at all, or
    series() raising);
  * the Features block has one row per proposal, with a completion % and a
    done/total item count;
  * every row is collapsed by default (`<details>` with no bare `open`);
  * nested expansion reaches three depths (item -> part -> sub-part), using
    parts.tree()'s own recursion;
  * the markup is correct with the page's inline <script> never having run.

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import datetime
import json
import re
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.tracker import board  # noqa: E402
from tools.tracker import parts as PARTS  # noqa: E402


def ledger(number, items, title="a proposal"):
    return {"proposal": number, "title": title, "status": "accepted", "updated": "2026-09-17",
            "phases": [{"id": "W", "name": "Build", "goal": "g", "exit": "e"}],
            "items": items, "asks": []}


def part(pid, title, share, status, **extra):
    row = {"id": pid, "title": title, "share": share, "status": status}
    row.update(extra)
    return row


def item(iid, status="not started", title=None, parts=None, **extra):
    row = {"id": iid, "phase": "W", "cx": "C2", "title": title or iid, "status": status,
           "tier": "medium", "model": "sonnet", "tag": "[ruflo]", "issue": None}
    if parts is not None:
        row["parts"] = parts
    row.update(extra)
    return row


def write(root: Path, number, data) -> Path:
    path = root / f"{number}-x.json"
    path.write_text(json.dumps(data))
    return path


class Repo:
    """A throwaway git repo with a ledger committed on a chosen day --
    same shape as test_tracker_history.py's helper, kept local here since
    this file must not import or edit tools/tracker/history.py's own tests."""

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

    def commit_ledger(self, name: str, data: dict, day: datetime.date):
        path = self.root / "docs" / "proposals" / name
        path.write_text(json.dumps(data, indent=2) + "\n")
        self.git("add", "-A")
        env = dict(os.environ)
        when = f"{day.isoformat()}T10:00:00+01:00"
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
        self.git("commit", "-qm", f"update {name}", env=env)


class ProgressChartsCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_charts_present_with_git_history(self):
        repo = Repo(self.root / "proj")
        repo.commit_ledger("30-x.json", ledger(30, [item("A-01", status="done")]), datetime.date.today())
        led = ledger(30, [item("A-01", status="done")])
        path = repo.root / "docs" / "proposals" / "30-x.json"
        text = board.render([(path, led)], "demo", None, repo.root)
        self.assertIn('<section class="progress" id="progress">', text)
        self.assertEqual(text.count("<svg"), 4)  # daily + hourly, two charts each
        self.assertIn("Progress over time", text)
        self.assertIn("1 of 1 nested tasks done · 100.0% overall", text)

    def test_top_summary_uses_the_same_nested_task_counts_as_the_graph(self):
        repo = Repo(self.root / "proj")
        data = ledger(30, [item("A-01", status="in progress", parts=[
            part("A-01.A", "done child", 50, "done"),
            part("A-01.B", "open child", 50, "not started"),
        ])])
        repo.commit_ledger("30-x.json", data, datetime.date.today())
        path = repo.root / "docs" / "proposals" / "30-x.json"
        text = board.render([(path, data)], "demo", None, repo.root)
        self.assertIn("3 tracked tasks", text)
        self.assertIn("1 done / 1 in progress / 0 blocked / 1 not started", text)
        self.assertIn("1 of 3 nested tasks done · 33.3% overall", text)

    def test_charts_omitted_without_git_history(self):
        # self.root is a plain directory, never `git init`-ed -- history.series()
        # raises, and the block must be omitted quietly, not crash the page.
        (self.root / "docs" / "proposals").mkdir(parents=True)
        led = ledger(30, [item("A-01")])
        path = write(self.root / "docs" / "proposals", 30, led)
        text = board.render([(path, led)], "demo", None, self.root)
        self.assertNotIn('id="progress"', text)
        self.assertNotIn("tracker-history-chart", text)

    def test_charts_omitted_when_project_is_none(self):
        led = ledger(30, [item("A-01")])
        path = write(self.root, 30, led)
        text = board.render([(path, led)], "demo", None, None)
        self.assertNotIn('id="progress"', text)

    def test_progress_history_sits_before_priority_groups(self):
        repo = Repo(self.root / "proj")
        repo.commit_ledger("30-x.json", ledger(30, [item("A-01", status="done")]), datetime.date.today())
        led = ledger(30, [item("A-01", status="done")])
        path = repo.root / "docs" / "proposals" / "30-x.json"
        text = board.render([(path, led)], "demo", None, repo.root)
        progress_at = text.index('<section class="progress"')
        groups_at = text.index('<section class="cgroup"')
        self.assertTrue(progress_at < groups_at)

    def test_progress_history_sits_before_the_proposal_tree(self):
        # Sponsor correction, 2026-09-18: the history is a top-level reading
        # aid, before the proposal tree, with the actionable queue below it.
        repo = Repo(self.root / "proj")
        repo.commit_ledger("30-x.json", ledger(30, [item("A-01", status="done")]), datetime.date.today())
        led = ledger(30, [item("A-01", status="done")])
        path = repo.root / "docs" / "proposals" / "30-x.json"
        text = board.render([(path, led)], "demo", None, repo.root)
        features_at = text.index('<section class="features"')
        progress_at = text.index('<section class="progress"')
        groups_at = text.index('<details class="cgroups" id="cgroups">')
        self.assertTrue(progress_at < features_at < groups_at)

    def test_chart_height_is_capped_regardless_of_page_width(self):
        # Sponsor correction, 2026-09-18: "the container is stretching them"
        # -- a shorter viewBox height, plus a max-width on the charts'
        # column, keep each chart to roughly 180px of real height without
        # touching any axis label's font-size (all fixed px values in
        # tools/tracker/history.py, untouched here).
        #
        # P-14: a flat 760px left half of a 1400px page empty. The cap is
        # now a sensible upper bound that still grows with the page
        # ("min(100%,1040px)"), not a hard 760 -- still a cap, so the chart
        # cannot stretch unboundedly tall either.
        repo = Repo(self.root / "proj")
        repo.commit_ledger("30-x.json", ledger(30, [item("A-01", status="done")]), datetime.date.today())
        led = ledger(30, [item("A-01", status="done")])
        path = repo.root / "docs" / "proposals" / "30-x.json"
        text = board.render([(path, led)], "demo", None, repo.root)
        self.assertIn('viewBox="0 0 640 150"', text)
        self.assertIn('max-width:min(100%,1040px)', text)
        self.assertNotIn('max-width:760px', text)
        self.assertIn('font-size="12"', text)  # the title -- unchanged
        self.assertIn('font-size="10"', text)  # axis ticks -- unchanged


class FeaturesDrilldownCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def render(self, items, number=30, title="a proposal"):
        led = ledger(number, items, title=title)
        path = write(self.root, number, led)
        return board.render([(path, led)], "demo", None, self.root)

    def test_the_block_heading_says_proposals_not_features(self):
        # Sponsor correction, 2026-09-18: "feature" named two different
        # things on the page (the tile's item count, and this block's
        # proposal rows). The class/id stay "features" (CSS, tests elsewhere
        # pin it) but the visible heading uses the ledger's own word.
        text = self.render([item("A-01")])
        self.assertIn('<section class="features" id="features"><h2>Proposals</h2>', text)
        self.assertNotIn('<h2>Features</h2>', text)

    def test_one_row_per_proposal_with_number_title_and_completion(self):
        text = self.render([item("A-01", status="done"), item("A-02", status="not started")], title="Widgets")
        self.assertIn('<section class="features" id="features">', text)
        self.assertIn('<details class="feature-row" data-proposal="30">', text)
        self.assertIn('<span class="fpn">P30</span>', text)
        self.assertIn('<span class="fptitle" title="Widgets">Widgets</span>', text)
        # A-01 is 100% (done, no parts), A-02 is 0% -- average 50%.
        self.assertIn('<span class="fppct">50.0%</span>', text)
        self.assertIn('<span class="fpcount">1/2 tasks done</span>', text)

    def test_feature_row_collapsed_by_default(self):
        text = self.render([item("A-01")])
        self.assertNotRegex(text, r'<details class="feature-row"[^>]*\bopen\b')
        self.assertNotRegex(text, r'<details class="item-row"[^>]*\bopen\b')

    def test_explains_item_and_nested_task_denominators(self):
        text = self.render([item("A-01")])
        self.assertIn("All proposal totals and percentages count nested tasks", text)
        self.assertIn("All proposal totals and percentages count nested tasks", text)

    def test_item_row_shows_completion_bar_group_and_next_part(self):
        text = self.render([
            item("A-01", parts=[part("A-01.A", "first", 60, "done"), part("A-01.B", "second", 40, "in progress")]),
        ])
        self.assertIn('<details class="item-row" data-item data-id="A-01" data-proposal="30" '
                      'data-status="not started" data-owner="" data-tier="medium" data-group="finish now"', text)
        self.assertIn('<span class="ipct">60%</span>', text)
        self.assertIn("next: A-01.B", text)
        self.assertIn('class="pill group-pill g-s-finish-now"', text)
        self.assertIn('class="pill status-pill s-not-started"', text)

    def test_item_without_parts_shows_one_implicit_part(self):
        text = self.render([item("I-01", status="in progress", title="no parts yet")])
        # Inside the features block (after the Features heading), the implicit
        # part row for I-01 carries a 100% share, same convention as the
        # completion overview above.
        block = text.split('<section class="features"', 1)[1]
        self.assertIn('<span class="pid">I-01</span>', block)
        self.assertIn('<span class="pshare">100%</span>', block)

    def test_nested_expansion_reaches_three_depths(self):
        text = self.render([
            item("W-10", status="in progress", parts=[
                part("W-10.A", "first half", 50, "done"),
                part("W-10.B", "second half", 50, "in progress", parts=[
                    part("W-10.B.1", "b sub 1", 50, "done"),
                    part("W-10.B.2", "b sub 2", 50, "in progress", parts=[
                        part("W-10.B.2.a", "b.2 leaf a", 50, "done"),
                        part("W-10.B.2.b", "b.2 leaf b", 50, "not started"),
                    ]),
                ]),
            ]),
        ])
        for pid in ("W-10.A", "W-10.B", "W-10.B.1", "W-10.B.2", "W-10.B.2.a", "W-10.B.2.b"):
            self.assertIn(f'<span class="pid">{pid}</span>', text)
        # A part with sub-parts is itself a <details> that expands further.
        self.assertIn('<details class="prow-details">', text)
        # None of the nested <details> is open by default.
        self.assertNotRegex(text, r'<details class="prow-details"[^>]*\bopen\b')

    def test_counts_done_items_by_group_not_raw_status(self):
        # A-01 is "done" outright; A-02 has all its parts done (group "done")
        # even though its own top-level status is "in progress" -- the same
        # rule the completion overview already uses (parts.group()).
        text = self.render([
            item("A-01", status="done"),
            item("A-02", status="in progress", parts=[part("A-02.A", "a", 100, "done")]),
            item("A-03", status="not started"),
        ])
        self.assertIn('<span class="fpcount">2/4 tasks done</span>', text)

    def test_no_javascript_required(self):
        text = self.render([
            item("A-01", parts=[part("A-01.A", "a", 100, "done")]),
            item("A-02", status="done"),
        ])
        body = text.split("<script>", 1)[0]
        self.assertIn('<section class="features"', body)
        self.assertIn('<span class="fpn">P30</span>', body)
        self.assertIn('<span class="pid">A-01.A</span>', body)

    def test_omitted_when_there_are_no_ledgers(self):
        self.assertEqual(board.features_section([]), "")

    def test_a_long_title_carries_a_title_attribute_and_is_not_truncated_in_python(self):
        # proposal 30, P-09: a title long enough to break the row's layout is
        # clamped in CSS, never cut down in Python -- the full text is still
        # in the markup, both as the row's own text and in a `title` attr.
        long_title = "x" * 400
        text = self.render([item("Q-02", status="done", title=long_title)])
        self.assertIn(f'title="{long_title}"', text)
        self.assertIn(f'>{long_title}<', text)


class KanbanCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def render(self, items, number=30, title="a proposal"):
        led = ledger(number, items, title=title)
        path = write(self.root, number, led)
        return board.render([(path, led)], "demo", None, self.root)

    def test_tree_and_kanban_buttons_exist_and_tree_is_the_default(self):
        # proposal 30, P-11: one group of four view buttons -- Tree, Kanban,
        # Board, List -- Tree pressed by default, in the one filter bar at
        # the top of the page.
        text = self.render([item("A-01")])
        self.assertIn('<button type="button" data-view="tree" aria-pressed="true">Tree</button>', text)
        self.assertIn('<button type="button" data-view="kanban" aria-pressed="false">Kanban</button>', text)
        self.assertIn('<button type="button" data-view="board" aria-pressed="false">Board</button>', text)
        self.assertIn('<button type="button" data-view="list" aria-pressed="false">List</button>', text)

    def test_one_column_per_ledger_status_including_empty_ones(self):
        from tools.tracker import ledger as L
        text = self.render([item("A-01", status="not started")])
        kanban = text.split('<section class="kanban"', 1)[1]
        for status in L.STATUSES:
            self.assertIn(f'data-column="{status}"', kanban)
        # columns are in the ledger's own order, not the board's attention order
        positions = [kanban.index(f'data-column="{s}"') for s in L.STATUSES]
        self.assertEqual(positions, sorted(positions))
        # an empty status still shows a column with a 0 count
        blocked_col = kanban.split('data-column="blocked"', 1)[1].split('data-column=', 1)[0]
        self.assertIn('<span class="n">0</span>', blocked_col)

    def test_card_names_item_proposal_and_completion(self):
        text = self.render([item("K-01", status="in progress", title="Kanban card title")], number=42)
        self.assertIn('<article class="kcard" data-item data-id="K-01" data-proposal="42"', text)
        self.assertIn('<span class="kid">K-01</span>', text)
        self.assertIn('<span class="pnum">P42</span>', text)
        self.assertIn('title="Kanban card title">Kanban card title</h3>', text)
        self.assertIn('0% <span class="fbar kbar">', text)

    def test_a_card_with_parts_shows_the_count_and_expands_to_list_them(self):
        text = self.render([
            item("K-02", parts=[part("K-02.A", "first", 60, "done"), part("K-02.B", "second", 40, "in progress")]),
        ])
        kanban = text.split('<section class="kanban"', 1)[1]
        self.assertIn('<summary>1 of 2 parts done</summary>', kanban)
        self.assertIn('<span class="pid">K-02.A</span>', kanban)
        self.assertIn('<span class="pid">K-02.B</span>', kanban)

    def test_kanban_omitted_when_there_are_no_entries(self):
        self.assertEqual(board.kanban_section([]), "")

    def test_done_column_is_collapsed_behind_an_affordance_by_default(self):
        # Sponsor correction, 2026-09-18: a 112-card done column is
        # unusable. The show-finished toggle (already on the page) governs
        # it: collapsed by default behind "N done -- show them", the column
        # itself and its real count staying put either way.
        text = self.render([
            item("D-01", status="done", title="first done"),
            item("D-02", status="done", title="second done"),
            item("D-03", status="in progress", title="still going"),
        ])
        kanban = text.split('<section class="kanban"', 1)[1]
        self.assertIn('<div class="kcards" data-kanban-done hidden>', kanban)
        self.assertIn('<button type="button" class="kdone-show" data-kanban-affordance>'
                      '2 done — show them</button>', kanban)
        # the column header count is the real, unhidden count -- 2, not 0
        done_col = kanban.split('data-column="done"', 1)[1].split('data-column=', 1)[0]
        self.assertIn('<span class="n">2</span>', done_col)
        # the cards are still in the markup (readable with JS off), just
        # server-rendered hidden by default
        self.assertIn('data-id="D-01"', kanban)
        self.assertIn('data-id="D-02"', kanban)

    def test_a_column_with_no_done_items_has_no_affordance(self):
        text = self.render([item("A-01", status="in progress")])
        body = text.split("<script>", 1)[0]
        kanban = body.split('<section class="kanban"', 1)[1]
        self.assertNotIn('data-kanban-affordance', kanban)
        self.assertNotIn('data-kanban-done', kanban)
        done_col = kanban.split('data-column="done"', 1)[1].split('data-column=', 1)[0]
        self.assertIn('<span class="n">0</span>', done_col)

    def test_both_views_are_rendered_server_side(self):
        # No page reload, no server round trip: all four views are already
        # in the markup -- the inline script only toggles which is hidden.
        # Tree is the default view, so it alone renders without a `hidden`
        # attribute; Kanban, Board and List start hidden server-side (proposal
        # 30, P-11), the same pattern List already used when Board was the
        # default view.
        text = self.render([item("A-01", status="in progress")])
        self.assertIn('<div id="view-tree">', text)
        self.assertIn('<div id="view-kanban" hidden>', text)
        self.assertNotIn('id="view-tree" hidden', text)

    def test_kanban_cards_are_never_counted_alongside_the_details_board(self):
        # Sponsor correction, 2026-09-18: a kanban card is an <article
        # data-item>, same as the Details section's own board card, so a
        # bare tagName check in the page's script summed both -- "the
        # numbers on that bar are exactly what the sponsor reads to trust
        # the page". A kanban card's class is "kcard", never "card", and
        # the script's own counting line checks class membership, not tag.
        text = self.render([item("A-01", status="in progress")])
        body = text.split("<script>", 1)[0]
        script = text.split("<script>", 1)[1]
        self.assertIn('class="kcard"', body)
        self.assertNotIn('class="kcard card"', body)
        self.assertNotIn('class="card kcard"', body)
        self.assertIn('el.classList.contains(counted)', script)
        self.assertNotIn('el.tagName === counted', script)


if __name__ == "__main__":
    unittest.main()


class TestTheBarFillsFromTheLeft(unittest.TestCase):
    """An item's bar is its completion, accumulated -- not its parts in
    letter order.

    The sponsor: "also some of the progress bars are wrong". W-10 was the
    live case: five parts of 20% with only C done rendered
    amber/amber/GREEN/amber/amber, a filled stripe floating in the middle of
    an empty bar, while the row beside it read 20%. A bar next to a
    percentage is read as a progress bar, so it has to fill like one.
    """

    @staticmethod
    def item(*statuses):
        share = 100 // len(statuses)
        return {"id": "W-10", "status": "in progress", "parts": [
            {"id": f"W-10.{chr(65 + n)}", "share": share, "status": s}
            for n, s in enumerate(statuses)]}

    def widths(self, html):
        return re.findall(r'class="(seg-[\w-]+)" style="width:(\d+)%"', html)

    def test_a_done_part_in_the_middle_still_fills_from_the_left(self):
        bar = board.feature_bar(self.item(
            "not started", "not started", "done", "not started", "not started"))
        self.assertEqual([("seg-done", "20"), ("seg-empty", "80")], self.widths(bar))

    def test_the_done_width_equals_the_completion_percent(self):
        for statuses in (("done", "not started"),
                         ("not started", "done"),
                         ("done", "done", "not started", "not started")):
            with self.subTest(statuses=statuses):
                item = self.item(*statuses)
                first = self.widths(board.feature_bar(item))[0]
                self.assertEqual("seg-done", first[0])
                self.assertEqual(PARTS.completion(item), int(first[1]))

    def test_one_segment_per_bucket_not_one_per_part(self):
        bar = board.feature_bar(self.item("done", "done", "done", "not started"))
        self.assertEqual([("seg-done", "75"), ("seg-empty", "25")], self.widths(bar))

    def test_a_bucket_with_no_share_is_left_out_entirely(self):
        bar = board.feature_bar(self.item("done", "done"))
        self.assertEqual([("seg-done", "100")], self.widths(bar))


def test_history_since_is_the_floor_of_both_charts(tmp_path, monkeypatch):
    """A declared history_since in .common-rules.json is the earliest date the
    progress block shows (Loom, 2026-09-25: "reset the old data from the graph")."""
    from tools.tracker import board as B
    calls = []

    def fake_series(project, since=None, granularity="day"):
        calls.append((since, granularity))
        return [{"date": "2026-09-25", "tickets_total": 2, "tickets_done": 1, "completion_pct": 50.0,
                 "by_status": {"done": 1, "not started": 1}}]
    monkeypatch.setattr(B.HIST, "series", fake_series)
    monkeypatch.setattr(B.P, "load", lambda project: {"history_since": "2026-09-25"})
    html = B.progress_block(tmp_path)
    assert "Progress over time" in html
    assert calls[0] == ("2026-09-25", "day")
    assert calls[1][0] >= "2026-09-25" and calls[1][1] == "hour"
