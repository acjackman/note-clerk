import datetime as dt
from typing import List

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
def test_plan_week(
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


def test_create_week_plan_file_exists(file_factory: FileFactory) -> None:
    date = dt.datetime(2021, 3, 8)
    preexisting = file_factory(filename=f"{date:%Y%m%d}050000.md")

    with pytest.raises(FileExistsError):
        planning.create_week_plan_file(date, preexisting.parent)


def test_create_correct_week(
    cli_runner: CliRunner,
    file_factory: FileFactory,
) -> None:
    date = dt.datetime(2021, 3, 29)
    expected_file = file_factory(filename=f"{date:%Y%m%d}050000.md", path_only=True)
    tmpdir = expected_file.parent

    with freeze_time("2021-03-28"):
        result = cli_runner.invoke(
            console.cli,
            [f"--config-dir={str(tmpdir)}", "plan", "week", f"--date={date:%Y-%m-%d}"],
        )

    show_output(result)
    assert result.exit_code == 0
    assert expected_file.exists()


@pytest.mark.parametrize(
    "current_date,plan_date,args",
    [
        (dt.datetime(2021, 3, 8), dt.datetime(2021, 3, 8), []),
        (dt.datetime(2021, 3, 8), dt.datetime(2021, 3, 9), ["--next"]),
        (dt.datetime(2021, 3, 8), dt.datetime(2021, 3, 7), ["--prev"]),
    ],
)
def test_plan_day(
    cli_runner: CliRunner,
    file_factory: FileFactory,
    current_date: dt.datetime,
    plan_date: dt.datetime,
    args: List[str],
) -> None:
    expected_file = file_factory(
        filename=f"{plan_date:%Y%m%d}060000.md", path_only=True
    )
    tmpdir = expected_file.parent

    assert not expected_file.exists()

    with freeze_time(current_date):
        result = cli_runner.invoke(
            console.cli, [f"--config-dir={str(tmpdir)}", "plan", "day", *args]
        )

    show_output(result)
    assert result.exit_code == 0
    assert expected_file.exists()


def test_plan_day_not_next_and_prev(
    cli_runner: CliRunner,
    file_factory: FileFactory,
) -> None:
    current_date = dt.datetime(2021, 3, 8)
    plan_date = current_date
    expected_file = file_factory(
        filename=f"{plan_date:%Y%m%d}060000.md", path_only=True
    )
    tmpdir = expected_file.parent

    assert not expected_file.exists()

    with freeze_time(current_date):
        result = cli_runner.invoke(
            console.cli,
            [f"--config-dir={str(tmpdir)}", "plan", "day", "--next", "--prev"],
        )

    show_output(result)
    assert result.exit_code == 1
    assert expected_file.exists() is False


def test_create_day_plan_file_exists(file_factory: FileFactory) -> None:
    date = dt.datetime(2021, 3, 8)
    preexisting = file_factory(filename=f"{date:%Y%m%d}060000.md")

    with pytest.raises(FileExistsError):
        planning.create_day_plan_file(date, preexisting.parent)
