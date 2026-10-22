"""Read a time typed as text, e.g. "2025-04-09 14:00", as Melbourne time.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

import pandas as pd
from .config import TIMEZONE, TIME_FORMAT

def read_time(text):
    """Read a time typed as text, e.g. "2025-04-09 14:00", as Melbourne time.

    Input:
        text: the time written exactly as YYYY-MM-DD HH:MM (24-hour clock).

    Output:
        The time, with the Melbourne time zone attached.

    Errors:
        ValueError if the text is not in that format, is not a real date and time, or
            falls in the hour that does not exist or happens twice when the clocks change.
    """
    try:
        moment = pd.to_datetime(str(text).strip(), format=TIME_FORMAT)
        if pd.isna(moment):
            raise ValueError("blank time")
        return moment.tz_localize(TIMEZONE, ambiguous="raise", nonexistent="raise")
    except Exception as error:
        raise ValueError(f"Time {text!r} is not valid. Write it as YYYY-MM-DD HH:MM, "
                         f"e.g. 2025-04-09 14:00, and make sure it is a real Melbourne time.") from error
