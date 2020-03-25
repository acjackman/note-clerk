"""Utility Functions for NoteClerk."""

from pathlib import Path
from typing import Iterable, Iterator

from boltons import iterutils


class FilesNotFound(Exception):
    """Returned when all_files is given a path to a non-existing directory."""

    def __init__(self, missing: Iterable[Path]) -> None:
        """Initiaze FilesNotFound with missing file paths."""
        self.missing = missing


def all_files(paths: Iterable[str], check_missing: bool = True) -> Iterator[Path]:
    """Iterate all files or files in directories of the given paths.

    This function does not recurse into directories, but does expand a
    directories immediate children.

    Args:
        paths: names of files and folders to look for notes.
        check_missing: check if given paths exist before iterating.

    Yields:
        Path to all files given and the immediate children of directories.

    Raises:
        FilesNotFound: If any file doesn't exist, will raise files not found
                       before yielding a value.
    """
    _paths = [Path(p) for p in iterutils.unique_iter(paths)]
    missing = [p for p in _paths if not p.exists()]
    if missing:
        raise FilesNotFound(missing)

    yield from iterutils.unique_iter(filter(lambda f: f.is_file(), _all_files(_paths)))


def _all_files(paths: Iterable[Path]) -> Iterator[Path]:
    for file in paths:
        if file.is_dir():  # pragma: no cover
            yield from file.iterdir()
        else:  # pragma: no cover
            yield file


def quoted_paths(paths: Iterable[Path]) -> str:
    """Return space separated list of quoted paths.

    Args:
        paths: iterable of paths.

    Returns:
        comma separated string of paths.

    """
    return " ".join([f'"{p}"' for p in paths])
