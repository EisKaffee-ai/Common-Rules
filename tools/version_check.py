"""Shared logic for VERSION's bump requirement (proposal 32, V-02).

Imported by both `bin/version-check` (reports and `--check`s) and
`tests/test_version.py`, the same shape `tools/workflow_stamp.py` uses for
`bin/workflow-stamp` and `tests/test_workflow_stamp.py` (proposal 31,
O-12): one implementation of "what does the CHANGELOG require", not two
computing it independently and drifting apart on the answer.

This module checks LOCAL CANDIDATE consistency, not official publication.
Actual release version selection uses tools/release_version.py with current
official published-release evidence and local/remote tag collision checks.
An unshipped VERSION edit must never become that official baseline.

THE MARKER FOR LOCAL CANDIDATE HISTORY IS: VERSION's own git history, not a
tag or a CHANGELOG heading. Specifically, `last_release_commit()` is the
oldest commit in the run of commits (walking back from HEAD) whose VERSION
blob already equals HEAD's -- the commit that most recently set VERSION to
its current value. This needs no separate bookkeeping a session can forget
to update: it records candidate version changes, without asserting publication.
A git tag was considered and rejected: proposal 32's V-04 (tagging 1.0.0)
is a separate, deliberately rare act the lead performs on a green main, and
gating every ordinary PR's merge on a tag existing would block all of them
until that one act happens. A CHANGELOG heading was also considered and
rejected: it is a second, hand-written fact about the same commit VERSION
already names, free to drift from it the way the count-sha stamp drifted
from committed reality before `rulecheck` existed.

MISSING MARKER: when `VERSION` is not tracked in git at all (a checkout
that predates V-01, or the file was deleted without committing that),
there is no commit to diff from. `required_bump()` refuses -- state
"could not check" -- rather than reporting "none pending", which would
tell a session nothing is required when the truth is unknown.

THE BUMP RULE (CLAUDE-workflow.md, "Changing these rules" / the version
stamp section):
  MAJOR  -- breaks a project already following the rules: a tool removed
            or renamed, a declaration whose absence now fails a gate, a
            rule reversed. Declared explicitly, with a second marker line
            in the CHANGELOG entry, MAJOR_MARKER below -- never inferred
            from prose. A wrong guess here is the one mistake that matters:
            it would silently tell every adopting project a breaking change
            is safe to ignore.
  MINOR  -- any entry carrying MANDATORY_MARKER (rulecheck's own marker,
            proposal 21 S-09). A project must now do something it did not
            have to before, but nothing it already does breaks.
  PATCH  -- everything else that shipped: a new tool nobody must use, a
            fix, wording.
A MAJOR entry is also, in substance, a Standard change -- it asks an
adopting project to do something (stop relying on what broke) -- so it
should normally carry MANDATORY_MARKER too. This module does not require
that pairing; it only reads MAJOR_MARKER to decide the bump is MAJOR
rather than MINOR. Pairing them is what makes rulecheck's own mandatory
gate list the entry for adopting projects to implement.
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import re
from pathlib import Path
from typing import NamedTuple

ROOT = Path(os.environ.get("VERSION_CHECK_ROOT")
            or Path(__file__).resolve().parent.parent)
VERSION_FILE = ROOT / "VERSION"
CHANGELOG = ROOT / "CHANGELOG.md"

MANDATORY_MARKER = "**Standard change (mandatory):**"
MAJOR_MARKER = "**Breaking change (major):**"

_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_RANK = {"none": 0, "patch": 1, "minor": 2, "major": 3}


def _load_rulecheck():
    """bin/rulecheck as a module: its fenced-code-aware paragraph scanner
    (`_paragraphs`, `_fenced`) is reused here rather than re-derived, the
    same way bin/warmup and bin/conformance already load it (proposal 21,
    S-09; their own `_load_rulecheck()` docstrings say so)."""
    path = ROOT / "bin" / "rulecheck"
    loader = importlib.machinery.SourceFileLoader("rulecheck_for_version_check", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


RC = _load_rulecheck()


class Bump(NamedTuple):
    """required_bump()'s answer.

    state     ok · disagree · could not check
    required  none · patch · minor · major -- "" when state is "could not check"
    current   the semver VERSION holds at HEAD, or None when it cannot be read
    applied   the bump VERSION's current value represents over what it held
              before the last release -- none · patch · minor · major ·
              initial (no prior value to compare against) · invalid (VERSION
              went backwards or is not a valid semver)
    since     the commit VERSION was last set to its current value (the
              release marker), or None when it could not be found
    entries   the CHANGELOG headings whose requirement forced `required`,
              topmost (newest) first
    why       for "could not check", what could not be read"""
    state: str
    required: str
    current: str | None
    applied: str
    since: str | None
    entries: tuple
    why: str = ""


def parse_semver(text: str) -> tuple[int, int, int]:
    m = _SEMVER.fullmatch(text.strip())
    if not m:
        raise ValueError(f"{text!r} is not a valid semver (MAJOR.MINOR.PATCH, no leading zeros)")
    return tuple(int(g) for g in m.groups())  # type: ignore[return-value]


def read_version(rules=ROOT) -> str | None:
    """VERSION as committed at HEAD (not the working tree -- a `--check` in
    CI reads what actually landed, and an uncommitted edit is not yet a
    bump). None when it cannot be read at all."""
    out = RC._read(rules, "show", "--no-textconv", "HEAD:VERSION")
    return out.strip() if out else None


def _version_at(commit: str, rules=ROOT) -> str | None:
    out = RC._read(rules, "show", "--no-textconv", f"{commit}:VERSION")
    return out.strip() if out else None


def last_release_commit(rules=ROOT):
    """The oldest commit, walking back from HEAD, whose VERSION content
    already equals HEAD's -- see the module docstring. None when VERSION is
    not tracked in git at all (the missing-marker case)."""
    log = RC._read(rules, "log", "--format=%H", "--", "VERSION")
    if not log:
        return None
    commits = log.strip("\n").split("\n") if log.strip("\n") else []
    if not commits:
        return None
    current = _version_at(commits[0], rules)
    if current is None:
        return None
    since = commits[0]
    for c in commits[1:]:
        if _version_at(c, rules) != current:
            break
        since = c
    return since


def _added_changelog_lines(old_commit: str | None, rules=ROOT):
    """Lines CHANGELOG.md gained between `old_commit` (exclusive) and HEAD,
    the marker text they carry read the same fenced-code-aware way
    rulecheck reads a Standard change (a marker inside a fenced example is
    prose about the convention, not an instance of it). `old_commit=None`
    means "from the beginning" -- diff against the empty tree."""
    base = old_commit if old_commit else RC.git("hash-object", "-t", "tree", "/dev/null", cwd=rules)
    diff = RC._read(rules, "diff", "--no-color", "--no-ext-diff", "--no-textconv", "--text",
                     "-U0", f"{base}..HEAD", "--", "CHANGELOG.md")
    if diff is None:
        return None
    return RC._added_line_numbers(diff)


def required_bump(rules=ROOT) -> Bump:
    """What VERSION's next bump must be at least, per the CHANGELOG entries
    added since the last release, and whether the bump already applied (if
    any) was enough. Reads only."""
    current = read_version(rules)
    since = last_release_commit(rules)
    if since is None:
        return Bump("could not check", "", current, "", None, (),
                     "VERSION is not tracked in git -- no commit sets its current value, "
                     "so there is no way to tell what has shipped since a release. "
                     "Not guessing: commit VERSION first.")
    head = RC._read(rules, "show", "--no-textconv", "HEAD:CHANGELOG.md")
    if head is None:
        return Bump("could not check", "", current, "", since, (),
                     "CHANGELOG.md cannot be read at HEAD")

    if current is None:
        return Bump("could not check", "", None, "", since, (),
                     "VERSION cannot be read at HEAD")
    try:
        parse_semver(current)
    except ValueError as exc:
        return Bump("could not check", "", current, "", since, (), str(exc))

    # Two ranges, not one. Phase 1: has anything shipped strictly AFTER the
    # release took effect, with VERSION never touched again? That is an
    # unconditional disagreement -- there is no "applied" bump to weigh it
    # against, because nothing changed VERSION at all.
    needed_after, entries_after = _bump_for_added(since, head, rules)
    if needed_after is None:
        return Bump("could not check", "", current, "", since, (),
                     "CHANGELOG.md diff could not be computed")
    if needed_after != "none":
        return Bump("disagree", needed_after, current, "none", since, entries_after)

    # Phase 2: nothing shipped after the release, so what remains is whether
    # the release commit itself -- VERSION's change together with whatever
    # CHANGELOG entries it carried -- was a big enough bump for those entries.
    prior_commit = f"{since}~1"
    rc, _ = RC._run(rules, "rev-parse", "--verify", "--quiet", prior_commit)
    has_parent = rc == 0
    prior_version = _version_at(prior_commit, rules) if has_parent else None
    diff_base_release = prior_commit if has_parent else None
    needed_release, entries_release = _bump_for_added(diff_base_release, head, rules)
    if needed_release is None:
        return Bump("could not check", "", current, "", since, (),
                     "CHANGELOG.md diff could not be computed")

    if prior_version is None:
        # VERSION did not exist before this commit -- its starting value
        # (proposal 32, V-01: "starting at 0.9.0") is a human's choice, not
        # a bump computed from a prior semver that never existed. Exempt,
        # once, at the file's introduction; every release after this one
        # goes through the real comparison below.
        return Bump("ok", needed_release, current, "initial", since, entries_release)

    try:
        applied = semver_diff(prior_version, current)
    except ValueError as exc:
        return Bump("could not check", needed_release, current, "", since, entries_release, str(exc))

    ok = _RANK[applied] >= _RANK[needed_release]
    return Bump("ok" if ok else "disagree", needed_release, current, applied, since, entries_release)


def _paragraphs_for(text, markers):
    """rulecheck's `_paragraphs()`, generalized to start a paragraph at a
    line beginning with ANY of `markers`, not only rulecheck's own single
    MANDATORY_MARKER. Needed because a MAJOR entry carries two marker lines
    (MAJOR_MARKER, then MANDATORY_MARKER) that must both be found -- reusing
    `_paragraphs()` unmodified would silently drop the MAJOR_MARKER line,
    since it does not match rulecheck's own marker text. Fenced-code
    awareness (`RC._fenced`) is reused as-is."""
    if text is None:
        return []
    lines = [raw[:-1] if raw.endswith("\r") else raw for raw in text.split("\n")]
    fenced = RC._fenced(lines)
    out, heading_at, heading = [], 0, RC.NO_HEADING
    for i, line in enumerate(lines):
        if i in fenced:
            continue
        if line.startswith("## "):
            heading_at, heading = i + 1, (line[3:].strip(" \t") or "(untitled heading)")
            continue
        if any(line.startswith(m) for m in markers):
            j = i + 1
            while (j < len(lines) and j not in fenced and lines[j].strip(" \t")
                   and not lines[j].startswith("## ")
                   and not any(lines[j].startswith(m) for m in markers)):
                j += 1
            out.append(RC._Paragraph(heading_at, heading, i + 1, j, tuple(lines[i:j])))
    return out


def _bump_for_added(diff_base, head_text, rules=ROOT):
    """(needed, entries) for the CHANGELOG lines added between `diff_base`
    (exclusive; None means from the beginning) and HEAD, read the same
    fenced-code-aware way rulecheck reads a Standard change. (None, ()) when
    the diff could not be computed at all."""
    added = _added_changelog_lines(diff_base, rules)
    if added is None:
        return None, ()
    paragraphs = [p for p in _paragraphs_for(head_text, (MAJOR_MARKER, MANDATORY_MARKER))
                  if any(n in added for n in range(p.start, p.end + 1))]
    entries = RC._group(paragraphs)
    major = any(l.startswith(MAJOR_MARKER) for p in paragraphs for l in p.lines)
    mandatory = any(l.startswith(MANDATORY_MARKER) for p in paragraphs for l in p.lines)
    if major:
        needed = "major"
    elif mandatory:
        needed = "minor"
    elif added:
        needed = "patch"
    else:
        needed = "none"
    return needed, entries


def semver_diff(old: str, new: str) -> str:
    """The bump `new` represents over `old`: none · patch · minor · major,
    or raises ValueError if `new` is not >= `old` component-wise (a version
    that goes backwards is never a valid bump, whatever the CHANGELOG says)."""
    o, n = parse_semver(old), parse_semver(new)
    if n == o:
        return "none"
    if n < o:  # lexicographic tuple compare: a decrease at the highest
        # differing field is a decrease overall, whatever a lower field did
        raise ValueError(f"{new} is behind {old} -- not a bump")
    if n[0] != o[0]:
        return "major"
    if n[1] != o[1]:
        return "minor"
    return "patch"
