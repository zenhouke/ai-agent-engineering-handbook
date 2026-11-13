"""Publish static trees and remove obsolete files after a successful build."""

import shutil
from pathlib import Path


def copy_tree(source: Path, target: Path) -> set[Path]:
    shutil.copytree(source, target, dirs_exist_ok=True)
    return {
        target / path.relative_to(source)
        for path in source.rglob("*")
        if path.is_file()
    }


def prune_output(output: Path, expected: set[Path]) -> None:
    """The output directory contains generated public files only.

    Copy and render first, then prune. A failed render never triggers cleanup of
    previous output, and deleted lessons/assets cannot linger after success.
    """
    for path in output.rglob("*"):
        if path.is_file() and path not in expected:
            path.unlink()
    for path in sorted(output.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
