"""The project declaration: `.common-rules.json` (proposal 20, D9).

The standard used to assume every project reads HANDOFF.md first, keeps its
prohibitions under a HANDOFF heading containing "prohibition", and has one
test gate. The PhotoVault app does none of that -- CLAUDE.md is its entry
point, its safety rules sit under "## Hard safety rules", and it has a quick
gate and a merge gate -- so its warm card said "Prohibitions: none found" over
five NEVER rules, and its warm-up pointer contradicted its own read order. A
project now says where its entry points are, and the tools read that.

THE FILE -- `.common-rules.json` at the project root, beside
`.common-rules-version`. A JSON object. Every key is optional, and a key this
module does not know is ignored, because later proposals add keys.

  "read_order":   ["CLAUDE.md", "SPONSOR-CONSTRAINTS.md"]
      Files a session reads first, in order. Not empty.
      Default: ["HANDOFF.md", "docs/OPERATING-RULES.md"].
  "safety_rules": "CLAUDE.md#Hard safety rules"     (or a list of these)
      FILE#heading: the `## ` section of FILE whose heading text contains
      `heading`, case-insensitive. Its list items and bold-numbered lines are
      the card's prohibitions, verbatim. Split at the first "#".
      Default: "HANDOFF.md#prohibition".
  "gates":        {"quick": "<cmd>", "merge": "<cmd>"}
      merge is what bin/land runs before it lands; quick is the gate an agent
      runs. Each is a non-empty, one-line command, trimmed. Default: {}. With
      no "merge" key here, the first non-blank, non-comment line of
      `.common-rules-test` is gates.merge -- that file keeps working.
  "plan_check":   "<cmd>"   the project's own plan checker. Default: None.
  "plan_page":    "<cmd>"   the project's own page generator. Default: None.
  "proposal_series": ["../engine"]
      Sibling projects that share this project's proposal number series --
      the PhotoVault app and engine interleave theirs across two repos. Each
      entry is a one-line path relative to the project root that stays
      inside the project's parent folder (so `..` is allowed here, and only
      here), is not the project itself, exists, and holds docs/proposals.
      bin/new-proposal numbers across all of them. Default: [].
  "value_defaults": {"tracker": "high", "docs": "low"}
      Proposal 25, Z-03: the value (high|medium|low) an item takes from its
      `cluster` when it has no `value` of its own. Default: {}.
  "risk_paths":   {"restricted": ["finance_data/*"], "elevated": ["shared/*"]}
  "risk_always":  "restricted"
      Proposal 25, Z-04: path globs that set an item's risk class, and a
      floor no path lowers (common-rules declares restricted, D4). Read by
      tools/tracker/risk.py. Defaults: {} and None.
  "ruflo_namespace": "patterns"
      RF-01: the Ruflo memory namespace this project's existing memories use.
      A non-empty, one-line string. Read by tools/ruflo.py's namespace_for(),
      which every Ruflo-facing tool (bin/ruflo-item, bin/warmup, bin/
      conformance item 9) now shares -- --namespace, then $RUFLO_NAMESPACE,
      then this key, then the project directory's own name. Default: None.
  "staging_branch": "staging"
      O-08: the integration branch a reviewed branch lands on instead of
      main. A non-empty, one-line string -- a branch name, not a command.
      Read by bin/land: `land` merges onto this branch (creating it from
      main when it does not exist yet) and `land --advance-staging` runs
      the merge gate on it and fast-forwards main only on a green verdict.
      Default: None -- straight to main, exactly as before this key existed.

  "goal": {"outcome": "...", "constraints": ["..."],
           "verification": ["..."]}
      The project's compact, durable goal contract. The native `/goal` remains
      the execution control; this declaration is the repository-side summary
      that warm-up and the tracker can verify after a context switch. All
      three fields are required when the key is present. Default: None.
      No project under apps/ declares it yet; the switch is the sponsor's
      to throw.

  "integration": {"repository_id": "engine", "role": "business-logic",
      "requirements": ["docs/requirements"], "tracker": "docs/proposals",
      "issue_linking": "off", "skill_receipts": true,
      "issue_repository": "owner/repository",
      "issue_granularity": "proposal",
      "issue_sync_direction": "ledger-to-github",
      "workspace": {"id": "product", "role": "member", "hub": "docs"}}
      Proposal 36's calibrated repository identity and optional workspace
      membership. The three issue_* fields are an optional, indivisible
      proposal-level synchronization contract: the ledger is authoritative
      and only ledger-to-GitHub flow is supported. Paths remain inside this
      repository; machine checkout paths belong in the ignored
      `.common-rules/workspace.local.json`.

EVERY VALUE IS UNTRUSTED. A path is relative to the project root: an absolute
path, a `..` part, or a path that resolves (through a symlink) outside the
project is a problem, and no declared path outside the project is read or hashed
(the default HANDOFF.md, ledgers and checkpoint are read as before). Every
path and command is one line -- no control character -- because a command is
eval'd by land and every value can be printed on the card, where a line break
would run a second command or forge a line. And every string must be valid
UTF-8: JSON can carry a lone surrogate ("\\udc80") that no output can print,
so it is a named problem, never a traceback. No problem message quotes a value
that failed one of these checks.

WHO READS IT
  bin/land test_cmd()  gates.merge, else .common-rules-test, else a guess from
                       the tree. It is bash and must stay self-contained, so it
                       carries its own few lines of json reading, run as
                       `python3 -I` so a project's own json.py cannot answer for
                       the standard library. test_command() below is its twin,
                       and tests pin the two equal.
  bin/warmup           read_order, safety_rules, gates, problems(), inside().
  tools/migrate.py     read_order, for the pointer it writes into CLAUDE.md --
                       and it writes nothing while problems() has anything to say.
  bin/new-proposal     proposal_series(), to number across sibling projects; it
                       refuses to run while the series has a problem.
  bin/land             staging_branch, read by its own self-contained bash
                       JSON reader (test_cmd()'s twin) so land stays a single
                       file; staging_target() above is that reader's python
                       twin, for tests and other callers.

A BROKEN DECLARATION. load() never raises: a file that is not valid JSON, or
not an object, gives the defaults, and a value that fails a check leaves that
key's default standing. problems() names each one, and warm-up's --check
fails on them.

A gate is different, because running the wrong one is worse than running
none. land -- and test_command() -- refuse with `false  # <why>` when the file
is not valid JSON, is not an object, has "gates" that is not an object, or
declares a "merge" or "quick" gate that is not a non-empty string, is not
valid UTF-8, or is not one line (lead rulings on V-00, 14 Sep). Nothing falls
back to .common-rules-test or the guess: that would silently run a gate nobody
declared. load() does not fill in a declared but broken gates.merge either. To
run the merge gate, ask test_command(), never load()["gates"]["merge"] -- only
the first carries the refusal.

  load(project)         -> dict       the declaration merged over the defaults
  declared(project)     -> dict       only the keys the file validly declares
  problems(project)     -> list[str]  what is wrong with the declaration
  test_command(project) -> str        what bin/land's test_cmd() answers
  inside(project, rel)  -> bool       rel resolves inside the project
  proposal_series(project) -> ([(rel, path)], [problem])   usable siblings, or the problems
"""
from __future__ import annotations

