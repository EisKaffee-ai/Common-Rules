from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACECHECK = ROOT / "bin" / "tracecheck"


def ledger(receipt="receipt: green", owner="lead"):
    return {"proposal": 1, "title": "Feature", "status": "accepted", "updated": "2026-10-03",
            "tiers": {"C3": {"tier": "high", "model": "sonnet", "effort": "high", "rule": "cross"}},
            "phases": [{"id": "F", "name": "Feature", "goal": "Ship", "exit": "Verified"}],
            "items": [{"id": "F-01", "phase": "F", "cx": "C3", "title": "Visible feature",
                       "status": "in progress", "owner": "lead"}],
            "traceability": [{"id": "TR-01", "item": "F-01", "requirement_ids": ["REQ-01"],
                              "guide_section": "docs/requirements/feature.md#req-01",
                              "architecture_section": "docs/design/feature.md#design",
                              "implementation_files": ["src/feature.py"],
                              "tests_commands": ["python3 -m unittest"],
                              "receipt_or_refusal": receipt, "owner": owner, "status": "in progress"}],
            "asks": [], "proposed_changes": [], "execution": {}}


class TracecheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name)
        for rel, body in (("docs/requirements/feature.md", "# Feature\n## REQ-01\n"),
                          ("docs/design/feature.md", "# Design\n## Design\n"),
                          ("src/feature.py", "VALUE = 1\n")):
            p = self.project / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(body)
        p = self.project / "docs/proposals/01-feature.json"; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(ledger()))
        (self.project / ".common-rules.json").write_text(json.dumps({"integration": {
            "repository_id": "engine", "role": "business-logic", "requirements": ["docs/requirements"],
            "tracker": "docs/proposals", "issue_linking": "off", "skill_receipts": True}}))

    def tearDown(self): self.tmp.cleanup()

    def invoke(self, *args):
        return subprocess.run([str(TRACECHECK), "--project", str(self.project), *args],
                              text=True, capture_output=True)

    def test_complete_graph_passes(self):
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("1 traceability row", result.stdout)

    def test_repository_qualified_file_uses_local_checkout_mapping(self):
        member = self.project / "vanilla"
        target = member / "lib/feature.py"
        target.parent.mkdir(parents=True)
        target.write_text("VALUE = 1\n")
        local = self.project / ".common-rules/workspace.local.json"
        local.parent.mkdir()
        local.write_text(json.dumps({"workspace_id": "photos", "checkouts": {"vanilla": str(member)}}))
        path = self.project / "docs/proposals/01-feature.json"
        data = ledger()
        data["traceability"][0]["implementation_files"] = ["vanilla:lib/feature.py"]
        path.write_text(json.dumps(data))
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_repository_qualified_implementation_directory_is_valid(self):
        member = self.project / "vanilla"
        target = member / "lib/work_tray"
        target.mkdir(parents=True)
        local = self.project / ".common-rules/workspace.local.json"
        local.parent.mkdir()
        local.write_text(json.dumps({"workspace_id": "photos", "checkouts": {"vanilla": str(member)}}))
        path = self.project / "docs/proposals/01-feature.json"
        data = ledger()
        data["traceability"][0]["implementation_files"] = ["vanilla:lib/work_tray/"]
        path.write_text(json.dumps(data))
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_repository_qualified_file_without_mapping_is_refused(self):
        path = self.project / "docs/proposals/01-feature.json"
        data = ledger()
        data["traceability"][0]["implementation_files"] = ["vanilla:lib/feature.py"]
        path.write_text(json.dumps(data))
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("repository checkout is not mapped for vanilla:lib/feature.py", result.stdout)

    def test_repository_qualified_change_uses_declared_member_revision(self):
        member = self.project / "vanilla"
        target = member / "lib/feature.py"
        target.parent.mkdir(parents=True)
        target.write_text("VALUE = 1\n")
        subprocess.run(["git", "init", "-q"], cwd=member, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=member, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=member, check=True)
        subprocess.run(["git", "add", "."], cwd=member, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=member, check=True)
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=member, check=True,
                                  text=True, capture_output=True).stdout.strip()
        local = self.project / ".common-rules/workspace.local.json"
        local.parent.mkdir()
        local.write_text(json.dumps({"workspace_id": "photos", "checkouts": {"vanilla": str(member)}}))
        workspace = self.project / "docs/common-rules/workspace.json"
        workspace.parent.mkdir(parents=True, exist_ok=True)
        workspace.write_text(json.dumps({"workspace_id": "photos", "members": [{
            "repository_id": "vanilla", "revision": revision}]}))
        path = self.project / "docs/proposals/01-feature.json"
        data = ledger()
        data["traceability"][0]["implementation_files"] = ["vanilla:lib/feature.py"]
        path.write_text(json.dumps(data))
        target.write_text("VALUE = 2\n")
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("vanilla:lib/feature.py changed without requirement", result.stdout)
        data["traceability"][0]["receipt_or_refusal"] = "no-change: reviewed compatible"
        path.write_text(json.dumps(data))
        self.assertEqual(0, self.invoke().returncode)

    def test_hook_mode_accepts_hub_ledger_update_for_member_change(self):
        member_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(member_tmp.cleanup)
        member = Path(member_tmp.name)
        target = member / "lib/feature.py"
        target.parent.mkdir(parents=True); target.write_text("VALUE = 1\n")
        subprocess.run(["git", "init", "-q"], cwd=member, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=member, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=member, check=True)
        subprocess.run(["git", "add", "."], cwd=member, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=member, check=True)
        member_revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=member, check=True,
                                         text=True, capture_output=True).stdout.strip()
        path = self.project / "docs/proposals/01-feature.json"
        data = ledger(); data["traceability"][0]["implementation_files"] = ["vanilla:lib/feature.py"]
        path.write_text(json.dumps(data))
        local = self.project / ".common-rules/workspace.local.json"
        local.parent.mkdir(); local.write_text(json.dumps({"workspace_id": "photos", "checkouts": {
            "engine": ".", "vanilla": str(member)}}))
        workspace = self.project / "docs/common-rules/workspace.json"
        workspace.parent.mkdir(parents=True, exist_ok=True)
        workspace.write_text(json.dumps({"workspace_id": "photos", "members": [
            {"repository_id": "engine", "revision": "WORKING"},
            {"repository_id": "vanilla", "revision": member_revision}]}))
        subprocess.run(["git", "init", "-q"], cwd=self.project, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=self.project, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.project, check=True)
        subprocess.run(["git", "add", "."], cwd=self.project, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=self.project, check=True)
        target.write_text("VALUE = 2\n")
        self.assertEqual(1, self.invoke().returncode)
        data["traceability"][0]["receipt_or_refusal"] = "receipt: member and requirement reviewed"
        path.write_text(json.dumps(data))
        self.assertEqual(0, self.invoke().returncode)

    def test_missing_linked_file_fails_by_name(self):
        (self.project / "src/feature.py").unlink()
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("src/feature.py does not exist", result.stdout)

    def test_no_change_receipt_requires_a_lead_or_sponsor(self):
        path = self.project / "docs/proposals/01-feature.json"
        path.write_text(json.dumps(ledger("no-change: API unchanged", "session:builder")))
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("no-change receipt requires owner lead or sponsor", result.stdout)

    def test_changed_linked_file_requires_trace_evidence_in_same_change(self):
        subprocess.run(["git", "init", "-q"], cwd=self.project, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=self.project, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.project, check=True)
        subprocess.run(["git", "add", "."], cwd=self.project, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=self.project, check=True)
        (self.project / "src/feature.py").write_text("VALUE = 2\n")
        result = self.invoke("--base", "HEAD")
        self.assertEqual(1, result.returncode)
        self.assertIn("changed without requirement, ledger, or reviewed no-change evidence", result.stdout)
        path = self.project / "docs/proposals/01-feature.json"
        data = json.loads(path.read_text()); data["traceability"][0]["receipt_or_refusal"] = "no-change: behavior remains compatible"
        path.write_text(json.dumps(data))
        self.assertEqual(0, self.invoke("--base", "HEAD").returncode)


if __name__ == "__main__":
    unittest.main()
