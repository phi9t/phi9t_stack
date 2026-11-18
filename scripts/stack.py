#!/usr/bin/env python3
"""Validate, install and restore phi9t packages. Python 3.9+, POSIX."""

import argparse
import base64
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile
import uuid
from collections.abc import Generator, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Optional
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ".phi9t/manifest.json"


class Refusal(Exception):
    pass


@dataclass(frozen=True)
class FileIdentity:
    sha256: str
    mode: int

    def to_record(self) -> dict:
        return {"sha256": self.sha256, "mode": self.mode}


@dataclass(frozen=True)
class FileSnapshot:
    data: bytes
    mode: int

    @property
    def identity(self) -> FileIdentity:
        return FileIdentity(digest(self.data), self.mode)

    def to_record(self) -> dict:
        return {"data": base64.b64encode(self.data).decode(), "mode": self.mode}


@dataclass(frozen=True)
class InstallationManifest:
    files: Mapping[str, FileIdentity]

    def __post_init__(self) -> None:
        object.__setattr__(self, "files", MappingProxyType(dict(self.files)))

    def to_record(self) -> dict:
        return {
            "schema": 2,
            "files": {name: value.to_record() for name, value in self.files.items()},
        }


@dataclass(frozen=True)
class Transaction:
    target: str
    before: Mapping[str, Optional[FileSnapshot]]
    after: Mapping[str, Optional[FileSnapshot]]

    def __post_init__(self) -> None:
        object.__setattr__(self, "before", MappingProxyType(dict(self.before)))
        object.__setattr__(self, "after", MappingProxyType(dict(self.after)))

    def to_record(self) -> dict:
        return {
            "schema": 1,
            "target": self.target,
            "before": {
                name: state.to_record() if state is not None else None
                for name, state in self.before.items()
            },
            "after": {
                name: state.to_record() if state is not None else None
                for name, state in self.after.items()
            },
        }


def parse_snapshot(value: object) -> Optional[FileSnapshot]:
    if value is None:
        return None
    if (
        not isinstance(value, dict)
        or set(value) != {"data", "mode"}
        or not isinstance(value["mode"], int)
        or not 0 <= value["mode"] <= 0o777
    ):
        raise Refusal("Invalid backup file state")
    return FileSnapshot(base64.b64decode(value["data"], validate=True), value["mode"])


def parse_identity(value: object, relative: str) -> FileIdentity:
    if (
        not isinstance(value, dict)
        or set(value) != {"sha256", "mode"}
        or not isinstance(value["sha256"], str)
        or not re.fullmatch("[a-f0-9]{64}", value["sha256"])
        or not isinstance(value["mode"], (int, float))
        or not 0 <= value["mode"] <= 0o777
        or int(value["mode"]) != value["mode"]
    ):
        raise Refusal("Invalid owned file record: " + relative)
    return FileIdentity(value["sha256"], int(value["mode"]))


def parse_manifest(value: object) -> InstallationManifest:
    if (
        not isinstance(value, dict)
        or value.get("schema") != 2
        or not isinstance(value.get("files"), dict)
    ):
        raise Refusal("Unsupported installation manifest")
    files = {}
    for relative, record in value["files"].items():
        if not relative.startswith("skills/phi9t"):
            raise Refusal("Unexpected owned path: " + relative)
        file_identity = parse_identity(record, relative)
        if file_identity.mode not in (0o644, 0o755):
            raise Refusal("Invalid owned file record: " + relative)
        files[relative] = file_identity
    return InstallationManifest(files)


def parse_transaction(value: dict, target: Path) -> Transaction:
    if value.get("schema") != 1 or value.get("target") != str(target):
        raise Refusal("Backup belongs to a different target or schema")
    before, after = value.get("before"), value.get("after")
    if (
        not isinstance(before, dict)
        or not isinstance(after, dict)
        or set(before) != set(after)
    ):
        raise Refusal("Backup must contain matching before and after paths")
    transaction = Transaction(
        str(target),
        {name: parse_snapshot(state) for name, state in before.items()},
        {name: parse_snapshot(state) for name, state in after.items()},
    )
    for relative in transaction.after:
        if relative != MANIFEST and not relative.startswith(
            ("skills/", "commands/", "agents/")
        ):
            raise Refusal("Unexpected backup path: " + relative)
    return transaction


