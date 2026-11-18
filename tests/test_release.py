"""Exercise release artifacts and the actual bundled installer through the CLI."""

import gzip
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts.release import MAX_ARCHIVE
from tests.support import HANG_GUARD

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/release.py"


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="phi9t-release-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.write_catalog()
        (self.repo / "scripts").mkdir()
        for name in ("stack.py", "install.sh", "release.py", "vendor.py"):
            shutil.copy2(ROOT / "scripts" / name, self.repo / "scripts" / name)
        (self.repo / "docs").mkdir()
        (self.repo / "docs/provenance.md").write_text("Fixture provenance\n")
        (self.repo / "docs/release-bundle.md").write_text("Fixture bundle notes\n")
        (self.repo / "legacy.json").write_text('{"schema": 1, "files": {}}\n')
        (self.repo / "vendor.json").write_text('{"vendors": {}}\n')
        # These are controlled two-version fixtures, independent of the next
        # real release selected by the source checkout's VERSION.
        (self.repo / "VERSION").write_text("0.1.0-rc.1\n")
        (self.repo / "releases").mkdir()
        (self.repo / "releases/0.1.0-rc.1.md").write_text("First candidate\n")
        private = self.repo / "docs/research/private.md"
        private.parent.mkdir(parents=True)
        private.write_text("DO NOT DISTRIBUTE THIS RESEARCH\n")
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Release test")
        self.git("config", "user.email", "test@example.invalid")
        self.git(
            "add",
            "scripts",
            "skills",
            "docs",
            "legacy.json",
            "vendor.json",
            "VERSION",
            "releases",
        )
        self.git("commit", "-m", "Release source")
        self.commit = self.git("rev-parse", "HEAD")

    def write_catalog(self):
        """A minimal valid catalog: one method plus the landing helper qualify runs."""
        for name, body in (
            ("phi9t", "Fixture router."),
            ("phi9t-land", "Fixture landing method."),
        ):
            package = self.repo / "skills" / name
            package.mkdir(parents=True)
            (package / "SKILL.md").write_text(
                f'---\nname: {name}\ndescription: "{body}"\n---\n# {name}\n'
            )
        driver = self.repo / "skills/phi9t-land/scripts/land.py"
        driver.parent.mkdir()
        shutil.copy2(ROOT / "skills/phi9t-land/scripts/land.py", driver)

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            text=True,
            capture_output=True,
            check=True,
            timeout=HANG_GUARD,
        ).stdout.strip()

    def cli(self, *args, ok=True):
        result = subprocess.run(
            [sys.executable, str(CLI), *args],
            text=True,
            capture_output=True,
            timeout=HANG_GUARD,
        )
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def build(self, name="output", ref="main"):
        return self.cli(
            "build",
            "--repo",
            str(self.repo),
            "--ref",
            ref,
            "--mainline",
            "main",
            "--output",
            str(self.root / name),
        )

    def test_reproducible_committed_bundle_excludes_private_and_dirty_content(self):
        (self.repo / "skills/phi9t/SKILL.md").write_text("uncommitted replacement")
        first = self.build()
        second = self.build("again")
        self.assertEqual(first["sha256"], second["sha256"])
        self.assertEqual(
            Path(first["archive"]).read_bytes(), Path(second["archive"]).read_bytes()
        )
        verified = self.cli(
            "verify", "--archive", first["archive"], "--sha256", first["sha256"]
        )
        self.assertEqual(verified["source_commit"], self.commit)
        unpacked = self.cli(
            "unpack",
            "--archive",
            first["archive"],
            "--output",
            str(self.root / "unpacked"),
        )
        source = Path(unpacked["directory"])
        self.assertFalse((source / "docs/research").exists())
        self.assertNotEqual(
            (source / "skills/phi9t/SKILL.md").read_text(), "uncommitted replacement"
        )
        driver = source / "skills/phi9t-land/scripts/land.py"
        self.assertEqual(driver.stat().st_mode & 0o777, 0o755)

    def test_qualify_installs_core_and_restores(self):
        release = self.build()
        receipt = self.cli(
            "qualify",
            "--archive",
            release["archive"],
            "--output",
            str(self.root / "qualification"),
        )
        self.assertEqual(receipt["status"], "qualified")
        self.assertEqual(receipt["archive_sha256"], release["sha256"])
        self.assertEqual(receipt["profiles"], [{"profile": "core", "restored": True}])
        self.assertTrue(all(row["restored"] for row in receipt["profiles"]))

    def test_checksum_mismatch_refuses_before_unpack(self):
        release = self.build()
        target = self.root / "unpacked"
        self.cli(
            "unpack",
            "--archive",
            release["archive"],
            "--sha256",
            "0" * 64,
            "--output",
            str(target),
            ok=False,
        )
        self.assertFalse(target.exists())

    def test_output_collision_preserves_existing_artifacts(self):
        release = self.build()
        before = Path(release["archive"]).read_bytes()
        self.cli(
            "build",
            "--repo",
            str(self.repo),
            "--ref",
            "main",
            "--mainline",
            "main",
            "--output",
            str(self.root / "output"),
            ok=False,
        )
        self.assertEqual(Path(release["archive"]).read_bytes(), before)
        target = self.root / "existing"
        target.mkdir()
        (target / "human").write_text("retain")
        self.cli(
            "unpack", "--archive", release["archive"], "--output", str(target), ok=False
        )
        self.assertEqual((target / "human").read_text(), "retain")

    def test_unlanded_source_and_retagged_version_refuse(self):
        self.git("switch", "-c", "topic")
        (self.repo / "skills/phi9t/extra.md").write_text("new")
        self.git("add", "skills/phi9t/extra.md")
        self.git("commit", "-m", "Unlanded")
        self.cli(
            "build",
            "--repo",
            str(self.repo),
            "--ref",
            "topic",
            "--mainline",
            "main",
            "--output",
            str(self.root / "output"),
            ok=False,
        )
        self.git("tag", "v0.1.0-rc.1", "topic")
        self.cli(
            "build",
            "--repo",
            str(self.repo),
            "--ref",
            "main",
            "--mainline",
            "main",
            "--output",
            str(self.root / "output"),
            ok=False,
        )

    def rewrite_archive(self, source, transform):
        raw = gzip.decompress(Path(source).read_bytes())
        result = io.BytesIO()
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as original:
            with tarfile.open(fileobj=result, mode="w:") as target:
                for entry in original:
                    data = original.extractfile(entry).read()
                    transform(entry, data, target)
        path = self.root / "tampered.tar.gz"
        path.write_bytes(gzip.compress(result.getvalue(), mtime=0))
        return str(path)

    def test_tampered_member_and_unsafe_paths_refuse(self):
        release = self.build()

        def replace(entry, data, target):
            if entry.name.endswith("scripts/stack.py"):
                data = b"tampered"
                entry.size = len(data)
            target.addfile(entry, io.BytesIO(data))

        archive = self.rewrite_archive(release["archive"], replace)
        self.cli("verify", "--archive", archive, ok=False)

        def escape(entry, data, target):
            if entry.name.endswith("scripts/stack.py"):
                entry.name = "../escape.py"
            target.addfile(entry, io.BytesIO(data))

        archive = self.rewrite_archive(release["archive"], escape)
        self.cli(
            "unpack", "--archive", archive, "--output", str(self.root / "bad"), ok=False
        )
        self.assertFalse((self.root / "escape.py").exists())

    def test_duplicate_members_and_symlinks_refuse(self):
        release = self.build()

        def duplicate(entry, data, target):
            target.addfile(entry, io.BytesIO(data))
            if entry.name.endswith("scripts/stack.py"):
                target.addfile(entry, io.BytesIO(data))

        archive = self.rewrite_archive(release["archive"], duplicate)
        self.cli("verify", "--archive", archive, ok=False)

        def link(entry, data, target):
            if entry.name.endswith("scripts/stack.py"):
                entry.type = tarfile.SYMTYPE
                entry.linkname = "/tmp/elsewhere"
                entry.size = 0
                target.addfile(entry)
            else:
                target.addfile(entry, io.BytesIO(data))

        archive = self.rewrite_archive(release["archive"], link)
        self.cli("verify", "--archive", archive, ok=False)

    def test_invalid_version_and_source_symlink_refuse(self):
        (self.repo / "VERSION").write_text("../bad\n")
        self.git("add", "VERSION")
        self.git("commit", "-m", "Invalid version")
        self.cli(
            "build",
            "--repo",
            str(self.repo),
            "--ref",
            "main",
            "--mainline",
            "main",
            "--output",
            str(self.root / "invalid"),
            ok=False,
        )

        (self.repo / "VERSION").write_text("0.1.0-rc.1\n")
        path = self.repo / "skills/phi9t/link"
        path.symlink_to("/etc/passwd")
        self.git("add", "VERSION", "skills/phi9t/link")
        self.git("commit", "-m", "Unsafe link")
        self.cli(
            "build",
            "--repo",
            str(self.repo),
            "--ref",
            "main",
            "--mainline",
            "main",
            "--output",
            str(self.root / "linked"),
            ok=False,
        )

    def test_git_replacement_objects_do_not_change_exported_source(self):
        name = "skills/phi9t/SKILL.md"
        original = (self.repo / name).read_bytes()
        blob = self.git("rev-parse", "HEAD:" + name)
        changed = (
            subprocess.run(
                ["git", "-C", str(self.repo), "hash-object", "-w", "--stdin"],
                input=original + b"\nREPLACEMENT CONTENT\n",
                capture_output=True,
                check=True,
                timeout=HANG_GUARD,
            )
            .stdout.decode()
            .strip()
        )
        self.git("replace", blob, changed)
        release = self.build()
        target = self.root / "unpacked"
        self.cli("unpack", "--archive", release["archive"], "--output", str(target))
        self.assertEqual((target / name).read_bytes(), original)

    def test_grafts_cannot_make_unlanded_source_releasable(self):
        self.git("switch", "-c", "candidate")
        (self.repo / "skills/phi9t/added.md").write_text("Unlanded\n")
        self.git("add", "skills/phi9t/added.md")
        self.git("commit", "-m", "Unlanded candidate")
        candidate = self.git("rev-parse", "HEAD")
        self.git("switch", "main")
        (self.repo / "local.txt").write_text("Mainline\n")
        self.git("add", "local.txt")
        self.git("commit", "-m", "Mainline advances independently")
        head = self.git("rev-parse", "HEAD")
        (self.repo / ".git/info/grafts").write_text(f"{head} {candidate}\n")
        result = self.cli(
            "build",
            "--repo",
            str(self.repo),
            "--ref",
            candidate,
            "--mainline",
            "main",
            "--output",
            str(self.root / "grafted"),
            ok=False,
        )
        self.assertIn("graft", result["reason"])
        self.assertFalse((self.root / "grafted").exists())

    def test_release_upgrade_can_restore_previous_distribution(self):
        first = self.build()
        (self.repo / "VERSION").write_text("0.1.0-rc.2\n")
        (self.repo / "releases/0.1.0-rc.2.md").write_text("Second candidate\n")
        (self.repo / "skills/phi9t/added.md").write_text("Added resource\n")
        self.git("add", "VERSION", "releases/0.1.0-rc.2.md", "skills/phi9t/added.md")
        self.git("commit", "-m", "Next release")
        second = self.build("second")
        one, two = self.root / "one", self.root / "two"
        self.cli("unpack", "--archive", first["archive"], "--output", str(one))
        self.cli("unpack", "--archive", second["archive"], "--output", str(two))
        target = self.root / "agent"

        def install(source, *args):
            result = subprocess.run(
                [
                    sys.executable,
                    str(source / "scripts/stack.py"),
                    *args,
                    "--target",
                    str(target),
                ],
                text=True,
                capture_output=True,
                check=True,
                timeout=HANG_GUARD,
            )
            return json.loads(result.stdout)

        install(one, "install")
        upgraded = install(two, "install")
        distribution = target / "skills/phi9t/references/distribution.json"
        self.assertEqual(json.loads(distribution.read_text())["version"], "0.1.0-rc.2")
        install(two, "restore", "--backup", upgraded["backup"])
        self.assertEqual(json.loads(distribution.read_text())["version"], "0.1.0-rc.1")
        self.assertFalse((target / "skills/phi9t/added.md").exists())
        install(one, "verify")

    def test_damaged_gzip_refuses_as_json_before_writing(self):
        release = self.build()
        original = Path(release["archive"]).read_bytes()
        cases = {
            "truncated-header": original[:5],
            "truncated-trailer": original[:-8],
            "invalid-deflate": b"\x1f\x8b\x08" + b"\x00" * 7 + b"\xff" * 20,
        }
        sentinel = self.root / "human.txt"
        sentinel.write_text("preserve\n")
        for name, data in cases.items():
            archive = self.root / (name + ".tar.gz")
            archive.write_bytes(data)
            for command in ("verify", "unpack", "qualify"):
                with self.subTest(input=name, command=command):
                    output = self.root / (name + "-" + command)
                    argv = [
                        sys.executable,
                        str(CLI),
                        command,
                        "--archive",
                        str(archive),
                        "--sha256",
                        hashlib.sha256(data).hexdigest(),
                    ]
                    if command != "verify":
                        argv.extend(["--output", str(output)])
                    result = subprocess.run(
                        argv,
                        text=True,
                        capture_output=True,
                        timeout=HANG_GUARD,
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(result.stderr, "")
                    refusal = json.loads(result.stdout)
                    self.assertEqual(refusal["status"], "refused")
                    self.assertIn("gzip", refusal["reason"])
                    self.assertFalse(output.exists())
                    self.assertEqual(archive.read_bytes(), data)
                    self.assertEqual(sentinel.read_text(), "preserve\n")

    def test_oversized_compressed_payload_and_nonobject_manifest_refuse(self):
        bomb = self.root / "oversized.tar.gz"
        bomb.write_bytes(gzip.compress(b"x" * (MAX_ARCHIVE + 1), mtime=0))
        self.cli("verify", "--archive", str(bomb), ok=False)
        release = self.build()

        def malformed(entry, data, target):
            if entry.name.endswith("/release.json"):
                data = b"[]"
                entry.size = len(data)
            target.addfile(entry, io.BytesIO(data))

        archive = self.rewrite_archive(release["archive"], malformed)
        self.cli("verify", "--archive", archive, ok=False)


if __name__ == "__main__":
    unittest.main()
