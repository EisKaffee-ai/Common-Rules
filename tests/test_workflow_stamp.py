"""The workflow.html version stamp must not drift from the rules it describes.

`docs/README.md` says any PR changing the shared rules updates `workflow.html`
and its stamp in the same PR. That was maintained by memory, and by 2026-08-07
the page claimed **version 62** while the rules were at **102** — forty versions
of drift on a page whose own README says a drifted bird's-eye view is worse than
none, because it is trusted at a glance.

This is that rule made checkable.

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.workflow_stamp import PAGE, RULES_FILE as RULES, git, rules_version, stamped_version  # noqa: E402

TOOL = ROOT / "bin" / "workflow-stamp"


class TestWorkflowStamp(unittest.TestCase):

    def test_page_is_not_older_than_the_rules_it_describes(self):
        stamped, required = stamped_version(), rules_version()
        self.assertGreaterEqual(
            stamped, required,
            f"docs/workflow.html says rules version {stamped}, but "
            f"{RULES} last changed at version {required}. The page has drifted "
            f"behind the rules — regenerate it and update the stamp.")

    def test_stamp_is_not_from_the_future(self):
        stamped, head = stamped_version(), int(git("rev-list", "--count", "HEAD"))
        # One ahead is legitimate: a stamp is written for the commit it lands
        # as, which does not exist yet at the time it is typed. More than that
        # is a typo or a guess.
        self.assertLessEqual(
            stamped, head + 1,
            f"stamp claims rules version {stamped}, but HEAD is only at {head}")

    def test_the_png_beside_it_is_not_stale(self):
        png = ROOT / "docs" / "workflow.png"
        self.assertTrue(png.exists(), "docs/workflow.png is missing")
        page_at = git("log", "-1", "--format=%ct", "--", "docs/workflow.html")
        png_at = git("log", "-1", "--format=%ct", "--", "docs/workflow.png")
        if page_at and png_at:
            self.assertGreaterEqual(
                int(png_at), int(page_at),
                "docs/workflow.png was committed before the last change to "
                "workflow.html — regenerate it (see docs/README.md)")


FAKE_CHROME = textwrap.dedent("""\
    #!/usr/bin/env python3
    # Stands in for headless Chrome in bin/workflow-stamp's own tests --
    # real Chrome is never run in this suite. Reads FAKE_CHROME_MODE to
    # decide what to do with the --screenshot=PATH it was given:
    #   good  -- write a real png with content in its top rows and
    #            background below (a page followed by a trailing blank,
    #            like the real capture)
    #   blank -- write a real png that is background color throughout
    #   crash -- exit 1 and write nothing, like a chrome that failed
    import os
    import sys
    from PIL import Image

    def screenshot_path():
        for a in sys.argv[1:]:
            if a.startswith("--screenshot="):
                return a.split("=", 1)[1]
        return None

    mode = os.environ.get("FAKE_CHROME_MODE", "good")
    path = screenshot_path()
    if mode == "crash":
        sys.exit(1)
    w, h = 200, 300
    im = Image.new("RGB", (w, h), (255, 255, 255))
    if mode == "good":
        # Background (white) at the top-left corner, where the crop's own
        # sample pixel is taken from -- a band of "content" in the middle,
        # white again below it (the trailing blank the crop trims off).
        px = im.load()
        for y in range(50, 150):
            for x in range(w):
                px[x, y] = (10, 20, 30)
    elif mode != "blank":
        raise SystemExit(f"unknown FAKE_CHROME_MODE {mode!r}")
    im.save(path)
    """)


class FixtureRepo:
    """A throwaway git repo shaped like this one just enough to exercise
    bin/workflow-stamp: a CLAUDE-workflow.md whose commit count IS the
    rules version, a docs/workflow.html with a stamp, a docs/workflow.png
    beside it. Never touches the real checkout running this test."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "proj"
        self.path.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        (self.path / "docs").mkdir()

        fake_chrome = Path(self.tmp.name) / "fake-chrome"
        fake_chrome.write_text(FAKE_CHROME.replace("#!/usr/bin/env python3", "#!" + sys.executable, 1))
        fake_chrome.chmod(fake_chrome.stat().st_mode | stat.S_IEXEC)
        self.fake_chrome = fake_chrome

        # Commit 1: CLAUDE-workflow.md + a page stamped to match it.
        # Commit count at this commit is 1, and it is the last (only)
        # commit touching CLAUDE-workflow.md -- rules_version() == 1.
        self.write("CLAUDE-workflow.md", "rules v1\n")
        self.write("docs/workflow.html",
                    "<html><body>derived from CLAUDE-workflow.md · "
                    "rules version 1 · 2020-01-01</body></html>\n")
        self.write("docs/workflow.png", "not a real png, just a placeholder\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "seed rules v1")

    def cleanup(self):
        self.tmp.cleanup()

    def git(self, *a, check=True):
        return subprocess.run(["git", "-C", str(self.path), *a],
                              capture_output=True, text=True, check=check)

    def write(self, rel: str, body: str):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)

    def commit(self, rel: str, body: str, message: str):
        self.write(rel, body)
        self.git("add", "-A")
        self.git("commit", "-qm", message)

    def run(self, *extra, chrome_mode: str = "good"):
        env = dict(os.environ)
        env["WORKFLOW_STAMP_ROOT"] = str(self.path)
        if chrome_mode == "missing":
            # An explicit override that resolves to nothing is authoritative
            # (see find_chrome()'s docstring) -- deterministic "no chrome
            # found" regardless of what is actually installed on the
            # machine running this test.
            env["WORKFLOW_STAMP_CHROME"] = str(Path(self.tmp.name) / "no-such-chrome")
            env.pop("FAKE_CHROME_MODE", None)
        else:
            env["WORKFLOW_STAMP_CHROME"] = str(self.fake_chrome)
            env["FAKE_CHROME_MODE"] = chrome_mode
        return subprocess.run([str(TOOL), *extra], cwd=str(self.path),
                              capture_output=True, text=True, env=env)


