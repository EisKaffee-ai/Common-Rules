"""`bin/new-proposal` -- every project creates proposals the same way (proposal 21, S-02).

The sponsor made the common-rules standard mandatory (proposal 21, A-01 and
A-02). The PhotoVault app's and engine's newest proposals had none of the
checked shape, and nothing existed to create one from. `new-proposal` writes
the page from templates/proposal.html and its ledger from
templates/ledger.json, then runs the two checkers on what it wrote. These
tests hold it to:

  * the next free number across every docs/proposals/NN-* entry, or an
    explicit --number that no entry already uses;
  * a slug made from the title, and a title that is empty, multi-line or
    carries control characters refused;
  * both files written, or neither -- including when a checker rejects the
    result after writing;
  * proposalcheck and tracker validate clean on the result, unedited;
  * never overwriting anything;
  * every template placeholder replaced, and the title escaped for HTML.

And, because a template can quietly defeat the checks it is meant to pass:
a page from the template that is flipped to accepted (or completed in part)
without recording the answers (or the exceptions) is still a violation.

Every test runs in a scratch git repository under a temp dir.

Run:  python3 -m unittest discover -s tests -p 'test_new_proposal.py' -v
"""
from __future__ import annotations

import contextlib
import datetime
import html
import importlib.machinery
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEW_PROPOSAL = ROOT / "bin" / "new-proposal"
PROPOSALCHECK = ROOT / "bin" / "proposalcheck"
TRACKER = ROOT / "bin" / "tracker"
TEMPLATE = ROOT / "templates" / "proposal.html"


def today_dates() -> set[str]:
    """The real clock's date, and tomorrow's in case a run crosses midnight."""
    now = datetime.date.today()
    return {now.isoformat(), (now + datetime.timedelta(days=1)).isoformat()}


