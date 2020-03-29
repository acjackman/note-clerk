"""Note linting utils."""

from typing import List, Optional, TypedDict

from note_clerk import linting


LintErrors = List[linting.LintError]


class LintDetails(TypedDict):
    """Parameterized details for linting errors."""

    content: Optional[str]
    errors: LintErrors
