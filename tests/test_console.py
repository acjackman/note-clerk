"""note-clerk application tests."""
from click.testing import CliRunner
import pytest

import note_clerk
from note_clerk import console


@pytest.fixture
def cli_runner() -> CliRunner:
    """Creates CliRunner instance."""
    return CliRunner()


def test_main(cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = cli_runner.invoke(console.cli)
    assert result.exit_code == 0


def test_version_option(cli_runner: CliRunner) -> None:
    """Nersion number printed."""
    result = cli_runner.invoke(console.cli, "--version")
    assert result.exit_code == 0

    assert result.output == f"main, version {note_clerk.__version__}\n"