import copy
import datetime
import glob
import json
import os
import re
from pathlib import Path, PurePosixPath

FILE = ".common-rules.json"
TEST_FILE = ".common-rules-test"
GATES = ("merge", "quick")  # land checks them in this order
COMMANDS = ("plan_check", "plan_page")

DEFAULTS: dict = {
    "read_order": ["HANDOFF.md", "docs/OPERATING-RULES.md"],
    "safety_rules": "HANDOFF.md#prohibition",
    "gates": {},
    "plan_check": None,
    "plan_page": None,
    "proposal_series": [],
    "value_defaults": {},
    "risk_paths": {},
    "risk_always": None,
    "ruflo_namespace": None,
    "staging_branch": None,
    "goal": None,
    "integration": None,
}

VALUES = ("high", "medium", "low")  # tools/tracker/ledger.py VALUES, proposal 25
RISKS = ("standard", "elevated", "restricted")  # tools/tracker/ledger.py RISKS
RISK_PATH_CLASSES = ("restricted", "elevated")
INTEGRATION_ROLES = ("business-logic", "interface", "documentation", "assets", "operations", "combined")
ISSUE_LINKING = ("off", "manual", "one-way")
ISSUE_GRANULARITY = ("proposal",)
ISSUE_SYNC_DIRECTIONS = ("ledger-to-github",)
WORKSPACE_ROLES = ("hub", "member")

