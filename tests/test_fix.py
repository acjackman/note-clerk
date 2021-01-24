from dataclasses import dataclass
import logging
from typing import Optional

from click.testing import CliRunner
import pytest

from note_clerk import console
from ._utils import FileFactory, inline_note, show_output


log = logging.getLogger(__name__)


@dataclass
class FixCase:
    name: str
    original: str
    fixed: Optional[str] = None
    filename: str = "-"
    newname: Optional[str] = None

    def __post_init__(self) -> None:
        self.original = inline_note(self.original, trailing_newline=True)
        if self.fixed is None:
            self.fixed = self.original
        self.fixed = inline_note(self.fixed, trailing_newline=True)
        if self.newname is None:
            self.newname = self.filename

    @property
    def code(self) -> str:
        return self.name.lower().replace(" ", "-")


FIXES = [
    FixCase(
        name="Change YAML Header",
        original="""
        ---
        ---
        # Test Note
        """,
        fixed="""
        ---
        ---
        # Test Note
        """,
    ),
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
def test_fixes(cli_runner: CliRunner, case: FixCase) -> None:
    result = cli_runner.invoke(
        console.cli, ["--log-level=DEBUG", "fix", "-"], input=case.original
    )
    show_output(result)
    assert result.output == case.fixed


TEST_FIX_FILES = [
    FixCase(
        name="ID name doesn't change",
        original="""
        ---
        type: note
        ---
        # Title
        """,
        filename="00000000000000.md",
    ),
    FixCase(
        name="names don't change for non .md files",
        original="""
        ---
        type: note
        ---
        # Title
        """,
        filename="testing.txt",
    ),
]


@pytest.mark.parametrize("case", TEST_FIX_FILES, ids=lambda c: c.code)
def test_fix_overwrites_files_with_valid_name(
    cli_runner: CliRunner,
    file_factory: FileFactory,
    case: FixCase,
) -> None:
    note = file_factory(case.filename, case.original)
    result = cli_runner.invoke(
        console.cli,
        ["--log-level=DEBUG", "fix", str(note)],
    )
    show_output(result)

    with note.open() as f:
        fixed = f.read()
    assert fixed == case.original


def test_fix_moves_files_with_invalid_name(
    cli_runner: CliRunner, file_factory: FileFactory
) -> None:
    CONTENT = inline_note(
        """
        ---
        type: note
        ---
        # Title
        """
    )
    note = file_factory("1234.md", CONTENT)

    result = cli_runner.invoke(
        console.cli,
        ["--log-level=DEBUG", "fix", str(note)],
    )
    show_output(result)
    assert result.exit_code == 0
    assert not note.exists()

    note = file_factory("00000000000000.md", CONTENT)
    with note.open() as f:
        fixed = f.read()

    assert fixed == CONTENT


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
    inline_note(
        """
        ---
        k1: 1
        ---
        ---
        k1: 2
        ---
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
