"""Plot the SVR's error against the constant-median baseline for each room and period.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
import numpy as np
from .config import PERIOD_NAMES


def plot_score_comparison(scores, save_file=None):
    """Plot the SVR's error against the constant-median baseline for each room and period.

    One group of bars per room and period (mean MAE over its year and weekday subsets), the SVR beside
    the baseline, so where the model helps and where it does not is visible at a glance. Lower is better.

    Input:
        scores: the table made by score_rooms (columns room, period, svr_mae, median_mae); subsets that
            were not scored are ignored.
        save_file: optional. A PNG path; the figure is saved there instead of being shown.

    Output:
        The saved file's path if save_file was given, otherwise None. None too if nothing was scored.

    Errors:
        None.
    """
    import matplotlib.pyplot as plt

    scored = scores.dropna(subset=["svr_mae"])
    if scored.empty:
        return None
    means = scored.groupby(["room", "period"])[["svr_mae", "median_mae"]].mean()
    means = means.reindex(PERIOD_NAMES, level="period").dropna().sort_index(level="room", sort_remaining=False)
    labels = [f"{room}\n{period.replace('_', ' ')}" for room, period in means.index]
    x = np.arange(len(means))
    fig, ax = plt.subplots(figsize=(max(8, 0.9 * len(means)), 5))
    ax.bar(x - 0.2, means["svr_mae"], 0.4, label="SVR model", color="tab:orange")
    ax.bar(x + 0.2, means["median_mae"], 0.4, label="constant median (baseline)", color="tab:grey")
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_ylabel("Mean absolute error (people), lower is better")
    wins = int((scored.svr_mae < scored.median_mae).sum())
    ax.set_title(f"Cross-validated error by room and period (SVR better in {wins} of {len(scored)} subsets)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    if save_file is None:
        plt.show()
        return None
    Path(save_file).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_file, dpi=110)
    plt.close(fig)
    return Path(save_file)
