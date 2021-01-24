from dataclasses import dataclass
import logging

from click.testing import CliRunner
import pytest

from note_clerk import console
from ._utils import inline_note, show_output


log = logging.getLogger(__name__)


@dataclass
class FixCase:
    name: str
    original: str
    fixed: str

    def __post_init__(self) -> None:
        self.original = inline_note(self.original, trailing_newline=True)
        self.fixed = inline_note(self.fixed, trailing_newline=True)

    @property
    def code(self) -> str:
        return self.name.lower().replace(" ", "-")


FIXES = [
    FixCase(
        name="Collapses Headers",
        original="""
        ---
        tags: ["#tag2"]
        created: 2020-11-15T05:42:49.301Z
        ---
        ---
        created: 2020-11-15T05:42:49.301Z
        tags: ["#inbox"]
        ---
        # Test Note
        """,
        fixed="""
        ---
        created: 2020-11-15T05:42:49.301000Z
        tags:
        - '#tag2'
        - '#inbox'
        ***
        # Test Note
        """,
    ),
]


@pytest.mark.parametrize("case", FIXES, ids=lambda c: c.code)
def test_fixs(cli_runner: CliRunner, case: FixCase) -> None:
    result = cli_runner.invoke(
        console.cli, ["--log-level=DEBUG", "fix", "-"], input=case.original
    )
    show_output(result)
    assert result.output == case.fixed


UNFIXABLE = [
    inline_note(
        """
        ---
        tags: ["#tag2"]
        created: 2020-11-15T05:42:49.301Z
        created: 2020-11-15T05:42:49.301Z
        tags: ["#inbox"]
        # Test Note
        """
    ),
]


@pytest.mark.parametrize("text", UNFIXABLE)
def test_unfixible(cli_runner: CliRunner, text: str) -> None:

    result = cli_runner.invoke(
        console.cli, ["--log-level=DEBUG", "fix", "-"], input=text
    )

    print(result.output)

    assert result.exit_code != 0
