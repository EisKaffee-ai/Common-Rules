"""A proposal that asked numbered decisions must record the answers.

CLAUDE-workflow.md, "Number every proposal": a decision date says *when* a
proposal was decided, never *what*. Measured in finance-tracker (issue #584):
11 proposals `accepted`, 9 carrying a decision date, 3 recording what was
actually decided -- and those three were hand-written on the day the gap was
noticed. `proposal-auditor` measures drift from what a proposal authorised
and had nothing to measure against.

`bin/proposalcheck` is the mechanical form of that rule: a proposal that asks
nothing needs nothing (`did it ask?`, not `is it big?`), and a proposal
predating the rule -- or carrying no `proposal-decided` date at all -- is
grandfathered rather than failed, because a test that fails on day one against
documents nobody can fix gets disabled. These tests pin both halves: the
requirement itself, and the grandfather that keeps it from being retroactive.

Run:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROPOSALCHECK = ROOT / "bin" / "proposalcheck"

# Resolving the real projects lives in one place -- see tests/projects.py for
# why it is read from git rather than derived from this file's location.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from projects import apps_dir  # noqa: E402

BEFORE_FLOOR = "2026-08-10"   # < EFFECTIVE_DATE (2026-08-19) in proposalcheck
ON_FLOOR = "2026-08-19"
AFTER_FLOOR = "2026-08-20"

# STATUS_EFFECTIVE_DATE in proposalcheck (2026-08-20) is its own, later floor --
# a different rule, written a day after the one above, so it gets its own
# before/on/after trio rather than reusing BEFORE_FLOOR/ON_FLOOR/AFTER_FLOOR.
STATUS_BEFORE_FLOOR = "2026-08-19"
STATUS_ON_FLOOR = "2026-08-20"
STATUS_AFTER_FLOOR = "2026-08-21"

# NEW_PROPOSAL_FLOOR in proposalcheck (2026-09-14, proposal 21 / S-03) is a
# third, later floor still -- gates a page's own git-add date, not its
# proposal-decided meta, so it gets its own trio too.
NEW_PROPOSAL_AFTER_FLOOR = "2026-09-14T00:00:00+00:00"


def proposal(status: str | None, decided: str | None = None, *,
             asks_decisions: bool = False, answered: bool = False,
             exceptions: bool = False, part_of: str | None = None,
             pid: str = "01") -> str:
    """A minimal but structurally real proposal document. `status=None` omits
    the meta tag entirely -- a lead with no status at all, the shape the
    status-required rule checks for. `part_of` marks this document as a
    section rather than a lead."""
    # Every document needs its *own* id, sections included -- measured across
    # finance-tracker's 14 real sections, where 33-38 all sit part-of 32 and
    # each carries its own number. Hardcoding "01" here made any two-document
    # fixture a proposal-id collision once that became a checked rule.
    meta = [f'<meta name="proposal-id" content="{pid}">']
    if status is not None:
        meta.append(f'<meta name="proposal-status" content="{status}">')
    if decided:
        meta.append(f'<meta name="proposal-decided" content="{decided}">')
    if part_of:
        meta.append(f'<meta name="proposal-part-of" content="{part_of}">')

    body = ["<h1>Test proposal</h1>"]
    if asks_decisions:
        body.append(
            '<ol class="decisions"><li><b>D1.</b> Ship it or not.</li></ol>'
        )
    if answered:
        body.append('<div id="decided"><b>Decided.</b> D1: ship it.</div>')
    if exceptions:
        body.append(
            '<div id="exceptions"><b>Not built.</b> The export button, '
            'because the sponsor deprioritised it in favour of the dashboard.</div>'
        )
    return "<html><head>" + "\n".join(meta) + "</head><body>" + \
        "\n".join(body) + "</body></html>"


def run(project: Path):
    return subprocess.run([sys.executable, str(PROPOSALCHECK), "--project", str(project)],
                          capture_output=True, text=True, check=False)


def load_proposalcheck_module():
    """White-box import of bin/proposalcheck (no .py suffix, so it needs an
    explicit SourceFileLoader -- spec_from_file_location cannot infer a
    loader from an extension-less filename on its own) -- used only by the
    tests below that need to monkeypatch subprocess.run or call internals
    directly (git-log failure simulation, hoisting call counts) that a
    black-box CLI run cannot exercise cleanly."""
    loader = importlib.machinery.SourceFileLoader("proposalcheck_whitebox", str(PROPOSALCHECK))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    # dataclass() looks the defining module up via sys.modules[__module__] --
    # register before exec_module, same as a normal import would.
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


class ProposalLifecycleTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        (self.tmp / "CLAUDE.md").write_text("test project\n")
        self.proposals = self.tmp / "docs" / "proposals"
        self.proposals.mkdir(parents=True)

    def write(self, name: str, text: str):
        (self.proposals / name).write_text(text)

    def with_decisions_heading(self, extra: str = "") -> str:
        return (proposal("proposed").replace(
            "</body>", f'{extra}<h2>Decisions</h2><ol class="decisions">'
            '<li>D1. Decide.</li></ol></body>'
        ))

    def test_visual_gap_is_a_warning_not_a_violation(self):
        self.write("01-x.html", self.with_decisions_heading())
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("warning", r.stdout)
        self.assertIn("no table, diagram, or headline-figure block", r.stdout)

    def test_table_before_decisions_has_no_visual_warning(self):
        self.write("01-x.html", self.with_decisions_heading(
            '<table><tr><td>evidence</td></tr></table>'
        ))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("warning:", r.stdout)

    def test_svg_and_stat_blocks_are_visual_evidence(self):
        for visual in ('<svg aria-label="flow"></svg>', '<div class="stat"><b>3</b></div>'):
            with self.subTest(visual=visual):
                self.write("01-x.html", self.with_decisions_heading(visual))
                r = run(self.tmp)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertNotIn("warning:", r.stdout)

    # -- the requirement itself -------------------------------------------

    def test_accepted_with_unanswered_decisions_fails(self):
        self.write("01-x.html", proposal("accepted", AFTER_FLOOR, asks_decisions=True))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("01-x.html", r.stdout)
        self.assertIn("records no answers", r.stdout)

    def test_accepted_with_answered_decisions_passes(self):
        self.write("01-x.html", proposal("accepted", AFTER_FLOOR,
                                          asks_decisions=True, answered=True))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_accepted_asking_nothing_passes_with_no_answer_block(self):
        """A proposal that asked no numbered decisions needs no answers block --
        scoped mechanically ("did it ask?"), not by size."""
        self.write("01-x.html", proposal("accepted", AFTER_FLOOR))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_empty_decisions_list_asks_nothing(self):
        text = proposal("accepted", AFTER_FLOOR).replace(
            "<h1>Test proposal</h1>",
            '<h1>Test proposal</h1><ol class="decisions"></ol>')
        self.write("01-x.html", text)
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_proposed_status_is_never_checked(self):
        """A proposal still being negotiated is expected to have open decisions."""
        self.write("01-x.html", proposal("proposed", asks_decisions=True))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_built_is_checked_like_completed(self):
        """`built` is a grandfathered *word*, not an exemption from the rule."""
        self.write("01-x.html", proposal("built", AFTER_FLOOR, asks_decisions=True))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    # -- completed in part --------------------------------------------------

    def test_completed_in_part_without_exceptions_fails(self):
        self.write("01-x.html", proposal("completed in part", AFTER_FLOOR))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("no id=\"exceptions\"", r.stdout)

    def test_completed_in_part_with_exceptions_passes(self):
        self.write("01-x.html", proposal("completed in part", AFTER_FLOOR,
                                          exceptions=True))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    # -- grandfathering -------------------------------------------------------

    def test_decided_before_the_floor_is_grandfathered(self):
        self.write("01-x.html", proposal("accepted", BEFORE_FLOOR, asks_decisions=True))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0,
                         "a proposal decided before the rule existed was failed by it: "
                         + r.stdout + r.stderr)

    def test_decided_exactly_on_the_floor_is_not_grandfathered(self):
        self.write("01-x.html", proposal("accepted", ON_FLOOR, asks_decisions=True))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 1,
                         "the floor date itself must be inside the rule, not before it: "
                         + r.stdout + r.stderr)

    def test_no_decided_date_at_all_is_grandfathered(self):
        """Undated reads the same as 'decided before this rule existed' -- not a
        loophole a new proposal can use by omitting the meta tag going forward,
        since every proposal created after this rule lands is expected to carry
        the date already (a separate, pre-existing convention)."""
        self.write("01-x.html", proposal("accepted", decided=None, asks_decisions=True))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_completed_in_part_exceptions_requirement_is_not_date_gated(self):
        """New vocabulary, nothing existing to grandfather -- so even a proposal
        dated before the floor must still carry the exceptions block once it
        claims this status at all."""
        self.write("01-x.html", proposal("completed in part", BEFORE_FLOOR))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    # -- the real gap this was measured against --------------------------

    def test_finance_tracker_blast_radius_is_all_grandfathered_today(self):
        """Every finance-tracker proposal non-compliant today was decided before
        this rule's floor -- so landing the rule blocks nothing retroactively.
        Guards against a fix that quietly re-tightens the floor and starts
        failing history."""
        apps = apps_dir()
        proj = apps / "finance-tracker" if apps else None
        if proj is None or not proj.exists():
            self.skipTest(f"finance-tracker not present beside {apps}")
        r = run(proj)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    # -- no docs/proposals at all -------------------------------------------

    def test_no_proposals_directory_is_could_not_check_not_a_pass(self):
        empty = self.tmp / "empty-project"
        empty.mkdir()
        r = run(empty)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)


class ProposalIsEitherAProposalOrAnArtifactTests(unittest.TestCase):
    """CLAUDE-workflow.md, 'A document is either a proposal or an artifact':
    a lead (no proposal-part-of) must carry a proposal-status from the known
    vocabulary; a section (has proposal-part-of) must carry none. Its own
    floor (STATUS_EFFECTIVE_DATE, 2026-08-20) is separate from the
    decisions-recorded rule's floor above -- a different rule, a different
    day."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        (self.tmp / "CLAUDE.md").write_text("test project\n")
        self.proposals = self.tmp / "docs" / "proposals"
        self.proposals.mkdir(parents=True)

    def write(self, name: str, text: str):
        (self.proposals / name).write_text(text)

    # -- a lead needs a status -----------------------------------------------

    def test_lead_with_no_status_after_the_floor_fails(self):
        self.write("01-x.html", proposal(None, STATUS_AFTER_FLOOR))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("carries no proposal-status", r.stdout)

    def test_lead_with_a_known_status_passes(self):
        for status in ("proposed", "accepted", "completed", "completed in part",
                        "built", "amends 07", "superseded by 14"):
            with self.subTest(status=status):
                self.tmp2 = tempfile.TemporaryDirectory()
                self.addCleanup(self.tmp2.cleanup)
                proposals = Path(self.tmp2.name) / "docs" / "proposals"
                proposals.mkdir(parents=True)
                (Path(self.tmp2.name) / "CLAUDE.md").write_text("test project\n")
                # "completed in part" separately requires its own id="exceptions"
                # block (the rule above) -- unrelated to the status-vocabulary
                # check this test targets, so give it one to isolate that.
                needs_exceptions = status == "completed in part"
                (proposals / "01-x.html").write_text(
                    proposal(status, STATUS_AFTER_FLOOR, exceptions=needs_exceptions)
                )
                r = run(Path(self.tmp2.name))
                self.assertEqual(r.returncode, 0, f"{status}: " + r.stdout + r.stderr)

    def test_lead_with_an_unrecognized_status_after_the_floor_fails(self):
        self.write("01-x.html", proposal("propsed", STATUS_AFTER_FLOOR))  # typo, on purpose
        r = run(self.tmp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("matches none of the known vocabulary", r.stdout)

    def test_superseded_by_hyphenated_is_not_the_known_form(self):
        """The exact typo found live in pockets ('superseded-by 14' instead of
        'superseded by 14') -- the whole-string regex must not accept it."""
        self.write("01-x.html", proposal("superseded-by 14", STATUS_AFTER_FLOOR))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    # -- a section (part-of) carries no status of its own --------------------

    def test_section_with_no_status_passes(self):
        self.write("01-lead.html", proposal("accepted", STATUS_AFTER_FLOOR))
        self.write("02-section.html", proposal(None, part_of="01", pid="02"))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_section_claiming_its_own_status_fails(self):
        self.write("01-lead.html", proposal("accepted", STATUS_AFTER_FLOOR))
        self.write("02-section.html", proposal("proposed", part_of="01", pid="02"))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("also claims its own status", r.stdout)

    # -- grandfathering, this rule's own floor --------------------------------

    def test_lead_with_no_status_decided_before_this_rules_floor_is_grandfathered(self):
        self.write("01-x.html", proposal(None, STATUS_BEFORE_FLOOR))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_lead_with_no_status_decided_exactly_on_this_rules_floor_is_not_grandfathered(self):
        self.write("01-x.html", proposal(None, STATUS_ON_FLOOR))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_lead_with_no_status_and_no_decided_date_at_all_is_grandfathered(self):
        """Matches pip's 02a/02b -- undated leads with no status, predating
        this rule the same way an undated proposal predates the one above."""
        self.write("01-x.html", proposal(None, decided=None))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_pockets_and_pip_blast_radius_is_grandfathered_today(self):
        """Every non-compliant lead in pockets and pip today was decided (or
        undated) before this rule's floor -- guards against a fix that
        quietly re-tightens the floor and starts failing history."""
        apps = apps_dir()
        for name in ("pockets", "pip"):
            with self.subTest(project=name):
                proj = apps / name if apps else None
                # `continue` here reported `ok` after asserting nothing, which
                # is indistinguishable from a run that actually checked the
                # project. A skip at least says so out loud.
                if proj is None or not proj.exists():
                    self.skipTest(f"{name} not present beside {apps}")
                r = run(proj)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class NewProposalMustCarryStatusTests(unittest.TestCase):
    """Proposal 21 (S-03): a lead with no `proposal-status` meta at all is a
    violation once the *page itself* is new -- measured by when it was first
    added to git, not by its (often-absent) `proposal-decided` date.

    PhotoVault's app proposals 72, 75, 76 and the engine's 77 all carry no
    status meta and no decided date, so the existing lead-status check (which
    is gated by `proposal-decided`) reads them as undated and silently
    grandfathers them -- this is the gap that check leaves open. This rule
    has its own floor (NEW_PROPOSAL_FLOOR, 2026-09-14) and needs real git
    history to answer "when was this page first added", so each test here
    builds a scratch git repo rather than writing loose files."""

    NEW_STATUS_MESSAGE = "carries no proposal status"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "proj"
        self.repo.mkdir()
        self.addCleanup(self._tmp.cleanup)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        (self.repo / "CLAUDE.md").write_text("test project\n")
        (self.repo / "docs" / "proposals").mkdir(parents=True)
        self.git("add", "-A")
        self.git("commit", "-qm", "seed")

    def git(self, *args, env=None):
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              capture_output=True, text=True, check=True, env=env)

    def commit_page(self, name: str, text: str, *, when: str | None = None):
        """Write `name` under docs/proposals/ and commit it, optionally
        back-dating the commit (both author and committer, as `git log
        --format=%aI` reads the author date)."""
        (self.repo / "docs" / "proposals" / name).write_text(text)
        self.git("add", "-A")
        env = dict(os.environ)
        if when:
            env["GIT_AUTHOR_DATE"] = when
            env["GIT_COMMITTER_DATE"] = when
        self.git("commit", "-qm", f"add {name}", env=env)

    def write_uncommitted(self, name: str, text: str):
        (self.repo / "docs" / "proposals" / name).write_text(text)

    def run_check(self):
        return run(self.repo)

    def test_new_committed_page_without_status_is_a_violation(self):
        self.commit_page("01-x.html", proposal(None), when=NEW_PROPOSAL_AFTER_FLOOR)
        r = self.run_check()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(self.NEW_STATUS_MESSAGE, r.stdout)
        self.assertIn("01-x.html", r.stdout)

    def test_old_page_committed_before_the_floor_is_not_a_violation(self):
        self.commit_page("01-x.html", proposal(None), when="2026-01-01T00:00:00+00:00")
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn(self.NEW_STATUS_MESSAGE, r.stdout)

    def test_uncommitted_page_without_status_is_a_violation(self):
        """A proposal cannot dodge this rule by staying out of git entirely."""
        self.write_uncommitted("01-x.html", proposal(None))
        r = self.run_check()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(self.NEW_STATUS_MESSAGE, r.stdout)

    def test_page_with_proposal_part_of_is_not_a_violation(self):
        """Round 2, item 4: this test was previously (mis-)named
        `test_artifact_page_is_not_a_violation`, but its fixture sets
        `proposal-part-of` -- exactly the SECTION shape the next test below
        checks, not a true artifact (a page with no proposal-* meta at all).
        Renamed honestly rather than deleted: it is a legitimate, if
        duplicate-looking, assertion that `is_lead()` returning False is
        what exempts a page here, independent of how the fixture below
        happens to be built. `test_true_artifact_page_...` is the real
        artifact case the old name wrongly claimed to cover."""
        self.commit_page("01-lead.html", proposal("accepted", STATUS_AFTER_FLOOR),
                         when=NEW_PROPOSAL_AFTER_FLOOR)
        self.commit_page("02-artifact.html", proposal(None, part_of="01", pid="02"),
                         when=NEW_PROPOSAL_AFTER_FLOOR)
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn(self.NEW_STATUS_MESSAGE, r.stdout)

    def test_true_artifact_page_with_no_proposal_meta_is_a_violation_when_new(self):
        """The real artifact shape, per the reviewer's ruling: a page that
        carries NO proposal-* meta at all (not even proposal-id), sitting
        beside an `NN-assets/` folder and `.css`/`.js` files -- the exact
        shape of PhotoVault app's 73/74/76 (self-described as "Proposal NN"
        in their own text, per the reviewer's reproduction). proposalcheck
        has no notion of "artifact" distinct from "lead with no part-of", so
        this page IS a lead by the code's own definition and must be flagged
        once it is new. No classifier change -- the ruling was explicit that
        this is correct, not a bug."""
        name = "01-workspace.html"
        text = ("<html><head><meta charset=\"utf-8\"></head><body>"
                "<h1>Proposal 01: Workspace</h1></body></html>")
        (self.repo / "docs" / "proposals" / "01-assets").mkdir(parents=True)
        (self.repo / "docs" / "proposals" / "01-assets" / "diagram.png").write_bytes(b"\x89PNG")
        (self.repo / "docs" / "proposals" / "01-workspace.css").write_text("body {}\n")
        (self.repo / "docs" / "proposals" / "01-workspace.js").write_text("// noop\n")
        self.commit_page(name, text, when=NEW_PROPOSAL_AFTER_FLOOR)
        r = self.run_check()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(self.NEW_STATUS_MESSAGE, r.stdout)
        self.assertIn(name, r.stdout)

    def test_section_page_is_not_a_violation(self):
        self.commit_page("01-lead.html", proposal("accepted", STATUS_AFTER_FLOOR),
                         when=NEW_PROPOSAL_AFTER_FLOOR)
        self.commit_page("02-section.html", proposal(None, part_of="01", pid="02"),
                         when=NEW_PROPOSAL_AFTER_FLOOR)
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn(self.NEW_STATUS_MESSAGE, r.stdout)

    def test_new_page_with_status_passes_the_new_rule(self):
        self.commit_page("01-x.html", proposal("proposed"),
                         when=NEW_PROPOSAL_AFTER_FLOOR)
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn(self.NEW_STATUS_MESSAGE, r.stdout)

    def test_outside_a_git_repository_the_rule_never_fires(self):
        """No git history to ask "when was this first added" -- today's
        behaviour holds rather than guessing. Uses a plain (non-git) tmpdir,
        same shape as ProposalLifecycleTests above."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "CLAUDE.md").write_text("test project\n")
            proposals = proj / "docs" / "proposals"
            proposals.mkdir(parents=True)
            (proposals / "01-x.html").write_text(proposal(None))
            r = run(proj)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertNotIn(self.NEW_STATUS_MESSAGE, r.stdout)


class ShallowCloneSkipsNewPageRuleTests(unittest.TestCase):
    """Round 2, item 1: `git log --diff-filter=A` on a shallow clone treats
    its single boundary commit as having no parent, so EVERY path in that
    commit's tree reads as "Added" there -- an old page looks freshly added
    purely because its real history was truncated. The fix: detect
    `--is-shallow-repository` once per run and skip the new-page rule
    entirely, with one stderr line explaining why."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.origin = Path(self._tmp.name) / "origin"
        self.origin.mkdir()
        self.addCleanup(self._tmp.cleanup)
        self.git(self.origin, "init", "-q", "-b", "main")
        self.git(self.origin, "config", "user.email", "t@example.com")
        self.git(self.origin, "config", "user.name", "t")
        (self.origin / "CLAUDE.md").write_text("test project\n")
        (self.origin / "docs" / "proposals").mkdir(parents=True)

    def git(self, repo, *args, env=None):
        return subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, check=True, env=env)

    def commit(self, repo, rel, text, *, when=None):
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        self.git(repo, "add", "-A")
        env = dict(os.environ)
        if when:
            env["GIT_AUTHOR_DATE"] = when
            env["GIT_COMMITTER_DATE"] = when
        self.git(repo, "commit", "-qm", f"add {rel}", env=env)

    def shallow_clone(self):
        clone = Path(self._tmp.name) / "clone"
        subprocess.run(["git", "clone", "--depth", "1", "-q",
                        f"file://{self.origin}", str(clone)],
                       capture_output=True, text=True, check=True)
        return clone

    def test_old_page_in_a_shallow_clone_is_not_flagged_and_a_reason_is_printed(self):
        # An old, statusless lead page -- committed long before the floor.
        self.commit(self.origin, "docs/proposals/01-x.html", proposal(None),
                    when="2020-01-01T00:00:00+00:00")
        # More commits after it, ending at HEAD, so a --depth 1 clone's one
        # boundary commit is NOT the one that originally added the page --
        # it just still contains the page in its tree.
        for i in range(3):
            self.commit(self.origin, f"docs/proposals/README-{i}.md", f"note {i}\n",
                        when=NEW_PROPOSAL_AFTER_FLOOR)

        clone = self.shallow_clone()
        is_shallow = self.git(clone, "rev-parse", "--is-shallow-repository")
        self.assertEqual(is_shallow.stdout.strip(), "true",
                         "test setup must actually produce a shallow clone")

        r = run(clone)
        self.assertNotIn("carries no proposal status", r.stdout,
                         "a shallow clone's truncated history must not manufacture "
                         "a new-page violation: " + r.stdout + r.stderr)
        self.assertIn("shallow clone", r.stderr)
        self.assertIn("skipped", r.stderr)

    def test_full_clone_of_the_same_history_is_flagged(self):
        """Same fixture, no --depth -- confirms the shallow case above is
        actually different behaviour, not just an always-passing rule."""
        self.commit(self.origin, "docs/proposals/01-x.html", proposal(None),
                    when="2020-01-01T00:00:00+00:00")
        for i in range(3):
            self.commit(self.origin, f"docs/proposals/README-{i}.md", f"note {i}\n",
                        when=NEW_PROPOSAL_AFTER_FLOOR)
        full_clone = Path(self._tmp.name) / "full"
        subprocess.run(["git", "clone", "-q", f"file://{self.origin}", str(full_clone)],
                       capture_output=True, text=True, check=True)
        r = run(full_clone)
        self.assertNotIn("carries no proposal status", r.stdout, r.stdout + r.stderr)
        self.assertEqual(r.stderr, "")


