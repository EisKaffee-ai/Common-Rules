"""Synthetic, offline regression checks for official release preflight."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bin" / "release-version"
REPO = "example/widgets"
SOURCE = f"https://api.github.com/repos/{REPO}/releases"


def release(tag="v0.8.1", **changes):
    row = dict(tag_name=tag, draft=False, prerelease=False,
               published_at="2026-10-01T12:00:00Z",
               html_url=f"https://github.com/{REPO}/releases/tag/{quote(tag, safe='/')}")
    row.update(changes)
    return row


class ReleaseVersionTests(unittest.TestCase):
    def run_cli(self, rows=None, tags=None, bump="patch", prefixes=("v", ""),
                complete=True, source=SOURCE, extra=()):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "VERSION").write_text("0.8.8\n")
            releases_path = base / "releases.json"
            tags_path = base / "tags.json"
            releases_path.write_text(json.dumps([release()] if rows is None else rows))
            tags_path.write_text(json.dumps(dict(local=[], remote=[]) if tags is None else tags))
            before = {p.name: p.read_bytes() for p in base.iterdir()}
            command = [sys.executable, "-B", str(CLI), "--repository", REPO,
                       "--releases-file", str(releases_path), "--tags-file", str(tags_path),
                       "--source-url", source, "--bump", bump]
            for prefix in prefixes:
                command += ["--tag-prefix", prefix]
            if complete:
                command += ["--complete-evidence"]
            result = subprocess.run(command + list(extra), cwd=base, text=True,
                                    capture_output=True, timeout=10)
            self.assertEqual(before, {p.name: p.read_bytes() for p in base.iterdir()})
            return result

    def good(self, **kwargs):
        result = self.run_cli(**kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def refused(self, **kwargs):
        result = self.run_cli(**kwargs)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("release-version:", result.stderr)

    def test_candidate_file_never_overrides_official_baseline(self):
        result = self.good()
        self.assertEqual(result["baseline_version"], "0.8.1")
        self.assertEqual(result["proposed_version"], "0.8.2")
        self.assertEqual(result["proposed_tag"], "v0.8.2")
        self.assertEqual(result["baseline_url"], release()["html_url"])
        self.assertEqual(result["baseline_tag"], "v0.8.1")
        self.assertEqual(result["change_class"], "patch")

    def test_exact_increments_and_resets(self):
        for bump, expected in [("patch", "2.8.10"), ("minor", "2.9.0"), ("major", "3.0.0")]:
            with self.subTest(bump=bump):
                self.assertEqual(self.good(rows=[release("v2.8.9")], bump=bump)["proposed_version"], expected)

    def test_numeric_not_lexical_order(self):
        rows = [release("v1.9.99"), release("v1.10.0"), release("v0.99.99")]
        self.assertEqual(self.good(rows=rows)["baseline_version"], "1.10.0")

    def test_drafts_and_prereleases_are_excluded(self):
        rows = [release(), release("v9.0.0", draft=True, published_at=None),
                release("v8.0.0-beta.1", prerelease=True)]
        self.assertEqual(self.good(rows=rows)["baseline_version"], "0.8.1")

    def test_component_aliases_share_baseline(self):
        rows = [release("sdk-v1.2.3"), release("sdk/1.3.0"), release("other-v9.0.0")]
        result = self.good(rows=rows, prefixes=("sdk-v", "sdk/"))
        self.assertEqual(result["baseline_version"], "1.3.0")
        self.assertEqual(result["proposed_tag"], "sdk-v1.3.1")

    def test_every_alias_collides_in_each_inventory(self):
        for inventory in ("local", "remote"):
            for tag in ("v0.8.2", "0.8.2"):
                with self.subTest(inventory=inventory, tag=tag):
                    tags = dict(local=[], remote=[])
                    tags[inventory] = [tag]
                    self.refused(tags=tags)

    def test_unpublished_tags_do_not_raise_baseline(self):
        self.assertEqual(self.good(tags=dict(local=["v0.8.8"], remote=["v0.8.7"]))["proposed_version"], "0.8.2")

    def test_no_stable_release_refuses(self):
        for rows in ([], [release(draft=True)], [release(prerelease=True)]):
            with self.subTest(rows=rows):
                self.refused(rows=rows)

    def test_complete_evidence_acknowledgement_required(self):
        self.refused(complete=False)

    def test_both_tag_inventories_required(self):
        for tags in ({}, {"local": []}, {"remote": []}, {"local": [], "remote": None}):
            with self.subTest(tags=tags):
                self.refused(tags=tags)

    def test_unknown_tag_inventory_fields_refuse(self):
        self.refused(tags=dict(local=[], remote=[], unknown=[]))

    def test_malformed_inventory_entries_refuse(self):
        for entry in (None, 123, {}, "", "v1.2.3\n"):
            self.refused(tags=dict(local=[entry], remote=[]))

    def test_ref_paths_and_peeled_inventory_lines_refuse(self):
        for inventory in ("local", "remote"):
            for entry in ("refs/tags/v0.8.2", "refs/heads/v0.8.2", "v0.8.2^{}",
                          "refs/tags/v0.8.2^{}", "a" * 40 + "\trefs/tags/v0.8.2"):
                with self.subTest(inventory=inventory, entry=entry):
                    tags = dict(local=[], remote=[])
                    tags[inventory] = [entry]
                    self.refused(tags=tags)

    def test_invalid_git_tag_names_refuse(self):
        for entry in (".hidden", "sdk/.hidden/v1", "v1.lock", "sdk.lock/v1",
                      "v1.", "sdk//v1", "/v1", "v1/", "v..1", "v@{1}",
                      "@", "v~1", "v:1", "v?1", "v*1", "v[1", "v\\1"):
            with self.subTest(entry=entry):
                self.refused(tags=dict(local=[entry], remote=[]))

    def test_invalid_tag_prefixes_refuse(self):
        for prefix in ("refs/tags/v", "v^", "sdk//", ".hidden/", "sdk.lock/"):
            with self.subTest(prefix=prefix):
                self.refused(rows=[release(prefix + "0.8.1")], prefixes=(prefix,))

    def test_publication_timestamp_required_and_valid(self):
        for value in (None, "", "yesterday", "2026-10-01", "2026-02-30T12:00:00Z", "2026-10-01T12:00:00"):
            with self.subTest(value=value):
                self.refused(rows=[release(published_at=value)])
        row = release()
        del row["published_at"]
        self.refused(rows=[row])

    def test_repository_matching_release_url_required(self):
        for url in (None, "https://github.com/other/widgets/releases/tag/v0.8.1",
                    "https://github.com/example/widgets/releases/tag/v0.8.2",
                    "https://github.com.evil.test/example/widgets/releases/tag/v0.8.1",
                    "http://github.com/example/widgets/releases/tag/v0.8.1"):
            with self.subTest(url=url):
                self.refused(rows=[release(html_url=url)])

    def test_unknown_or_wrong_source_refuses(self):
        for source in ("file:///tmp/releases", SOURCE + "/latest", "https://api.github.com/repos/other/widgets/releases"):
            self.refused(source=source)

    def test_missing_or_malformed_flags_refuse(self):
        for key in ("draft", "prerelease", "tag_name"):
            row = release()
            del row[key]
            self.refused(rows=[row])
        self.refused(rows=[release(draft="false")])
        self.refused(rows=[release(prerelease=0)])

    def test_malformed_release_list_refuses(self):
        for rows in ({"releases": []}, [None], ["v0.8.1"]):
            self.refused(rows=rows)

    def test_invalid_stable_semver_refuses(self):
        for tag in ("v01.2.3", "v1.2", "v1.2.3+", "v1.2.3+build..1", "v1.2.3-rc.1", "v1.٢.3"):
            self.refused(rows=[release(tag)], prefixes=("v",))

    def test_stable_build_metadata_preserves_observed_identity(self):
        for metadata in ("build", "001", "build.001-alpha"):
            with self.subTest(metadata=metadata):
                row = release("v1.2.3+" + metadata)
                result = self.good(rows=[row])
                self.assertEqual(result["baseline_version"], "1.2.3")
                self.assertEqual(result["baseline_tag"], row["tag_name"])
                self.assertEqual(result["baseline_url"], row["html_url"])
                self.assertEqual(result["proposed_version"], "1.2.4")
                self.assertEqual(result["proposed_tag"], "v1.2.4")

    def test_equal_core_metadata_has_no_precedence_and_tie_is_deterministic(self):
        rows = [release("v1.2.3+zzz"), release("v1.2.3+001"), release("v1.2.3")]
        first = self.good(rows=rows)
        reverse = self.good(rows=list(reversed(rows)))
        self.assertEqual(first["baseline_tag"], reverse["baseline_tag"])
        self.assertEqual(first["baseline_version"], "1.2.3")
        self.assertEqual(first["proposed_version"], "1.2.4")
        rows.append(release("v1.2.4+000"))
        self.assertEqual(self.good(rows=rows)["baseline_version"], "1.2.4")

    def test_build_metadata_plus_can_be_literal_in_release_path(self):
        row = release("v1.2.3+build", html_url=f"https://github.com/{REPO}/releases/tag/v1.2.3+build")
        self.assertEqual(self.good(rows=[row])["baseline_url"], row["html_url"])

    def test_conflicting_duplicate_release_identity_refuses(self):
        self.refused(rows=[release(), release(published_at="2026-10-02T12:00:00Z")])

    def test_deterministic_output_and_hash_bound_to_evidence(self):
        first = self.good()
        self.assertEqual(first, self.good())
        self.assertRegex(first["evidence_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotEqual(first["evidence_sha256"], self.good(tags=dict(local=["v7.0.0"], remote=[]))["evidence_sha256"])
        self.assertIn("caller-supplied", first["evidence_limit"])

    def test_invalid_cli_inputs_refuse(self):
        self.refused(bump="auto")
        self.refused(prefixes=())
        self.refused(extra=("--candidate-version", "0.8.8"))

    def test_unsafe_or_oversized_evidence_files_refuse_without_blocking(self):
        for kind in ("oversized", "symlink", "fifo"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                ordinary = base / "ordinary.json"
                ordinary.write_text(json.dumps([release()]))
                evidence = base / "evidence.json"
                if kind == "oversized":
                    evidence.write_bytes(ordinary.read_bytes() + b" " * (8 * 1024 * 1024))
                elif kind == "symlink":
                    evidence.symlink_to(ordinary)
                else:
                    os.mkfifo(evidence)
                tags = base / "tags.json"
                tags.write_text('{"local":[],"remote":[]}')
                before = {p.name: (p.lstat().st_mode, p.lstat().st_size,
                                   p.lstat().st_mtime_ns) for p in base.iterdir()}
                for releases_file, tags_file in ((evidence, tags), (ordinary, evidence)):
                    result = subprocess.run(
                        [sys.executable, "-B", str(CLI), "--repository", REPO,
                         "--releases-file", str(releases_file), "--tags-file", str(tags_file),
                         "--source-url", SOURCE, "--tag-prefix", "v", "--bump", "patch",
                         "--complete-evidence"], capture_output=True, text=True, timeout=3)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("release-version:", result.stderr)
                self.assertEqual(before, {p.name: (p.lstat().st_mode, p.lstat().st_size,
                                                  p.lstat().st_mtime_ns) for p in base.iterdir()})


if __name__ == "__main__":
    unittest.main()