INVALID, NOT_OBJECT = "invalid", "not an object"


def _raw(project: Path) -> tuple[dict | None, str | None]:
    """(the parsed object, None) · (None, INVALID | NOT_OBJECT) · (None, None) when there is no file."""
    path = Path(project) / FILE
    if not path.is_file():
        return None, None
    try:
        data = json.loads(path.read_bytes())
    except (OSError, ValueError):  # UnicodeDecodeError is a ValueError
        return None, INVALID
    if not isinstance(data, dict):
        return None, NOT_OBJECT
    return data, None


def _utf8(s: str) -> bool:
    try:
        s.encode("utf-8")
    except UnicodeEncodeError:  # a lone surrogate
        return False
    return True


def _one_line(s: str) -> bool:
    """No control character (C0, DEL, C1). bin/land's test_cmd() uses the same test."""
    return not any(ord(c) < 32 or 127 <= ord(c) < 160 for c in s)


def _goal_problem(value) -> str | None:
    """Validate the small project-side mirror of a native `/goal`.

    The mirror is deliberately optional: projects that rely only on the
    host's goal UI keep the old contract. When present, it must be useful to a
    cold session without importing the whole chat transcript.
    """
    if not isinstance(value, dict):
        return f"{FILE}: goal must be an object with outcome, constraints and verification"
    outcome = value.get("outcome")
    if not isinstance(outcome, str) or not outcome.strip() or not _utf8(outcome) or not _one_line(outcome):
        return f"{FILE}: goal.outcome must be non-empty, valid UTF-8 and one line"
    for key in ("constraints", "verification"):
        rows = value.get(key)
        if not isinstance(rows, list) or not rows:
            return f"{FILE}: goal.{key} must be a non-empty list of one-line strings"
        for row in rows:
            if not isinstance(row, str) or not row.strip() or not _utf8(row) or not _one_line(row):
                return f"{FILE}: goal.{key} entries must be non-empty, valid UTF-8 and one line"
    if "updated" in value:
        updated = value["updated"]
        if not isinstance(updated, str) or not _utf8(updated) or not _one_line(updated):
            return f"{FILE}: goal.updated must be a one-line date"
    return None


def _integration_problems(value) -> list[str]:
    if not isinstance(value, dict):
        return [f"{FILE}: integration must be an object"]
    bad = []
    rid = value.get("repository_id")
    if not isinstance(rid, str) or not rid.strip() or not _utf8(rid) or not _one_line(rid):
        bad.append(f"{FILE}: integration.repository_id must be non-empty, valid UTF-8 and one line")
    if value.get("role") not in INTEGRATION_ROLES:
        bad.append(f"{FILE}: integration.role must be one of {', '.join(INTEGRATION_ROLES)}")
    requirements = value.get("requirements")
    if not isinstance(requirements, list) or not requirements or not all(isinstance(v, str) for v in requirements):
        bad.append(f"{FILE}: integration.requirements must be a non-empty list of repository paths")
    else:
        bad.extend(filter(None, (_path_problem("integration.requirements", v) for v in requirements)))
    tracker = value.get("tracker")
    if not isinstance(tracker, str):
        bad.append(f"{FILE}: integration.tracker must be a repository path")
    else:
        why = _path_problem("integration.tracker", tracker)
        if why: bad.append(why)
    if value.get("issue_linking") not in ISSUE_LINKING:
        bad.append(f"{FILE}: integration.issue_linking must be one of {', '.join(ISSUE_LINKING)}")
    issue_keys = ("issue_repository", "issue_granularity", "issue_sync_direction")
    if any(key in value for key in issue_keys):
        if not all(key in value for key in issue_keys):
            bad.append(f"{FILE}: proposal issue synchronization requires issue_repository, "
                       "issue_granularity and issue_sync_direction together")
        repository = value.get("issue_repository")
        if (not isinstance(repository, str) or not _utf8(repository) or not _one_line(repository)
                or re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is None):
            bad.append(f"{FILE}: integration.issue_repository must be an owner/repository name")
        if value.get("issue_granularity") not in ISSUE_GRANULARITY:
            bad.append(f"{FILE}: integration.issue_granularity must be proposal")
        if value.get("issue_sync_direction") not in ISSUE_SYNC_DIRECTIONS:
            bad.append(f"{FILE}: integration.issue_sync_direction must be ledger-to-github")
        if value.get("issue_linking") != "one-way":
            bad.append(f"{FILE}: proposal issue synchronization requires integration.issue_linking one-way")
    if value.get("skill_receipts") is not True:
        bad.append(f"{FILE}: integration.skill_receipts must be true")
    workspace = value.get("workspace")
    if workspace is not None:
        if not isinstance(workspace, dict):
            bad.append(f"{FILE}: integration.workspace must be an object")
        else:
            if not isinstance(workspace.get("id"), str) or not workspace.get("id", "").strip():
                bad.append(f"{FILE}: integration.workspace.id must be a non-empty string")
            if workspace.get("role") not in WORKSPACE_ROLES:
                bad.append(f"{FILE}: integration.workspace.role must be hub or member")
            if workspace.get("role") == "member" and not isinstance(workspace.get("hub"), str):
                bad.append(f"{FILE}: a workspace member must name its hub repository id")
    return bad


