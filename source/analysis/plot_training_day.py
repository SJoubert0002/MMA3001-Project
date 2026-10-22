"""Plot the day of a query for the training data: the saved model over its raw readings.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

from .config import MODELS_DIR
from .find_period import find_period
from ..preprocessing.config import LOOKUP_FOLDERS, OUTPUT_DIR
from ..preprocessing.find_floorspace_ids import find_floorspace_ids
from ..preprocessing.ids_in_folder import ids_in_folder
from .plot_day_against_model import plot_day_against_model
from .read_time import read_time

TRAINING_STREAMS = OUTPUT_DIR / "occupancy_streams"


def plot_training_day(room_name, time_text, calendar, streams_folder=TRAINING_STREAMS, models_folder=MODELS_DIR,
                      lookup_folders=LOOKUP_FOLDERS, save_file=None):
    """Plot the queried day of a room for the training data: the saved model over the day's raw readings.

    The model is the project's saved model for that year and period (the one made from the training
    data, if there is one). The readings are those in the training data's preprocessed room file, so
    a date the training data does not cover (for example one in 2025) shows the model alone.

    Input:
        room_name: the room, e.g. "G.20".
        time_text: the time, YYYY-MM-DD HH:MM (Melbourne time); its date and period are plotted.
        calendar: the dictionary made by read_semester_calendar.
        streams_folder: the folder of the training data's preprocessed room files
            (default: data/derived/preprocessed/occupancy_streams, made by run_preprocessing).
        models_folder: the folder of saved models (default: data/models).
        lookup_folders: folders searched for lookup files.
        save_file: optional. A PNG path; the figure is saved there instead of being shown.

    Output:
        The saved file's path if save_file was given, otherwise None.

    Errors:
        ValueError if the time or room is invalid or the year is not in the calendar.
        FileNotFoundError if there is no saved model for that period, or the training data
            has not been preprocessed (run run_preprocessing on the raw training file first).
    """
    moment = read_time(time_text)
    year, period = find_period(moment, calendar)
    floorspace_id = find_floorspace_ids([room_name], lookup_folders, ids_in_folder(models_folder))[room_name]
    model_file = models_folder / floorspace_id / f"{year}_{period}.csv"
    if not (streams_folder / f"{floorspace_id}.csv").is_file():
        raise FileNotFoundError(f"The training data has not been preprocessed ({streams_folder} has no file for "
                                f"{room_name}). Run run_preprocessing on the raw training file first.")
    title = f"{room_name}, training data: {moment:%A %d %b %Y}, {year} {period}"
    return plot_day_against_model(model_file, streams_folder, floorspace_id, moment, title, calendar, save_file)
