"""Plot every saved model: the regression of each weekday, one panel per year and period.

Part of the analysis package.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from ..preprocessing.config import LOOKUP_FOLDERS
from ..preprocessing.read_lookup import read_lookup
from .config import MODELS_DIR, PERIOD_NAMES, WEEKDAYS
from .evaluate_model import evaluate_model
from .room_label import room_label


def plot_saved_models(models_folder=MODELS_DIR, lookup_folders=LOOKUP_FOLDERS, room_ids=None, save_folder=None):
    """Draw the saved regression of every weekday for every saved model, to check the fit by eye.

    One figure per room, one panel per year and period, one coloured line per weekday. Only the
    saved models are used (no raw data is needed). Models made from supplied data (with a label
    in their name) are not drawn.

    Input:
        models_folder: the folder of saved models (default: the project's models folder).
        lookup_folders: folders to search for the lookup files, used to name the rooms.
        room_ids: optional. Only these floorspace IDs are drawn (default: every room with models).
        save_folder: optional. If given, each figure is saved there as a PNG instead of being shown.

    Output:
        A list of the figures' file paths if save_folder was given, otherwise an empty list.

    Errors:
        FileNotFoundError if the lookup file is missing.
    """
    import matplotlib.pyplot as plt

    lookup = read_lookup(lookup_folders)
    saved = []
    for room_folder in sorted(p for p in Path(models_folder).iterdir() if p.is_dir()):
        if room_ids is not None and room_folder.name not in room_ids:
            continue
        model_files = sorted((f for f in room_folder.glob("*.csv")
                              if f.stem.split("_", 1)[0].isdigit() and f.stem[5:] in PERIOD_NAMES),
                             key=lambda f: (f.stem[:4], PERIOD_NAMES.index(f.stem[5:])))
        if not model_files:
            continue
        columns = 3
        rows = -(-len(model_files) // columns)
        fig, axes = plt.subplots(rows, columns, figsize=(15, 2.8 * rows), squeeze=False, sharex=True)
        for ax in axes.ravel()[len(model_files):]:
            ax.axis("off")
        grid = np.arange(0, 24, 0.25)
        for ax, model_file in zip(axes.ravel(), model_files):
            model = pd.read_csv(model_file)
            for weekday in sorted(model["weekday"].unique()):
                heights = [evaluate_model(model, pd.Timestamp(2024, 1, 1 + int(weekday), int(h), int(h % 1 * 60))) for h in grid]
                ax.plot(grid, heights, linewidth=1, label=WEEKDAYS[int(weekday)][:3])
            ax.set_title(model_file.stem, fontsize=9)
            ax.set_xticks(range(0, 25, 6))
            ax.tick_params(labelsize=7)
            ax.grid(True, alpha=0.25)
        axes[0][0].legend(fontsize=6, ncol=4)
        fig.suptitle(f"{room_label(lookup, room_folder.name)} ({room_folder.name[:8]}): saved regression for each weekday "
                     f"(x: hour of day, y: headcount)", y=1.0)
        fig.tight_layout()
        if save_folder is None:
            plt.show()
        else:
            Path(save_folder).mkdir(parents=True, exist_ok=True)
            target = Path(save_folder) / f"saved_models_{room_folder.name[:8]}.png"
            fig.savefig(target, dpi=110)
            plt.close(fig)
            saved.append(target)
    return saved
