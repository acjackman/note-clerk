"""Test general note linting."""

from io import StringIO
import logging
from typing import List, TypedDict

import pytest

from note_clerk import linting
from note_clerk.linting import checks
from ..._utils import inline_header, paramaterize_cases, ParamCase


log = logging.getLogger(__name__)


class LintDetails(TypedDict):
    """Parameterized details for linting errors."""

    content: str
    errors: List[linting.LintError]


class CleanDetails(TypedDict):
    """Parameterized details for linting errors."""

    content: str


LINT_CASES = [
    ParamCase(
        id="HEAD_TAGS_QUOTED_1",
        description="tags should be a quoted array",
        variables=LintDetails(
            content=inline_header("tags: [#value]"),
            errors=[linting.LintError(line=2, column=7, error="header-tags-quoted",)],
        ),
    ),
    ParamCase(
        id="HEAD_TAGS_QUOTED_1",
        description="tags should be a quoted array",
        variables=LintDetails(
            content=inline_header("tags: [#value, #value2]"),
            errors=[
                linting.LintError(line=2, column=7, error="header-tags-quoted",),
                linting.LintError(line=2, column=15, error="header-tags-quoted",),
            ],
        ),
    ),
    ParamCase(
        id="HEAD_TAGS_QUOTED_PASS",
        description="Quoted array should pass",
        variables=LintDetails(content=inline_header('tags: ["#value"]'), errors=[],),
    ),
    ParamCase(
        id="HEAD_TAGS_QUOTED_PASS_SINGLE_QUOTE",
        description="Quoted array should pass",
        variables=LintDetails(content=inline_header("tags: ['#value']"), errors=[],),
    ),
    ParamCase(
        id="HEAD_TAGS_COMMENT",
        description="Comment should be allowed",
        variables=LintDetails(
            content=inline_header('tags: ["#value"] # comment'), errors=[],
        ),
    ),
]


@pytest.mark.parametrize(**paramaterize_cases(LINT_CASES))
def test_lints(content: str, errors: List[linting.LintError],) -> None:
    """Test lints are identified correctly."""
    lints = list(
        linting.lint_file(
            file=StringIO(content),
            filename=None,
            checks=[checks.CheckHeaderTagsQuoted],
        )
    )

    assert lints == errors
