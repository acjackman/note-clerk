import datetime as dt

import pytest

from note_clerk import planning


@pytest.mark.parametrize(
    "date, quarter",
    [
        (dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 1)),
        (dt.datetime(2020, 1, 2), dt.datetime(2020, 1, 1)),
        (dt.datetime(2020, 4, 1), dt.datetime(2020, 4, 1)),
        (dt.datetime(2020, 4, 2), dt.datetime(2020, 4, 1)),
        (dt.datetime(2020, 5, 2), dt.datetime(2020, 4, 1)),
        (dt.datetime(2020, 6, 2), dt.datetime(2020, 4, 1)),
        (dt.datetime(2020, 7, 2), dt.datetime(2020, 7, 1)),
        (dt.datetime(2020, 8, 2), dt.datetime(2020, 7, 1)),
        (dt.datetime(2020, 9, 2), dt.datetime(2020, 7, 1)),
        (dt.datetime(2020, 10, 2), dt.datetime(2020, 10, 1)),
        (dt.datetime(2020, 11, 2), dt.datetime(2020, 10, 1)),
        (dt.datetime(2020, 12, 2), dt.datetime(2020, 10, 1)),
    ],
)
def test_quarter_start(date: dt.datetime, quarter: dt.datetime) -> None:
    adjusted = planning.quarter_start(date)
    assert adjusted == quarter
