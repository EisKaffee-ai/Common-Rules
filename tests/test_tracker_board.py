"""`tracker board` renders a project's one tracker page (proposal 22, T-01).

The sponsor asked for "per project, there should be one tracker", readable at
a glance with filters. The tests pin what makes that page trustworthy, not
its look:

  * every item of every ledger appears exactly once, carrying its proposal
    and status, and the page's totals are the sum of each ledger's own counts;
  * rendering twice gives identical bytes;
  * `--check` compares each ledger's digest, so editing, adding or removing a
    ledger makes the page stale -- a checkout resets mtimes, digests it cannot;
  * free text from a ledger is escaped;
  * the filters are built from the ledgers (one chip per proposal and per
    status, with counts), and the page loads no external script;
  * an invalid ledger writes nothing; the per-proposal pages and the
    hand-written proposal pages are never touched.

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TRACKER = ROOT / "bin" / "tracker"
from tools.tracker import board  # noqa: E402


def ledger(number, title, items, asks=(), status="accepted", traceability=()):
    return {
        "proposal": number, "title": title, "status": status, "updated": "2026-09-14",
        "tiers": {"C2": {"tier": "medium", "model": "sonnet", "effort": "medium", "rule": "bounded"},
                  "C4": {"tier": "lead", "model": "lead model", "effort": "-", "rule": "lead"}},
        "phases": [{"id": "W", "name": "Build", "goal": "the goal", "exit": "the exit"}],
        "items": list(items), "traceability": list(traceability), "asks": list(asks),
    }


def item(iid, status, title="an item", cx="C2", **extra):
    tier, model = ("medium", "sonnet") if cx == "C2" else ("lead", "lead model")
    row = {"id": iid, "phase": "W", "cx": cx, "title": title, "status": status,
           "tier": tier, "model": model, "tag": f"[ruflo · {tier} · {model}]", "issue": None,
           "log": [{"at": "2026-09-14T10:00:00+02:00", "event": "started", "by": "lead", "evidence": "e"}]}
    row.update(extra)
    return row


class Project:
    def __init__(self, tmp: Path):
        self.root = tmp
        self.proposals = tmp / "docs" / "proposals"
        self.proposals.mkdir(parents=True)

    def write(self, name, data):
        (self.proposals / name).write_text(json.dumps(data, indent=2) + "\n")

    @property
    def page(self):
        return self.proposals / "tracker" / "index.html"

    def run(self, *args):
        return subprocess.run([sys.executable, str(TRACKER), "board", "--project", str(self.root), *args],
                              capture_output=True, text=True, timeout=60)


def two_ledgers(p: Project):
    p.write("19-warmup.json", ledger(19, "Warm-up", [
        item("W-01", "done"), item("W-02", "in progress", title="render <b>bold</b>"),
        item("W-03", "blocked", cx="C4", owner="sponsor",
             log=[{"at": "2026-09-14T11:00:00+02:00", "event": "blocked", "by": "lead",
                   "evidence": "waits on the sponsor & his go"}]),
    ], asks=[{"id": "A-01", "at": "2026-09-14", "kind": "question", "state": "open",
              "quote": "will it <script>alert(1)</script> work?", "owner": "sponsor"}]))
    p.write("21-standard.json", ledger(21, "The standard", [
        item("S-01", "done"), item("S-02", "not started"), item("S-03", "not started"),
    ]))


class TestBoardPage(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.p = Project(Path(self._tmp.name))
        two_ledgers(self.p)

    def tearDown(self):
        self._tmp.cleanup()

    def test_writes_one_page_for_the_project(self):
        r = self.p.run()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.p.page.is_file())
        self.assertIn("2 done / 1 in progress / 1 blocked / 2 not started", r.stdout)

    def test_goal_contract_is_shown_and_makes_the_page_stale_when_changed(self):
        (self.p.root / ".common-rules.json").write_text(json.dumps({
            "goal": {
                "outcome": "ship the smallest release",
                "constraints": ["preserve behavior"],
                "verification": ["run the gate"],
            }
        }))
        self.assertEqual(0, self.p.run().returncode)
        text = self.p.page.read_text()
        self.assertIn("ship the smallest release", text)
        self.assertIn("preserve behavior", text)
        self.assertEqual("ok", board.project_page_state(self.p.root)[0])
        (self.p.root / ".common-rules.json").write_text(json.dumps({
            "goal": {
                "outcome": "ship a verified release",
                "constraints": ["preserve behavior"],
                "verification": ["run the gate"],
            }
        }))
        self.assertEqual("stale", board.project_page_state(self.p.root)[0])
        (self.p.root / ".common-rules.json").unlink()
        self.assertEqual("stale", board.project_page_state(self.p.root)[0])

    def test_every_item_appears_once_with_its_proposal_and_status(self):
        self.p.run()
        text = self.p.page.read_text()
        cards = re.findall(r'<article class="card"[^>]*>', text)
        found = {}
        for tag in cards:
            iid = re.search(r'data-id="([^"]+)"', tag).group(1)
            prop = re.search(r'data-proposal="([^"]+)"', tag).group(1)
            status = re.search(r'data-status="([^"]+)"', tag).group(1)
            self.assertNotIn(iid, found, f"{iid} appears twice")
            found[iid] = (prop, status)
        self.assertEqual(found, {
            "W-01": ("19", "done"), "W-02": ("19", "in progress"), "W-03": ("19", "blocked"),
            "S-01": ("21", "done"), "S-02": ("21", "not started"), "S-03": ("21", "not started")})

    def test_totals_are_the_sum_of_each_ledgers_counts(self):
        self.p.run()
        text = self.p.page.read_text()
        m = re.search(r'<section class="totals" data-task-total="\d+" data-done="(\d+)" data-in-progress="(\d+)" '
                      r'data-blocked="(\d+)" data-not-started="(\d+)"', text)
        self.assertIsNotNone(m)
        self.assertEqual(tuple(int(x) for x in m.groups()), (2, 1, 1, 2))

    def test_one_summary_block_per_proposal(self):
        self.p.run()
        text = self.p.page.read_text()
        blocks = re.findall(r'<button class="proposal"[^>]*data-proposal="([^"]+)"', text)
        self.assertEqual(blocks, ["19", "21"])

    def test_filters_are_built_from_the_ledgers(self):
        self.p.run()
        text = self.p.page.read_text()
        statuses = dict(re.findall(r'<button class="chip" data-filter="status" data-value="([^"]+)"[^>]*>'
                                   r'.*?<span class="n">(\d+)</span>', text))
        # C-06: two more filter chips, always built (even at zero).
        self.assertEqual(statuses, {"in progress": "1", "in review": "0", "in testing": "0",
                                     "blocked": "1", "not started": "2", "done": "2", "deferred": "0"})
        self.assertRegex(text, r'<input[^>]+type="search"')
        owners = re.findall(r'<option value="([^"]*)"', text)
        self.assertIn("sponsor", owners)

    def test_renders_identically_twice(self):
        self.p.run()
        first = self.p.page.read_bytes()
        self.p.run()
        self.assertEqual(first, self.p.page.read_bytes())

    def test_free_text_is_escaped(self):
        self.p.run()
        text = self.p.page.read_text()
        self.assertNotIn("<b>bold</b>", text)
        self.assertNotIn("<script>alert(1)</script>", text)
        self.assertIn("render &lt;b&gt;bold&lt;/b&gt;", text)

    def test_open_asks_and_blocked_reasons_are_shown(self):
        self.p.run()
        text = self.p.page.read_text()
        self.assertIn('data-ask="A-01"', text)
        self.assertIn("waits on the sponsor &amp; his go", text)

    def test_deferred_is_a_green_terminal_column_with_its_reason(self):
        row = item("D-01", "deferred", title="parked work", log=[{
            "at": "2026-09-20T10:00:00+02:00", "event": "deferred", "by": "lead",
            "evidence": "not part of this release", "status": "deferred"}],
            deferred_reason="not part of this release")
        self.p.write("22-deferred.json", ledger(22, "Deferred", [row]))
        r = self.p.run()
        self.assertEqual(0, r.returncode, r.stderr)
        text = self.p.page.read_text()
        self.assertIn('data-column="deferred"', text)
        self.assertIn("not part of this release", text)
        self.assertIn("s-deferred", text)

    def test_traceability_is_rendered_as_a_contract_map(self):
        row = {
            "id": "TR-01", "item": "W-02", "requirement_ids": ["REQ-01", "REQ-02"],
            "guide_section": "docs/guides/operator.md#commands",
            "architecture_section": "docs/architecture/system.md#boundary",
            "implementation_files": ["src/runner.py", "src/receipt.py"],
            "tests_commands": ["pytest tests/test_runner.py"],
            "receipt_or_refusal": "receipt: run-2026-09-20-01",
            "owner": "lead", "status": "in progress",
        }
        self.p.write("22-traceability.json", ledger(22, "Traceability", [item("W-02", "in progress")],
                                                      traceability=[row]))
        r = self.p.run()
        self.assertEqual(0, r.returncode, r.stderr)
        text = self.p.page.read_text()
        self.assertIn('id="traceability"', text)
        self.assertIn("REQ-01", text)
        self.assertIn("docs/guides/operator.md#commands", text)
        self.assertIn("receipt: run-2026-09-20-01", text)
        self.assertIn('data-traceability="TR-01"', text)

    def test_filtered_blocks_hide_outside_the_artifact_wrapper(self):
        # A card is display:flex, which beats the browser's own [hidden] rule, so a
        # filtered-out block stayed on screen when the file was opened directly.
        self.p.run()
        text = self.p.page.read_text()
        self.assertRegex(text, r"\[hidden\]\s*\{\s*display:\s*none\s*!important\s*\}")

    def test_no_external_script(self):
        self.p.run()
        text = self.p.page.read_text()
        self.assertNotRegex(text, r"<script[^>]+src=")

    def test_check_is_fresh_after_render(self):
        self.p.run()
        r = self.p.run("--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_check_is_stale_when_a_ledger_changes(self):
        self.p.run()
        data = json.loads((self.p.proposals / "21-standard.json").read_text())
        data["items"][1]["status"] = "in progress"
        self.p.write("21-standard.json", data)
        self.assertEqual(self.p.run("--check").returncode, 1)

    def test_check_is_stale_when_a_ledger_is_added_or_removed(self):
        self.p.run()
        self.p.write("22-new.json", ledger(22, "New", [item("T-01", "not started")]))
        self.assertEqual(self.p.run("--check").returncode, 1)
        self.p.run()
        (self.p.proposals / "22-new.json").unlink()
        self.assertEqual(self.p.run("--check").returncode, 1)

    def test_check_is_stale_when_the_page_is_missing(self):
        r = self.p.run("--check")
        self.assertEqual(r.returncode, 1)
        self.assertFalse(self.p.page.exists())

    def test_invalid_ledger_writes_nothing(self):
        bad = ledger(23, "Bad", [item("T-01", "finished")])
        self.p.write("23-bad.json", bad)
        r = self.p.run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("23-bad.json", r.stderr)
        self.assertFalse(self.p.page.exists())

    def test_unreadable_ledger_is_exit_2(self):
        (self.p.proposals / "24-broken.json").write_text("{not json")
        r = self.p.run()
        self.assertEqual(r.returncode, 2)
        self.assertFalse(self.p.page.exists())

    def test_no_ledgers_is_exit_2(self):
        for f in self.p.proposals.glob("*.json"):
            f.unlink()
        r = self.p.run()
        self.assertEqual(r.returncode, 2)
        self.assertFalse(self.p.page.exists())

    def test_other_pages_are_never_touched(self):
        tracker = self.p.proposals / "tracker"
        tracker.mkdir()
        own = tracker / "19-warmup.html"
        own.write_text("per-proposal page")
        hand = self.p.proposals / "19-warmup.html"
        hand.write_text("hand-written proposal")
        self.p.run()
        self.assertEqual(own.read_text(), "per-proposal page")
        self.assertEqual(hand.read_text(), "hand-written proposal")


class TestReviewRoundOne(unittest.TestCase):
    """Findings of the round-1 review of 11d7bbe, each pinned before its fix."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.p = Project(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_fresh_when_proposal_order_differs_from_file_order(self):
        self.p.write("99-a.json", ledger(99, "A", [item("A-01", "done")]))
        self.p.write("100-b.json", ledger(100, "B", [item("B-01", "done")]))
        self.assertEqual(self.p.run().returncode, 0)
        r = self.p.run("--check")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_fresh_when_a_file_number_differs_from_its_proposal(self):
        self.p.write("21-x.json", ledger(30, "X", [item("X-01", "done")]))
        self.p.write("22-y.json", ledger(22, "Y", [item("Y-01", "done")]))
        self.assertEqual(self.p.run().returncode, 0)
        r = self.p.run("--check")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_digest_line_cannot_be_forged_by_a_filename(self):
        import hashlib
        a = ledger(19, "A", [item("A-01", "done")])
        b = ledger(20, "B", [item("B-01", "done")])
        self.p.write("19-a.json", a)
        self.p.write("20-b.json", b)
        self.p.run()
        sha_a = hashlib.sha256((self.p.proposals / "19-a.json").read_bytes()).hexdigest()
        (self.p.proposals / "19-a.json").unlink()
        (self.p.proposals / "20-b.json").unlink()
        self.p.write(f"19-a.json={sha_a};20-b.json", b)
        self.assertEqual(self.p.run("--check").returncode, 1)

    def test_list_rows_appear_once_each(self):
        two_ledgers(self.p)
        self.p.run()
        ids = re.findall(r'<tr class="row"[^>]*data-id="([^"]+)"', self.p.page.read_text())
        self.assertEqual(sorted(ids), ["S-01", "S-02", "S-03", "W-01", "W-02", "W-03"])

    def test_board_and_list_search_the_same_text(self):
        # Round 2: the search string is stored once, on the card; the page's
        # script gives each list row its card's string, so the page is not
        # doubled in size and the two views cannot drift apart.
        two_ledgers(self.p)
        self.p.run()
        text = self.p.page.read_text()
        cards = dict(re.findall(r'<article class="card"[^>]*data-id="([^"]+)"[^>]*data-search="([^"]*)"', text))
        self.assertEqual(len(cards), 6)
        self.assertNotRegex(text, r'<tr class="row"[^>]*data-search=')
        self.assertIn("rows.forEach", text)
        self.assertIn("waits on the sponsor", cards["W-03"])
        self.assertIn("blocked", cards["W-03"])

    def test_every_ledger_string_is_escaped(self):
        self.p.write("19-x.json", ledger(19, "title <pt>", [
            item("W-01", "blocked", title="t", cx="C4", owner='session:a"b<ow>', tag="[ruflo · lead · <tg>]",
                 log=[{"at": "2026-09-14T11:00:00+02:00", "event": "<evt>", "by": "<by>", "evidence": "<ev>"}]),
        ]))
        r = self.p.run()
        self.assertEqual(r.returncode, 0, r.stderr)
        text = self.p.page.read_text()
        for raw in ("<pt>", "<ow>", "<tg>", "<evt>", "<by>", "<ev>", 'a"b'):
            self.assertNotIn(raw, text)
        self.assertIn('data-owner="session:a&quot;b&lt;ow&gt;"', text)

    def test_blocked_reason_has_its_own_paragraph(self):
        two_ledgers(self.p)
        self.p.run()
        self.assertIn('<p class="why">waits on the sponsor &amp; his go</p>', self.p.page.read_text())

    def test_one_column_per_status_with_its_count(self):
        two_ledgers(self.p)
        self.p.run()
        cols = re.findall(r'<section class="col [^"]*" data-column="([^"]+)"><h2>.*?<span class="n">(\d+)</span>',
                          self.p.page.read_text())
        # C-06: two more columns, always shown (even at zero), between
        # "in progress" and "blocked".
        self.assertEqual(cols, [("in progress", "1"), ("in review", "0"), ("in testing", "0"),
                                 ("blocked", "1"), ("not started", "2"), ("done", "2"), ("deferred", "0")])

    def test_page_declares_doctype_and_charset(self):
        two_ledgers(self.p)
        self.p.run()
        head = self.p.page.read_text()[:400]
        self.assertTrue(head.startswith("<!doctype html>"), head[:40])
        self.assertIn('<meta charset="utf-8">', head)

    def test_asks_carry_owner_and_search_text(self):
        two_ledgers(self.p)
        self.p.run()
        m = re.search(r'<li class="ask" data-ask="A-01"[^>]*>', self.p.page.read_text())
        self.assertIsNotNone(m)
        self.assertIn('data-owner="sponsor"', m.group(0))
        self.assertIn('data-search="', m.group(0))