class CommitterDateNotAuthorDateTests(unittest.TestCase):
    """Round 2, item 2: `git commit --date` (GIT_AUTHOR_DATE) is free text
    anyone with commit access can set to anything. The committer date
    (%cI, GIT_COMMITTER_DATE) is what the repository itself recorded the
    commit as happening. A page whose author date is spoofed to 2020 but
    whose commit actually happened today must still be flagged as new."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "proj"
        self.repo.mkdir()
        self.addCleanup(self._tmp.cleanup)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        (self.repo / "CLAUDE.md").write_text("test project\n")
        (self.repo / "docs" / "proposals").mkdir(parents=True)
        self.git("add", "-A")
        self.git("commit", "-qm", "seed")

    def git(self, *args, env=None):
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              capture_output=True, text=True, check=True, env=env)

    def test_spoofed_old_author_date_with_a_real_committer_date_today_is_flagged(self):
        p = self.repo / "docs" / "proposals" / "01-x.html"
        p.write_text(proposal(None))
        self.git("add", "-A")
        env = dict(os.environ)
        # Author date spoofed to 2020 -- what `git commit --date=2020-01-01`
        # would do. GIT_COMMITTER_DATE deliberately left unset, so git uses
        # the real current time for it, exactly like an ordinary `git commit`
        # run today would.
        env["GIT_AUTHOR_DATE"] = "2020-01-01T00:00:00+00:00"
        self.git("commit", "-qm", "add 01-x.html (spoofed author date)", env=env)

        author_date = self.git("log", "-1", "--format=%aI").stdout.strip()
        committer_date = self.git("log", "-1", "--format=%cI").stdout.strip()
        self.assertTrue(author_date.startswith("2020"), "test setup sanity check")
        self.assertFalse(committer_date.startswith("2020"),
                         "test setup sanity check -- committer date must be real")

        r = run(self.repo)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("carries no proposal status", r.stdout)


class NewestAddRecordTests(unittest.TestCase):
    """Round 2, item 3: the newest "A" (add) record decides "new", not the
    oldest. A rename (--follow) keeps its single original record and reads
    as old either way -- a delete-then-re-add at the same path produces a
    SECOND "A" record, and the resurrection is what should decide "new"."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "proj"
        self.repo.mkdir()
        self.addCleanup(self._tmp.cleanup)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        (self.repo / "CLAUDE.md").write_text("test project\n")
        (self.repo / "docs" / "proposals").mkdir(parents=True)
        self.git("add", "-A")
        self.git("commit", "-qm", "seed")

    def git(self, *args, env=None):
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              capture_output=True, text=True, check=True, env=env)

    def commit_all(self, msg, *, when=None):
        self.git("add", "-A")
        env = dict(os.environ)
        if when:
            env["GIT_AUTHOR_DATE"] = when
            env["GIT_COMMITTER_DATE"] = when
        self.git("commit", "-qm", msg, env=env)

    def test_old_page_renamed_today_is_not_new(self):
        old = self.repo / "docs" / "proposals" / "01-old.html"
        old.write_text(proposal(None))
        self.commit_all("add 01-old.html", when="2020-01-01T00:00:00+00:00")

        renamed = self.repo / "docs" / "proposals" / "01-old-renamed.html"
        self.git("mv", "docs/proposals/01-old.html", "docs/proposals/01-old-renamed.html")
        self.commit_all("rename 01-old.html", when=NEW_PROPOSAL_AFTER_FLOOR)

        add_records = self.git("log", "--diff-filter=A", "--follow", "--format=%cI",
                               "--", "docs/proposals/01-old-renamed.html").stdout
        self.assertEqual(len(add_records.strip().splitlines()), 1,
                         "test setup sanity check -- a rename must not produce a "
                         "second add record under --follow")

        r = run(self.repo)
        self.assertNotIn("carries no proposal status", r.stdout, r.stdout + r.stderr)

    def test_old_page_deleted_and_re_added_at_the_same_path_today_is_new(self):
        target = self.repo / "docs" / "proposals" / "01-x.html"
        target.write_text(proposal(None))
        self.commit_all("add 01-x.html", when="2020-01-01T00:00:00+00:00")

        self.git("rm", "-q", "docs/proposals/01-x.html")
        self.commit_all("remove 01-x.html", when="2020-06-01T00:00:00+00:00")

        # `git rm` can take the now-empty directory with it (git tracks no
        # empty directories) -- recreate it before writing the resurrection.
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(proposal(None))
        self.commit_all("re-add 01-x.html", when=NEW_PROPOSAL_AFTER_FLOOR)

        add_records = self.git("log", "--diff-filter=A", "--follow", "--format=%cI",
                               "--", "docs/proposals/01-x.html").stdout
        self.assertEqual(len(add_records.strip().splitlines()), 2,
                         "test setup sanity check -- delete then re-add must produce "
                         "two add records: " + add_records)

        r = run(self.repo)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("carries no proposal status", r.stdout)


