#!/usr/bin/env python3
"""Cooperative local landing lane. POSIX, Python 3.9+, no remote publication."""

import argparse
import fcntl
import hashlib
import json
import os
import re
import signal
import sqlite3
import stat
import subprocess
import sys
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path


class Refusal(Exception):
    """The requested transition cannot safely proceed."""


@dataclass(frozen=True)
class Submission:
    commit: str
    base: str
    owner: str
    dependencies: list[dict]
    version: int


def environment() -> dict[str, str]:
    return {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }


def git(root: Path, *args: str, fd: int = -1, action: str = "") -> str:
    env = environment()
    if action:
        env["GIT_REFLOG_ACTION"] = action
    settings = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "config",
            "--name-only",
            "--get-regexp",
            r"^(filter\.|merge\..*\.driver$)",
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=15,
    )
    if settings.returncode not in (0, 1):
        raise Refusal("Cannot inspect Git conversion/merge policy")
    overrides = []
    drivers = {key.rsplit(".", 1)[0] for key in settings.stdout.splitlines()}
    for driver in sorted(drivers):
        values = (
            {"driver": "/usr/bin/false"}
            if driver.startswith("merge.")
            else {
                "clean": "/bin/cat",
                "smudge": "/bin/cat",
                "process": "",
                "required": "false",
            }
        )
        for key, value in values.items():
            overrides.extend(["-c", f"{driver}.{key}={value}"])
    result = subprocess.run(
        [
            "git",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "core.autocrlf=false",
            "-C",
            str(root),
            *overrides,
            *args,
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        pass_fds=(fd,) if fd >= 0 else (),
    )
    if result.returncode:
        raise Refusal(result.stderr.strip() or result.stdout.strip() or "Git refused")
    return result.stdout.strip()


def common_directory(root: Path) -> Path:
    value = Path(git(root, "rev-parse", "--git-common-dir"))
    return (root / value).resolve()


def encode(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def file_hash(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean(root: Path, commit: str) -> None:
    if git(root, "rev-parse", "HEAD") != commit:
        raise Refusal("Checkout HEAD changed")
    if git(root, "status", "--porcelain", "--untracked-files=all", "--ignored"):
        raise Refusal(
            "Checkout is dirty; tracked, untracked and ignored files are retained"
        )
    flags = git(root, "ls-files", "-v", "-z").split("\0")
    if any(entry and entry[0] != "H" for entry in flags):
        raise Refusal("Special index flags require inspection before verification")
    # Compare actual file bytes as well as Git's normalized/index view.
    entries = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-rz", commit],
        capture_output=True,
        check=True,
        timeout=30,
        env=environment(),
    ).stdout
    for entry in entries.split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        mode, _, blob = metadata.split()
        path = root / os.fsdecode(name)
        if mode == b"160000":
            raise Refusal("Submodules need a qualified landing adapter")
        expected_type = stat.S_ISLNK if mode == b"120000" else stat.S_ISREG
        if not expected_type(path.lstat().st_mode):
            raise Refusal("Checkout file type differs from candidate")
        data = (
            os.fsencode(os.readlink(path)) if mode == b"120000" else path.read_bytes()
        )
        header = f"blob {len(data)}\0".encode()
        if hashlib.sha1(header + data).hexdigest().encode() != blob:
            raise Refusal(
                "Checkout bytes differ from candidate; filters are unqualified"
            )
        if mode in (b"100644", b"100755"):
            if bool(path.stat().st_mode & 0o111) != (mode == b"100755"):
                raise Refusal("Checkout executable mode differs from candidate")


class Lane:
    def __init__(self, root: Path, fd: int):
        self.root = root
        self.fd = fd
        self.state = common_directory(root) / "phi9t-land"
        self.db: sqlite3.Connection
        self.opened = False

    def open(self, readonly: bool = False) -> None:
        if not (self.state / "queue.sqlite3").is_file():
            raise Refusal("Initialize this repository's landing lane first")
        database = self.state / "queue.sqlite3"
        self.db = sqlite3.connect(
            database.as_uri() + "?mode=ro" if readonly else str(database),
            isolation_level=None,
            uri=readonly,
        )
        self.opened = True
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA synchronous=FULL")
        if self.db.execute("SELECT COUNT(*) FROM config").fetchone()[0] != 1:
            raise Refusal("Incomplete initialization; retain state for inspection")

    def snapshot(self) -> dict:
        self.db.execute("BEGIN")
        try:
            return {
                "items": [
                    dict(row)
                    for row in self.db.execute("SELECT * FROM items ORDER BY rowid")
                ],
                "operation": self.operation(),
            }
        finally:
            self.db.execute("ROLLBACK")

    def config(self) -> dict:
        return json.loads(self.db.execute("SELECT data FROM config").fetchone()[0])

    def operation(self) -> dict:
        row = self.db.execute("SELECT data FROM operation WHERE id=1").fetchone()
        return json.loads(row[0]) if row else {}

    def record(self, operation: dict) -> None:
        self.db.execute(
            "INSERT OR REPLACE INTO operation VALUES(1,?)", (encode(operation),)
        )

    def event(self, kind: str, data: dict) -> None:
        self.db.execute(
            "INSERT INTO events(kind,data) VALUES(?,?)", (kind, encode(data))
        )

    def item(self, identifier: str) -> sqlite3.Row:
        row = self.db.execute(
            "SELECT * FROM items WHERE id=?", (identifier,)
        ).fetchone()
        if row is None:
            raise Refusal("Unknown item: " + identifier)
        return row

    def check_policy(self) -> dict:
        config = self.config()
        for path, pin in config["pins"].items():
            if (
                str(Path(path).resolve()) != pin["resolved"]
                or file_hash(path) != pin["sha256"]
            ):
                raise Refusal("Acceptance command/input changed: " + path)
        destination = Path(config["destination"])
        if common_directory(destination) != common_directory(self.root):
            raise Refusal("Destination repository changed")
        if git(destination, "symbolic-ref", "HEAD") != config["mainline"]:
            raise Refusal("Destination is not the configured mainline checkout")
        return config

    def submit(self, args, retry: bool = False) -> dict:
        if self.operation():
            raise Refusal("Unresolved operation: recover before changing the queue")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", args.id):
            raise Refusal(
                "Use a simple item ID (letters, digits, underscore or hyphen)"
            )
        old = self.item(args.id) if retry else None
        if old and old["status"] != "blocked":
            raise Refusal("Only a blocked item can be retried")
        if (
            not retry
            and self.db.execute("SELECT 1 FROM items WHERE id=?", (args.id,)).fetchone()
        ):
            raise Refusal("Item already exists")
        previous = json.loads(old["data"]) if old else {}
        commit = git(self.root, "rev-parse", "--verify", args.candidate + "^{commit}")
        base = git(self.root, "rev-parse", "--verify", args.base + "^{commit}")
        git(self.root, "merge-base", "--is-ancestor", base, commit)
        if commit == base or git(
            self.root, "rev-list", "--merges", base + ".." + commit
        ):
            raise Refusal(
                "Submit a nonempty linear contribution above the declared base"
            )
        dependencies = []
        names = (
            args.depends
            if args.depends is not None
            else [d["id"] for d in previous.get("dependencies", [])]
        )
        for name in names:
            if name == args.id:
                raise Refusal("An item cannot depend on itself")
            dependency = json.loads(self.item(name)["data"])
            dependencies.append({"id": name, "version": dependency["version"]})
        graph = {
            row["id"]: [d["id"] for d in json.loads(row["data"])["dependencies"]]
            for row in self.db.execute("SELECT id,data FROM items")
        }
        graph[args.id] = names

        def visit(name: str, ancestors: set[str]) -> None:
            if name in ancestors:
                raise Refusal("Dependency cycle")
            for parent in graph[name]:
                visit(parent, ancestors | {name})

        visit(args.id, set())
        version = previous.get("version", 0) + 1
        subject = asdict(
            Submission(
                commit=commit,
                base=base,
                owner=previous.get("owner") or args.owner,
                dependencies=dependencies,
                version=version,
            )
        )
        reference = f"refs/phi9t-land/{args.id}/v{version}"
        prepared = {"id": args.id, "reference": reference, **subject}
        prior = self.db.execute(
            "SELECT data FROM events WHERE kind='submission_prepared' "
            "AND json_extract(data,'$.reference')=? ORDER BY sequence DESC LIMIT 1",
            (reference,),
        ).fetchone()
        if prior and json.loads(prior[0]) != prepared:
            raise Refusal(
                "Interrupted submission has different inputs; inspect its event"
            )
        if not prior:
            self.event("submission_prepared", prepared)
        try:
            pinned = git(self.root, "rev-parse", "--verify", reference)
        except Refusal:
            pinned = ""
        if pinned and pinned != commit:
            raise Refusal("Existing candidate pin differs from submission")
        if not pinned:
            git(self.root, "update-ref", reference, commit, "0" * 40)
        if retry:
            self.db.execute(
                "UPDATE items SET data=?,status='ready',detail='' WHERE id=?",
                (encode(subject), args.id),
            )
        else:
            self.db.execute(
                "INSERT INTO items(id,data,status,detail) VALUES(?,?,'ready','')",
                (args.id, encode(subject)),
            )
        self.event("submitted", {"id": args.id, **subject})
        return {"id": args.id, "status": "ready", **subject}

    def eligible(self, row: sqlite3.Row) -> bool:
        for dependency in json.loads(row["data"])["dependencies"]:
            parent = self.item(dependency["id"])
            if json.loads(parent["data"])["version"] != dependency["version"]:
                self.db.execute(
                    "UPDATE items SET status='blocked',detail=? WHERE id=?",
                    ("Dependency version changed; explicitly retry", row["id"]),
                )
                return False
            if parent["status"] != "landed":
                return False
        return True

    def integrate(self, row: sqlite3.Row) -> dict:
        config = self.check_policy()
        destination = Path(config["destination"])
        base = git(destination, "rev-parse", "HEAD")
        clean(destination, base)
        subject = json.loads(row["data"])
        token = uuid.uuid4().hex
        directory = self.state / "attempts" / token
        directory.mkdir(parents=True)
        workspace = directory / "worktree"
        operation = {
            "id": row["id"],
            "attempt": token,
            "base": base,
            "workspace": str(workspace),
            "stage": "preparing",
            "subject": subject,
        }
        self.record(operation)
        self.event("preparing", operation)
        try:
            git(
                self.root,
                "worktree",
                "add",
                "--detach",
                str(workspace),
                subject["commit"],
                fd=self.fd,
            )
            if subject["base"] != base:
                git(
                    workspace,
                    "-c",
                    "rebase.updateRefs=false",
                    "rebase",
                    "--no-update-refs",
                    "--onto",
                    base,
                    subject["base"],
                    fd=self.fd,
                )
            candidate = git(workspace, "rev-parse", "HEAD")
            git(workspace, "merge-base", "--is-ancestor", base, candidate)
            if candidate == base:
                raise Refusal("Contribution became empty; review as superseded")
            clean(workspace, candidate)
            git(self.root, "update-ref", f"refs/phi9t-land/attempts/{token}", candidate)
            operation.update(stage="checking", candidate=candidate)
            operation["checks"] = []
            self.record(operation)
            for number, check in enumerate(config["checks"]):
                argv = [
                    str(workspace) if value == "{worktree}" else value
                    for value in check
                ]
                with (directory / f"check-{number}.log").open("wb") as log:
                    process = subprocess.Popen(
                        argv,
                        cwd=workspace,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        env=environment(),
                        start_new_session=True,
                        pass_fds=(self.fd,),
                    )
                    operation["pid"] = process.pid
                    self.record(operation)
                    try:
                        code = process.wait(timeout=config["timeout"])
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=10)
                        raise Refusal("Acceptance timed out; output retained") from None
                    if code:
                        raise Refusal(
                            f"Acceptance check {number} exited {code}; output retained"
                        )
                    log.flush()
                    os.fsync(log.fileno())
                operation["checks"].append(
                    {
                        "argv": argv,
                        "exit": code,
                        "log": str(directory / f"check-{number}.log"),
                        "sha256": file_hash(str(directory / f"check-{number}.log")),
                    }
                )
                self.record(operation)
            clean(workspace, candidate)
            self.check_policy()
            if git(destination, "rev-parse", "HEAD") != base:
                raise Refusal(
                    "Mainline moved during verification; retry against its new tip"
                )
            clean(destination, base)
        except (Refusal, OSError, subprocess.SubprocessError) as error:
            self.db.execute(
                "UPDATE items SET status='blocked',detail=? WHERE id=?",
                (str(error), row["id"]),
            )
            self.event("blocked", {**operation, "reason": str(error)})
            self.db.execute("DELETE FROM operation")
            return {"id": row["id"], "status": "blocked", "reason": str(error)}

        operation["stage"] = "landing"
        self.event("verified", operation)
        self.record(operation)
        git(
            destination,
            "merge",
            "--ff-only",
            "--no-autostash",
            "--no-overwrite-ignore",
            candidate,
            fd=self.fd,
            action="phi9t-land:" + token,
        )
        clean(destination, candidate)
        return self.finish(operation)

    def finish(self, operation: dict) -> dict:
        result = {
            "id": operation["id"],
            "status": "landed",
            "candidate": operation["candidate"],
            "base": operation["base"],
            "attempt": operation["attempt"],
        }
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self.event("landed", result)
            self.db.execute(
                "UPDATE items SET status='landed',detail=? WHERE id=?",
                (encode(result), operation["id"]),
            )
            self.db.execute("DELETE FROM operation")
            self.db.execute("COMMIT")
        except sqlite3.Error:
            self.db.execute("ROLLBACK")
            raise
        return result

    def recover(self, stopped: bool, not_landed: bool) -> dict:
        operation = self.operation()
        if not operation:
            return {"status": "idle"}
        if operation["stage"] == "landing":
            config = self.check_policy()
            destination = Path(config["destination"])
            candidate = operation["candidate"]
            log = git(
                destination, "reflog", "show", "--format=%H %gs", config["mainline"]
            )
            marker = "phi9t-land:" + operation["attempt"]
            lines = log.splitlines()
            attributed = any(
                line.startswith(candidate + " ")
                and marker in line
                and index + 1 < len(lines)
                and lines[index + 1].startswith(operation["base"] + " ")
                for index, line in enumerate(lines)
            )
            if attributed:
                git(
                    destination,
                    "merge-base",
                    "--is-ancestor",
                    candidate,
                    config["mainline"],
                )
                clean(destination, git(destination, "rev-parse", "HEAD"))
                return {**self.finish(operation), "reconciled": True}
            if not (stopped and not_landed):
                raise Refusal(
                    "Unattributed landing: retain lane for operator reconciliation"
                )
            clean(destination, operation["base"])
        if not stopped:
            raise Refusal("Confirm prior owned checks stopped with recover --stopped")
        reason = (
            "Interrupted preparation/check; retained for inspection and explicit retry"
        )
        self.event("interrupted", operation)
        self.db.execute(
            "UPDATE items SET status='blocked',detail=? WHERE id=?",
            (reason, operation["id"]),
        )
        self.db.execute("DELETE FROM operation")
        return {"id": operation["id"], "status": "blocked", "reason": reason}


@contextmanager
def locked_lane(root: Path):
    common = common_directory(root)
    path = common / "phi9t-land.lock"
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Refusal(
                "Another integrator or its check owns this repository's landing lane"
            ) from None
        lane = Lane(root, fd)
        try:
            yield lane
        finally:
            if lane.opened:
                lane.db.close()
    finally:
        os.close(fd)


def initialize(lane: Lane, args) -> dict:
    if not args.acknowledge_local_landing:
        raise Refusal(
            "Acknowledge local landing authority and disabled hooks explicitly"
        )
    if lane.state.exists():
        raise Refusal(
            "Landing state already exists; initialization never overwrites it"
        )
    destination = Path(args.destination).resolve()
    mainline = "refs/heads/" + args.mainline
    if common_directory(destination) != common_directory(lane.root):
        raise Refusal("Destination must be a checkout of this repository")
    if git(destination, "symbolic-ref", "HEAD") != mainline:
        raise Refusal("Destination must have the declared mainline checked out")
    if git(destination, "rev-parse", "--show-object-format") != "sha1":
        raise Refusal("This version supports SHA-1 Git repositories only")
    clean(destination, git(destination, "rev-parse", "HEAD"))
    checks = json.loads(args.checks)
    if not isinstance(checks, list) or not checks or args.timeout <= 0:
        raise Refusal("Provide nonempty acceptance argv checks and a positive timeout")
    pins = {}
    for check in checks:
        if (
            not isinstance(check, list)
            or not check
            or not all(isinstance(x, str) and x for x in check)
        ):
            raise Refusal("Each check must be a nonempty string argv array")
        if not Path(check[0]).is_absolute():
            raise Refusal("Acceptance executables must have absolute paths")
        if not Path(check[0]).is_file() or not os.access(check[0], os.X_OK):
            raise Refusal("Acceptance executable must exist and be executable")
        if Path(check[0]).name.startswith(("python", "pypy")):
            scripts = [value for value in check[1:] if not value.startswith("-")]
            if (
                "-m" in check
                or "-c" in check
                or not scripts
                or not Path(scripts[0]).is_absolute()
                or not Path(scripts[0]).is_file()
            ):
                raise Refusal(
                    "Python acceptance requires an existing absolute checker file"
                )
        for value in check:
            path = Path(value)
            if path.is_absolute() and not path.is_file():
                raise Refusal("Absolute acceptance file arguments must exist")
            if (
                not path.is_absolute()
                and value != "{worktree}"
                and not value.startswith("-")
                and path.suffix in (".py", ".sh")
            ):
                raise Refusal("Checker scripts must use absolute file paths")
            if path.is_absolute() and path.is_file():
                resolved = path.resolve()
                if (
                    destination == resolved
                    or destination in resolved.parents
                    or lane.root in resolved.parents
                ):
                    raise Refusal(
                        "Acceptance tools/inputs must be owned outside worker source"
                    )
                pins[str(path)] = {
                    "resolved": str(resolved),
                    "sha256": file_hash(str(path)),
                }
    lane.state.mkdir(mode=0o700)
    lane.db = sqlite3.connect(lane.state / "queue.sqlite3", isolation_level=None)
    lane.opened = True
    lane.db.row_factory = sqlite3.Row
    lane.db.execute("PRAGMA synchronous=FULL")
    lane.db.executescript("""
        CREATE TABLE config(data TEXT NOT NULL);
        CREATE TABLE items(id TEXT PRIMARY KEY,data TEXT NOT NULL,
                           status TEXT NOT NULL,detail TEXT NOT NULL);
        CREATE TABLE operation(id INTEGER PRIMARY KEY CHECK(id=1),data TEXT NOT NULL);
        CREATE TABLE events(sequence INTEGER PRIMARY KEY,
                            kind TEXT NOT NULL,data TEXT NOT NULL);
    """)
    config = {
        "mainline": mainline,
        "destination": str(destination),
        "checks": checks,
        "pins": pins,
        "timeout": args.timeout,
        "hooks": "disabled; acceptance must cover required policy",
    }
    lane.db.execute("INSERT INTO config VALUES(?)", (encode(config),))
    return {"status": "initialized", "config": config, "state": str(lane.state)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--mainline", required=True)
    init.add_argument("--destination", required=True)
    init.add_argument("--checks", required=True)
    init.add_argument("--timeout", type=float, default=300)
    init.add_argument("--acknowledge-local-landing", action="store_true")
    for name in ("submit", "retry"):
        command = commands.add_parser(name)
        command.add_argument("--id", required=True)
        command.add_argument("--candidate", required=True)
        command.add_argument("--base", required=True)
        command.add_argument("--depends", action="append", default=None)
        command.add_argument("--owner", required=name == "submit")
    commands.add_parser("status")
    run = commands.add_parser("run")
    run.add_argument("--id")
    recover = commands.add_parser("recover")
    recover.add_argument("--stopped", action="store_true")
    recover.add_argument("--not-landed", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "status":
            lane = Lane(Path(args.repo).resolve(), -1)
            try:
                lane.open(readonly=True)
                print(json.dumps(lane.snapshot(), indent=2))
                return 0
            finally:
                if lane.opened:
                    lane.db.close()
        with locked_lane(Path(args.repo).resolve()) as lane:
            if args.command == "init":
                result = initialize(lane, args)
            else:
                lane.open()
                if args.command in ("submit", "retry"):
                    result = lane.submit(args, retry=args.command == "retry")
                elif args.command == "recover":
                    result = lane.recover(args.stopped, args.not_landed)
                else:
                    if lane.operation():
                        raise Refusal(
                            "Unresolved operation blocks the lane; recover first"
                        )
                    lane.check_policy()
                    results = []
                    rows = list(
                        lane.db.execute(
                            "SELECT * FROM items WHERE status='ready' ORDER BY rowid"
                        )
                    )
                    if args.id:
                        if lane.item(args.id)["status"] != "ready":
                            raise Refusal("Requested item is not ready")
                        rows = [row for row in rows if row["id"] == args.id]
                    for row in rows:
                        if lane.eligible(row):
                            results.append(lane.integrate(row))
                    unfinished = lane.db.execute(
                        "SELECT COUNT(*) FROM items WHERE status!='landed'"
                    ).fetchone()[0]
                    selected_incomplete = (
                        lane.item(args.id)["status"] != "landed"
                        if args.id
                        else unfinished > 0
                    )
                    result = {
                        "results": results,
                        "status": "incomplete" if selected_incomplete else "complete",
                        "queue_unfinished": unfinished,
                    }
            print(json.dumps(result, indent=2))
            return (
                1
                if result.get("status") == "incomplete" and args.command == "run"
                else 0
            )
    except (
        Refusal,
        OSError,
        ValueError,
        sqlite3.Error,
        subprocess.SubprocessError,
    ) as error:
        print(json.dumps({"status": "refused", "reason": str(error)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
