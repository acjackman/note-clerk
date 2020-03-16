"""Utility Functions for NoteClerk."""

from pathlib import Path
from typing import Iterable, Iterator

from boltons import iterutils


def all_files(paths: Iterable[str]) -> Iterator[Path]:
    """Iterate all files or files in directories of the given paths.

    This function does not recurse into directories, but does expand a
    directories immediate children.

    Args:
        paths: names of files and folders to look for notes.

    Yields:
        Path to all files given and the immediate children of directories.
    """
    _paths = [Path(p) for p in paths]
    yield from iterutils.unique_iter(_all_files(_paths))


def _all_files(paths: Iterable[Path]) -> Iterator[Path]:
    for file in paths:
        if file.is_dir():  # pragma: no cover
            yield from file.iterdir()
        else:  # pragma: no cover
            yield file
