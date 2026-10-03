from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKER = ROOT / "bin/tracker"


class TrackerTraceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name) / "01-feature.json"
        self.ledger.write_text(json.dumps({
            "proposal": 1, "title": "Feature", "status": "accepted", "updated": "2026-10-03",
            "tiers": {}, "phases": [{"id": "F", "name": "Feature"}],
            "items": [{"id": "F-01", "phase": "F", "cx": "C1", "title": "Feature",
                       "status": "in review", "owner": "lead"}],
            "traceability": [{"id": "TR-01", "item": "F-01", "requirement_ids": ["R-01"],
                "guide_section": "docs/guide.md#r-01", "architecture_section": "docs/design.md#r-01",
                "implementation_files": ["src/feature.py"], "tests_commands": ["python3 -m unittest"],
                "receipt_or_refusal": "pending", "owner": "lead", "status": "in review"}],
            "asks": [], "proposed_changes": [], "execution": {},
        }))

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self, *args):
        return subprocess.run([str(TRACKER), "trace", str(self.ledger), *args], text=True, capture_output=True)

    def test_updates_receipt_and_status_and_renders(self):
        result = self.invoke("TR-01", "--status", "done", "--receipt", "receipt: suite green")
        self.assertEqual(0, result.returncode, result.stderr)
        data = json.loads(self.ledger.read_text())
        self.assertEqual("done", data["traceability"][0]["status"])
        self.assertEqual("receipt: suite green", data["traceability"][0]["receipt_or_refusal"])
        self.assertTrue((self.ledger.parent / "tracker/01-feature.html").is_file())

    def test_refuses_unknown_row_without_writing(self):
        before = self.ledger.read_bytes()
        result = self.invoke("TR-99", "--status", "done")
        self.assertEqual(1, result.returncode)
        self.assertEqual(before, self.ledger.read_bytes())

    def test_appends_generated_links_without_duplicates(self):
        result = self.invoke("TR-01", "--requirement", "R-02", "--requirement", "R-01",
                             "--implementation-file", "tools/feature.py",
                             "--test-command", "python3 -m unittest -q tests.test_feature")
        self.assertEqual(0, result.returncode, result.stderr)
        row = json.loads(self.ledger.read_text())["traceability"][0]
        self.assertEqual(["R-01", "R-02"], row["requirement_ids"])
        self.assertIn("tools/feature.py", row["implementation_files"])
        self.assertIn("python3 -m unittest -q tests.test_feature", row["tests_commands"])


if __name__ == "__main__":
    unittest.main()
