"""Note linting utils."""

from typing import List, TypedDict

from note_clerk import linting


LintErrors = List[linting.LintError]


class LintDetails(TypedDict):
    """Parameterized details for linting errors."""

    content: str
    errors: LintErrors
