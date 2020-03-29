import logging
import re

from ..linting import HeaderCheck, LintError, Lints

log = logging.getLogger(__name__)


class CheckHeaderTagsQuoted(HeaderCheck):
    """Check if tags are are quoted."""

    TAG_QUOTED = re.compile(r"(?<![\"'])#[^\s.,/]")

    def check_line(self, line: str, line_num: int) -> Lints:
        """Check if tags are structured as an array."""
        yield from super().check_line(line, line_num)

        if self.in_header and line != "---\n":
            for m in self.TAG_QUOTED.finditer(line):
                yield LintError("header-tags-quoted", line_num, m.start())