class Scratch(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve() / "project"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.proposals = self.root / "docs" / "proposals"

    def tearDown(self):
        self._tmp.cleanup()

    def run_new(self, *args, project: Path | None = None, cwd: Path | None = None):
        argv = [sys.executable, str(NEW_PROPOSAL)]
        if project is not False:
            argv += ["--project", str(project or self.root)]
        return subprocess.run(argv + list(args), capture_output=True, text=True,
                              check=False, cwd=str(cwd or self.root))

    def seed(self, name: str, text: str = "") -> Path:
        self.proposals.mkdir(parents=True, exist_ok=True)
        p = self.proposals / name
        p.write_text(text)
        return p

    def listing(self) -> list[str]:
        return sorted(p.name for p in self.proposals.iterdir()) if self.proposals.exists() else []

    def assert_ok(self, r):
        self.assertEqual(r.returncode, 0, f"exit {r.returncode}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}")


class TestNumbering(Scratch):
    def test_first_proposal_in_an_empty_project_is_01(self):
        r = self.run_new("Warm-up for everyone")
        self.assert_ok(r)
        self.assertEqual(self.listing(), ["01-warm-up-for-everyone.html", "01-warm-up-for-everyone.json", "tracker"])

    def test_next_number_is_one_above_every_numbered_entry(self):
        self.seed("03-proposal-a.html")
        self.seed("12-data.sidecar.json", "{}")      # not a ledger, still a number in use
        self.seed("07-b.json", "{}")
        (self.proposals / "09-assets").mkdir()         # a directory holds its number too
        self.seed("README.md")
        r = self.run_new("Next one")
        self.assert_ok(r)
        self.assertTrue((self.proposals / "13-next-one.html").is_file(), self.listing())
        self.assertTrue((self.proposals / "13-next-one.json").is_file(), self.listing())

    def test_explicit_number_is_used_and_zero_padded(self):
        self.seed("03-proposal-a.html")
        r = self.run_new("--number", "5", "Explicit")
        self.assert_ok(r)
        self.assertIn("05-explicit.html", self.listing())
        self.assertIn("05-explicit.json", self.listing())
        page = (self.proposals / "05-explicit.html").read_text()
        self.assertIn('<meta name="proposal-id" content="05">', page)
        self.assertEqual(json.loads((self.proposals / "05-explicit.json").read_text())["proposal"], 5)

    def test_explicit_number_three_digits(self):
        r = self.run_new("--number", "120", "Big")
        self.assert_ok(r)
        self.assertIn("120-big.html", self.listing())

    def test_explicit_number_already_used_is_refused_naming_the_file(self):
        self.seed("05-something-else.json", '{"keep": true}')
        before = self.listing()
        for spelled in ("5", "05", "005"):
            with self.subTest(number=spelled):
                r = self.run_new("--number", spelled, "Collides")
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("05-something-else.json", r.stdout + r.stderr)
                self.assertEqual(self.listing(), before)
        self.assertEqual((self.proposals / "05-something-else.json").read_text(), '{"keep": true}')

    def test_bad_numbers_are_refused(self):
        for bad in ("0", "-3", "abc", "4.5", ""):
            with self.subTest(number=bad):
                r = self.run_new("--number", bad, "Fine title")
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("--number", r.stderr)
                self.assertEqual(self.listing(), [])


class TestTitles(Scratch):
    def test_bidi_and_invisible_characters_are_refused(self):
        """S-02 final review: a U+202E title was written."""
        for bad in ("safe\u202eevil", "zero\u200bwidth", "sep\u2028arated"):
            with self.subTest(title=ascii(bad)):
                r = self.run_new(bad)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertEqual(self.listing(), [])

    def test_slug_is_lowercase_ascii_hyphens(self):
        cases = {
            "The Standard: Is Mandatory!": "the-standard-is-mandatory",
            "Café résumé, déjà vu": "cafe-resume-deja-vu",
            "  spaced   out  ": "spaced-out",
            "v2.0 -- the_sequel": "v2-0-the-sequel",
        }
        for n, (title, slug) in enumerate(cases.items(), start=1):
            with self.subTest(title=title):
                r = self.run_new("--number", str(n), title)
                self.assert_ok(r)
                self.assertIn(f"{n:02d}-{slug}.html", self.listing())

    def test_bad_titles_are_refused_and_write_nothing(self):
        bad = {
            "empty": "",
            "whitespace only": "   ",
            "multi-line": "first line\nsecond line",
            "carriage return": "title\rinjected",
            "tab": "a\tb",
            "escape sequence": "red \x1b[31mtitle",
            "C1 control": "a\x85b",
            "unicode line separator": "a\u2028b",
            "unicode paragraph separator": "a\u2029b",
            "no ascii to slug": "日本語",
        }
        for label, title in bad.items():
            with self.subTest(label):
                r = self.run_new(title)
                self.assertEqual(r.returncode, 1, f"{label}: {r.stdout}{r.stderr}")
                self.assertIn("title", (r.stdout + r.stderr).lower())
                self.assertEqual(self.listing(), [], label)
                # Nothing at all created, not even the directory.
                self.assertFalse((self.root / "docs").exists(), label)


class TestWritten(Scratch):
    def make(self, title="The standard is mandatory", *extra):
        r = self.run_new(*extra, title)
        self.assert_ok(r)
        html = next(self.proposals.glob("*.html"))
        ledger = next(self.proposals.glob("*.json"))
        return r, html, ledger

    def test_both_files_written_and_both_paths_printed_with_next_step(self):
        r, html, ledger = self.make()
        self.assertEqual(html.name, "01-the-standard-is-mandatory.html")
        self.assertEqual(ledger.name, "01-the-standard-is-mandatory.json")
        self.assertIn(str(html), r.stdout)
        self.assertIn(str(ledger), r.stdout)
        self.assertIn("fill the page", r.stdout.lower())
        self.assertIn("items", r.stdout.lower())

    def test_proposalcheck_and_tracker_validate_clean_on_the_result(self):
        _, _, ledger = self.make()
        pc = subprocess.run([sys.executable, str(PROPOSALCHECK), "--project", str(self.root)],
                            capture_output=True, text=True, check=False)
        self.assertEqual(pc.returncode, 0, pc.stdout + pc.stderr)
        self.assertIn("1 asked decisions", pc.stdout)
        tv = subprocess.run([sys.executable, str(TRACKER), "validate", str(ledger)],
                            capture_output=True, text=True, check=False)
        self.assertEqual(tv.returncode, 0, tv.stdout + tv.stderr)
        self.assertIn("well-formed", tv.stdout)

    def test_page_carries_the_checked_shape(self):
        _, html, _ = self.make()
        page = html.read_text()
        self.assertIn('<meta name="proposal-status" content="proposed">', page)
        self.assertIn('<meta name="proposal-id" content="01">', page)
        self.assertIn('<meta name="common-rules-template" content="proposal/21">', page)
        self.assertRegex(page, r'<ol class="decisions">\s*<li')
        self.assertIn("<title>01 · proposed · The standard is mandatory</title>", page)
        self.assertIsNone(re.search(r'<meta name="proposal-part-of"', page))
        self.assertIsNone(re.search(r'<meta name="proposal-decided"', page))
        self.assertTrue(any(d in page for d in today_dates()), "page carries today's date")

    def test_page_carries_visual_decision_primitives(self):
        _, html, _ = self.make()
        page = html.read_text()
        self.assertIn('class="verdict"', page)
        self.assertIn('class="big"', page)
        self.assertIn('class="stat"', page)
        self.assertIn('class="tk"', page)
        self.assertLess(page.index('class="tk"'), page.index('<h2>Decisions</h2>'))

    def test_ledger_is_the_minimal_contract(self):
        _, _, ledger = self.make()
        data = json.loads(ledger.read_text())
        self.assertEqual(data["proposal"], 1)
        self.assertEqual(data["title"], "The standard is mandatory")
        self.assertEqual(data["status"], "proposed")
        self.assertIn(data["updated"], today_dates())
        self.assertEqual(data["items"], [])
        self.assertIn("tiers", data)

    def test_every_placeholder_replaced_in_both_files(self):
        _, html, ledger = self.make()
        self.assertNotRegex(html.read_text(), r"\{\{")
        self.assertNotRegex(ledger.read_text(), r"\{\{")

    def test_template_placeholders_are_exactly_the_three(self):
        found = set(re.findall(r"\{\{(.*?)\}\}", TEMPLATE.read_text()))
        self.assertEqual(found, {"NUMBER", "TITLE", "DATE"})

    def test_title_is_escaped_in_html_and_not_reexpanded(self):
        title = 'Tags <b>&amp; "quotes" {{DATE}}'
        r = self.run_new(title)
        self.assert_ok(r)
        html = next(self.proposals.glob("*.html")).read_text()
        self.assertNotIn(title, html)
        self.assertIn("Tags &lt;b&gt;&amp;amp; &quot;quotes&quot; {{DATE}}", html)
        data = json.loads(next(self.proposals.glob("*.json")).read_text())
        self.assertEqual(data["title"], title)

    def test_template_meta_is_in_the_template_itself(self):
        self.assertIn('<meta name="common-rules-template" content="proposal/21">', TEMPLATE.read_text())

    def test_new_proposal_is_executable(self):
        self.assertTrue(os.access(NEW_PROPOSAL, os.X_OK))


class TestNoOverwrite(Scratch):
    def test_same_title_twice_takes_the_next_number(self):
        self.assert_ok(self.run_new("Same"))
        first = (self.proposals / "01-same.html").read_text()
        self.assert_ok(self.run_new("Same"))
        self.assertEqual(self.listing(), ["01-same.html", "01-same.json", "02-same.html", "02-same.json", "tracker"])
        self.assertEqual((self.proposals / "01-same.html").read_text(), first)

    def test_existing_page_is_never_overwritten(self):
        self.assert_ok(self.run_new("Same"))
        page = self.proposals / "01-same.html"
        page.write_text("hand edited")
        r = self.run_new("--number", "1", "Same")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(page.read_text(), "hand edited")


class TestAllOrNothing(Scratch):
    def test_a_checker_rejecting_the_result_leaves_nothing_behind(self):
        # A document with no NN- filename that already claims proposal-id 01:
        # the number looks free by filename, but proposalcheck reports a
        # collision once the new page exists.
        self.seed("draft.html",
                  '<meta name="proposal-id" content="01">\n'
                  '<meta name="proposal-status" content="proposed">\n<h1>draft</h1>')
        r = self.run_new("Collides by id")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("proposalcheck", r.stdout + r.stderr)
        self.assertEqual(self.listing(), ["draft.html"])

    def test_a_violation_elsewhere_does_not_block(self):
        # A pre-existing lead with a typo'd status, dated after the floor: a
        # violation that is not new-proposal's to fix or to be blocked by.
        self.seed("02-old.html",
                  '<meta name="proposal-id" content="02">\n'
                  '<meta name="proposal-status" content="superseded-by 1">\n'
                  '<meta name="proposal-decided" content="2026-09-01">\n<h1>old</h1>')
        r = self.run_new("Unrelated")
        self.assert_ok(r)
        self.assertIn("03-unrelated.html", self.listing())


class TestProject(Scratch):
    def test_project_is_the_git_top_of_dir(self):
        sub = self.root / "src" / "deep"
        sub.mkdir(parents=True)
        r = self.run_new("From below", project=sub)
        self.assert_ok(r)
        self.assertTrue((self.root / "docs" / "proposals" / "01-from-below.html").is_file())
        self.assertFalse((sub / "docs").exists())

    def test_default_project_is_cwd(self):
        sub = self.root / "src"
        sub.mkdir()
        r = self.run_new("From cwd", project=False, cwd=sub)
        self.assert_ok(r)
        self.assertTrue((self.root / "docs" / "proposals" / "01-from-cwd.html").is_file())

    def test_not_a_git_repository_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.run_new("Nowhere", project=Path(tmp))
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("not inside a git repository", r.stderr)
            self.assertEqual(list(Path(tmp).iterdir()), [])


class TestTemplateDoesNotDefeatTheChecks(Scratch):
    """The page must not pre-satisfy the rules it exists to meet: an answers
    block or an exceptions block baked into the template would let every
    future proposal reach accepted with nothing recorded."""

    def flip(self, status: str, decided: str | None = "2026-09-14") -> subprocess.CompletedProcess:
        self.assert_ok(self.run_new("Flip me"))
        page = self.proposals / "01-flip-me.html"
        lines = f'<meta name="proposal-status" content="{status}">'
        if decided:
            lines += f'\n<meta name="proposal-decided" content="{decided}">'
        page.write_text(page.read_text().replace(
            '<meta name="proposal-status" content="proposed">', lines))
        return proposalcheck(self.root)

    def test_accepted_without_answers_is_a_violation(self):
        r = self.flip("accepted")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("records no answers", r.stdout)

    def test_completed_in_part_without_exceptions_is_a_violation(self):
        r = self.flip("completed in part")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("exceptions", r.stdout)

    # S-03 owns this fix, in bin/proposalcheck: a decision status with no
    # proposal-decided date, on a page carrying the common-rules-template
    # meta, is a violation. Today an undated page is grandfathered, so this
    # fails. When S-03 merges it passes, unittest reports an unexpected
    # success (FAILED), and this marker must come off.
    def test_accepted_without_a_decided_date_is_a_violation(self):
        r = self.flip("accepted", decided=None)
        self.assertEqual(r.returncode, 1, r.stdout)


def proposalcheck(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(PROPOSALCHECK), "--project", str(root)],
                          capture_output=True, text=True, check=False)


