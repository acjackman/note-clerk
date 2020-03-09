"""note-clerk application tests."""
import click.testing

import note_clerk
from note_clerk import console


def test_main() -> None:
    """It exits with a status code of zero."""
    runner = click.testing.CliRunner()
    result = runner.invoke(console.main)
    assert result.exit_code == 0


def test_version_option() -> None:
    """Nersion number printed."""
    runner = click.testing.CliRunner()
    result = runner.invoke(console.main, "--version")
    assert result.exit_code == 0

    assert result.output == f"main, version {note_clerk.__version__}\n"