def _relative(rel: str) -> bool:
    p = PurePosixPath(rel)
    return not p.is_absolute() and ".." not in p.parts


def inside(project: Path, rel: str) -> bool:
    """rel, joined to the project root and resolved through any symlink, is still inside it."""
    root = Path(project).resolve()
    try:
        return (root / rel).resolve().is_relative_to(root)
    except (OSError, ValueError, RuntimeError):
        return False


def _path_problem(key: str, value: str) -> str | None:
    if not value.strip():
        return f"{FILE}: {key} entries must be file paths, relative to the project root"
    if not _utf8(value):
        return f"{FILE}: a {key} entry is not valid UTF-8"
    if not _one_line(value):
        return f"{FILE}: a {key} entry must be one line"
    if not _relative(value):
        return f"{FILE}: {key} entry {value!r} is outside the project -- paths are relative to the root"
    return None


# Bidi controls, invisible characters and the Unicode line and paragraph
# separators: none of them belongs in a path, and each can disguise one.
_REORDER_OR_HIDE_SERIES = frozenset("\u061c\u200b\u200e\u200f\u2028\u2029\u202a\u202b\u202c\u202d\u202e"
                                    "\u2060\u2061\u2062\u2063\u2064\u2066\u2067\u2068\u2069\ufeff")


def _series_problem(value: str) -> str | None:
    """What is wrong with one proposal_series entry on its face, or None.
    Unlike every other path here, `..` is allowed: a series names siblings."""
    if not value.strip():
        return f"{FILE}: proposal_series entries must be sibling project paths, relative to the project root"
    if not _utf8(value):
        return f"{FILE}: a proposal_series entry is not valid UTF-8"
    if not _one_line(value):
        return f"{FILE}: a proposal_series entry must be one line"
    if any(ch in _REORDER_OR_HIDE_SERIES for ch in value):
        return f"{FILE}: a proposal_series entry carries an invisible, bidi or line-separator character"
    if PurePosixPath(value).is_absolute():
        return f"{FILE}: proposal_series entry {value!r} is absolute -- paths are relative to the project root"
    return None


def _series_place(project: Path, rel: str) -> tuple[Path | None, str | None]:
    """(the sibling's resolved root, None), or (None, why it cannot be used)."""
    root = Path(project).resolve()
    parent = root.parent
    outside = (f"{FILE}: proposal_series entry {rel!r} is outside the parent folder of the project "
               f"-- a series names sibling projects")
    lexical = Path(os.path.normpath(root / rel))
    if not lexical.is_relative_to(parent) or lexical == parent:
        return None, outside
    try:
        target = (root / rel).resolve()
    except (OSError, RuntimeError):
        return None, f"{FILE}: proposal_series entry {rel!r} cannot be resolved"
    if target == root:
        return None, f"{FILE}: proposal_series entry {rel!r} names the project itself"
    if not target.is_relative_to(parent) or target == parent:
        return None, outside
    if target.is_relative_to(root) or target.parent != parent:
        return None, (f"{FILE}: proposal_series entry {rel!r} is a folder inside a project, not a sibling "
                      "-- a series names ../<project>")
    if not target.is_dir():
        return None, f"{FILE}: proposal_series names {rel}, which does not exist"
    if not (target / "docs" / "proposals").is_dir():
        return None, f"{FILE}: proposal_series names {rel}, which holds no docs/proposals"
    return target, None


