from __future__ import annotations

import tempfile
import unittest
import hashlib
import json
from pathlib import Path

from tools import release_evidence


class ReleaseEvidenceTest(unittest.TestCase):
    def receipt(self, root: Path, command=None, label="merge-gate") -> Path:
        log = root / "gate.log"
        log.write_text("Ran 12 tests in 1.000s\n\nOK\n\nRan 2084 tests in 176.439s\n\nOK\n")
        receipt = root / "receipt.json"
        receipt.write_text(json.dumps({"schema": 1, "kind": "common-rules-quiet-gate",
            "label": label, "status": "OK", "command": command or ["python3", "-m", "unittest",
            "discover", "-s", "tests", "-q"], "tests": 2084, "test_seconds": 176.439,
            "log": str(log), "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}))
        return receipt

    def test_successful_aggregate_log_updates_numbers(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt = self.receipt(root)
            doc = root / "README.md"
            doc.write_text("The final release gate passed all 2,065 tests in 189.1 seconds.\n"
                           "The final 2,065-test evidence landed.\n")
            count, seconds, _data = release_evidence.measurement(receipt)
            release_evidence.update(doc, count, seconds)
            self.assertEqual(2084, count)
            self.assertEqual(176.439, seconds)
            self.assertIn("final release gate passed all 2,084 tests in 176.4 seconds", doc.read_text())
            self.assertIn("final 2,084-test evidence", doc.read_text())

    def test_failed_log_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt = self.receipt(root, command=["python3", "-m", "unittest", "-q", "tests.test_one"])
            with self.assertRaisesRegex(ValueError, "not a successful full"):
                release_evidence.measurement(receipt)


if __name__ == "__main__":
    unittest.main()
