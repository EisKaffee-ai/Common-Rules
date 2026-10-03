from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from tools.context_budget import measure_root

ROOT = Path(__file__).resolve().parent.parent


class ContextBudgetTest(unittest.TestCase):
    def test_discovery_is_separate_from_on_demand_content(self):
        report = measure_root(ROOT)
        self.assertEqual(13, report["discovery"]["skills"])
        self.assertLess(report["discovery"]["bytes"], report["on_demand"]["skill_instruction_bytes"])
        self.assertGreater(report["references"]["bytes"], 0)
        self.assertEqual(0, report["hooks"]["idle_context_tokens"])

    def test_json_output_is_machine_readable_and_budgeted(self):
        result = subprocess.run(
            [str(ROOT / "bin/context-budget"), "--project", str(ROOT), "--json", "--check"],
            text=True, capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("current", data)
        self.assertIn("estimated_tokens", data["current"]["discovery"])

    def test_unknown_comparison_ref_is_a_named_refusal(self):
        result = subprocess.run(
            [str(ROOT / "bin/context-budget"), "--compare-ref", "not-a-real-ref"],
            text=True, capture_output=True,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("cannot read git ref", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_readme_explains_estimate_not_ram(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        report = measure_root(ROOT)
        self.assertIn("bin/context-budget", readme)
        self.assertIn("not process RAM", readme)
        self.assertIn("Progressive loading", readme)
        self.assertIn(f"{report['discovery']['bytes']:,}", readme)
        self.assertIn(f"{report['discovery']['estimated_tokens']:,}", readme)
        self.assertIn(f"{report['full_skill_package_ceiling']['estimated_tokens']:,}", readme)


if __name__ == "__main__":
    unittest.main()