def _safety_problem(spec: str) -> str | None:
    if not _utf8(spec):
        return f"{FILE}: a safety_rules entry is not valid UTF-8"
    if not _one_line(spec):
        return f"{FILE}: a safety_rules entry must be one line"
    rel, sep, _heading = spec.partition("#")
    if sep and rel.strip() and not _relative(rel.strip()):
        return f"{FILE}: safety_rules entry {spec!r} is outside the project -- paths are relative to the root"
    return None


def _gate_problem(value) -> str | None:
    """Why land cannot run this gate, worded as bin/land's test_cmd() words it; None when it can."""
    if not isinstance(value, str) or not value.strip():
        return "is not a string"
    if not _utf8(value):
        return "is not valid UTF-8"
    if not _one_line(value.strip()):
        return "must be one line"
    return None


def _gate_refusal(data: dict | None) -> str | None:
    """Why land cannot use the gates this object declares, or None. Word for
    word what bin/land's test_cmd() prints after `false  # .common-rules.json `."""
    if data is None or "gates" not in data:
        return None
    gates = data["gates"]
    if not isinstance(gates, dict):
        return "gates is not an object"
    for name in GATES:
        if name in gates:
            why = _gate_problem(gates[name])
            if why:
                return f"gates.{name} {why}"
    return None


def _command(key: str, value) -> tuple[str | None, str | None]:
    """(the command, or None when not declared; the problem, or None)."""
    if value is None:
        return None, None
    if not isinstance(value, str):
        return None, f"{FILE}: {key} must be a command string"
    if not _utf8(value):
        return None, f"{FILE}: {key} is not valid UTF-8"
    s = value.strip()
    if not _one_line(s):
        return None, f"{FILE}: {key} must be one line"
    return (s or None), None


def _unique(items) -> list[str]:
    return list(dict.fromkeys(i for i in items if i))