class TestWorkflowStampTool(unittest.TestCase):
    """bin/workflow-stamp: writes the stamp rules_version() computes,
    regenerates the png, --check without writing, and refuses a bad
    capture rather than writing one. Never runs real Chrome (FixtureRepo
    hands it a fake one instead)."""

    def setUp(self):
        self.repo = FixtureRepo()

    def tearDown(self):
        self.repo.cleanup()

    def _bump_rules(self):
        """A second commit touching CLAUDE-workflow.md: commit count 2,
        and now the last commit to touch the rules file -- rules_version()
        becomes 2, while the page is still stamped 1."""
        self.repo.commit("CLAUDE-workflow.md", "rules v2\n", "bump rules to v2")

    def test_writes_the_stamp_rules_version_computes(self):
        self._bump_rules()
        out = self.repo.run()
        self.assertEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertIn("stamp 1 -> 2", out.stdout)
        page = (self.repo.path / "docs" / "workflow.html").read_text()
        self.assertIn("rules version 2", page)
        self.assertNotIn("rules version 1", page)

    def test_check_passes_on_a_current_page_and_writes_nothing(self):
        # Stamp (1) already matches rules_version() (1) from the seed commit.
        before_html = (self.repo.path / "docs" / "workflow.html").read_text()
        before_png = (self.repo.path / "docs" / "workflow.png").read_bytes()
        out = self.repo.run("--check")
        self.assertEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertEqual(before_html, (self.repo.path / "docs" / "workflow.html").read_text())
        self.assertEqual(before_png, (self.repo.path / "docs" / "workflow.png").read_bytes())

    def test_check_fails_non_zero_on_a_drifted_page(self):
        self._bump_rules()
        before = (self.repo.path / "docs" / "workflow.html").read_text()
        out = self.repo.run("--check")
        self.assertNotEqual(0, out.returncode)
        self.assertIn("stale", out.stdout)
        # --check writes nothing, ever.
        self.assertEqual(before, (self.repo.path / "docs" / "workflow.html").read_text())

    def test_a_commit_touching_only_the_page_is_a_no_op_for_the_required_stamp(self):
        """The anti-off-by-one property rules_version()'s docstring
        describes: a commit that edits only workflow.html (or the png)
        must not move the target, or every correction would need
        correcting again."""
        # Compute "required" the same way tools/workflow_stamp.rules_version()
        # does, directly against the fixture repo.
        def required():
            sha = self.repo.git("log", "-1", "--format=%H", "--", "CLAUDE-workflow.md").stdout.strip()
            return int(self.repo.git("rev-list", "--count", sha).stdout.strip())

        before = required()
        self.repo.commit("docs/workflow.html", "<html>touched only the page</html>\n",
                          "touch only the page")
        after = required()
        self.assertEqual(before, after,
                          "a commit touching only the page changed the required stamp")

    def test_regenerates_the_png(self):
        self._bump_rules()
        png_path = self.repo.path / "docs" / "workflow.png"
        before = png_path.read_bytes()
        out = self.repo.run()
        self.assertEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertIn("regenerated:", out.stdout)
        after = png_path.read_bytes()
        self.assertNotEqual(before, after)
        from PIL import Image
        with Image.open(png_path) as im:
            im.verify()  # a real, non-corrupt png -- not the placeholder text

    def test_refuses_a_blank_capture_and_writes_nothing(self):
        self._bump_rules()
        png_path = self.repo.path / "docs" / "workflow.png"
        before = png_path.read_bytes()
        out = self.repo.run(chrome_mode="blank")
        self.assertNotEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertIn("blank", (out.stdout + out.stderr).lower())
        self.assertEqual(before, png_path.read_bytes(),
                          "a blank capture must not overwrite the real png")
        # The stamp itself is a separate step and does get written -- only
        # the png write is refused.
        self.assertIn("stamp 1 -> 2", out.stdout)

    def test_refuses_a_missing_capture_and_writes_nothing(self):
        self._bump_rules()
        png_path = self.repo.path / "docs" / "workflow.png"
        before = png_path.read_bytes()
        out = self.repo.run(chrome_mode="crash")
        self.assertNotEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertEqual(before, png_path.read_bytes())

    def test_refuses_when_chrome_cannot_be_found(self):
        self._bump_rules()
        out = self.repo.run(chrome_mode="missing")
        self.assertNotEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertIn("no chrome", (out.stdout + out.stderr).lower())

    def test_reports_the_pngs_new_size(self):
        self._bump_rules()
        out = self.repo.run()
        self.assertEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertRegex(out.stdout, r"\d+x\d+px, [\d,]+ bytes")


