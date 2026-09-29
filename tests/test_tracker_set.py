"""`tracker set` -- one item, changed and logged in one line (proposal 23,
lever L4, L-04), in place of the inline `python3 -` scripts that used to load
a ledger, edit one item and dump it back.

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.tracker import ledger as L  # noqa: E402
from tools.tracker import render as R  # noqa: E402

TRACKER = ROOT / "bin" / "tracker"


def fixture(**over):
    d = {
        "proposal": 99, "title": "fixture", "status": "accepted", "updated": "2026-01-01",
        "phases": [{"id": "W", "name": "build"}],
        "items": [
            {"id": "W-01", "phase": "W", "cx": "C2", "title": "a", "status": "not started"},
            {"id": "W-02", "phase": "W", "cx": "C3", "title": "b", "status": "not started"},
        ],
        "asks": [],
    }
    d.update(over)
    return d


class TrackerSetCase(unittest.TestCase):
    """A temp copy of a small fixture ledger, per proposal 23's instruction."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "99-fixture.json"
        self.write(fixture())

    def write(self, data):
        self.ledger.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    def read(self):
        return json.loads(self.ledger.read_text())

    def run_set(self, *args):
        return subprocess.run([sys.executable, str(TRACKER), "set", str(self.ledger), *args],
                              capture_output=True, text=True)

    def item(self, iid, data=None):
        return L.by_id(data or self.read())[iid]


class TestStatusAndAutoLog(TrackerSetCase):

    def test_status_change_appends_an_event_equal_to_the_status(self):
        before = self.ledger.read_bytes()
        r = self.run_set("W-01", "--status", "in progress")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertNotEqual(before, self.ledger.read_bytes())
        item = self.item("W-01")
        self.assertEqual("in progress", item["status"])
        self.assertEqual(1, len(item["log"]))
        self.assertEqual("in progress", item["log"][0]["event"])
        self.assertEqual("lead", item["log"][0]["by"])

    def test_stdout_is_exactly_one_line(self):
        r = self.run_set("W-01", "--status", "in progress")
        self.assertEqual(0, r.returncode, r.stderr)
        lines = r.stdout.splitlines()
        self.assertEqual(1, len(lines))
        self.assertTrue(lines[0].startswith("tracker set: W-01 "))
        self.assertIn("status in progress", lines[0])
        self.assertIn("page rendered", lines[0])

    def test_deferred_requires_reason_and_records_it_in_history(self):
        before = self.ledger.read_bytes()
        missing = self.run_set("W-01", "--status", "deferred")
        self.assertEqual(1, missing.returncode)
        self.assertEqual(before, self.ledger.read_bytes())
        r = self.run_set("W-01", "--status", "deferred", "--reason", "parked until priorities change")
        self.assertEqual(0, r.returncode, r.stderr)
        item = self.item("W-01")
        self.assertEqual("deferred", item["status"])
        self.assertEqual("parked until priorities change", item["deferred_reason"])
        self.assertEqual("deferred", item["log"][-1]["status"])
        self.assertEqual("parked until priorities change", item["log"][-1]["evidence"])

    def test_deferred_can_only_be_reopened_explicitly(self):
        self.assertEqual(0, self.run_set("W-01", "--status", "deferred", "--reason", "parked").returncode)
        refused = self.run_set("W-01", "--status", "in progress")
        self.assertEqual(1, refused.returncode)
        self.assertEqual("deferred", self.item("W-01")["status"])
        reopened = self.run_set("W-01", "--status", "in progress", "--reopen")
        self.assertEqual(0, reopened.returncode, reopened.stderr)
        self.assertEqual("in progress", self.item("W-01")["status"])
        self.assertNotIn("deferred_reason", self.item("W-01"))


class TestCustomEvent(TrackerSetCase):

    def test_event_evidence_by_and_at_are_all_honoured(self):
        r = self.run_set("W-01", "--status", "in progress", "--event", "started",
                          "--evidence", "kickoff call", "--by", "the sponsor", "--at",
                          "2026-01-02T09:00:00+05:30")
        self.assertEqual(0, r.returncode, r.stderr)
        item = self.item("W-01")
        entry = item["log"][-1]
        self.assertEqual("started", entry["event"])
        self.assertEqual("kickoff call", entry["evidence"])
        self.assertEqual("the sponsor", entry["by"])
        self.assertEqual("2026-01-02T09:00:00+05:30", entry["at"])
        self.assertIn('log "started"', r.stdout)