class TestReviewRoundTwo(unittest.TestCase):
    """The final round's remaining findings on 1e3afa9, fixed by the lead."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.p = Project(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_inline_free_text_is_bidi_isolated(self):
        self.p.write("19-x.json", ledger(19, "X", [
            item("W-01", "in progress", log=[{"at": "2026-09-14T10:00:00+02:00", "event": "‮evt",
                                              "by": "lead", "evidence": "e"}])]))
        r = self.p.run("--name", "‮name")
        self.assertEqual(r.returncode, 0, r.stderr)
        text = self.p.page.read_text()
        self.assertIn("<bdi>‮evt</bdi>", text)
        self.assertIn("<bdi>‮name</bdi>", text)

    def test_search_text_is_lowercase_and_carries_the_status(self):
        self.p.write("19-x.json", ledger(19, "X", [item("W-01", "in progress", title="Render The PAGE")]))
        self.p.run()
        m = re.search(r'<article class="card"[^>]*data-id="W-01"[^>]*data-search="([^"]*)"', self.p.page.read_text())
        self.assertIsNotNone(m)
        self.assertIn("w-01", m.group(1))
        self.assertIn("in progress", m.group(1))
        self.assertIn("render the page", m.group(1))
        self.assertEqual(m.group(1), m.group(1).lower())

    def test_requests_are_escaped_and_unblocks_is_a_list(self):
        data = ledger(19, "X", [item("W-01", "not started")])
        data["requests"] = [{"id": "RQ-01", "from": "session:<rf>", "to": "lead", "state": "open",
                             "unblocks": ["W-01"]}]
        self.p.write("19-x.json", data)
        r = self.p.run()
        self.assertEqual(r.returncode, 0, r.stderr)
        text = self.p.page.read_text()
        self.assertNotIn("<rf>", text)
        self.assertIn("unblocks W-01", text)
        self.assertIn('data-request="RQ-01"', text)

    def test_a_log_entry_that_is_not_an_object_does_not_crash(self):
        """Proposal 22, T-02 closed the hole in ledger.validate: a string log
        entry is now a named problem, so the command refuses cleanly and
        writes nothing. The renderer itself still skips one, rather than
        crash, for a caller that renders without validating."""
        from tools.tracker import board
        data = ledger(19, "X", [item("W-01", "done", log=["just a string"])])
        self.p.write("19-x.json", data)
        r = self.p.run()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("W-01: log[0] is not an object", r.stderr)
        self.assertFalse(self.p.page.exists())
        text = board.render([(self.p.proposals / "19-x.json", data)], "demo", None)
        self.assertIn('data-id="W-01"', text)

    def test_the_asks_headers_follow_the_filters(self):
        self.p.write("19-x.json", ledger(19, "X", [item("W-01", "done")], asks=[
            {"id": "A-01", "at": "2026-09-14", "kind": "question", "state": "open", "quote": "open one"},
            {"id": "A-02", "at": "2026-09-14", "kind": "decision", "state": "answered", "quote": "answered one"}]))
        self.p.run()
        text = self.p.page.read_text()
        self.assertIn('id="attention"', text)
        self.assertIn('id="answered-n"', text)


class TestProjectPageState(unittest.TestCase):
    """T-02: warmup, conformance and new-proposal ask one helper whether the
    project page is fresh, so none of them re-derives which ledgers it reads."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.p = Project(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_ok_stale_and_no_ledgers(self):
        from tools.tracker import board
        self.assertEqual(("none", self.p.page), board.project_page_state(self.p.root))
        two_ledgers(self.p)
        self.assertEqual(("missing", self.p.page), board.project_page_state(self.p.root))
        self.assertEqual(0, self.p.run().returncode)
        self.assertEqual(("ok", self.p.page), board.project_page_state(self.p.root))
        # A data file shaped NN-*.json is not a ledger, and does not make the page stale.
        (self.p.proposals / "56-sheet.sidecar.json").write_text('{"rows": []}')
        self.assertEqual("ok", board.project_page_state(self.p.root)[0])
        self.p.write("30-new.json", ledger(30, "New", [item("N-01", "not started")]))
        self.assertEqual("stale", board.project_page_state(self.p.root)[0])