class GitLogFailureIsNamedNotSilentlyNewTests(unittest.TestCase):
    """Round 2, item 6: `--is-inside-work-tree` succeeding already rules out
    "not a repository" -- if `git log` itself then fails, that is a distinct
    problem (permissions, a corrupt object, whatever), and must be reported
    by name rather than silently treated as "new". Simulated with a
    monkeypatched subprocess.run: reproducing a genuinely corrupt git
    repository deterministically is not practical for a unit test, and the
    function under test only cares about the git-log call's return code and
    stderr, not how they came about."""

    def setUp(self):
        self.mod = load_proposalcheck_module()

    def test_git_log_failure_is_reported_by_name_not_treated_as_new(self):
        ctx = self.mod.RepoContext(inside=True, shallow=False)
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return subprocess.CompletedProcess(
                cmd, returncode=128, stdout="",
                stderr="fatal: bad object HEAD\nadditional detail\n")

        original = self.mod.subprocess.run
        self.mod.subprocess.run = fake_run
        try:
            msg = self.mod.new_page_violation(Path("/tmp/does-not-matter/01-x.html"), ctx)
        finally:
            self.mod.subprocess.run = original

        self.assertIsNotNone(msg, "a git-log failure must be reported, not swallowed")
        self.assertIn("could not read its git history", msg)
        self.assertIn("fatal: bad object HEAD", msg)
        self.assertNotIn("additional detail", msg, "only the first stderr line")
        self.assertNotEqual(msg, "carries no proposal status -- create proposals "
                                 "with bin/new-proposal (common-rules proposal 21)",
                            "a git failure must never read as an ordinary new-page violation")


