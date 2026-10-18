"""Score the adopted layout: one RBF SVR per room, year, period (semester_1, semester_2, non_teaching) and weekday.

Each weekday's 15-minute slot means are scored with 4-fold cross-validation that holds out whole dates, against a constant
median of the training slots. Settings are the fixed ones in the notebook (C 0.3, length 2 h, epsilon 0.1).
Output: results.csv (one row per room, year, period and weekday) and printed tables.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))
from _common import ROOMS, load_notebook_functions

here = Path(__file__).parent
nb = load_notebook_functions()
streams = nb["OUTPUT_DIR"] / "occupancy_streams"

rows = []
for room_id, room in ROOMS.items():
    data, times = nb["read_room_data"](room_id, streams)
    counts = pd.to_numeric(data["headcount"], errors="coerce")
    labels = nb["label_periods"](times, nb["calendar"])
    for year in sorted(times.dt.year.unique()):
        if year not in nb["calendar"]:
            continue
        for period in nb["PERIOD_NAMES"]:
            for weekday in range(7):
                chosen = ((labels == period) & (times.dt.year == year) & (times.dt.dayofweek == weekday) & counts.notna()).to_numpy()
                if not chosen.any():
                    continue
                slots = nb["slot_means"](times[chosen], counts[chosen])
                result = nb["score_svr"](slots)
                rows.append({"room": room, "year": year, "period": period, "weekday": nb["WEEKDAYS"][weekday][:3],
                             "dates": slots.date.nunique(), "svr_mae": result and result[0], "median_mae": result and result[1]})

results = pd.DataFrame(rows)
results.to_csv(here / "results.csv", index=False)
scored = results.dropna(subset=["svr_mae"])
print(f"{len(scored)} of {len(results)} subsets scored")
print(scored.groupby(["room", "period"])[["dates", "svr_mae", "median_mae"]].mean().round(3).to_string())
print(scored.groupby(["room", "year", "period"])[["svr_mae", "median_mae"]].mean().round(3).to_string())
print("Overall:", scored[["svr_mae", "median_mae"]].mean().round(3).to_dict(),
      "| SVR better in", int((scored.svr_mae < scored.median_mae).sum()), "of", len(scored))