def decided_slot(page: str) -> str:
    """The Decided section, as a reader sees it (entities decoded)."""
    start = page.index("<h2>Decided</h2>")
    return html.unescape(page[start:page.index("</section>", start)])


class TestDecidedInstructions(Scratch):
    DATE_LINE = '<meta name="proposal-decided" content="YYYY-MM-DD">'
    STATUS_LINE = '<meta name="proposal-status" content="accepted">'

    def page(self) -> str:
        self.assert_ok(self.run_new("Instructions"))
        return (self.proposals / "01-instructions.html").read_text()

    def test_both_meta_lines_are_shown_literally_date_first(self):
        slot = decided_slot(self.page())
        self.assertIn(self.DATE_LINE, slot)
        self.assertIn(self.STATUS_LINE, slot)
        self.assertLess(slot.index(self.DATE_LINE), slot.index(self.STATUS_LINE))
        self.assertIn("self-clos", slot.lower())

    def test_the_shown_lines_copied_in_are_read_by_proposalcheck(self):
        text = self.page()
        slot = decided_slot(text)
        date = slot[slot.index(self.DATE_LINE):slot.index(self.DATE_LINE) + len(self.DATE_LINE)]
        status = slot[slot.index(self.STATUS_LINE):slot.index(self.STATUS_LINE) + len(self.STATUS_LINE)]
        copied = date.replace("YYYY-MM-DD", "2026-09-14") + "\n" + status
        (self.proposals / "01-instructions.html").write_text(
            text.replace('<meta name="proposal-status" content="proposed">', copied))
        r = proposalcheck(self.root)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn('"accepted", but records no answers', r.stdout)

    def test_the_raw_page_carries_neither_line_and_one_decisions_list(self):
        text = self.page()
        self.assertNotIn(self.DATE_LINE, text)
        self.assertNotIn(self.STATUS_LINE, text)
        self.assertEqual(text.count('<ol class="decisions">'), 1)

    def test_status_comment_names_every_place_the_status_appears(self):
        tpl = TEMPLATE.read_text()
        comment = tpl[tpl.index("<!--"):tpl.index("-->")]
        for place in ("proposal-status meta", "<title>", "<h1>", "Proposal NN · proposed DATE"):
            self.assertIn(place, comment)

    def test_exceptions_note_names_the_decisions_list(self):
        self.assertRegex(decided_slot(self.page()), r'exceptions[^.]*<ol class="decisions">')


