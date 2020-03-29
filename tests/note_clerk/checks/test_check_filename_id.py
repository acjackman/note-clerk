"""Test general note linting."""

from io import StringIO
import logging

import pytest

from note_clerk import checks, linting
from .utils import LintDetails, LintErrors
from ..._utils import paramaterize_cases, ParamCase

log = logging.getLogger(__name__)


LINT_CASES = [
    ParamCase(id="NO_FILENAME", variables=LintDetails(content=None, errors=[],),),
    ParamCase(
        id="HAS_ID", variables=LintDetails(content="20200101000000.md", errors=[],),
    ),
    ParamCase(
        id="NO_ID",
        variables=LintDetails(
            content="test.md",
            errors=[linting.LintError("filename-id-missing", line=None, column=None,)],
        ),
    ),
    ParamCase(
        id="INCOMPLETE_ID",
        variables=LintDetails(
            content="202001010000.md",
            errors=[
                linting.LintError("filename-id-incomplete", line=None, column=None,)
            ],
        ),
    ),
    ParamCase(
        id="ID_HAS_DASHES",
        variables=LintDetails(
            content="2020-03-29T00-23-12.md",
            errors=[
                linting.LintError("filename-id-incomplete", line=None, column=None)
            ],
        ),
    ),
]


@pytest.mark.parametrize(**paramaterize_cases(LINT_CASES))
def test_lints(content: str, errors: LintErrors,) -> None:
    """Test lints are identified correctly."""
    lints = list(
        linting.lint_file(
            file=StringIO(""), filename=content, checks=[checks.CheckFilenameId],
        )
    )

    assert lints == errors
