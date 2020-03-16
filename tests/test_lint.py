"""Test general note linting."""
from dataclasses import dataclass

from click.testing import CliRunner
import pytest

from note_clerk import console
from ._utils import inline_header, inline_note


@dataclass(frozen=True)
class FixCase:
    """Test case for lint --fix."""

    name: str
    content: str
    corrected: str


HEADER_FIXES = [
    FixCase(
        name="make array",
        content=inline_header("tags: #value"),
        corrected=inline_header('tags: ["#value"]'),
    ),
    FixCase(
        name="fix quotes in array",
        content=inline_header("tags: [“#value”]"),
        corrected=inline_header('tags: ["#value"]'),
    ),
    FixCase(
        name="",
        content=inline_header("tags: #value, #value1, #value-2, #thing_three]"),
        corrected=inline_header(
            """
            tags: ["#value", "#value1", "#value-2", "#thing_three"]
            """
        ),
    ),
    FixCase(
        name="combines multiple yaml together",
        content=inline_note(
            """
            ---
            key1: value1
            ---
            ---
            key2: value2
            ---
            """
        ),
        corrected=inline_note(
            """
            ---
            key1: value1
            key2: value2
            ---
            """
        ),
    ),
    FixCase(
        name="combines multiple yaml together maintains multiple key values",
        content=inline_note(
            """
            ---
            key1: value1
            ---
            ---
            key1: value2
            ---
            """
        ),
        corrected=inline_note(
            """
            ---
            key1: value1
            key1: value2
            ---
            """
        ),
    ),
]


@pytest.mark.parametrize(
    "content,corrected", [(c.content, c.corrected) for c in HEADER_FIXES]
)
def test_fixes(cli_runner: CliRunner, content: str, corrected: str) -> None:
    """Test fix applies the correct."""
    result = cli_runner.invoke(console.cli, ["lint", "--fix", "-"])

    assert result.exit_code == 0
    assert result.output == corrected


def test_lint_files(cli_runner: CliRunner) -> None:
    """Test applies lint to all files given."""
    result = cli_runner.invoke(console.cli, ["lint-paths"])

    assert result.exit_code == 0
