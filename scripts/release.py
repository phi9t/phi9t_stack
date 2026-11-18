#!/usr/bin/env python3
"""Build, inspect, unpack and qualify versioned phi9t installation bundles."""

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import zlib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

MAX_ARCHIVE = 32 * 1024 * 1024
MAX_FILE = 8 * 1024 * 1024
VERSION_PATTERN = (
    r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-(?:rc|beta|alpha)\.[1-9]\d*)?"
)


class Refusal(Exception):
    """The release cannot be built or consumed safely."""


@dataclass(frozen=True)
class ArtifactFile:
    data: bytes
    mode: int


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(repo: Path, *args: str) -> bytes:
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=True,
        timeout=30,
        env=env,
    ).stdout


def safe_name(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(name)
        and not path.is_absolute()
        and path.as_posix() == name
        and all(part not in (".", "..", ".git", ".phi9t") for part in path.parts)
        and "\\" not in name
    )


def new_directory(path: Path) -> Path:
    # Normalize system aliases such as macOS /tmp without following an existing
    # output entry. The output itself must be exclusively created.
    path = path.parent.resolve() / path.name
    if path.is_symlink():
        raise Refusal("Output directory must not be a symlink")
    path.mkdir(mode=0o700, parents=True, exist_ok=False)
    return path


