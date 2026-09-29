"""The one filter bar at the top, governing every view (proposal 30, P-11).

The sponsor: "right now there are filters board list and there should be
another filter and then basically I should be able to filter all types of
views the drop down the board and other things so I have a common set of
filters there on top so it's possible for me to just in the drop down list
as well uh, filter the pending items". Three things pinned here: one bar, at
the top, above every view (Tree/Kanban/Board/List); the bar reaches inside
the Proposals tree's dropdowns, hiding a non-matching item or part and
hiding a proposal left with no matching items, while a surviving proposal
shows how many matched next to its real done-count; a first-class Pending
control, coherent with the existing show-finished toggle rather than a
second switch that can disagree with it.

The page has no build step and no external script, so its filtering lives in
one inline <script>; these tests pin structure and the script's own text --
never pixel values or CSS property order, and never a headless-browser run
(none is part of this repo's toolchain).

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.tracker import board  # noqa: E402


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


class FilterBarCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def render(self, items, number=30, title="a proposal"):
        led = ledger(number, items, title=title)
        path = write(self.root, number, led)
        return board.render([(path, led)], "demo", None, self.root)

    def test_the_bar_renders_once_above_the_tiles(self):
        text = self.render([item("A-01")])
        self.assertEqual(text.count('<div class="filters"'), 1)
        bar_at = text.index('<div class="filters"')
        tiles_at = text.index('<div class="tiles">')
        totals_at = text.index('<section class="totals"')
        self.assertTrue(totals_at < bar_at < tiles_at, "the bar sits under the totals, above the tiles")

    def test_details_section_has_no_bar_of_its_own(self):
        text = self.render([item("A-01")])
        details_at = text.index('<h2 id="details">Details</h2>')
        self.assertNotIn('<div class="filters"', text[details_at:])

    def test_bar_is_sticky(self):
        text = self.render([item("A-01")])
        self.assertRegex(text, r"\.filters\{[^}]*position:sticky[^}]*top:0")

    def test_view_group_is_one_group_of_four_tree_first(self):
        text = self.render([item("A-01")])
        m = re.search(r'<div class="views" role="group"[^>]*>(.*?)</div>', text, re.S)
        self.assertIsNotNone(m)
        views = re.findall(r'data-view="([^"]+)"', m.group(1))
        self.assertEqual(views, ["tree", "kanban", "board", "list"])
        self.assertEqual(text.count('data-view="tree"'), 1)

    def test_pending_is_a_first_class_control_not_a_chip(self):
        text = self.render([item("A-01")])
        self.assertIn('<label class="toggle pending"><input type="checkbox" id="pending">', text)
        # not one of the status chips
        self.assertNotIn('data-filter="status" data-value="pending"', text)

    def test_pending_and_show_finished_rule_is_stated_in_the_page(self):
        text = self.render([item("A-01")])
        self.assertIn('class="pending-rule', text)
        self.assertIn("Pending hides everything already done", text)
        self.assertIn('Show finished" off', text)

    def test_item_row_carries_the_full_filter_set(self):
        text = self.render([
            item("A-01", status="in progress", owner="lead", tier="medium",
                 parts=[part("A-01.A", "a", 100, "in progress")]),
        ])
        m = re.search(r'<details class="item-row"[^>]*data-id="A-01"[^>]*>', text)
        self.assertIsNotNone(m)
        tag = m.group(0)
        for attr in ('data-status="in progress"', 'data-owner="lead"', 'data-tier="medium"',
                     'data-group="finish now"', 'data-search="'):
            self.assertIn(attr, tag)

    def test_a_part_carries_its_own_status_and_search_for_filtering(self):
        text = self.render([
            item("A-01", parts=[part("A-01.A", "first half", 60, "done"),
                                 part("A-01.B", "second half", 40, "in progress")]),
        ])
        self.assertIn('data-pstatus="done"', text)
        self.assertIn('data-pstatus="in progress"', text)
        self.assertIn('data-psearch="a-01.b second half"', text)

    def test_a_proposal_shows_a_hidden_matched_count_span_next_to_its_done_count(self):
        text = self.render([item("A-01", status="done"), item("A-02", status="not started")])
        m = re.search(r'<span class="fpcount">1/2 tasks done</span><span class="fpmatched" hidden></span>', text)
        self.assertIsNotNone(m, "the real done-count and the (initially hidden) matched-count sit side by side")

    def test_proposal_row_and_item_row_and_part_row_are_all_present_for_js_to_filter(self):
        # Nothing here depends on the inline <script> having run -- these
        # are exactly the elements the script's match()/applyFeatures()/
        # applyTreeParts() (asserted below) operate on at runtime.
        text = self.render([item("A-01", parts=[part("A-01.A", "a", 100, "not started")])])
        body = text.split("<script>", 1)[0]
        self.assertIn('<details class="feature-row" data-proposal="30">', body)
        self.assertIn('<details class="item-row" data-item data-id="A-01"', body)
        self.assertIn('data-pstatus="not started"', body)

    def test_script_hides_a_part_that_does_not_match_its_own_status(self):
        text = self.render([item("A-01")])
        script = text.split("<script>", 1)[1]
        self.assertIn("function partOwnMatches(row)", script)
        self.assertIn('row.dataset.pstatus', script)
        self.assertIn("function filterPartNode(el)", script)

    def test_script_hides_a_proposal_left_with_no_matching_items(self):
        text = self.render([item("A-01")])
        script = text.split("<script>", 1)[1]
        self.assertIn("function applyFeatures(anyFilter)", script)
        self.assertIn("frow.hidden = anyFilter && matched === 0", script)
        self.assertIn('mEl.textContent = anyFilter ? matched + " of " + total + " items" : ""', script)

    def test_script_auto_expands_a_matching_proposal_and_never_auto_closes_it(self):
        text = self.render([item("A-01")])
        script = text.split("<script>", 1)[1]
        self.assertIn("if (anyFilter && matched > 0) frow.open = true;", script)
        # no branch ever sets frow.open = false while filtering -- only clear() does
        self.assertNotIn("frow.open = false", script)
        clear_fn = script[script.index("function clear()"):script.index("function clear()") + 700]
        self.assertIn('.feature-row', clear_fn)
        self.assertIn(".open = false", clear_fn)

    def test_pending_hides_done_items_parts_and_fully_done_proposals(self):
        text = self.render([
            item("D-01", status="done"),
            item("F-01", parts=[part("F-01.A", "a", 50, "done"), part("F-01.B", "b", 50, "not started")]),
        ])
        script = text.split("<script>", 1)[1]
        # item/proposal level: Pending reuses the same "hide finished" rule
        # the show-finished toggle already used (d.group === "done")
        self.assertIn('function hideFinished(){ return state.pending || !state.showFinished; }', script)
        self.assertIn('hideFinished() && isTerminal(el)', script)
        self.assertIn('el.dataset.group === "done" || el.dataset.status === "deferred"', script)
        # part level: a done part is dropped under Pending even inside a
        # surviving (not fully done) item
        self.assertIn('if (state.pending && (row.dataset.pstatus === "done" || row.dataset.pstatus === "deferred")) return false;', script)
        # the item/proposal-level data this drives is present in the markup
        self.assertIn('data-id="D-01" data-proposal="30" data-status="done"', text)
        self.assertIn('data-pstatus="done"', text)

    def test_pending_forces_show_finished_off_and_disables_it(self):
        text = self.render([item("A-01")])
        script = text.split("<script>", 1)[1]
        self.assertIn("showFinished.disabled = state.pending", script)
        self.assertIn("if (state.pending) showFinished.checked = false", script)
        self.assertIn("if (state.pending) state.showFinished = false", script)

    def test_kanban_affordance_is_unreachable_while_pending_is_on(self):
        text = self.render([item("A-01")])
        script = text.split("<script>", 1)[1]
        self.assertIn("if (state.pending) return;", script)
        self.assertIn("kshow.hidden = state.pending || !hideDone;", script)

    def test_counts_use_one_class_per_view_so_switching_views_cannot_double_count(self):
        text = self.render([item("A-01")])
        script = text.split("<script>", 1)[1]
        self.assertIn(
            'var counted = {tree: "item-row", kanban: "kcard", board: "card", list: "row"}[state.view] || "card";',
            script)
        self.assertIn('el.classList.contains(counted)', script)
        self.assertNotIn('el.tagName === counted', script)

    def test_kanban_card_also_carries_the_full_filter_set(self):
        text = self.render([item("K-01", status="in progress", owner="sponsor", tier="medium")])
        kanban = text.split('<section class="kanban"', 1)[1]
        m = re.search(r'<article class="kcard"[^>]*data-id="K-01"[^>]*>', kanban)
        self.assertIsNotNone(m)
        tag = m.group(0)
        for attr in ('data-status="in progress"', 'data-owner="sponsor"', 'data-tier="medium"',
                     'data-group=', 'data-search="'):
            self.assertIn(attr, tag)

    def test_clear_resets_pending_and_every_filter_and_collapses_the_tree(self):
        text = self.render([item("A-01")])
        script = text.split("<script>", 1)[1]
        clear_fn = script[script.index("function clear()"):script.index("function clear()") + 700]
        for field in ('state.proposal = ""', 'state.statuses = []', 'state.owner = ""', 'state.tier = ""',
                      'state.group = ""', 'state.q = ""', 'state.pending = false', 'state.showFinished = false'):
            self.assertIn(field, clear_fn)
        self.assertIn('.feature-row,.item-row,.prow-details', clear_fn)

    def test_state_is_persisted_reads_and_writes_are_guarded(self):
        text = self.render([item("A-01")])
        script = text.split("<script>", 1)[1]
        self.assertIn("function persist()", script)
        self.assertIn('localStorage.setItem("tracker-view"', script)
        self.assertIn('localStorage.setItem("tracker-filters"', script)
        # every localStorage access in the script is inside a try -- a
        # naive count that reads never throw would miss a bare getItem
        for m in re.finditer(r"localStorage\.(get|set)Item", script):
            before = script[:m.start()]
            self.assertIn("try {", before[-40:], f"unwrapped localStorage call near: {script[m.start()-20:m.start()+40]!r}")

    def test_page_still_reads_when_there_are_no_filters_and_view_is_tree(self):
        # The declared defaults, before any localStorage read succeeds.
        text = self.render([item("A-01")])
        script = text.split("<script>", 1)[1]
        self.assertIn(
            'var state = {proposal: "", statuses: [], owner: "", tier: "", group: "", q: "",\n'
            '               view: "tree", pending: false, showFinished: false};',
            script)


if __name__ == "__main__":
    unittest.main()
