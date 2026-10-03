from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TrackerSkillTest(unittest.TestCase):
    def test_tracker_routes_proposal_issue_work_to_the_detailed_reference(self):
        text = (ROOT / "skills/tracker/SKILL.md").read_text()
        self.assertIn("proposal", text.lower())
        self.assertIn("references/proposal-issue-sync.md", text)
        self.assertIn("integrated GitHub", text)

    def test_issue_workflow_preflights_before_remote_mutation_and_records_results(self):
        text = (ROOT / "skills/tracker/references/proposal-issue-sync.md").read_text()
        normalized = " ".join(text.split())
        preflight = text.index("tracker sync --project . --output")
        mutate = text.index("Create or update issues")
        record = text.index("--record")
        self.assertLess(preflight, mutate)
        self.assertLess(mutate, record)
        self.assertIn("Do not use `gh`", text)
        self.assertIn("browser UI", text)
        self.assertIn("never changes ledger status", normalized)
        self.assertIn("close", text)
        self.assertIn("reopen", text)

    def test_setup_and_review_cover_the_optional_issue_contract(self):
        setup = (ROOT / "skills/setup/SKILL.md").read_text()
        review = (ROOT / "skills/review-and-verify/SKILL.md").read_text()
        review_normalized = " ".join(review.lower().split())
        for key in ("issue_repository", "issue_granularity", "issue_sync_direction"):
            self.assertIn(key, setup)
        self.assertIn("full-set", review)
        self.assertIn("one issue per proposal", review)
        self.assertIn("ledger remains authoritative", review_normalized)


if __name__ == "__main__":
    unittest.main()
