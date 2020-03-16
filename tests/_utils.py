"""Testing utility fuctions."""

from inspect import cleandoc as multiline_trim


def inline_note(contents: str) -> str:
    """Create a file for testing."""
    return multiline_trim(contents)


def inline_header(header: str) -> str:
    """Create a file that is header only."""
    return inline_note(
        f"""
        ---
        {multiline_trim(header)}
        ---
        """
    )