def encode(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def path_at(root: Path, relative: str) -> Path:
    parts = PurePosixPath(relative).parts
    if not parts or relative.startswith("/") or any(p in (".", "..") for p in parts):
        raise Refusal("Unsafe relative path: " + relative)
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise Refusal("Symlink at " + str(current))
    return current


def snapshot(path: Path) -> Optional[FileSnapshot]:
    if path.is_symlink():
        raise Refusal("Symlink at " + str(path))
    if not path.exists():
        return None
    if not path.is_file():
        raise Refusal("Expected a regular file: " + str(path))
    return FileSnapshot(path.read_bytes(), path.stat().st_mode & 0o777)


def identity(state: Optional[FileSnapshot]) -> Optional[FileIdentity]:
    return state.identity if state is not None else None


def atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".phi9t-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def apply_state(path: Path, state: Optional[FileSnapshot]) -> None:
    if state is None:
        if path.exists():
            path.unlink()
    else:
        atomic_write(path, state.data, state.mode)


def read_json(path: Path) -> object:
    return json.loads(path.read_text())


def markdown_targets(text: str) -> Iterator[str]:
    """Local resource destinations in inline links and reference definitions."""
    # Resource names use URI-escaped spaces/parentheses or angle destinations.
    # Ignore fenced examples; they do not ask the reader to open a resource.
    text = re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$", "", text)
    destination = r"(?:<([^>\n]+)>|([^\s)]+))"
    inline = r"\]\(\s*" + destination + r"(?:\s+[^\n)]*)?\s*\)"
    definitions = r"(?m)^ {0,3}\[[^\]\n]+\]:\s*" + destination
    for pattern in (inline, definitions):
        for match in re.finditer(pattern, text):
            yield match[1] or match[2]


def catalog(source: Path) -> dict[str, FileSnapshot]:
    """Return installed relative path -> bytes/mode; validate all package links."""
    packages = (
        sorted((source / "skills").iterdir()) if (source / "skills").is_dir() else []
    )
    if not packages:
        raise Refusal("No skill packages found")
    payload = {}
    for package in packages:
        if not package.is_dir() or package.is_symlink():
            raise Refusal("Expected skill directory: " + str(package))
        if not re.fullmatch(r"phi9t(?:-[a-z0-9]+)*", package.name):
            raise Refusal("Invalid skill name: " + package.name)
        entry = package / "SKILL.md"
        if not entry.is_file() or entry.is_symlink():
            raise Refusal("Missing regular SKILL.md: " + str(package))
        text = entry.read_text()
        match = re.match(
            r'\A---\nname: ([a-z0-9-]+)\ndescription: ("[^\n]+")\n---\n', text
        )
        if not match or match[1] != package.name:
            raise Refusal("Expected name and JSON-quoted description: " + str(entry))
        description = json.loads(match[2])
        if not description.strip() or len(description) > 1024:
            raise Refusal("Invalid description: " + str(entry))
        for item in sorted(package.rglob("*")):
            if item.is_symlink():
                raise Refusal("Source symlink: " + str(item))
            if item.is_dir():
                continue
            if not item.is_file():
                raise Refusal("Unsupported source file: " + str(item))
            relative = (
                "skills/" + package.name + "/" + item.relative_to(package).as_posix()
            )
            if relative in payload:
                raise Refusal("Duplicate package file: " + relative)
            state = snapshot(item)
            if state is None:
                raise Refusal("Source file disappeared: " + str(item))
            payload[relative] = state
    # Check references against the selected install, not only the source tree.
    for relative, state in payload.items():
        if not relative.endswith(".md"):
            continue
        text = state.data.decode()
        for link in markdown_targets(text):
            url = urlsplit(link.strip("<>"))
            if url.scheme or not url.path:
                continue
            destination = os.path.normpath(
                str(PurePosixPath(relative).parent / unquote(url.path))
            )
            if destination not in payload:
                raise Refusal("Missing packaged reference: " + relative + " -> " + link)
    return payload


def installed_manifest(target: Path) -> InstallationManifest:
    path = path_at(target, MANIFEST)
    if not path.exists():
        return InstallationManifest({})
    manifest = parse_manifest(read_json(path))
    for relative in manifest.files:
        path_at(target, relative)
    return manifest


def read_transaction(target: Path, backup: str, recovery: bool) -> Transaction:
    value = read_json(path_at(target, ".phi9t/backups/" + backup + ".json"))
    if not isinstance(value, dict):
        raise Refusal("Backup belongs to a different target or schema")
    transaction = parse_transaction(value, target)
    for relative in transaction.after:
        current = snapshot(path_at(target, relative))
        observed = current.to_record() if current is not None else None
        allowed = [value["after"][relative]]
        if recovery:
            allowed.append(value["before"][relative])
        if observed not in allowed:
            raise Refusal("Changed since transaction; preserved: " + relative)
    return transaction


@contextmanager
def locked_target(raw: str) -> Generator[Path, None, None]:
    target = Path(raw).expanduser()
    if target.is_symlink():
        raise Refusal("Target is a symlink: " + str(target))
    target = target.resolve()
    state = path_at(target, ".phi9t")
    state.mkdir(parents=True, exist_ok=True)
    lock = path_at(target, ".phi9t/lock")
    with lock.open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Refusal("Another installer owns " + str(target))
        yield target


def pending_guard(target: Path) -> None:
    if path_at(target, ".phi9t/pending.json").exists():
        raise Refusal("Interrupted transaction. Run recover --target " + str(target))


def transact(target: Path, changes: Mapping[str, Optional[FileSnapshot]]) -> dict:
    before = {name: snapshot(path_at(target, name)) for name in changes}
    changed = {name: state for name, state in changes.items() if state != before[name]}
    if not changed:
        return {"outcome": "unchanged", "files": 0}
    transaction = Transaction(
        str(target), {name: before[name] for name in changed}, changed
    )
    backup = uuid.uuid4().hex
    atomic_write(
        path_at(target, ".phi9t/backups/" + backup + ".json"),
        encode(transaction.to_record()),
    )
    pending = path_at(target, ".phi9t/pending.json")
    atomic_write(pending, encode({"backup": backup}))
    try:
        for relative, state in changed.items():
            apply_state(path_at(target, relative), state)
    except BaseException:
        # A hard kill retains pending.json for explicit recovery.
        for relative in reversed(list(changed)):
            apply_state(path_at(target, relative), before[relative])
        pending.unlink()
        raise
    pending.unlink()
    return {"outcome": "changed", "files": len(changed), "backup": backup}


def install(args: argparse.Namespace) -> dict:
    payload = catalog(args.source)
    for relative, state in payload.items():
        if state.mode not in (0o644, 0o755):
            raise Refusal("Source file must have mode 644 or 755: " + relative)
    with locked_target(args.target) as target:
        pending_guard(target)
        old = installed_manifest(target)
        changes: dict[str, Optional[FileSnapshot]] = dict(payload)
        for relative in sorted(set(payload) | set(old.files)):
            current = identity(snapshot(path_at(target, relative)))
            expected = old.files.get(relative)
            if expected is None and current is not None:
                raise Refusal("Unmanaged collision: " + relative)
            if (
                expected is not None
                and current != expected
                and not args.replace_modified
            ):
                raise Refusal(
                    "Locally modified: "
                    + relative
                    + "; preserve or use --replace-modified"
                )
            if relative not in payload:
                changes[relative] = None
        if args.migrate_legacy:
            legacy = read_json(args.source / "legacy.json")
            if not isinstance(legacy, dict) or not isinstance(
                legacy.get("files"), dict
            ):
                raise Refusal("Invalid legacy file records")
            for relative, record in legacy["files"].items():
                if relative in payload:
                    continue
                current = identity(snapshot(path_at(target, relative)))
                if current is not None:
                    expected = parse_identity(record, relative)
                    if current != expected:
                        raise Refusal("Modified legacy file preserved: " + relative)
                    changes[relative] = None
        new = InstallationManifest(
            {name: state.identity for name, state in payload.items()}
        )
        changes[MANIFEST] = FileSnapshot(encode(new.to_record()), 0o600)
        return transact(target, changes)


def verify(args: argparse.Namespace) -> dict:
    payload = catalog(args.source)
    with locked_target(args.target) as target:
        pending_guard(target)
        manifest = installed_manifest(target)
        if not path_at(target, MANIFEST).is_file():
            raise Refusal("No phi9t installation manifest")
        expected = {name: state.identity for name, state in payload.items()}
        if expected != manifest.files:
            raise Refusal("Installation differs from selected source; run install")
        failures = [
            name
            for name, record in expected.items()
            if identity(snapshot(path_at(target, name))) != record
        ]
        if failures:
            raise Refusal("Installed file drift: " + ", ".join(failures))
        return {"outcome": "verified", "files": len(expected)}


def restore(args: argparse.Namespace, recovery: bool = False) -> dict:
    with locked_target(args.target) as target:
        pending = path_at(target, ".phi9t/pending.json")
        if recovery:
            if not pending.exists():
                return {"outcome": "unchanged", "reason": "no interrupted transaction"}
            pending_record = read_json(pending)
            if not isinstance(pending_record, dict):
                raise Refusal("Invalid pending transaction")
            backup = pending_record["backup"]
        else:
            pending_guard(target)
            backup = args.backup
        if not re.fullmatch("[a-f0-9]{32}", backup):
            raise Refusal("Invalid backup identity")
        transaction = read_transaction(target, backup, recovery)
        # Restoration itself is reversible and uses the same pending protocol.
        if recovery:
            for relative in reversed(list(transaction.before)):
                apply_state(path_at(target, relative), transaction.before[relative])
            pending.unlink()
            return {"outcome": "recovered", "backup": backup}
        return transact(target, transaction.before)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT,
        help="package source, defaults to this checkout",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="validate source packages and their references")
    for name in ("install", "verify", "restore", "recover"):
        command = sub.add_parser(name)
        command.add_argument(
            "--target", required=True, help="agent root containing skills/"
        )
        if name == "install":
            command.add_argument("--replace-modified", action="store_true")
            command.add_argument("--migrate-legacy", action="store_true")
        if name == "restore":
            command.add_argument("--backup", required=True)
    args = parser.parse_args()
    try:
        if args.command == "check":
            result = {
                "outcome": "valid",
                "files": len(catalog(args.source)),
            }
        elif args.command == "install":
            result = install(args)
        elif args.command == "verify":
            result = verify(args)
        else:
            result = restore(args, recovery=args.command == "recover")
        print(json.dumps(result, sort_keys=True))
    except (Refusal, OSError, ValueError, KeyError, TypeError) as error:
        print("phi9t: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
