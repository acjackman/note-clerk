from dataclasses import dataclass
import logging

from click.testing import CliRunner
import pytest

from note_clerk import console
from ._utils import FileFactory, inline_note, show_output


log = logging.getLogger(__name__)


@dataclass()
class FixCase:
    name: str
    original: str
    fixed: str = ""
    filename: str = "-"
    newname: str = ""

    def __post_init__(self) -> None:
        self.original = inline_note(self.original, trailing_newline=True)
        if self.fixed == "":
            self.fixed = self.original
        self.fixed = inline_note(self.fixed, trailing_newline=True)
        if self.newname == "":
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
    FixCase(
        name="Collapses date headers by minimizing",
        original="""
        ---
        created: 2020-11-15T06:00:00Z
        ---
        ---
        created: 2020-11-15T05:42:49.301Z
        ---
        # Test Note
        """,
        fixed="""
        ---
        created: 2020-11-15T05:42:49.301000Z
        ***
        # Test Note
        """,
    ),
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
    FixCase(
        name="maxes out id length",
        original="""
        ---
        type: note
        ---
        # Title
        """,
        filename="1234.md",
        newname="12340000000000.md",
    ),
    FixCase(
        name="overlong ids are not changed",
        original="""
        ---
        type: note
        ---
        # Title
        """,
        filename="123456789012345.md",
    ),
]


@pytest.mark.parametrize("case", FIXES, ids=lambda c: c.code)
def test_fixes(
    cli_runner: CliRunner,
    file_factory: FileFactory,
    case: FixCase,
) -> None:
    if case.name == "-":
        result = cli_runner.invoke(
            console.cli, ["--log-level=DEBUG", "fix", "-"], input=case.original
        )
        show_output(result)
        assert result.exit_code == 0
        assert result.output == case.fixed
    else:
        note = file_factory(case.filename, case.original)
        result = cli_runner.invoke(
            console.cli,
            ["--log-level=DEBUG", "fix", str(note)],
        )
        show_output(result)
        assert result.exit_code == 0

        fixed_note = file_factory(case.newname, path_only=True)
        with fixed_note.open() as f:
            fixed = f.read()

        assert fixed == case.fixed
        if case.filename != case.newname:
            not note.exists()


UNFIXABLE = [
    FixCase(
        name="unclosed header",
        original="""
        ---
        tags: ["#tag2"]
        created: 2020-11-15T05:42:49.301Z
        created: 2020-11-15T05:42:49.301Z
        tags: ["#inbox"]
        # Test Note
        """,
    ),
    FixCase(
        name="duplicate keys integer values ",
        original="""
        ---
        k1: 1
        ---
        ---
        k1: 2
        ---
        # Test Note
        """,
    ),
]


@pytest.mark.parametrize("case", UNFIXABLE, ids=lambda c: c.code)
def test_unfixible(cli_runner: CliRunner, case: FixCase) -> None:
    result = cli_runner.invoke(
        console.cli, ["--log-level=DEBUG", "fix", "-"], input=case.original
    )
    show_output(result)
    assert result.exit_code != 0
