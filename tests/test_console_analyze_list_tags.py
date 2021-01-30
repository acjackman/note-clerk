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

    filename: str
    content: str

    def create(self) -> None:
        """Create file."""
        with open(self.filename, "w") as f:
            f.write(inline_note(self.content))


Files = List[FileInfo]


class AnalyzeDetails(TypedDict):
    """Parameterized details for linting errors."""

    files: Files
    output: str


CASES = [
    ParamCase(
        id="START_OF_FILE_TAG",
        description="tag at the start of file counts",
        variables=AnalyzeDetails(
            files=[
                FileInfo(
                    filename="test.txt",
                    content=("#tag at start of line"),
                )
            ],
            output="#tag\t'test.txt:1:1'\tBODY",
        ),
    ),
    ParamCase(
        id="IN_SENTANCE_TAG",
        description="quoted tags count as tags",
        variables=AnalyzeDetails(
            files=[
                FileInfo(
                    filename="test.txt",
                    content=("A #tag in a sentence."),
                )
            ],
            output="#tag\t'test.txt:1:3'\tBODY",
        ),
    ),
    ParamCase(
        id="SINGLE_QUTOED_TAGS",
        description="quoted tags count as tags",
        variables=AnalyzeDetails(
            files=[
                FileInfo(
                    filename="test.txt",
                    content=inline_header("tags: ['#inbox']"),
                )
            ],
            output="#inbox\t'test.txt:2:9'\tHEADER_TAGS",
        ),
    ),
    ParamCase(
        id="DOUBLE_QUTOED_TAGS",
        description="quoted tags count as tags",
        variables=AnalyzeDetails(
            files=[
                FileInfo(
                    filename="test.txt",
                    content=inline_header('tags: ["#inbox"]'),
                )
            ],
            output="#inbox\t'test.txt:2:9'\tHEADER_TAGS",
        ),
    ),
    ParamCase(
        id="DOUBLE_HASH_TAG",
        description="double hash structure notes count",
        variables=AnalyzeDetails(
            files=[
                FileInfo(
                    filename="test.txt",
                    content=inline_note("##tag", trailing_newline=False),
                )
            ],
            output="##tag\t'test.txt:1:1'\tBODY",
        ),
    ),
    ParamCase(
        id="DOUBLE_HASH_TAG_TOP_LEVEL",
        description="double hash structure notes count",
        variables=AnalyzeDetails(
            files=[
                FileInfo(
                    filename="test.txt",
                    content=inline_header("top_level: ##tag"),
                )
            ],
            output="##tag\t'test.txt:2:12'\tHEADER_TOP_LEVEL",
        ),
    ),
    ParamCase(
        id="DOUBLE_HASH_TAG_HEADER",
        description="double hash structure notes count",
        variables=AnalyzeDetails(
            files=[
                FileInfo(
                    filename="test.txt",
                    content=inline_header("other: ##tag"),
                )
            ],
            output="##tag\t'test.txt:2:8'\tHEADER",
        ),
    ),
    ParamCase(
        id="SHBANG",
        description="shbangs don't count as tags",
        variables=AnalyzeDetails(
            files=[
                FileInfo(
                    filename="test.sh",
                    content="""
                    #!/usr/bin/env python3
                    """,
                )
            ],
            output="",
        ),
    ),
    ParamCase(
        id="MARKDOWN_HEADER_1",
        description="PR identifier doesn't count",
        variables=AnalyzeDetails(
            files=[FileInfo(filename="test.txt", content="# Header 1")],
            output="",
        ),
    ),
    ParamCase(
        id="MARKDOWN_HEADER_2",
        description="PR identifier doesn't count",
        variables=AnalyzeDetails(
            files=[FileInfo(filename="test.txt", content="## Header 2")],
            output="",
        ),
    ),
    ParamCase(
        id="MARKDOWN_HEADER_3",
        description="PR identifier doesn't count",
        variables=AnalyzeDetails(
            files=[FileInfo(filename="test.txt", content="### Header 3")],
            output="",
        ),
    ),
    ParamCase(
        id="PR_IDENTIFIER",
        description="PR identifier doesn't count",
        variables=AnalyzeDetails(
            files=[FileInfo(filename="test.txt", content="repo#1")],
            output="",
        ),
    ),
]


@pytest.mark.parametrize(**paramaterize_cases(CASES))
def test_analyze_list_tags(cli_runner: CliRunner, files: Files, output: str) -> None:
    """Test list tags."""
    with cli_runner.isolated_filesystem():
        for file in files:
            file.create()

        result = cli_runner.invoke(
            console.cli, ["--log-level=DEBUG", "analyze", "list-tags", "."]
        )

    print(result.output, end="")

    expected_output = output + "\n" if output != "" else ""

    assert result.exit_code == 0
    assert result.output == expected_output