class HoistedRepoChecksTests(unittest.TestCase):
    """Round 2, item 5: `--is-inside-work-tree` and `--is-shallow-repository`
    are repository-level facts, not per-page ones. `repo_context()` must be
    called exactly once per `main()` run, regardless of how many proposal
    pages exist -- verified by counting `rev-parse` invocations through a
    wrapped subprocess.run, across a repo with several statusless pages."""

    def setUp(self):
        self.mod = load_proposalcheck_module()
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "proj"
        self.repo.mkdir()
        self.addCleanup(self._tmp.cleanup)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        (self.repo / "CLAUDE.md").write_text("test project\n")
        (self.repo / "docs" / "proposals").mkdir(parents=True)
        # Statusless leads -- the shape that actually reaches the git calls
        # under test. Pages that already carry a status never call git at
        # all (before or after hoisting), which would make this count
        # comparison meaningless.
        for i in range(5):
            (self.repo / "docs" / "proposals" / f"{i:02d}-x.html").write_text(
                proposal(None, pid=f"{i:02d}"))
        self.git("add", "-A")
        self.git("commit", "-qm", "seed")

    def git(self, *args, env=None):
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              capture_output=True, text=True, check=True, env=env)

    def test_rev_parse_runs_exactly_once_per_flag_regardless_of_page_count(self):
        calls = []
        real_run = subprocess.run

        def counting_run(cmd, **kwargs):
            calls.append(cmd)
            return real_run(cmd, **kwargs)

        self.mod.subprocess.run = counting_run
        try:
            # main() reads sys.argv directly -- drive it the same way the CLI does.
            old_argv = sys.argv
            sys.argv = ["proposalcheck", "--project", str(self.repo)]
            try:
                self.mod.main()
            finally:
                sys.argv = old_argv
        finally:
            self.mod.subprocess.run = real_run

        inside_calls = [c for c in calls if "--is-inside-work-tree" in c]
        shallow_calls = [c for c in calls if "--is-shallow-repository" in c]
        self.assertEqual(len(inside_calls), 1,
                         f"expected exactly 1 --is-inside-work-tree call for 5 pages, "
                         f"got {len(inside_calls)}")
        self.assertEqual(len(shallow_calls), 1,
                         f"expected exactly 1 --is-shallow-repository call for 5 pages, "
                         f"got {len(shallow_calls)}")


