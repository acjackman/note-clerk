"""Test general note linting."""
import logging
from pathlib import Path
from typing import TypedDict
from unittest.mock import PropertyMock


from click.testing import CliRunner
import pytest
from pytest_mock import MockFixture

from note_clerk import console, linting
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
        id="HEAD_TAG_ARRAY",
        description="tags should be a quoted array",
        variables=LintDetails(
            content=inline_header('tags: "#value"'),
            line=2,
            column=5,
            error="header-tags-array",
        ),
    )
]


FAKE_CONTENT = inline_note("a fake note")


@pytest.fixture
def checks_mock(mocker: MockFixture) -> PropertyMock:
    """Patch app mock list."""
    checks_mock = PropertyMock()
    checks_mock.return_value = []
    mocker.patch("note_clerk.console.App.lint_checks", checks_mock)
    return checks_mock


class LineCheck(linting.LintCheck):
    """Yield lint for testing."""

    def check_line(self, line: str, line_num: int) -> linting.Lints:
        """Yield lint for testing."""
        yield from super().check_line(line, line_num)

        if line_num == 1:
            yield linting.LintError("a-fake-error", line_num, 1)


@pytest.fixture
def checks_mock_dirty(checks_mock: PropertyMock) -> PropertyMock:
    """Add a check that will fail to see lint output."""
    checks_mock.return_value = [LineCheck]
    return checks_mock


def test_lint_stdin_clean(cli_runner: CliRunner, checks_mock: PropertyMock) -> None:
    """Test lints are identified correctly."""
    result = cli_runner.invoke(console.cli, ["lint", "-"], input=FAKE_CONTENT)

    print(result.output, end="")

    assert result.exit_code == 0
    assert result.output == ""


def test_lint_stdin_dirty(
    cli_runner: CliRunner, checks_mock_dirty: PropertyMock
) -> None:
    """Test lints are identified correctly."""
    result = cli_runner.invoke(console.cli, ["lint", "-"], input=FAKE_CONTENT)

    print(result.output, end="")

    assert result.exit_code == 10
    assert result.output == f"stdin:1:1 | a-fake-error\n"


def test_lint_file_clean(cli_runner: CliRunner, checks_mock: PropertyMock) -> None:
    """Test lints are identified correctly."""
    filename = "foo.txt"

    with cli_runner.isolated_filesystem():
        with open(filename, "w") as f:
            f.write(FAKE_CONTENT)

        result = cli_runner.invoke(console.cli, ["lint", filename])

    print(result.output, end="")

    assert result.exit_code == 0
    assert result.output == ""


def test_lint_file_dirty(
    cli_runner: CliRunner, checks_mock_dirty: PropertyMock
) -> None:
    """Test lints are identified correctly."""
    filename = "foo.txt"

    with cli_runner.isolated_filesystem():
        with open(filename, "w") as f:
            f.write(FAKE_CONTENT)

        result = cli_runner.invoke(console.cli, ["lint", filename])

    print(result.output, end="")

    assert result.exit_code == 10
    assert result.output == f"{filename}:1:1 | a-fake-error\n"


def test_lint_sub_file_dirty(
    cli_runner: CliRunner, checks_mock_dirty: PropertyMock
) -> None:
    """Test lints are identified correctly."""
    filename = "foo/bar.txt"

    with cli_runner.isolated_filesystem():
        Path(filename).parent.mkdir(parents=True)
        with open(filename, "w") as f:
            f.write(FAKE_CONTENT)

        result = cli_runner.invoke(console.cli, ["lint", filename])

    print(result.output, end="")

    assert result.exit_code == 10
    assert result.output == f"{filename}:1:1 | a-fake-error\n"


def test_lint_multiple_stdin_errors(
    cli_runner: CliRunner, checks_mock: PropertyMock
) -> None:
    """Test multiple standard inputs are discarded."""
    result = cli_runner.invoke(console.cli, ["lint", "-", "-"], input=FAKE_CONTENT)

    print(result.output, end="")

    assert result.exit_code == 2
    assert console.STD_IN_INDEPENDENT in result.output


def test_lint_mixed_stdin_files_errors(
    cli_runner: CliRunner, checks_mock: PropertyMock
) -> None:
    """Test multiple standard inputs are discarded."""
    result = cli_runner.invoke(console.cli, ["lint", "-", "foo.txt"])

    print(result.output, end="")

    assert result.exit_code == 2
    assert console.STD_IN_INDEPENDENT in result.output


def test_lint_file_does_not_exist(
    cli_runner: CliRunner, checks_mock: PropertyMock
) -> None:
    """Test multiple standard inputs are discarded."""
    result = cli_runner.invoke(console.cli, ["lint", "foo.txt"])

    print(result.output, end="")

    assert result.exit_code == 2
    assert 'All paths should exist, these do not: "foo.txt"' in result.output


def test_lint_multiple_files_do_not_exist(
    cli_runner: CliRunner, checks_mock: PropertyMock
) -> None:
    """Test multiple standard inputs are discarded."""
    result = cli_runner.invoke(console.cli, ["lint", "foo.txt", "bar.txt"])

    print(result.output, end="")

    assert result.exit_code == 2
    assert 'All paths should exist, these do not: "foo.txt" "bar.txt"' in result.output


def test_lint_binary_file(cli_runner: CliRunner, checks_mock: PropertyMock) -> None:
    """Test multiple standard inputs are discarded."""
    TEST_FILE = "foo.txt"

    with cli_runner.isolated_filesystem():
        with open(TEST_FILE, "wb") as f:
            f.write(
                b"\x93Y2\xc1\xf8\xc2\xb7\xbe\xe0\xe8\xc4\x18\xcd')Bx^_\xdf_5\xd7\xb7"
            )
        result = cli_runner.invoke(console.cli, ["lint", TEST_FILE])

    print(result.output, end="")

    assert result.exit_code == 0


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


@pytest.mark.skip()
@pytest.mark.parametrize(**paramaterize_cases(NOTE_FIX_CASES))
def test_fixes(cli_runner: CliRunner, content: str, corrected: str) -> None:
    """Test fix applies the correct."""
    result = cli_runner.invoke(console.cli, ["lint", "--fix", "-"])

    assert result.exit_code == 0
    assert result.output == corrected


@pytest.mark.skip()
def test_lint_files(cli_runner: CliRunner) -> None:
    """Test applies lint to all files given."""
    result = cli_runner.invoke(console.cli, ["lint-paths"])

    assert result.exit_code == 0, "\n" + result.output
