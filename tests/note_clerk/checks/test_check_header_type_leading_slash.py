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
        id="HEAD_TYPE_LEADING_SLASH",
        description="type with leading slash should lint",
        variables=LintDetails(
            content=inline_header("type: /foo"),
            errors=[
                linting.LintError(line=2, column=7, error="header-type-leading-slash",)
            ],
        ),
    ),
    ParamCase(
        id="HEAD_TYPE_LEADING_SLASH_PASS",
        description="type without leading slash should not lint",
        variables=LintDetails(content=inline_header("type: foo"), errors=[],),
    ),
]


@pytest.mark.parametrize(**paramaterize_cases(LINT_CASES))
def test_check_header_type_leading_slash(content: str, errors: LintErrors,) -> None:
    """Test lints are identified correctly."""
    lints = set(
        linting.lint_file(
            file=StringIO(content),
            filename=None,
            checks=[checks.CheckHeaderTypeLeadingSlash],
        )
    )

    assert lints == set(errors)
