"""bin/quiet -- run a gate, keep its output in a file, print one verdict line
(common-rules proposal 23, lever L3).

Why: build/test/receipt runs were 62% of PhotoVault App subagent spend
because agents piped raw `flutter test ... | tail -N` and
`python3 -m unittest ... | tail -N` straight into context. A past incident
(docs/OPERATING-RULES.md S3) shipped a broken commit because a
`grep ... && git commit` chain trusted grep's exit code instead of the
runner's own summary line -- grep exits 0 on a line containing "FAILED".
These tests pin the verdict to the runner's real summary text AND its exit
code, not to a naive grep.

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUIET = ROOT / "bin" / "quiet"


def _load_quiet_module():
    """`bin/quiet` has no .py extension (it's a script), so it's loaded the
    same way tests/test_derecord.py loads bin/conformance: by explicit
    SourceFileLoader, to unit-test its internal helpers (shard ordering,
    --jobs auto) without going through a subprocess for every case."""
    loader = importlib.machinery.SourceFileLoader("quiet_module_for_tests", str(QUIET))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


quiet = _load_quiet_module()


def py(code: str) -> list[str]:
    """A fake tool: a small python3 -c script producing a chosen summary
    shape and exiting with a chosen code."""
    return [sys.executable, "-c", code]


UNITTEST_OK = (
    "test_a (t.T) ... ok\n"
    "----------------------------------------------------------------------\n"
    "Ran 3 tests in 0.001s\n"
    "\n"
    "OK\n"
)

UNITTEST_FAILED = (
    "test_a (t.T) ... ok\n"
    "======================================================================\n"
    "FAIL: test_b (t.T)\n"
    "----------------------------------------------------------------------\n"
    "AssertionError: boom\n"
    "----------------------------------------------------------------------\n"
    "Ran 3 tests in 0.001s\n"
    "\n"
    "FAILED (failures=1)\n"
)

FLUTTER_OK = "00:02 +3: All tests passed!\n"
FLUTTER_FAILED = "00:03 +2 -1: Some tests failed.\n"

ANALYZE_OK = "No issues found!\n"
ANALYZE_FAILED = "3 issues found.\n"

PYTEST_OK = "3 passed in 0.01s\n"
PYTEST_FAILED = "2 failed, 1 passed in 0.02s\n"
#: A green run whose summary spells its zeros out. The PhotoVault
#: engine's parallel merge gate prints exactly this shape, per group.
PYTEST_OK_EXPLICIT_ZEROS = (
    "  group     serial: 426 passed, 0 failed, 0 errors, 0 skipped, 0 xfailed -- 510.1s -- ok\n"
    "parallel merge gate: 5499 passed, 0 failed, 0 errors, 48 skipped, 17 xfailed\n"
    "overall: PASS\n")


class TestQuiet(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def run_quiet(self, extra_args, text, code):
        script = f"import sys; sys.stdout.write({text!r}); sys.exit({code})"
        log = str(Path(self.tmp.name) / "run.log")
        cmd = [str(QUIET), "--log", log, *extra_args, "--", *py(script)]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return r, Path(log)

    # -- unittest ---------------------------------------------------------

    def test_unittest_ok(self):
        r, log = self.run_quiet([], UNITTEST_OK, 0)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(r.stdout.startswith("quiet: OK"), r.stdout)
        self.assertIn("3 tests", r.stdout)

    def test_unittest_failed_exit_1(self):
        r, log = self.run_quiet([], UNITTEST_FAILED, 1)
        self.assertEqual(r.returncode, 1)
        self.assertTrue(r.stdout.startswith("quiet: FAILED"), r.stdout)
        self.assertIn("failures=1", r.stdout)
        self.assertIn("FAIL: test_b", r.stdout)

    def test_unittest_failed_text_but_exit_0_is_still_failed(self):
        """The regression this exists for: a runner that prints a failure
        summary but exits 0 must not be reported OK."""
        r, log = self.run_quiet([], UNITTEST_FAILED, 0)
        self.assertEqual(r.returncode, 0, "quiet exits with CMD's own code")
        self.assertTrue(r.stdout.startswith("quiet: FAILED"),
                         f"verdict must distrust exit 0 when output says FAILED: {r.stdout!r}")

    # -- flutter test -------------------------------------------------------

    def test_flutter_pass(self):
        r, log = self.run_quiet([], FLUTTER_OK, 0)
        self.assertTrue(r.stdout.startswith("quiet: OK"), r.stdout)
        self.assertIn("+3", r.stdout)

    def test_flutter_fail(self):
        r, log = self.run_quiet([], FLUTTER_FAILED, 1)
        self.assertTrue(r.stdout.startswith("quiet: FAILED"), r.stdout)
        self.assertIn("-1", r.stdout)

    # -- flutter/dart analyze ------------------------------------------------

    def test_analyze_clean(self):
        r, log = self.run_quiet([], ANALYZE_OK, 0)
        self.assertTrue(r.stdout.startswith("quiet: OK"), r.stdout)
        self.assertIn("No issues found", r.stdout)

    def test_analyze_issues(self):
        r, log = self.run_quiet([], ANALYZE_FAILED, 1)
        self.assertTrue(r.stdout.startswith("quiet: FAILED"), r.stdout)
        self.assertIn("3 issues found", r.stdout)

    # -- pytest -----------------------------------------------------------

    def test_pytest_pass(self):
        r, log = self.run_quiet([], PYTEST_OK, 0)
        self.assertTrue(r.stdout.startswith("quiet: OK"), r.stdout)

    def test_pytest_fail(self):
        r, log = self.run_quiet([], PYTEST_FAILED, 1)
        self.assertTrue(r.stdout.startswith("quiet: FAILED"), r.stdout)

    def test_a_summary_that_spells_out_its_zeros_is_still_OK(self):
        """`0 failed` is a zero, not a failure.

        The verdict used to be `"failed" in summary`, a substring test, so a
        runner that writes its zeros out -- as the PhotoVault engine's
        parallel merge gate does, per group -- could never report OK however
        green it was. That is the same mistake this file's own module
        docstring warns about (`grep` exits 0 on a line containing
        "FAILED"), made inside the checker itself. It cost that project its
        conformance item 9: `ruflo-item done` keys off this verdict, so no
        item could ever be recorded done."""
        r, log = self.run_quiet([], PYTEST_OK_EXPLICIT_ZEROS, 0)
        self.assertTrue(r.stdout.startswith("quiet: OK"), r.stdout)

    def test_a_nonzero_count_among_zeros_still_fails(self):
        """The other half: zeros do not make a real failure disappear."""
        out = "  group balanced-2: 793 passed, 1 failed, 0 errors, 0 skipped\n"
        r, log = self.run_quiet([], out, 1)
        self.assertTrue(r.stdout.startswith("quiet: FAILED"), r.stdout)

    # -- unknown tool fallback ----------------------------------------------

    def test_unknown_tool_fallback_ok(self):
        r, log = self.run_quiet([], "some noise\nthe actual last line\n", 0)
        self.assertTrue(r.stdout.startswith("quiet: OK"), r.stdout)
        self.assertIn("the actual last line", r.stdout)

    def test_unknown_tool_fallback_failed_relies_on_exit_code(self):
        r, log = self.run_quiet([], "some noise\nthe actual last line\n", 1)
        self.assertEqual(r.returncode, 1)
        self.assertTrue(r.stdout.startswith("quiet: FAILED"), r.stdout)

    # -- command cannot start -----------------------------------------------

    def test_command_not_found_exits_2(self):
        log = str(Path(self.tmp.name) / "missing.log")
        cmd = [str(QUIET), "--log", log, "--", "/no/such/binary/here-xyz"]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 2)
        self.assertTrue(r.stdout.startswith("quiet: FAILED"), r.stdout)

    # -- log file and single-line stdout invariants --------------------------

    def test_log_file_has_full_output(self):
        r, log = self.run_quiet([], UNITTEST_FAILED, 1)
        self.assertTrue(log.exists())
        logged = log.read_text()
        self.assertEqual(logged, UNITTEST_FAILED)

    def test_stdout_is_exactly_one_line(self):
        r, log = self.run_quiet([], UNITTEST_OK, 0)
        lines = [l for l in r.stdout.split("\n") if l != ""]
        self.assertEqual(len(lines), 1, f"expected exactly one line, got {r.stdout!r}")

    def test_label_used_in_default_log_name(self):
        script = f"import sys; sys.stdout.write({UNITTEST_OK!r}); sys.exit(0)"
        cmd = [str(QUIET), "--label", "mylabel-xyz", "--", *py(script)]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        m = re.search(r"log (\S+)", r.stdout)
        self.assertIsNotNone(m, r.stdout)
        self.assertIn("mylabel-xyz", m.group(1))
        Path(m.group(1)).unlink(missing_ok=True)

    def test_detail_never_contains_newline_or_exceeds_160_chars(self):
        long_last_line = "x" * 500
        r, log = self.run_quiet([], f"noise\n{long_last_line}\n", 0)
        line = r.stdout.rstrip("\n")
        self.assertNotIn("\n", line)
        self.assertLessEqual(len(line), 300)


# -- --jobs: parallel unittest discover (proposal 23, lever M-01) -----------
#
# Why: 67-81% faster suites (Trail of Bits, May 2025). The requirement is
# that quiet's own one-line verdict is unchanged: these tests build a real
# fixture test tree (some files pass, one fails) and assert that running it
# through `quiet -- python3 -m unittest discover -s DIR -q` (sequential) and
# through `quiet --jobs N -- python3 -m unittest discover -s DIR -q`
# (parallel, sharded one OS process per file) report the *same* verdict --
# same OK/FAILED, same total test count, same failure count.

PASSING_MODULE = """
import unittest

class T{n}(unittest.TestCase):
    def test_a(self):
        self.assertTrue(True)

    def test_b(self):
        self.assertEqual(1, 1)
"""

FAILING_MODULE = """
import unittest

class TFail(unittest.TestCase):
    def test_ok(self):
        self.assertTrue(True)

    def test_boom(self):
        self.fail("boom")
"""


class TestQuietParallelDiscover(unittest.TestCase):
    def _make_fixture(self, n_passing_modules: int, failing: bool) -> Path:
        d = Path(self.tmp.name) / "fixture_tests"
        d.mkdir(parents=True, exist_ok=True)
        for i in range(n_passing_modules):
            (d / f"test_p{i}.py").write_text(PASSING_MODULE.format(n=i))
        if failing:
            (d / "test_zfail.py").write_text(FAILING_MODULE)
        return d

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, extra_args, fixture_dir):
        log = str(Path(self.tmp.name) / f"run-{'-'.join(extra_args) or 'seq'}.log")
        cmd = [
            str(QUIET), "--log", log, *extra_args, "--",
            sys.executable, "-m", "unittest", "discover", "-s", str(fixture_dir), "-q",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return r, Path(log)

    def test_parallel_passes_agree_with_sequential(self):
        fixture = self._make_fixture(n_passing_modules=5, failing=False)
        seq, _ = self._run([], fixture)
        par, _ = self._run(["--jobs", "4"], fixture)
        self.assertTrue(seq.stdout.startswith("quiet: OK"), seq.stdout)
        self.assertTrue(par.stdout.startswith("quiet: OK"), par.stdout)
        # 5 modules x 2 tests each = 10, same total either way.
        self.assertIn("10 tests", seq.stdout)
        self.assertIn("10 tests", par.stdout)
        self.assertEqual(seq.returncode, 0)
        self.assertEqual(par.returncode, 0)

    def test_parallel_failure_agrees_with_sequential(self):
        fixture = self._make_fixture(n_passing_modules=4, failing=True)
        seq, _ = self._run([], fixture)
        par, _ = self._run(["--jobs", "4"], fixture)
        self.assertTrue(seq.stdout.startswith("quiet: FAILED"), seq.stdout)
        self.assertTrue(par.stdout.startswith("quiet: FAILED"), par.stdout)
        self.assertIn("failures=1", seq.stdout)
        self.assertIn("failures=1", par.stdout)
        self.assertNotEqual(seq.returncode, 0)
        self.assertNotEqual(par.returncode, 0)

    def test_jobs_without_discover_shape_falls_back_unchanged(self):
        """--jobs is a no-op for any CMD that is not a plain `unittest
        discover` invocation -- it must never change behaviour for an
        arbitrary command."""
        log = str(Path(self.tmp.name) / "run.log")
        cmd = [str(QUIET), "--log", log, "--jobs", "4", "--", *py(
            f"import sys; sys.stdout.write({UNITTEST_OK!r}); sys.exit(0)"
        )]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        self.assertTrue(r.stdout.startswith("quiet: OK"), r.stdout)
        self.assertIn("3 tests", r.stdout)

    def test_jobs_1_runs_sequentially(self):
        fixture = self._make_fixture(n_passing_modules=3, failing=False)
        seq, _ = self._run([], fixture)
        one, _ = self._run(["--jobs", "1"], fixture)
        self.assertTrue(seq.stdout.startswith("quiet: OK"), seq.stdout)
        self.assertTrue(one.stdout.startswith("quiet: OK"), one.stdout)
        self.assertIn("6 tests", seq.stdout)
        self.assertIn("6 tests", one.stdout)

    def test_stdout_still_exactly_one_line_when_parallel(self):
        fixture = self._make_fixture(n_passing_modules=5, failing=False)
        par, _ = self._run(["--jobs", "4"], fixture)
        lines = [l for l in par.stdout.split("\n") if l != ""]
        self.assertEqual(len(lines), 1, f"expected exactly one line, got {par.stdout!r}")


# -- shard duration cache and dispatch order (M-01, the coordinator's       --
# -- correction, 2026-09-17): a shard is one file's own process, and the    --
# -- whole run is only as fast as whichever one is submitted last and       --
# -- happens to be the slow one -- so slowest-known-first dispatch matters, --
# -- not just splitting the work across `jobs` workers.

class TestOrderedShards(unittest.TestCase):
    """Pure unit tests of `_ordered_shards`, the sort `_run_parallel_discover`
    uses to decide submission order -- no subprocess, no timing, so these
    can't be flaky. It sorts Units (a whole file, or a group of one file's
    classes) since O-10 made a slow file splittable."""

    @staticmethod
    def units(*names):
        return [quiet.Unit(Path(n)) for n in names]

    def test_the_slowest_known_module_goes_first(self):
        files = self.units("test_a.py", "test_slow.py", "test_b.py", "test_c.py")
        durations = {"test_a.py": 1.0, "test_slow.py": 575.0, "test_b.py": 2.0, "test_c.py": 0.5}
        ordered = quiet._ordered_shards(files, durations)
        self.assertEqual(ordered[0].path.name, "test_slow.py")
        # and otherwise strictly by descending duration
        self.assertEqual([u.path.name for u in ordered],
                          ["test_slow.py", "test_b.py", "test_a.py", "test_c.py"])

    def test_a_cold_cache_still_orders_every_file_and_drops_none(self):
        files = self.units("test_a.py", "test_b.py", "test_c.py")
        ordered = quiet._ordered_shards(files, {})
        self.assertEqual({u.path.name for u in ordered}, {"test_a.py", "test_b.py", "test_c.py"})
        # no durations known at all -> the incoming (alphabetical) order is
        # kept, a plain round-robin.
        self.assertEqual([u.path.name for u in ordered], ["test_a.py", "test_b.py", "test_c.py"])

    def test_unknown_files_sort_after_every_timed_file(self):
        files = self.units("test_new.py", "test_timed.py")
        ordered = quiet._ordered_shards(files, {"test_timed.py": 3.0})
        self.assertEqual([u.path.name for u in ordered], ["test_timed.py", "test_new.py"])


class TestAutoJobs(unittest.TestCase):
    """--jobs auto (or a bare trailing --jobs) resolves to os.cpu_count() -
    2, floor 2, both as a unit (the resolver itself) and end to end
    (through the real quiet subprocess, in the discover-shape it changes
    behaviour for)."""

    def test_auto_jobs_resolver_matches_cpu_count_minus_two_floored_at_two(self):
        n = quiet._auto_jobs()
        self.assertIsInstance(n, int)
        self.assertGreaterEqual(n, 2)
        self.assertEqual(n, max(2, (os.cpu_count() or 2) - 2))

    def test_jobs_auto_end_to_end_runs_and_agrees_with_sequential(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "fixture_tests"
            fixture.mkdir()
            for i in range(3):
                (fixture / f"test_p{i}.py").write_text(PASSING_MODULE.format(n=i))
            log = str(Path(tmp) / "auto.log")
            cmd = [str(QUIET), "--log", log, "--jobs", "auto", "--",
                   sys.executable, "-m", "unittest", "discover", "-s", str(fixture), "-q"]
            r = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertTrue(r.stdout.startswith("quiet: OK"), r.stdout)
            self.assertIn("6 tests", r.stdout)

    def test_bare_trailing_jobs_also_means_auto(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "fixture_tests"
            fixture.mkdir()
            (fixture / "test_p0.py").write_text(PASSING_MODULE.format(n=0))
            log = str(Path(tmp) / "bare.log")
            cmd = [str(QUIET), "--log", log, "--jobs", "--",
                   sys.executable, "-m", "unittest", "discover", "-s", str(fixture), "-q"]
            r = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertTrue(r.stdout.startswith("quiet: OK"), r.stdout)
            self.assertIn("2 tests", r.stdout)


class TestShardDurationCache(unittest.TestCase):
    """The cache `_run_parallel_discover` writes after a real parallel run --
    following tools/tracker/history.py's own placement rule (system temp,
    keyed by the repo's absolute path, when .cache/ isn't gitignored)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_real_parallel_run_populates_the_duration_cache(self):
        fixture = Path(self.tmp.name) / "fixture_tests"
        fixture.mkdir()
        for i in range(3):
            (fixture / f"test_p{i}.py").write_text(PASSING_MODULE.format(n=i))
        cache_path = quiet._duration_cache_path(fixture)
        self.assertFalse(cache_path.exists(), "cache must start cold for this fixture")

        log = str(Path(self.tmp.name) / "run.log")
        cmd = [str(QUIET), "--log", log, "--jobs", "3", "--",
               sys.executable, "-m", "unittest", "discover", "-s", str(fixture), "-q"]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        self.assertTrue(r.stdout.startswith("quiet: OK"), r.stdout)

        cache = quiet._load_duration_cache(cache_path)
        self.assertEqual(set(cache), {"test_p0.py", "test_p1.py", "test_p2.py"})
        for v in cache.values():
            self.assertIsInstance(v, (int, float))
            self.assertGreaterEqual(v, 0)


