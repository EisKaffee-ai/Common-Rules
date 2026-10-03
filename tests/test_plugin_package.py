import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PluginPackageTest(unittest.TestCase):
    def test_portable_manifest_and_lifecycle_skills(self):
        manifest = json.loads((ROOT / "plugin.json").read_text())
        self.assertEqual((ROOT / "VERSION").read_text().strip(), manifest["version"])
        self.assertEqual("https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", manifest["$schema"])
        for name in ("setup", "calibrate", "intake", "tracker", "plan-and-route", "review-and-verify",
                     "repair", "land-handoff", "visual-proposal"):
            skill = ROOT / "skills" / name / "SKILL.md"
            self.assertTrue(skill.is_file(), name)
            text = skill.read_text()
            self.assertIn("name:", text)
            self.assertIn("description:", text)

    def test_plugin_hooks_are_portable_and_non_mutating(self):
        hooks = json.loads((ROOT / "hooks/hooks.json").read_text())
        commands = json.dumps(hooks)
        self.assertIn("CLAUDE_PLUGIN_ROOT", commands)
        self.assertNotIn("/Users/", commands)

    def test_claude_manifest_matches_the_portable_release(self):
        portable = json.loads((ROOT / "plugin.json").read_text())
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(portable["name"], claude["name"])
        self.assertEqual(portable["version"], claude["version"])
        self.assertNotIn("hooks", claude)  # standard hooks/hooks.json is auto-loaded once

    def test_claude_marketplace_installs_this_plugin(self):
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual("eiskaffee-common-rules", market["name"])
        entry = market["plugins"][0]
        self.assertEqual("common-rules", entry["name"])
        self.assertEqual("./", entry["source"])

    def test_hooks_are_noop_until_a_project_adopts_common_rules(self):
        with tempfile.TemporaryDirectory() as td:
            for action in ("doctor", "tracecheck"):
                result = subprocess.run([str(ROOT / "hooks/project-lifecycle"), action],
                                        cwd=td, text=True, capture_output=True)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual("", result.stdout)


if __name__ == "__main__":
    unittest.main()
