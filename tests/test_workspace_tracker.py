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

    def test_proposal_hub_uses_canonical_board_instead_of_a_second_tracker(self):
        with tempfile.TemporaryDirectory() as td:
            hub = Path(td)
            ledgers = hub / "content/proposals"; ledgers.mkdir(parents=True)
            (hub / "docs/architecture").mkdir(parents=True)
            (hub / "docs/common-rules").mkdir(parents=True)
            (hub / ".common-rules.json").write_text(json.dumps({"integration": {
                "repository_id": "docs", "role": "documentation",
                "requirements": ["docs/architecture"], "tracker": "content/proposals",
                "issue_linking": "one-way", "issue_repository": "EisKaffee-ai/bean-engine",
                "issue_granularity": "proposal", "issue_sync_direction": "ledger-to-github",
                "skill_receipts": True, "workspace": {"id": "photos", "role": "hub"},
            }}))
            (hub / "docs/common-rules/workspace.json").write_text(json.dumps({"schema": 1,
                "workspace_id": "photos", "hub_repository_id": "docs", "members": [{
                    "repository_id": "docs", "role": "documentation", "revision": "abc",
                    "tracker": "content/proposals"}]}))
            (ledgers / "01-upload.json").write_text(json.dumps({
                "proposal": 1, "title": "Application · Upload", "namespace": "application.upload",
                "status": "accepted", "updated": "2026-10-03", "tiers": {}, "phases": [],
                "features": [], "items": [], "traceability": [], "asks": []}))

            result = subprocess.run([str(COMMAND), "--project", str(hub)], text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((ledgers / "tracker/index.html").is_file())
            self.assertFalse((hub / "docs/common-rules/tracker.html").exists())
            self.assertIn("single canonical tracker", result.stdout)


if __name__ == "__main__": unittest.main()
