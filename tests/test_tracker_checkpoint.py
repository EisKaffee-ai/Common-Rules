"""tools/tracker/checkpoint.py -- the checkpoint's own group section
(proposal 30, P-04): open items by PT.group, with completion % and the next
open part, short by design.

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import datetime
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.tracker import checkpoint as CP  # noqa: E402

NOW = datetime.datetime(2026, 9, 17, 12, 0)


def item(iid, status="in progress", parts=None, **extra):
    i = {"id": iid, "phase": "W", "cx": "C2", "title": f"title {iid}", "status": status, **extra}
    if parts is not None:
        i["parts"] = parts
    return i


def part(iid, letter, share, status="not started", **extra):
    return {"id": f"{iid}.{letter}", "title": f"part {letter}", "share": share, "status": status, **extra}


def ledger(items):
    return {"proposal": 30, "title": "Parts", "items": items}


class TestGroupsSection(unittest.TestCase):

    def test_an_item_without_parts_is_its_own_finish_now_line(self):
        d = ledger([item("W-01")])
        out = CP.render([(Path("x.json"), d)], "deadbeef", "manual", Path("."), NOW)
        self.assertIn("### Open work by group", out)
        self.assertIn("**finish now**", out)
        self.assertIn("- W-01 0%\n", out)
        self.assertNotIn("next W-01", out)

    def test_a_split_item_shows_completion_and_next_part(self):
        d = ledger([item("W-10", parts=[part("W-10", "A", 60, "done"), part("W-10", "B", 40)])])
        out = CP.render([(Path("x.json"), d)], "deadbeef", "manual", Path("."), NOW)
        self.assertIn("**finish now**", out)
        self.assertIn("- W-10 60% · next W-10.B", out)

    def test_80_percent_or_more_is_back_burner(self):
        d = ledger([item("W-10", parts=[part("W-10", "A", 80, "done"), part("W-10", "B", 20)])])
        out = CP.render([(Path("x.json"), d)], "deadbeef", "manual", Path("."), NOW)
        self.assertIn("**back burner**", out)
        self.assertIn("- W-10 80% · next W-10.B", out)

    def test_a_waiting_date_says_why(self):
        d = ledger([item("W-10", parts=[part("W-10", "A", 40, "done"),
                                        part("W-10", "B", 60, waiting_until="2099-01-01")])])
        out = CP.render([(Path("x.json"), d)], "deadbeef", "manual", Path("."), NOW)
        self.assertIn("**waiting**", out)
        self.assertIn("(waiting 2099-01-01)", out)

    def test_a_session_owner_says_who(self):
        d = ledger([item("W-10", parts=[part("W-10", "A", 40, "done"),
                                        part("W-10", "B", 60, owner="session:PhotoVault Engine")])])
        out = CP.render([(Path("x.json"), d)], "deadbeef", "manual", Path("."), NOW)
        self.assertIn("(waiting on PhotoVault Engine)", out)

    def test_done_items_are_not_open_work(self):
        entry = [{"at": "2026-09-13T21:00:00+02:00", "event": "merged", "by": "lead", "evidence": "abc"}]
        d = ledger([item("W-01", status="done", log=entry)])
        out = CP.render([(Path("x.json"), d)], "deadbeef", "manual", Path("."), NOW)
        self.assertIn("### Open work by group\n\n- none", out)

    def test_deferred_items_are_not_open_work_or_next_actions(self):
        entry = [{"at": "2026-09-20T21:00:00+02:00", "event": "deferred", "by": "lead",
                  "evidence": "out of scope", "status": "deferred"}]
        d = ledger([item("W-01", status="deferred", deferred_reason="out of scope", log=entry),
                    item("W-02", status="not started", depends="W-01")])
        out = CP.render([(Path("x.json"), d)], "deadbeef", "manual", Path("."), NOW)
        self.assertIn("### Open work by group", out)
        self.assertIn("- W-02 0%", out)
        self.assertNotIn("- W-01", out)
        self.assertIn("### Next unblocked", out)
        self.assertIn("- W-02", out)

    def test_flat_sections_are_kept(self):
        # The existing sections are untouched -- P-04 adds a section, it does
        # not remove what a hook or a reader already relies on.
        d = ledger([item("W-01")])
        out = CP.render([(Path("x.json"), d)], "deadbeef", "manual", Path("."), NOW)
        self.assertIn("### In progress", out)
        self.assertIn("- W-01 ·  · title W-01 · no log entry yet", out)


if __name__ == "__main__":
    unittest.main()
