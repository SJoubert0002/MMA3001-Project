"""Say which year and period a time falls in.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

import pandas as pd
from .label_periods import label_periods

def find_period(moment, calendar):
    """Say which year and period a time falls in.

    Input:
        moment: a time made by read_time.
        calendar: the dictionary made by read_semester_calendar.

    Output:
        A pair (year, period name), e.g. (2025, "semester_1").

    Errors:
        ValueError if the time's year is not in the calendar (add its dates to
            "Semester Calendar.csv" first).
    """
    if moment.year not in calendar:
        raise ValueError(f"The year {moment.year} is not in the semester calendar. "
                         f"Add its dates to Semester Calendar.csv.")
    label = label_periods(pd.Series([moment]), calendar).iloc[0]
    return moment.year, label
