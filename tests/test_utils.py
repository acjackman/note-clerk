"""Test the utils."""
from pathlib import Path
import textwrap

import pytest

from note_clerk import utils
from ._utils import inline_note


class TestAllFiles:
    """Tests for all_files."""

    def test_empty_directory(self, tmpdir) -> None:  # noqa: ANN001, ANN101
        """Test empty directory."""
        tmp = Path(str(tmpdir))
        full_list = list(utils._all_files((tmp,)))

        assert full_list == []

    # Testing the private function for coverage
    def test_directory_with_no_file(self, tmpdir) -> None:  # noqa: ANN001, ANN101
        """Test empty directory."""
        tmp = Path(str(tmpdir))
        full_list = list(utils._all_files((tmp,)))

        assert full_list == []

    def test_with_single_file(
        self, tmpdir, file_factory  # noqa: ANN001, ANN101
    ) -> None:
        """Test empty directory."""
        f = file_factory("hello.txt")

        full_list = list(utils._all_files((f,)))

        assert full_list == [f]

    # Testing the private function for coverage
    def test_directory_with_single_file(
        self, tmpdir, file_factory  # noqa: ANN001, ANN101
    ) -> None:
        """Test empty directory."""
        tmp = Path(str(tmpdir))
        f = file_factory("hello.txt")
        f2 = file_factory("test2.txt")

        full_list = list(utils._all_files((tmp,)))

        assert set(full_list) == set([f, f2])


HEADERS = [
    (
        inline_note(
            """
            # Note
            """
        ),
        0,
    ),
    (
        inline_note(
            """
            # Note with line
            ---
            has content
            """
        ),
        0,
    ),
    (
        inline_note(
            """
            ***
            # Note
            """
        ),
        0,
    ),
    (
        inline_note(
            """
            ---
            ---
            # Note
            """
        ),
        2,
    ),
    (
        inline_note(
            """
            ---
            thing1: true
            ---
            # Note
            """
        ),
        3,
    ),
    (
        inline_note(
            """
            ---
            thing1: true
            ---
            ---
            ---
            # Note
            """
        ),
        5,
    ),
    (
        inline_note(
            """
            ---
            thing1: true
            ---
            ---
            thing2: true
            ---
            # Note
            """
        ),
        6,
    ),
    (
        inline_note(
            """
            ---
            thing1: true
            ---
            ---
            ---
            # Note with divider
            ---
            """
        ),
        5,
    ),
    (
        inline_note(
            """
            ---
            thing1: true
            ***
            ---
            ---
            """
        ),
        3,
    ),
    (
        inline_note(
            """
            ---
            ***
            ***
            """
        ),
        2,
    ),
]


def print_text(label: str, value: str) -> None:
    print(f"{label}:\n{textwrap.indent(value, ' ' * 4)}")


@pytest.mark.parametrize("text,header_lines", HEADERS)
def test_extract_header(text: str, header_lines: int) -> None:
    lines = text.split("\n")
    correct_header = "\n".join(lines[:header_lines])
    correct_body = "\n".join(lines[header_lines:])

    print_text("Correct Header", correct_header)
    print_text("Correct Body", correct_body)

    header, body = utils.split_header(lines)

    print_text("Header", header)
    print_text("Body", body)

    assert header == correct_header
    assert body == correct_body


def test_ensure_newline() -> None:
    assert utils.ensure_newline("") == "\n"
    assert utils.ensure_newline("\n") == "\n"
