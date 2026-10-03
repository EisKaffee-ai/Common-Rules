from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKER = ROOT / "bin/tracker"


def row(item_id: str, status: str, feature: str, *, issue=2) -> dict:
    return {
        "id": item_id, "phase": item_id.split("-", 1)[0], "cx": "C2",
        "title": f"{feature} · {item_id}", "what": "deliver", "feature": feature,
        "files": [], "tests": [], "done": "verified", "depends": [],
        "status": status, "owner": "lead", "tier": "medium", "model": "sonnet",
        "tag": "[ruflo · medium · sonnet]", "issue": issue,
        "log": [{"at": "2026-10-03", "event": status, "by": "lead",
                 "evidence": "receipt.json", "status": status}],
    }


class CanonicalArchitectureBoardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ledgers = self.root / "content/proposal/delivery/docs/proposals"
        self.ledgers.mkdir(parents=True)
        (self.root / "docs/architecture").mkdir(parents=True)
        (self.root / "docs/common-rules").mkdir(parents=True)
        manifest = {"integration": {
            "repository_id": "docs", "role": "documentation",
            "requirements": ["docs/architecture"],
            "tracker": "content/proposal/delivery/docs/proposals",
            "issue_linking": "one-way", "issue_repository": "EisKaffee-ai/bean-engine",
            "issue_granularity": "proposal", "issue_sync_direction": "ledger-to-github",
            "issue_series": "documentation-delivery",
            "skill_receipts": True, "workspace": {"id": "eiskaffee-vanilla", "role": "hub"},
        }}
        (self.root / ".common-rules.json").write_text(json.dumps(manifest))
        workspace = {"schema": 1, "workspace_id": "eiskaffee-vanilla", "hub_repository_id": "docs",
                     "members": [
                         {"repository_id": "docs", "role": "documentation", "tracker": "content/proposals", "revision": "abc"},
                         {"repository_id": "vanilla", "role": "interface", "tracker": "docs/proposals", "revision": "def"},
                         {"repository_id": "bean-engine", "role": "business-logic", "tracker": "docs/proposals", "revision": "123"},
                         {"repository_id": "ui-assets", "role": "assets", "tracker": "docs/proposals", "revision": "456"},
                     ]}
        (self.root / "docs/common-rules/workspace.json").write_text(json.dumps(workspace))
        issue = {"repository": "EisKaffee-ai/bean-engine", "number": 2,
                 "url": "https://github.com/EisKaffee-ai/bean-engine/issues/2"}
        data = {
            "proposal": 8, "title": "Engine · Media access & rendition", "namespace": "engine.media",
            "series": "documentation-delivery",
            "status": "accepted", "updated": "2026-10-03", "tiers": {},
            "phases": [{"id": "D", "name": "Design"}, {"id": "I", "name": "Implementation"}],
            "features": [
                {"key": "engine.media.preview", "name": "Photo previews", "issue": issue,
                 "approval": {"status": "accepted"}, "alignment": {"status": "partial"},
                 "gap": "Attach installed-pair receipt", "affectedCode": [
                     {"repository": "bean-engine", "revision": "123", "path": "bean/media.py"}]},
                {"key": "engine.media.document", "name": "Document previews", "issue": issue,
                 "approval": {"status": "pending"}, "alignment": {"status": "missing"},
                 "gap": "Implement document preview"},
            ],
            "items": [row("D-01", "done", "engine.media.preview"),
                      row("I-01", "in progress", "engine.media.preview"),
                      row("D-02", "blocked", "engine.media.document")],
            "asks": [], "traceability": [{
                "id": "TR-01", "item": "I-01", "requirement_ids": ["MEDIA-R01"],
                "guide_section": "docs/guide.md#preview", "architecture_section": "docs/architecture/media.md",
                "implementation_files": ["bean-engine:bean/media.py"],
                "tests_commands": ["pytest tests/test_media.py"], "receipt_or_refusal": "pending",
                "owner": "lead", "status": "in progress"}],
        }
        (self.ledgers / "08-engine-media.json").write_text(json.dumps(data, indent=2) + "\n")
        operations = {
            "proposal": 28, "title": "Vanilla · Focused findings", "series": "project-operations",
            "status": "accepted", "phases": [{"id": "U", "name": "UI"}],
            "items": [row("U-01", "in progress", "ui.library.timeline", issue=None)],
            "asks": [], "traceability": [],
        }
        (self.ledgers / "28-project-operations.json").write_text(json.dumps(operations, indent=2) + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_nested_canonical_tracker_has_five_visual_information_views(self):
        result = subprocess.run([sys.executable, str(TRACKER), "board", "--project", str(self.root)],
                                text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        page = self.ledgers / "tracker/index.html"
        self.assertTrue(page.is_file())
        self.assertFalse((self.root / "docs/proposals/tracker/index.html").exists())
        text = page.read_text()
        for view in ("Overview", "Product delivery", "Architecture", "Repositories", "Evidence"):
            self.assertIn(f">{view}<", text)
        self.assertIn("1 layer · 1 architecture group · 2 features · 3 lifecycle steps", text)
        self.assertNotIn("tracked tasks", text)
        self.assertIn('data-layer="Engine"', text)
        self.assertIn('data-layer="Project Operations"', text)
        self.assertIn("Issue sync excluded", text)
        self.assertIn("2 features", text)
        self.assertIn("1/3 rows complete", text)
        self.assertIn("accepted / pending", text)
        self.assertIn("partial / missing", text)
        self.assertIn("Attach installed-pair receipt", text)
        self.assertIn("Implement document preview", text)
        self.assertIn("https://github.com/EisKaffee-ai/bean-engine/issues/2", text)
        for repository in ("docs", "vanilla", "bean-engine", "ui-assets"):
            self.assertIn(f'data-repository="{repository}"', text)
        self.assertIn("MEDIA-R01", text)


if __name__ == "__main__":
    unittest.main()
