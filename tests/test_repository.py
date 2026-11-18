"""Exercise this checkout's full packages, and required tool resources."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryTests(unittest.TestCase):
    def test_complete_catalog_installs_verifies_and_restores(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "agent"
            cli = [sys.executable, str(ROOT / "scripts/stack.py")]

            def run(*args):
                return subprocess.run(
                    cli + list(args), capture_output=True, text=True, check=True
                )

            install = json.loads(run("install", "--target", str(target)).stdout)
            run("verify", "--target", str(target))
            helper = target / "skills/phi9t-land/scripts/land.py"
            help_result = subprocess.run(
                [sys.executable, str(helper), "--help"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("--repo", help_result.stdout)
            for source in (ROOT / "skills").rglob("*"):
                if source.is_file():
                    installed = target / source.relative_to(ROOT)
                    self.assertEqual(installed.read_bytes(), source.read_bytes())
            run("restore", "--target", str(target), "--backup", install["backup"])
            self.assertFalse((target / "skills/phi9t/SKILL.md").exists())
            self.assertFalse(helper.exists())

    def test_vendored_trees_match_pins_and_refuse_edits(self):
        vendor = [sys.executable, str(ROOT / "scripts/vendor.py")]
        subprocess.run(vendor + ["check"], capture_output=True, check=True)
        manifest = json.loads((ROOT / "vendor.json").read_text())
        for spec in manifest["vendors"].values():
            package = ROOT / "skills" / spec["package"]
            self.assertTrue((package / "LICENSE").is_file())
            self.assertRegex(spec["commit"], r"^[0-9a-f]{40}$")
        poteto = ROOT / "skills/phi9t-pstack/poteto-mode/SKILL.md"
        self.assertTrue((poteto.parent.parent / "how/SKILL.md").is_file())
        original = poteto.read_bytes()
        try:
            poteto.write_bytes(original + b"\nedit\n")
            result = subprocess.run(vendor + ["check"], capture_output=True, text=True)
        finally:
            poteto.write_bytes(original)
        self.assertEqual(result.returncode, 1)
        self.assertIn("pstack: changed poteto-mode/SKILL.md", result.stderr)


if __name__ == "__main__":
    unittest.main()
