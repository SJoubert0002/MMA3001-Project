"""Write the answer to a query with its provenance and uncertainty.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

from .config import WEEKDAYS


def describe_answer(room_name, time_text, value, details):
    """Write the answer to a query with the model that gave it and how uncertain it is.

    Input:
        room_name: the room asked about.
        time_text: the time asked about, YYYY-MM-DD HH:MM.
        value: the expected headcount returned by get_headcount.
        details: the dictionary filled by get_headcount (model_file, year, period, weekday, dates, cv_mae).

    Output:
        A text of several lines: the answer with its typical error and likely range, then the model file,
        period, weekday and number of training dates behind it.

    Errors:
        None.
    """
    error = details["cv_mae"]
    low, high = max(value - error, 0.0), value + error
    lines = [f"Expected headcount in {room_name} at {time_text}: {value:.1f} people "
             f"(typically within {error:.1f} of the model; about {low:.1f} to {high:.1f})",
             f"  model:  {details['model_file']} ({details['year']} {details['period']}, "
             f"{WEEKDAYS[details['weekday']]} regression)",
             f"  basis:  {details['dates']} dates of that weekday in the period; the error is the model's "
             f"cross-validated mean absolute error on dates it was not trained on"]
    if details["dates"] < 6:
        lines.append(f"  caution: only {details['dates']} training dates, so both the value and its error are uncertain")
    return "\n".join(lines)
