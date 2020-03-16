"""Note-clerk application tests."""
from click.testing import CliRunner

from note_clerk import console


def test_list_no_files(cli_runner: CliRunner) -> None:
    """List no files."""
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(console.cli, "list-files")

    assert result.exit_code == 0

    assert result.output == f""


def test_list_directory_single_file(cli_runner: CliRunner) -> None:
    """List directory with single file."""
    with cli_runner.isolated_filesystem():
        with open("hello.txt", "w") as f:
            f.write("Hello World!")

        result = cli_runner.invoke(console.cli, "list-files")

    assert result.exit_code == 0

    assert result.output == f"hello.txt\n"


def test_list_single_file(cli_runner: CliRunner) -> None:
    """List single file."""
    with cli_runner.isolated_filesystem():
        with open("hello.txt", "w") as f:
            f.write("Hello World!")

        result = cli_runner.invoke(console.cli, "list-files", "hello.txt")

    assert result.exit_code == 0

    assert result.output == f"hello.txt\n"
