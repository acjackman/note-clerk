import datetime as dt
from functools import partial
from pathlib import Path
from typing import Optional

from note_clerk import utils


def day_link(date: dt.datetime, days: int = 0, link_fmt: str = "%Y-%m-%d") -> str:
    d = date + dt.timedelta(days=days)
    formatted = d.strftime(link_fmt)
    return f"[[{d:%Y%m%d}060000|{formatted}]]"


def week_label(date: dt.datetime) -> str:
    week_num = date.isocalendar()[1]
    return f"{date.year}W{week_num:02d}"


def week_link(date: dt.datetime, link_fmt: str = "%A %Y-%m-%d") -> str:
    week_start = last_monday(date)
    return f"[[{week_start:%Y%m%d}050000|{week_label(date)}]]"


def quarter_link(date: dt.datetime, link_fmt: str = "%A %Y-%m-%d") -> str:
    quarter = quarter_start(date)
    quarter_num = utils.month_to_quarter(quarter.month)
    return f"[[{quarter:%Y%m%d}020000|{quarter.year}Q{quarter_num}]]"


def generate_week_plan(date: dt.datetime) -> str:
    day = partial(day_link, date, link_fmt="%A %Y-%m-%d")

    week = week_label(date)
    week_num = date.isocalendar()[1]
    year = date.year
    return utils.trim(
        f"""
        ---
        created: {dt.datetime.utcnow():%Y-%m-%dT%H:%M:%S}Z
        type: note/plan/week
        top_level: "#{week}"
        alias: ["{week}"]
        ---
        # {year} Week {week_num}
        **Quarter:** {quarter_link(date)}

        ## Week Plan
        ### TODO

        ### Habits

        ## Action Plans
        - {day(0)}
        - {day(1)}
        - {day(2)}
        - {day(3)}
        - {day(4)}
        - {day(5)}
        - {day(6)}
        """
    )


def generate_day_plan(date: dt.datetime) -> str:
    day = partial(day_link, date)
    return utils.trim(
        f"""
        ---
        created: {dt.datetime.utcnow():%Y-%m-%dT%H:%M:%S}Z
        type: note/plan/day
        alias: ["{date:%Y-%m-%d}"]
        ---
        # {date:%Y-%m-%d}
        **Week:** {week_link(date)}
        **Yesterday:** {day(-1)}
        **Tomorrow:** {day(1)}

        ## Habits

        ## Log
        """
    )


def create_week_plan_file(date: dt.datetime, note_dir: Path) -> Path:
    filename = f"{date:%Y%m%d}050000.md"
    file = note_dir / filename
    if file.expanduser().exists():
        raise FileExistsError("Weekly plan already exists")
    with open(file.expanduser(), "w") as f:
        f.write(generate_week_plan(date))
    return file


def create_day_plan_file(date: dt.datetime, note_dir: Path) -> Path:
    filename = f"{date:%Y%m%d}060000.md"
    file = note_dir / filename
    if file.expanduser().exists():
        raise FileExistsError("Daily plan already exists")
    with open(file.expanduser(), "w") as f:
        f.write(generate_day_plan(date))
    return file


def quarter_start(date: Optional[dt.datetime] = None) -> dt.datetime:
    date = date or dt.datetime.now()
    month = date.month - ((date.month - 1) % 3)
    return date.replace(month=month, day=1, hour=0, minute=0, second=0, microsecond=0)


def last_monday(date: Optional[dt.datetime] = None) -> dt.datetime:
    date = date or dt.datetime.now()
    monday = date - dt.timedelta(days=date.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def determine_date(
    date: dt.datetime, _next: bool = False, _prev: bool = False
) -> dt.datetime:
    if _next and _prev:
        raise Exception("--next and --prev must not be passed together")
    elif _next:
        date += dt.timedelta(days=1)
    elif _prev:
        date -= dt.timedelta(days=1)
    return date
