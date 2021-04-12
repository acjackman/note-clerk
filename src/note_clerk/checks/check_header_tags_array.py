from ..linting import HeaderCheck, LintError, Lints


class CheckHeaderTagsArray(HeaderCheck):
    """Check if tags are structured as an array."""

    def check_line(self, line: str, line_num: int) -> Lints:
        """Check if tags are structured as an array."""
        yield from super().check_line(line, line_num)

        if self.in_header and line.startswith("tags:"):
            if not line.startswith("tags: ["):
                yield LintError("header-tags-array", line_num, 5)
