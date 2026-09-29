"""VERSION must not drift from what the CHANGELOG actually shipped (proposal
32, V-01/V-02). The sponsor: "Can you version the common rule ... Use
semantic version version and change Lock to maintain it going ahead".

`tools/version_check.py` computes the bump the CHANGELOG requires since the
last release, and `bin/version-check --check` fails the merge gate when
VERSION disagrees with it -- both read here, hermetically, against throwaway
fixture repos, never the real checkout running this suite.

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.version_check import (  # noqa: E402
    MAJOR_MARKER, MANDATORY_MARKER, parse_semver, required_bump, semver_diff,
)

TOOL = ROOT / "bin" / "version-check"


class TestRealCheckoutVersion(unittest.TestCase):
    """Pinned against the real repo, not a fixture -- these are true of THIS
    checkout, right now."""

    def test_version_file_exists_and_is_a_valid_semver(self):
        text = (ROOT / "VERSION").read_text(encoding="utf-8")
        parse_semver(text.strip())  # raises ValueError if not MAJOR.MINOR.PATCH

    def test_version_file_content_is_pinned(self):
        """The released version, pinned so a bump is a reviewed one-line diff.

        Every other test here reads VERSION; this one asserts a literal, on
        purpose (proposal 32, V-01), so raising the version cannot happen by
        accident or by a tool nobody watched.

        **Update this line in the same commit that edits VERSION.** It was
        missed at 1.0.0 and again at 1.0.1: main sat red both times, and the
        full suite that would have caught it ran just BEFORE the bump, not
        after. That is finding 33/R-02's case exactly -- a check that exists
        and fires too late to stop the thing it checks.
        """
        pinned = "1.2.0\n"
        actual = (ROOT / "VERSION").read_text(encoding="utf-8")
        self.assertEqual(
            actual, pinned,
            f"VERSION is {actual.strip()!r} but this test still pins "
            f"{pinned.strip()!r}. If the bump was deliberate, update this one "
            f"line in the same commit as VERSION; if it was not, that is what "
            f"this test is for.")

    def test_rulecheck_reports_both_the_semver_and_the_count(self):
        """`--version --semver` is the human form; bare `--version` is not.

        This test asked for the semver from bare `--version` when V-01
        landed, and that is exactly what broke `bin/land`: it parses that
        output against the project's stamp file, so a label there made every
        project read as "not aligned" (21 failures on main). The semver moved
        behind `--semver`; see TestVersionFlagIsAMachineContract in
        tests/test_rulecheck.py for the other half of this contract.
        """
        out = subprocess.run([str(ROOT / "bin" / "rulecheck"), "--version", "--semver"],
                             capture_output=True, text=True, check=True).stdout.strip()
        semver = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertIn(semver, out)
        # the count-sha is still there, in parentheses, beside it
        self.assertRegex(out, r"\(\d+-[0-9a-f]+\)")

    def test_bare_version_stays_machine_readable(self):
        out = subprocess.run([str(ROOT / "bin" / "rulecheck"), "--version"],
                             capture_output=True, text=True, check=True).stdout.strip()
        self.assertRegex(out, r"^\d+-[0-9a-f]{7,}$")


class FixtureRepo:
    """A throwaway git repo with a VERSION file and a CHANGELOG.md, shaped
    just enough to exercise tools/version_check.py. Never touches the real
    checkout running this test (VERSION_CHECK_ROOT points every call here)."""

    def __init__(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "proj"
        self.path.mkdir()
        (self.path / "bin").mkdir()
        # bin/rulecheck is loaded as a module by tools/version_check.py for
        # its fenced-code-aware paragraph scanner -- copy the real one in,
        # it is pure logic and needs no rules checkout of its own to import.
        import shutil
        shutil.copy2(ROOT / "bin" / "rulecheck", self.path / "bin" / "rulecheck")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")

    def cleanup(self):
        self.tmp.cleanup()

    def git(self, *a, check=True):
        return subprocess.run(["git", "-C", str(self.path), *a],
                              capture_output=True, text=True, check=check)

    def write(self, rel: str, body: str):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)

    def commit(self, message: str):
        self.git("add", "-A")
        self.git("commit", "-qm", message)

    def env(self):
        e = dict(os.environ)
        e["VERSION_CHECK_ROOT"] = str(self.path)
        return e

    def required_bump(self):
        """required_bump() run as a subprocess against this fixture -- a
        real process boundary, not an in-process monkeypatch of ROOT."""
        script = (
            "import sys; sys.path.insert(0, %r)\n"
            "from tools.version_check import required_bump\n"
            "b = required_bump()\n"
            "print(b.state, b.required, b.applied, b.current, sep='|')\n"
        ) % str(ROOT)
        return subprocess.run([sys.executable, "-c", script], cwd=str(self.path),
                              capture_output=True, text=True, env=self.env())

    def run_tool(self, *extra):
        return subprocess.run([sys.executable, str(TOOL), *extra], cwd=str(self.path),
                              capture_output=True, text=True, env=self.env())


PATCH_ENTRY = "## 2026-01-02 · a fix\n\nFixed a thing nobody has to change anything for.\n\n"
MANDATORY_ENTRY = (
    "## 2026-01-03 · a mandatory change\n\n"
    f"{MANDATORY_MARKER} every project must now do the new thing.\n\n"
)
MAJOR_ENTRY = (
    "## 2026-01-04 · a breaking change\n\n"
    f"{MAJOR_MARKER} the old tool is gone; a project calling it now fails.\n"
    f"{MANDATORY_MARKER} every project must switch to the new tool.\n\n"
)


class TestBumpRule(unittest.TestCase):
    """required_bump() applied to fixture changelogs -- the three levels."""

    def setUp(self):
        # Two commits: A establishes real history (a project this old
        # already has a CHANGELOG), B introduces VERSION with no new
        # entries of its own -- the release marker every later test adds
        # commits on top of. Mirrors how V-01 actually lands in a repo with
        # existing history, not a repo whose first-ever commit is VERSION.
        self.repo = FixtureRepo()
        self.repo.write("CHANGELOG.md", "# CHANGELOG\n\n" + PATCH_ENTRY)
        self.repo.commit("A: pre-existing history")
        self.repo.write("VERSION", "0.1.0\n")
        self.repo.commit("B: seed release 0.1.0")

    def tearDown(self):
        self.repo.cleanup()

    def _out(self):
        r = self.repo.required_bump()
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        state, required, applied, current = r.stdout.strip().split("|")
        return state, required, applied, current

    def test_nothing_new_since_the_release_needs_no_bump(self):
        state, required, applied, current = self._out()
        self.assertEqual((state, required), ("ok", "none"))

    def test_a_patch_only_entry_since_the_release_stays_patch(self):
        self.repo.write("CHANGELOG.md",
                        "# CHANGELOG\n\n" + PATCH_ENTRY + "\n## 2026-01-05 · another fix\n\nAnother fix.\n")
        self.repo.commit("a second patch-level entry, VERSION not bumped")
        state, required, applied, current = self._out()
        self.assertEqual((state, required), ("disagree", "patch"))

    def test_a_mandatory_entry_forces_at_least_minor(self):
        self.repo.write("CHANGELOG.md", "# CHANGELOG\n\n" + PATCH_ENTRY + MANDATORY_ENTRY)
        self.repo.commit("a mandatory entry, VERSION not bumped")
        state, required, applied, current = self._out()
        self.assertEqual((state, required), ("disagree", "minor"))

    def test_a_declared_major_entry_forces_major(self):
        self.repo.write("CHANGELOG.md", "# CHANGELOG\n\n" + PATCH_ENTRY + MAJOR_ENTRY)
        self.repo.commit("a breaking entry, VERSION not bumped")
        state, required, applied, current = self._out()
        self.assertEqual((state, required), ("disagree", "major"))

    def test_a_mandatory_entry_without_the_major_marker_is_only_minor(self):
        """A mandatory entry alone never escalates to major on its own --
        major must be declared, never inferred from 'mandatory' alone."""
        self.repo.write("CHANGELOG.md", "# CHANGELOG\n\n" + PATCH_ENTRY + MANDATORY_ENTRY)
        self.repo.commit("mandatory only")
        state, required, applied, current = self._out()
        self.assertNotEqual(required, "major")

    def test_a_marker_inside_a_fenced_example_is_prose_not_an_instance(self):
        fenced = (
            "## 2026-01-06 · documenting the convention\n\n"
            "How to write one:\n\n```\n" + MANDATORY_MARKER + " example text\n```\n\n"
        )
        self.repo.write("CHANGELOG.md", "# CHANGELOG\n\n" + PATCH_ENTRY + fenced)
        self.repo.commit("a fenced mention of the marker, not a real instance")
        state, required, applied, current = self._out()
        self.assertEqual(required, "patch",
                         "a marker inside a fenced code block must not force a bump")


class TestCheckExitCodes(unittest.TestCase):
    """bin/version-check --check: passes on agreement, fails on disagreement,
    writes nothing either way."""

    def setUp(self):
        self.repo = FixtureRepo()
        self.repo.write("CHANGELOG.md", "# CHANGELOG\n\n" + PATCH_ENTRY)
        self.repo.commit("A: pre-existing history")
        self.repo.write("VERSION", "0.1.0\n")
        self.repo.commit("B: seed release 0.1.0")

    def tearDown(self):
        self.repo.cleanup()

    def _tracked_files_snapshot(self):
        return {p: (self.repo.path / p).read_bytes()
                for p in ("VERSION", "CHANGELOG.md")}

    def test_check_passes_when_they_agree(self):
        before = self._tracked_files_snapshot()
        out = self.repo.run_tool("--check")
        self.assertEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertEqual(before, self._tracked_files_snapshot(), "--check must write nothing")

    def test_check_fails_non_zero_when_they_disagree(self):
        self.repo.write("CHANGELOG.md", "# CHANGELOG\n\n" + PATCH_ENTRY + MANDATORY_ENTRY)
        self.repo.commit("mandatory entry, VERSION not bumped")
        before = self._tracked_files_snapshot()
        out = self.repo.run_tool("--check")
        self.assertNotEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertEqual(before, self._tracked_files_snapshot(), "--check must write nothing, even on failure")

    def test_check_passes_when_the_same_commit_bumps_version_enough(self):
        self.repo.write("CHANGELOG.md", "# CHANGELOG\n\n" + PATCH_ENTRY + MANDATORY_ENTRY)
        self.repo.write("VERSION", "0.2.0\n")
        self.repo.commit("mandatory entry, VERSION bumped to minor in the same commit")
        out = self.repo.run_tool("--check")
        self.assertEqual(0, out.returncode, out.stdout + out.stderr)

    def test_check_fails_when_the_bump_applied_is_too_small(self):
        self.repo.write("CHANGELOG.md", "# CHANGELOG\n\n" + PATCH_ENTRY + MANDATORY_ENTRY)
        self.repo.write("VERSION", "0.1.1\n")  # only patch; a mandatory entry needs minor
        self.repo.commit("mandatory entry, VERSION under-bumped in the same commit")
        out = self.repo.run_tool("--check")
        self.assertNotEqual(0, out.returncode, out.stdout + out.stderr)


class TestMissingReleaseMarker(unittest.TestCase):
    """A checkout where VERSION is not tracked in git at all refuses rather
    than assuming nothing is pending."""

    def setUp(self):
        self.repo = FixtureRepo()
        self.repo.write("CHANGELOG.md", "# CHANGELOG\n\n" + MANDATORY_ENTRY)
        self.repo.commit("no VERSION file at all")

    def tearDown(self):
        self.repo.cleanup()

    def test_required_bump_refuses(self):
        r = self.repo.required_bump()
        state = r.stdout.strip().split("|")[0]
        self.assertEqual(state, "could not check")

    def test_check_exits_could_not_check_and_writes_nothing(self):
        before = (self.repo.path / "CHANGELOG.md").read_bytes()
        out = self.repo.run_tool("--check")
        self.assertEqual(2, out.returncode, out.stdout + out.stderr)
        self.assertEqual(before, (self.repo.path / "CHANGELOG.md").read_bytes())

    def test_it_does_not_read_as_nothing_pending(self):
        out = self.repo.run_tool("--check")
        low = (out.stdout + out.stderr).lower()
        self.assertNotIn("nothing pending", low)
        self.assertIn("not tracked", low)


class TestSemverDiff(unittest.TestCase):

    def test_patch(self):
        self.assertEqual(semver_diff("0.9.0", "0.9.1"), "patch")

    def test_minor(self):
        self.assertEqual(semver_diff("0.9.5", "0.10.0"), "minor")

    def test_major(self):
        self.assertEqual(semver_diff("0.9.0", "1.0.0"), "major")

    def test_none(self):
        self.assertEqual(semver_diff("0.9.0", "0.9.0"), "none")

    def test_a_decrease_is_rejected(self):
        with self.assertRaises(ValueError):
            semver_diff("0.9.5", "0.9.3")

    def test_a_decrease_in_a_higher_field_is_rejected_even_if_a_lower_field_grew(self):
        with self.assertRaises(ValueError):
            semver_diff("1.5.3", "1.4.9")

    def test_invalid_semver_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_semver("v1.0")
        with self.assertRaises(ValueError):
            parse_semver("1.0")
        with self.assertRaises(ValueError):
            parse_semver("01.0.0")


if __name__ == "__main__":
    unittest.main()