class TestWhatCountsAsANumber(Scratch):
    def test_a_date_prefixed_file_is_not_a_proposal_number(self):
        self.seed("2026-09-14-notes.md")
        self.seed("05-x.html")
        self.assert_ok(self.run_new("After notes"))
        self.assertIn("06-after-notes.html", self.listing())

    def test_a_date_prefixed_file_alone_leaves_01(self):
        self.seed("2026-09-14-notes.md")
        self.assert_ok(self.run_new("First"))
        self.assertIn("01-first.html", self.listing())

    def test_lettered_numbers_count(self):
        self.seed("02a-first.html")
        self.seed("02b-second.html")
        self.assert_ok(self.run_new("Third"))
        self.assertIn("03-third.html", self.listing())

    def test_a_lettered_number_collides(self):
        self.seed("02a-first.html")
        self.seed("02b-second.html")
        r = self.run_new("--number", "2", "Clash")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("02a-first.html", r.stderr)
        self.assertIn("02b-second.html", r.stderr)

    def test_a_number_above_three_digits_is_refused(self):
        r = self.run_new("--number", "1000", "Too big")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("--number", r.stderr)
        self.assertEqual(self.listing(), [])


class ProjectPage(Scratch):
    @property
    def index(self) -> Path:
        return self.proposals / "tracker" / "index.html"

    def board_check(self):
        return subprocess.run([sys.executable, str(TRACKER), "board", "--project", str(self.root), "--check"],
                              capture_output=True, text=True, check=False)

    def tracker_listing(self) -> list[str]:
        folder = self.proposals / "tracker"
        return sorted(p.name for p in folder.iterdir()) if folder.exists() else []


