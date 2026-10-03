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

    def test_joined_page_accepts_absolute_ignored_checkout_mapping(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as md:
            hub = Path(td); member = Path(md); (member / "docs/proposals").mkdir(parents=True)
            (member / "docs/proposals/01-upload.json").write_text(json.dumps({
                "proposal": 1, "title": "Upload", "status": "accepted", "items": [
                    {"id": "F-01", "title": "Upload a photo", "status": "in progress"}]}))
            (hub / "docs/common-rules").mkdir(parents=True)
            (hub / "docs/common-rules/workspace.json").write_text(json.dumps({"schema": 1,
                "workspace_id": "photos", "hub_repository_id": "docs", "members": [{
                    "repository_id": "engine", "role": "business-logic", "revision": "abc",
                    "tracker": "docs/proposals"}]}))
            (hub / ".common-rules").mkdir()
            (hub / ".common-rules/workspace.local.json").write_text(json.dumps({
                "workspace_id": "photos", "checkouts": {"engine": str(member)}}))
            result = subprocess.run([str(COMMAND), "--project", str(hub)], text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("Upload a photo", (hub / "docs/common-rules/tracker.html").read_text())

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
                    "repository_id": "docs", "role": "documentation", "revision": "WORKING",
                    "tracker": "content/proposals"}]}))
            (hub / ".common-rules").mkdir()
            (hub / ".common-rules/workspace.local.json").write_text(json.dumps({
                "workspace_id": "photos", "checkouts": {"docs": "."}}))
            (ledgers / "01-upload.json").write_text(json.dumps({
                "proposal": 1, "title": "Application · Upload", "namespace": "application.upload",
                "status": "accepted", "updated": "2026-10-03", "tiers": {}, "phases": [],
                "features": [], "items": [], "traceability": [], "asks": []}))

            result = subprocess.run([str(COMMAND), "--project", str(hub)], text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((ledgers / "tracker/index.html").is_file())
            self.assertFalse((hub / "docs/common-rules/tracker.html").exists())
            self.assertIn("single canonical tracker", result.stdout)
            strict = subprocess.run([str(COMMAND), "--project", str(hub), "--check"],
                                    text=True, capture_output=True)
            self.assertEqual(2, strict.returncode)
            self.assertIn("must pin a commit revision", strict.stdout)

    def test_proposal_hub_refuses_missing_member_checkout_and_wrong_revision(self):
        with tempfile.TemporaryDirectory() as td:
            hub = Path(td)
            (hub / "content/proposals").mkdir(parents=True)
            (hub / "docs/architecture").mkdir(parents=True)
            (hub / "docs/common-rules").mkdir(parents=True)
            (hub / ".common-rules").mkdir()
            (hub / ".common-rules.json").write_text(json.dumps({"integration": {
                "repository_id": "docs", "role": "documentation",
                "requirements": ["docs/architecture"], "tracker": "content/proposals",
                "issue_linking": "one-way", "issue_repository": "EisKaffee-ai/bean-engine",
                "issue_granularity": "proposal", "issue_sync_direction": "ledger-to-github",
                "skill_receipts": True, "workspace": {"id": "photos", "role": "hub"}}}))
            (hub / "docs/common-rules/workspace.json").write_text(json.dumps({"schema": 1,
                "workspace_id": "photos", "hub_repository_id": "docs", "members": [{
                    "repository_id": "docs", "role": "documentation", "revision": "deadbeef"}]}))
            (hub / ".common-rules/workspace.local.json").write_text(json.dumps({
                "workspace_id": "photos", "checkouts": {}}))
            missing = subprocess.run([str(COMMAND), "--project", str(hub)], text=True, capture_output=True)
            self.assertEqual(2, missing.returncode)
            self.assertIn("local checkout is not mapped", missing.stdout)
            local = json.loads((hub / ".common-rules/workspace.local.json").read_text())
            local["checkouts"]["docs"] = "."
            (hub / ".common-rules/workspace.local.json").write_text(json.dumps(local))
            wrong = subprocess.run([str(COMMAND), "--project", str(hub)], text=True, capture_output=True)
            self.assertEqual(2, wrong.returncode)
            self.assertIn("is not at revision deadbeef", wrong.stdout)

    def test_proposal_check_refuses_dirty_pinned_checkout(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as cd:
            hub, checkout = Path(td), Path(cd)
            (hub / "content/proposals").mkdir(parents=True)
            (hub / "docs/architecture").mkdir(parents=True)
            (hub / "docs/common-rules").mkdir(parents=True)
            (hub / ".common-rules").mkdir()
            (hub / ".common-rules.json").write_text(json.dumps({"integration": {
                "repository_id": "docs", "role": "documentation",
                "requirements": ["docs/architecture"], "tracker": "content/proposals",
                "issue_linking": "one-way", "issue_repository": "EisKaffee-ai/bean-engine",
                "issue_granularity": "proposal", "issue_sync_direction": "ledger-to-github",
                "skill_receipts": True, "workspace": {"id": "photos", "role": "hub"}}}))
            subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=checkout, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=checkout, check=True)
            (checkout / "tracked.txt").write_text("clean\n")
            subprocess.run(["git", "add", "."], cwd=checkout, check=True)
            subprocess.run(["git", "commit", "-qm", "baseline"], cwd=checkout, check=True)
            revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=checkout, check=True,
                                      text=True, capture_output=True).stdout.strip()
            (hub / "docs/common-rules/workspace.json").write_text(json.dumps({"schema": 1,
                "workspace_id": "photos", "hub_repository_id": "docs", "members": [{
                    "repository_id": "docs", "role": "documentation", "revision": revision}]}))
            (hub / ".common-rules/workspace.local.json").write_text(json.dumps({
                "workspace_id": "photos", "checkouts": {"docs": str(checkout)}}))
            (checkout / "tracked.txt").write_text("dirty\n")
            result = subprocess.run([str(COMMAND), "--project", str(hub), "--check"],
                                    text=True, capture_output=True)
            self.assertEqual(2, result.returncode)
            self.assertIn("checkout is dirty", result.stdout)


if __name__ == "__main__": unittest.main()
