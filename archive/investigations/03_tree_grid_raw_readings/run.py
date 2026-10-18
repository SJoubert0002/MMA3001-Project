"""Decision-tree grid on raw readings: min leaf x max depth, random 80/20 split of readings and a whole-day hold-out.
Output: results_random_split.csv, results_day_split.csv (in this folder)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor

sys.path.insert(0, str(Path(__file__).parents[1]))
from _common import ROOMS, load_notebook_functions

g = load_notebook_functions()
here = Path(__file__).parent
LEAVES, DEPTHS = [1, 5, 20, 50, 100, 200, 500, 1000, 2000], [4, 8, None]
random_rows, day_rows = [], []

for rid, room in ROOMS.items():
    data, times = g["read_room_data"](rid, g["OUTPUT_DIR"] / "occupancy_streams")
    h = pd.to_numeric(data["headcount"], errors="coerce")
    labels = g["label_periods"](times, g["calendar"])
    local = times.dt.tz_localize(None)
    hour = (local.dt.hour + local.dt.minute / 60 + local.dt.second / 3600).to_numpy()
    for year in sorted(times.dt.year.unique()):
        if year not in g["calendar"]:
            continue
        for period in g["PERIOD_NAMES"]:
            for wd in (0, 1, 2):
                m = ((labels == period) & (times.dt.year == year) & (times.dt.dayofweek == wd) & h.notna()).to_numpy()
                n = int(m.sum())
                if n < 50:
                    continue
                x, y, dates = hour[m].reshape(-1, 1), h.to_numpy()[m], local[m].dt.normalize().to_numpy()
                base = dict(room=room, year=year, period=period, weekday=["Mon", "Tue", "Wed"][wd], readings=n)
                idx = np.random.default_rng(0).permutation(n)
                splits = {"random": (idx[: int(n * 0.8)], idx[int(n * 0.8):])}
                unique_days = np.unique(dates)
                if len(unique_days) >= 5:
                    held = set(np.random.default_rng(1).choice(unique_days, max(1, len(unique_days) // 5), replace=False))
                    hm = np.array([d in held for d in dates])
                    splits["day"] = (np.where(~hm)[0], np.where(hm)[0])
                for name, (tr, te) in splits.items():
                    out = random_rows if name == "random" else day_rows
                    median_mae = float(np.abs(y[te] - np.median(y[tr])).mean())
                    for d in DEPTHS:
                        for leaf in LEAVES:
                            if leaf > len(tr) // 2:
                                continue
                            tree = DecisionTreeRegressor(min_samples_leaf=leaf, max_depth=d, random_state=0).fit(x[tr], y[tr])
                            out.append({**base, "max_depth": d or 0, "min_leaf": leaf,
                                        "mae": float(np.abs(tree.predict(x[te]) - y[te]).mean()), "median_baseline": median_mae})

pd.DataFrame(random_rows).round(4).to_csv(here / "results_random_split.csv", index=False)
pd.DataFrame(day_rows).round(4).to_csv(here / "results_day_split.csv", index=False)
for name, rows in [("random", random_rows), ("day", day_rows)]:
    print(name, "split: mean MAE by max_depth x min_leaf")
    print(pd.DataFrame(rows).groupby(["max_depth", "min_leaf"]).mae.mean().unstack(0).round(3))
