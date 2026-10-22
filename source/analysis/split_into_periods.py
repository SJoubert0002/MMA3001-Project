"""Split one room's headcount data into the periods of each covered year.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
import pandas as pd
from .config import PERIOD_NAMES
from .label_periods import label_periods
from .read_room_data import read_room_data

def split_into_periods(floorspace_id, calendar, streams_folder, output_folder):
    """Split one room's headcount data into the periods of each covered year.

    Every reading is placed in exactly one period. Readings are put in time order
    first (the raw data has a few out of order). A year that is not in the calendar is
    reported as not covered and skipped. Old files for this room are replaced.

    Input:
        floorspace_id: the room's floorspace ID.
        calendar: the dictionary made by read_semester_calendar.
        streams_folder: the folder of room files made by the preprocessing.
        output_folder: where the period files are saved. This room's files go in a
            sub-folder named after its floorspace ID, one file per year and period,
            e.g. "2024_semester_1.csv", each with headcount and collecteddate.

    Output:
        A table with one line per year and period: how many readings it holds, and the
        first and last reading times. Periods with no data are listed with 0 readings.

    Errors:
        FileNotFoundError if the room's data file is missing.
        ValueError if the headings are wrong, a time is invalid, or the periods do not
            add back up to all the readings of a year.
    """
    data, times = read_room_data(floorspace_id, streams_folder)
    labels = label_periods(times, calendar)

    room_folder = Path(output_folder) / floorspace_id
    room_folder.mkdir(parents=True, exist_ok=True)
    for old_file in room_folder.glob("*.csv"):
        old_file.unlink()

    lines = []
    for year in sorted(times.dt.year.unique()):
        if year not in calendar:
            print(f"NOT COVERED: {floorspace_id} year {year} is not in the semester calendar, so it was skipped.")
            continue
        in_year = times.dt.year == year
        placed = 0
        for number, name in enumerate(PERIOD_NAMES):
            in_period = in_year & (labels == name)
            rows = int(in_period.sum())
            placed += rows
            if rows:
                data.loc[in_period].to_csv(room_folder / f"{year}_{name}.csv", index=False)
            lines.append({"floorspace_id": floorspace_id, "year": year, "period": f"{number + 1}_{name}", "rows": rows,
                          "first_time": times[in_period].min() if rows else None,
                          "last_time": times[in_period].max() if rows else None})
        if placed != int(in_year.sum()):
            raise ValueError(f"{floorspace_id} year {year}: readings were lost or duplicated while splitting.")
    return pd.DataFrame(lines, columns=["floorspace_id", "year", "period", "rows", "first_time", "last_time"])