if __name__ == "__main__":
    unittest.main()


class TestCheckMatchesTheSuite(unittest.TestCase):
    """`workflow-stamp --check` must accept exactly what the two tests above
    accept, no more and no less.

    It is wired into `gates.merge`, so a check stricter than the suite would
    refuse a merge the suite itself passes -- and one looser would let the
    drift through that made main red on 17 Sep. The interesting case is a
    stamp one ahead of the rules: legitimate, because a stamp is written for
    the commit it lands as, and allowed by test_stamp_is_not_from_the_future.
    """

    def test_a_stamp_one_ahead_of_the_rules_is_accepted(self):
        import subprocess as sp
        r = sp.run([sys.executable, str(ROOT / "bin" / "workflow-stamp"), "--check"],
                   capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("current", r.stdout)

    def test_check_writes_nothing(self):
        import subprocess as sp
        before = (ROOT / "docs" / "workflow.html").read_bytes()
        png_before = (ROOT / "docs" / "workflow.png").stat().st_mtime
        sp.run([sys.executable, str(ROOT / "bin" / "workflow-stamp"), "--check"],
               capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(before, (ROOT / "docs" / "workflow.html").read_bytes())
        self.assertEqual(png_before, (ROOT / "docs" / "workflow.png").stat().st_mtime)
