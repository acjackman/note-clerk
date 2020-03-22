import logging
from typing import TypedDict
from io import StringIO

import pytest

from note_clerk import linting
from ._utils import inline_header, inline_note, paramaterize_cases, ParamCase


log = logging.getLogger(__name__)


class LintDetails(TypedDict):
    """Parameterized details for linting errors."""

    content: str
    line: int
    column: int
    error: str


LINT_CASES = [
    ParamCase(
        id="HEAD_TAG_ARRAY",
        description="tags should be a quoted array",
        variables=LintDetails(
            content=inline_header("tags: #value"),
            line=2,
            column=7,
            error="head-tag-array",
        ),
    )
]


@pytest.mark.parametrize(**paramaterize_cases(LINT_CASES))
def test_lints(content: str, line: int, column: int, error: str) -> None:
    """Test lints are identified correctly."""
    lints = linting.lint_file(StringIO(content), filename="stdin")

    assert lints == [linting.LintError(line=line, column=column, error=error)]
