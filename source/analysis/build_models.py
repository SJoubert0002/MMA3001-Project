"""Build and save a model for every year and period that has readings for one room.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
import pandas as pd
from .config import PERIOD_NAMES, SVR_MIN_DATES
from .label_periods import label_periods
from .make_model import make_model
from .read_room_data import read_room_data

def build_models(floorspace_id, calendar, streams_folder, models_folder, label=""):
    """Build and save a model for every year and period that has readings for one room.

    Each period of each year gets its own model of one regression per weekday
    (see make_model). A period with no weekday that has enough dates is reported and skipped.
    Models are saved next to the existing ones and never overwrite a model made from
    different data. With no label the files are named "<year>_<period>.csv"; with a
    label they are named "<year>_<period>_<label>.csv" (running again with the same
    label replaces only that label's models). A year not in the calendar is reported
    and skipped.

    Input:
        floorspace_id: the room's floorspace ID.
        calendar: the dictionary made by read_semester_calendar.
        streams_folder: the folder of room files made by the preprocessing.
        models_folder: where models are saved, as models_folder / floorspace ID / file.
        label: optional short name for where the data came from (e.g. the new file's name).

    Output:
        A table listing each model built: year, period, number of support vectors saved
        ("readings" column) and the model's file name.

    Errors:
        FileNotFoundError, ValueError as in read_room_data.
    """
    data, times = read_room_data(floorspace_id, streams_folder)
    labels = label_periods(times, calendar)
    headcounts = pd.to_numeric(data["headcount"], errors="coerce")
    room_folder = Path(models_folder) / floorspace_id
    room_folder.mkdir(parents=True, exist_ok=True)

    built = []
    for year in sorted(times.dt.year.unique()):
        if year not in calendar:
            print(f"NOT COVERED: {floorspace_id} year {year} is not in the semester calendar, so no model was built.")
            continue
        for name in PERIOD_NAMES:
            chosen = (labels == name) & (times.dt.year == year) & headcounts.notna()
            if chosen.any():
                model = make_model(times[chosen], headcounts[chosen])
                if model.empty:
                    print(f"NOT COVERED: {floorspace_id} {year} {name} has no weekday with at least {SVR_MIN_DATES} dates, so no model was built.")
                    continue
                file_name = f"{year}_{name}_{label}.csv" if label else f"{year}_{name}.csv"
                model.to_csv(room_folder / file_name, index=False)
                built.append({"floorspace_id": floorspace_id, "year": year, "period": name,
                              "readings": len(model), "model_file": file_name})
    return pd.DataFrame(built, columns=["floorspace_id", "year", "period", "readings", "model_file"])
