"""`tracker stage` / `tracker apply-staged` -- one writer for ledger and
tracker files (proposal 23, M-04). An item lead or builder stages an
intended change without ever touching the ledger; the dispatcher applies
every staged file, one at a time, in a later, single call.

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


class StagingCase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "99-fixture.json"
        self.ledger.write_text(json.dumps(fixture(), indent=2, ensure_ascii=False) + "\n")
        self.staging = self.root / ".staging"

    def read(self):
        return json.loads(self.ledger.read_text())

    def item(self, iid, data=None):
        return L.by_id(data or self.read())[iid]

    def run_tracker(self, *args):
        return subprocess.run([sys.executable, str(TRACKER), *args], capture_output=True, text=True)

    def stage(self, *args):
        return self.run_tracker("stage", str(self.ledger), *args)

    def apply_staged(self):
        return self.run_tracker("apply-staged", str(self.ledger))


class TestStageNeverTouchesTheLedger(StagingCase):

    def test_stage_writes_only_under_dot_staging(self):
        before = self.ledger.read_bytes()
        r = self.stage("W-01", "--status", "in progress")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual(before, self.ledger.read_bytes())
        files = list(self.staging.glob("*.json"))
        self.assertEqual(1, len(files))
        self.assertEqual("not started", self.item("W-01")["status"])

    def test_forbidden_field_is_refused(self):
        r = self.stage("W-01", "--field", "id=NOPE")
        self.assertEqual(1, r.returncode)
        self.assertFalse(list(self.staging.glob("*.json")) if self.staging.is_dir() else [])

    def test_bad_field_syntax_is_refused(self):
        r = self.stage("W-01", "--field", "no-equals-sign")
        self.assertEqual(1, r.returncode)


class TestApplyStaged(StagingCase):

    def test_deferred_stage_carries_reason_and_apply_can_reopen_explicitly(self):
        r = self.stage("W-01", "--status", "deferred", "--reason", "parked")
        self.assertEqual(0, r.returncode, r.stderr)
        r = self.apply_staged()
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual("deferred", self.item("W-01")["status"])
        self.assertEqual("parked", self.item("W-01")["deferred_reason"])
        r = self.stage("W-01", "--status", "in progress", "--reopen")
        self.assertEqual(0, r.returncode, r.stderr)
        r = self.apply_staged()
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual("in progress", self.item("W-01")["status"])
        self.assertNotIn("deferred_reason", self.item("W-01"))

    def test_two_staged_changes_from_different_owners_both_land(self):
        self.stage("W-01", "--status", "in progress", "--by", "session:builder-a")
        self.stage("W-02", "--status", "in progress", "--by", "session:builder-b")
        r = self.apply_staged()
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual("in progress", self.item("W-01")["status"])
        self.assertEqual("in progress", self.item("W-02")["status"])
        self.assertEqual([], list(self.staging.glob("*.json")))

    def test_applied_files_are_deleted_one_by_one(self):
        self.stage("W-01", "--status", "in progress")
        r = self.apply_staged()
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual([], list(self.staging.glob("*.json")))

    def test_unknown_item_is_left_in_place_and_reported(self):
        self.stage("NOPE-01", "--status", "done")
        r = self.apply_staged()
        self.assertEqual(1, r.returncode)
        self.assertIn("NOPE-01", r.stderr)
        self.assertEqual(1, len(list(self.staging.glob("*.json"))))

    def test_one_bad_staged_file_does_not_block_the_others(self):
        self.stage("W-01", "--status", "in progress")
        self.stage("NOPE-01", "--status", "done")
        r = self.apply_staged()
        self.assertEqual(1, r.returncode)
        self.assertEqual("in progress", self.item("W-01")["status"])
        self.assertEqual(1, len(list(self.staging.glob("*.json"))))

    def test_a_validation_failure_does_not_block_a_later_valid_file(self):
        """The cheap failure (unknown item) returns before touching the ledger
        dict; this is the expensive one, which mutates an item and only then
        fails validate(). Applying it to `data` itself left every later file
        validating against the poisoned copy, so the whole run failed on one
        bad file -- the opposite of what this command promises."""
        self.stage("W-01", "--status", "wip", "--at", "2026-01-01T10:00:00+00:00")
        self.stage("W-02", "--status", "done", "--at", "2026-01-01T11:00:00+00:00")
        r = self.apply_staged()
        self.assertEqual(1, r.returncode)
        self.assertEqual("done", self.item("W-02")["status"])
        self.assertEqual("not started", self.item("W-01")["status"])
        left = [p.name for p in self.staging.glob("*.json")]
        self.assertEqual(1, len(left), left)
        self.assertIn("W-01", left[0])

    def test_a_failed_file_leaves_none_of_its_own_changes_in_the_ledger(self):
        """The severe case: the failed file's OTHER mutations (its owner, its
        log entry) must not ride into the written ledger on the back of a
        later file that happens to make the ledger valid again."""
        self.stage("W-01", "--status", "wip", "--owner", "session:ghost",
                   "--event", "should never appear", "--at", "2026-01-01T10:00:00+00:00")
        self.stage("W-01", "--status", "done", "--at", "2026-01-01T11:00:00+00:00")
        r = self.apply_staged()
        self.assertEqual(1, r.returncode)
        item = self.item("W-01")
        self.assertEqual("done", item["status"])
        self.assertNotEqual("session:ghost", item.get("owner"))
        events = [e["event"] for e in item.get("log") or []]
        self.assertNotIn("should never appear", events)
        self.assertEqual(["done"], events)

    def test_nothing_staged_is_a_clean_no_op(self):
        r = self.apply_staged()
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("nothing staged", r.stdout)

    def test_multiple_changes_to_the_same_item_apply_in_order(self):
        self.stage("W-01", "--status", "in progress", "--at", "2026-01-01T10:00:00+00:00")
        self.stage("W-01", "--status", "done", "--at", "2026-01-01T11:00:00+00:00")
        r = self.apply_staged()
        self.assertEqual(0, r.returncode, r.stderr)
        item = self.item("W-01")
        self.assertEqual("done", item["status"])
        self.assertEqual(["in progress", "done"], [e["event"] for e in item["log"]])


if __name__ == "__main__":
    unittest.main()
