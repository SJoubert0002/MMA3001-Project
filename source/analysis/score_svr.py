"""Score the regression on dates it has not seen, against a constant-median baseline.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

import numpy as np
from .config import SVR_FOLDS, SVR_MIN_DATES
from .fit_svr import fit_svr
from .predict_svr import predict_svr

def score_svr(slots):
    """Score the regression on dates it has not seen, against a constant-median baseline.

    The dates are shared out at random (fixed seed) between folds; each fold's dates are predicted by a regression trained on
    the other folds, so no date is both trained and tested on.

    Input:
        slots: the table made by slot_means (one room, year, period and weekday).

    Output:
        A pair (svr_mae, median_mae): the mean absolute error of the regression and of predicting the training median.
        None if there are fewer than SVR_MIN_DATES dates.
    """
    dates = slots.date.to_numpy()
    days = np.unique(dates)
    if len(days) < SVR_MIN_DATES:
        return None
    folds = min(SVR_FOLDS, len(days))
    fold_of = dict(zip(days[np.random.default_rng(1).permutation(len(days))], np.arange(len(days)) % folds))
    fold = np.array([fold_of[d] for d in dates])
    hours, counts = slots.hour.to_numpy(), slots.headcount.to_numpy()
    svr_error, median_error = np.empty(len(slots)), np.empty(len(slots))
    for f in range(folds):
        test = fold == f
        svr_error[test] = np.abs(predict_svr(fit_svr(hours[~test], counts[~test]), hours[test]) - counts[test])
        median_error[test] = np.abs(np.median(counts[~test]) - counts[test])
    return float(svr_error.mean()), float(median_error.mean())
