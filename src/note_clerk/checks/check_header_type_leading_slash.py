from ..linting import HeaderCheck, LintError, Lints


class CheckHeaderTypeLeadingSlash(HeaderCheck):
    """Check if type starts with leading slash."""

    def check_line(self, line: str, line_num: int) -> Lints:
        """Check if tags are structured as an array."""
        yield from super().check_line(line, line_num)

        if self.in_header and line.startswith("type:"):
            if line.startswith("type: /"):
                yield LintError("header-type-leading-slash", line_num, 7)