def _checked(data: dict) -> tuple[dict, list[str]]:
    ok: dict = {}
    bad: list[str] = []
    if "read_order" in data:
        v = data["read_order"]
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            bad.append(f"{FILE}: read_order must be a list of file paths, relative to the project root")
        elif not v:
            bad.append(f"{FILE}: read_order is empty -- name at least one file, or leave read_order out "
                       f"for the default")
        else:
            why = _unique(_path_problem("read_order", x) for x in v)
            if why:
                bad.extend(why)
            else:
                ok["read_order"] = list(v)
    if "safety_rules" in data:
        v = data["safety_rules"]
        if isinstance(v, str):
            specs = [v]
        elif isinstance(v, list) and all(isinstance(x, str) for x in v):
            specs = v
        else:
            specs = None
        if specs is None:
            bad.append(f'{FILE}: safety_rules must be "FILE#heading", or a list of them')
        else:
            why = _unique(_safety_problem(s) for s in specs)
            if why:
                bad.extend(why)
            else:
                ok["safety_rules"] = copy.deepcopy(v)
    if "gates" in data:
        v = data["gates"]
        if not isinstance(v, dict):
            bad.append(f'{FILE}: gates must be an object, like {{"quick": "<cmd>", "merge": "<cmd>"}} '
                       f"-- land refuses until it is")
        else:
            gates = {}
            for name in GATES:
                if name not in v:
                    continue
                why = _gate_problem(v[name])
                if why:
                    bad.append(f"{FILE}: gates.{name} {why} -- a gate is a non-empty, one-line command; "
                               f"land refuses until it is")
                else:
                    gates[name] = v[name].strip()
            ok["gates"] = gates
    if "proposal_series" in data:
        v = data["proposal_series"]
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            bad.append(f"{FILE}: proposal_series must be a list of sibling project paths, "
                       f"relative to the project root")
        else:
            why = _unique(_series_problem(x) for x in v)
            if why:
                bad.extend(why)
            else:
                ok["proposal_series"] = list(v)
    if "value_defaults" in data:
        v = data["value_defaults"]
        if not isinstance(v, dict):
            bad.append(f'{FILE}: value_defaults must be an object, like {{"tracker": "high"}}')
        elif not all(isinstance(k, str) and k.strip() and _utf8(k) and _one_line(k) for k in v):
            bad.append(f"{FILE}: value_defaults names must be surface names, one line of text")
        elif not all(x in VALUES for x in v.values()):
            bad.append(f"{FILE}: value_defaults values must be one of {', '.join(VALUES)}")
        else:
            ok["value_defaults"] = dict(v)
    if "risk_paths" in data:
        v = data["risk_paths"]
        if not isinstance(v, dict) or not set(v) <= set(RISK_PATH_CLASSES):
            bad.append(f'{FILE}: risk_paths must be an object with "restricted" and/or "elevated" glob lists')
        elif not all(isinstance(g, list) and all(isinstance(x, str) and x.strip() and _utf8(x) and _one_line(x)
                                                 for x in g) for g in v.values()):
            bad.append(f"{FILE}: risk_paths entries must be lists of path globs, one line each")
        else:
            ok["risk_paths"] = {k: list(g) for k, g in v.items()}
    if "risk_always" in data:
        if data["risk_always"] in RISKS:
            ok["risk_always"] = data["risk_always"]
        else:
            bad.append(f"{FILE}: risk_always must be one of {', '.join(RISKS)}")
    for key in COMMANDS:
        if key in data:
            cmd, why = _command(key, data[key])
            if why:
                bad.append(why)
            elif cmd:
                ok[key] = cmd
    if "ruflo_namespace" in data:
        v = data["ruflo_namespace"]
        if not isinstance(v, str) or not v.strip():
            bad.append(f"{FILE}: ruflo_namespace must be a non-empty string")
        elif not _utf8(v):
            bad.append(f"{FILE}: ruflo_namespace is not valid UTF-8")
        elif not _one_line(v.strip()):
            bad.append(f"{FILE}: ruflo_namespace must be one line")
        else:
            ok["ruflo_namespace"] = v.strip()
    if "staging_branch" in data:
        v = data["staging_branch"]
        if not isinstance(v, str) or not v.strip():
            bad.append(f"{FILE}: staging_branch must be a non-empty string")
        elif not _utf8(v):
            bad.append(f"{FILE}: staging_branch is not valid UTF-8")
        elif not _one_line(v.strip()):
            bad.append(f"{FILE}: staging_branch must be one line")
        else:
            ok["staging_branch"] = v.strip()
    if "history_since" in data:
        # The tracker's progress graph starts here rather than at the first
        # commit. Loom asked for it on 2026-09-25 after consolidating 25
        # ledgers into two: the old counts (299 done, then 28) made the graph
        # read as a collapse, and the sponsor said "reset the old data from
        # the graph". A date, never a deletion: history stays in git; the page
        # just starts its story where the project did.
        v = data["history_since"]
        try:
            if not isinstance(v, str):
                raise ValueError
            # A date, or an ISO timestamp when the story starts mid-day
            # (Loom, 2026-09-26: the hourly chart still showed the old counts).
            (datetime.datetime if "T" in v else datetime.date).fromisoformat(v)
            ok["history_since"] = v
        except ValueError:
            bad.append(f'{FILE}: history_since must be a YYYY-MM-DD date or an ISO timestamp, got {v!r}')
    if "goal" in data:
        why = _goal_problem(data["goal"])
        if why:
            bad.append(why)
        else:
            ok["goal"] = copy.deepcopy(data["goal"])
    if "integration" in data:
        why = _integration_problems(data["integration"])
        if why:
            bad.extend(why)
        else:
            ok["integration"] = copy.deepcopy(data["integration"])
    return ok, bad


def declared(project: Path) -> dict:
    """Only what the file validly declares; {} when there is no usable file."""
    data, _why = _raw(project)
    return _checked(data)[0] if data is not None else {}


def test_file_command(project: Path) -> str | None:
    """The first non-blank, non-comment line of .common-rules-test, stripped."""
    path = Path(project) / TEST_FILE
    if not path.is_file():
        return None
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return None


def _declares_merge(data: dict | None) -> bool:
    """The file speaks for gates.merge -- usable or not -- so nothing fills it in."""
    if data is None or "gates" not in data:
        return False
    return not isinstance(data["gates"], dict) or "merge" in data["gates"]


def load(project: Path) -> dict:
    d = copy.deepcopy(DEFAULTS)
    d.update(declared(project))
    data, _why = _raw(project)
    if "merge" not in d["gates"] and not _declares_merge(data):
        merge = test_file_command(project)
        if merge:
            d["gates"]["merge"] = merge
    return d


