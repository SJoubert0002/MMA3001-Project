"""Read one room's preprocessed file and put the readings in time order.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
import pandas as pd
from .config import TIMEZONE
from ..preprocessing.config import FINAL_HEADINGS
from ..preprocessing.check_headings import check_headings

def read_room_data(floorspace_id, streams_folder):
    """Read one room's preprocessed file and put the readings in time order.

    The raw data has a few readings out of order, so they are sorted by time.

    Input:
        floorspace_id: the room's floorspace ID.
        streams_folder: the folder of room files made by the preprocessing.

    Output:
        Two things: the table of readings (headcount and collecteddate, as text) and a
        column of the same readings' times in Melbourne time.

    Errors:
        FileNotFoundError if the room's data file is missing.
        ValueError if the headings are wrong or a time is invalid.
    """
    room_file = Path(streams_folder) / f"{floorspace_id}.csv"
    if not room_file.is_file():
        raise FileNotFoundError(f"No occupancy data for floorspace {floorspace_id}.")
    check_headings(room_file, FINAL_HEADINGS)
    data = pd.read_csv(room_file, dtype=str, keep_default_na=False)
    times = pd.to_datetime(data["collecteddate"], errors="coerce", utc=True).dt.tz_convert(TIMEZONE)
    if times.isna().any():
        raise ValueError(f"{room_file.name} contains an invalid time.")
    order = times.argsort(kind="stable")
    return data.iloc[order].reset_index(drop=True), times.iloc[order].reset_index(drop=True)
