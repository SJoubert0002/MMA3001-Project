"""Compare the selected model with its alternatives in the final three-period layout.

Every room, year, period and weekday of G.20 and G.25 with at least 3 dates is scored by the same date-grouped
cross-validation folds as the tool uses (see score_svr). Models compared: the selected RBF SVR, a shallow decision tree,
the slot-mean profile and a constant median (the baseline). For each, the mean absolute error, the time to fit and
predict, and the size of the stored model are recorded. The result is written to reports/model_comparison.txt.

Needs the preprocessed room files (run preprocessing on the raw export first).
Run from anywhere:  python examples/compare_models.py
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from source.analysis.config import PERIOD_NAMES, SVR_FOLDS, SVR_MIN_DATES
from source.analysis.fit_svr import fit_svr
from source.analysis.label_periods import label_periods
from source.analysis.predict_svr import predict_svr
from source.analysis.read_room_data import read_room_data
from source.analysis.read_semester_calendar import read_semester_calendar
from source.analysis.slot_means import slot_means
from source.preprocessing.config import DATA_DIR

STREAMS = DATA_DIR / "derived" / "preprocessed" / "occupancy_streams"
ROOMS = {"G.20": "cca1ac3e", "G.25": "227f1068"}  # room name: start of its floorspace ID
REPORT = Path(__file__).resolve().parents[1] / "reports" / "model_comparison.txt"


def fit_tree(hours, counts):
    """Fit the rival decision tree (depth 3, at least 20 slots per leaf, absolute-error criterion)."""
    from sklearn.tree import DecisionTreeRegressor
    return DecisionTreeRegressor(max_depth=3, min_samples_leaf=20, criterion="absolute_error", random_state=0).fit(
        hours.reshape(-1, 1), counts)


def slot_profile(hours, counts):
    """Return a predictor: the mean headcount of the training slots at each clock time."""
    table = pd.Series(counts).groupby(hours).mean()
    return lambda query: table.reindex(query).fillna(counts.mean()).to_numpy()


def score_subset(slots):
    """Score every model on one subset with the tool's folds.

    Input:
        slots: the table made by slot_means for one room, year, period and weekday.

    Output:
        A dictionary of mean absolute error, fit seconds and predict seconds per model (None if too few dates).
    """
    dates = slots.date.to_numpy()
    days = np.unique(dates)
    if len(days) < SVR_MIN_DATES:
        return None
    folds = min(SVR_FOLDS, len(days))
    fold_of = dict(zip(days[np.random.default_rng(1).permutation(len(days))], np.arange(len(days)) % folds))
    fold = np.array([fold_of[d] for d in dates])
    hours, counts = slots.hour.to_numpy(), slots.headcount.to_numpy()
    errors = {name: np.empty(len(slots)) for name in ["svr", "tree", "slot_mean", "median"]}
    seconds = {name: [0.0, 0.0] for name in errors}
    for f in range(folds):
        test = fold == f
        train_h, train_c, test_h = hours[~test], counts[~test], hours[test]

        start = time.perf_counter()
        model = fit_svr(train_h, train_c)
        seconds["svr"][0] += time.perf_counter() - start
        start = time.perf_counter()
        guess = predict_svr(model, test_h)
        seconds["svr"][1] += time.perf_counter() - start
        errors["svr"][test] = np.abs(guess - counts[test])

        start = time.perf_counter()
        tree = fit_tree(train_h, train_c)
        seconds["tree"][0] += time.perf_counter() - start
        start = time.perf_counter()
        guess = np.maximum(tree.predict(test_h.reshape(-1, 1)), 0)
        seconds["tree"][1] += time.perf_counter() - start
        errors["tree"][test] = np.abs(guess - counts[test])

        start = time.perf_counter()
        profile = slot_profile(train_h, train_c)
        seconds["slot_mean"][0] += time.perf_counter() - start
        start = time.perf_counter()
        guess = profile(test_h)
        seconds["slot_mean"][1] += time.perf_counter() - start
        errors["slot_mean"][test] = np.abs(guess - counts[test])

        errors["median"][test] = np.abs(np.median(train_c) - counts[test])
    result = {name: float(err.mean()) for name, err in errors.items()}
    result["fit_s"] = {name: seconds[name][0] / folds for name in seconds}
    result["predict_s"] = {name: seconds[name][1] / folds for name in seconds}
    return result


def main():
    """Score every subset and write reports/model_comparison.txt."""
    calendar = read_semester_calendar([DATA_DIR])
    names = ["svr", "tree", "slot_mean", "median"]
    rows, fit_s, predict_s = [], {n: [] for n in names}, {n: [] for n in names}
    sizes = {"svr": [], "tree": []}
    for room, prefix in ROOMS.items():
        floorspace_id = next(path.stem for path in STREAMS.glob("*.csv") if path.stem.startswith(prefix))
        data, times = read_room_data(floorspace_id, STREAMS)
        labels = label_periods(times, calendar)
        counts = pd.to_numeric(data["headcount"], errors="coerce")
        for year in sorted(times.dt.year.unique()):
            for period in PERIOD_NAMES:
                chosen = ((labels == period) & (times.dt.year == year) & counts.notna()).to_numpy()
                if not chosen.any():
                    continue
                for weekday in range(7):
                    pick = chosen & (times.dt.dayofweek == weekday).to_numpy()
                    slots = slot_means(times[pick], counts[pick])
                    scored = score_subset(slots)
                    if scored is None:
                        continue
                    rows.append({n: scored[n] for n in names})
                    for n in names:
                        fit_s[n].append(scored["fit_s"][n])
                        predict_s[n].append(scored["predict_s"][n])
                    svr = fit_svr(slots.hour, slots.headcount)
                    sizes["svr"].append(len(svr.support_))
                    sizes["tree"].append(fit_tree(slots.hour.to_numpy(), slots.headcount.to_numpy()).tree_.node_count)
    table = pd.DataFrame(rows)
    lines = [f"Subsets scored (room, year, period, weekday): {len(table)}", "",
             f"{'model':<10}{'MAE':>8}{'beats median in':>18}{'fit ms':>10}{'predict ms':>12}"]
    for n in names:
        beats = int((table[n] < table["median"]).sum()) if n != "median" else 0
        lines.append(f"{n:<10}{table[n].mean():>8.3f}{(str(beats) + ' of ' + str(len(table))) if n != 'median' else '-':>18}"
                     f"{1000 * np.mean(fit_s[n]):>10.2f}{1000 * np.mean(predict_s[n]):>12.3f}")
    lines += ["", f"SVR beats the tree in {int((table['svr'] < table['tree']).sum())} of {len(table)} subsets.",
              f"Mean stored size: SVR {np.mean(sizes['svr']):.0f} support vectors (2 numbers each), "
              f"tree {np.mean(sizes['tree']):.1f} nodes."]
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
