"""`bin/conformance` -- /standard's twelve items, measured (proposal 21, S-04).

The sponsor made the standard mandatory for every project (A-01 to A-04), and
a session reports "standard: N of 12 hold". That number has to come from a
tool, not from a session's say-so. What these tests hold the tool to:

  * an empty git repository: most items do not hold, exit 1;
  * a project made conforming the way /standard says -- derecord, new-proposal,
    warmup --migrate, rulecheck --align, a commit through the installed hook --
    holds every item, except item 5, which waits on common-rules until the
    lead-prompt template carries its marker (S-06);
  * breaking one item breaks that item, and only that item -- except where the
    card (item 12) necessarily sees the same fault, and the test says so;
  * waiting never makes the exit 1; not a git repository is exit 2;
  * every printed value is escaped, so a ledger id cannot forge a status line;
  * it is read-only: a run changes no byte and no mtime in the project, .git
    included.

The expected states are written here, never read back from the tool.

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import datetime
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))   # test_rulecheck's FakeRules
CONFORMANCE = ROOT / "bin" / "conformance"
DERECORD = ROOT / "bin" / "derecord"
WARMUP = ROOT / "bin" / "warmup"
NEW_PROPOSAL = ROOT / "bin" / "new-proposal"
RULECHECK = ROOT / "bin" / "rulecheck"
TEMPLATE = ROOT / "templates" / "lead-prompt.md"
MARKER = "<!-- common-rules:lead-prompt proposal/21 -->"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
# RF-01: item 9's own cutoff is a fixed date (2026-09-17). A done log entry
# dated with a fixed pre-cutoff timestamp, rather than NOW, keeps the
# conforming fixture's one done item (B-01) out of item 9's "needs a Ruflo
# record" set regardless of when these tests actually run.
PRE_CUTOFF_DONE_AT = "2026-09-10T09:00:00+02:00"

HOLDS, NOT, WAITING = "holds", "does not hold", "waiting"

CLAUDE_MD = """# demo

This project follows common-rules' CLAUDE-workflow.md.

## Hard safety rules

1. **Never write to the real store.** It is the only copy.
2. **Never kill a process by name.** A PID you started only.
"""

HANDOFF = """# demo -- start here

## Prohibitions, verbatim
1. **Never write to the real store.** It is the only copy.
"""

DECLARATION = {
    "read_order": ["CLAUDE.md", "HANDOFF.md"],
    "safety_rules": "CLAUDE.md#Hard safety rules",
    "gates": {"quick": "true", "merge": "true"},
}

TAG = "[ruflo · medium · sonnet]"


def run(cmd, check=True):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, check=False)
    if check and r.returncode != 0:
        raise AssertionError(f"{cmd} exited {r.returncode}\n--stdout--\n{r.stdout}\n--stderr--\n{r.stderr}")
    return r


def git(root: Path, *args, check=True):
    return run(["git", "-C", root, *args], check=check)


def write(root: Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def commit(root: Path, msg: str):
    git(root, "add", "-A")
    git(root, "commit", "-qm", msg)


def ledger_path(root: Path) -> Path:
    found = sorted((root / "docs" / "proposals").glob("01-*.json"))
    assert len(found) == 1, found
    return found[0]


def write_swarm_db(root: Path, rows: list[tuple[str, str]] = ()):
    """A minimal Ruflo memory.db -- the memory_entries(key, namespace) table
    bin/conformance item 9 reads read-only. Written under .swarm/, which
    derecord's own ignore lines already exclude, so it never shows up in
    `git status`."""
    db = root / ".swarm" / "memory.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    db.unlink(missing_ok=True)  # overwrite, not append, when a fixture already wrote one
    conn = sqlite3.connect(db)
    try:
        conn.execute("CREATE TABLE memory_entries (key TEXT, namespace TEXT)")
        conn.executemany("INSERT INTO memory_entries (key, namespace) VALUES (?, ?)", rows)
        conn.commit()
    finally:
        conn.close()


def edit_ledger(root: Path, change):
    p = ledger_path(root)
    data = json.loads(p.read_text())
    change(data)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def plan(data: dict):
    done_log = [{"at": PRE_CUTOFF_DONE_AT, "event": "done", "by": "lead",
                "evidence": "ruflo-item done B-01: memory stored"}]
    data["phases"] = [{"id": "B", "name": "Build", "goal": "build it", "exit": "built"}]
    data["items"] = [
        {"id": "B-01", "phase": "B", "cx": "C2", "title": "first", "status": "done",
         "tier": "medium", "model": "sonnet", "tag": TAG, "log": done_log},
        {"id": "B-02", "phase": "B", "cx": "C2", "title": "second", "status": "blocked", "owner": "lead",
         "tier": "medium", "model": "sonnet", "tag": TAG, "log": []},
        {"id": "B-03", "phase": "B", "cx": "C2", "title": "third", "status": "not started",
         "depends": ["B-01"], "tier": "medium", "model": "sonnet", "tag": TAG, "log": []},
    ]
    data["asks"] = [{"id": "A-01", "at": NOW, "kind": "decision", "state": "open", "owner": "sponsor",
                     "quote": "which one first"}]


def build_empty(root: Path):
    root.mkdir(parents=True)
    git(root, "init", "-q", "-b", "main")


def build_conforming(root: Path):
    """What /standard section 2 says to do, with the tools it names."""
    build_empty(root)
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "t")
    git(root, "config", "commit.gpgsign", "false")
    write(root, "CLAUDE.md", CLAUDE_MD)
    write(root, "HANDOFF.md", HANDOFF)
    write(root, "docs/OPERATING-RULES.md", "# Operating rules\n\n## 1 The plan\n- one plan\n")
    write(root, ".common-rules.json", json.dumps(DECLARATION, indent=2) + "\n")
    commit(root, "seed")
    run([DERECORD, root])                                                        # item 4
    run([sys.executable, NEW_PROPOSAL, "--project", root, "Demo plan"])          # item 7
    edit_ledger(root, plan)                                                      # items 2, 6, 9
    run([sys.executable, WARMUP, "--project", root, "--migrate", "--at", NOW, "--no-recall"])  # item 11
    # --implemented: the real CHANGELOG.md this reads against (no
    # COMMON_RULES_DIR override here) carries mandatory Standard change
    # entries, and P21 F-01 makes plain `--align` refuse past those.
    run([sys.executable, RULECHECK, "--project", root, "--align", "--implemented"])  # item 1
    prompt = root / "docs" / "handovers" / "lead-prompt.md"                      # item 5
    if MARKER not in prompt.read_text():
        # Until S-06 puts the marker in the template, derecord seeds a prompt
        # without it; the regenerated prompt /standard asks for carries it.
        prompt.write_text(MARKER + "\n" + prompt.read_text())
    commit(root, "standard")                    # the pre-commit hook renders the page and the checkpoint
    # item 9 (RF-01): B-01's own done log entry predates the 2026-09-17
    # cutoff, so no record is required for it -- but item 9 still requires a
    # readable .swarm/memory.db to exist at all, so the conforming fixture
    # gets an empty one.
    write_swarm_db(root)
    status = git(root, "status", "--porcelain").stdout
    assert status == "", f"the conforming fixture left changes behind:\n{status}"


def expected_base() -> dict[int, str]:
    states = {n: HOLDS for n in range(1, 13)}
    if MARKER not in TEMPLATE.read_text():
        states[5] = WAITING
    return states


def conformance(project: Path, *args):
    return subprocess.run([sys.executable, str(CONFORMANCE), "--project", str(project), *args],
                          capture_output=True, text=True, check=False)


def report(project: Path) -> tuple[dict, int]:
    r = conformance(project, "--json")
    try:
        return json.loads(r.stdout), r.returncode
    except ValueError:
        raise AssertionError(f"--json printed no JSON (exit {r.returncode}):\n{r.stdout}\n{r.stderr}") from None


def states_of(data: dict) -> dict[int, str]:
    return {item["n"]: item["state"] for item in data["items"]}


def load_module():
    loader = importlib.machinery.SourceFileLoader("conformance_under_test", str(CONFORMANCE))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


_TMP: tempfile.TemporaryDirectory | None = None
BASE: Path | None = None


def setUpModule():
    global _TMP, BASE
    _TMP = tempfile.TemporaryDirectory()
    BASE = Path(_TMP.name) / "base" / "demo"
    build_conforming(BASE)


def tearDownModule():
    if _TMP is not None:
        _TMP.cleanup()


class Copy(unittest.TestCase):
    """A fresh copy of the conforming project per test."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name) / "demo"
        shutil.copytree(BASE, self.p, symlinks=True)

    def tearDown(self):
        self.tmp.cleanup()

    def assert_breaks(self, broken: set[int], also: set[int] = frozenset()):
        """`broken` do not hold; every other item is as in the conforming
        project, except `also`, which the test names as seeing the same fault."""
        data, code = report(self.p)
        got, want = states_of(data), expected_base()
        for n in broken:
            self.assertEqual(got[n], NOT, f"item {n} should not hold: {data['items'][n - 1]}")
            item = data["items"][n - 1]
            self.assertTrue(item["why"] and item["fix"], f"item {n} must say why and the fix: {item}")
        for n in set(range(1, 13)) - set(broken) - set(also):
            self.assertEqual(got[n], want[n], f"item {n} changed too: {data['items'][n - 1]}")
        self.assertEqual(code, 1)
        return data

    def item(self, data: dict, n: int) -> dict:
        return data["items"][n - 1]