if __name__ == "__main__":
    unittest.main()


class TestPlanUnits(unittest.TestCase):
    """`_plan_units` is the O-10 change: a file too slow to be one shard is
    cut across its own test classes, so the suite's floor stops being its
    slowest file (finding 31/F-02 -- tests/test_warmup.py was 575s of a
    ~1000s suite and `discover -p <one file>` could not split it).

    Pure input/output, no subprocess and no timing, so these cannot flake.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def write(self, name, classes, tests_each=1):
        body = ["import unittest", ""]
        for c in classes:
            body.append(f"class {c}(unittest.TestCase):")
            for n in range(tests_each):
                body.append(f"    def test_{n}(self):")
                body.append("        pass")
            body.append("")
        p = self.dir / name
        p.write_text("\n".join(body) + "\n")
        return p

    def test_a_cold_cache_splits_nothing(self):
        slow = self.write("test_slow.py", ["TestA", "TestB", "TestC", "TestD"])
        fast = self.write("test_fast.py", ["TestE"])
        units = quiet._plan_units([fast, slow], {}, jobs=4)
        self.assertEqual([u.classes for u in units], [[], []],
                         "with no timings there is no evidence to split on")

    def test_the_slow_file_is_split_and_the_others_are_not(self):
        slow = self.write("test_slow.py", ["TestA", "TestB", "TestC", "TestD"])
        fast = self.write("test_fast.py", ["TestE"])
        durations = {"test_slow.py": 600.0, "test_fast.py": 10.0}
        units = quiet._plan_units([fast, slow], durations, jobs=4)
        fast_units = [u for u in units if u.path.name == "test_fast.py"]
        slow_units = [u for u in units if u.path.name == "test_slow.py"]
        self.assertEqual(len(fast_units), 1)
        self.assertEqual(fast_units[0].classes, [])
        # target = 610/4 ~= 152.5s; 600/152.5 -> 4 groups, capped by 4 classes
        self.assertEqual(len(slow_units), 4)
        self.assertEqual(sorted(c for u in slow_units for c in u.classes),
                         ["TestA", "TestB", "TestC", "TestD"])

    def test_every_class_appears_exactly_once_across_the_groups(self):
        slow = self.write("test_slow.py", [f"Test{n}" for n in range(9)])
        units = quiet._plan_units([slow], {"test_slow.py": 900.0}, jobs=3)
        got = [c for u in units for c in u.classes]
        self.assertEqual(sorted(got), sorted(f"Test{n}" for n in range(9)))
        self.assertEqual(len(got), len(set(got)), "a class must not run twice")

    def test_a_file_is_never_split_past_its_class_count(self):
        slow = self.write("test_slow.py", ["TestOnly"])
        units = quiet._plan_units([slow], {"test_slow.py": 9000.0}, jobs=8)
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].classes, [], "one class cannot be spread over eight")

    def test_jobs_one_never_splits(self):
        slow = self.write("test_slow.py", ["TestA", "TestB"])
        units = quiet._plan_units([slow], {"test_slow.py": 600.0}, jobs=1)
        self.assertEqual([u.classes for u in units], [[]])

    def test_a_split_units_key_names_its_own_classes(self):
        u = quiet.Unit(Path("test_slow.py"), ["TestA", "TestB"])
        self.assertEqual(u.key, "test_slow.py::TestA+TestB")
        self.assertEqual(quiet.Unit(Path("test_slow.py")).key, "test_slow.py")

    def test_a_split_unit_runs_named_modules_from_the_tests_directory(self):
        u = quiet.Unit(Path("test_slow.py"), ["TestA"])
        argv = u.argv("python3", "tests")
        self.assertEqual(argv, ["python3", "-m", "unittest", "test_slow.TestA", "-q"])
        self.assertEqual(u.cwd("tests"), "tests",
                         "tests/ is not a package, so a bare module name needs that cwd")
        whole = quiet.Unit(Path("test_slow.py"))
        self.assertIn("discover", whole.argv("python3", "tests"))
        self.assertIsNone(whole.cwd("tests"))

    def test_a_files_duration_is_the_sum_of_its_split_units(self):
        durations = {"test_slow.py::TestA": 100.0, "test_slow.py::TestB": 200.0}
        self.assertEqual(300.0, quiet._file_duration(Path("test_slow.py"), durations))
        self.assertEqual(-1.0, quiet._file_duration(Path("test_new.py"), durations))

    def test_test_classes_reads_the_source_and_skips_classes_with_no_tests(self):
        p = self.write("test_mixed.py", ["TestReal"])
        p.write_text(p.read_text() + "\nclass Helper:\n    def build(self):\n        pass\n")
        self.assertEqual(["TestReal"], quiet._test_classes(p))

    def test_split_shards_agree_with_a_sequential_run(self):
        """End to end: the aggregate over split units reports the same test
        count and the same verdict as one plain run of the same files."""
        self.write("test_alpha.py", ["TestA", "TestB", "TestC", "TestD"], tests_each=2)
        self.write("test_beta.py", ["TestE"], tests_each=2)
        cache = quiet._duration_cache_path(self.dir)
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({"test_alpha.py": 600.0, "test_beta.py": 10.0}))
        self.addCleanup(lambda: cache.unlink(missing_ok=True))

        result = quiet._run_parallel_discover(sys.executable, str(self.dir), "test*.py", 4)
        self.assertIsNotNone(result)
        out, code = result
        self.assertEqual(0, code, out)
        self.assertIn("Ran 10 tests", out)
        self.assertIn("OK", out)

        seq = subprocess.run([sys.executable, "-m", "unittest", "discover",
                              "-s", str(self.dir), "-q"],
                             capture_output=True, text=True)
        self.assertIn("Ran 10 tests", seq.stdout + seq.stderr)


# ── RQ-09: a green gate reported as FAILED ───────────────────────────────
# From the PhotoVault app's open-fix list, 2026-09-24: `quiet` printed
# "FAILED · 2 failed" on a gate that was 1,522 passed and 0 failed. Two
# defects behind one symptom, and OPERATING-RULES sends every session to read
# exactly that printed line, so a wrong verdict there is worse than none.


class AGreenGateIsNotReportedAsFailed(unittest.TestCase):
    def test_an_application_debug_line_is_not_read_as_a_pytest_summary(self):
        """The exact line that did it: `failed` matched the prefix of
        `failedBatches` because the alternation had no word boundary."""
        output = ("[pv] hydrating viewport\n"
                  "[pv] batch settled found=2 failedBatches=0 ok=2\n"
                  "1522 passed, 3 warnings in 41.20s\n")
        summary, ok = quiet._detect(output)
        self.assertTrue(ok, f"a green gate was reported as failing: {summary}")
        self.assertIn("1522 passed", summary)

    def test_a_summary_shaped_substring_inside_a_line_is_ignored(self):
        """The second defect: the search was unanchored and ran line by line,
        so the first summary-looking fragment in the log won over pytest's
        real one."""
        output = ("collected 4 items / 1 error recovered, 2 failed retries queued\n"
                  "4 passed in 0.10s\n")
        summary, ok = quiet._detect(output)
        self.assertTrue(ok, summary)
        self.assertTrue(summary.startswith("4 passed"), summary)

    def test_a_real_failure_is_still_a_failure(self):
        """The fix must not buy quiet by making it quiet about real failures."""
        summary, ok = quiet._detect("2 failed, 1520 passed in 41.20s\n")
        self.assertFalse(ok)
        self.assertIn("2 failed", summary)

    def test_the_padded_form_pytest_actually_prints_is_matched(self):
        summary, ok = quiet._detect(
            "=========== 1522 passed, 3 warnings in 41.20s ============\n")
        self.assertTrue(ok, summary)
        self.assertIn("1522 passed", summary)

    def test_zeros_spelled_out_are_still_green(self):
        """The engine's parallel gate prints its zeros; this is the regression
        the surrounding comment in bin/quiet was already written about."""
        summary, ok = quiet._detect(
            "426 passed, 0 failed, 0 errors, 2 skipped in 12.00s\n")
        self.assertTrue(ok, summary)

    def test_xfailed_and_deselected_counts_do_not_read_as_failures(self):
        """`xfailed` begins with an x, not with `failed`, but a count of
        deselected or xfailed tests is not a failure either way -- and the
        engine's own gate prints both."""
        summary, ok = quiet._detect(
            "8078 passed, 83 skipped, 17 xfailed in 540.00s\n")
        self.assertTrue(ok, summary)
        self.assertIn("17 xfailed", summary)
