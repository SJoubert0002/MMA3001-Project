"""Plot the fitted regression over the 15-minute slot means it was trained on.

Part of the analysis package.
"""

from pathlib import Path
import numpy as np
from .config import FIT_PLOT_YEAR, PERIOD_NAMES, SVR_C, SVR_EPSILON, SVR_LENGTH_HOURS, WEEKDAYS
from .predict_svr import predict_svr


def plot_fits(fits, year=FIT_PLOT_YEAR, room_names=None, save_folder=None):
    """Draw each fitted regression over the slot means it was trained on, one figure per room.

    Rows are the periods and columns are the weekdays. Each dot is a 15-minute slot mean of one
    date; the red line is the fitted regression.

    Input:
        fits: the dictionary made by score_rooms.
        year: the year to draw (default 2025).
        room_names: optional. Only these room labels are drawn (default: every room in fits).
        save_folder: optional. If given, each figure is saved there as a PNG instead of being shown.

    Output:
        A list of the figures' file paths if save_folder was given, otherwise an empty list.

    Errors:
        None.
    """
    import matplotlib.pyplot as plt

    saved = []
    grid_hours = np.arange(0, 24, 0.1)
    for room in sorted({key[0] for key in fits}):
        if room_names is not None and room not in room_names:
            continue
        fig, axes = plt.subplots(len(PERIOD_NAMES), 7, figsize=(22, 2.2 * len(PERIOD_NAMES)), sharex=True, squeeze=False)
        for r, period in enumerate(PERIOD_NAMES):
            for column in range(7):
                ax = axes[r][column]
                ax.grid(True, alpha=0.25)
                ax.tick_params(labelsize=6)
                if r == 0:
                    ax.set_title(WEEKDAYS[column], fontsize=9)
                key = (room, year, period, WEEKDAYS[column][:3])
                if key not in fits:
                    ax.text(0.5, 0.5, "no data", ha="center", va="center", fontsize=7, color="grey", transform=ax.transAxes)
                    continue
                fitted, slots = fits[key]
                ax.plot(slots.hour, slots.headcount, ".", markersize=2, alpha=0.35)
                ax.plot(grid_hours, predict_svr(fitted, grid_hours), color="crimson", linewidth=1.2)
        for column in range(7):
            axes[-1][column].set_xticks(range(0, 25, 6))
            axes[-1][column].set_xlabel("hour of day", fontsize=7)
        for r, period in enumerate(PERIOD_NAMES):
            axes[r][0].set_ylabel(period.replace("_", " "), fontsize=7)
        fig.suptitle(f"{room}, {year}: 15-minute slot means (dots) and SVR fit (red), C={SVR_C}, "
                     f"length={SVR_LENGTH_HOURS} h, eps={SVR_EPSILON}", y=1.0)
        fig.tight_layout()
        if save_folder is None:
            plt.show()
        else:
            Path(save_folder).mkdir(parents=True, exist_ok=True)
            safe = "".join(c if c.isalnum() else "-" for c in room)
            target = Path(save_folder) / f"fits_{safe}_{year}.png"
            fig.savefig(target, dpi=100)
            plt.close(fig)
            saved.append(target)
    return saved
