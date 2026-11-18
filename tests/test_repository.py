"""Install this checkout's real catalog once, and exercise the vendor tool hermetically."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import HANG_GUARD

ROOT = Path(__file__).resolve().parents[1]


def run(*argv, ok=True):
    result = subprocess.run(
        [sys.executable, *map(str, argv)],
        capture_output=True,
        text=True,
        timeout=HANG_GUARD,
    )
    if ok and result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    return result


class CatalogTests(unittest.TestCase):
    def test_shipped_catalog_installs_verifies_and_restores(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "agent"
            cli = ROOT / "scripts/stack.py"
            install = json.loads(run(cli, "install", "--target", target).stdout)
            run(cli, "verify", "--target", target)
            helper = target / "skills/phi9t-land/scripts/land.py"
            self.assertIn("--repo", run(helper, "--help").stdout)
            run(cli, "restore", "--target", target, "--backup", install["backup"])
            self.assertFalse((target / "skills/phi9t/SKILL.md").exists())


class VendorTests(unittest.TestCase):
    """Drive scripts/vendor.py against a disposable repository and upstream."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="phi9t-vendor-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        shutil.copy2(ROOT / "scripts/vendor.py", self.repo / "scripts/vendor.py")
        (self.repo / "skills/demo").mkdir(parents=True)
        (self.repo / "skills/demo/SKILL.md").write_text("Local router\n")
        self.upstream = self.root / "upstream"
        (self.upstream / "skills/tool").mkdir(parents=True)
        (self.upstream / "skills/tool/SKILL.md").write_text("Upstream [link](x/)\n")
        (self.upstream / "LICENSE").write_text("MIT\n")
        self.manifest = self.repo / "vendor.json"
        self.write_manifest(patches=[])

    def write_manifest(self, patches):
        spec = {
            "package": "demo",
            "include": [{"from": "skills/tool", "to": "tool"}],
            "notice": ["LICENSE"],
            "patches": patches,
        }
        self.manifest.write_text(json.dumps({"vendors": {"demo": spec}}))

    def vendor(self, *args, ok=True):
        return run(self.repo / "scripts/vendor.py", *args, ok=ok)

    def test_sync_then_check_passes_and_keeps_the_local_router(self):
        self.vendor("sync", "demo", self.upstream)
        self.vendor("check")
        package = self.repo / "skills/demo"
        self.assertEqual((package / "SKILL.md").read_text(), "Local router\n")
        self.assertEqual((package / "LICENSE").read_text(), "MIT\n")

    def test_edited_vendored_file_is_refused(self):
        self.vendor("sync", "demo", self.upstream)
        (self.repo / "skills/demo/tool/SKILL.md").write_text("edited\n")
        self.assertEqual(self.vendor("check", ok=False).returncode, 1)

    def test_recorded_patch_applies_and_a_stale_patch_refuses(self):
        patch = {"path": "tool/SKILL.md", "old": "(x/)", "new": "(x/README.md)"}
        self.write_manifest(patches=[patch])
        self.vendor("sync", "demo", self.upstream)
        self.vendor("check")
        self.assertIn(
            "(x/README.md)", (self.repo / "skills/demo/tool/SKILL.md").read_text()
        )
        (self.upstream / "skills/tool/SKILL.md").write_text("Upstream moved on\n")
        self.assertEqual(
            self.vendor("sync", "demo", self.upstream, ok=False).returncode, 2
        )

    def test_missing_upstream_path_refuses(self):
        shutil.rmtree(self.upstream / "skills/tool")
        self.assertEqual(
            self.vendor("sync", "demo", self.upstream, ok=False).returncode, 2
        )


if __name__ == "__main__":
    unittest.main()
