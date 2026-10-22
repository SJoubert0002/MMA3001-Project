"""Build the model of one period: one regression for each weekday, ready to be saved.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

import numpy as np
import pandas as pd
from .config import MODEL_HEADINGS, SVR_MIN_DATES
from .fit_svr import fit_svr
from .score_svr import score_svr
from .slot_means import slot_means

def make_model(times, headcounts):
    """Build the model of one period: one regression for each weekday, ready to be saved.

    The readings of each weekday are averaged into 15-minute slots for each date (see
    slot_means) and a regression of slot headcount against time of day is fitted (see
    fit_svr). Only what is needed to predict is kept: the regression's support vectors
    (their time of day, their weights and the intercept), plus the weekday's uncertainty: the
    number of dates it was trained on and its cross-validated mean absolute error (see score_svr),
    i.e. how far, in people, a 15-minute average typically is from the model on a date the model
    has not seen. A weekday with readings on fewer than SVR_MIN_DATES dates gets no model.

    Input:
        times: a column of reading times in Melbourne time.
        headcounts: a column of headcounts (numbers; blanks are ignored), same length.

    Output:
        A table with the columns weekday (0 = Monday ... 6 = Sunday), support_hour,
        dual_coef, intercept, dates and cv_mae (the last three the same for every row of a
        weekday), one row per support vector. It is empty if no weekday has enough dates.
    """
    parts = []
    for weekday in range(7):
        chosen = (times.dt.dayofweek == weekday).to_numpy()
        slots = slot_means(times[chosen], headcounts[chosen])
        if slots.date.nunique() < SVR_MIN_DATES:
            continue
        fitted = fit_svr(slots.hour, slots.headcount)
        hours, weights = fitted.support_vectors_.ravel(), fitted.dual_coef_.ravel()
        if len(hours) == 0:   # a flat weekday: only the intercept is needed
            hours, weights = np.array([0.0]), np.array([0.0])
        parts.append(pd.DataFrame({"weekday": weekday, "support_hour": hours, "dual_coef": weights,
                                   "intercept": float(fitted.intercept_[0]),
                                   "dates": slots.date.nunique(), "cv_mae": score_svr(slots)[0]}))
    if not parts:
        return pd.DataFrame(columns=MODEL_HEADINGS)
    return pd.concat(parts, ignore_index=True)[MODEL_HEADINGS]
