"""Decision-tree grid on 15-minute slot averages (one value per date and slot), against zero / median / slot-mean baselines.
Splits: random 80/20 of slots, and whole held-out days. Output: results.csv (in this folder)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor

sys.path.insert(0, str(Path(__file__).parents[1]))
from _common import ROOMS, load_notebook_functions

g = load_notebook_functions()
here = Path(__file__).parent
LEAVES, DEPTHS = [1, 3, 5, 10, 20, 50, 100], [3, 5, 8, 0]
rows = []

for rid, room in ROOMS.items():
    data, times = g["read_room_data"](rid, g["OUTPUT_DIR"] / "occupancy_streams")
    h = pd.to_numeric(data["headcount"], errors="coerce")
    local = times.dt.tz_localize(None)
    df = pd.DataFrame({"t": local.to_numpy(), "h": h.to_numpy(), "lab": g["label_periods"](times, g["calendar"]).to_numpy(),
                       "year": times.dt.year.to_numpy()}).dropna(subset=["h"])
    df["slot"], df["wd"], df["date"] = df.t.dt.floor("15min"), df.t.dt.dayofweek, df.t.dt.normalize()
    slots = df[df.wd <= 2].groupby(["year", "lab", "wd", "date", "slot"], sort=False).h.mean().rename("mean").reset_index()
    slots["hour"] = slots.slot.dt.hour + slots.slot.dt.minute / 60
    for (year, period, wd), s in slots.groupby(["year", "lab", "wd"]):
        if year not in g["calendar"] or len(s) < 40:
            continue
        x, y, dates, n = s.hour.to_numpy().reshape(-1, 1), s["mean"].to_numpy(), s.date.to_numpy(), len(s)
        unique_days = np.unique(dates)
        idx = np.random.default_rng(0).permutation(n)
        splits = {"random": (idx[: int(n * 0.8)], idx[int(n * 0.8):])}
        if len(unique_days) >= 5:
            held = set(np.random.default_rng(1).choice(unique_days, max(1, len(unique_days) // 5), replace=False))
            hm = np.array([d in held for d in dates])
            splits["day"] = (np.where(~hm)[0], np.where(hm)[0])
        for split, (tr, te) in splits.items():
            base = dict(room=room, year=year, period=period, weekday=["Mon", "Tue", "Wed"][wd], split=split, slots=n, days=len(unique_days))
            profile = pd.Series(y[tr]).groupby(x[tr, 0]).mean()
            slot_mean = pd.Series(x[te, 0]).map(profile).fillna(float(np.mean(y[tr]))).to_numpy()
            rows += [{**base, "model": "zero", "max_depth": 0, "min_leaf": 0, "mae": float(np.abs(y[te]).mean())},
                     {**base, "model": "median", "max_depth": 0, "min_leaf": 0, "mae": float(np.abs(y[te] - np.median(y[tr])).mean())},
                     {**base, "model": "slot_mean", "max_depth": 0, "min_leaf": 0, "mae": float(np.abs(slot_mean - y[te]).mean())}]
            for d in DEPTHS:
                for leaf in LEAVES:
                    if leaf > len(tr) // 2:
                        continue
                    tree = DecisionTreeRegressor(min_samples_leaf=leaf, max_depth=d or None, random_state=0).fit(x[tr], y[tr])
                    rows.append({**base, "model": "tree", "max_depth": d, "min_leaf": leaf, "mae": float(np.abs(tree.predict(x[te]) - y[te]).mean())})

res = pd.DataFrame(rows)
res.round(4).to_csv(here / "results.csv", index=False)
for split in ("random", "day"):
    q = res[res.split == split]
    print(f"{split} split, mean MAE")
    print(q[q.model == "tree"].groupby(["max_depth", "min_leaf"]).mae.mean().unstack(0).round(3))
    print(q[q.model != "tree"].groupby("model").mae.mean().round(3).to_dict())
