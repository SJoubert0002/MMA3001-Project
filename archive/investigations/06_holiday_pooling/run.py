"""How should the non-teaching periods be grouped before fitting the SVR?

Scheme A (minimum pooling): every period is its own model. Each weekday is fitted alone, except the two mid-semester breaks,
which hold one date per weekday per year, so their Monday-Friday are fitted together (the least pooling that can be fitted).
Scheme B (one holiday model): before semester 1, both mid-semester breaks, the mid-year break and after semester 2 of a year are
lumped into one 'holiday' group; each weekday (Mon-Sun) is fitted alone on all that year's holiday dates.

Both schemes predict exactly the same held-out dates (4 folds, whole dates held out, same seed), so the MAEs are directly
comparable. A constant median of the same training dates as scheme B is the baseline. SVR settings are the fixed ones from
investigation 05. Output: results.csv (one row per held-out slot, in test/output/investigations/06_holiday_pooling/) and printed tables.
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
BREAKS = ["mid_semester_break_1", "mid_semester_break_2"]
FOLDS, MIN_TRAIN_DATES = 4, 2


def group_a(period, weekday):
    return (period, "Mon-Fri" if period in BREAKS and weekday < 5 else weekday)


def fit_predict(train, test):
    model = nb["fit_svr"](train.hour, train.headcount)
    return nb["predict_svr"](model, test.hour)


rows = []
for room_id, room in ROOMS.items():
    data, times = nb["read_room_data"](room_id, streams)
    counts = pd.to_numeric(data["headcount"], errors="coerce")
    labels = nb["label_periods"](times, calendar)
    keep = (labels.isin(HOLIDAY) & counts.notna()).to_numpy()
    slots = nb["slot_means"](times[keep], counts[keep])
    day_info = pd.DataFrame({"date": times[keep].dt.tz_localize(None).dt.normalize().to_numpy(),
                             "period": labels[keep].to_numpy()}).drop_duplicates("date")
    slots = slots.merge(day_info, on="date")
    slots["year"] = slots.date.dt.year
    slots["weekday"] = slots.date.dt.dayofweek
    for year, ydata in slots.groupby("year"):
        days = np.sort(ydata.date.unique())
        fold_of = dict(zip(days[np.random.default_rng(1).permutation(len(days))], np.arange(len(days)) % FOLDS))
        ydata = ydata.assign(fold=ydata.date.map(fold_of))
        ydata["ga"] = [group_a(p, w) for p, w in zip(ydata.period, ydata.weekday)]
        for f in range(FOLDS):
            test_all, train_all = ydata[ydata.fold == f], ydata[ydata.fold != f]
            for (period, weekday), test in test_all.groupby(["period", "weekday"]):
                train_a = train_all[train_all.ga == group_a(period, weekday)]
                train_b = train_all[train_all.weekday == weekday]
                train_c = train_all[(train_all.period == period) & (train_all.weekday == weekday)]
                if train_a.date.nunique() < MIN_TRAIN_DATES or train_b.date.nunique() < MIN_TRAIN_DATES:
                    continue
                truth = test.headcount.to_numpy()
                err_a = np.abs(fit_predict(train_a, test) - truth)
                err_b = np.abs(fit_predict(train_b, test) - truth)
                err_c = (np.abs(fit_predict(train_c, test) - truth) if train_c.date.nunique() >= MIN_TRAIN_DATES
                         else np.full(len(test), np.nan))
                err_m = np.abs(np.median(train_b.headcount) - truth)
                rows += [(room, year, period, weekday, f, a, b, c, m) for a, b, c, m in zip(err_a, err_b, err_c, err_m)]

results = pd.DataFrame(rows, columns=["room", "year", "period", "weekday", "fold", "mae_a_min_pool", "mae_b_holiday",
                                      "mae_c_no_pool", "mae_median"])
results.to_csv(here / "results.csv", index=False)

cols = ["mae_a_min_pool", "mae_b_holiday", "mae_c_no_pool", "mae_median"]
print(f"{len(results)} held-out slots scored by A and B; {results.mae_c_no_pool.notna().sum()} also scorable with no pooling (C)\n")
common = results.dropna(subset=["mae_c_no_pool"])
print("Share of each period's slots that no pooling can score:")
print(results.groupby("period").mae_c_no_pool.apply(lambda s: s.notna().mean()).reindex(HOLIDAY).round(3).to_string())
print("\nBy period, on the slots all schemes can score (mean absolute error, people):")
print(common.groupby("period")[cols].mean().reindex(HOLIDAY).round(3).assign(slots=common.groupby("period").size()).to_string())
print("\nBy room and period, same slots:")
print(common.groupby(["room", "period"])[cols].mean().round(3).to_string())
print("\nBy weekday type, same slots:")
print(common.assign(kind=np.where(common.weekday < 5, "Mon-Fri", "Sat-Sun")).groupby("kind")[cols].mean().round(3).to_string())
print("\nOverall, same slots:", common[cols].mean().round(3).to_dict())
print("Overall, all slots (A, B, median):", results[["mae_a_min_pool", "mae_b_holiday", "mae_median"]].mean().round(3).to_dict())
