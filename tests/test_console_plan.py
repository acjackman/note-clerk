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


def test_create_full_week(
    cli_runner: CliRunner,
    file_factory: FileFactory,
) -> None:
    date = dt.datetime(2021, 3, 15)
    expected_files = [
        file_factory(filename="20210315050000.md", path_only=True),
        file_factory(filename="20210315060000.md", path_only=True),
        file_factory(filename="20210316060000.md", path_only=True),
        file_factory(filename="20210317060000.md", path_only=True),
        file_factory(filename="20210318060000.md", path_only=True),
        file_factory(filename="20210319060000.md", path_only=True),
        file_factory(filename="20210320060000.md", path_only=True),
        file_factory(filename="20210321060000.md", path_only=True),
    ]
    expected_file = file_factory(filename=f"{date:%Y%m%d}050000.md", path_only=True)
    tmpdir = expected_file.parent

    with freeze_time(date):
        result = cli_runner.invoke(
            console.cli,
            [
                f"--config-dir={str(tmpdir)}",
                "plan",
                "full-week",
            ],
        )

    show_output(result)
    assert result.exit_code == 0
    for file in expected_files:
        assert file.exists()


def test_create_full_week_specific_date(
    cli_runner: CliRunner,
    file_factory: FileFactory,
) -> None:
    date = dt.datetime(2021, 3, 22)
    expected_files = [
        file_factory(filename="20210322050000.md", path_only=True),
        file_factory(filename="20210322060000.md", path_only=True),
        file_factory(filename="20210323060000.md", path_only=True),
        file_factory(filename="20210324060000.md", path_only=True),
        file_factory(filename="20210325060000.md", path_only=True),
        file_factory(filename="20210326060000.md", path_only=True),
        file_factory(filename="20210327060000.md", path_only=True),
        file_factory(filename="20210328060000.md", path_only=True),
    ]
    expected_file = file_factory(filename=f"{date:%Y%m%d}050000.md", path_only=True)
    tmpdir = expected_file.parent

    with freeze_time("2021-03-21"):
        result = cli_runner.invoke(
            console.cli,
            [
                f"--config-dir={str(tmpdir)}",
                "plan",
                "full-week",
                f"--date={date:%Y-%m-%d}",
            ],
        )

    show_output(result)
    assert result.exit_code == 0
    for file in expected_files:
        assert file.exists()


def test_create_full_week_next_from_sat(
    cli_runner: CliRunner,
    file_factory: FileFactory,
) -> None:
    date = dt.datetime(2021, 3, 22)
    expected_files = [
        file_factory(filename="20210322050000.md", path_only=True),
        file_factory(filename="20210322060000.md", path_only=True),
        file_factory(filename="20210323060000.md", path_only=True),
        file_factory(filename="20210324060000.md", path_only=True),
        file_factory(filename="20210325060000.md", path_only=True),
        file_factory(filename="20210326060000.md", path_only=True),
        file_factory(filename="20210327060000.md", path_only=True),
        file_factory(filename="20210328060000.md", path_only=True),
    ]
    expected_file = file_factory(filename=f"{date:%Y%m%d}050000.md", path_only=True)
    tmpdir = expected_file.parent

    with freeze_time("2021-03-20"):
        result = cli_runner.invoke(
            console.cli,
            [
                f"--config-dir={str(tmpdir)}",
                "plan",
                "full-week",
                "--next",
            ],
        )

    show_output(result)
    assert result.exit_code == 0
    for file in expected_files:
        assert file.exists()


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