class TestEmptyRepository(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name) / "empty"
        build_empty(self.p)

    def tearDown(self):
        self.tmp.cleanup()

    def test_most_items_do_not_hold_and_exit_is_1(self):
        data, code = report(self.p)
        self.assertEqual(code, 1)
        got = states_of(data)
        for n in (1, 2, 3, 4, 5, 6, 7, 9, 11, 12):
            self.assertEqual(got[n], NOT, f"item {n}: {data['items'][n - 1]}")
        # Nothing to duplicate and nothing published: vacuously true, not waived.
        self.assertEqual(got[8], HOLDS)
        self.assertEqual(got[10], HOLDS)
        self.assertEqual(data["hold"], 2)

    def test_first_line_is_the_count_then_one_line_per_item(self):
        r = conformance(self.p)
        lines = r.stdout.splitlines()
        self.assertEqual(lines[0], "standard: 2 of 12 hold")
        self.assertEqual(len(lines), 13, r.stdout)
        for n, line in enumerate(lines[1:], start=1):
            self.assertRegex(line, rf"^[✓✗…] {n} ")

    def test_not_a_git_repository_could_not_run(self):
        with tempfile.TemporaryDirectory() as plain:
            for where in (Path(plain), Path(plain) / "missing"):
                r = conformance(where)
                self.assertEqual(r.returncode, 2, r.stderr)
                # Python also exits 2 for a script that does not exist: the
                # sentence is what proves the tool ran and refused.
                self.assertIn("not inside a git repository -- could not run", r.stderr)
                self.assertEqual(r.stdout, "")


class TestConforming(Copy):

    def test_every_item_holds_or_waits_on_common_rules_and_exit_is_0(self):
        data, code = report(self.p)
        self.assertEqual(states_of(data), expected_base(), json.dumps(data, indent=2, ensure_ascii=False))
        self.assertEqual(code, 0, "an item that only waits must not make the exit 1")
        self.assertEqual(data["hold"], sum(1 for s in expected_base().values() if s == HOLDS))
        self.assertEqual(data["total"], 12)

    def test_the_text_report_matches_the_json(self):
        r = conformance(self.p)
        lines = r.stdout.splitlines()
        want = expected_base()
        self.assertEqual(lines[0], f"standard: {sum(1 for s in want.values() if s == HOLDS)} of 12 hold")
        marks = {HOLDS: "✓", NOT: "✗", WAITING: "…"}
        for n, line in enumerate(lines[1:], start=1):
            self.assertTrue(line.startswith(f"{marks[want[n]]} {n} "), line)
        if want[5] == WAITING:
            self.assertIn("waiting on common-rules", lines[5])
            self.assertIn("S-06", lines[5])

    def test_json_shape(self):
        data, _ = report(self.p)
        self.assertEqual(set(data), {"project", "hold", "total", "items"})
        self.assertEqual([i["n"] for i in data["items"]], list(range(1, 13)))
        for item in data["items"]:
            self.assertEqual(set(item), {"n", "name", "state", "why", "fix"})
            self.assertIn(item["state"], (HOLDS, NOT, WAITING))

    def test_all_twelve_hold_once_the_template_carries_the_marker(self):
        mod = load_module()
        template = Path(self.tmp.name) / "lead-prompt.md"
        template.write_text(MARKER + "\n" + TEMPLATE.read_text().replace(MARKER, ""))
        mod.LEAD_TEMPLATE = template
        data = mod.measure(self.p)
        self.assertEqual(data["hold"], 12, json.dumps(data, indent=2, ensure_ascii=False))
        self.assertEqual(mod.exit_code(data), 0)

    def test_a_run_writes_nothing(self):
        def snapshot(root: Path) -> dict:
            out = {}
            for dirpath, dirnames, filenames in os.walk(root):
                for name in dirnames + filenames:
                    p = Path(dirpath) / name
                    st = p.lstat()
                    body = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() and not p.is_symlink() else None
                    out[str(p.relative_to(root))] = (st.st_mtime_ns, st.st_size, body)
            return out

        # A fresh copy's index no longer matches the files' stat data: exactly
        # when a plain `git status` or `git diff` would rewrite .git/index.
        before = snapshot(self.p)
        text_run = conformance(self.p)
        json_run = conformance(self.p, "--json")
        # A run that did nothing would write nothing too: prove both measured.
        self.assertTrue(text_run.stdout.startswith("standard: "), text_run.stdout + text_run.stderr)
        self.assertEqual(len(json.loads(json_run.stdout)["items"]), 12)
        self.assertEqual(snapshot(self.p), before)


