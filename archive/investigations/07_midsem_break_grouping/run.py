"""Where should a mid-semester break be modelled: with its semester, or with the other holiday periods?

For each break (mid_semester_break_1 / _2) the break's dates are held out and predicted by an SVR (fixed settings from
investigation 05, one weekday at a time) trained on:
  S, with the semester: that semester's other dates (semester_1 + break 1, or semester_2 + break 2) of the same year.
  H, with the holidays: that year's before semester 1, mid-year break, after semester 2 and both breaks.
  A, break only: the same break's other weekdays, Monday-Friday fitted together (minimum pooling, from investigation 06).
Folds are whole dates (4 folds, the same split for every scheme, drawn over all dates of the year used by S and H), so all
schemes predict exactly the same held-out break slots. Baseline: the constant median of S's training dates.
Output: results.csv (one row per held-out slot, in test/output/investigations/07_midsem_break_grouping/) and printed tables.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))
from _common import ROOMS, load_notebook_functions

here = Path(__file__).resolve().parents[3] / "test" / "output" / "investigations" / Path(__file__).parent.name; here.mkdir(parents=True, exist_ok=True)
nb = load_notebook_functions()
nb["np"], nb["pd"] = np, pd
calendar = nb["calendar"]
streams = nb["OUTPUT_DIR"] / "occupancy_streams"
HOLIDAY = ["before_semester_1", "mid_semester_break_1", "mid_year_break", "mid_semester_break_2", "after_semester_2"]
SEMESTER_OF = {"mid_semester_break_1": ["semester_1", "mid_semester_break_1"],
               "mid_semester_break_2": ["semester_2", "mid_semester_break_2"]}
FOLDS, MIN_TRAIN_DATES = 4, 2


def fit_predict(train, test):
    return nb["predict_svr"](nb["fit_svr"](train.hour, train.headcount), test.hour)


rows = []
for room_id, room in ROOMS.items():
    data, times = nb["read_room_data"](room_id, streams)
    counts = pd.to_numeric(data["headcount"], errors="coerce")
    labels = nb["label_periods"](times, calendar)
    used = sorted(set(HOLIDAY) | {"semester_1", "semester_2"})
    keep = (labels.isin(used) & counts.notna()).to_numpy()
    slots = nb["slot_means"](times[keep], counts[keep])
    day_info = pd.DataFrame({"date": times[keep].dt.tz_localize(None).dt.normalize().to_numpy(),
                             "period": labels[keep].to_numpy()}).drop_duplicates("date")
    slots = slots.merge(day_info, on="date")
    slots["year"], slots["weekday"] = slots.date.dt.year, slots.date.dt.dayofweek
    for year, ydata in slots.groupby("year"):
        days = np.sort(ydata.date.unique())
        fold_of = dict(zip(days[np.random.default_rng(1).permutation(len(days))], np.arange(len(days)) % FOLDS))
        ydata = ydata.assign(fold=ydata.date.map(fold_of))
        for f in range(FOLDS):
            train_all = ydata[ydata.fold != f]
            for brk, semester_periods in SEMESTER_OF.items():
                for weekday, test in ydata[(ydata.fold == f) & (ydata.period == brk)].groupby("weekday"):
                    train_s = train_all[train_all.period.isin(semester_periods) & (train_all.weekday == weekday)]
                    train_h = train_all[train_all.period.isin(HOLIDAY) & (train_all.weekday == weekday)]
                    train_a = train_all[(train_all.period == brk) & (train_all.weekday < 5)]
                    if min(train_s.date.nunique(), train_h.date.nunique(), train_a.date.nunique()) < MIN_TRAIN_DATES:
                        continue
                    truth = test.headcount.to_numpy()
                    err = [np.abs(fit_predict(t, test) - truth) for t in (train_s, train_h, train_a)]
                    err_m = np.abs(np.median(train_s.headcount) - truth)
                    rows += [(room, year, brk, weekday, f, *vals) for vals in zip(*err, err_m)]

results = pd.DataFrame(rows, columns=["room", "year", "period", "weekday", "fold", "mae_S_with_semester", "mae_H_with_holidays",
                                      "mae_A_break_only", "mae_median"])
results.to_csv(here / "results.csv", index=False)
cols = ["mae_S_with_semester", "mae_H_with_holidays", "mae_A_break_only", "mae_median"]
print(f"{len(results)} held-out break slots scored by every scheme (mean absolute error, people)\n")
print("By break:")
print(results.groupby("period")[cols].mean().round(3).assign(slots=results.groupby("period").size()).to_string())
print("\nBy room and break:")
print(results.groupby(["room", "period"])[cols].mean().round(3).to_string())
print("\nBy year and break:")
print(results.groupby(["year", "period"])[cols].mean().round(3).assign(slots=results.groupby(["year", "period"]).size()).to_string())
print("\nBy weekday:")
print(results.groupby("weekday")[cols].mean().round(3).to_string())
print("\nOverall:", results[cols].mean().round(3).to_dict())
for a, b in (("mae_S_with_semester", "mae_H_with_holidays"), ("mae_S_with_semester", "mae_A_break_only")):
    d = (results[a] - results[b]).groupby([results.room, results.year, results.period, results.weekday]).mean()
    print(f"{a} better than {b} in {(d < 0).sum()} of {len(d)} room/year/break/weekday cells")
