from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETUP = ROOT / "bin" / "project-setup"


class ProjectSetupTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name)
        (self.project / "docs" / "requirements").mkdir(parents=True)
        (self.project / "docs" / "proposals").mkdir(parents=True)
        (self.project / "README.md").write_text("# Example\n")

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self, *args):
        return subprocess.run([str(SETUP), "--project", str(self.project), *args],
                              text=True, capture_output=True)

    def test_preview_discovers_but_does_not_write(self):
        result = self.invoke("preview", "--repository-id", "engine", "--role", "business-logic")
        self.assertEqual(0, result.returncode, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual("engine", data["integration"]["repository_id"])
        self.assertEqual(["docs/requirements"], data["integration"]["requirements"])
        self.assertFalse((self.project / ".common-rules.json").exists())

    def test_preview_prefers_existing_nested_ledger_catalogue(self):
        canonical = self.project / "content/proposal/delivery/docs/proposals"
        canonical.mkdir(parents=True)
        for number in range(1, 28):
            (canonical / f"{number:02d}-group.json").write_text(json.dumps({
                "proposal": number, "title": f"Group {number}", "items": []
            }))
        generated = self.project / "build/proposal/delivery/docs/proposals"
        generated.mkdir(parents=True)
        for number in range(1, 28):
            (generated / f"{number:02d}-group.json").write_text(json.dumps({
                "proposal": number, "title": f"Generated {number}", "items": []
            }))

        result = self.invoke("preview", "--repository-id", "docs", "--role", "documentation")
        self.assertEqual(0, result.returncode, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual("content/proposal/delivery/docs/proposals", data["integration"]["tracker"])

    def test_preview_adds_proposal_issue_contract(self):
        result = self.invoke(
            "preview", "--repository-id", "docs", "--role", "documentation",
            "--issue-linking", "one-way",
            "--issue-repository", "EisKaffee-ai/bean-engine",
            "--issue-granularity", "proposal",
            "--issue-sync-direction", "ledger-to-github",
            "--issue-series", "documentation-delivery",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        integration = json.loads(result.stdout)["integration"]
        self.assertEqual("EisKaffee-ai/bean-engine", integration["issue_repository"])
        self.assertEqual("proposal", integration["issue_granularity"])
        self.assertEqual("ledger-to-github", integration["issue_sync_direction"])
        self.assertEqual("documentation-delivery", integration["issue_series"])

    def test_preview_refuses_an_incomplete_or_reverse_issue_contract(self):
        incomplete = self.invoke(
            "preview", "--issue-linking", "one-way",
            "--issue-repository", "EisKaffee-ai/bean-engine",
        )
        self.assertEqual(2, incomplete.returncode)
        self.assertIn("requires issue_repository", incomplete.stdout)

        reverse = self.invoke(
            "preview", "--issue-linking", "one-way",
            "--issue-repository", "EisKaffee-ai/bean-engine",
            "--issue-granularity", "proposal",
            "--issue-sync-direction", "github-to-ledger",
        )
        self.assertEqual(2, reverse.returncode)

    def test_apply_preserves_existing_declaration(self):
        original = {"gates": {"quick": "true"}, "unknown_future_key": {"keep": True}}
        (self.project / ".common-rules.json").write_text(json.dumps(original))
        result = self.invoke("apply", "--repository-id", "engine", "--role", "business-logic")
        self.assertEqual(0, result.returncode, result.stderr)
        data = json.loads((self.project / ".common-rules.json").read_text())
        self.assertEqual(original["gates"], data["gates"])
        self.assertEqual(original["unknown_future_key"], data["unknown_future_key"])
        self.assertEqual("engine", data["integration"]["repository_id"])

    def test_workspace_hub_writes_portable_and_ignored_local_manifests(self):
        result = self.invoke("apply", "--repository-id", "docs", "--role", "documentation",
                          "--workspace-id", "product", "--workspace-role", "hub")
        self.assertEqual(0, result.returncode, result.stderr)
        hub = json.loads((self.project / "docs/common-rules/workspace.json").read_text())
        self.assertEqual("product", hub["workspace_id"])
        self.assertEqual("docs", hub["hub_repository_id"])
        self.assertTrue((self.project / ".common-rules/workspace.local.json").exists())
        self.assertIn(".common-rules/workspace.local.json", (self.project / ".gitignore").read_text())

    def test_workspace_hub_records_explicit_member_checkout_locally(self):
        member = self.project / "vanilla"
        member.mkdir()
        result = self.invoke("apply", "--repository-id", "docs", "--role", "documentation",
                             "--workspace-id", "product", "--workspace-role", "hub",
                             "--checkout", f"vanilla={member}")
        self.assertEqual(0, result.returncode, result.stderr)
        local = json.loads((self.project / ".common-rules/workspace.local.json").read_text())
        self.assertEqual(str(member), local["checkouts"]["vanilla"])

    def test_apply_refuses_bad_checkout_before_writing_any_manifest(self):
        manifest = self.project / ".common-rules.json"
        manifest.write_text('{"keep": "original"}\n')
        before = manifest.read_bytes()
        result = self.invoke("apply", "--repository-id", "docs", "--role", "documentation",
                             "--workspace-id", "product", "--workspace-role", "hub",
                             "--checkout", "not-a-pair")
        self.assertEqual(2, result.returncode)
        self.assertEqual(before, manifest.read_bytes())
        self.assertFalse((self.project / ".common-rules/workspace.local.json").exists())

    def test_doctor_names_invalid_or_missing_paths(self):
        declaration = {"integration": {"repository_id": "engine", "role": "business-logic",
                                        "requirements": ["missing"], "tracker": "also-missing",
                                        "issue_linking": "off", "skill_receipts": True}}
        (self.project / ".common-rules.json").write_text(json.dumps(declaration))
        result = self.invoke("doctor")
        self.assertEqual(1, result.returncode)
        self.assertIn("requirements path does not exist", result.stdout)
        self.assertIn("tracker path does not exist", result.stdout)

    def test_doctor_refuses_incomplete_proposal_issue_contract(self):
        declaration = {"integration": {"repository_id": "docs", "role": "documentation",
            "requirements": ["docs/requirements"], "tracker": "docs/proposals",
            "issue_linking": "one-way", "issue_series": "documentation-delivery",
            "skill_receipts": True}}
        (self.project / ".common-rules.json").write_text(json.dumps(declaration))
        result = self.invoke("doctor")
        self.assertEqual(1, result.returncode)
        self.assertIn("requires the complete proposal issue contract", result.stdout)


if __name__ == "__main__":
    unittest.main()
