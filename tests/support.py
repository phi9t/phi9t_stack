"""Shared test helpers: git isolation, one hang guard, condition waits, snapshots."""

import atexit
import os
import shutil
import tempfile
import time
from pathlib import Path

# Tests build their own repositories and must not inherit the developer's
# global git configuration: hooks, URL rewrites and identity there change
# behavior and cost (a global commit hook made every test commit ~20x slower).
# The landing CLI deliberately drops GIT_* variables, so isolate through a
# disposable HOME, which every child process, including the CLIs, inherits.
_HOME = tempfile.mkdtemp(prefix="phi9t-test-home-")
atexit.register(shutil.rmtree, _HOME, True)
os.environ["HOME"] = _HOME
os.environ["XDG_CONFIG_HOME"] = os.path.join(_HOME, ".config")
os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
os.environ["GIT_TERMINAL_PROMPT"] = "0"

# A guard against a hung child process, not a claim about speed. Assertions
# never depend on elapsed time; raise it on a slow machine instead of editing tests.
HANG_GUARD = float(os.environ.get("PHI9T_TEST_HANG_GUARD", "120"))


def wait_for(condition, what, timeout=HANG_GUARD):
    """Poll until condition() is true; fail with a named reason on timeout."""
    deadline = time.monotonic() + timeout
    while not condition():
        if time.monotonic() > deadline:
            raise AssertionError("Timed out waiting for " + what)
        time.sleep(0.01)


def process_gone(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    return False


def tree_state(root, exclude=()):
    """Relative path -> (bytes, mode) for every regular file under root."""
    root = Path(root)
    return {
        path.relative_to(root).as_posix(): (
            path.read_bytes(),
            path.stat().st_mode & 0o777,
        )
        for path in sorted(root.rglob("*"))
        if path.is_file() and not set(path.relative_to(root).parts) & set(exclude)
    }
