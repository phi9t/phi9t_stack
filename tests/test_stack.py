"""Exercise the public CLI against disposable source and agent roots."""

import base64
import fcntl
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from itertools import product
from pathlib import Path

from tests.support import HANG_GUARD, tree_state

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/stack.py"
BASELINE = ROOT / "tests/fixtures/installer-baseline"


class StackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.target = self.base / "agent"
        package = self.source / "skills/phi9t"
        (package / "references").mkdir(parents=True)
        (package / "scripts").mkdir()
        (package / "SKILL.md").write_text(
            '---\nname: phi9t\ndescription: "Use for fixture work."\n---\n'
            "# Fixture\nRead [guide](references/guide.md).\n"
            "Run [driver](scripts/driver).\n"
        )
        (package / "references/guide.md").write_text("A real sidecar.\n")
        driver = package / "scripts/driver"
        driver.write_text('#!/bin/sh\nprintf "verified fixture\\n"\n')
        driver.chmod(0o755)
        self.file = self.target / "skills/phi9t/references/guide.md"

    def run_cli(self, *args, ok=True):
        result = subprocess.run(
            [sys.executable, str(CLI), "--source", str(self.source), *args],
            text=True,
            capture_output=True,
            timeout=HANG_GUARD,
        )
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("phi9t:", result.stderr)
        return result

    def install(self, *extra):
        return self.run_cli("install", "--target", str(self.target), *extra)

    def verify(self, ok=True):
        return self.run_cli("verify", "--target", str(self.target), ok=ok)

    def test_install_runs_packaged_driver_and_repeat_is_noop(self):
        first = json.loads(self.install().stdout)
        self.assertTrue(self.file.is_file())
        driver = self.target / "skills/phi9t/scripts/driver"
        self.assertEqual(
            subprocess.check_output([str(driver)], text=True), "verified fixture\n"
        )
        self.verify()
        manifest = (self.target / ".phi9t/manifest.json").read_bytes()
        second = json.loads(self.install().stdout)
        self.assertEqual(second["outcome"], "unchanged")
        self.assertEqual(manifest, (self.target / ".phi9t/manifest.json").read_bytes())
        self.assertEqual(len(list((self.target / ".phi9t/backups").glob("*.json"))), 1)
        self.assertTrue(first["backup"])

    def test_drift_refuses_update_and_explicit_replacement_can_restore(self):
        self.install()
        self.file.write_text("User customization\n")
        self.verify(ok=False)
        self.run_cli("install", "--target", str(self.target), ok=False)
        self.assertEqual(self.file.read_text(), "User customization\n")
        result = json.loads(self.install("--replace-modified").stdout)
        self.verify()
        self.run_cli(
            "restore", "--target", str(self.target), "--backup", result["backup"]
        )
        self.assertEqual(self.file.read_text(), "User customization\n")

    def test_unmanaged_collision_has_no_partial_install(self):
        self.file.parent.mkdir(parents=True)
        self.file.write_text("Unowned\n")
        self.run_cli("install", "--target", str(self.target), ok=False)
        self.assertEqual(self.file.read_text(), "Unowned\n")
        self.assertFalse((self.target / "skills/phi9t/SKILL.md").exists())

    def test_missing_reference_refuses_before_install(self):
        (self.source / "skills/phi9t/references/guide.md").unlink()
        self.run_cli("check", ok=False)
        self.run_cli("install", "--target", str(self.target), ok=False)
        self.assertFalse(self.target.exists())

    def test_titled_and_reference_style_links_require_packaged_targets(self):
        guide = self.source / "skills/phi9t/references/guide.md"
        for text in [
            '[detail](missing.md "Details")\n',
            "[detail][target]\n\n[target]: missing.md\n",
        ]:
            with self.subTest(text=text):
                guide.write_text(text)
                self.run_cli("check", ok=False)
                self.run_cli("install", "--target", str(self.target), ok=False)
                self.assertFalse(self.target.exists())

    def test_first_install_restore_preserves_unrelated_files(self):
        self.target.mkdir()
        unrelated = self.target / "my-notes.txt"
        unrelated.write_text("Keep me\n")
        backup = json.loads(self.install().stdout)["backup"]
        self.run_cli("restore", "--target", str(self.target), "--backup", backup)
        self.assertFalse(self.file.exists())
        self.assertFalse((self.target / ".phi9t/manifest.json").exists())
        self.assertEqual(unrelated.read_text(), "Keep me\n")

    def test_restore_refuses_later_user_edit(self):
        backup = json.loads(self.install().stdout)["backup"]
        self.file.write_text("Later edit\n")
        self.run_cli(
            "restore", "--target", str(self.target), "--backup", backup, ok=False
        )
        self.assertEqual(self.file.read_text(), "Later edit\n")

    def test_executable_mode_drift_fails_verification(self):
        self.install()
        (self.target / "skills/phi9t/scripts/driver").chmod(0o644)
        self.verify(ok=False)

    def test_symlink_destination_preserves_outside_state(self):
        outside = self.base / "outside"
        outside.mkdir()
        self.target.mkdir()
        (self.target / "skills").symlink_to(outside, target_is_directory=True)
        self.run_cli("install", "--target", str(self.target), ok=False)
        self.assertEqual(list(outside.iterdir()), [])

    def test_unsafe_source_symlink_fails(self):
        link = self.source / "skills/phi9t/references/outside.md"
        link.symlink_to("/etc/hosts")
        self.run_cli("check", ok=False)

    def test_removed_owned_package_is_backed_up_and_restorable(self):
        self.install()
        retired = self.target / "skills/phi9t-extra/SKILL.md"
        retired.parent.mkdir(parents=True)
        content = b"Previously installed tool\n"
        retired.write_bytes(content)
        manifest_path = self.target / ".phi9t/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["extensions"] = ["phi9t-extra"]
        manifest["files"]["skills/phi9t-extra/SKILL.md"] = {
            "sha256": hashlib.sha256(content).hexdigest(),
            "mode": 0o644,
        }
        manifest_path.write_text(json.dumps(manifest))
        retired.write_text("User modification\n")
        self.run_cli("install", "--target", str(self.target), ok=False)
        self.assertEqual(retired.read_text(), "User modification\n")
        retired.write_bytes(content)
        backup = json.loads(self.install().stdout)["backup"]
        self.assertFalse(retired.exists())
        self.verify()
        self.assertEqual(json.loads(self.install().stdout)["outcome"], "unchanged")
        self.run_cli("restore", "--target", str(self.target), "--backup", backup)
        self.assertEqual(retired.read_bytes(), content)
        self.assertEqual(manifest_path.read_text(), json.dumps(manifest))

    def test_extension_selection_is_not_supported(self):
        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--source",
                str(self.source),
                "install",
                "--target",
                str(self.target),
                "--extension",
                "phi9t-extra",
            ],
            text=True,
            capture_output=True,
            timeout=HANG_GUARD,
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.target.exists())

    def test_legacy_retirement_requires_exact_original_bytes(self):
        old = b"Original legacy skill\n"
        legacy = self.target / "skills/old.md"
        legacy.parent.mkdir(parents=True)
        legacy.write_bytes(old)
        (self.source / "legacy.json").write_text(
            json.dumps(
                {
                    "schema": 1,
                    "files": {
                        "skills/old.md": {
                            "sha256": hashlib.sha256(old).hexdigest(),
                            "mode": 0o644,
                        }
                    },
                }
            )
        )
        legacy.write_text("Customized legacy\n")
        self.run_cli(
            "install", "--target", str(self.target), "--migrate-legacy", ok=False
        )
        self.assertFalse((self.target / "skills/phi9t/SKILL.md").exists())
        legacy.write_bytes(old)
        backup = json.loads(self.install("--migrate-legacy").stdout)["backup"]
        self.assertFalse(legacy.exists())
        self.run_cli("restore", "--target", str(self.target), "--backup", backup)
        self.assertEqual(legacy.read_bytes(), old)

    def test_interrupted_install_recovers_original_state_and_preserves_new_edits(self):
        self.install()
        original = self.file.read_bytes()
        (self.source / "skills/phi9t/references/guide.md").write_text("Updated\n")
        backup = json.loads(self.install().stdout)["backup"]
        state = self.target / ".phi9t"
        # Recreate the on-disk state of a transaction interrupted after one write.
        receipt = json.loads((state / ("backups/" + backup + ".json")).read_text())
        self.file.write_bytes(original)
        (state / "pending.json").write_text(json.dumps({"backup": backup}))
        self.verify(ok=False)
        self.file.write_text("User edit after interruption\n")
        self.run_cli("recover", "--target", str(self.target), ok=False)
        self.assertEqual(self.file.read_text(), "User edit after interruption\n")
        self.assertTrue((state / "pending.json").exists())
        self.file.write_bytes(original)
        self.run_cli("recover", "--target", str(self.target))
        self.assertFalse((state / "pending.json").exists())
        self.assertEqual(self.file.read_bytes(), original)
        old_manifest = receipt["before"][".phi9t/manifest.json"]
        self.assertEqual(
            (state / "manifest.json").read_bytes(),
            base64.b64decode(old_manifest["data"]),
        )
        self.install()
        self.verify()

    def test_writer_lock_refuses_concurrent_mutation(self):
        state = self.target / ".phi9t"
        state.mkdir(parents=True)
        with (state / "lock").open("w") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            self.run_cli("install", "--target", str(self.target), ok=False)
        self.assertFalse(self.file.exists())
        self.install()

    def test_failed_write_leaves_a_recoverable_transaction(self):
        self.install()
        before = tree_state(self.target, exclude=(".phi9t",))
        (self.source / "skills/phi9t/references/guide.md").write_text("Updated\n")
        (self.source / "skills/phi9t/scripts/driver").write_text(
            "#!/bin/sh\necho new\n"
        )
        scripts = self.target / "skills/phi9t/scripts"
        scripts.chmod(0o555)  # a real write fault after guide.md is updated
        self.addCleanup(scripts.chmod, 0o755)
        self.run_cli("install", "--target", str(self.target), ok=False)
        self.assertTrue((self.target / ".phi9t/pending.json").exists())
        self.verify(ok=False)
        scripts.chmod(0o755)
        self.run_cli("recover", "--target", str(self.target))
        self.assertEqual(tree_state(self.target, exclude=(".phi9t",)), before)
        self.assertFalse((self.target / ".phi9t/pending.json").exists())
        self.install()
        self.verify()

    def test_baseline_manifest_verifies_and_saved_backup_restores(self):
        self.install()
        state = self.target / ".phi9t"
        baseline_manifest = (BASELINE / "manifest-v2.json").read_bytes()
        self.assertEqual((state / "manifest.json").read_bytes(), baseline_manifest)
        self.assertEqual((state / "manifest.json").stat().st_mode & 0o777, 0o600)
        (state / "manifest.json").write_bytes(baseline_manifest)
        self.verify()
        transaction = json.loads((BASELINE / "transaction-v1.json").read_text())
        transaction["target"] = str(self.target.resolve())
        backup = "1" * 32
        (state / "backups" / (backup + ".json")).write_text(json.dumps(transaction))
        unrelated = self.target / "custom.txt"
        unrelated.write_bytes(b"User customization\x00\xff")
        self.run_cli("restore", "--target", str(self.target), "--backup", backup)
        for relative in transaction["after"]:
            self.assertFalse((self.target / relative).exists(), relative)
        self.assertEqual(unrelated.read_bytes(), b"User customization\x00\xff")

    def test_restore_distinguishes_absence_empty_binary_and_prior_permissions(self):
        empty_source = self.source / "skills/phi9t/references/empty.bin"
        empty_source.write_bytes(b"")
        self.install()
        empty = self.target / "skills/phi9t/references/empty.bin"
        self.file.write_bytes(b"\x00\xffPrior binary\x00")
        self.file.chmod(0o601)
        empty.chmod(0o640)
        empty_source.write_bytes(b"Updated empty file")
        new_source = self.source / "skills/phi9t/references/new-empty.bin"
        new_source.write_bytes(b"")
        backup = json.loads(self.install("--replace-modified").stdout)["backup"]
        new_file = self.target / "skills/phi9t/references/new-empty.bin"
        self.assertTrue(new_file.is_file())
        self.assertEqual(new_file.read_bytes(), b"")
        self.verify()
        self.run_cli("restore", "--target", str(self.target), "--backup", backup)
        self.assertEqual(self.file.read_bytes(), b"\x00\xffPrior binary\x00")
        self.assertEqual(self.file.stat().st_mode & 0o777, 0o601)
        self.assertTrue(empty.is_file())
        self.assertEqual(empty.read_bytes(), b"")
        self.assertEqual(empty.stat().st_mode & 0o777, 0o640)
        self.assertFalse(new_file.exists())
        self.assertEqual(
            (self.target / ".phi9t/manifest.json").stat().st_mode & 0o777, 0o600
        )

    def test_noncanonical_after_snapshot_refuses_restore_and_recovery(self):
        relative = "skills/phi9t/references/blob.bin"
        (self.source / relative).write_bytes(b"A")
        backup = json.loads(self.install().stdout)["backup"]
        state = self.target / ".phi9t"
        backup_path = state / "backups" / (backup + ".json")
        transaction = json.loads(backup_path.read_text())
        transaction["after"][relative]["data"] = "QR=="
        backup_path.write_text(json.dumps(transaction))
        for command in ("restore", "recover"):
            with self.subTest(command=command):
                pending = state / "pending.json"
                args = [command, "--target", str(self.target)]
                if command == "recover":
                    pending.write_text(json.dumps({"backup": backup}))
                else:
                    args.extend(["--backup", backup])
                before = tree_state(self.target)
                self.run_cli(*args, ok=False)
                after = tree_state(self.target)
                self.assertEqual(after, before)
                pending.unlink(missing_ok=True)

    def test_noncanonical_before_snapshot_restores_from_canonical_after(self):
        relative = "skills/phi9t/references/blob.bin"
        source = self.source / relative
        for command in ("restore", "recover"):
            with self.subTest(command=command):
                source.write_bytes(b"A")
                self.install()
                source.write_bytes(b"B")
                backup = json.loads(self.install().stdout)["backup"]
                state = self.target / ".phi9t"
                backup_path = state / "backups" / (backup + ".json")
                transaction = json.loads(backup_path.read_text())
                transaction["before"][relative]["data"] = "QR=="
                backup_path.write_text(json.dumps(transaction))
                args = [command, "--target", str(self.target)]
                if command == "recover":
                    (state / "pending.json").write_text(json.dumps({"backup": backup}))
                else:
                    args.extend(["--backup", backup])
                self.run_cli(*args)
                self.assertEqual((self.target / relative).read_bytes(), b"A")
                self.assertFalse((state / "pending.json").exists())

    def test_recovery_accepts_canonical_before_with_noncanonical_after(self):
        relative = "skills/phi9t/references/blob.bin"
        (self.source / relative).write_bytes(b"A")
        backup = json.loads(self.install().stdout)["backup"]
        state = self.target / ".phi9t"
        backup_path = state / "backups" / (backup + ".json")
        transaction = json.loads(backup_path.read_text())
        transaction["after"][relative]["data"] = "QR=="
        backup_path.write_text(json.dumps(transaction))
        (self.target / relative).unlink()
        (state / "pending.json").write_text(json.dumps({"backup": backup}))
        self.run_cli("recover", "--target", str(self.target))
        self.assertFalse((self.target / relative).exists())
        self.assertFalse((state / "pending.json").exists())

    def test_invalid_transaction_metadata_and_paths_refuse_before_writes(self):
        self.install()
        state = self.target / ".phi9t"
        backup = "3" * 32
        backup_path = state / "backups" / (backup + ".json")
        pending = state / "pending.json"
        for command, invalid in product(
            ("restore", "recover"), ("target", "path-set", "unsafe-late-path")
        ):
            with self.subTest(command=command, invalid=invalid):
                transaction = json.loads((BASELINE / "transaction-v1.json").read_text())
                transaction["target"] = str(self.target.resolve())
                if invalid == "target":
                    transaction["target"] = str(self.base / "other-agent")
                elif invalid == "path-set":
                    transaction["before"].pop(next(iter(transaction["before"])))
                else:
                    for side in ("before", "after"):
                        transaction[side]["skills/../../outside.txt"] = None
                backup_path.write_text(json.dumps(transaction))
                args = [command, "--target", str(self.target)]
                if command == "recover":
                    pending.write_text(json.dumps({"backup": backup}))
                else:
                    args.extend(["--backup", backup])
                before = tree_state(self.target)
                self.run_cli(*args, ok=False)
                after = tree_state(self.target)
                self.assertEqual(after, before)
                self.assertFalse((self.base / "outside.txt").exists())
                pending.unlink(missing_ok=True)

    def test_malformed_late_snapshot_refuses_restore_and_recovery_before_writes(self):
        self.install()
        state = self.target / ".phi9t"
        backup = "2" * 32
        backup_path = state / "backups" / (backup + ".json")
        pending = state / "pending.json"
        for command, side, invalid in product(
            ("restore", "recover"),
            ("before", "after"),
            (
                {"data": "!!!", "mode": 0o644},
                {"data": "", "mode": 0o1000},
                {"data": ""},
            ),
        ):
            with self.subTest(command=command, side=side, invalid=invalid):
                transaction = json.loads((BASELINE / "transaction-v1.json").read_text())
                transaction["target"] = str(self.target.resolve())
                final_path = list(transaction[side])[-1]
                transaction[side][final_path] = invalid
                backup_path.write_text(json.dumps(transaction))
                args = [command, "--target", str(self.target)]
                if command == "recover":
                    pending.write_text(json.dumps({"backup": backup}))
                else:
                    args.extend(["--backup", backup])
                before = tree_state(self.target)
                self.run_cli(*args, ok=False)
                after = tree_state(self.target)
                self.assertEqual(after, before)
                pending.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
