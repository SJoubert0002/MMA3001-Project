"""Read a saved model's uncertainty for one day of the week.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

import pandas as pd
from .config import MODEL_HEADINGS


def model_error(model, weekday):
    """Read a saved model's uncertainty for one day of the week.

    The error is the cross-validated mean absolute error stored when the model was built (see
    make_model): on dates the model was not trained on, a 15-minute average headcount was typically
    this many people away from the model's value. It is an average over the day, so it is a guide
    to the model's typical error, not a guarantee for one time.

    Input:
        model: a table with the model headings (see MODEL_HEADINGS).
        weekday: 0 = Monday ... 6 = Sunday.

    Output:
        A pair (cv_mae, dates): the typical error in people and the number of dates the weekday's
        regression was trained on. None if the model has no regression for that weekday.

    Errors:
        ValueError if the headings are wrong or a value is not a number.
    """
    if list(model.columns) != MODEL_HEADINGS:
        raise ValueError(f"Model headings are {list(model.columns)}, expected {MODEL_HEADINGS}.")
    rows = model.apply(pd.to_numeric, errors="coerce")
    if rows.isna().any().any():
        raise ValueError("The model has a blank or non-numeric value.")
    rows = rows[rows["weekday"] == weekday]
    if rows.empty:
        return None
    return float(rows["cv_mae"].iloc[0]), int(rows["dates"].iloc[0])
