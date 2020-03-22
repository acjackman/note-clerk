"""Linting implementation."""

from dataclasses import dataclass
import logging
import re
from typing import Callable, Iterable, List, Optional, TextIO

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class LintError:
    """Lint error location."""

    line: int
    column: int
    error: str


LintCheck = Callable[[str, int, bool], Iterable[LintError]]
LintList = List[LintError]


HEAD_TAG_QUOTED = re.compile(r"(?<![\"'])#")


def lint_factory(line_num: int) -> Callable[[int, str], LintError]:
    """Builds a utility fuction for adding a LintError to the list."""

    def _lint_factory(column: int, error: str) -> LintError:
        return LintError(line_num, column, error)

    return _lint_factory


def check_header_tags_array(
    line: str, line_num: int, in_header: bool
) -> Iterable[LintError]:
    """Check if tags key is an array."""
    # log.debug(f"{line_num=} {in_header=}")
    line_lint = lint_factory(line_num)

    if in_header and line.startswith("tags:"):
        if not line.startswith("tags: ["):
            yield line_lint(5, "header-tags-array")


def check_header_tags_quoted(
    line: str, line_num: int, in_header: bool
) -> Iterable[LintError]:
    """Check if tags key is an array."""
    # log.debug(f"{line_num=} {in_header=}")
    line_lint = lint_factory(line_num)

    if in_header and line.startswith("tags:"):
        for m in HEAD_TAG_QUOTED.finditer(line):
            log.debug(m)
            yield line_lint(m.start(), "header-tags-quoted")


def lint_file(
    file: TextIO, filename: Optional[str], checks: Iterable[LintCheck]
) -> Iterable[LintError]:
    """Lint a file."""
    filename = None
    in_header = 0
    log.debug(f"{filename=}")

    lints: List[LintError] = []
    for n, line in enumerate(file, start=1):
        log.debug(f"{n:03}: {line.strip()}")

        if line.strip() == "---":
            in_header += 1

        is_header = in_header == 1
        for check in checks:
            lints += list(check(line, n, is_header))

    return lints
