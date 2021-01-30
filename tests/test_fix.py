from dataclasses import dataclass
import datetime as dt
import logging
from typing import Any, List, Optional

from click.testing import CliRunner
import pytest

from note_clerk import console, fixing
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
        slug_replacements = {
            " ": "-",
            "'": "",
            '"': "",
        }
        slug = self.name.lower()
        for char, to in slug_replacements.items():
            slug = slug.replace(char, to)
        return slug


FIXES = [
    FixCase(
        name="Empty YAML Header doesn't change",
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


@pytest.mark.parametrize(
    "test_value,expected",
    [
        (dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 1)),
        ("2020-01-01", dt.datetime(2020, 1, 1)),
    ],
    ids=lambda v: f"{type(v).__name__}-{v}",
)
def test_as_date(test_value: fixing.DateLike, expected: dt.datetime) -> None:
    assert fixing.as_date(test_value) == expected


@pytest.mark.parametrize(
    "x,y,expected",
    [
        (dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 2), dt.datetime(2020, 1, 1)),
        (dt.datetime(2020, 1, 2), dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 1)),
    ],
    ids=lambda v: f"{v:%Y-%m-%d}",
)
def test_min_date(expected: dt.datetime, x: dt.datetime, y: dt.datetime) -> None:
    assert fixing.min_date(x, y) == expected


@pytest.mark.parametrize(
    "key,x,y",
    [
        ("created", int(1), dt.datetime(2020, 1, 2)),
        ("any", 1, None),
        ("any", None, 2),
        ("any", "foo", "bar"),
    ],
)
def test_min_date_error(key: str, x: Any, y: Any) -> None:
    with pytest.raises(fixing.UnableFix):
        fixing.merge_values(key, x, y)


@pytest.mark.parametrize(
    "filename, expected",
    [
        (None, None),
        ("1234.md", "12340000000000.md"),
        ("123456789012345.md", "123456789012345.md"),
    ],
)
def test_fix_filename(filename: Optional[str], expected: Optional[str]) -> None:
    assert fixing.fix_filename(filename) == expected


OVERWRIITE_CASES = [
    ("12340000000001.md", "1234.md", ["12340000000000.md"]),
    ("12340000000002.md", "1234.md", ["12340000000000.md", "12340000000001.md"]),
    ("01234000000001.md", "01234.md", ["01234000000000.md"]),
]


@pytest.mark.parametrize(
    "expected,filename,overlap_names",
    OVERWRIITE_CASES,
    ids=lambda x: x,
)
def test_fix_filename_dosnt_overwrite(
    filename: str,
    expected: str,
    overlap_names: List[str],
    file_factory: FileFactory,
) -> None:
    note = file_factory(filename, content="note_1")
    log.debug(f"{note=}")
    [file_factory(name, content=f"note_{i}") for i, name in enumerate(overlap_names)]
    correct = file_factory(expected, path_only=True)
    assert fixing.fix_filename(str(note)) == str(correct)
    # for i, overlap in enumerate(overlaps):
    assert correct.name == expected
