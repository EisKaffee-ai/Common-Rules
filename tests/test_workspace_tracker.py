from __future__ import annotations
import json, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "bin/workspace-tracker"


class WorkspaceTrackerTest(unittest.TestCase):
    def test_joined_page_keeps_repository_and_revision_identity(self):
        with tempfile.TemporaryDirectory() as td:
            hub = Path(td); member = hub / "engine"; (member / "docs/proposals").mkdir(parents=True)
            ledger = {"proposal": 1, "title": "Upload", "status": "accepted", "updated": "2026-10-03",
                      "tiers": {}, "phases": [], "items": [{"id": "F-01", "phase": "F", "cx": "C3",
                      "title": "Upload a photo", "status": "in progress"}], "traceability": [], "asks": []}
            (member / "docs/proposals/01-upload.json").write_text(json.dumps(ledger))
            (hub / "docs/common-rules").mkdir(parents=True)
            (hub / "docs/common-rules/workspace.json").write_text(json.dumps({"schema": 1,
                "workspace_id": "photos", "hub_repository_id": "docs", "members": [{
                "repository_id": "engine", "role": "business-logic", "remote": None,
                "manifest": ".common-rules.json", "tracker": "docs/proposals", "revision": "WORKING"}]}))
            (hub / ".common-rules").mkdir()
            (hub / ".common-rules/workspace.local.json").write_text(json.dumps({"workspace_id": "photos",
                "checkouts": {"engine": "engine"}}))
            result = subprocess.run([str(COMMAND), "--project", str(hub)], text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            page = (hub / "docs/common-rules/tracker.html").read_text()
            self.assertIn("Upload a photo", page)
            self.assertIn("engine", page)
            self.assertIn("WORKING", page)


if __name__ == "__main__": unittest.main()
