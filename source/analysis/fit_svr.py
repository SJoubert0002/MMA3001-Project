"""Fit the RBF support-vector regression of headcount against time of day.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

import numpy as np
from .config import SVR_C, SVR_EPSILON, SVR_LENGTH_HOURS

def fit_svr(hours, headcounts):
    """Fit the RBF support-vector regression of headcount against time of day.

    Input:
        hours: the slot start times in hours (numbers 0-24).
        headcounts: the slot mean headcounts, same length.

    Output:
        The fitted regression, which predicts a headcount for any hour (see predict_svr).
    """
    from sklearn.svm import SVR
    return SVR(kernel="rbf", C=SVR_C, gamma=1 / (2 * SVR_LENGTH_HOURS ** 2), epsilon=SVR_EPSILON).fit(
        np.asarray(hours, dtype=float).reshape(-1, 1), np.asarray(headcounts, dtype=float))
