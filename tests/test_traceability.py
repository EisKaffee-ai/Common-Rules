from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "bin" / "traceability"


class TraceabilityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name)
        self.repo = self.project / "checkout"
        (self.repo / "src").mkdir(parents=True)
        (self.repo / "reports").mkdir()
        (self.repo / "src/flow.py").write_text(
            "def import_photo():\n"
            "    return store_photo()\n\n"
            "# TRACE CODE-STORE START\n"
            "def store_photo():\n"
            "    return 'stored'\n"
            "# TRACE CODE-STORE END\n",
            encoding="utf-8",
        )
        (self.repo / "reports/latest.json").write_text(
            json.dumps({"runner": "unittest", "status": "passed"}), encoding="utf-8"
        )
        self._git("init", "-q")
        self._git("config", "user.email", "test@example.invalid")
        self._git("config", "user.name", "Test")
        self._git("add", ".")
        self._git("commit", "-qm", "fixture")
        self.revision = self._git("rev-parse", "HEAD").stdout.strip()
        local = self.project / ".common-rules/workspace.local.json"
        local.parent.mkdir()
        local.write_text(json.dumps({"checkouts": {"app": str(self.repo)}}), encoding="utf-8")
        self.manifest_path = self.project / "docs/common-rules/traceability.json"
        self.manifest_path.parent.mkdir(parents=True)
        self.manifest = self._manifest()
        self._write_manifest()

    def tearDown(self):
        self.tmp.cleanup()

    def _git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.repo, text=True, capture_output=True, check=True
        )

    def _manifest(self):
        return {
            "schema_version": 1,
            "reviewed": {
                "by": "architecture-review",
                "at": "2026-10-03T12:00:00+02:00",
                "status": "accepted",
            },
            "output": "docs/traceability/index.html",
            "repositories": [
                {
                    "id": "app",
                    "revision": self.revision,
                    "scan": {"include": ["**/*.py", "reports/*.json"], "exclude": []},
                }
            ],
            "features": [
                {
                    "id": "FEAT-PHOTO-IMPORT",
                    "title": "Photo import",
                    "requirements": [
                        {
                            "id": "REQ-PHOTO-IMPORT",
                            "text": "Import and persist a photo",
                        }
                    ],
                    "workflow": {
                        "expected_nodes": [
                            {"id": "WFN-IMPORT", "label": "Import"},
                            {"id": "WFN-STORE", "label": "Store"},
                        ],
                        "expected_edges": [
                            {
                                "id": "WFE-IMPORT-STORE",
                                "from": "WFN-IMPORT",
                                "to": "WFN-STORE",
                            }
                        ],
                        "actual_nodes": [
                            {
                                "id": "WFN-IMPORT",
                                "code_anchor_ids": ["CODE-IMPORT"],
                                "status": "accepted",
                            },
                            {
                                "id": "WFN-STORE",
                                "code_anchor_ids": ["CODE-STORE"],
                                "status": "accepted",
                            },
                        ],
                        "actual_edges": [
                            {
                                "id": "WFE-IMPORT-STORE",
                                "code_anchor_ids": ["CODE-FLOW"],
                                "status": "accepted",
                            }
                        ],
                    },
                    "code_anchors": [
                        {
                            "id": "CODE-IMPORT",
                            "repository": "app",
                            "revision": self.revision,
                            "path": "src/flow.py",
                            "symbol": "import_photo",
                        },
                        {
                            "id": "CODE-STORE",
                            "repository": "app",
                            "revision": self.revision,
                            "path": "src/flow.py",
                            "region": {
                                "start": "# TRACE CODE-STORE START",
                                "end": "# TRACE CODE-STORE END",
                            },
                        },
                        {
                            "id": "CODE-FLOW",
                            "repository": "app",
                            "revision": self.revision,
                            "path": "src/flow.py",
                            "whole_file": True,
                        },
                    ],
                    "test_cases": [
                        {
                            "id": "TEST-PHOTO-IMPORT",
                            "requirement_ids": ["REQ-PHOTO-IMPORT"],
                            "code_anchor_ids": ["CODE-IMPORT", "CODE-STORE"],
                        }
                    ],
                    "test_reports": [
                        {
                            "id": "REPORT-PHOTO-IMPORT-20261003",
                            "repository": "app",
                            "revision": self.revision,
                            "path": "reports/latest.json",
                            "generated_at": "2026-10-03T12:30:00+02:00",
                            "results": [
                                {"test_case_id": "TEST-PHOTO-IMPORT", "status": "passed"}
                            ],
                        }
                    ],
                    "issues": [
                        {
                            "id": "ISSUE-PHOTO-IMPORT",
                            "url": "https://example.invalid/issues/1",
                            "status": "open",
                        }
                    ],
                    "receipts": [
                        {
                            "id": "RECEIPT-PHOTO-IMPORT",
                            "kind": "review",
                            "status": "accepted",
                            "evidence_ids": ["REPORT-PHOTO-IMPORT-20261003"],
                        }
                    ],
                    "mappings": [
                        {
                            "id": "MAP-PHOTO-IMPORT",
                            "status": "accepted",
                            "requirement_ids": ["REQ-PHOTO-IMPORT"],
                            "workflow_node_ids": ["WFN-IMPORT", "WFN-STORE"],
                            "workflow_edge_ids": ["WFE-IMPORT-STORE"],
                            "code_anchor_ids": ["CODE-IMPORT", "CODE-STORE", "CODE-FLOW"],
                            "test_case_ids": ["TEST-PHOTO-IMPORT"],
                            "test_report_ids": ["REPORT-PHOTO-IMPORT-20261003"],
                            "issue_ids": ["ISSUE-PHOTO-IMPORT"],
                            "receipt_ids": ["RECEIPT-PHOTO-IMPORT"],
                        }
                    ],
                }
            ],
        }

    def _write_manifest(self):
        self.manifest_path.write_text(
            json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8"
        )

    def invoke(self, subcommand="check"):
        return subprocess.run(
            [str(COMMAND), subcommand, "--project", str(self.project)],
            text=True,
            capture_output=True,
        )

    def build(self):
        result = self.invoke("build")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return self.project / "docs/traceability/index.html"

    def test_build_then_check_shows_overall_feature_and_latest_test_evidence(self):
        page = self.build()
        text = page.read_text(encoding="utf-8")
        self.assertLess(text.index("Overall traceability"), text.index("Photo import"))
        self.assertIn("TEST-PHOTO-IMPORT", text)
        self.assertIn("REPORT-PHOTO-IMPORT-20261003", text)
        self.assertIn("Latest test report", text)
        self.assertIn(f"app@{self.revision}:reports/latest.json", text)
        self.assertIn("Expected versus actual implementation", text)
        self.assertIn("Accepted implementation", text)
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("1 feature", result.stdout)

    def test_check_refuses_stale_generated_output(self):
        self.build()
        self.manifest["features"][0]["title"] = "Changed title"
        self._write_manifest()
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("generated output is stale", result.stdout)

    def test_symbol_and_explicit_region_are_strong_but_whole_file_is_weak(self):
        page = self.build().read_text(encoding="utf-8")
        self.assertIn("CODE-IMPORT", page)
        self.assertIn("symbol · strong", page)
        self.assertIn("region · strong", page)
        self.assertIn("whole file · weak", page)

    def test_broken_symbol_anchor_fails(self):
        self.manifest["features"][0]["code_anchors"][0]["symbol"] = "missing_symbol"
        self._write_manifest()
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("CODE-IMPORT: symbol missing_symbol not found", result.stdout)

    def test_expected_edge_missing_from_actual_graph_is_a_conformance_gap(self):
        self.manifest["features"][0]["workflow"]["actual_edges"] = []
        self._write_manifest()
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("WFE-IMPORT-STORE: expected workflow edge has no accepted implementation", result.stdout)

    def test_ai_proposed_mapping_never_counts_as_accepted_evidence(self):
        self.manifest["features"][0]["workflow"]["actual_edges"][0]["status"] = "proposed_ai"
        self.manifest["features"][0]["mappings"][0]["status"] = "proposed_ai"
        self._write_manifest()
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("proposed AI mapping does not count as accepted evidence", result.stdout)
        self.assertIn("WFE-IMPORT-STORE: expected workflow edge has no accepted implementation", result.stdout)

    def test_report_must_be_bound_to_the_configured_repository_revision(self):
        self.manifest["features"][0]["test_reports"][0]["revision"] = "0" * 40
        self._write_manifest()
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("REPORT-PHOTO-IMPORT-20261003: revision does not match repository app", result.stdout)

    def test_report_symlink_cannot_escape_configured_repository(self):
        outside = self.project / "outside-report.json"
        outside.write_text("{}", encoding="utf-8")
        link = self.repo / "reports/outside.json"
        link.symlink_to(outside)
        self.manifest["features"][0]["test_reports"][0]["path"] = "reports/outside.json"
        self._write_manifest()
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("REPORT-PHOTO-IMPORT-20261003: report path is outside repository app", result.stdout)

    def test_all_configured_repositories_are_scanned(self):
        self.manifest["repositories"].append(
            {"id": "missing", "revision": "0" * 40, "scan": {"include": ["**/*"], "exclude": []}}
        )
        self._write_manifest()
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("repository missing has no configured checkout", result.stdout)

    def test_ids_are_type_checked_and_globally_unique(self):
        duplicate = copy.deepcopy(self.manifest["features"][0]["requirements"][0])
        duplicate["id"] = "TEST-WRONG-TYPE"
        self.manifest["features"][0]["requirements"].append(duplicate)
        self._write_manifest()
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("requirement id TEST-WRONG-TYPE must start with REQ-", result.stdout)

    def test_unreviewed_manifest_is_refused(self):
        self.manifest["reviewed"]["status"] = "draft"
        self._write_manifest()
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("manifest is not reviewed and accepted", result.stdout)


class TraceabilityFixtureTest(unittest.TestCase):
    def test_committed_fixture_is_current(self):
        fixture = ROOT / "tests/fixtures/traceability"
        result = subprocess.run(
            [str(COMMAND), "check", "--project", str(fixture)],
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
