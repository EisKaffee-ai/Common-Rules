from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class ReadmeLandingTest(unittest.TestCase):
    def setUp(self):
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_landing_page_uses_only_common_rules_identity(self):
        self.assertIn("# EisKaffee.ai / Common Rules", self.readme)
        self.assertNotIn("Emberline", self.readme)
        self.assertNotIn("emberline", self.readme.lower())

    def test_codex_and_claude_install_paths_are_visible(self):
        self.assertIn("codex plugin marketplace add EisKaffee-ai/Common-Rules", self.readme)
        self.assertIn("claude plugin marketplace add EisKaffee-ai/Common-Rules", self.readme)
        self.assertIn("claude plugin install common-rules@eiskaffee-common-rules", self.readme)
        self.assertIn("/common-rules:setup", self.readme)

    def test_every_readme_image_exists_and_has_current_identity(self):
        images = re.findall(r"!\[[^]]*\]\((docs/assets/[^)]+)\)", self.readme)
        self.assertGreaterEqual(len(images), 3)
        for relative in images:
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            if path.suffix == ".svg":
                text = path.read_text(encoding="utf-8")
                self.assertIn("Common Rules", text, relative)
                self.assertNotIn("EMBERLINE", text, relative)

    def test_landing_visuals_explain_hosts_lifecycle_and_tracker(self):
        expected = {
            "docs/assets/product-overview.svg": ("Codex", "Claude Code", "Common Rules"),
            "docs/assets/host-setup.svg": ("Codex", "Claude Code", "/common-rules:setup"),
            "docs/assets/skills-map.svg": ("setup", "visual-proposal", "tracker", "repair", "land-handoff"),
            "docs/assets/warmup-reheat-hero.svg": ("warmup", "reheat", "Common Rules"),
            "docs/assets/delivery-lifecycle.svg": ("visual proposal", "requirements", "independent review", "release", "evidence"),
            "docs/assets/tracker-coherence.svg": ("requirements", "files", "tests"),
        }
        for relative, words in expected.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            for word in words:
                self.assertIn(word, text, relative)

    def test_skill_catalog_has_examples_for_the_complete_delivery_path(self):
        skills = (
            "setup",
            "calibrate",
            "intake",
            "visual-proposal",
            "tracker",
            "plan-and-route",
            "review-and-verify",
            "repair",
            "land-handoff",
            "warmup",
            "reheat",
            "preheat",
        )
        for skill in skills:
            self.assertIn(f"`{skill}`", self.readme)
        self.assertIn("### Example: one repository", self.readme)
        self.assertIn("### Example: several repositories", self.readme)
        self.assertIn("### Example: a traceability failure", self.readme)

    def test_companion_pages_use_current_identity_and_visuals(self):
        pages = (
            "docs/readme-preview.html",
            "docs/warmup-reheat.html",
            "docs/public-review.html",
        )
        for relative in pages:
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("Common Rules", text, relative)
            self.assertNotIn("Emberline", text, relative)
            self.assertNotIn("tracker-overview-edited.png", text, relative)
            self.assertIn("assets/skills-map.svg", text, relative)


if __name__ == "__main__":
    unittest.main()
