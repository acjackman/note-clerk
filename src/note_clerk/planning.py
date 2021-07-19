import datetime as dt
from functools import partial
from os import PathLike
from pathlib import Path
from typing import Iterable, Optional, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape

from note_clerk import utils

TEMPLATES = Path(__file__).parent / "templates"


def day_link(date: dt.datetime, days: int = 0, link_fmt: str = "%Y-%m-%d") -> str:
    d = date + dt.timedelta(days=days)
    formatted = d.strftime(link_fmt)
    return f"[[{d:%Y%m%d}060000|{formatted}]]"


def week_label(date: dt.datetime) -> str:
    week_num = date.isocalendar()[1]
    return f"{date.year}W{week_num:02d}"


def week_link(date: dt.datetime) -> str:
    week_start = last_monday(date)
    return f"[[{week_start:%Y%m%d}050000|{week_label(date)}]]"


def quarter_link(date: dt.datetime) -> str:
    quarter = quarter_start(date)
    quarter_num = utils.month_to_quarter(quarter.month)
    return f"[[{quarter:%Y%m%d}020000|{quarter.year}Q{quarter_num}]]"


def get_jinja_env(
    template_dirs: Optional[Iterable[Union[str, PathLike]]] = None
) -> Environment:
    template_dirs = [*(template_dirs or []), TEMPLATES]
    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(),
    )
    env.filters["timedelta"] = lambda v, days: v + dt.timedelta(days=days)
    env.filters["quarter_link"] = quarter_link
    env.filters["week_link"] = week_link
    env.filters["strftime"] = lambda value, format: value.strftime(format)
    return env


def generate_week_plan(date: dt.datetime, extension: str = "md") -> str:
    env = get_jinja_env()
    template = env.get_template(f"week_plan.{extension}")
    ctx = {
        "now_utc": dt.datetime.utcnow(),
        "date": date,
        "week_label": week_label(date),
        "week_num": date.isocalendar()[1],
        "year": date.year,
        "day": partial(day_link, date, link_fmt="%A %Y-%m-%d"),
    }
    return utils.trim(template.render(**ctx))


def generate_day_plan(date: dt.datetime, extension: str = "md") -> str:
    env = get_jinja_env()
    template = env.get_template(f"day_plan.{extension}")
    ctx = {
        "now_utc": dt.datetime.utcnow(),
        "date": date,
        "day": partial(day_link, date),
    }
    return utils.trim(template.render(**ctx))


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


def adjust_date(
    date: dt.datetime,
    _next: bool = False,
    _prev: bool = False,
    delta: dt.timedelta = None,
) -> dt.datetime:
    delta = delta or dt.timedelta(days=1)

    if _next and _prev:
        raise Exception("--next and --prev must not be passed together")
    elif _next:
        date += delta
    elif _prev:
        date -= delta
    return date
