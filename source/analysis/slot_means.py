"""Average each date's readings into 15-minute slots.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

import pandas as pd
from .config import SLOT_MINUTES

def slot_means(times, headcounts):
    """Average each date's readings into 15-minute slots.

    Input:
        times: a column of reading times in Melbourne time.
        headcounts: a column of headcounts (numbers; blanks are ignored), same length.

    Output:
        A table with one row per date and slot: date, hour (start of the slot, e.g. 14.25 = 14:15) and headcount (mean of the
        readings in the slot).
    """
    local = times.dt.tz_localize(None)
    table = pd.DataFrame({"slot": local.dt.floor(f"{SLOT_MINUTES}min").to_numpy(), "headcount": headcounts.to_numpy()}).dropna()
    table = table.groupby("slot", as_index=False).headcount.mean()
    table["date"] = table.slot.dt.normalize()
    table["hour"] = table.slot.dt.hour + table.slot.dt.minute / 60
    return table[["date", "hour", "headcount"]]
