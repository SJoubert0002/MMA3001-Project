"""Plot the day of a query for new data: its model over its raw readings.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

from .find_period import find_period
from ..preprocessing.find_floorspace_ids import find_floorspace_ids
from ..preprocessing.ids_in_folder import ids_in_folder
from .plot_day_against_model import plot_day_against_model
from .read_time import read_time


def plot_new_data_day(room_name, time_text, calendar, new_data_folder, models_folder, label, lookup_folders,
                      save_file=None):
    """Plot the queried day of a room for new data: the model built from it over the day's raw readings.

    Use it after get_headcount was given the same new data, so the new data's model for that
    period exists. The readings are those in the new data's preprocessed room file (from load_new_data).

    Input:
        room_name: the room, e.g. "G.20".
        time_text: the time, YYYY-MM-DD HH:MM (Melbourne time); its date and period are plotted.
        calendar: the dictionary made by read_semester_calendar.
        new_data_folder: the folder of preprocessed new data made by load_new_data.
        models_folder: the folder the new data's models were saved in.
        label: the name of the new data (as given to get_headcount).
        lookup_folders: folders searched for lookup files.
        save_file: optional. A PNG path; the figure is saved there instead of being shown.

    Output:
        The saved file's path if save_file was given, otherwise None.

    Errors:
        ValueError if the time or room is invalid or the year is not in the calendar.
        FileNotFoundError if the new data's model for that period does not exist.
    """
    moment = read_time(time_text)
    year, period = find_period(moment, calendar)
    floorspace_id = find_floorspace_ids([room_name], lookup_folders, ids_in_folder(new_data_folder))[room_name]
    model_file = models_folder / floorspace_id / f"{year}_{period}_{label}.csv"
    title = f"{room_name}, new data ({label}): {moment:%A %d %b %Y}, {year} {period}"
    return plot_day_against_model(model_file, new_data_folder, floorspace_id, moment, title, calendar, save_file)
