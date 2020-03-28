"""note-clerk application tests."""
from dataclasses import dataclass
import logging
from typing import List, TypedDict


from click.testing import CliRunner
import pytest

from note_clerk import console
from ._utils import inline_header, inline_note, paramaterize_cases, ParamCase


logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """File information."""

    content: str
    filename: str = "test.txt"

    def create(self) -> None:
        """Create file."""
        with open(self.filename, "w") as f:
            f.write(inline_note(self.content) + "\n")


Files = List[FileInfo]


class AnalyzeDetails(TypedDict):
    """Parameterized details for linting errors."""

    files: Files
    output: str


CASES = [
    ParamCase(
        id="SIMPLE_TYPE",
        variables=AnalyzeDetails(
            files=[FileInfo(inline_header("type: foo"))], output="foo\t'test.txt'",
        ),
    ),
    ParamCase(
        id="COMPLEX_TYPE",
        variables=AnalyzeDetails(
            files=[FileInfo(inline_header("type: foo/bar/baz"))],
            output="foo/bar/baz\t'test.txt'",
        ),
    ),
    ParamCase(
        id="LEADING_SLASH",
        variables=AnalyzeDetails(
            files=[FileInfo(inline_header("type: /foo/bar/baz"))],
            output="/foo/bar/baz\t'test.txt'",
        ),
    ),
    ParamCase(
        id="UPPER_CASE_TYPE_KEY",
        variables=AnalyzeDetails(
            files=[FileInfo(inline_header("Type: foo"))], output="",
        ),
    ),
    ParamCase(
        id="TYPE_OUTSIDE_HEADER",
        variables=AnalyzeDetails(
            files=[FileInfo(inline_note("---\n---\ntype: foo"))], output="",
        ),
    ),
]


@pytest.mark.parametrize(**paramaterize_cases(CASES))
def test_analyze_list_types(cli_runner: CliRunner, files: Files, output: str) -> None:
    """Test list tags."""
    with cli_runner.isolated_filesystem():
        for file in files:
            file.create()

        result = cli_runner.invoke(
            console.cli, ["--log-level=DEBUG", "analyze", "list-types", "."]
        )

    print(result.output, end="")

    expected_output = output + "\n" if output != "" else ""

    assert result.exit_code == 0
    assert result.output == expected_output


class FVDetails(TypedDict):
    """Parameterixed details for file value location."""

    fv: console.FileValue
    file_location: str


FILE_VALUE_CASES = [
    ParamCase(
        "VALUE_ONLY",
        variables=FVDetails(fv=console.FileValue("foo", None), file_location=""),
    ),
    ParamCase(
        "FILENAME",
        variables=FVDetails(
            fv=console.FileValue("foo", filepath="test.txt"), file_location="test.txt"
        ),
    ),
    ParamCase(
        "LINE_NUM",
        variables=FVDetails(
            fv=console.FileValue("foo", filepath="test.txt", line=5,),
            file_location="test.txt:5",
        ),
    ),
    ParamCase(
        "COLUMN",
        variables=FVDetails(
            fv=console.FileValue("foo", filepath="test.txt", line=5, column=4),
            file_location="test.txt:5:4",
        ),
    ),
    ParamCase(
        "COLUMN_WITHOUT_LINE",
        variables=FVDetails(
            fv=console.FileValue(
                "foo",
                filepath="test.txt",
                # line=5,
                column=4,
            ),
            file_location="test.txt",
        ),
    ),
    ParamCase(
        "LOCATION_WITHOUT_FILE",
        variables=FVDetails(
            fv=console.FileValue("foo", filepath=None, line=5, column=4,),
            file_location=":5:4",
        ),
    ),
]


@pytest.mark.parametrize(**paramaterize_cases(FILE_VALUE_CASES))
def test_file_value_file_location(fv: console.FileValue, file_location: str) -> None:
    """Test file_location generates the correct identifier."""
    result = fv.file_location()

    assert result == file_location
