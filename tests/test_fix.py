import logging

from click.testing import CliRunner

from note_clerk import console
from ._utils import inline_note


log = logging.getLogger(__name__)


def test_fix_collapses_headers(cli_runner: CliRunner) -> None:
    original = inline_note(
        """
        ---
        tags: ["#tag2"]
        created: 2020-11-15T05:42:49.301Z
        ---
        ---
        created: 2020-11-15T05:42:49.301Z
        tags: ["#inbox"]
        ---
        # Test Note
        """
    )

    fixed = inline_note(
        """
        ---
        created: 2020-11-15T05:42:49.301000Z
        tags:
        - '#tag2'
        - '#inbox'
        ***
        # Test Note
        """,
        trailing_newline=True,
    )

    result = cli_runner.invoke(
        console.cli, ["--log-level=DEBUG", "fix", "-"], input=original
    )

    print(result.output)

    assert result.output == fixed


def test_fix_no_close_header(cli_runner: CliRunner) -> None:
    original = inline_note(
        """
        ---
        tags: ["#tag2"]
        created: 2020-11-15T05:42:49.301Z
        created: 2020-11-15T05:42:49.301Z
        tags: ["#inbox"]
        # Test Note
        """
    )

    result = cli_runner.invoke(
        console.cli, ["--log-level=DEBUG", "fix", "-"], input=original
    )

    print(result.output)

    assert result.exit_code != 0
