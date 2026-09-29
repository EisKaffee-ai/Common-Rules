"""The completion overview (proposal 30, P-03): four tiles, then finish now /
back burner / waiting groups, each open feature's parts visible underneath,
grouped and colored by the rules in tools/tracker/parts.py -- never
recomputed here. Also: the old Lanes view survives, folded; the Details
filter bar carries a group/proposal/owner/status/search set and a
show-finished toggle, off by default (D4).

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from unittest import mock
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.tracker import board  # noqa: E402


def ledger(number, items):
    return {"proposal": number, "title": f"proposal {number}", "status": "accepted", "updated": "2026-09-17",
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


class CompletionOverviewCase(unittest.TestCase):
    def setUp(self):
        class FixtureDate(datetime.date):
            @classmethod
            def today(cls): return cls(2026, 9, 17)
        clock = mock.patch("tools.tracker.parts.datetime.date", FixtureDate)
        clock.start()
        self.addCleanup(clock.stop)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def render(self, items):
        led = ledger(30, items)
        path = write(self.root, 30, led)
        return board.render([(path, led)], "demo", None, self.root)

    def test_a_done_item_is_hidden_by_default_and_counted_in_the_tile(self):
        text = self.render([item("D-01", status="done")])
        self.assertRegex(text, r'data-id="D-01"[^>]*data-group="done"[^>]*\bhidden\b')
        self.assertIn("1 of 1", text)  # "N of M items done"

    def test_the_done_tile_says_items_done_not_features_finished(self):
        # Sponsor correction, 2026-09-18: the tile used to read "N of M
        # features finished" while M counts items, not proposals -- one
        # word for two different things on the same screen.
        text = self.render([item("D-01", status="done")])
        self.assertIn('<span class="l">tasks done</span>', text)
        self.assertNotIn("features finished", text)

    def test_waiting_by_date_and_by_other_project_owner(self):
        text = self.render([
            item("W-01", parts=[part("W-01.A", "a", 100, "not started", waiting_until="2099-01-01")]),
            item("W-02", parts=[part("W-02.A", "a", 100, "not started", owner="session:other")]),
        ])
        self.assertIn('data-group="waiting"', text)
        self.assertNotIn('data-id="W-01" data-proposal="30" data-group="finish now"', text)
        # both land in the waiting group section
        self.assertIn('data-feature data-id="W-01" data-proposal="30" data-group="waiting"', text)
        self.assertIn('data-feature data-id="W-02" data-proposal="30" data-group="waiting"', text)
        self.assertIn("other project", text)

    def test_finish_now_under_80_back_burner_at_80(self):
        text = self.render([
            item("F-01", parts=[part("F-01.A", "a", 79, "done"), part("F-01.B", "b", 21, "not started")]),
            item("B-01", parts=[part("B-01.A", "a", 80, "done"), part("B-01.B", "b", 20, "not started")]),
        ])
        self.assertIn('data-feature data-id="F-01" data-proposal="30" data-group="finish now"', text)
        self.assertIn('data-feature data-id="B-01" data-proposal="30" data-group="back burner"', text)

    def test_a_high_risk_open_part_forces_finish_now_even_above_80(self):
        text = self.render([
            item("R-01", parts=[part("R-01.A", "a", 90, "done"),
                                 part("R-01.B", "b", 10, "not started", risk="high", risk_reason="untested path")]),
        ])
        self.assertIn('data-feature data-id="R-01" data-proposal="30" data-group="finish now"', text)
        self.assertIn('risk high', text)
        self.assertIn('title="untested path"', text)

    def test_group_counts_in_the_headers(self):
        text = self.render([
            item("F-01", parts=[part("F-01.A", "a", 50, "not started")]),
            item("F-02", parts=[part("F-02.A", "a", 50, "not started")]),
            item("B-01", parts=[part("B-01.A", "a", 100, "done")]),
        ])
        self.assertIn("Finish now · under 80% done, or an open part is high risk", text)
        self.assertIn("Back burner · 80% or more done, the rest is low or medium risk", text)
        self.assertIn("Waiting · owned by another project, or waiting for a date", text)

    def test_parts_sub_rows_show_id_title_share_and_pill(self):
        text = self.render([
            item("P-01", parts=[part("P-01.A", "first half", 60, "done"),
                                 part("P-01.B", "second half", 40, "in progress")]),
        ])
        self.assertIn('<span class="pid">P-01.A</span>', text)
        self.assertIn('<span class="ptitle" title="first half">first half</span>', text)
        self.assertIn('<span class="pshare">60%</span>', text)
        self.assertIn('p-done s-done">done</span>', text)
        self.assertIn('data-pstatus="in progress"', text)
        self.assertIn('.pill.p-s-in-progress', text)
        self.assertIn('<span class="pid">P-01.B</span>', text)

    def test_a_waiting_date_pill_shows_the_short_date(self):
        text = self.render([
            item("D-02", parts=[part("D-02.A", "a", 100, "not started", waiting_until="2026-09-23")]),
        ])
        self.assertIn(">23 Sep<", text)

    # -- proposal 30, P-13: "pull forward" -----------------------------------

    def test_a_waiting_part_renders_the_pull_forward_affordance(self):
        text = self.render([
            item("D-02", parts=[part("D-02.A", "a", 100, "not started", waiting_until="2026-09-23")]),
        ])
        self.assertIn('<div class="pull-forward"', text)
        self.assertIn('Copy the command that pulls this forward', text)

    def test_a_non_waiting_part_does_not_render_the_affordance(self):
        text = self.render([
            item("N-01", parts=[part("N-01.A", "a", 60, "done"),
                                 part("N-01.B", "b", 40, "in progress")]),
        ])
        # The JS's own delegated-listener selectors always mention
        # "data-pull-forward" (they must, to find any affordance the page
        # does render elsewhere); what must not appear for a non-waiting
        # part is the affordance markup itself.
        self.assertNotIn('<div class="pull-forward"', text)
        self.assertNotIn('Copy the command that pulls this forward', text)

    def test_the_copied_command_names_the_ledger_item_and_part(self):
        text = self.render([
            item("D-02", parts=[part("D-02.A", "a", 100, "not started", waiting_until="2026-09-23")]),
        ])
        self.assertIn('data-cmd="bin/tracker set docs/proposals/30-*.json D-02.A --waiting-until none', text)

    def test_the_copied_command_for_a_session_owned_wait_reclaims_the_owner(self):
        text = self.render([
            item("D-03", parts=[part("D-03.A", "a", 100, "not started", owner="session:PhotoVault Engine")]),
        ])
        self.assertIn('data-cmd="bin/tracker set docs/proposals/30-*.json D-03.A --owner lead', text)

    def test_the_label_and_confirmation_never_claim_something_ran(self):
        text = self.render([
            item("D-02", parts=[part("D-02.A", "a", 100, "not started", waiting_until="2026-09-23")]),
        ])
        self.assertIn('Copy the command that pulls this forward', text)
        self.assertNotIn('>Run now<', text)
        self.assertIn('nothing has run yet', text)
        self.assertIn('Paste this into a session for this project', text)

    def test_the_waiting_reason_is_present_as_text_date(self):
        text = self.render([
            item("D-02", parts=[part("D-02.A", "a", 100, "not started", waiting_until="2026-09-23")]),
        ])
        self.assertIn('waiting until 2026-09-23', text)

    def test_the_waiting_reason_is_present_as_text_session(self):
        text = self.render([
            item("D-03", parts=[part("D-03.A", "a", 100, "not started", owner="session:PhotoVault Engine")]),
        ])
        self.assertIn('waiting for session:PhotoVault Engine', text)

    def test_an_item_without_parts_renders_as_one_implicit_part(self):
        text = self.render([item("I-01", status="in progress", title="no parts yet")])
        self.assertIn('<span class="pid">I-01</span>', text)
        self.assertIn('<span class="pshare">100%</span>', text)

    def test_lanes_section_is_present_but_folded(self):
        text = self.render([item("L-01", status="not started", value="high", points=5, impact=1, likelihood=1)])
        self.assertIn('<details class="lanes" id="lanes">', text)
        # closed: no bare `open` attribute on the folded section
        self.assertNotRegex(text, r'<details class="lanes" id="lanes"[^>]*\bopen\b')

    def test_by_urgency_and_lanes_get_the_same_card_surface_as_clusters(self):
        # P-14: the folded "By urgency" (`.cgroups`) and "Advanced · Lanes"
        # (`.lanes`) summaries floated as bare text between blocks -- the
        # shared card-surface rule named `.clusters` and `.lanes` but never
        # `.cgroups`, so only one of the two the sponsor pointed at was
        # actually covered. Both must share the one rule now.
        text = self.render([item("L-01", status="not started", value="high", points=5, impact=1, likelihood=1)])
        self.assertIn(
            '.clusters,.lanes,.cgroups{background:var(--surface);'
            'border:1px solid var(--rule);border-radius:6px;padding:14px 16px}', text)

    def test_filters_markup_carries_group_proposal_owner_status_search(self):
        # P-14: the proposal nav is a filter among proposals, so it only
        # earns its place with more than one -- a second ledger here keeps
        # this test about the filter bar's own markup, not that behavior
        # (pinned on its own below).
        led2 = ledger(31, [item("Y-01")])
        path2 = write(self.root, 31, led2)
        led1 = ledger(30, [item("X-01")])
        path1 = write(self.root, 30, led1)
        text = board.render([(path1, led1), (path2, led2)], "demo", None, self.root)
        self.assertIn('<select id="group">', text)
        self.assertIn('<nav class="proposals"', text)  # the proposal filter
        self.assertIn('<select id="owner">', text)
        self.assertIn('role="group" aria-label="Task status"', text)
        self.assertIn('<input type="search" id="q"', text)

    def test_proposal_filter_nav_omitted_with_only_one_proposal(self):
        # P-14: on a one-proposal project (PhotoVault/engine's own page),
        # this nav repeated the Proposals tree's completion line for the
        # single proposal, with nothing to filter among -- omitted now
        # rather than kept as a bare duplicate.
        text = self.render([item("X-01")])
        self.assertNotIn('<nav class="proposals"', text)
        self.assertNotIn('class="proposal" type="button"', text)

    def test_show_finished_toggle_is_present_and_off(self):
        text = self.render([item("X-01", status="done")])
        self.assertIn('<input type="checkbox" id="show-finished">', text)
        self.assertNotIn('id="show-finished" checked', text)

    def test_proposal_tree_sits_above_the_folded_group_lists(self):
        # proposal 30, P-09: the sponsor's proposal tree is the top view --
        # the finish-now/back-burner/waiting grouping (by urgency) comes
        # after it, folded into a closed <details>, not the first thing shown.
        text = self.render([item("A-01", parts=[part("A-01.A", "a", 50, "not started")])])
        tiles_at = text.index('<div class="tiles">')
        features_at = text.index('<section class="features"')
        groups_at = text.index('<details class="cgroups" id="cgroups">')
        cgroup_at = text.index('<section class="cgroup"')
        self.assertTrue(tiles_at < features_at < groups_at < cgroup_at)

    def test_group_lists_are_folded_closed_by_default(self):
        text = self.render([item("A-01", parts=[part("A-01.A", "a", 50, "not started")])])
        self.assertIn('<details class="cgroups" id="cgroups">', text)
        self.assertNotRegex(text, r'<details class="cgroups" id="cgroups"[^>]*\bopen\b')

    def test_overview_is_correct_without_javascript(self):
        # The tiles, group headers and feature/part rows are plain markup --
        # no attribute here depends on the inline <script> having run.
        text = self.render([
            item("A-01", parts=[part("A-01.A", "a", 50, "not started")]),
            item("A-02", status="done"),
        ])
        body = text.split("<script>", 1)[0]
        self.assertIn("1 of 3", body)
        self.assertIn("finish now", body)
        self.assertIn('<span class="pid">A-01.A</span>', body)


if __name__ == "__main__":
    unittest.main()
