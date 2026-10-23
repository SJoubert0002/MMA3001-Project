"""RBF SVR vs decision tree on 15-minute slot averages, tuned by whole-day cross-validation.

Input is time of day only (hours). Target is the 15-minute slot mean headcount. One regression per
(room, year, period, weekday) for Mon-Wed. Every setting is scored with 4-fold cross-validation grouped by
date (a date is never split between train and test), then averaged over all subsets so ONE global setting
can be chosen and shipped. Selection bias check: settings are chosen on 2024 subsets and scored on 2025-2026.
Output: results.csv (per subset and setting, in test/output/investigations/05_svr_vs_tree_tuning/), summary tables printed.
"""
import sys
import time
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

sys.path.insert(0, str(Path(__file__).parents[1]))
from _common import ROOMS, load_notebook_functions

here = Path(__file__).resolve().parents[3] / "test" / "output" / "investigations" / Path(__file__).parent.name; here.mkdir(parents=True, exist_ok=True)
FOLDS = 4
SVR_C = [0.1, 0.3, 1, 3]
SVR_LENGTH = [1.0, 2.0, 3.0, 4.0, 6.0]      # kernel length scale in hours; gamma = 1 / (2 * length^2)
SVR_EPS = [0.01, 0.03, 0.1, 0.2]
TREE_DEPTH = [2, 3, 4, 6]
TREE_LEAF = [5, 10, 20, 50, 100]
TREE_CRITERION = ["squared_error", "absolute_error"]


def folds_by_date(dates, seed=1):
    days = np.unique(dates)
    order = np.random.default_rng(seed).permutation(len(days))
    fold_of_day = dict(zip(days[order], np.arange(len(days)) % FOLDS))
    return np.array([fold_of_day[d] for d in dates])


def score_subset(key, x, y, dates):
    fold = folds_by_date(dates)
    rows = []

    def cv(make_prediction):
        errors = np.empty(len(y))
        for f in range(FOLDS):
            te = fold == f
            errors[te] = np.abs(make_prediction(x[~te], y[~te], x[te]) - y[te])
        return float(errors.mean())

    rows.append({**key, "model": "zero", "setting": "-", "mae": cv(lambda a, b, c: np.zeros(len(c)))})
    rows.append({**key, "model": "median", "setting": "-", "mae": cv(lambda a, b, c: np.full(len(c), np.median(b)))})

    def slot_mean(xa, ya, xc):
        profile = pd.Series(ya).groupby(xa[:, 0]).mean()
        return pd.Series(xc[:, 0]).map(profile).fillna(float(ya.mean())).to_numpy()
    rows.append({**key, "model": "slot_mean", "setting": "-", "mae": cv(slot_mean)})

    for c, length, eps in product(SVR_C, SVR_LENGTH, SVR_EPS):
        gamma = 1 / (2 * length ** 2)
        mae = cv(lambda a, b, d: SVR(kernel="rbf", C=c, gamma=gamma, epsilon=eps).fit(a, b).predict(d))
        rows.append({**key, "model": "svr", "setting": f"C={c} length={length}h eps={eps}", "mae": mae})
    for depth, leaf, crit in product(TREE_DEPTH, TREE_LEAF, TREE_CRITERION):
        mae = cv(lambda a, b, d: DecisionTreeRegressor(max_depth=depth, min_samples_leaf=leaf, criterion=crit,
                                                       random_state=0).fit(a, b).predict(d))
        rows.append({**key, "model": "tree", "setting": f"depth={depth} leaf={leaf} {crit}", "mae": mae})
    return rows


def main():
    g = load_notebook_functions()
    tasks = []
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
            if year not in g["calendar"] or s.date.nunique() < FOLDS or len(s) < 40:
                continue
            key = dict(room=room, year=year, period=period, weekday=["Mon", "Tue", "Wed"][wd], slots=len(s), days=s.date.nunique())
            tasks.append((key, s.hour.to_numpy().reshape(-1, 1), s["mean"].to_numpy(), s.date.to_numpy()))
    print(len(tasks), "subsets", flush=True)
    t0 = time.time()
    out = Parallel(n_jobs=20, verbose=5)(delayed(score_subset)(*t) for t in tasks)
    res = pd.DataFrame([r for rows in out for r in rows])
    res.round(4).to_csv(here / "results.csv", index=False)
    print("seconds", round(time.time() - t0))
    summarise(res)


def summarise(res):
    pd.set_option("display.width", 200)
    keys = ["room", "year", "period", "weekday"]
    mean = res.groupby(["model", "setting"]).mae.mean()
    print("\nBaselines:", mean.loc[["zero", "median", "slot_mean"]].droplevel(1).round(3).to_dict())
    for model in ("svr", "tree"):
        m = mean.loc[model].sort_values()
        print(f"\nBest 8 {model} settings (mean MAE over all subsets):\n", m.head(8).round(3).to_string())
    best = {model: mean.loc[model].idxmin() for model in ("svr", "tree")}
    print("\nGlobal best:", best)
    # Selection-bias check: choose on 2024, score on 2025-2026.
    print("\nChoose on 2024, test on 2025-2026:")
    for model in ("svr", "tree"):
        r = res[res.model == model]
        pick = r[r.year == 2024].groupby("setting").mae.mean().idxmin()
        test = r[(r.year > 2024) & (r.setting == pick)].set_index(keys).mae
        base = res[(res.model == "median") & (res.year > 2024)].set_index(keys).mae.reindex(test.index)
        print(f"  {model}: picked [{pick}] test MAE {test.mean():.3f} vs median {base.mean():.3f}; beats median in {(test < base).sum()}/{len(test)}")
    # Head to head at the global bests.
    s = res[(res.model == "svr") & (res.setting == best["svr"])].set_index(keys).mae
    t = res[(res.model == "tree") & (res.setting == best["tree"])].set_index(keys).mae
    md = res[res.model == "median"].set_index(keys).mae
    print(f"\nHead to head over {len(s)} subsets: svr {s.mean():.3f}, tree {t.mean():.3f}, median {md.mean():.3f}; "
          f"svr beats tree in {(s < t.reindex(s.index)).sum()}, svr beats median in {(s < md.reindex(s.index)).sum()}")
    by = pd.DataFrame({"svr": s, "tree": t, "median": md}).groupby(level="period").mean().round(3)
    print("\nBy period (mean MAE):\n", by.to_string())
    # Sensitivity of each SVR parameter (mean MAE, others free to their best).
    r = res[res.model == "svr"].copy()
    parts = r.setting.str.extract(r"C=(?P<C>\S+) length=(?P<length>\S+)h eps=(?P<eps>\S+)")
    r = pd.concat([r, parts], axis=1)
    for p in ("C", "length", "eps"):
        print(f"\nSVR sensitivity to {p} (best of the others):")
        print(r.groupby(["setting", p]).mae.mean().groupby(p).min().round(3).to_string())


if __name__ == "__main__":
    main()
