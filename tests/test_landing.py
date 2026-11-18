"""Drive the public landing CLI against real repositories and acceptance scripts."""

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import HANG_GUARD, process_gone, wait_for

CLI = Path(
    os.environ.get(
        "PHI9T_LANDING_CLI",
        str(Path(__file__).resolve().parents[1] / "skills/phi9t-land/scripts/land.py"),
    )
)


class LandingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="phi9t-land-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Landing test")
        self.git("config", "user.email", "test@example.invalid")
        (self.repo / "base.txt").write_text("BASE\n")
        self.git("add", "base.txt")
        self.git("commit", "-m", "Baseline")
        self.base = self.git("rev-parse", "HEAD")
        self.oracle = self.root / "oracle.py"
        self.oracle.write_text(
            "import pathlib,sys\n"
            "root=pathlib.Path(sys.argv[1])\n"
            "assert all(p.read_text()==p.stem.upper()+'\\n' "
            "for p in root.glob('*.txt'))\n"
        )

    def git(self, *args, cwd=None):
        return subprocess.run(
            ["git", *args],
            cwd=cwd or self.repo,
            text=True,
            capture_output=True,
            check=True,
            timeout=HANG_GUARD,
        ).stdout.strip()

    def cli(self, *args, ok=True):
        result = subprocess.run(
            [sys.executable, str(CLI), "--repo", str(self.repo), *args],
            text=True,
            capture_output=True,
            timeout=HANG_GUARD,
        )
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return json.loads(result.stdout)

    def initialize(self, timeout=HANG_GUARD):
        return self.cli(
            "init",
            "--acknowledge-local-landing",
            "--mainline",
            "main",
            "--destination",
            str(self.repo),
            "--checks",
            json.dumps([[sys.executable, str(self.oracle), "{worktree}"]]),
            "--timeout",
            str(timeout),
        )

    def candidate(self, name, value=None, base=None):
        worktree = self.root / name
        self.git(
            "worktree", "add", "-b", f"task-{name}", str(worktree), base or self.base
        )
        (worktree / f"{name}.txt").write_text(value or name.upper() + "\n")
        self.git("add", f"{name}.txt", cwd=worktree)
        self.git("commit", "-m", name, cwd=worktree)
        return self.git("rev-parse", "HEAD", cwd=worktree)

    def submit(self, name, candidate=None, dependencies=()):
        args = [
            "submit",
            "--id",
            name,
            "--candidate",
            candidate or self.candidate(name),
            "--base",
            self.base,
            "--owner",
            "test-agent",
        ]
        for dependency in dependencies:
            args.extend(["--depends", dependency])
        return self.cli(*args)

    def test_two_candidates_rebase_land_and_keep_linear_history(self):
        self.initialize()
        self.submit("a")
        self.submit("b")
        result = self.cli("run")
        self.assertEqual([x["id"] for x in result["results"]], ["a", "b"])
        self.assertTrue(all(x["status"] == "landed" for x in result["results"]))
        self.assertEqual((self.repo / "a.txt").read_text(), "A\n")
        self.assertEqual((self.repo / "b.txt").read_text(), "B\n")
        self.assertEqual(self.git("rev-list", "--count", "--merges", "main"), "0")
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_failed_item_does_not_block_independent_item(self):
        self.initialize()
        self.submit("bad", self.candidate("bad", "wrong\n"))
        self.submit("dependent", dependencies=("bad",))
        self.submit("good")
        self.cli("run", ok=False)
        items = {x["id"]: x for x in self.cli("status")["items"]}
        self.assertEqual(items["bad"]["status"], "blocked")
        self.assertEqual(items["dependent"]["status"], "ready")
        self.assertEqual(items["good"]["status"], "landed")
        self.assertFalse((self.repo / "bad.txt").exists())

    def test_dirty_destination_and_untracked_collision_are_preserved(self):
        self.initialize()
        self.submit("a")
        (self.repo / "a.txt").write_text("human work\n")
        self.cli("run", ok=False)
        self.assertEqual((self.repo / "a.txt").read_text(), "human work\n")
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)

    def test_checker_mutation_blocks_without_landing(self):
        self.oracle.write_text(
            "import pathlib,sys\n"
            "pathlib.Path(sys.argv[1],'base.txt').write_text('mutated')\n"
        )
        self.initialize()
        self.submit("a")
        self.cli("run", ok=False)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)
        self.assertEqual((self.repo / "base.txt").read_text(), "BASE\n")

    def test_checker_drift_refuses_even_when_new_checker_passes(self):
        self.initialize()
        self.submit("a")
        self.oracle.write_text("pass\n")
        self.cli("run", ok=False)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)

    def test_unknown_dependencies_and_duplicate_ids_refuse(self):
        self.initialize()
        candidate = self.candidate("a")
        self.cli(
            "submit",
            "--id",
            "a",
            "--candidate",
            candidate,
            "--base",
            self.base,
            "--owner",
            "test",
            "--depends",
            "missing",
            ok=False,
        )
        self.submit("a", candidate)
        self.cli(
            "submit",
            "--id",
            "a",
            "--candidate",
            candidate,
            "--base",
            self.base,
            "--owner",
            "test",
            ok=False,
        )

    def test_failed_check_can_retry_with_repaired_immutable_candidate(self):
        self.initialize()
        self.submit("a", self.candidate("a", "wrong\n"))
        self.cli("run", ok=False)
        worktree = self.root / "a"
        (worktree / "a.txt").write_text("A\n")
        self.git("add", "a.txt", cwd=worktree)
        self.git("commit", "-m", "Repair", cwd=worktree)
        candidate = self.git("rev-parse", "HEAD", cwd=worktree)
        self.cli("retry", "--id", "a", "--candidate", candidate, "--base", self.base)
        self.cli("run", "--id", "a")
        self.assertEqual(self.cli("status")["items"][0]["status"], "landed")

    def test_timeout_blocks_and_preserves_mainline(self):
        self.oracle.write_text("import time\ntime.sleep(60)\n")
        self.initialize(timeout=0.2)
        self.submit("a")
        self.cli("run", ok=False)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)

    def test_submission_pins_commit_even_if_worker_branch_moves(self):
        self.initialize()
        candidate = self.candidate("a")
        self.submit("a", candidate)
        workspace = self.root / "a"
        (workspace / "a.txt").write_text("worker changed its mind\n")
        self.git("add", "a.txt", cwd=workspace)
        self.git("commit", "-m", "Later unrelated revision", cwd=workspace)
        self.cli("run", "--id", "a")
        self.assertEqual((self.repo / "a.txt").read_text(), "A\n")
        self.assertEqual((workspace / "a.txt").read_text(), "worker changed its mind\n")

    def test_checker_symlink_retargeting_is_rejected(self):
        original = self.root / "original.py"
        self.oracle.rename(original)
        self.oracle.symlink_to(original)
        self.initialize()
        self.submit("a", self.candidate("a", "wrong\n"))
        replacement = self.root / "replacement.py"
        replacement.write_text("pass\n")
        self.oracle.unlink()
        self.oracle.symlink_to(replacement)
        self.cli("run", ok=False)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)

    def test_rebase_cannot_update_original_contributor_refs(self):
        self.initialize()
        candidate = self.candidate("a")
        self.git("branch", "contributor-preserved", candidate)
        self.submit("a", candidate)
        self.git("config", "rebase.updateRefs", "true")
        self.submit("b")
        self.cli("run", "--id", "b")
        self.cli("run", "--id", "a")
        self.assertEqual(self.git("rev-parse", "contributor-preserved"), candidate)

    def test_bare_fast_forward_accepts_bad_code_guarded_lane_does_not(self):
        candidate = self.candidate("a", "wrong\n")
        raw = self.root / "raw"
        self.git("worktree", "add", "-b", "raw-main", str(raw), self.base)
        self.git("merge", "--ff-only", candidate, cwd=raw)
        self.assertEqual((raw / "a.txt").read_text(), "wrong\n")
        self.initialize()
        self.submit("a", candidate)
        self.cli("run", ok=False)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)

    def run_and_interrupt_git(self, command, phase):
        """Kill the integrator while one selected git call is parked.

        The fake git records its pid and parks on a release file, so the kill
        lands at a known point. The test then releases it and waits for that
        orphaned child to exit before inspecting the repository.
        """
        actual_git = shutil.which("git")
        marker, release = self.root / "parked", self.root / "release"
        tools = self.root / "bin"
        tools.mkdir()
        if phase == "submission":
            select = "selected='update-ref' in args and 'refs/phi9t-land/a/v1' in args"
        else:
            select = "selected='merge' in args and '--ff-only' in args"
        park = (
            "if selected:\n"
            f" pathlib.Path({str(marker)!r}).write_text(str(os.getpid()))\n"
            f" deadline=time.monotonic()+{HANG_GUARD}\n"
            f" while not pathlib.Path({str(release)!r}).exists():\n"
            "  assert time.monotonic()<deadline\n"
            "  time.sleep(0.01)\n"
        )
        real_git = f"result=subprocess.run([{actual_git!r},*args],env=os.environ)\n"
        if phase == "before":
            body = park + " sys.exit(1)\n" + real_git
        else:
            body = real_git + park
        wrapper = tools / "git"
        wrapper.write_text(
            f"#!{sys.executable}\n"
            "import os,pathlib,subprocess,sys,time\nargs=sys.argv[1:]\n"
            + select
            + "\n"
            + body
            + "sys.exit(result.returncode)\n"
        )
        wrapper.chmod(0o755)
        process = subprocess.Popen(
            [sys.executable, str(CLI), "--repo", str(self.repo), *command],
            env=dict(os.environ, PATH=str(tools) + os.pathsep + os.environ["PATH"]),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        wait_for(lambda: marker.exists() and marker.read_text(), "git to park")
        parked = int(marker.read_text())
        os.kill(process.pid, signal.SIGKILL)
        process.communicate(timeout=HANG_GUARD)
        release.write_text("go")
        wait_for(lambda: process_gone(parked), "the orphaned git call to exit")

    def test_death_after_git_reconciles_without_duplicate_commits(self):
        self.initialize()
        self.submit("a")
        self.run_and_interrupt_git(["run"], "after")
        head = self.git("rev-parse", "HEAD")
        self.cli("run", ok=False)
        result = self.cli("recover")
        self.assertTrue(result["reconciled"])
        self.assertEqual(result["candidate"], head)
        self.assertEqual(self.git("rev-list", "--count", "main"), "2")
        self.cli("run")
        self.assertEqual(self.git("rev-parse", "HEAD"), head)

    def test_death_before_git_retains_uncertain_lane_until_operator_resolution(self):
        self.initialize()
        self.submit("a")
        self.run_and_interrupt_git(["run"], "before")
        self.cli("recover", ok=False)
        self.cli("run", ok=False)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)
        result = self.cli("recover", "--stopped", "--not-landed")
        self.assertEqual(result["status"], "blocked")

    def test_death_after_submission_pin_allows_identical_resubmission(self):
        self.initialize()
        candidate = self.candidate("a")
        command = [
            "submit",
            "--id",
            "a",
            "--candidate",
            candidate,
            "--base",
            self.base,
            "--owner",
            "test-agent",
        ]
        self.run_and_interrupt_git(command, "submission")
        self.cli(*command)
        self.cli("run")
        self.assertEqual((self.repo / "a.txt").read_text(), "A\n")

    def test_zero_exit_checker_that_commits_new_head_is_rejected(self):
        self.oracle.write_text(
            "import pathlib,subprocess,sys\nroot=sys.argv[1]\n"
            "pathlib.Path(root,'a.txt').write_text('wrong\\n')\n"
            "subprocess.run(['git','add','a.txt'],cwd=root,check=True)\n"
            "subprocess.run(['git','commit',"
            "'-m','tamper'],cwd=root,check=True)\n"
        )
        self.initialize()
        self.submit("a")
        self.cli("run", ok=False)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)

    def test_rebase_conflict_preserves_worker_and_mainline(self):
        self.initialize()
        candidate = self.candidate("a")
        workspace = self.root / "a"
        (workspace / "base.txt").write_text("worker\n")
        self.git("add", "base.txt", cwd=workspace)
        self.git("commit", "-m", "Worker base edit", cwd=workspace)
        candidate = self.git("rev-parse", "HEAD", cwd=workspace)
        self.submit("a", candidate)
        (self.repo / "base.txt").write_text("operator\n")
        self.git("add", "base.txt")
        self.git("commit", "-m", "Competing edit")
        destination = self.git("rev-parse", "HEAD")
        (workspace / "private-note").write_text("retain\n")
        self.cli("run", ok=False)
        self.assertEqual(self.git("rev-parse", "HEAD"), destination)
        self.assertEqual(self.git("rev-parse", "HEAD", cwd=workspace), candidate)
        self.assertEqual((workspace / "private-note").read_text(), "retain\n")

    def start_with_gate(self):
        marker, release = self.root / "started", self.root / "release"
        self.oracle.write_text(
            "import pathlib,time\n"
            f"pathlib.Path({str(marker)!r}).write_text('started')\n"
            f"release=pathlib.Path({str(release)!r})\n"
            f"deadline=time.monotonic()+{HANG_GUARD}\n"
            "while not release.exists() and time.monotonic()<deadline:\n"
            " time.sleep(.01)\n"
            "assert release.exists()\n"
        )
        self.initialize()
        self.submit("a")
        process = subprocess.Popen(
            [sys.executable, str(CLI), "--repo", str(self.repo), "run", "--id", "a"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        wait_for(marker.exists, "the checker to start")
        return process, release

    def test_direct_and_queued_runners_share_one_lane(self):
        process, release = self.start_with_gate()
        snapshot = self.cli("status")
        self.assertEqual(snapshot["operation"]["stage"], "checking")
        denied = self.cli("run", ok=False)
        self.assertIn("owns", denied["reason"])
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)
        release.write_text("go")
        output, errors = process.communicate(timeout=HANG_GUARD)
        self.assertEqual(process.returncode, 0, output + errors)
        self.assertEqual((self.repo / "a.txt").read_text(), "A\n")

    def test_mainline_moving_during_check_invalidates_result(self):
        process, release = self.start_with_gate()
        (self.repo / "other.txt").write_text("OTHER\n")
        self.git("add", "other.txt")
        self.git("commit", "-m", "External writer moved mainline")
        moved = self.git("rev-parse", "HEAD")
        release.write_text("go")
        output, errors = process.communicate(timeout=HANG_GUARD)
        self.assertEqual(process.returncode, 1, output + errors)
        self.assertEqual(self.git("rev-parse", "HEAD"), moved)
        self.assertFalse((self.repo / "a.txt").exists())

    def test_dependency_cycle_on_retry_is_rejected(self):
        self.initialize()
        candidate = self.candidate("a", "bad\n")
        self.submit("a", candidate)
        self.submit("b", dependencies=("a",))
        self.cli("run", ok=False)
        self.cli(
            "retry",
            "--id",
            "a",
            "--candidate",
            candidate,
            "--base",
            self.base,
            "--depends",
            "b",
            ok=False,
        )

    def test_reinitialization_refuses(self):
        self.initialize()
        self.initialize_refusal = self.cli(
            "init",
            "--mainline",
            "main",
            "--destination",
            str(self.repo),
            "--acknowledge-local-landing",
            "--checks",
            "[]",
            ok=False,
        )
        self.assertIn("already exists", self.initialize_refusal["reason"])

    def test_foreign_destination_is_rejected(self):
        other = self.root / "foreign"
        other.mkdir()
        self.git("init", "-b", "main", cwd=other)
        result = self.cli(
            "init",
            "--mainline",
            "main",
            "--destination",
            str(other),
            "--acknowledge-local-landing",
            "--checks",
            "[]",
            ok=False,
        )
        self.assertIn("this repository", result["reason"])

    def test_candidate_relative_checker_is_rejected_at_initialization(self):
        result = self.cli(
            "init",
            "--mainline",
            "main",
            "--destination",
            str(self.repo),
            "--acknowledge-local-landing",
            "--checks",
            json.dumps([[sys.executable, "verify.py", "{worktree}"]]),
            ok=False,
        )
        self.assertIn("absolute checker", result["reason"])

    def test_zero_exit_checker_with_hidden_index_changes_is_rejected(self):
        self.oracle.write_text(
            "import pathlib,subprocess,sys\nroot=sys.argv[1]\n"
            "subprocess.run(['git','update-index','--assume-unchanged','a.txt'],"
            "cwd=root,check=True)\n"
            "pathlib.Path(root,'a.txt').write_text('hidden change\\n')\n"
        )
        self.initialize()
        self.submit("a")
        self.cli("run", ok=False)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)

    def test_dependency_version_change_needs_explicit_rebinding(self):
        self.initialize()
        first = self.candidate("a", "bad\n")
        self.submit("a", first)
        dependent = self.candidate("b")
        self.submit("b", dependent, dependencies=("a",))
        self.cli("run", ok=False)
        workspace = self.root / "a"
        (workspace / "a.txt").write_text("A\n")
        self.git("add", "a.txt", cwd=workspace)
        self.git("commit", "-m", "Repair", cwd=workspace)
        repaired = self.git("rev-parse", "HEAD", cwd=workspace)
        self.cli("retry", "--id", "a", "--candidate", repaired, "--base", self.base)
        self.cli("run", ok=False)
        items = {x["id"]: x for x in self.cli("status")["items"]}
        self.assertEqual(items["b"]["status"], "blocked")
        self.cli("retry", "--id", "b", "--candidate", dependent, "--base", self.base)
        self.cli("run")
        self.assertEqual((self.repo / "a.txt").read_text(), "A\n")
        self.assertEqual((self.repo / "b.txt").read_text(), "B\n")

    def test_ignored_files_are_preserved(self):
        (self.repo / ".gitignore").write_text("*.private\n")
        self.git("add", ".gitignore")
        self.git("commit", "-m", "Ignore local notes")
        self.base = self.git("rev-parse", "HEAD")
        self.initialize()
        self.submit("a")
        note = self.repo / "operator.private"
        note.write_text("keep me\n")
        self.cli("run", ok=False)
        self.assertEqual(note.read_text(), "keep me\n")

    def test_killed_integrator_cannot_be_silently_retried(self):
        marker, release = self.root / "checking", self.root / "release"
        self.oracle.write_text(
            "import os,pathlib,time\n"
            f"pathlib.Path({str(marker)!r}).write_text(str(os.getpid()))\n"
            f"deadline=time.monotonic()+{HANG_GUARD}\n"
            f"while not pathlib.Path({str(release)!r}).exists():\n"
            " assert time.monotonic()<deadline\n"
            " time.sleep(0.01)\n"
        )
        self.initialize()
        self.submit("a")
        process = subprocess.Popen(
            [sys.executable, str(CLI), "--repo", str(self.repo), "run"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        wait_for(lambda: marker.exists() and marker.read_text(), "the checker to start")
        checker = int(marker.read_text())
        os.kill(process.pid, signal.SIGKILL)
        process.communicate(timeout=HANG_GUARD)
        self.cli("run", ok=False)
        release.write_text("go")
        wait_for(lambda: process_gone(checker), "the orphaned checker to exit")
        recovered = self.cli("recover", "--stopped")
        self.assertEqual(recovered["status"], "blocked")
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)


if __name__ == "__main__":
    unittest.main()
