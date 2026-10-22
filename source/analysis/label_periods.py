"""Give every reading time the name of the period it belongs to.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

import pandas as pd

def label_periods(times, calendar):
    """Give every reading time the name of the period it belongs to.

    The periods are listed in PERIOD_NAMES: semester_1 and semester_2 (their teaching days, so the
    mid-semester breaks are left out) and non_teaching (every other day of the year: before
    Semester 1, the mid-semester breaks, the mid-year break, after Semester 2). A time in a year
    that is not in the calendar gets no name (it is left empty).

    Input:
        times: a column of times in Melbourne time.
        calendar: the dictionary made by read_semester_calendar.

    Output:
        A column of period names, the same length and order as the times.
    """
    days = times.dt.tz_localize(None).dt.normalize()
    labels = pd.Series([None] * len(times), index=times.index, dtype=object)
    for year, semesters in calendar.items():
        in_year = days.dt.year == year
        labels[in_year] = "non_teaching"
        for number in (1, 2):
            start, end, break_start, break_end = (pd.Timestamp(d) for d in semesters[number])
            labels[in_year & (days >= start) & (days <= end) & ~((days >= break_start) & (days <= break_end))] = f"semester_{number}"
    return labels
