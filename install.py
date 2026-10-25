#!/usr/bin/env python3
"""Install the bundled skill locally without overwriting existing content."""

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile

SKILL_NAME = "evidence-learning-coach"
REQUIRED = ("SKILL.md", "LICENSE", "agents/openai.yaml", "scripts/learning.py",
            "references/learning-protocol.md", "references/scoring-rubrics.md",
            "references/source-policy.md", "references/workspace.md",
            "assets/workspace/profile.md", "assets/workspace/.gitignore")


def manifest(directory):
    entries = {}
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Symbolic links are not supported: {path}")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            entries[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return entries


def install(source, parent):
    source = Path(source).absolute()
    parent = Path(parent).expanduser().absolute()
    if any(path.is_symlink() for path in (source, *source.parents, parent, *parent.parents)):
        raise ValueError("Refusing symbolic-link install paths")
    for item in REQUIRED:
        if not (source / item).is_file():
            raise ValueError(f"Incomplete skill: missing {item}")
    incoming = manifest(source)
    destination = parent / SKILL_NAME
    if destination.is_symlink():
        raise ValueError("Installed skill path is a symbolic link")
    if destination.exists():
        if destination.is_dir() and manifest(destination) == incoming:
            return destination, "already installed; identical files"
        raise FileExistsError(f"Existing content preserved: {destination}. Use another --dest or back up before upgrading.")
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".learning-coach-", dir=parent) as temporary:
        staged = Path(temporary) / SKILL_NAME
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if manifest(staged) != incoming:
            raise ValueError("Installation copy verification failed")
        staged.rename(destination)
    return destination, "installed"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    default_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    parser.add_argument("--dest", type=Path, default=default_home / "skills",
                        help="Parent directory for the installed skill")
    args = parser.parse_args(argv)
    try:
        destination, state = install(Path(__file__).resolve().parent / "skills" / SKILL_NAME, args.dest)
        print(f"{state}: {destination}\nCodex: use the skill in the next turn.")
        return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