def safety_sources(value) -> list[tuple[str, str]]:
    """(file, heading) for each well-formed FILE#heading in a safety_rules value."""
    specs = [value] if isinstance(value, str) else [s for s in (value or []) if isinstance(s, str)]
    out = []
    for spec in specs:
        rel, sep, heading = spec.partition("#")
        if sep and rel.strip() and heading.strip():
            out.append((rel.strip(), heading.strip()))
    return out


def problems(project: Path) -> list[str]:
    data, why = _raw(project)
    if why == INVALID:
        return [f"{FILE} is not valid JSON -- fix it; until then the defaults apply and land refuses"]
    if why == NOT_OBJECT:
        return [f"{FILE} is not a JSON object -- fix it; until then the defaults apply and land refuses"]
    if data is None:
        return []
    ok, bad = _checked(data)
    root = Path(project)
    outside = "resolves outside the project -- paths are relative to the root"
    for rel in ok.get("read_order", []):
        if not inside(root, rel):
            bad.append(f"{FILE}: read_order entry {rel!r} {outside}")
        elif not (root / rel).is_file():
            bad.append(f"{FILE}: read_order names {rel}, which does not exist")
    if "safety_rules" in ok:
        v = ok["safety_rules"]
        for spec in ([v] if isinstance(v, str) else v):
            found = safety_sources(spec)
            if not found:
                bad.append(f"{FILE}: safety_rules entry {spec!r} is not FILE#heading")
            elif not inside(root, found[0][0]):
                bad.append(f"{FILE}: safety_rules entry {spec!r} {outside}")
            elif not (root / found[0][0]).is_file():
                bad.append(f"{FILE}: safety_rules names {found[0][0]}, which does not exist")
    for rel in ok.get("proposal_series", []):
        _target, why = _series_place(root, rel)
        if why:
            bad.append(why)
    integration = ok.get("integration")
    if integration:
        for rel in [*integration["requirements"], integration["tracker"]]:
            if not inside(root, rel):
                bad.append(f"{FILE}: integration path {rel!r} {outside}")
            elif not (root / rel).exists():
                bad.append(f"{FILE}: integration path {rel} does not exist")
    return _unique(bad)


def proposal_series(project: Path) -> tuple[list[tuple[str, Path]], list[str]]:
    """The declared siblings as (entry, resolved root), and every problem with
    them. While there is any problem the list is empty: numbering across part
    of a series is how a collision gets made, so a caller refuses instead."""
    data, why = _raw(project)
    if why == INVALID:
        return [], [f"{FILE} is not valid JSON -- its proposal_series cannot be read"]
    if why == NOT_OBJECT:
        return [], [f"{FILE} is not a JSON object -- its proposal_series cannot be read"]
    if data is None or "proposal_series" not in data:
        return [], []
    ok, bad = _checked({"proposal_series": data["proposal_series"]})
    if bad:
        return [], bad
    roots, problems, seen = [], [], set()
    for rel in ok["proposal_series"]:
        target, why = _series_place(project, rel)
        if why:
            problems.append(why)
        elif target not in seen:
            seen.add(target)
            roots.append((rel, target))
    return ([] if problems else roots), problems


def test_command(project: Path) -> str:
    """bin/land's test_cmd(), in the same order: gates.merge from
    .common-rules.json, then .common-rules-test, then the guess from the tree.
    A declaration or a declared gate land cannot use is a refusal, never a
    fall-back."""
    root = Path(project)
    data, why = _raw(root)
    if why == INVALID:
        return f"false  # {FILE} is not valid JSON"
    if why == NOT_OBJECT:
        return f"false  # {FILE} is not a JSON object"
    refusal = _gate_refusal(data)
    if refusal:
        return f"false  # {FILE} {refusal}"
    if _declares_merge(data):
        return data["gates"]["merge"].strip()
    merge = test_file_command(root)
    if merge:
        return merge
    if (root / "tests").is_dir() and glob.glob(str(root / "tests" / "*.py")):
        return "python3 -m unittest discover -s tests -q"
    pkg = root / "package.json"
    if pkg.is_file() and '"test"' in pkg.read_text(errors="replace"):
        return "npm test --silent"
    return ""


def staging_target(project: Path) -> str | None:
    """bin/land's staging_branch() twin: the declared staging_branch, or None
    when it is not declared or not usable -- in which case land goes straight
    to main, exactly as it did before this key existed."""
    return declared(project).get("staging_branch")
