#!/usr/bin/env python3
"""Build reproducible ZIPs from an explicit public-content allowlist."""

import hashlib
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = {"README.md", "README.en.md", "INSTALL.md", "LICENSE", "CONTRIBUTING.md",
         "RELEASING.md", "VALIDATION.md", "VERSION", ".gitignore", "install.py"}
FOLDERS = {"skills", "examples", "tests", "scripts", ".github"}


def public_files(root):
    result = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if relative.parts[0] not in FOLDERS and relative.as_posix() not in FILES:
            continue
        if any(part in {"__pycache__", ".git", ".venv"} for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"Refusing symbolic link in release: {relative}")
        if path.is_file() and path.suffix != ".pyc":
            result.append(path)
    return result


def write_zip(destination, entries):
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, name in entries:
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def build(root=ROOT):
    output = root / "dist"
    output.mkdir(exist_ok=True)
    files = public_files(root)
    project = output / "evidence-learning-coach-project.zip"
    skill = output / "evidence-learning-coach.zip"
    write_zip(project, [(path, "evidence-learning-coach/" + path.relative_to(root).as_posix()) for path in files])
    base = root / "skills/evidence-learning-coach"
    write_zip(skill, [(path, "evidence-learning-coach/" + path.relative_to(base).as_posix())
                      for path in files if path.is_relative_to(base)])
    checksums = []
    for path in (project, skill):
        checksums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (output / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    return project, skill


if __name__ == "__main__":
    try:
        for artifact in build():
            print(artifact)
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(2)
