"""Linting implementation."""

from dataclasses import dataclass
import logging
from typing import Iterable, Optional, TextIO

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class LintError:
    """Lint error location."""

    line: int
    column: int
    error: str


def lint_file(file: TextIO, filename: Optional[str]) -> Iterable[LintError]:
    """Lint a file."""
    filename = None
    logging.debug(f"{filename=}")

    return []
