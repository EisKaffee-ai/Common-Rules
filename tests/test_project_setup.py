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

    def test_doctor_names_invalid_or_missing_paths(self):
        declaration = {"integration": {"repository_id": "engine", "role": "business-logic",
                                        "requirements": ["missing"], "tracker": "also-missing",
                                        "issue_linking": "off", "skill_receipts": True}}
        (self.project / ".common-rules.json").write_text(json.dumps(declaration))
        result = self.invoke("doctor")
        self.assertEqual(1, result.returncode)
        self.assertIn("requirements path does not exist", result.stdout)
        self.assertIn("tracker path does not exist", result.stdout)


if __name__ == "__main__":
    unittest.main()
