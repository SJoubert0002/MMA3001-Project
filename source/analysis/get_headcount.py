"""Return the expected headcount of a room at a time.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

import pandas as pd
from pathlib import Path
from .config import MODELS_DIR, MODEL_HEADINGS
from ..preprocessing.config import LOOKUP_FOLDERS
from .build_models import build_models
from ..preprocessing.check_headings import check_headings
from .evaluate_model import evaluate_model
from ..preprocessing.find_floorspace_ids import find_floorspace_ids
from .find_period import find_period
from .model_error import model_error
from ..preprocessing.ids_in_folder import ids_in_folder
from .read_time import read_time

def get_headcount(room_name, time_text, calendar, new_data_folder=None, label="", models_folder=None,
                  lookup_folders=None, details=None):
    """Return the expected headcount of a room at a time.

    With new data (a folder made by load_new_data): models are built from it for that
    room, saved next to the existing models (named after the label) and never replacing
    them, and the answer comes from the new model. Without new data: the saved model
    (made from the preprocessed data) is used; if there is none for that period, the
    newest model made from earlier supplied data is used.
    The answer is read from the regression of that period's model for the time's weekday
    (see evaluate_model), so it works at any minute of a weekday that has a regression.
    If that weekday has none in the period (too few dates), the answer is None.

    Input:
        room_name: the room, e.g. "G.20" (matched against the lookup file).
        time_text: the time, written YYYY-MM-DD HH:MM in Melbourne time.
        calendar: the dictionary made by read_semester_calendar.
        new_data_folder: optional. The folder of processed new data made by load_new_data.
        label: a short name for the new data (used in the model file names).
        models_folder: where models are read from and, with new data, saved (default: the project's data/models).
            See choose_output for where each kind of input should be kept.
        lookup_folders: folders searched for lookup files (default: the project's).
        details: optional. An empty dictionary that is filled, when a value is returned, with the model
            used: model_file, year, period, weekday, dates (trained on) and cv_mae (typical error in
            people, see model_error). It lets the caller report the answer's provenance and uncertainty.

    Output:
        The expected headcount (a number),         or None if the model has no data for that weekday.

    Errors:
        ValueError if the time is invalid, its year is not in the calendar, the room
            is not covered, or the new data has no readings for that room and period.
        FileNotFoundError if no new data is given and there is no saved model.
    """
    moment = read_time(time_text)
    year, period = find_period(moment, calendar)
    models_folder = MODELS_DIR if models_folder is None else Path(models_folder)
    lookup_folders = LOOKUP_FOLDERS if lookup_folders is None else lookup_folders

    if new_data_folder is not None:
        ids = find_floorspace_ids([room_name], lookup_folders, ids_in_folder(new_data_folder))
        floorspace_id = ids[room_name]
        built = build_models(floorspace_id, calendar, new_data_folder, models_folder, label=label)
        print(f"Built {len(built)} model(s) for {room_name} from the new data.")
        name = f"{year}_{period}_{label}.csv"
        if not (built["model_file"] == name).any():
            raise ValueError(f"The new data has no readings for {room_name} in {year} {period}.")
        candidates = [models_folder / floorspace_id / name]
    else:
        ids = find_floorspace_ids([room_name], lookup_folders, ids_in_folder(models_folder))
        floorspace_id = ids[room_name]
        # The model made from the preprocessed data first, then those made from supplied data, newest first.
        exact = models_folder / floorspace_id / f"{year}_{period}.csv"
        extras = sorted((models_folder / floorspace_id).glob(f"{year}_{period}_*.csv"),
                        key=lambda f: f.stat().st_mtime_ns, reverse=True)
        candidates = ([exact] if exact.is_file() else []) + extras
        if not candidates:
            raise FileNotFoundError(f"No saved model for {room_name} in {year} {period}. "
                                    f"Supply a data file covering that period.")

    for model_file in candidates:
        check_headings(model_file, MODEL_HEADINGS)
        model = pd.read_csv(model_file)
        value = evaluate_model(model, moment)
        if value is not None:
            if new_data_folder is None and model_file.name != f"{year}_{period}.csv":
                print(f"Using the model made from supplied data: {model_file.name}")
            if details is not None:
                error, dates = model_error(model, moment.dayofweek)
                details.update(model_file=model_file.name, year=year, period=period, weekday=moment.dayofweek,
                               dates=dates, cv_mae=error)
            return value
    print(f"NO VALUE: the {year} {period} model(s) of {room_name}     have no data for that weekday "
              f"({time_text}). Supply data that covers it.")
    return None
