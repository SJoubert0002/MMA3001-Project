"""Read a saved model's headcount at an exact time.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

import numpy as np
import pandas as pd
from .config import MODEL_HEADINGS, SVR_LENGTH_HOURS

def evaluate_model(model, moment):
    """Read a saved model's headcount at an exact time.

    Evaluates the weekday's regression: the sum over its support vectors of weight times
    exp(-(time - support time)^2 / (2 * length^2)), plus the intercept, never below 0.
    Only the saved table is needed (not the raw data and not scikit-learn).

    Input:
        model: a table with the model headings (see make_model / MODEL_HEADINGS).
        moment: a time made by read_time.

    Output:
        The expected headcount (a number), or None if the model has no regression for
        that day of the week (too few dates, or no readings at all).

    Errors:
        ValueError if the headings are wrong or a value is not a number.
    """
    if list(model.columns) != MODEL_HEADINGS:
        raise ValueError(f"Model headings are {list(model.columns)}, expected {MODEL_HEADINGS}.")
    values = model.apply(pd.to_numeric, errors="coerce")
    if values.isna().any().any():
        raise ValueError("The model has a blank or non-numeric value.")
    rows = values[values["weekday"] == moment.dayofweek]
    if rows.empty:
        return None
    hour = moment.hour + moment.minute / 60 + moment.second / 3600
    kernel = np.exp(-(hour - rows["support_hour"].to_numpy()) ** 2 / (2 * SVR_LENGTH_HOURS ** 2))
    return float(max(rows["intercept"].iloc[0] + (rows["dual_coef"].to_numpy() * kernel).sum(), 0))