def build(args) -> dict:
    repo = Path(args.repo).resolve()
    common = Path(git(repo, "rev-parse", "--git-common-dir").decode().strip())
    grafts = (repo / common) / "info/grafts"
    if grafts.exists() and grafts.stat().st_size:
        raise Refusal("Release ancestry requires no active Git graft overrides")
    commit = git(repo, "rev-parse", "--verify", args.ref + "^{commit}").decode().strip()
    git(repo, "merge-base", "--is-ancestor", commit, args.mainline)
    tree = git(repo, "rev-parse", commit + "^{tree}").decode().strip()
    if not re.fullmatch(r"[a-f0-9]{40}", commit) or not re.fullmatch(
        r"[a-f0-9]{40}", tree
    ):
        raise Refusal("This release format supports SHA-1 source repositories")
    version = git(repo, "show", commit + ":VERSION").decode().strip()
    if not re.fullmatch(VERSION_PATTERN, version):
        raise Refusal("VERSION must be a supported semantic version")
    try:
        tagged_commit = (
            git(repo, "rev-parse", "--verify", f"refs/tags/v{version}^{{commit}}")
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        tagged_commit = ""
    if tagged_commit and tagged_commit != commit:
        raise Refusal("This version tag already identifies a different commit")
    required = {
        "VERSION",
        "legacy.json",
        "vendor.json",
        "scripts/stack.py",
        "scripts/install.sh",
        "scripts/release.py",
        "scripts/vendor.py",
        "docs/provenance.md",
        "docs/release-bundle.md",
        f"releases/{version}.md",
    }
    files = {}
    for entry in git(repo, "ls-tree", "-rz", commit).split(b"\0"):
        if not entry:
            continue
        metadata, raw_name = entry.split(b"\t", 1)
        name = raw_name.decode()
        if name not in required and not name.startswith("skills/"):
            continue
        mode, kind, blob = metadata.split()
        if not safe_name(name) or kind != b"blob" or mode not in (b"100644", b"100755"):
            raise Refusal("Nonregular or unsafe release source: " + name)
        size = int(git(repo, "cat-file", "-s", blob.decode()))
        if size > MAX_FILE:
            raise Refusal("Release file exceeds size limit: " + name)
        if sum(len(value.data) for value in files.values()) + size > MAX_ARCHIVE:
            raise Refusal("Release source exceeds archive limit")
        data = git(repo, "cat-file", "blob", blob.decode())
        files[name] = ArtifactFile(data, int(mode, 8) & 0o777)
    if required - files.keys() or not any(name.startswith("skills/") for name in files):
        raise Refusal("Committed release inputs are incomplete")
    files["README.md"] = files.pop("docs/release-bundle.md")
    identity = {"version": version, "source_commit": commit, "source_tree": tree}
    distribution = "skills/phi9t/references/distribution.json"
    if distribution in files:
        raise Refusal("Distribution identity is generated, not a source override")
    files[distribution] = ArtifactFile(encoded(identity), 0o644)
    manifest = {
        "schema": 1,
        **identity,
        "files": {
            name: {"sha256": digest(value.data), "mode": value.mode}
            for name, value in sorted(files.items())
        },
    }
    files["release.json"] = ArtifactFile(encoded(manifest), 0o644)
    prefix = "phi9t_stack-" + version
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w:", format=tarfile.USTAR_FORMAT) as archive:
        for name, value in sorted(files.items()):
            entry = tarfile.TarInfo(prefix + "/" + name)
            entry.mode = value.mode
            entry.size = len(value.data)
            entry.mtime = 0
            archive.addfile(entry, io.BytesIO(value.data))
    if len(raw.getvalue()) > MAX_ARCHIVE:
        raise Refusal("Release exceeds decompressed archive limit")
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", filename="", mtime=0) as stream:
        stream.write(raw.getvalue())
    output = new_directory(Path(args.output).absolute())
    target = output / (prefix + ".tar.gz")
    target.write_bytes(compressed.getvalue())
    checksum = digest(compressed.getvalue())
    (output / "SHA256SUMS").write_text(checksum + "  " + target.name + "\n")
    (output / "release.json").write_bytes(encoded(manifest))
    (output / "RELEASE-NOTES.md").write_bytes(files[f"releases/{version}.md"].data)
    return {"status": "built", **identity, "archive": str(target), "sha256": checksum}


def inspect_archive(path: Path, expected: str = "") -> tuple[dict, dict, str]:
    with path.open("rb") as source:
        compressed = source.read(MAX_ARCHIVE + 1)
    if len(compressed) > MAX_ARCHIVE:
        raise Refusal("Compressed archive exceeds size limit")
    checksum = digest(compressed)
    if expected and (
        not re.fullmatch(r"[a-f0-9]{64}", expected) or expected != checksum
    ):
        raise Refusal("Archive SHA-256 mismatch")
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
            raw = stream.read(MAX_ARCHIVE + 1)
    except (gzip.BadGzipFile, EOFError, zlib.error) as error:
        raise Refusal("Invalid gzip archive: " + str(error)) from error
    if len(raw) > MAX_ARCHIVE:
        raise Refusal("Decompressed archive exceeds size limit")
    files = {}
    prefix = ""
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        for entry in archive:
            if (
                not safe_name(entry.name)
                or entry.type not in (tarfile.REGTYPE, tarfile.AREGTYPE)
                or entry.mode not in (0o644, 0o755)
                or not 0 <= entry.size <= MAX_FILE
                or len(files) >= 4096
            ):
                raise Refusal("Unsafe archive member: " + entry.name)
            parts = entry.name.split("/", 1)
            if len(parts) != 2 or (prefix and parts[0] != prefix):
                raise Refusal("Archive must have one release root")
            prefix, name = parts
            if name in files:
                raise Refusal("Duplicate archive member: " + name)
            stream = archive.extractfile(entry)
            if stream is None:
                raise Refusal("Unreadable archive member")
            files[name] = ArtifactFile(stream.read(), entry.mode)
    manifest = json.loads(files["release.json"].data)
    if not isinstance(manifest, dict):
        raise Refusal("Release manifest must be an object")
    if (
        manifest.get("schema") != 1
        or not isinstance(manifest.get("files"), dict)
        or not re.fullmatch(VERSION_PATTERN, manifest.get("version", ""))
        or prefix != "phi9t_stack-" + manifest["version"]
        or not all(
            re.fullmatch(r"[a-f0-9]{40}", manifest.get(name, ""))
            for name in ("source_commit", "source_tree")
        )
    ):
        raise Refusal("Invalid release manifest")
    if set(manifest["files"]) != set(files) - {"release.json"}:
        raise Refusal("Archive inventory differs from manifest")
    required = {
        "VERSION",
        "README.md",
        "legacy.json",
        "vendor.json",
        "scripts/stack.py",
        "scripts/install.sh",
        "scripts/release.py",
        "scripts/vendor.py",
        "docs/provenance.md",
        "skills/phi9t/SKILL.md",
        "skills/phi9t/references/distribution.json",
        f"releases/{manifest['version']}.md",
    }
    if (
        required - files.keys()
        or files["VERSION"].data.decode().strip() != manifest["version"]
    ):
        raise Refusal("Release inputs/version are incomplete or inconsistent")
    for name, record in manifest["files"].items():
        value = files[name]
        if record != {"sha256": digest(value.data), "mode": value.mode}:
            raise Refusal("Release file identity mismatch: " + name)
    identity = {
        key: manifest[key] for key in ("version", "source_commit", "source_tree")
    }
    if json.loads(files["skills/phi9t/references/distribution.json"].data) != identity:
        raise Refusal("Installed distribution identity differs from manifest")
    return manifest, files, checksum


def write_verified_files(files: dict, output: Path) -> None:
    output = new_directory(output)
    for name, value in files.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(value.data)
        target.chmod(value.mode)


def unpack(path: Path, output: Path, expected: str = "") -> tuple[dict, str]:
    manifest, files, checksum = inspect_archive(path, expected)
    write_verified_files(files, output)
    return manifest, checksum


def qualify(args) -> dict:
    # This command explicitly executes release code; verify/unpack do not.
    output = Path(args.output).absolute()
    manifest, files, checksum = inspect_archive(Path(args.archive), args.sha256)
    output = new_directory(output)
    source = output / "package"
    write_verified_files(files, source)
    profiles = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    commands = []

    def invoke(argv: list[str]) -> dict:
        result = subprocess.run(
            argv, capture_output=True, text=True, timeout=60, env=env
        )
        commands.append(
            {
                "argv": argv,
                "exit": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        if result.returncode:
            raise Refusal(
                "Bundle qualification command failed: " + json.dumps(commands[-1])
            )
        return json.loads(result.stdout)

    target = output / "core"
    target.mkdir()
    (target / "human.txt").write_text("preserve\n")
    cli = [sys.executable, str(source / "scripts/stack.py")]
    invoke([*cli, "check"])
    installed = invoke([*cli, "install", "--target", str(target)])
    invoke([*cli, "verify", "--target", str(target)])
    backups = sorted((target / ".phi9t/backups").iterdir())
    repeated = invoke([*cli, "install", "--target", str(target)])
    if (
        repeated["outcome"] != "unchanged"
        or sorted((target / ".phi9t/backups").iterdir()) != backups
    ):
        raise Refusal("Repeated installation is not a no-op")
    for relative, value in files.items():
        if not relative.startswith("skills/"):
            continue
        actual = target / relative
        if (
            actual.read_bytes() != value.data
            or actual.stat().st_mode & 0o777 != value.mode
        ):
            raise Refusal("Installed bytes/modes differ from bundle")
    help_result = subprocess.run(
        [
            sys.executable,
            str(target / "skills/phi9t-land/scripts/land.py"),
            "--help",
        ],
        capture_output=True,
        text=True,
        timeout=15,
        env=env,
    )
    if help_result.returncode or "--repo" not in help_result.stdout:
        raise Refusal("Installed landing helper is not runnable")
    invoke([*cli, "restore", "--target", str(target), "--backup", installed["backup"]])
    if any(path.is_file() for path in (target / "skills").rglob("*")):
        raise Refusal("Restore left installed files")
    if (target / "human.txt").read_text() != "preserve\n":
        raise Refusal("Restore changed unrelated state")
    profiles.append({"profile": "core", "restored": True})
    receipt = {
        "status": "qualified",
        "version": manifest["version"],
        "source_commit": manifest["source_commit"],
        "archive_sha256": checksum,
        "profiles": profiles,
        "commands": commands,
        "limits": (
            "File distribution and local helper launch only; "
            "no runtime discovery or method-quality qualification."
        ),
    }
    (output / "qualification.json").write_bytes(encoded(receipt))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    builder = commands.add_parser("build")
    builder.add_argument("--repo", required=True)
    builder.add_argument("--ref", required=True)
    builder.add_argument("--mainline", required=True)
    builder.add_argument("--output", required=True)
    for name in ("verify", "unpack", "qualify"):
        command = commands.add_parser(name)
        command.add_argument("--archive", required=True)
        command.add_argument("--sha256", default="")
        if name != "verify":
            command.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = build(args)
        elif args.command == "qualify":
            result = qualify(args)
        elif args.command == "unpack":
            manifest, checksum = unpack(
                Path(args.archive), Path(args.output).absolute(), args.sha256
            )
            result = {
                "status": "unpacked",
                "directory": str(Path(args.output).absolute()),
                "version": manifest["version"],
                "sha256": checksum,
            }
        else:
            manifest, _, checksum = inspect_archive(Path(args.archive), args.sha256)
            result = {
                "status": "verified",
                "version": manifest["version"],
                "source_commit": manifest["source_commit"],
                "sha256": checksum,
            }
        print(json.dumps(result, indent=2))
        return 0
    except (
        Refusal,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        tarfile.TarError,
        subprocess.SubprocessError,
    ) as error:
        print(json.dumps({"status": "refused", "reason": str(error)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