class TemplateMetaUndatedDecisionTests(unittest.TestCase):
    """Round 2, item 7a (queued from S-02's review): a page written by
    bin/new-proposal (`<meta name="common-rules-template" ...>`) that
    reaches a decision status with no proposal-decided date is a violation,
    not date-gated -- there is no backlog to grandfather, since the template
    did not exist before proposal 21. Pages without the template meta keep
    every existing grandfather unchanged."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        (self.tmp / "CLAUDE.md").write_text("test project\n")
        self.proposals = self.tmp / "docs" / "proposals"
        self.proposals.mkdir(parents=True)

    def write(self, name: str, text: str):
        (self.proposals / name).write_text(text)

    def templated(self, status: str, decided: str | None = None) -> str:
        meta = ['<meta name="proposal-id" content="01">',
                '<meta name="common-rules-template" content="1">',
                f'<meta name="proposal-status" content="{status}">']
        if decided:
            meta.append(f'<meta name="proposal-decided" content="{decided}">')
        return ("<html><head>" + "\n".join(meta) +
               "</head><body><h1>Test proposal</h1></body></html>")

    def test_template_page_accepted_with_no_decided_date_is_a_violation(self):
        self.write("01-x.html", self.templated("accepted"))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("accepted without a proposal-decided date", r.stdout)
        self.assertIn("record when it was decided", r.stdout)

    def test_template_page_accepted_with_a_decided_date_passes(self):
        self.write("01-x.html", self.templated("accepted", decided="2020-01-01"))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_template_page_proposed_with_no_decided_date_passes(self):
        """`proposed` is not a decision status -- an open proposal is
        expected to have no decided date yet."""
        self.write("01-x.html", self.templated("proposed"))
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_non_template_page_with_no_decided_date_keeps_the_existing_grandfather(self):
        """Same shape, minus the template meta -- must NOT trigger item 7a;
        stays governed by the pre-existing (dated) grandfather only."""
        text = proposal("accepted", decided=None)
        self.write("01-x.html", text)
        r = run(self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("without a proposal-decided date", r.stdout)


class SelfClosingMetaTagTests(unittest.TestCase):
    """Round 2, item 7b: `<meta ... />` (self-closing) is valid HTML and
    must be read identically to `<meta ...>`.

    Fixtures are git-committed on or after NEW_PROPOSAL_FLOOR (item 5's
    new-page rule, not a bare tmpdir) deliberately: a self-closed
    proposal-status or proposal-decided meta that `meta()` fails to parse
    reads back as `None`, which the *undated-grandfather* in the pre-existing
    checks would then quietly wave through anyway -- masking the parsing bug
    behind an unrelated grandfather. Landing the page new and dated, instead,
    means a parsing failure surfaces as a concrete "carries no proposal
    status" violation, so the test actually distinguishes the two regexes."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "proj"
        self.repo.mkdir()
        self.addCleanup(self._tmp.cleanup)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        (self.repo / "CLAUDE.md").write_text("test project\n")
        (self.repo / "docs" / "proposals").mkdir(parents=True)
        self.git("add", "-A")
        self.git("commit", "-qm", "seed")

    def git(self, *args, env=None):
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              capture_output=True, text=True, check=True, env=env)

    def commit_page(self, name: str, text: str, *, when: str):
        (self.repo / "docs" / "proposals" / name).write_text(text)
        self.git("add", "-A")
        env = dict(os.environ)
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
        self.git("commit", "-qm", f"add {name}", env=env)

    def test_self_closing_status_meta_is_read_not_reported_as_missing(self):
        text = ('<html><head>'
               '<meta name="proposal-id" content="01" />'
               '<meta name="proposal-status" content="accepted" />'
               '<meta name="proposal-decided" content="2020-01-01" />'
               '</head><body><h1>Test proposal</h1></body></html>')
        self.commit_page("01-x.html", text, when=NEW_PROPOSAL_AFTER_FLOOR)
        r = run(self.repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("carries no proposal", r.stdout)

    def test_self_closing_part_of_meta_is_read_as_a_section(self):
        lead = ('<html><head><meta name="proposal-id" content="01" />'
               '<meta name="proposal-status" content="accepted" />'
               '<meta name="proposal-decided" content="2020-01-01" />'
               '</head><body><h1>Lead</h1></body></html>')
        section = ('<html><head><meta name="proposal-id" content="02" />'
                  '<meta name="proposal-part-of" content="01" />'
                  '</head><body><h1>Section</h1></body></html>')
        self.commit_page("01-lead.html", lead, when=NEW_PROPOSAL_AFTER_FLOOR)
        self.commit_page("02-section.html", section, when=NEW_PROPOSAL_AFTER_FLOOR)
        r = run(self.repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
