#!/usr/bin/env python3
"""Import and verify pinned third-party skill trees vendored into skills/."""

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "vendor.json"


class Refusal(Exception):
    """The vendored tree cannot be imported or does not match its pin."""


def load() -> dict:
    return json.loads(MANIFEST.read_text())


def tree_files(base: Path) -> dict[str, str]:
    """Relative path -> sha256 for regular files under base, excluding routers."""
    return {
        item.relative_to(base).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in sorted(base.rglob("*"))
        if item.is_file() and item.relative_to(base).as_posix() != "SKILL.md"
    }


def sources(spec: dict, checkout: Path) -> list[tuple[Path, str]]:
    """Upstream directory -> destination relative to the package."""
    found = []
    for entry in spec["include"]:
        origin = checkout / entry["from"]
        if not origin.is_dir() and not origin.is_file():
            raise Refusal("Missing upstream path: " + str(origin))
        found.append((origin, entry["to"]))
    return found


def build(spec: dict, checkout: Path, router: Path, staged: Path) -> None:
    """Assemble the complete package in staged; raise before touching the tree."""
    staged.mkdir()
    if router.exists():
        shutil.copy2(router, staged / "SKILL.md")
    for origin, relative in sources(spec, checkout):
        destination = staged / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if origin.is_dir():
            shutil.copytree(origin, destination, symlinks=False)
        else:
            shutil.copy2(origin, destination)
    for patch in spec.get("patches", []):
        target = staged / patch["path"]
        text = target.read_text()
        if text.count(patch["old"]) != 1:
            raise Refusal("Patch no longer applies: " + patch["path"])
        target.write_text(text.replace(patch["old"], patch["new"]))
    for notice in spec["notice"]:
        shutil.copy2(checkout / notice, staged / "LICENSE")


def write_manifest(manifest: dict, work: Path) -> None:
    pending = work / "vendor.json"
    pending.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    os.replace(pending, MANIFEST)


def sync(name: str, checkout: Path) -> None:
    """Replace one vendored package and its pins, or change nothing.

    The new package is built beside the tree and swapped in by rename only
    after every include, patch and notice succeeded, so a refused or failed
    sync leaves the vendored package and vendor.json exactly as they were.
    """
    manifest = load()
    spec = manifest["vendors"][name]
    package = ROOT / "skills" / spec["package"]
    work = Path(tempfile.mkdtemp(prefix=".vendor-sync-", dir=ROOT))
    try:
        staged, previous = work / "package", work / "previous"
        build(spec, checkout, package / "SKILL.md", staged)
        spec["files"] = tree_files(staged)
        if package.exists():
            package.rename(previous)
        swapped = False
        try:
            staged.rename(package)
            swapped = True
            write_manifest(manifest, work)
        except BaseException:
            if swapped:
                package.rename(staged)
            if previous.exists():
                previous.rename(package)
            raise
    finally:
        shutil.rmtree(work, ignore_errors=True)


def check() -> list[str]:
    problems = []
    for name, spec in load()["vendors"].items():
        package = ROOT / "skills" / spec["package"]
        if not (package / "SKILL.md").is_file():
            problems.append(name + ": missing router SKILL.md")
            continue
        actual = tree_files(package)
        for relative in sorted(spec["files"].keys() | actual.keys()):
            if spec["files"].get(relative) != actual.get(relative):
                problems.append(name + ": changed " + relative)
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check")
    run = sub.add_parser("sync")
    run.add_argument("vendor")
    run.add_argument("checkout", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "sync":
            sync(args.vendor, args.checkout.resolve())
            return 0
        problems = check()
    except (Refusal, KeyError, OSError, json.JSONDecodeError) as error:
        print("Refused: " + str(error), file=sys.stderr)
        return 2
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
