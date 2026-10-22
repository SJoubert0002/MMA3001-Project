"""Read the semester dates for each year from the calendar file.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
import pandas as pd
from .config import CALENDAR_HEADINGS
from ..preprocessing.check_headings import check_headings

def read_semester_calendar(calendar_folders):
    """Read the semester dates for each year from the calendar file.

    The file is called "Semester Calendar.csv" and has one line per semester:
    year, semester (1 or 2), start_date (first day of week 1), end_date (last day
    of week 12), and break_start / break_end (the mid-semester break). Dates are
    written as YYYY-MM-DD. A year needs both its semesters.

    Input:
        calendar_folders: folders to search for the calendar file (e.g. the project's
            main folder).

    Output:
        A dictionary {year: {1: (start, end, break start, break end), 2: (...)}} with
        the dates as plain dates.

    Errors:
        FileNotFoundError if the calendar file is missing.
        ValueError if the headings are wrong, a date or semester is invalid, a year has
            a repeated or missing semester, a semester ends before it starts, the break
            is not inside its semester, or Semester 2 does not come after Semester 1.
    """
    files = [p for folder in calendar_folders for p in Path(folder).glob("Semester Calendar*.csv")]
    if not files:
        raise FileNotFoundError("Semester calendar file (Semester Calendar.csv) not found.")
    calendar_file = max(files, key=lambda p: p.stat().st_mtime_ns)
    check_headings(calendar_file, CALENDAR_HEADINGS)
    table = pd.read_csv(calendar_file, dtype=str, keep_default_na=False)

    dates = {}
    for _, row in table.iterrows():
        year, semester = row["year"].strip(), row["semester"].strip()
        parsed = [pd.to_datetime(row[heading], format="%Y-%m-%d", errors="coerce")
                  for heading in CALENDAR_HEADINGS[2:]]
        if not year.isdigit() or semester not in ("1", "2") or any(pd.isna(d) for d in parsed):
            raise ValueError(f"Invalid line in {calendar_file.name}: {row.to_dict()}")
        start, end, break_start, break_end = parsed
        if end < start or break_end < break_start:
            raise ValueError(f"Year {year} semester {semester} has dates that end before they start.")
        if not (start <= break_start and break_end <= end):
            raise ValueError(f"Year {year} semester {semester}: the break must be inside the semester.")
        if (int(year), int(semester)) in dates:
            raise ValueError(f"Year {year} semester {semester} appears more than once.")
        dates[(int(year), int(semester))] = tuple(d.date() for d in parsed)

    calendar = {}
    for year in sorted({y for y, _ in dates}):
        if (year, 1) not in dates or (year, 2) not in dates:
            raise ValueError(f"Year {year} needs both semester 1 and semester 2 in the calendar.")
        if dates[(year, 2)][0] <= dates[(year, 1)][1]:
            raise ValueError(f"Year {year}: semester 2 must start after semester 1 ends.")
        calendar[year] = {1: dates[(year, 1)], 2: dates[(year, 2)]}
    return calendar
