"""Plot one day's raw headcount readings with the period's model drawn over them.

Part of the analysis package; the two public plots (plot_new_data_day, plot_training_day) call it.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from .evaluate_model import evaluate_model
from .config import WEEKDAYS
from .label_periods import label_periods
from .model_error import model_error
from .read_room_data import read_room_data


def plot_day_against_model(model_file, streams_folder, floorspace_id, moment, title, calendar, save_file=None):
    """Plot the readings of one date with the model of that date's weekday drawn over them.

    The readings come straight from the room's preprocessed file (the post-processed input), every
    reading of that date. The line is the saved regression for that weekday, read with evaluate_model
    at every minute of the day, with a shaded band of the model's typical error (its cross-validated
    mean absolute error, see model_error), and a marker shows the model's value at the requested time.
    The same weekday's readings on the period's other dates are drawn faintly behind, for context.
    If the preprocessed file has no readings for that date the model is still drawn and a note says so.

    Input:
        model_file: the saved model (CSV) of the date's year and period.
        streams_folder: the folder of preprocessed room files that holds the readings.
        floorspace_id: the room's floorspace ID (names its preprocessed file).
        moment: the requested time (made by read_time), in Melbourne time.
        title: the figure title (say the room, date and period).
        calendar: the dictionary made by read_semester_calendar (finds the period's other dates).
        save_file: optional. A PNG path; the figure is saved there instead of being shown.

    Output:
        The saved file's path if save_file was given, otherwise None (the figure was shown).

    Errors:
        FileNotFoundError if the model file or the room's preprocessed file is missing.
        ValueError if a file's headings are wrong.
    """
    import matplotlib.pyplot as plt

    model_file = Path(model_file)
    if not model_file.is_file():
        raise FileNotFoundError(f"No model file {model_file}.")
    model = pd.read_csv(model_file)
    data, times = read_room_data(floorspace_id, streams_folder)
    all_counts = pd.to_numeric(data["headcount"], errors="coerce")
    all_hours = times.dt.hour + times.dt.minute / 60 + times.dt.second / 3600
    on_day = (times.dt.date == moment.date()).to_numpy()
    headcounts, hours = all_counts[on_day], all_hours[on_day]
    period = label_periods(pd.Series([moment]), calendar).iloc[0]
    others = ((label_periods(times, calendar) == period) & (times.dt.year == moment.year)
              & (times.dt.dayofweek == moment.dayofweek)).to_numpy() & ~on_day & all_counts.notna().to_numpy()

    start = moment.normalize()
    grid = np.arange(0, 24, 1 / 60)
    curve = [evaluate_model(model, start + pd.Timedelta(hours=float(h))) for h in grid]
    value_now = evaluate_model(model, moment)
    error = model_error(model, moment.dayofweek)
    curve_top = (max(curve) + error[0]) if value_now is not None else 0.0

    fig, ax = plt.subplots(figsize=(14, 5))
    if others.any():
        ax.plot(all_hours[others], all_counts[others], ".", markersize=2, color="lightgrey", alpha=0.5, zorder=1,
                label=f"other {WEEKDAYS[moment.dayofweek]}s this period")
    if headcounts.notna().any():
        ax.plot(hours[headcounts.notna()], headcounts.dropna(), ".", markersize=3, color="tab:blue", alpha=0.6,
                zorder=2, label=f"raw readings on the day ({headcounts.notna().sum():,})")
    else:
        ax.text(0.5, 0.92, "No readings for this date in the preprocessed file", transform=ax.transAxes,
                ha="center", color="tab:red")
    if value_now is not None:
        low = np.maximum(np.array(curve) - error[0], 0)
        ax.fill_between(grid, low, np.array(curve) + error[0], color="tab:orange", alpha=0.2, zorder=3,
                        label=f"typical error ±{error[0]:.1f} (whole-day average; {error[1]} training dates)")
        ax.plot(grid, curve, color="tab:orange", linewidth=2, zorder=4, label=f"model ({model_file.stem})")
        now_hour = moment.hour + moment.minute / 60
        ax.plot([now_hour], [value_now], "o", color="black", zorder=5, label=f"requested time: {value_now:.1f} people")
    else:
        ax.text(0.5, 0.85, "The model has no regression for this weekday", transform=ax.transAxes,
                ha="center", color="tab:red")
    ax.set_xlim(0, 24)
    top = max([curve_top] + ([float(headcounts.max())] if headcounts.notna().any() else []))
    ax.set_ylim(0, top * 1.15 + 1)
    ax.set_xticks(range(0, 25, 2), [f"{h % 24:02d}:00" for h in range(0, 25, 2)])
    ax.set_xlabel("Time of day (Melbourne time, 24-hour clock)")
    ax.set_ylabel("Headcount (people)")
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right")
    if save_file is None:
        plt.show()
        return None
    Path(save_file).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_file, dpi=110)
    plt.close(fig)
    return Path(save_file)
