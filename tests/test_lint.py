"""Test general note linting."""
from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Optional

from boltons.setutils import IndexedSet
from click.testing import CliRunner
import pytest


from note_clerk import console
from ._utils import inline_header, inline_note, paramaterize_cases


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FixCase:
    """Test case for lint --fix."""

    id: str
    name: str
    content: str
    corrected: str


def _build_fix_cases(cases: List[FixCase]) -> Dict:
    _cases = paramaterize_cases([
        (c.id, dict(content=c.content, corrected=c.corrected))
        for c in cases
    ])

    return _cases


NOTE_FIX_CASES = _build_fix_cases([
    FixCase(
        id="HEAD_TAG_ARRAY",
        name="make array",
        content=inline_header("tags: #value"),
        corrected=inline_header('tags: ["#value"]'),
    ),
    FixCase(
        id="HEAD_TAG_ARRAY_MULTIPLE",
        name="make tag aray with multiple",
        content=inline_header("tags: #value, #value1, #value-2, #thing_three"),
        corrected=inline_header(
            """
            tags: ["#value", "#value1", "#value-2", "#thing_three"]
            """
        ),
    ),
    FixCase(
        id="HEAD_TAG_QUOTES",
        name="fix quotes in array",
        content=inline_header("tags: [“#value”]"),
        corrected=inline_header('tags: ["#value"]'),
    ),
    FixCase(
        id="HEAD_COMBINE",
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
        id="HEAD_COMBINE_MULI_KEY",
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
])


@pytest.mark.parametrize(**NOTE_FIX_CASES)
def test_fixes(cli_runner: CliRunner, content: str, corrected: str) -> None:
    """Test fix applies the correct."""
    result = cli_runner.invoke(console.cli, ["lint", "--fix", "-"])

    assert result.exit_code == 0
    assert result.output == corrected


def test_lint_files(cli_runner: CliRunner) -> None:
    """Test applies lint to all files given."""
    result = cli_runner.invoke(console.cli, ["lint-paths"])

    assert result.exit_code == 0
