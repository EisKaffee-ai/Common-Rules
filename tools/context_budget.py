"""Measure the text Common Rules can add to an agent context.

This reports prompt/context footprint, not process RAM.  Both Codex and Claude
Code discover skills from small frontmatter records and load full instructions
on demand, so the measurements deliberately keep those surfaces separate.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path


def estimated_tokens(text: str) -> int:
    """A transparent, tokenizer-independent upper-level estimate."""
    return math.ceil(len(text.encode("utf-8")) / 4)


def _frontmatter(text: str, source: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{source}: missing YAML frontmatter")
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    for key in ("name", "description"):
        if not values.get(key):
            raise ValueError(f"{source}: missing {key} frontmatter")
    return values


def _record(path: str, text: str) -> dict[str, object]:
    size = len(text.encode("utf-8"))
    return {"path": path, "bytes": size, "estimated_tokens": estimated_tokens(text)}


def _measure(files: dict[str, str], source: str) -> dict[str, object]:
    skill_paths = sorted(path for path in files if path.startswith("skills/") and path.endswith("/SKILL.md"))
    skills = []
    discovery_parts = []
    for path in skill_paths:
        text = files[path]
        meta = _frontmatter(text, f"{source}:{path}")
        # OpenAI documents name, description and path as discovery context.
        # Claude documents names/descriptions; including the path here is the
        # conservative portable estimate.
        discovery = f"name: {meta['name']}\ndescription: {meta['description']}\npath: {path}\n"
        discovery_parts.append(discovery)
        skills.append({**_record(path, text), "name": meta["name"],
                       "description_bytes": len(meta["description"].encode("utf-8"))})

    reference_paths = sorted(path for path in files if path.startswith("skills/") and not path.endswith("/SKILL.md"))
    references = [_record(path, files[path]) for path in reference_paths]
    discovery_text = "".join(discovery_parts)
    skill_bytes = sum(int(row["bytes"]) for row in skills)
    reference_bytes = sum(int(row["bytes"]) for row in references)
    hook_config = files.get("hooks/hooks.json", "")
    return {
        "source": source,
        "method": "UTF-8 bytes divided by four, rounded up; an estimate, not tokenizer or RAM telemetry",
        "discovery": {
            "skills": len(skills),
            "bytes": len(discovery_text.encode("utf-8")),
            "estimated_tokens": estimated_tokens(discovery_text),
            "loads": "every request/session discovery",
        },
        "on_demand": {
            "skill_instruction_bytes": skill_bytes,
            "skill_instruction_estimated_tokens": math.ceil(skill_bytes / 4),
            "largest_skill": max(skills, key=lambda row: int(row["bytes"]), default=None),
            "skills": skills,
        },
        "references": {
            "bytes": reference_bytes,
            "estimated_tokens": math.ceil(reference_bytes / 4),
            "loads": "only when an invoked skill explicitly needs the reference",
            "files": references,
        },
        "full_skill_package_ceiling": {
            "bytes": skill_bytes + reference_bytes,
            "estimated_tokens": math.ceil((skill_bytes + reference_bytes) / 4),
            "loads": "never by default; comparison ceiling if every skill and reference were read",
        },
        "hooks": {
            "configuration_bytes_on_disk": len(hook_config.encode("utf-8")),
            "idle_context_tokens": 0,
            "loads": "hook output only; scripts and configuration run outside model context",
        },
    }


def measure_root(root: Path) -> dict[str, object]:
    files = {}
    for path in sorted((root / "skills").rglob("*")):
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8")
    hooks = root / "hooks" / "hooks.json"
    if hooks.is_file():
        files["hooks/hooks.json"] = hooks.read_text(encoding="utf-8")
    return _measure(files, str(root.resolve()))


def measure_git_ref(root: Path, ref: str) -> dict[str, object]:
    listing = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "--", "skills", "hooks/hooks.json"],
        cwd=root, text=True, capture_output=True, check=True,
    ).stdout.splitlines()
    files = {}
    for path in listing:
        result = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=root,
                                text=True, capture_output=True, check=True)
        files[path] = result.stdout
    return _measure(files, ref)


def markdown(report: dict[str, object], baseline: dict[str, object] | None = None) -> str:
    discovery = report["discovery"]
    on_demand = report["on_demand"]
    references = report["references"]
    ceiling = report["full_skill_package_ceiling"]
    largest = on_demand["largest_skill"] or {"path": "none", "estimated_tokens": 0}
    lines = [
        "# Common Rules context budget", "",
        "This measures prompt text, not process RAM. Token counts are reproducible estimates (UTF-8 bytes / 4).", "",
        "| Surface | When loaded | Bytes | Estimated tokens |", "|---|---|---:|---:|",
        f"| Skill discovery ({discovery['skills']} descriptions + paths) | Session/request discovery | {discovery['bytes']:,} | {discovery['estimated_tokens']:,} |",
        f"| All SKILL.md instructions | One skill at a time, on demand | {on_demand['skill_instruction_bytes']:,} | {on_demand['skill_instruction_estimated_tokens']:,} |",
        f"| Supporting references | Only when the invoked workflow needs them | {references['bytes']:,} | {references['estimated_tokens']:,} |",
        f"| Full package ceiling | Never loaded by default | {ceiling['bytes']:,} | {ceiling['estimated_tokens']:,} |",
        "| Hook configuration/scripts | Run outside model context | — | 0 while idle |", "",
        f"Largest on-demand skill: `{largest['path']}` (~{largest['estimated_tokens']:,} tokens).",
    ]
    if baseline:
        before = baseline["discovery"]["estimated_tokens"]
        after = discovery["estimated_tokens"]
        lines += ["", f"Discovery comparison with `{baseline['source']}`: {before:,} → {after:,} estimated tokens ({after - before:+,})."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="measure Common Rules context footprint")
    parser.add_argument("--project", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--compare-ref")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--max-discovery-tokens", type=int, default=650)
    args = parser.parse_args(argv)
    root = Path(args.project).resolve()
    report = measure_root(root)
    try:
        baseline = measure_git_ref(root, args.compare_ref) if args.compare_ref else None
    except subprocess.CalledProcessError:
        print(f"context-budget: cannot read git ref {args.compare_ref!r}", file=sys.stderr)
        return 2
    print(json.dumps({"current": report, "baseline": baseline}, indent=2) if args.json else markdown(report, baseline), end="")
    if args.check and report["discovery"]["estimated_tokens"] > args.max_discovery_tokens:
        print(f"context-budget: discovery estimate exceeds {args.max_discovery_tokens} tokens")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
