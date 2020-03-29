import logging
import re
from typing import Optional

from ..linting import LintCheck, LintError, Lints

log = logging.getLogger(__name__)


class CheckFilenameId(LintCheck):
    """Check if type starts with leading slash."""

    FULL_ID = re.compile(r"^[0-9]{14}")
    PARTIAL_ID = re.compile(r"^[0-9]+")

    def check_filename(self, filename: Optional[str]) -> Lints:
        """Check if tags are structured as an array."""
        yield from super().check_filename(filename)

        if filename:  # pragma: no cover
            if self.FULL_ID.match(filename):
                pass
            elif self.PARTIAL_ID.match(filename):
                yield LintError("filename-id-incomplete", None, None)
            else:
                yield LintError("filename-id-missing", None, None)
