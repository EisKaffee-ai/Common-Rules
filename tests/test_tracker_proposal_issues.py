from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.tracker import proposal_issues


def item(item_id: str, status: str, feature: str, *, reason: str | None = None,
         issue=None, evidence: str = "") -> dict:
    row = {
        "id": item_id, "phase": item_id.split("-", 1)[0], "cx": "C2",
        "title": f"{feature} · {item_id}", "what": "Deliver the row",
        "feature": feature, "files": [], "tests": [], "done": "Evidence exists",
        "depends": [], "status": status, "owner": "lead", "tier": "medium",
        "model": "sonnet", "tag": "[ruflo · medium · sonnet]", "issue": issue,
        "log": ([{"at": "2026-10-03", "event": "verified", "by": "lead",
                  "evidence": evidence, "status": status}] if evidence else []),
    }
    if reason is not None:
        row["deferred_reason"] = reason
    return row


def ledger(number: int, title: str, feature: str, rows: list[dict], issue=None) -> dict:
    return {
        "proposal": number, "title": title, "namespace": feature.rsplit(".", 1)[0],
        "status": "accepted", "phases": [
            {"id": phase, "name": phase} for phase in sorted({r["phase"] for r in rows})
        ],
        "features": [{"key": feature, "name": feature.rsplit(".", 1)[-1].title(),
                      "gap": "Attach the missing receipt", "issue": issue,
                      "tests": ["repo:tests/test_feature.py"],
                      "affectedCode": [{"repository": "repo", "revision": "abc123",
                                        "path": "src/feature.py", "evidence": "pinned source"}]}],
        "items": rows, "asks": [], "traceability": [],
    }


class ProposalIssueTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.tracker = self.root / "content/proposals"
        self.tracker.mkdir(parents=True)
        (self.root / "docs/architecture").mkdir(parents=True)
        (self.root / "docs/common-rules").mkdir(parents=True)
        manifest = {"integration": {
            "repository_id": "docs", "role": "documentation",
            "requirements": ["docs/architecture"], "tracker": "content/proposals",
            "issue_linking": "one-way", "issue_repository": "EisKaffee-ai/bean-engine",
            "issue_granularity": "proposal", "issue_sync_direction": "ledger-to-github",
            "skill_receipts": True, "workspace": {"id": "product", "role": "hub"},
        }}
        (self.root / ".common-rules.json").write_text(json.dumps(manifest))
        workspace = {"schema": 1, "workspace_id": "product", "hub_repository_id": "docs",
                     "members": [
                         {"repository_id": "docs", "role": "documentation", "revision": "abc"},
                         {"repository_id": "bean-engine", "role": "business-logic", "revision": "def"},
                     ]}
        (self.root / "docs/common-rules/workspace.json").write_text(json.dumps(workspace))

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name: str, data: dict) -> Path:
        path = self.tracker / name
        path.write_text(json.dumps(data, indent=2) + "\n")
        return path

    def test_plan_has_one_group_issue_and_stable_status_checkboxes(self):
        issue = {"repository": "EisKaffee-ai/bean-engine", "number": 2,
                 "url": "https://github.com/EisKaffee-ai/bean-engine/issues/2"}
        self.write("08-engine-media.json", ledger(8, "Engine · Media access", "engine.media.preview", [
            item("D-01", "done", "engine.media.preview", evidence="receipt.json"),
            item("I-01", "in progress", "engine.media.preview"),
            item("V-01", "deferred", "engine.media.preview", reason="Superseded", evidence="decision.md"),
        ], issue=issue))
        plan = proposal_issues.build_plan(self.root)

        self.assertEqual(1, plan["preflight"]["groups"])
        self.assertEqual(3, plan["preflight"]["checkboxes"])
        group = plan["groups"][0]
        self.assertEqual(2, group["issue"]["number"])
        self.assertEqual("[Architecture 08/08] Engine · Media access", group["title"])
        self.assertIn("- [x] `D-01`", group["body"])
        self.assertIn("- [ ] `I-01`", group["body"])
        self.assertIn("in progress", group["body"])
        self.assertIn("- [x] `V-01`", group["body"])
        self.assertIn("Superseded", group["body"])
        self.assertEqual(["D-01", "I-01", "V-01"], [m["item_id"] for m in group["mappings"]])
        self.assertEqual("ledger-to-github", plan["direction"])
        self.assertRegex(plan["digest"], r"^[0-9a-f]{64}$")

    def test_deferred_without_reason_refuses_the_complete_plan(self):
        self.write("01-app.json", ledger(1, "Application · Consumer", "application.consumer", [
            item("D-01", "deferred", "application.consumer", evidence="decision.md"),
        ]))
        with self.assertRaisesRegex(ValueError, "deferred requires"):
            proposal_issues.build_plan(self.root)

    def test_conflicting_existing_issue_mappings_refuse_the_whole_plan(self):
        self.write("01-app.json", ledger(1, "Application · Consumer", "application.consumer", [
            item("D-01", "done", "application.consumer", issue=3, evidence="receipt"),
            item("V-01", "done", "application.consumer", issue=4, evidence="receipt"),
        ]))
        with self.assertRaisesRegex(ValueError, "conflicting issue mappings"):
            proposal_issues.build_plan(self.root)

    def test_one_remote_issue_cannot_be_shared_by_two_proposals(self):
        issue = {"repository": "EisKaffee-ai/bean-engine", "number": 7,
                 "url": "https://github.com/EisKaffee-ai/bean-engine/issues/7"}
        self.write("01-app.json", ledger(1, "Application · Consumer", "application.consumer", [
            item("D-01", "in progress", "application.consumer"),
        ], issue=issue))
        self.write("02-app.json", ledger(2, "Application · Request", "application.request", [
            item("D-01", "in progress", "application.request"),
        ], issue=issue))
        with self.assertRaisesRegex(ValueError, "issue #7 maps to proposals 1 and 2"):
            proposal_issues.build_plan(self.root)

    def test_record_mapping_assigns_one_identity_to_group_features_and_items(self):
        path = self.write("01-app.json", ledger(1, "Application · Consumer", "application.consumer", [
            item("D-01", "done", "application.consumer", evidence="receipt"),
            item("V-01", "in progress", "application.consumer"),
        ]))
        proposal_issues.record_mapping(
            self.root, path, 31, "https://github.com/EisKaffee-ai/bean-engine/issues/31"
        )
        saved = json.loads(path.read_text())
        self.assertEqual(31, saved["issue"]["number"])
        self.assertEqual({31}, {row["issue"] for row in saved["items"]})
        self.assertEqual(31, saved["features"][0]["issue"]["number"])
        self.assertEqual("done", saved["items"][0]["status"])
        self.assertEqual("receipt", saved["items"][0]["log"][0]["evidence"])

    def test_reconciliation_reports_remote_drift_without_changing_the_ledger(self):
        issue = {"repository": "EisKaffee-ai/bean-engine", "number": 2,
                 "url": "https://github.com/EisKaffee-ai/bean-engine/issues/2"}
        path = self.write("01-app.json", ledger(1, "Application · Consumer", "application.consumer", [
            item("D-01", "done", "application.consumer", evidence="receipt"),
        ], issue=issue))
        before = path.read_bytes()
        plan = proposal_issues.build_plan(self.root)
        drift = proposal_issues.reconcile(plan, [{
            "number": 2, "state": "open", "title": plan["groups"][0]["title"],
            "body": plan["groups"][0]["body"].replace("[x]", "[ ]"),
        }])
        self.assertTrue(any("body differs; ledger remains authoritative" in row for row in drift))
        self.assertEqual(before, path.read_bytes())


if __name__ == "__main__":
    unittest.main()
