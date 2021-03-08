import datetime as dt

from click.testing import CliRunner
from freezegun import freeze_time
import pytest

from note_clerk import console, planning
from ._utils import FileFactory, show_output


@pytest.mark.parametrize(
    "current_date,plan_date",
    [
        (dt.datetime(2021, 3, 8), dt.datetime(2021, 3, 8)),
        (dt.datetime(2021, 3, 7), dt.datetime(2021, 3, 1)),
    ],
)
def test_lint_stdin_clean(
    cli_runner: CliRunner,
    file_factory: FileFactory,
    current_date: dt.datetime,
    plan_date: dt.datetime,
) -> None:
    expected_file = file_factory(
        filename=f"{plan_date:%Y%m%d}050000.md", path_only=True
    )
    tmpdir = expected_file.parent

    assert not expected_file.exists()

    with freeze_time(current_date):
        result = cli_runner.invoke(
            console.cli, [f"--config-dir={str(tmpdir)}", "plan", "week"]
        )

    show_output(result)
    assert result.exit_code == 0

    assert expected_file.exists()


def test_create_plan_file(file_factory: FileFactory) -> None:
    date = dt.datetime(2021, 3, 8)
    preexisting = file_factory(filename=f"{date:%Y%m%d}050000.md")

    with pytest.raises(FileExistsError):
        planning.create_plan_file(date, preexisting.parent)
