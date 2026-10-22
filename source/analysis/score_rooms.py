"""Score the regression of every room, year, period and weekday against a constant-median baseline.

Part of the analysis package.
"""

import pandas as pd
from ..preprocessing.ids_in_folder import ids_in_folder
from ..preprocessing.read_lookup import read_lookup
from .config import PERIOD_NAMES, WEEKDAYS
from .fit_svr import fit_svr
from .label_periods import label_periods
from .read_room_data import read_room_data
from .room_label import room_label
from .score_svr import score_svr
from .slot_means import slot_means


def score_rooms(calendar, streams_folder, lookup_folders, room_ids=None):
    """Score the regression of every subset of every room by cross-validation that holds out whole dates.

    A subset is one room, year, period and weekday. Each is scored by score_svr (4 folds, whole dates
    held out) against predicting the training median. A weekday with too few dates is listed but not scored.
    Years that are not in the calendar are skipped.

    Input:
        calendar: the dictionary made by read_semester_calendar.
        streams_folder: the folder of preprocessed room files (see run_preprocessing).
        lookup_folders: folders to search for the room lookup files (see read_lookup); used to name the rooms.
        room_ids: optional. Only these floorspace IDs are scored (default: every room in the folder).

    Output:
        A pair (scores, fits).
        scores: a table with one line per subset: room_id, room, year, period, weekday, dates,
            svr_mae, median_mae and a note (svr_mae and median_mae are empty if not scored).
        fits: a dictionary {(room, year, period, weekday): (fitted regression, slot means)} for the
            scored subsets, ready for plot_fits.

    Errors:
        FileNotFoundError if the lookup or a room file is missing.
        ValueError if a file's headings are wrong.
    """
    lookup = read_lookup(lookup_folders)
    chosen = sorted(ids_in_folder(streams_folder) if room_ids is None else room_ids)
    rows, fits = [], {}
    for room_id in chosen:
        room = room_label(lookup, room_id)
        data, times = read_room_data(room_id, streams_folder)
        counts = pd.to_numeric(data["headcount"], errors="coerce")
        labels = label_periods(times, calendar)
        for year in sorted(times.dt.year.unique()):
            if year not in calendar:
                continue
            for period in PERIOD_NAMES:
                for weekday in range(7):
                    chosen_rows = ((labels == period) & (times.dt.year == year) & (times.dt.dayofweek == weekday)
                                   & counts.notna()).to_numpy()
                    if not chosen_rows.any():
                        continue
                    slots = slot_means(times[chosen_rows], counts[chosen_rows])
                    result = score_svr(slots)
                    group = WEEKDAYS[weekday][:3]
                    row = {"room_id": room_id, "room": room, "year": year, "period": period, "weekday": group,
                           "dates": slots.date.nunique(), "svr_mae": None, "median_mae": None, "note": ""}
                    if result is None:
                        row["note"] = "not scored (too few dates)"
                    else:
                        row["svr_mae"], row["median_mae"] = result
                        fits[(room, year, period, group)] = (fit_svr(slots.hour, slots.headcount), slots)
                    rows.append(row)
    return pd.DataFrame(rows), fits
