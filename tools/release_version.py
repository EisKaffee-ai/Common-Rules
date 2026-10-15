"""Offline official-release preflight; supplied evidence is not authentication.

No VERSION, Git, network, package discovery or mutation participates. Callers
must supply all GitHub release-list pages and both tag inventories. Prefixes
are all known aliases for one component; the first is its proposed tag spelling.
Each evidence file must be a regular file of at most 8 MiB; leaf symlinks,
special files and files changing during the read are refused.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
import re
import stat
import sys
from urllib.parse import quote


class EvidenceError(ValueError):
    """The supplied snapshot cannot establish a safe release proposal."""


SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?", re.ASCII)
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", re.ASCII)
TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})")
MAX_EVIDENCE_BYTES = 8 * 1024 * 1024


def _timestamp(value):
    if not isinstance(value, str) or not TIMESTAMP.fullmatch(value):
        raise EvidenceError("stable release requires a valid published_at timestamp with timezone")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise EvidenceError("invalid published_at timestamp") from error


def _tag(value):
    if not isinstance(value, str) or not value or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in value):
        raise EvidenceError("tag evidence must contain nonempty tag strings without whitespace/control characters")
    # Bare names only: accepting refs/tags/* or peeled ls-remote lines here
    # would conceal collisions with the proposed bare tag. Match Git's ref
    # constraints without invoking Git or silently rewriting supplied evidence.
    if (value.startswith("refs/") or value == "@" or value.endswith(".")
            or ".." in value or "@{" in value
            or any(c in value for c in "~^:?*[\\")
            or any(not part or part.startswith(".") or part.endswith(".lock")
                   for part in value.split("/"))):
        raise EvidenceError("tag evidence must use valid bare Git tag names, never refs/* or peeled lines")
    return value


def propose(releases, tags, *, repository, prefixes, bump, source_url,
            complete_evidence=False):
    """Return a deterministic proposal or raise EvidenceError; never perform IO.

    releases is the concatenation of every GitHub API release-list page.
    tags is exactly {"local": [tag, ...], "remote": [tag, ...]} (bare tag
    names, not refs/ prefixes or peeled ^{} lines). complete_evidence attests
    all pages, all component prefix aliases and both complete inventories.
    This attestation cannot independently prove completeness or authenticity.
    """
    if complete_evidence is not True:
        raise EvidenceError("explicit --complete-evidence acknowledgement required")
    if not isinstance(repository, str) or not REPOSITORY.fullmatch(repository) or any(part in (".", "..") for part in repository.split("/")):
        raise EvidenceError("repository must be OWNER/REPO")
    if source_url != f"https://api.github.com/repos/{repository}/releases":
        raise EvidenceError("source URL must name this repository's GitHub API releases endpoint")
    if not isinstance(prefixes, (list, tuple)) or not prefixes or any(not isinstance(p, str) or any(c.isspace() or ord(c) < 32 for c in p) for p in prefixes) or len(set(prefixes)) != len(prefixes):
        raise EvidenceError("supply distinct allowed tag prefixes for every component alias")
    for prefix in prefixes:
        _tag(prefix + "0.0.0")
    if bump not in ("patch", "minor", "major"):
        raise EvidenceError("bump must be patch, minor or major")
    if not isinstance(releases, list):
        raise EvidenceError("release evidence must be a JSON array concatenating all API pages")
    if not isinstance(tags, dict) or set(tags) != {"local", "remote"}:
        raise EvidenceError("tag evidence must contain exactly local AND remote inventories")
    for inventory in tags.values():
        if not isinstance(inventory, list):
            raise EvidenceError("each tag inventory must be an array")
        for value in inventory:
            _tag(value)
    stable = []
    identities = {}
    for row in releases:
        if not isinstance(row, dict):
            raise EvidenceError("every release record must be an object")
        tag = _tag(row.get("tag_name"))
        if type(row.get("draft")) is not bool or type(row.get("prerelease")) is not bool:
            raise EvidenceError("every release requires boolean draft and prerelease fields")
        if row["draft"] or row["prerelease"]:
            continue
        _timestamp(row.get("published_at"))
        expected_url = f"https://github.com/{repository}/releases/tag/{quote(tag, safe='')}"
        # GitHub permits unescaped slashes in the tag path as well.
        unescaped_url = f"https://github.com/{repository}/releases/tag/{quote(tag, safe='/')}"
        # A literal + is a valid path character, not query-string space.
        metadata_url = f"https://github.com/{repository}/releases/tag/{quote(tag, safe='/+')}"
        if row.get("html_url") not in (expected_url, unescaped_url, metadata_url):
            raise EvidenceError("stable release URL must match repository and exact tag")
        identity = (row["published_at"], row["html_url"])
        if tag in identities and identities[tag] != identity:
            raise EvidenceError("ambiguous duplicate release identity")
        identities[tag] = identity
        versions = set()
        matched = False
        for prefix in prefixes:
            if tag.startswith(prefix):
                matched = True
                parsed = SEMVER.fullmatch(tag[len(prefix):])
                if parsed:
                    versions.add(tuple(map(int, parsed.groups())))
        if len(versions) > 1:
            raise EvidenceError("ambiguous component tag prefixes")
        if not versions:
            if matched:
                raise EvidenceError("component stable tag must contain MAJOR.MINOR.PATCH SemVer with optional build metadata")
            continue
        stable.append((versions.pop(), tag, row["html_url"]))
    if not stable:
        raise EvidenceError("no officially published stable component release in supplied evidence")
    # Build metadata has no SemVer precedence. Lexical tag/URL order only
    # chooses a deterministic representative of equal numeric cores; it does
    # not claim one equal-precedence release is newer than another.
    version, baseline_tag, baseline_url = max(stable)
    major, minor, patch = version
    proposed = {"major": (major + 1, 0, 0), "minor": (major, minor + 1, 0),
                "patch": (major, minor, patch + 1)}[bump]
    proposed_version = ".".join(map(str, proposed))
    aliases = [prefix + proposed_version for prefix in prefixes]
    for inventory_name, inventory in tags.items():
        collisions = sorted(set(aliases).intersection(inventory))
        if collisions:
            raise EvidenceError(f"proposed release collides with {inventory_name} tags: {', '.join(collisions)}")
    evidence = dict(releases=releases, tags=tags, repository=repository,
                    prefixes=list(prefixes), bump=bump, source_url=source_url,
                    complete_evidence=complete_evidence)
    digest = hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=True, allow_nan=False).encode()).hexdigest()
    return dict(baseline_url=baseline_url, baseline_version=".".join(map(str, version)),
                baseline_tag=baseline_tag, proposed_version=proposed_version,
                proposed_tag=aliases[0], checked_tag_aliases=aliases,
                evidence_sha256=digest, source_url=source_url, change_class=bump,
                evidence_limit="caller-supplied snapshots and completeness attestation; not independently authenticated")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json(path):
    def invalid_constant(value):
        raise EvidenceError(f"invalid JSON constant: {value}")

    if not all(hasattr(os, flag) and getattr(os, flag) for flag in ("O_NONBLOCK", "O_NOFOLLOW")):
        raise EvidenceError("platform lacks required nonblocking/no-follow evidence-file flags")
    descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise EvidenceError("evidence must be a regular file")
        if before.st_size > MAX_EVIDENCE_BYTES:
            raise EvidenceError("evidence exceeds 8 MiB file limit")
        chunks = []
        remaining = MAX_EVIDENCE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(remaining, 65536))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        after = os.fstat(descriptor)
        current = os.stat(path, follow_symlinks=False)
        def identity(info):
            return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
                    info.st_mtime_ns, info.st_ctime_ns)
        if identity(before) != identity(after) or identity(after) != identity(current):
            raise EvidenceError("evidence file changed during read")
        contents = b"".join(chunks)
        if len(contents) > MAX_EVIDENCE_BYTES:
            raise EvidenceError("evidence exceeds 8 MiB file limit")
        if len(contents) != before.st_size:
            raise EvidenceError("evidence file changed during read")
    finally:
        os.close(descriptor)
    return json.loads(contents.decode("utf-8"),
                      object_pairs_hook=_unique_object, parse_constant=invalid_constant)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="release-version", description=__doc__,
        epilog="Read-only preflight, never publication authority. JSON output on success; exit 2 on refusal.")
    parser.add_argument("--repository", required=True, help="GitHub OWNER/REPO")
    parser.add_argument("--releases-file", required=True, help="JSON array of records from ALL release-list pages")
    parser.add_argument("--tags-file", required=True, help='JSON object: {"local": [bare tags], "remote": [bare tags]}')
    parser.add_argument("--source-url", required=True, help="https://api.github.com/repos/OWNER/REPO/releases")
    parser.add_argument("--tag-prefix", action="append", required=True,
                        help="repeat for ALL component aliases; first spells proposed tag; use '' for bare SemVer")
    parser.add_argument("--bump", choices=("patch", "minor", "major"), required=True)
    parser.add_argument("--complete-evidence", action="store_true", required=True,
                        help="attest ALL release API pages, ALL component aliases, and complete local AND remote tag inventories")
    args = parser.parse_args(argv)
    try:
        result = propose(_read_json(args.releases_file), _read_json(args.tags_file),
                         repository=args.repository, prefixes=args.tag_prefix,
                         bump=args.bump, source_url=args.source_url,
                         complete_evidence=args.complete_evidence)
    except (EvidenceError, OSError, UnicodeError, ValueError, RecursionError) as error:
        print(f"release-version: refused: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0