class TestItem1Rules(Copy):

    def test_no_stamp_does_not_hold(self):
        git(self.p, "rm", "-q", ".common-rules-version")
        commit(self.p, "unstamp")
        data = self.assert_breaks({1})
        self.assertIn("rulecheck", self.item(data, 1)["fix"])

    def test_the_rules_repository_itself_holds(self):
        mod = load_module()
        result = mod.check_rules(mod.Context(ROOT))
        self.assertEqual(result.state, HOLDS, result)

    def test_an_untracked_stamp_does_not_hold(self):
        git(self.p, "rm", "-q", "--cached", ".common-rules-version")
        # Not commit(): its `git add -A` would track the stamp again.
        git(self.p, "commit", "-qm", "untrack the stamp")
        self.assertTrue((self.p / ".common-rules-version").is_file())
        data = self.assert_breaks({1})
        self.assertIn("not committed", self.item(data, 1)["why"])

    def test_a_committed_crlf_stamp_holds(self):
        """S-04 final review: text-mode git output turned \\r\\n into \\n, so a stamp
        committed exactly as it is on disk read "not committed"."""
        import subprocess as sp
        stamp = self.p / ".common-rules-version"
        stamp.write_bytes(stamp.read_text().strip().encode() + b"\r\n")
        commit(self.p, "crlf stamp")
        size = sp.run(["git", "-C", str(self.p), "cat-file", "-s", "HEAD:.common-rules-version"],
                      capture_output=True, text=True).stdout.strip()
        if size != str(len(stamp.read_bytes())):
            self.skipTest("this fixture normalises line endings on commit")
        mod = load_module()
        self.assertTrue(mod.stamp_committed(mod.Context(self.p)))

    def test_a_stamp_changed_since_head_does_not_hold(self):
        stamp = self.p / ".common-rules-version"
        stamp.write_text(stamp.read_text() + "\n")      # the same version, but not what HEAD holds
        data = self.assert_breaks({1})
        self.assertIn("not committed", self.item(data, 1)["why"])

    def test_without_mandatory_pending_it_waits_on_common_rules(self):
        mod = load_module()
        mod.MANDATORY_PENDING = None
        result = mod.check_rules(mod.Context(self.p))
        self.assertEqual(result.state, WAITING, result)

    def test_rulecheck_runs_in_process_without_optional_locks(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("GIT_OPTIONAL_LOCKS", None)
            mod = load_module()
            mod.check_rules(mod.Context(self.p))
            self.assertEqual(os.environ.get("GIT_OPTIONAL_LOCKS"), "0")


class TestItem1AgainstRulecheck(unittest.TestCase):
    """Item 1 through bin/rulecheck's real mandatory_pending(), on the FakeRules
    fixture tests/test_rulecheck.py builds. Nothing is mocked."""

    def setUp(self):
        from test_rulecheck import POINTER, FakeRules
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = Path(self._tmp.name)
        self.rules = FakeRules(tmp)
        env = mock.patch.dict(os.environ, {"COMMON_RULES_DIR": str(self.rules.root)})
        env.start()
        self.addCleanup(env.stop)
        self.proj = tmp / "app"
        build_empty(self.proj)
        git(self.proj, "config", "user.email", "t@example.com")
        git(self.proj, "config", "user.name", "t")
        write(self.proj, "CLAUDE.md", POINTER)

    def stamp(self, version: str):
        write(self.proj, ".common-rules-version", version + "\n")
        commit(self.proj, "stamp")

    def result(self):
        mod = load_module()
        self.assertIsNotNone(mod.MANDATORY_PENDING, "bin/rulecheck has no mandatory_pending()")
        return mod.check_rules(mod.Context(self.proj))

    def test_aligned_holds(self):
        self.stamp(self.rules.version())
        self.assertEqual(self.result().state, HOLDS)

    def test_behind_a_mandatory_change_does_not_hold_and_names_it(self):
        self.stamp(self.rules.version())
        self.rules.add("2026-09-14 · Reheat is mandatory", "run derecord again")
        r = self.result()
        self.assertEqual(r.state, NOT, r)
        self.assertIn("Reheat is mandatory", r.why)
        self.assertIn("--align", r.fix)

    def test_behind_on_information_only_holds(self):
        self.stamp(self.rules.version())
        self.rules.add("2026-09-14 · A wording fix")
        self.assertEqual(self.result().state, HOLDS)

    def test_diverged_counts_what_main_added(self):
        self.rules.add("2026-09-14 · Here", "already here")
        self.stamp(self.rules.ahead("2026-09-15 · Side", "only on a side branch"))
        self.rules.add("2026-09-16 · New on main", "do the new thing")
        r = self.result()
        self.assertEqual(r.state, NOT, r)
        self.assertIn("New on main", r.why)

    def test_truly_ahead_holds_and_says_so(self):
        self.rules.add("2026-09-14 · Here", "already here")
        self.stamp(self.rules.ahead("2026-09-15 · Future", "not here yet"))
        r = self.result()
        self.assertEqual(r.state, HOLDS, r)
        self.assertIn("ahead of this rules checkout -- update common-rules", r.why)

    def test_an_unresolvable_stamp_does_not_hold_and_lists_every_entry(self):
        self.rules.add("2026-09-14 · First", "do one")
        self.rules.add("2026-09-15 · Second", "do two")
        self.stamp("9-deadbee")
        r = self.result()
        self.assertEqual(r.state, NOT, r)
        self.assertIn("the stamp names no commit in common-rules", r.why)
        self.assertIn("First", r.why)
        self.assertIn("Second", r.why)
        self.assertIn("--align", r.fix)
        self.assertNotIn("CLAUDE-workflow.md", r.fix)


OWN_TRACKER = {"own": True, "by": "sponsor", "at": "2026-09-14T21:00:00+02:00",
               "quote": "this one gets a tracker of its own"}
INDEX = "docs/proposals/tracker/index.html"
URL = "https://claude.ai/code/artifact/00000000-0000-0000-0000-000000000000"


class TestItem2Migrated(Copy):
    """Proposal 22, T-02: item 2 reads the project's one tracker page, and a
    per-ledger page only for a ledger that records its own tracker."""

    def tracker(self, *args):
        return run([sys.executable, ROOT / "bin" / "tracker", *args])

    def test_a_stale_tracker_page_does_not_hold(self):
        edit_ledger(self.p, lambda d: d.update(title="Demo plan, renamed"))
        # The card fails on the same stale page and checkpoint.
        data = self.assert_breaks({2}, also={12})
        self.assertIn(f"page {INDEX} is stale", self.item(data, 2)["why"])
        self.assertIn("tracker board", self.item(data, 2)["fix"])

    def test_a_missing_project_page_does_not_hold(self):
        (self.p / INDEX).unlink()
        data = self.assert_breaks({2}, also={12})
        self.assertIn(f"page {INDEX} is missing", self.item(data, 2)["why"])
        self.assertIn("tracker board --project", self.item(data, 2)["fix"])

    def test_the_conforming_project_holds_on_its_project_page(self):
        data, _ = report(self.p)
        self.assertEqual(HOLDS, self.item(data, 2)["state"])
        self.assertIn("the project page matching", self.item(data, 2)["why"])

    def test_a_per_ledger_page_of_a_ledger_without_its_own_tracker_is_not_read(self):
        write(self.p, f"docs/proposals/tracker/{ledger_path(self.p).stem}.html", "an old per-proposal page\n")
        data, code = report(self.p)
        self.assertEqual(states_of(data), expected_base(), json.dumps(data, indent=2, ensure_ascii=False))
        self.assertEqual(code, 0)

    def test_a_ledger_with_its_own_tracker_needs_its_own_page(self):
        edit_ledger(self.p, lambda d: d.update(tracker=OWN_TRACKER))
        self.tracker("board", "--project", self.p)
        own_page = self.p / "docs" / "proposals" / "tracker" / f"{ledger_path(self.p).stem}.html"
        own_page.unlink(missing_ok=True)
        data = self.assert_breaks({2}, also={12})
        self.assertIn(f"page docs/proposals/tracker/{own_page.name} is missing", self.item(data, 2)["why"])
        self.assertIn("tracker render", self.item(data, 2)["fix"])
        self.tracker("render", ledger_path(self.p))
        data, _ = report(self.p)
        self.assertEqual(HOLDS, self.item(data, 2)["state"], self.item(data, 2))
        self.assertIn("1 own tracker page(s) matching", self.item(data, 2)["why"])


class TestItem3Declared(Copy):

    def test_no_quick_gate_does_not_hold(self):
        decl = dict(DECLARATION, gates={"merge": "true"})
        write(self.p, ".common-rules.json", json.dumps(decl, indent=2) + "\n")
        commit(self.p, "drop the quick gate")
        data = self.assert_breaks({3})
        self.assertIn("gates.quick", self.item(data, 3)["why"])


class TestItem4Installed(Copy):

    def test_no_posttooluse_agent_hook_does_not_hold(self):
        path = self.p / ".claude" / "settings.json"
        settings = json.loads(path.read_text())
        del settings["hooks"]["PostToolUse"]
        path.write_text(json.dumps(settings, indent=2))
        commit(self.p, "drop the agent hook")
        data = self.assert_breaks({4})
        self.assertIn("posttooluse-agent", self.item(data, 4)["why"])

    def test_an_edited_pre_commit_hook_does_not_hold(self):
        hook = Path(git(self.p, "rev-parse", "--git-path", "hooks").stdout.strip())
        hook = (self.p / hook if not hook.is_absolute() else hook) / "pre-commit"
        hook.write_text(hook.read_text() + "\n# edited by hand\n")
        data = self.assert_breaks({4})
        self.assertIn("pre-commit", self.item(data, 4)["why"])

    def drop_ignore_line(self, line: str):
        gi = self.p / ".gitignore"
        kept = [l for l in gi.read_text().splitlines(keepends=True) if l.strip() != line]
        self.assertNotEqual(len(kept), len(gi.read_text().splitlines()), f"{line} was not in .gitignore")
        gi.write_text("".join(kept))
        commit(self.p, f"drop {line} from .gitignore")

    def test_a_missing_ruflo_ignore_line_does_not_hold(self):
        self.drop_ignore_line("ruvector.db")
        data = self.assert_breaks({4})
        self.assertIn("ruvector.db", self.item(data, 4)["why"])

    def test_a_nested_gitignore_inside_the_project_counts(self):
        # The PhotoVault app ignores .claude-flow/data and logs from its own
        # .claude-flow/.gitignore; the path is ignored, so the line holds.
        self.drop_ignore_line(".claude-flow/data")
        write(self.p, ".claude-flow/.gitignore", "data/\n")
        commit(self.p, "ignore it from a nested file")
        data, _ = report(self.p)
        self.assertEqual(states_of(data), expected_base(), self.item(data, 4))

    def test_the_local_exclude_file_does_not_count(self):
        # .git/info/exclude is this machine's, not the project's: a clone
        # would track the runtime file.
        self.drop_ignore_line("ruvector.db")
        exclude = Path(git(self.p, "rev-parse", "--git-path", "info/exclude").stdout.strip())
        exclude = exclude if exclude.is_absolute() else self.p / exclude
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text((exclude.read_text() if exclude.is_file() else "") + "ruvector.db\n")
        data = self.assert_breaks({4})
        self.assertIn("ruvector.db", self.item(data, 4)["why"])

    def test_a_personal_excludes_file_named_gitignore_does_not_count(self):
        self.drop_ignore_line("ruvector.db")
        personal = Path(self.tmp.name) / ".gitignore"
        personal.write_text("ruvector.db\n")
        git(self.p, "config", "core.excludesFile", str(personal))
        data = self.assert_breaks({4})
        self.assertIn("ruvector.db", self.item(data, 4)["why"])

    def test_a_negated_ignore_line_does_not_hold(self):
        # The verbatim line is still there; a later `!` line re-includes the path.
        gi = self.p / ".gitignore"
        gi.write_text(gi.read_text() + "!ruvector.db\n")
        commit(self.p, "re-include ruvector.db")
        data = self.assert_breaks({4})
        self.assertIn("ruvector.db", self.item(data, 4)["why"])

    def hook_path(self) -> Path:
        hooks = Path(git(self.p, "rev-parse", "--git-path", "hooks").stdout.strip())
        return (hooks if hooks.is_absolute() else self.p / hooks) / "pre-commit"

    def current_body(self) -> str:
        return self.hook_path().read_text().split("\n", 2)[2]

    def write_marked_hook(self, body: str):
        """A hook that passes derecord's own "may I overwrite" test."""
        digest = hashlib.sha256(body.encode()).hexdigest()
        self.hook_path().write_text(f"#!/usr/bin/env bash\n# derecord-body-sha256: {digest}\n{body}")

    def test_a_forged_self_consistent_hook_does_not_hold(self):
        self.write_marked_hook("exit 0\n")
        data = self.assert_breaks({4})
        self.assertIn("pre-commit", self.item(data, 4)["why"])

    def test_a_hook_from_an_older_derecord_does_not_hold(self):
        body = self.current_body()
        older = body.replace("# 1. never commit a conflict marker.\n", "")
        self.assertNotEqual(older, body)
        self.write_marked_hook(older)
        data = self.assert_breaks({4})
        self.assertIn("derecord", self.item(data, 4)["fix"])

    def test_a_hook_naming_another_rules_directory_does_not_hold(self):
        body = self.current_body()
        elsewhere = body.replace(f'RULES="{ROOT}"', f'RULES="{Path(self.tmp.name) / "other-rules"}"')
        self.assertNotEqual(elsewhere, body)
        self.write_marked_hook(elsewhere)
        self.assert_breaks({4})

    def test_a_copied_hooks_directory_does_not_hold(self):
        fake = Path(self.tmp.name) / "copied-rules"
        shutil.copytree(ROOT / "hooks", fake / "hooks")
        write(fake, "bin/derecord", "#!/bin/sh\n")
        path = self.p / ".claude" / "settings.json"
        settings = json.loads(path.read_text())
        for entry in settings["hooks"]["Stop"]:
            for h in entry["hooks"]:
                if h["command"].endswith("/hooks/stop"):
                    h["command"] = str(fake / "hooks" / "stop")
        path.write_text(json.dumps(settings, indent=2))
        commit(self.p, "a copied hook")
        data = self.assert_breaks({4})
        self.assertIn("hooks/stop", self.item(data, 4)["why"])

    def test_a_tracked_ruflo_runtime_file_does_not_hold(self):
        write(self.p, ".swarm/memory.db", "x")
        git(self.p, "add", "-f", ".swarm/memory.db")
        git(self.p, "commit", "-qm", "track runtime state")
        # .swarm/memory.db is also the Ruflo memory state item 9 looks for.
        data = self.assert_breaks({4}, also={9})
        self.assertIn(".swarm/memory.db", self.item(data, 4)["why"])
        self.assertIn("git rm", self.item(data, 4)["fix"])


class TestItem5LeadPrompt(Copy):

    def test_no_lead_prompt_does_not_hold(self):
        git(self.p, "rm", "-q", "docs/handovers/lead-prompt.md")
        commit(self.p, "drop the prompt")
        self.assert_breaks({5})

    def test_a_prompt_without_the_marker_does_not_hold_once_the_template_has_it(self):
        prompt = self.p / "docs" / "handovers" / "lead-prompt.md"
        prompt.write_text(prompt.read_text().replace(MARKER, ""))
        mod = load_module()
        template = Path(self.tmp.name) / "lead-prompt.md"
        template.write_text(MARKER + "\n")
        mod.LEAD_TEMPLATE = template
        result = mod.check_lead_prompt(mod.Context(self.p))
        self.assertEqual(result.state, NOT, result)

    def test_a_template_without_the_marker_waits_on_s06(self):
        mod = load_module()
        template = Path(self.tmp.name) / "lead-prompt.md"
        template.write_text("# no marker yet\n")
        mod.LEAD_TEMPLATE = template
        result = mod.check_lead_prompt(mod.Context(self.p))
        self.assertEqual(result.state, WAITING, result)
        self.assertIn("S-06", result.why)

    def test_a_superseded_prompt_is_not_the_lead_prompt(self):
        write(self.p, "docs/handovers/superseded/2026-09-01-lead-prompt.md", "# the old one, no marker\n")
        data, _ = report(self.p)
        self.assertEqual(states_of(data)[5], expected_base()[5])


class TestItem6CommonLanguage(Copy):

    def test_a_row_without_a_tag_does_not_hold(self):
        edit_ledger(self.p, lambda d: d["items"][2].pop("tag"))
        commit(self.p, "untag")
        data = self.assert_breaks({6})
        self.assertIn("B-03", self.item(data, 6)["why"])

    def test_a_blocked_row_without_an_owner_does_not_hold(self):
        edit_ledger(self.p, lambda d: d["items"][1].pop("owner"))
        commit(self.p, "unown")
        data = self.assert_breaks({6})
        self.assertIn("B-02", self.item(data, 6)["why"])

    def test_an_open_decision_ask_without_an_owner_does_not_hold(self):
        edit_ledger(self.p, lambda d: d["asks"][0].pop("owner"))
        commit(self.p, "unown the ask")
        data = self.assert_breaks({6})
        self.assertIn("A-01", self.item(data, 6)["why"])

    def test_two_routing_tables_do_not_hold(self):
        edit_ledger(self.p, lambda d: d.update(model_routing={"simple": "haiku"}))
        commit(self.p, "a second table")
        data = self.assert_breaks({6})
        self.assertIn("model_routing", self.item(data, 6)["why"])

    def test_no_routing_table_does_not_hold(self):
        edit_ledger(self.p, lambda d: d.pop("tiers"))
        commit(self.p, "no table")
        self.assert_breaks({6})

    def test_an_invalid_request_does_not_hold(self):
        edit_ledger(self.p, lambda d: d.update(requests=[{"id": "RQ-01", "from": "demo", "state": "open"}]))
        # The ledger no longer validates, so migration (2) and the card (12) see it too.
        data = self.assert_breaks({6}, also={2, 12})
        self.assertIn("RQ-01", self.item(data, 6)["why"])

    def test_a_tag_that_is_not_the_tag_shape_does_not_hold(self):
        edit_ledger(self.p, lambda d: d["items"][2].update(tag="x"))
        commit(self.p, "tag x")
        data = self.assert_breaks({6})
        self.assertIn("B-03", self.item(data, 6)["why"])

    def test_a_tag_that_disagrees_with_the_rows_tier_and_model_does_not_hold(self):
        edit_ledger(self.p, lambda d: d["items"][2].update(tag="[ruflo · high · opus]"))
        commit(self.p, "a tag from another row")
        data = self.assert_breaks({6})
        self.assertIn("B-03", self.item(data, 6)["why"])

    def test_an_owner_that_is_not_sponsor_lead_or_a_session_does_not_hold(self):
        edit_ledger(self.p, lambda d: d["items"][1].update(owner="bob"))
        # validate() names it too, so migration (2) and the card (12) see it.
        data = self.assert_breaks({6}, also={2, 12})
        self.assertIn("B-02", self.item(data, 6)["why"])


class TestItem7Proposals(Copy):

    def test_a_new_page_without_a_status_does_not_hold(self):
        write(self.p, "docs/proposals/02-by-hand.html", "<!doctype html><title>by hand</title>\n")
        data = self.assert_breaks({7})
        self.assertIn("02-by-hand.html", self.item(data, 7)["why"])


class TestItem8Duplicates(Copy):

    def twin(self) -> Path:
        return ledger_path(self.p).with_suffix(".md")

    def test_a_hand_kept_md_twin_does_not_hold(self):
        self.twin().write_text("# Demo plan\n\n" + "".join(f"- B-0{i} status\n" for i in range(1, 9)))
        data = self.assert_breaks({8})
        self.assertIn(self.twin().name, self.item(data, 8)["why"])

    def test_a_pointer_naming_the_ledger_holds(self):
        self.twin().write_text(f"# Demo plan\n\nRetired: the plan is {ledger_path(self.p).name}.\n")
        data, _ = report(self.p)
        self.assertEqual(states_of(data), expected_base())

    def test_a_short_twin_that_does_not_name_the_ledger_does_not_hold(self):
        self.twin().write_text("# Demo plan\n\nSee the other file.\n")
        self.assert_breaks({8})

    def test_a_declared_plan_page_holds(self):
        self.twin().write_text("# Demo plan\n\n" + "".join(f"- row {i}\n" for i in range(20)))
        write(self.p, ".common-rules.json", json.dumps(dict(DECLARATION, plan_page="true"), indent=2) + "\n")
        data, _ = report(self.p)
        self.assertEqual(states_of(data)[8], HOLDS)


POST_CUTOFF_DONE_AT = "2026-09-17T10:00:00+02:00"  # on the RF-01 cutoff itself
AFTER_CUTOFF_DONE_AT = "2026-09-20T10:00:00+02:00"


class TestItem9Ruflo(Copy):
    """RF-01: item 9 now reads .swarm/memory.db read-only with sqlite3
    (table memory_entries(key, namespace)) instead of treating a non-empty
    database, or a log line merely mentioning a Ruflo step, as proof. The
    conforming fixture's own B-01 is done, dated before the 2026-09-17
    cutoff, and needs no record; these tests close a second item (B-02) on
    or after the cutoff to exercise the evidence path."""

    def close_b02(self, at=POST_CUTOFF_DONE_AT):
        edit_ledger(self.p, lambda d: d["items"][1].update(
            status="done", log=[{"at": at, "event": "done", "by": "lead", "evidence": "shipped"}]))
        commit(self.p, "close B-02")

    def test_a_post_cutoff_done_item_without_records_does_not_hold(self):
        self.close_b02()
        data = self.assert_breaks({9})
        self.assertIn("B-02", self.item(data, 9)["why"])
        self.assertIn("2026-09-17", self.item(data, 9)["why"])

    def test_a_post_cutoff_done_item_with_both_records_holds(self):
        self.close_b02()
        write_swarm_db(self.p, [("item:B-02:start", "demo"), ("item:B-02:done", "demo")])
        data, _ = report(self.p)
        self.assertEqual(states_of(data)[9], HOLDS)

    def test_checkpoint_compatibility_done_record_holds(self):
        """`ruflo-item checkpoint` writes this done key beside its richer
        checkpoint key, so existing conformance remains compatible."""
        self.close_b02()
        write_swarm_db(self.p, [("item:B-02:start", "demo"),
                                ("item:B-02:checkpoint", "demo"),
                                ("item:B-02:done", "demo")])
        data, _ = report(self.p)
        self.assertEqual(states_of(data)[9], HOLDS)

    def test_only_a_start_record_still_does_not_hold(self):
        self.close_b02()
        write_swarm_db(self.p, [("item:B-02:start", "demo")])
        data = self.assert_breaks({9})
        self.assertIn("B-02", self.item(data, 9)["why"])

    def test_a_record_under_the_wrong_namespace_does_not_count(self):
        self.close_b02()
        write_swarm_db(self.p, [("item:B-02:start", "other-namespace"), ("item:B-02:done", "other-namespace")])
        self.assert_breaks({9})

    def test_pre_cutoff_items_are_ignored_but_counted(self):
        # B-01 (done, pre-cutoff) alone: nothing required, and the baseline
        # empty .swarm/memory.db already holds -- this pins that the note
        # appears once a pre-cutoff item exists.
        data, code = report(self.p)
        self.assertEqual(states_of(data)[9], HOLDS)
        self.assertIn("2026-09-17", self.item(data, 9)["why"])
        self.assertIn("not checked", self.item(data, 9)["why"])

    def test_f05_the_note_says_not_checked_not_missing_a_record(self):
        # F-05: the pre-cutoff note used to read "have no Ruflo record (not
        # counted)", which is false for any pre-cutoff item that does have a
        # done record -- it's excluded because it predates the cutoff and was
        # never checked, not because evidence is missing. Give B-01 (the
        # fixture's lone pre-cutoff done item) a done record and confirm the
        # why states the true reason and never claims the record is absent.
        write_swarm_db(self.p, [("item:B-01:start", "demo"), ("item:B-01:done", "demo")])
        data, code = report(self.p)
        why = self.item(data, 9)["why"]
        self.assertEqual(states_of(data)[9], HOLDS)
        self.assertIn("1 item(s) closed before 2026-09-17 not checked", why)
        self.assertIn("of which 1 have records", why)
        self.assertNotIn("no Ruflo record", why)

    def test_an_id_shared_by_two_ledgers_needs_only_one_record(self):
        run([sys.executable, NEW_PROPOSAL, "--project", self.p, "Second plan"])
        second = sorted((self.p / "docs" / "proposals").glob("02-*.json"))[0]
        data2 = json.loads(second.read_text())
        data2["phases"] = [{"id": "B", "name": "Build", "goal": "build it", "exit": "built"}]
        data2["items"] = [{"id": "B-02", "phase": "B", "cx": "C2", "title": "same id, other ledger",
                           "status": "done", "tier": "medium", "model": "sonnet", "tag": TAG,
                           "log": [{"at": AFTER_CUTOFF_DONE_AT, "event": "done", "by": "lead",
                                    "evidence": "shipped"}]}]
        second.write_text(json.dumps(data2, indent=2) + "\n")
        self.close_b02(at=AFTER_CUTOFF_DONE_AT)  # also commits the second ledger's own edits
        write_swarm_db(self.p, [("item:B-02:start", "demo"), ("item:B-02:done", "demo")])
        data, code = report(self.p)
        self.assertEqual(states_of(data)[9], HOLDS, self.item(data, 9))

    def test_switched_off_holds_and_says_by_whom(self):
        self.close_b02()
        edit_ledger(self.p, lambda d: d.update(switches={"ruflo": {"on": False, "by": "sponsor", "at": NOW}}))
        commit(self.p, "ruflo off")
        data, _ = report(self.p)
        self.assertEqual(states_of(data)[9], HOLDS)
        self.assertIn("switched off by sponsor", self.item(data, 9)["why"])

    def test_no_ledger_does_not_hold(self):
        mod = load_module()
        tmp = tempfile.TemporaryDirectory()
        try:
            root = Path(tmp.name) / "empty"
            build_empty(root)
            result = mod.check_ruflo(mod.Context(root))
            self.assertEqual(result.state, NOT)
            self.assertIn("no ledger", result.why)
        finally:
            tmp.cleanup()

    def test_a_status_keyed_close_entry_is_read_over_a_non_done_event(self):
        """`tracker set --status done --event "<free text>"` (RF-01 lead
        review): the event text does not say "done", but the entry's own
        `status` key does, and that is what must be read."""
        edit_ledger(self.p, lambda d: d["items"][1].update(
            status="done", log=[{"at": POST_CUTOFF_DONE_AT, "event": "shipped in PR #99",
                                  "by": "lead", "evidence": "", "status": "done"}]))
        commit(self.p, "close B-02 the tracker-set way")
        data = self.assert_breaks({9})
        self.assertIn("B-02", self.item(data, 9)["why"])

    def test_an_older_row_with_no_status_key_still_falls_back_to_the_event(self):
        self.close_b02()  # writes event="done", no status key -- the pre-RF-01 shape
        data = self.assert_breaks({9})
        self.assertIn("B-02", self.item(data, 9)["why"])

    def test_the_last_matching_entry_wins_when_a_row_logs_several(self):
        edit_ledger(self.p, lambda d: d["items"][1].update(status="done", log=[
            {"at": PRE_CUTOFF_DONE_AT, "event": "in progress", "by": "lead", "evidence": ""},
            {"at": POST_CUTOFF_DONE_AT, "event": "shipped", "by": "lead", "evidence": "", "status": "done"},
        ]))
        commit(self.p, "close B-02 with an earlier non-done entry first")
        data = self.assert_breaks({9})
        self.assertIn("B-02", self.item(data, 9)["why"])
        self.assertIn("2026-09-17", self.item(data, 9)["why"])

    def test_missing_swarm_database_does_not_hold(self):
        shutil.rmtree(self.p / ".swarm")
        self.assert_breaks({9})

    def test_an_unreadable_swarm_database_does_not_hold(self):
        write(self.p, ".swarm/memory.db", "not a sqlite database")
        self.assert_breaks({9})

    def test_a_zero_byte_swarm_database_does_not_hold(self):
        write(self.p, ".swarm/memory.db", "")
        self.assert_breaks({9})


class TestItem10Publishing(Copy):
    """Proposal 22, T-03: the sidecar of record is the project page's,
    docs/proposals/tracker/index.published.json. A per-ledger sidecar is read
    only for a ledger that records its own tracker (or a declared plan_page);
    a leftover one does not hold, and the fix is to remove it."""

    def tracker(self, *args):
        return run([sys.executable, ROOT / "bin" / "tracker", *args])

    def published_project(self):
        return run([sys.executable, ROOT / "bin" / "tracker", "published", "--project", self.p,
                    "--url", URL, "--by", "lead"])

    def test_a_leftover_per_ledger_sidecar_does_not_hold(self):
        stem = ledger_path(self.p).stem
        write(self.p, f"docs/proposals/tracker/{stem}.published.json",
              json.dumps({"url": URL, "digest": "0" * 64, "at": NOW, "by": None}) + "\n")
        # The card is silent about it (T-03), so item 12 still holds.
        data = self.assert_breaks({10})
        self.assertIn(f"{stem}.published.json", self.item(data, 10)["why"])
        self.assertIn("git rm", self.item(data, 10)["fix"])
        self.assertIn("tracker published --project", self.item(data, 10)["fix"])

    def test_a_malformed_leftover_is_not_read_either(self):
        stem = ledger_path(self.p).stem
        write(self.p, f"docs/proposals/tracker/{stem}.published.json", "{\"url\": 1}\n")
        data = self.assert_breaks({10})
        self.assertIn(f"{stem}.published.json", self.item(data, 10)["why"])

    def test_an_own_tracker_ledgers_sidecar_is_still_read(self):
        edit_ledger(self.p, lambda d: d.update(tracker=OWN_TRACKER))
        self.tracker("board", "--project", self.p)
        self.tracker("render", ledger_path(self.p))
        self.tracker("checkpoint", "--project", self.p)
        stem = ledger_path(self.p).stem
        write(self.p, f"docs/proposals/tracker/{stem}.published.json", "{\"url\": 1}\n")
        commit(self.p, "own tracker, a malformed sidecar")
        # The card reads this one, so item 12 sees the same fault.
        data = self.assert_breaks({10}, also={12})
        self.assertIn(f"{stem}.published.json", self.item(data, 10)["why"])

    def test_the_recorded_project_page_holds(self):
        r = self.published_project()
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        commit(self.p, "record the project page")
        data, code = report(self.p)
        self.assertEqual(states_of(data), expected_base(), json.dumps(data, indent=2, ensure_ascii=False))
        self.assertEqual(0, code)
        self.assertIn("1 publish record(s)", self.item(data, 10)["why"])

    def test_a_malformed_project_sidecar_does_not_hold(self):
        write(self.p, "docs/proposals/tracker/index.published.json", "{\"url\": 1}\n")
        # The card names the same unreadable sidecar.
        data = self.assert_breaks({10}, also={12})
        self.assertIn("index.published.json", self.item(data, 10)["why"])


class TestItem11Pointer(Copy):

    BEGIN = "<!-- common-rules:warmup -->"

    def test_a_committed_edit_to_the_block_does_not_hold(self):
        cm = self.p / "CLAUDE.md"
        cm.write_text(cm.read_text().replace("The ledger is the record.", "The ledger is a record."))
        commit(self.p, "edit the pointer")
        self.assert_breaks({11})

    def test_an_uncommitted_change_to_the_block_does_not_hold(self):
        cm = self.p / "CLAUDE.md"
        right = cm.read_text()
        cm.write_text(right.replace("The ledger is the record.", "The ledger is a record."))
        commit(self.p, "a stale pointer")
        cm.write_text(right)                    # the block is right again, but only on disk
        data = self.assert_breaks({11})
        self.assertIn("uncommitted", self.item(data, 11)["why"])

    def test_an_uncommitted_change_outside_the_block_holds(self):
        cm = self.p / "CLAUDE.md"
        cm.write_text(cm.read_text().replace("# demo", "# demo, renamed"))
        data, _ = report(self.p)
        self.assertEqual(states_of(data), expected_base())

    def test_a_claude_md_symlinked_out_of_the_project_does_not_hold(self):
        cm = self.p / "CLAUDE.md"
        outside = Path(self.tmp.name) / "CLAUDE.md"
        outside.write_text(cm.read_text())
        cm.unlink()
        cm.symlink_to(outside)
        # The declaration (3) and the card (12) refuse a read order outside the project too.
        data = self.assert_breaks({11}, also={3, 12})
        self.assertIn("not read", self.item(data, 11)["why"])

    def test_no_pointer_does_not_hold(self):
        cm = self.p / "CLAUDE.md"
        text = cm.read_text()
        cm.write_text(text[:text.index(self.BEGIN)])
        commit(self.p, "no pointer")
        self.assert_breaks({11})


class TestItem12Card(Copy):

    def test_a_placeholder_in_the_read_order_does_not_hold(self):
        write(self.p, "HANDOFF.md", HANDOFF + "\n## Orientation\n{{ORIENTATION}}\n")
        commit(self.p, "placeholder")
        data = self.assert_breaks({12})
        self.assertIn("warmup", self.item(data, 12)["fix"])

    def test_check_card_calls_warmup_in_process_without_recursing(self):
        """O-09 (31/F-01): check_card now calls bin/warmup's main(argv) in
        process instead of as a subprocess. main() computes conformance_state()
        (which re-enters bin/conformance's measure(), item 12 included) only
        when args.check is false -- and check_card always passes --check, so
        the nested warmup can never reach conformance_state(). Proven here by
        making conformance_state raise if it is ever called from inside
        check_card's own call, rather than trusting the argument alone."""
        mod = load_module()
        ctx = mod.Context(self.p)

        def _boom(project):
            raise AssertionError("check_card's nested warmup --check called "
                                 "conformance_state() -- this recurses")

        with mock.patch.object(mod.W, "conformance_state", side_effect=_boom):
            result = mod.check_card(ctx)
        self.assertEqual(result.state, HOLDS, result)


class TestRunInprocessCrash(unittest.TestCase):
    """O-09 (31/F-01): run_inprocess() replaced a subprocess launch. A
    crashed subprocess produced a non-zero returncode and a traceback on
    stderr, and the caller (check 7 or 12) just reported "does not hold" --
    it never took the other eleven checks down with it. run_inprocess() must
    keep that shape for any exception fn(argv) raises, not just SystemExit."""

    def test_a_crashing_check_reports_failure_instead_of_propagating(self):
        mod = load_module()

        def _crashes(argv):
            raise KeyError("malformed-ledger")

        r = mod.run_inprocess(_crashes, ["--project", "/nonexistent"])
        self.assertIsInstance(r, subprocess.CompletedProcess)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("KeyError", r.stderr)
        self.assertIn("malformed-ledger", r.stderr)

    def test_a_crashing_item_12_leaves_the_other_eleven_reporting(self):
        mod = load_module()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p = Path(tmp.name) / "empty"
        build_empty(p)

        def _crashes(argv):
            raise KeyError("boom")

        with mock.patch.object(mod.W, "main", side_effect=_crashes):
            data = mod.measure(p)
        self.assertEqual(len(data["items"]), 12)
        card = next(i for i in data["items"] if i["n"] == 12)
        self.assertEqual(card["state"], NOT)
        # The other eleven checks still ran and reported -- none is missing
        # or itself marked as "the check itself failed" by measure()'s own
        # blanket handler, which would mean the crash propagated past
        # run_inprocess and had to be caught one level up instead.
        for i in data["items"]:
            if i["n"] != 12:
                self.assertNotIn("the check itself failed", i["why"], i)


class TestEscaping(Copy):

    def test_a_forged_line_in_a_ledger_id_stays_on_one_line(self):
        forged = "B-09\nstandard: 12 of 12 hold‮"
        edit_ledger(self.p, lambda d: d["items"].append(
            {"id": forged, "phase": "B", "cx": "C2", "title": "x", "status": "blocked", "log": []}))
        r = conformance(self.p)
        lines = r.stdout.splitlines()
        self.assertEqual(len(lines), 13, r.stdout)
        self.assertEqual(sum(1 for l in lines if l.startswith("standard:")), 1)
        self.assertIn("B-09\\nstandard", r.stdout)
        self.assertNotIn("‮", r.stdout)
        data, _ = report(self.p)
        self.assertNotIn("‮", json.dumps(data, ensure_ascii=False))


class TestExitCode(unittest.TestCase):

    def test_waiting_alone_is_exit_0_and_any_does_not_hold_is_1(self):
        mod = load_module()
        items = [{"n": n, "name": "x", "state": HOLDS, "why": "", "fix": ""} for n in range(1, 13)]
        self.assertEqual(mod.exit_code({"items": items}), 0)
        items[4]["state"] = WAITING
        self.assertEqual(mod.exit_code({"items": items}), 0)
        items[6]["state"] = NOT
        self.assertEqual(mod.exit_code({"items": items}), 1)

    def test_it_is_executable(self):
        self.assertTrue(os.access(CONFORMANCE, os.X_OK))


if __name__ == "__main__":
    unittest.main()
