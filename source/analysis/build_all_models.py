"""Build the saved models of every room in a folder of room files.

Part of the analysis package.
"""

import pandas as pd
from ..preprocessing.ids_in_folder import ids_in_folder
from .build_models import build_models
from .split_into_periods import split_into_periods


def build_all_models(calendar, streams_folder, models_folder, periods_folder=None, room_ids=None):
    """Build and save the models of every room (or the chosen rooms) in a folder of preprocessed room files.

    For each room, build_models saves one model per year and period (see build_models). Rooms
    the lookup does not name are included: their floorspace ID is their only label.

    Input:
        calendar: the dictionary made by read_semester_calendar.
        streams_folder: the folder of preprocessed room files (see run_preprocessing).
        models_folder: the folder to save the models in. Each room gets a sub-folder named by its ID.
        periods_folder: optional. If given, the readings of each room are also saved split by year
            and period (see split_into_periods), for checking the split by eye.
        room_ids: optional. Only these floorspace IDs are built (default: every room in the folder).

    Output:
        A table with one line per model saved (floorspace_id, year, period, readings, model_file).
        Empty if there were no rooms.

    Errors:
        ValueError or FileNotFoundError as raised by build_models and split_into_periods.
    """
    chosen = sorted(ids_in_folder(streams_folder) if room_ids is None else room_ids)
    tables = []
    for floorspace_id in chosen:
        if periods_folder is not None:
            split_into_periods(floorspace_id, calendar, streams_folder, periods_folder)
        tables.append(build_models(floorspace_id, calendar, streams_folder, models_folder))
    return pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()
