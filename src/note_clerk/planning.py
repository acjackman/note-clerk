import datetime as dt
from inspect import cleandoc as trim
from pathlib import Path
from typing import Optional


def generate_plan(date: dt.datetime) -> str:
    def day(days: int = 0) -> str:
        return f"{date + dt.timedelta(days=days):%A %Y-%m-%d}"

    week_num = date.isocalendar()[1]
    year = date.year
    return (
        trim(
            f"""
        ---
        created: {dt.datetime.utcnow():%Y-%m-%dT%H:%M:%S}Z
        type: note
        top_level: "#{year}W{week_num:02d}"
        ---
        # {year} Week {week_num}

        ## TODO

        ## Habits

        ## Week Plan
        ### {day(0)}


        ### {day(1)}


        ### {day(2)}


        ### {day(3)}


        ### {day(4)}


        ### {day(5)}


        ### {day(6)}
        """
        )
        + "\n"
    )


def create_plan_file(date: dt.datetime, note_dir: Path) -> Path:
    filename = f"{date:%Y%m%d}050000.md"
    file = note_dir / filename
    if file.expanduser().exists():
        raise FileExistsError("Weekly plan already exists")
    with open(file.expanduser(), "w") as f:
        f.write(generate_plan(date))
    return file


def last_monday(date: Optional[dt.datetime] = None) -> dt.datetime:
    date = date or dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return date - dt.timedelta(days=date.weekday())
