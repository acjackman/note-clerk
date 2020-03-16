"""note-clerk application tests."""
from click.testing import CliRunner

import note_clerk
from note_clerk import console


def test_main(cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = cli_runner.invoke(console.cli)
    assert result.exit_code == 0


def test_version_option(cli_runner: CliRunner) -> None:
    """Nersion number printed."""
    result = cli_runner.invoke(console.cli, "--version")
    assert result.exit_code == 0

    assert result.output == f"note-clerk, version {note_clerk.__version__}\n"


def test_info(cli_runner: CliRunner) -> None:
    """Test info command."""
    result = cli_runner.invoke(console.cli, "info")
    assert result.exit_code == 0

    assert result.output == f'Configuration Directory: "."\n'