class TestTrackerPage(ProjectPage):
    """Proposal 22, T-02: a new proposal renders the project's one tracker
    page, docs/proposals/tracker/index.html, not a page of its own."""

    def test_the_project_page_is_rendered_fresh_and_named(self):
        r = self.run_new("Rendered")
        self.assert_ok(r)
        self.assertTrue(self.index.is_file())
        self.assertIn(str(self.index), r.stdout)
        self.assertIn("tracker board", r.stdout)
        self.assertEqual(self.tracker_listing(), ["index.html"])
        chk = self.board_check()
        self.assertEqual(chk.returncode, 0, chk.stdout + chk.stderr)

    def test_an_existing_project_page_is_regenerated_to_carry_every_ledger(self):
        self.assert_ok(self.run_new("First"))
        self.index.write_text("an out-of-date page\n")
        self.assert_ok(self.run_new("Second"))
        text = self.index.read_text()
        self.assertIn("First", text)
        self.assertIn("Second", text)
        self.assertEqual(self.board_check().returncode, 0)

    def test_an_old_per_ledger_page_is_left_alone(self):
        existing = self.proposals / "tracker" / "01-rendered.html"
        existing.parent.mkdir(parents=True)
        existing.write_text("keep")
        r = self.run_new("Rendered")
        self.assert_ok(r)
        self.assertEqual(existing.read_text(), "keep")
        self.assertEqual(self.tracker_listing(), ["01-rendered.html", "index.html"])

    def test_a_rejected_result_removes_the_tracker_page_too(self):
        self.seed("draft.html", '<meta name="proposal-id" content="01">\n'
                                '<meta name="proposal-status" content="proposed">\n')
        r = self.run_new("Collides by id")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertFalse((self.proposals / "tracker").exists())

    def test_a_rejected_result_restores_the_project_page_byte_for_byte(self):
        self.assert_ok(self.run_new("First"))
        before = "the page as it was • not regenerated\n".encode("utf-8") + b"\r\n"
        self.index.write_bytes(before)
        self.seed("draft.html", '<meta name="proposal-id" content="02">\n'
                                '<meta name="proposal-status" content="proposed">\n')
        r = self.run_new("Collides by id")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(self.index.read_bytes(), before)
        self.assertEqual(self.listing(), ["01-first.html", "01-first.json", "draft.html", "tracker"])
        self.assertEqual(self.tracker_listing(), ["index.html"])

    def test_an_invalid_ledger_elsewhere_refuses_and_restores(self):
        """The project page reads every ledger, and refuses to show numbers from
        a broken one; the new proposal is then refused as a unit."""
        self.assert_ok(self.run_new("First"))
        before = self.index.read_bytes()
        first = self.proposals / "01-first.json"
        data = json.loads(first.read_text())
        data["items"] = [{"id": "not-an-id", "status": "wip"}]
        first.write_text(json.dumps(data))
        r = self.run_new("Second")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("tracker board", r.stderr)
        self.assertIn("01-first.json", r.stderr)
        self.assertEqual(self.index.read_bytes(), before)
        self.assertEqual(self.listing(), ["01-first.html", "01-first.json", "tracker"])

    def test_a_symlinked_project_page_is_refused_and_nothing_written(self):
        outside = Path(self._tmp.name) / "elsewhere.html"
        outside.write_text("outside the project")
        self.index.parent.mkdir(parents=True)
        self.index.symlink_to(outside)
        r = self.run_new("Linked")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("index.html", r.stderr)
        self.assertEqual(outside.read_text(), "outside the project")
        self.assertEqual(self.listing(), ["tracker"])
        self.assertTrue(self.index.is_symlink())


class TestOnlyTheNewPageIsMatched(Scratch):
    def test_violations_in_longer_names_are_not_ours(self):
        # 01-foo.html is a substring of every name below.
        self.seed("101-foo.html", '<meta name="proposal-id" content="101">\n'
                                  '<meta name="proposal-status" content="superseded-by 1">\n'
                                  '<meta name="proposal-decided" content="2026-09-01">\n')
        for name in ("201-foo.html", "301-foo.html"):
            self.seed(name, '<meta name="proposal-id" content="77">\n'
                            '<meta name="proposal-status" content="proposed">\n')
        r = self.run_new("--number", "1", "Foo")
        self.assert_ok(r)
        self.assertIn("01-foo.html", self.listing())


