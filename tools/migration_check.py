"""Prove a non-destructive Emberline-to-Common-Rules Git migration."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

DEFAULT_REFS = ("upstream/main", "upstream/w10-measured", "local-source/w10-measured")


def _git(root: Path, *args: str) -> tuple[int, str]:
    run = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True)
    return run.returncode, run.stdout.strip() if run.returncode == 0 else run.stderr.strip()


def _exists(root: Path, ref: str) -> bool:
    return _git(root, "rev-parse", "--verify", "--quiet", ref)[0] == 0


def _files(root: Path, ref: str) -> set[str] | None:
    code, out = _git(root, "ls-tree", "-r", "--name-only", ref)
    return set(out.splitlines()) if code == 0 else None


def local_check(root: Path, candidate: str, required: list[str], source_files_ref: str) -> tuple[int, list[str]]:
    findings, receipts = [], []
    if not _exists(root, candidate):
        return 2, [f"candidate {candidate} does not resolve"]
    for ref in required:
        if not _exists(root, ref):
            findings.append(f"required history {ref} does not resolve")
            continue
        if _git(root, "merge-base", "--is-ancestor", ref, candidate)[0] != 0:
            findings.append(f"{ref} is not an ancestor of {candidate}")
    if not findings:
        receipts.append(f"{len(required)} required histories are ancestors of {candidate}")
    source, target = _files(root, source_files_ref), _files(root, candidate)
    if source is None:
        return 2, [f"cannot read source tree {source_files_ref}"]
    if target is None:
        return 2, [f"cannot read candidate tree {candidate}"]
    missing = sorted(source - target)
    findings.extend(f"{name} is missing from {candidate}" for name in missing)
    if not missing:
        receipts.append(f"all {len(source)} source files preserved from {source_files_ref}")
    return (1 if findings else 0), findings or receipts


def _ls_remote(root: Path, remote: str) -> tuple[dict[str, str] | None, str | None]:
    code, out = _git(root, "ls-remote", "--heads", "--tags", remote)
    if code:
        return None, out or f"cannot read remote {remote}"
    refs = {}
    for line in out.splitlines():
        obj, sep, ref = line.partition("\t")
        if sep: refs[ref] = obj
    return refs, None


def remote_check(root: Path, source: str, destination: str, release_branch: str,
                 candidate: str) -> tuple[int, list[str]]:
    src, why = _ls_remote(root, source)
    if why: return 2, [why]
    dst, why = _ls_remote(root, destination)
    if why: return 2, [why]
    assert src is not None and dst is not None
    findings = []
    for ref, obj in sorted(src.items()):
        if ref.startswith("refs/tags/") and dst.get(ref) != obj:
            findings.append(f"destination is missing source tag {ref[len('refs/tags/'):]}")
    for name in ("main", "w10-measured"):
        source_ref, destination_ref = f"refs/heads/{name}", f"refs/heads/{name}"
        if source_ref in src and destination_ref not in dst:
            findings.append(f"destination is missing source branch {name}")
    code, candidate_obj = _git(root, "rev-parse", candidate)
    remote_release = dst.get(f"refs/heads/{release_branch}")
    if code or remote_release != candidate_obj:
        findings.append(f"destination branch {release_branch} is not at {candidate}")
    source_tags = sum(1 for ref in src if ref.startswith("refs/tags/") and not ref.endswith("^{}"))
    receipts = [f"all {source_tags} source tags preserved on {destination}",
                f"release branch {release_branch} matches {candidate}"]
    return (1 if findings else 0), findings or receipts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="migration-check")
    ap.add_argument("--project", default=".")
    ap.add_argument("--candidate", default="HEAD")
    ap.add_argument("--required-ref", action="append", dest="required")
    ap.add_argument("--source-files-ref", default="upstream/main")
    ap.add_argument("--remote", action="store_true")
    ap.add_argument("--source-remote", default="upstream")
    ap.add_argument("--destination-remote", default="origin")
    ap.add_argument("--release-branch", default="codex/calibrated-setup-release")
    args = ap.parse_args(argv)
    root = Path(args.project).resolve()
    code, lines = local_check(root, args.candidate, args.required or list(DEFAULT_REFS), args.source_files_ref)
    if code == 0 and args.remote:
        code, remote_lines = remote_check(root, args.source_remote, args.destination_remote,
                                          args.release_branch, args.candidate)
        lines.extend(remote_lines)
    for line in lines: print(("✓ " if code == 0 else "✗ ") + line)
    return code
