"""Test general note linting."""

from io import StringIO
import logging

import pytest

from note_clerk import checks, linting
from .utils import LintDetails, LintErrors
from ..._utils import inline_header, paramaterize_cases, ParamCase

log = logging.getLogger(__name__)


LINT_CASES = [
    ParamCase(
        id="HEAD_TAGS_ARRAY_PASS",
        description="tags should be a quoted array",
        variables=LintDetails(
            content=inline_header('tags: ["#value"]'),
            errors=[],
        ),
    ),
    ParamCase(
        id="HEAD_TAGS_ARRAY",
        description="tags should be a quoted array",
        variables=LintDetails(
            content=inline_header('tags: "#value"'),
            errors=[
                linting.LintError(
                    line=2,
                    column=5,
                    error="header-tags-array",
                )
            ],
        ),
    ),
]


@pytest.mark.parametrize(**paramaterize_cases(LINT_CASES))
def test_lints(
    content: str,
    errors: LintErrors,
) -> None:
    """Test lints are identified correctly."""
    lints = list(
        linting.lint_file(
            file=StringIO(content),
            filename=None,
            checks=[checks.CheckHeaderTagsArray],
        )
    )

    assert lints == errors
