import re

from ..base import HeaderCheck, LintError, Lints


class CheckHeaderTagsQuoted(HeaderCheck):
    """Check if tags are are quoted."""

    TAG_QUOTED = re.compile(r"(?<![\"'])#")

    def check_line(self, line: str, line_num: int) -> Lints:
        """Check if tags are structured as an array."""
        yield from super().check_line(line, line_num)

        if self.in_header and line.startswith("tags:"):
            for m in self.TAG_QUOTED.finditer(line):
                yield LintError(line_num, m.start(), "header-tags-quoted")