class TestLogEntryStatusKey(TrackerSetCase):
    """RF-01: `--status` stamps the log entry's own `status` key too,
    independent of `--event`'s free text -- bin/conformance item 9 reads the
    close date from `status`, not `event`, since a lead's own `--event`
    wording does not reliably spell "done"."""

    def test_status_alone_stamps_the_log_entry_status_key(self):
        r = self.run_set("W-01", "--status", "done")
        self.assertEqual(0, r.returncode, r.stderr)
        entry = self.item("W-01")["log"][-1]
        self.assertEqual("done", entry.get("status"))
        self.assertEqual("done", entry["event"])

    def test_status_with_a_free_text_event_still_stamps_status(self):
        r = self.run_set("W-01", "--status", "done", "--event", "shipped in PR #99")
        self.assertEqual(0, r.returncode, r.stderr)
        entry = self.item("W-01")["log"][-1]
        self.assertEqual("done", entry.get("status"))
        self.assertEqual("shipped in PR #99", entry["event"])

    def test_event_without_status_never_stamps_a_status_key(self):
        r = self.run_set("W-01", "--event", "a note, no status change")
        self.assertEqual(0, r.returncode, r.stderr)
        entry = self.item("W-01")["log"][-1]
        self.assertNotIn("status", entry)

    def test_the_ledger_still_validates_with_a_status_keyed_entry(self):
        r = self.run_set("W-01", "--status", "done", "--event", "shipped")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual([], L.validate(self.read()))


class TestField(TrackerSetCase):

    def test_field_parses_json_when_valid(self):
        r = self.run_set("W-01", "--field", "weight=2")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual(2, self.item("W-01")["weight"])

    def test_field_falls_back_to_a_string(self):
        r = self.run_set("W-01", "--field", "tag=[ruflo · low · haiku]")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual("[ruflo · low · haiku]", self.item("W-01")["tag"])

    def test_forbidden_fields_are_refused(self):
        for key in ("id", "log", "phase"):
            before = self.ledger.read_bytes()
            r = self.run_set("W-01", "--field", f"{key}=x")
            self.assertEqual(1, r.returncode)
            self.assertEqual(before, self.ledger.read_bytes())


class TestUnknownItem(TrackerSetCase):

    def test_unknown_item_writes_nothing(self):
        before = self.ledger.read_bytes()
        r = self.run_set("W-99", "--status", "done")
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())


class TestInvalidStatusLeavesFileUntouched(TrackerSetCase):

    def test_a_status_outside_the_vocabulary_writes_nothing(self):
        before = self.ledger.read_bytes()
        r = self.run_set("W-01", "--status", "wip")
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())
        self.assertIn("wip", r.stderr)


class TestPageIsRendered(TrackerSetCase):

    def test_render_check_passes_after_set(self):
        r = self.run_set("W-01", "--status", "done", "--event", "merged")
        self.assertEqual(0, r.returncode, r.stderr)
        check = subprocess.run([sys.executable, str(TRACKER), "render", str(self.ledger), "--check"],
                               capture_output=True, text=True)
        self.assertEqual(0, check.returncode, check.stdout + check.stderr)


# --- proposal 30, P-02: `tracker set` on an item's lettered parts ----------

def with_parts(parts):
    return fixture(items=[
        {"id": "W-10", "phase": "W", "cx": "C2", "title": "split item", "status": "in progress",
         "parts": parts},
        {"id": "W-02", "phase": "W", "cx": "C3", "title": "b", "status": "not started"},
    ])


def part(letter, share, status="not started", **extra):
    return {"id": f"W-10.{letter}", "title": f"part {letter}", "share": share, "status": status, **extra}


