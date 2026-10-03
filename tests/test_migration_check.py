from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "bin/migration-check"


class MigrationCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.repo, check=True)
        (self.repo / "ledger.json").write_text('{"id":"preserved"}\n')
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "source main"], cwd=self.repo, check=True)
        source_main = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/remotes/upstream/main", source_main)
        (self.repo / "development.txt").write_text("published\n")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "published development"], cwd=self.repo, check=True)
        published = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/remotes/upstream/w10-measured", published)
        (self.repo / "local.txt").write_text("local-only history\n")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "local development"], cwd=self.repo, check=True)
        local = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/remotes/local-source/w10-measured", local)

    def tearDown(self): self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True, text=True,
                              capture_output=True).stdout.strip()

    def invoke(self):
        return subprocess.run([str(COMMAND), "--project", str(self.repo)],
                              text=True, capture_output=True)

    def test_preserved_history_and_files_pass(self):
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("3 required histories are ancestors", result.stdout)
        self.assertIn("source files preserved", result.stdout)

    def test_removed_source_file_fails(self):
        (self.repo / "ledger.json").unlink()
        subprocess.run(["git", "add", "-u"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "remove source data"], cwd=self.repo, check=True)
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("ledger.json is missing", result.stdout)

    def test_unmerged_local_history_fails(self):
        self.git("update-ref", "refs/remotes/local-source/w10-measured", "HEAD")
        self.git("checkout", "-qb", "candidate", "upstream/main")
        result = self.invoke()
        self.assertEqual(1, result.returncode)
        self.assertIn("local-source/w10-measured is not an ancestor", result.stdout)


if __name__ == "__main__": unittest.main()