def load_tool():
    """bin/new-proposal as a module, so a test can simulate a race or a crash."""
    loader = importlib.machinery.SourceFileLoader("new_proposal_under_test", str(NEW_PROPOSAL))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class InProcess(Scratch):
    def call(self, tool, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = tool.main(["--project", str(self.root), *argv])
        return rc, out.getvalue(), err.getvalue()


class TestRace(InProcess):
    """Another session claims the number between the scan and the write."""

    def blind_first_scan(self, tool):
        real, calls = tool.numbers_in_use, []

        def blind(*a, **k):
            calls.append(1)
            return {} if len(calls) == 1 else real(*a, **k)
        tool.numbers_in_use = blind

    def test_the_same_file_claimed_meanwhile(self):
        self.seed("01-same.html", "theirs")
        tool = load_tool()
        self.blind_first_scan(tool)
        rc, out, err = self.call(tool, "Same")
        self.assertEqual(rc, 1, out + err)
        self.assertIn("just claimed", err)
        self.assertIn("run it again", err)
        self.assertEqual((self.proposals / "01-same.html").read_text(), "theirs")
        self.assertEqual(self.listing(), ["01-same.html"])

    def test_the_same_number_claimed_meanwhile_under_another_name(self):
        self.seed("01-other.html", "theirs")
        tool = load_tool()
        self.blind_first_scan(tool)
        rc, out, err = self.call(tool, "Same")
        self.assertEqual(rc, 1, out + err)
        self.assertIn("just claimed", err)
        self.assertIn("run it again", err)
        self.assertEqual(self.listing(), ["01-other.html"])


class TestCouldNotRun(InProcess):
    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignores permissions")
    def test_an_unwritable_tracker_directory_is_exit_2_without_a_traceback(self):
        """S-02 final review: a read-only tracker/ surfaced as 'refused' with render's traceback."""
        (self.proposals / "tracker").mkdir(parents=True)
        (self.proposals / "tracker").chmod(0o555)
        try:
            r = self.run_new("Locked tracker")
        finally:
            (self.proposals / "tracker").chmod(0o755)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("could not write", r.stderr)
        self.assertEqual(self.listing(), ["tracker"])

    def crash_script(self) -> Path:
        crash = Path(self._tmp.name) / "crash.py"
        crash.write_text("import sys\nsys.exit(3)\n")
        return crash

    def test_a_crashing_proposalcheck_is_exit_2_and_leaves_nothing(self):
        tool = load_tool()
        tool.PROPOSALCHECK = self.crash_script()
        rc, out, err = self.call(tool, "Crash")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("proposalcheck", err)
        self.assertFalse((self.root / "docs").exists())

    def test_a_crashing_tracker_is_exit_2_and_leaves_nothing(self):
        tool = load_tool()
        tool.TRACKER = self.crash_script()
        rc, out, err = self.call(tool, "Crash")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("tracker", err)
        self.assertFalse((self.root / "docs").exists())

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignores permissions")
    def test_an_unwritable_proposals_directory_is_exit_2_without_a_traceback(self):
        self.proposals.mkdir(parents=True)
        self.proposals.chmod(0o555)
        try:
            r = self.run_new("Locked")
        finally:
            self.proposals.chmod(0o755)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("could not write", r.stderr)
        self.assertEqual(self.listing(), [])


LEDGER_21 = {"proposal": 21, "title": "The standard is mandatory", "status": "accepted",
             "updated": "2026-09-14", "items": []}


class TestPageFor(Scratch):
    REL = "docs/proposals/21-standard-is-mandatory.json"

    def seed_ledger(self, data=None, name="21-standard-is-mandatory.json") -> Path:
        return self.seed(name, json.dumps(LEDGER_21 if data is None else data))

    def test_writes_only_the_page_for_an_existing_ledger(self):
        ledger = self.seed_ledger()
        before = ledger.read_bytes()
        r = self.run_new("--page-for", self.REL)
        self.assert_ok(r)
        self.assertEqual(self.listing(), ["21-standard-is-mandatory.html", "21-standard-is-mandatory.json", "tracker"])
        page = (self.proposals / "21-standard-is-mandatory.html").read_text()
        self.assertIn('<meta name="proposal-id" content="21">', page)
        self.assertIn("<title>21 · proposed · The standard is mandatory</title>", page)
        self.assertIn('<meta name="common-rules-template" content="proposal/21">', page)
        self.assertEqual(ledger.read_bytes(), before)
        self.assertIn(str(self.proposals / "21-standard-is-mandatory.html"), r.stdout)
        self.assertEqual(proposalcheck(self.root).returncode, 0)

    def test_refused_when_its_page_already_exists(self):
        self.seed_ledger()
        self.seed("21-standard-is-mandatory.html", "mine")
        r = self.run_new("--page-for", self.REL)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("21-standard-is-mandatory.html", r.stderr)
        self.assertEqual((self.proposals / "21-standard-is-mandatory.html").read_text(), "mine")

    def test_refused_when_another_page_holds_the_number(self):
        self.seed_ledger()
        self.seed("21-other.html", "theirs")
        r = self.run_new("--page-for", self.REL)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("21-other.html", r.stderr)
        self.assertNotIn("21-standard-is-mandatory.html", self.listing())

    def test_refused_for_a_missing_ledger(self):
        r = self.run_new("--page-for", self.REL)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("21-standard-is-mandatory.json", r.stderr)
        self.assertFalse((self.root / "docs").exists())

    def test_refused_when_the_ledger_number_disagrees_with_its_name(self):
        self.seed_ledger(dict(LEDGER_21, proposal=22))
        r = self.run_new("--page-for", self.REL)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("22", r.stderr)
        self.assertEqual(self.listing(), ["21-standard-is-mandatory.json"])

    def test_refused_for_a_ledger_outside_docs_proposals(self):
        (self.root / "21-loose.json").write_text(json.dumps(LEDGER_21))
        r = self.run_new("--page-for", "21-loose.json")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("docs/proposals", r.stderr)
        self.assertFalse((self.root / "docs").exists())

    def test_refused_for_a_bad_title_in_the_ledger(self):
        self.seed_ledger(dict(LEDGER_21, title="two\nlines"))
        r = self.run_new("--page-for", self.REL)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("title", r.stderr)
        self.assertEqual(self.listing(), ["21-standard-is-mandatory.json"])

    def test_cannot_be_combined_with_a_title_or_a_number(self):
        self.seed_ledger()
        for extra in (["A title"], ["--number", "21"]):
            with self.subTest(extra=extra):
                r = self.run_new("--page-for", self.REL, *extra)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("from the ledger", r.stderr)
                self.assertEqual(self.listing(), ["21-standard-is-mandatory.json"])

    def test_a_md_twin_and_an_assets_folder_do_not_block_its_page(self):
        """S-02 final review: the engine keeps 71-engine-1-3-programme.json beside
        a .md twin; --page-for called the twin a race and refused every time."""
        self.seed_ledger()
        self.seed("21-standard-is-mandatory.md", "twin")
        (self.proposals / "21-assets").mkdir()
        r = self.run_new("--page-for", self.REL)
        self.assert_ok(r)
        self.assertNotIn("just claimed", r.stderr)
        self.assertTrue((self.proposals / "21-standard-is-mandatory.html").is_file())

    def test_another_ledger_with_the_same_number_is_refused_and_not_called_a_race(self):
        self.seed_ledger()
        self.seed("21-second.json", json.dumps(dict(LEDGER_21, title="Second")))
        r = self.run_new("--page-for", self.REL)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("just claimed", r.stderr)
        self.assertIn("21-second.json", r.stderr)
        self.assertNotIn("21-standard-is-mandatory.html", self.listing())

    def test_renders_the_project_page(self):
        """Proposal 22, T-02: the project page, not a per-ledger page."""
        self.seed_ledger()
        r = self.run_new("--page-for", self.REL)
        self.assert_ok(r)
        index = self.proposals / "tracker" / "index.html"
        self.assertTrue(index.is_file())
        self.assertFalse((self.proposals / "tracker" / "21-standard-is-mandatory.html").exists())
        self.assertIn(f"tracker  {index}", r.stdout)
        self.assertIn("tracker board", r.stdout)
        chk = subprocess.run([sys.executable, str(TRACKER), "board", "--project", str(self.root), "--check"],
                             capture_output=True, text=True, check=False)
        self.assertEqual(chk.returncode, 0, chk.stdout + chk.stderr)

    def test_an_existing_per_ledger_page_is_left_alone(self):
        self.seed_ledger()
        (self.proposals / "tracker").mkdir()
        (self.proposals / "tracker" / "21-standard-is-mandatory.html").write_text("the owner's page")
        r = self.run_new("--page-for", self.REL)
        self.assert_ok(r)
        self.assertEqual((self.proposals / "tracker" / "21-standard-is-mandatory.html").read_text(), "the owner's page")
        self.assertTrue((self.proposals / "tracker" / "index.html").is_file())
        self.assertNotIn("render --check", r.stdout)


class TestProjectPageIsRestored(InProcess):
    """Proposal 22, T-02: new-proposal regenerates index.html, which most
    projects already have. On any failure after that, the created files go and
    index.html is put back byte for byte -- or removed if this run made it."""

    REL = "docs/proposals/21-standard-is-mandatory.json"

    @property
    def index(self) -> Path:
        return self.proposals / "tracker" / "index.html"

    def crashing_proposalcheck(self):
        crash = Path(self._tmp.name) / "crash.py"
        crash.write_text("import sys\nsys.exit(3)\n")
        tool = load_tool()
        tool.PROPOSALCHECK = crash
        return tool

    def test_a_crashing_proposalcheck_restores_an_existing_project_page(self):
        self.assert_ok(self.run_new("First"))
        before = b"hand bytes, not what board writes\n"
        self.index.write_bytes(before)
        rc, out, err = self.call(self.crashing_proposalcheck(), "Second")
        self.assertEqual(rc, 2, out + err)
        self.assertEqual(self.index.read_bytes(), before)
        self.assertEqual(self.listing(), ["01-first.html", "01-first.json", "tracker"])

    def test_page_for_restores_an_existing_project_page(self):
        self.seed("21-standard-is-mandatory.json", json.dumps(LEDGER_21))
        self.index.parent.mkdir(parents=True)
        before = b"the project page as committed\n"
        self.index.write_bytes(before)
        rc, out, err = self.call(self.crashing_proposalcheck(), "--page-for", self.REL)
        self.assertEqual(rc, 2, out + err)
        self.assertEqual(self.index.read_bytes(), before)
        self.assertEqual(self.listing(), ["21-standard-is-mandatory.json", "tracker"])

    def test_page_for_removes_a_project_page_it_created(self):
        self.seed("21-standard-is-mandatory.json", json.dumps(LEDGER_21))
        rc, out, err = self.call(self.crashing_proposalcheck(), "--page-for", self.REL)
        self.assertEqual(rc, 2, out + err)
        self.assertFalse(self.index.exists())
        self.assertEqual(self.listing(), ["21-standard-is-mandatory.json"])

    def test_page_for_is_refused_with_a_symlinked_project_page(self):
        self.seed("21-standard-is-mandatory.json", json.dumps(LEDGER_21))
        outside = Path(self._tmp.name) / "elsewhere.html"
        outside.write_text("outside")
        self.index.parent.mkdir(parents=True)
        self.index.symlink_to(outside)
        rc, out, err = self.call(load_tool(), "--page-for", self.REL)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("index.html", err)
        self.assertEqual(outside.read_text(), "outside")
        self.assertEqual(self.listing(), ["21-standard-is-mandatory.json", "tracker"])


CHILD = r'''
import importlib.machinery, importlib.util, pathlib, sys
loader = importlib.machinery.SourceFileLoader("new_proposal_child", sys.argv[1])
spec = importlib.util.spec_from_loader(loader.name, loader)
tool = importlib.util.module_from_spec(spec)
loader.exec_module(tool)
tool.PROPOSALCHECK = pathlib.Path(sys.argv[2])
sys.exit(tool.main(sys.argv[3:]))
'''


class TestSignalsRollBack(ProjectPage):
    """T-02 review round 1: SIGTERM or SIGHUP left the created files and a
    changed index.html. Each now raises inside the run, so the same rollback
    runs. A real signal, sent to this test's own child by its PID, while the
    child waits on a proposalcheck that sleeps -- after the board was written."""

    def interrupt(self, signum, *argv):
        import signal
        import time
        tmp = Path(self._tmp.name)
        marker = tmp / "checking.pid"
        # A marker left by an earlier run in this test would send the signal
        # before the child is ready (it would then die of the default action).
        marker.unlink(missing_ok=True)
        Path(str(marker) + ".part").unlink(missing_ok=True)
        sleeper = tmp / "sleeper.py"
        sleeper.write_text("import os, pathlib, time\n"
                           f"part = pathlib.Path({str(marker) + '.part'!r})\n"
                           "part.write_text(str(os.getpid()))\n"
                           f"os.replace(part, {str(marker)!r})\n"
                           "time.sleep(60)\n")
        child = subprocess.Popen([sys.executable, "-c", CHILD, str(NEW_PROPOSAL), str(sleeper),
                                  "--project", str(self.root), *argv],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 30
            while not marker.exists() and child.poll() is None and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertTrue(marker.exists(), "the child never reached proposalcheck")
            os.kill(child.pid, signum)
            out, err = child.communicate(timeout=30)
        finally:
            if child.poll() is None:
                os.kill(child.pid, signal.SIGKILL)
                child.wait()
            if marker.exists():
                # The sleeper is this test's grandchild: stopped by its PID, and only
                # if that PID is still the sleeper (never a recycled one).
                pid = int(marker.read_text())
                cmd = subprocess.run(["ps", "-p", str(pid), "-o", "command="],
                                     capture_output=True, text=True).stdout
                if str(sleeper) in cmd:
                    os.kill(pid, signal.SIGKILL)
        return child.returncode, out, err

    def test_sigterm_and_sighup_roll_back_a_new_proposal(self):
        import signal
        self.assert_ok(self.run_new("First"))
        before = b"the project page as committed\n"
        for signum in (signal.SIGTERM, signal.SIGHUP):
            with self.subTest(signal=signum.name):
                self.index.write_bytes(before)
                rc, out, err = self.interrupt(signum, "Second")
                self.assertEqual(rc, 128 + signum, out + err)
                self.assertIn(f"stopped by {signum.name}", err)
                self.assertNotIn("Traceback", err)
                self.assertEqual(self.listing(), ["01-first.html", "01-first.json", "tracker"])
                self.assertEqual(self.index.read_bytes(), before)

    def test_sigterm_rolls_back_page_for(self):
        import signal
        self.seed("21-standard-is-mandatory.json", json.dumps(LEDGER_21))
        rc, out, err = self.interrupt(signal.SIGTERM, "--page-for", "docs/proposals/21-standard-is-mandatory.json")
        self.assertEqual(rc, 128 + signal.SIGTERM, out + err)
        self.assertEqual(self.listing(), ["21-standard-is-mandatory.json"])
        self.assertFalse(self.index.exists())


class TestSeries(unittest.TestCase):
    """The PhotoVault app and engine number from one series across two repos."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        parent = Path(self._tmp.name).resolve()
        self.app, self.engine = parent / "app", parent / "engine"
        for repo, seed in ((self.app, "72-a.html"), (self.engine, "78-b.json")):
            (repo / "docs" / "proposals").mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "docs" / "proposals" / seed).write_text("")

    def tearDown(self):
        self._tmp.cleanup()

    def run_new(self, *args):
        return subprocess.run([sys.executable, str(NEW_PROPOSAL), "--project", str(self.app), *args],
                              capture_output=True, text=True, check=False)

    def declare(self, value, back=True):
        (self.app / ".common-rules.json").write_text(json.dumps({"proposal_series": value}))
        if back:
            (self.engine / ".common-rules.json").write_text(json.dumps({"proposal_series": ["../app"]}))

    def names(self, repo):
        return sorted(p.name for p in (repo / "docs" / "proposals").iterdir())

    def test_without_a_series_only_the_project_counts(self):
        r = self.run_new("Alone")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("73-alone.html", self.names(self.app))

    def test_the_next_number_is_free_across_the_series(self):
        self.declare(["../engine"])
        r = self.run_new("Shared")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("79-shared.html", self.names(self.app))
        self.assertEqual(self.names(self.engine), ["78-b.json"])

    def test_a_collision_with_a_sibling_is_refused_naming_it(self):
        self.declare(["../engine"])
        r = self.run_new("--number", "78", "Clash")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("../engine/docs/proposals/78-b.json", r.stderr)
        self.assertEqual(self.names(self.app), ["72-a.html"])

    def test_a_one_sided_series_cannot_run(self):
        """S-02 final review: declared only in the app, both repos took 79."""
        self.declare(["../engine"], back=False)
        r = self.run_new("One sided")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("does not declare", r.stderr)
        self.assertEqual(self.names(self.app), ["72-a.html"])

    def test_a_folder_inside_the_project_is_not_a_sibling(self):
        (self.app / "sub" / "docs" / "proposals").mkdir(parents=True)
        self.declare(["sub"], back=False)
        r = self.run_new("Nested")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("not a sibling", r.stderr)

    def test_a_broken_series_cannot_run(self):
        self.declare(["../missing"])
        r = self.run_new("Broken")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("proposal_series", r.stderr)
        self.assertEqual(self.names(self.app), ["72-a.html"])


class TestUsage(Scratch):
    def test_a_title_starting_with_a_dash_is_documented_and_works(self):
        h = subprocess.run([sys.executable, str(NEW_PROPOSAL), "--help"],
                           capture_output=True, text=True, check=False)
        self.assertIn('new-proposal -- "-5% budget"', h.stdout)
        self.assert_ok(self.run_new("--", "-5% budget"))
        self.assertIn("01-5-budget.html", self.listing())


if __name__ == "__main__":
    unittest.main()
