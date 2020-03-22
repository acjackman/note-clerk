"""Test general note linting."""

from io import StringIO
import logging
from typing import Optional, TypedDict, Iterable, Callable

import pytest

from note_clerk import linting
from ._utils import inline_header, paramaterize_cases, ParamCase


log = logging.getLogger(__name__)


class LintDetails(TypedDict):
    """Parameterized details for linting errors."""

    checks: Iterable[linting.LintCheck]
    content: str
    line: int
    column: int
    error: str


class CleanDetails(TypedDict):
    """Parameterized details for linting errors."""

    checks: Iterable[linting.LintCheck]
    content: str


LINT_CASES = [
    ParamCase(
        id="HEAD_TAGS_ARRAY_PASS",
        description="tags should be a quoted array",
        variables=CleanDetails(
            checks=[linting.check_header_tags_array],
            content=inline_header('tags: ["#value"]'),
        ),
    ),
    ParamCase(
        id="HEAD_TAGS_ARRAY",
        description="tags should be a quoted array",
        variables=LintDetails(
            checks=[linting.check_header_tags_array],
            content=inline_header('tags: "#value"'),
            line=2,
            column=5,
            error="header-tags-array",
        ),
    ),
    ParamCase(
        id="HEAD_TAGS_QUOTED_1",
        description="tags should be a quoted array",
        variables=LintDetails(
            checks=[linting.check_header_tags_quoted],
            content=inline_header("tags: [#value]"),
            line=2,
            column=7,
            error="header-tags-quoted",
        ),
    ),
    ParamCase(
        id="HEAD_TAGS_QUOTED_PASS",
        description="Quoted array should pass",
        variables=CleanDetails(
            checks=[linting.check_header_tags_quoted],
            content=inline_header('tags: ["#value"]'),
        ),
    ),
    ParamCase(
        id="HEAD_TAGS_QUOTED_PASS_SINGLE_QUOTE",
        description="Quoted array should pass",
        variables=CleanDetails(
            checks=[linting.check_header_tags_quoted],
            content=inline_header("tags: ['#value']"),
        ),
    ),
]


@pytest.mark.parametrize(**paramaterize_cases(LINT_CASES))
def test_lints(
    content: str, line: Optional[int], column: Optional[int], error: Optional[str], checks: Iterable[Callable]
) -> None:
    """Test lints are identified correctly."""
    lints = linting.lint_file(
        file=StringIO(content), filename="stdin", checks=checks,
    )

    if error and line and column:
        assert lints == [linting.LintError(line=line, column=column, error=error)]
    else:
        assert lints == []
