"""Proposal 33 R-04: lean session, feedback, gate and Ruflo behavior."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WARMUP = ROOT / "bin" / "warmup"
TRACKER = ROOT / "bin" / "tracker"
HANDOVER = ROOT / "bin" / "handover"
GATE = ROOT / "bin" / "gate"
RUFLO = ROOT / "bin" / "ruflo-item"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_warmup import Project  # noqa: E402


def load_handover():
    loader = importlib.machinery.SourceFileLoader("lean_handover", str(HANDOVER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


H = load_handover()


class WarmupDedupeTests(unittest.TestCase):
    def setUp(self):
        self.project = Project(seeded=True)
        self.state = self.project.root / ".claude" / "warmup" / "last.json"

    def tearDown(self):
        self.project.close()

    def run_warmup(self):
        env = {**os.environ, "COMMON_RULES_SESSION_ID": "session-one"}
        return subprocess.run(
            [sys.executable, str(WARMUP), "--project", str(self.project.root),
             "--no-recall", "--no-pull", "--state", str(self.state)],
            capture_output=True, text=True, env=env,
        )

    def test_duplicate_plain_warmup_in_same_session_is_delta_only(self):
        first = self.run_warmup()
        second = self.run_warmup()
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertIn("Read in order:", first.stdout)
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        self.assertIn("no change since the last warm-up", second.stdout)
        self.assertNotIn("Read in order:", second.stdout)

    def test_same_session_and_state_path_do_not_suppress_another_project(self):
        other = Project(seeded=True)
        self.addCleanup(other.close)
        env = {**os.environ, "COMMON_RULES_SESSION_ID": "session-one"}
        first = subprocess.run(
            [sys.executable, str(WARMUP), "--project", str(self.project.root),
             "--no-recall", "--no-pull", "--state", str(self.state)],
            capture_output=True, text=True, env=env,
        )
        second = subprocess.run(
            [sys.executable, str(WARMUP), "--project", str(other.root),
             "--no-recall", "--no-pull", "--state", str(self.state)],
            capture_output=True, text=True, env=env,
        )
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        self.assertIn("Read in order:", second.stdout)


def ledger_data():
    return {
        "proposal": 99, "title": "fixture", "status": "accepted", "updated": "2026-10-04",
        "phases": [{"id": "W", "name": "work"}],
        "items": [{"id": "W-01", "phase": "W", "cx": "C2", "title": "screen review",
                   "status": "in progress", "log": []}],
        "asks": [],
    }


class ReviewCoalescingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "docs" / "proposals" / "99-fixture.json"
        self.ledger.parent.mkdir(parents=True)
        self.ledger.write_text(json.dumps(ledger_data(), indent=2) + "\n")

    def ask(self, text, at):
        return subprocess.run(
            [sys.executable, str(TRACKER), "ask", str(self.ledger), "--review", "W-01",
             "--kind", "defect", "--quote", text, "--at", at],
            capture_output=True, text=True,
        )

    def test_feedback_for_one_open_review_coalesces_into_one_ask(self):
        one = self.ask("make the ruler calmer", "2026-10-04T10:00:00+02:00")
        two = self.ask("the label should move with the ruler", "2026-10-04T10:03:00+02:00")
        self.assertEqual(0, one.returncode, one.stdout + one.stderr)
        self.assertEqual(0, two.returncode, two.stdout + two.stderr)
        asks = json.loads(self.ledger.read_text())["asks"]
        self.assertEqual(1, len(asks))
        self.assertEqual("W-01", asks[0]["review"])
        self.assertEqual(2, len(asks[0]["feedback"]))
        self.assertIn("coalesced", two.stdout)

    def test_handover_accepts_each_feedback_entry_as_covered(self):
        self.ask("make the ruler calmer", "2026-10-04T10:00:00+02:00")
        self.ask("the label should move with the ruler", "2026-10-04T10:03:00+02:00")
        transcript = self.root / "transcript.jsonl"
        rows = []
        for text, at in (("make the ruler calmer", "2026-10-04T10:00:00+02:00"),
                         ("the label should move with the ruler", "2026-10-04T10:03:00+02:00")):
            rows.append({"type": "user", "timestamp": at,
                         "message": {"role": "user", "content": [{"type": "text", "text": text}]}})
        transcript.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
        mark, detail = H.check_asks(self.root, transcript, None)
        self.assertEqual(H.PASS, mark, detail)


class GateReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "project"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=self.root, check=True)
        (self.root / "tracked.txt").write_text("one\n")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "initial"], cwd=self.root, check=True)
        self.counter = Path(self.tmp.name) / ".gate-count"
        declaration = {"gates": {
            "quick": f"printf q >> {self.counter}",
            "merge": f"printf m >> {self.counter}",
        }}
        (self.root / ".common-rules.json").write_text(json.dumps(declaration))

    def run_gate(self, level):
        return subprocess.run([sys.executable, str(GATE), level, "--project", str(self.root)],
                              capture_output=True, text=True)

    def test_same_level_revision_and_configuration_reuses_receipt(self):
        first = self.run_gate("checkpoint")
        second = self.run_gate("checkpoint")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        self.assertEqual("m", self.counter.read_text())
        self.assertIn("reused", second.stdout)

    def test_release_does_not_reuse_a_checkpoint_receipt(self):
        self.run_gate("checkpoint")
        release = self.run_gate("release")
        self.assertEqual(0, release.returncode, release.stdout + release.stderr)
        self.assertEqual("mm", self.counter.read_text())
        self.assertNotIn("reused", release.stdout)

    def test_worktree_change_invalidates_receipt(self):
        self.run_gate("development")
        (self.root / "tracked.txt").write_text("two\n")
        self.run_gate("development")
        self.assertEqual("qq", self.counter.read_text())


FAKE_RUFLO = """#!/bin/sh
printf '%s\\n' "$*" >> "$FAKE_RUFLO_LOG"
exit 0
"""


class RufloLevelsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.root = base / "project"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=self.root, check=True)
        (self.root / "tracked.txt").write_text("one\n")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "initial"], cwd=self.root, check=True)
        self.count = base / ".counts"
        (self.root / ".common-rules.json").write_text(json.dumps({"gates": {
            "quick": f"printf q >> {self.count}", "merge": f"printf m >> {self.count}"}}))
        fake = base / "claude-flow"
        fake.write_text(FAKE_RUFLO)
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
        self.log = base / "ruflo.log"
        self.env = {**os.environ, "RUFLO": str(fake), "FAKE_RUFLO_LOG": str(self.log)}

    def run_item(self, command):
        return subprocess.run([sys.executable, str(RUFLO), "--project", str(self.root),
                               command, "W-01", "summary"], capture_output=True, text=True, env=self.env)

    def test_ready_runs_only_the_quick_gate_and_no_testgaps(self):
        result = self.run_item("ready")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("q", self.count.read_text())
        self.assertNotIn("testgaps", self.log.read_text())

    def test_checkpoint_and_land_are_the_only_new_commands_that_dispatch_testgaps(self):
        checkpoint = self.run_item("checkpoint")
        land = self.run_item("land")
        self.assertEqual(0, checkpoint.returncode, checkpoint.stdout + checkpoint.stderr)
        self.assertEqual(0, land.returncode, land.stdout + land.stderr)
        self.assertEqual("mm", self.count.read_text(), "release evidence must be stronger than checkpoint evidence")
        self.assertEqual(2, self.log.read_text().count("testgaps"))

    def test_repeated_checkpoint_reuses_receipt_without_redispatching_testgaps(self):
        first = self.run_item("checkpoint")
        second = self.run_item("checkpoint")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        self.assertEqual(1, self.log.read_text().count("testgaps"))

    def test_repeated_land_reuses_receipt_without_redispatching_testgaps(self):
        first = self.run_item("land")
        second = self.run_item("land")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        self.assertEqual(1, self.log.read_text().count("testgaps"))

    def test_checkpoint_stores_checkpoint_and_conformance_compatible_done_keys(self):
        result = self.run_item("checkpoint")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        log = self.log.read_text()
        self.assertIn("item:W-01:checkpoint", log)
        self.assertIn("item:W-01:done", log)

    def test_done_is_a_checkpoint_compatibility_alias(self):
        done = self.run_item("done")
        land = self.run_item("land")
        self.assertEqual(0, done.returncode, done.stdout + done.stderr)
        self.assertEqual(0, land.returncode, land.stdout + land.stderr)
        self.assertEqual("mm", self.count.read_text())
        log = self.log.read_text()
        self.assertIn("item:W-01:done", log)
        self.assertIn("hooks post-task", log)


if __name__ == "__main__":
    unittest.main()
