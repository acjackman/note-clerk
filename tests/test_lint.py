"""Test general note linting."""
import logging
from typing import TypedDict

from click.testing import CliRunner
import pytest


from note_clerk import console
from ._utils import inline_header, inline_note, paramaterize_cases, ParamCase


logger = logging.getLogger(__name__)


class LintDetails(TypedDict):
    """Parameterized details for linting errors."""

    content: str
    line: int
    column: int
    error: str


LINT_CASES = [
    ParamCase(
        id="HEAD_TAG_QUOTED",
        description="tags should be a quoted array",
        variables=LintDetails(
            content=inline_header("tags: #value"), line=2, column=7, error="H0101",
        ),
    )
]


@pytest.mark.parametrize(**paramaterize_cases(LINT_CASES))
def test_lints(
    cli_runner: CliRunner, content: str, line: int, column: int, error: str
) -> None:
    """Test lints are identified correctly."""
    result = cli_runner.invoke(console.cli, ["lint", "-"], input=content)

    assert result.exit_code == 1
    assert result.output == f"stdin:{line}:{column}: {error}"


class FixDetails(TypedDict):
    """Parameterized details for lint --fix."""

    content: str
    corrected: str


NOTE_FIX_CASES = [
    ParamCase(
        id="HEAD_TAG_ARRAY",
        description="make array",
        variables=FixDetails(
            content=inline_header("tags: #value"),
            corrected=inline_header('tags: ["#value"]'),
        ),
    ),
    ParamCase(
        id="HEAD_TAG_ARRAY_MULTIPLE",
        description="make tag aray with multiple",
        variables=FixDetails(
            content=inline_header("tags: #value, #value1, #value-2, #thing_three"),
            corrected=inline_header(
                """
                tags: ["#value", "#value1", "#value-2", "#thing_three"]
                """
            ),
        ),
    ),
    ParamCase(
        id="HEAD_TAG_QUOTES",
        description="fix quotes in array",
        variables=FixDetails(
            content=inline_header("tags: [“#value”]"),
            corrected=inline_header('tags: ["#value"]'),
        ),
    ),
    ParamCase(
        id="HEAD_COMBINE",
        description="combines multiple yaml together",
        variables=FixDetails(
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
    ),
    ParamCase(
        id="HEAD_COMBINE_MULI_KEY",
        description="combines multiple yaml together maintains multiple key values",
        variables=FixDetails(
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
    ),
]


@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize(**paramaterize_cases(NOTE_FIX_CASES))
def test_fixes(cli_runner: CliRunner, content: str, corrected: str) -> None:
    """Test fix applies the correct."""
    result = cli_runner.invoke(console.cli, ["lint", "--fix", "-"])

    assert result.exit_code == 0
    assert result.output == corrected


@pytest.mark.xfail(strict=True)
def test_lint_files(cli_runner: CliRunner) -> None:
    """Test applies lint to all files given."""
    result = cli_runner.invoke(console.cli, ["lint-paths"])

    assert result.exit_code == 0, "\n" + result.output
