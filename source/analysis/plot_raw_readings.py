"""Plot every raw reading of one weekday of one period, one figure per room.

Part of the analysis package.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from ..preprocessing.ids_in_folder import ids_in_folder
from ..preprocessing.read_lookup import read_lookup
from .config import RAW_PLOT_YEAR, RAW_PLOT_PERIOD, RAW_PLOT_WEEKDAY, WEEKDAYS
from .label_periods import label_periods
from .read_room_data import read_room_data
from .room_label import room_label


def plot_raw_readings(calendar, streams_folder, lookup_folders, year=RAW_PLOT_YEAR, period=RAW_PLOT_PERIOD,
                      weekday=RAW_PLOT_WEEKDAY, room_ids=None, save_folder=None):
    """Draw every raw reading of one weekday of one period of one year, one figure per room.

    The x-axis is the time of day and each date is its own colour, so the spread between dates
    at the same time of day is visible. Needs the preprocessed room files (the raw readings).

    Input:
        calendar: the dictionary made by read_semester_calendar.
        streams_folder: the folder of preprocessed room files (see run_preprocessing).
        lookup_folders: folders to search for the lookup files, used to name the rooms.
        year: the year to draw (default 2024).
        period: "semester_1", "semester_2" or "non_teaching" (default "semester_1").
        weekday: 0 = Monday ... 6 = Sunday (default 0).
        room_ids: optional. Only these floorspace IDs are drawn (default: every room in the folder).
        save_folder: optional. If given, each figure is saved there as a PNG instead of being shown.

    Output:
        A list of the figures' file paths if save_folder was given, otherwise an empty list.
        A room with no readings in that period is skipped.

    Errors:
        FileNotFoundError if the lookup or a room file is missing.
        ValueError if a file's headings are wrong.
    """
    import matplotlib.pyplot as plt

    lookup = read_lookup(lookup_folders)
    chosen_ids = sorted(ids_in_folder(streams_folder) if room_ids is None else room_ids)
    saved = []
    for room_id in chosen_ids:
        data, times = read_room_data(room_id, streams_folder)
        headcounts = pd.to_numeric(data["headcount"], errors="coerce")
        chosen = ((label_periods(times, calendar) == period) & (times.dt.year == year)
                  & (times.dt.dayofweek == weekday) & headcounts.notna())
        if not chosen.any():
            continue
        days = times[chosen].dt.tz_localize(None)
        hours = (days - days.dt.normalize()).dt.total_seconds() / 3600
        dates = days.dt.normalize()
        fig, ax = plt.subplots(figsize=(14, 5))
        colours = plt.cm.viridis(np.linspace(0, 1, dates.nunique()))
        for colour, (date, group) in zip(colours, hours.groupby(dates)):
            ax.plot(group, headcounts[chosen][group.index], ".", markersize=2, color=colour, alpha=0.5,
                    label=date.strftime("%d %b"))
        ax.set_xlim(0, 24)
        ax.set_xticks(range(0, 25, 2), [f"{h % 24:02d}:00" for h in range(0, 25, 2)])
        ax.yaxis.get_major_locator().set_params(integer=True)
        ax.set_xlabel("Time of day (Melbourne time, 24-hour clock)")
        ax.set_ylabel("Headcount (people)")
        ax.set_title(f"{room_label(lookup, room_id)}: every {WEEKDAYS[weekday]} reading, {year} {period} "
                     f"({chosen.sum():,} readings)")
        ax.legend(ncol=7, fontsize=7, markerscale=4, loc="upper right")
        ax.grid(True, alpha=0.25)
        if save_folder is None:
            plt.show()
        else:
            Path(save_folder).mkdir(parents=True, exist_ok=True)
            target = Path(save_folder) / f"raw_readings_{room_id[:8]}_{year}_{period}_{WEEKDAYS[weekday][:3]}.png"
            fig.savefig(target, dpi=110)
            plt.close(fig)
            saved.append(target)
    return saved
