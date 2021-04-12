"""Linting implementation."""
from abc import ABC
from dataclasses import dataclass
import logging
from typing import Iterable, Optional, TextIO, Type

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class LintError:
    """Lint error location."""

    error: str
    line: Optional[int]
    column: Optional[int]


Lints = Iterable[LintError]


class LintCheck(ABC):
    """Lint Check Base Class."""

    def check_filename(self, filename: Optional[str]) -> Lints:
        """Check filename."""
        yield from ()

    def check_line(self, line: str, line_num: int) -> Lints:
        """Check line."""
        yield from ()

    def check_file(self) -> Lints:
        """Emit any final errors."""
        yield from ()


LintChecks = Iterable[Type[LintCheck]]


class HeaderCheck(LintCheck):
    """Track if line is in the header or not."""

    def __init__(self) -> None:
        """Initialize object."""
        super().__init__()
        self.yaml_seperators = 0

    @property
    def in_header(self) -> bool:
        """Identify if in the header by the number of yaml document lines."""
        return self.yaml_seperators == 1

    def check_line(self, line: str, line_num: int) -> Lints:
        """Track number of yaml seperators."""
        yield from super().check_line(line, line_num)
        if line.strip() == "---":
            self.yaml_seperators += 1


def lint_file(file: TextIO, filename: Optional[str], checks: LintChecks) -> Lints:
    """Lint a file."""
    # Instantiate instaces of all checks
    _checks = [c() for c in checks]

    # Check filename for lints
    if filename:
        for c in _checks:
            yield from c.check_filename(filename)

    # Check file content line by line
    for n, line in enumerate(file, start=1):
        log.debug(f"{n:03}: {line.strip()}")

        for c in _checks:
            yield from c.check_line(line, n)

    # Check final errors
    for c in _checks:
        yield from c.check_file()


__all__ = [
    "HeaderCheck",
    "lint_file",
    "LintCheck",
    "LintChecks",
    "LintError",
    "Lints",
]