class TrackerSetPartsCase(TrackerSetCase):
    """Same harness as TrackerSetCase, but the fixture ledger starts with a
    W-10 item split into parts (each subclass writes its own parts)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "99-fixture.json"


class TestSetOnAPart(TrackerSetPartsCase):

    def test_setting_a_part_status_updates_only_that_part(self):
        self.write(with_parts([part("A", 60), part("B", 40)]))
        r = self.run_set("W-10.A", "--status", "done", "--event", "shipped")
        self.assertEqual(0, r.returncode, r.stderr)
        item = self.item("W-10")
        self.assertEqual("done", item["parts"][0]["status"])
        self.assertEqual("not started", item["parts"][1]["status"])
        self.assertEqual("in progress", item["status"], "item stays open while a part is open")

    def test_the_log_entry_lands_on_the_part_not_the_item(self):
        self.write(with_parts([part("A", 60), part("B", 40)]))
        r = self.run_set("W-10.A", "--status", "done", "--evidence", "PR #1", "--by", "the sponsor")
        self.assertEqual(0, r.returncode, r.stderr)
        item = self.item("W-10")
        self.assertEqual(1, len(item["parts"][0]["log"]))
        entry = item["parts"][0]["log"][0]
        self.assertEqual("done", entry["status"])
        self.assertEqual("PR #1", entry["evidence"])
        self.assertEqual("the sponsor", entry["by"])
        self.assertEqual([], item.get("log") or [], "no item-level log entry while a part remains open")

    def test_field_on_a_part_writes_the_part_not_the_item(self):
        self.write(with_parts([part("A", 60), part("B", 40)]))
        r = self.run_set("W-10.A", "--field", "title=renamed slice")
        self.assertEqual(0, r.returncode, r.stderr)
        item = self.item("W-10")
        self.assertEqual("renamed slice", item["parts"][0]["title"])
        self.assertEqual("split item", item["title"], "the item's own title is untouched")

    def test_field_share_on_a_part_parses_as_an_int(self):
        self.write(with_parts([part("A", 60), part("B", 40)]))
        r = self.run_set("W-10.A", "--field", "share=50")
        # Deliberately leaves shares at 50 + 40 = 90 -- refused, proving the
        # ledger is validated (and shares parsed as JSON ints) before write.
        self.assertEqual(1, r.returncode)
        self.assertIn("add up to 90", r.stderr)

    def test_field_not_allowed_on_a_part_is_refused(self):
        self.write(with_parts([part("A", 60), part("B", 40)]))
        before = self.ledger.read_bytes()
        r = self.run_set("W-10.A", "--field", "cx=C1")
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())
        self.assertIn("cx", r.stderr)

    def test_owner_on_a_part(self):
        self.write(with_parts([part("A", 60), part("B", 40)]))
        r = self.run_set("W-10.A", "--owner", "session:builder-2")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual("session:builder-2", self.item("W-10")["parts"][0]["owner"])

    def test_unknown_part_writes_nothing(self):
        self.write(with_parts([part("A", 60), part("B", 40)]))
        before = self.ledger.read_bytes()
        r = self.run_set("W-10.C", "--status", "done")
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())

    def test_unknown_parent_item_writes_nothing(self):
        self.write(with_parts([part("A", 60), part("B", 40)]))
        before = self.ledger.read_bytes()
        r = self.run_set("W-99.A", "--status", "done")
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())

    def test_output_names_the_part_and_the_completion_percent(self):
        self.write(with_parts([part("A", 60), part("B", 40)]))
        r = self.run_set("W-10.A", "--status", "done")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("W-10.A", r.stdout)
        self.assertIn("completion 60%", r.stdout)


class TestWaitingUntilOnAPart(TrackerSetPartsCase):
    """Proposal 30, P-13: `--waiting-until` on an *existing* part -- editing
    (not `--add-part`) previously ignored the flag entirely, so a lead had
    to reach for `--field waiting_until=...`, which could set a date but
    never remove one. The tracker page's "pull forward" button needs a
    command that actually clears a wait, so `none`/`now` now do that."""

    def test_waiting_until_sets_a_date_on_an_existing_part(self):
        self.write(with_parts([part("A", 60), part("B", 40)]))
        r = self.run_set("W-10.A", "--waiting-until", "2026-09-23")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual("2026-09-23", self.item("W-10")["parts"][0]["waiting_until"])

    def test_waiting_until_none_removes_the_date_rather_than_setting_one(self):
        self.write(with_parts([part("A", 60, waiting_until="2026-09-23"), part("B", 40)]))
        r = self.run_set("W-10.A", "--waiting-until", "none", "--event", "pulled forward")
        self.assertEqual(0, r.returncode, r.stderr)
        p = self.item("W-10")["parts"][0]
        self.assertNotIn("waiting_until", p, "the key is removed, not set to null or empty")

    def test_waiting_until_now_also_clears_it(self):
        self.write(with_parts([part("A", 60, waiting_until="2026-09-23"), part("B", 40)]))
        r = self.run_set("W-10.A", "--waiting-until", "now")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertNotIn("waiting_until", self.item("W-10")["parts"][0])

    def test_clearing_an_already_clear_wait_still_succeeds(self):
        self.write(with_parts([part("A", 60), part("B", 40)]))
        r = self.run_set("W-10.A", "--waiting-until", "none")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertNotIn("waiting_until", self.item("W-10")["parts"][0])

    def test_waiting_until_logs_the_change_when_given_an_event(self):
        self.write(with_parts([part("A", 60, waiting_until="2026-09-23"), part("B", 40)]))
        r = self.run_set("W-10.A", "--waiting-until", "none", "--event", "pulled forward from 2026-09-23",
                          "--by", "sponsor")
        self.assertEqual(0, r.returncode, r.stderr)
        entry = self.item("W-10")["parts"][0]["log"][0]
        self.assertEqual("pulled forward from 2026-09-23", entry["event"])
        self.assertEqual("sponsor", entry["by"])


class TestWaitingUntilOnAnItem(TrackerSetCase):
    """Same clearing behaviour, but for a plain item (no `.LETTER` suffix) --
    `apply_change` took the same fix as `apply_part_change` (proposal 30,
    P-13)."""

    def test_waiting_until_sets_and_clears_on_an_item(self):
        r = self.run_set("W-01", "--waiting-until", "2026-09-23")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual("2026-09-23", self.item("W-01")["waiting_until"])
        r = self.run_set("W-01", "--waiting-until", "none")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertNotIn("waiting_until", self.item("W-01"))


class TestLastPartClosesTheItem(TrackerSetPartsCase):

    def test_setting_the_last_open_part_done_closes_the_item(self):
        self.write(with_parts([part("A", 60, "done"), part("B", 40)]))
        r = self.run_set("W-10.B", "--status", "done", "--event", "merged")
        self.assertEqual(0, r.returncode, r.stderr)
        item = self.item("W-10")
        self.assertEqual("done", item["status"])
        self.assertEqual("done", item["parts"][1]["status"])
        self.assertTrue(item.get("log"), "item gets its own roll-up log entry")
        last = item["log"][-1]
        self.assertEqual("all parts done", last["event"])
        self.assertEqual("done", last.get("status"))

    def test_completion_is_100_after_the_last_part(self):
        self.write(with_parts([part("A", 60, "done"), part("B", 40)]))
        r = self.run_set("W-10.B", "--status", "done")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("completion 100%", r.stdout)

    def test_ledger_still_validates_after_the_roll_up(self):
        self.write(with_parts([part("A", 60, "done"), part("B", 40)]))
        r = self.run_set("W-10.B", "--status", "done")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual([], L.validate(self.read()))


class TestItemDoneWhileAPartIsOpenIsRefused(TrackerSetPartsCase):

    def test_setting_the_item_itself_done_with_an_open_part_is_refused(self):
        self.write(with_parts([part("A", 60, "done"), part("B", 40)]))
        before = self.ledger.read_bytes()
        r = self.run_set("W-10", "--status", "done")
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())
        self.assertIn("status done while a part is still open", r.stderr)


class TestAddPart(TrackerSetPartsCase):

    def test_add_part_appends_the_next_letter(self):
        self.write(with_parts([part("A", 60, "done")]))
        r = self.run_set("W-10", "--add-part", "wrap-up", "--share", "40")
        self.assertEqual(0, r.returncode, r.stderr)
        item = self.item("W-10")
        self.assertEqual(2, len(item["parts"]))
        self.assertEqual("W-10.B", item["parts"][1]["id"])
        self.assertEqual("wrap-up", item["parts"][1]["title"])
        self.assertEqual(40, item["parts"][1]["share"])
        self.assertEqual("not started", item["parts"][1]["status"])

    def test_add_part_onto_an_item_with_no_parts_yet_becomes_part_a(self):
        self.write(fixture(items=[
            {"id": "W-10", "phase": "W", "cx": "C2", "title": "split item", "status": "not started"},
            {"id": "W-02", "phase": "W", "cx": "C3", "title": "b", "status": "not started"},
        ]))
        r = self.run_set("W-10", "--add-part", "first slice", "--share", "100")
        self.assertEqual(0, r.returncode, r.stderr)
        item = self.item("W-10")
        self.assertEqual(1, len(item["parts"]))
        self.assertEqual("W-10.A", item["parts"][0]["id"])
        self.assertEqual([], L.validate(self.read()))

    def test_add_part_with_owner_and_risk(self):
        self.write(with_parts([part("A", 60, "done")]))
        r = self.run_set("W-10", "--add-part", "wrap-up", "--share", "40", "--owner", "session:builder-3",
                          "--risk", "high", "--risk-reason", "external dependency")
        self.assertEqual(0, r.returncode, r.stderr)
        p = self.item("W-10")["parts"][1]
        self.assertEqual("session:builder-3", p["owner"])
        self.assertEqual("high", p["risk"])
        self.assertEqual("external dependency", p["risk_reason"])

    def test_add_part_needs_share(self):
        self.write(with_parts([part("A", 60, "done")]))
        before = self.ledger.read_bytes()
        r = self.run_set("W-10", "--add-part", "wrap-up")
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())

    def test_add_part_risk_needs_risk_reason(self):
        self.write(with_parts([part("A", 60, "done")]))
        before = self.ledger.read_bytes()
        r = self.run_set("W-10", "--add-part", "wrap-up", "--share", "40", "--risk", "high")
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())

    def test_add_part_that_leaves_shares_not_adding_to_100_is_refused(self):
        self.write(with_parts([part("A", 60, "done")]))
        before = self.ledger.read_bytes()
        r = self.run_set("W-10", "--add-part", "wrap-up", "--share", "10")
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())
        self.assertIn("add up to 70", r.stderr)

    def test_add_part_on_a_part_id_is_refused(self):
        self.write(with_parts([part("A", 60, "done"), part("B", 40)]))
        before = self.ledger.read_bytes()
        r = self.run_set("W-10.A", "--add-part", "wrap-up", "--share", "40")
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())


class TestPartsList(TrackerSetPartsCase):

    def test_parts_json_list_replaces_an_items_empty_parts(self):
        self.write(fixture(items=[
            {"id": "W-10", "phase": "W", "cx": "C2", "title": "split item", "status": "not started"},
            {"id": "W-02", "phase": "W", "cx": "C3", "title": "b", "status": "not started"},
        ]))
        spec = json.dumps([{"title": "first", "share": 60}, {"title": "second", "share": 40}])
        r = self.run_set("W-10", "--parts", spec)
        self.assertEqual(0, r.returncode, r.stderr)
        item = self.item("W-10")
        self.assertEqual(2, len(item["parts"]))
        self.assertEqual("W-10.A", item["parts"][0]["id"])
        self.assertEqual("W-10.B", item["parts"][1]["id"])
        self.assertEqual([], L.validate(self.read()))

    def test_parts_list_refused_when_the_item_already_has_parts(self):
        self.write(with_parts([part("A", 60, "done"), part("B", 40)]))
        before = self.ledger.read_bytes()
        spec = json.dumps([{"title": "x", "share": 100}])
        r = self.run_set("W-10", "--parts", spec)
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())

    def test_parts_list_invalid_json_is_refused(self):
        self.write(fixture(items=[
            {"id": "W-10", "phase": "W", "cx": "C2", "title": "split item", "status": "not started"},
            {"id": "W-02", "phase": "W", "cx": "C3", "title": "b", "status": "not started"},
        ]))
        before = self.ledger.read_bytes()
        r = self.run_set("W-10", "--parts", "{not json")
        self.assertEqual(1, r.returncode)
        self.assertEqual(before, self.ledger.read_bytes())


if __name__ == "__main__":
    unittest.main()