class TestTheSidecarHelpers(unittest.TestCase):
    """T-03: `tracker published --project` and bin/warmup ask board.py where
    the project page's publish record lives, and what ledger digests the page
    itself carries -- neither re-derives the path or re-reads the markup."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.p = Project(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_the_sidecar_sits_beside_the_page(self):
        from tools.tracker import board
        self.assertEqual(self.p.proposals / "tracker" / "index.published.json",
                         board.published_path(self.p.root))

    def test_page_digests_is_the_pages_own_meta(self):
        from tools.tracker import board
        two_ledgers(self.p)
        self.assertEqual(0, self.p.run().returncode)
        paths = board.ledger_paths(self.p.root)
        self.assertEqual(board.digests(paths), board.page_digests(self.p.page))
        for name in ("19-warmup.json", "21-standard.json"):
            self.assertIn(name, board.page_digests(self.p.page))

    def test_goal_digest_is_carried_when_declared(self):
        from tools.tracker import board
        two_ledgers(self.p)
        (self.p.root / ".common-rules.json").write_text(json.dumps({
            "goal": {"outcome": "ship", "constraints": ["safe"], "verification": ["test"]}
        }))
        self.assertEqual(0, self.p.run().returncode)
        text = self.p.page.read_text()
        self.assertIn('meta name="goal-digest"', text)
        self.assertEqual("ok", board.freshness(board.ledger_paths(self.p.root), self.p.page, self.p.root))

    def test_a_page_without_the_meta_or_no_page_at_all_reads_none(self):
        from tools.tracker import board
        self.assertIsNone(board.page_digests(self.p.page))
        self.p.page.parent.mkdir(parents=True, exist_ok=True)
        self.p.page.write_text("<p>not the generated page</p>\n")
        self.assertIsNone(board.page_digests(self.p.page))


if __name__ == "__main__":
    unittest.main()
