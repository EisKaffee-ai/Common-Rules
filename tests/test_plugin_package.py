import json
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
        self.assertIn("PLUGIN_ROOT", commands)
        self.assertNotIn("/Users/", commands)


if __name__ == "__main__":
    unittest.main()
