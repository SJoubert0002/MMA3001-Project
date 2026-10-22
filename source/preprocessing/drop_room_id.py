"""Remove the room ID column from every room file, leaving only headcount and time.

Part of the preprocessing package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
import pandas as pd
from .config import FINAL_HEADINGS, KEPT_HEADINGS, ROWS_PER_PIECE
from .check_headings import check_headings

def drop_room_id(room_folder):
    """Remove the room ID column from every room file, leaving only headcount and time.

    This is the very last step. Each file's name is still the room ID, so no
    information about which room it belongs to is lost. "rows_per_room.csv" is left alone.

    Input:
        room_folder: the folder of room files made by split_by_room.

    Output:
        Nothing. The files are rewritten in place.

    Errors:
        ValueError if a room file does not have the expected headings.
    """
    for room_file in Path(room_folder).glob("*.csv"):
        if room_file.name == "rows_per_room.csv":
            continue
        check_headings(room_file, KEPT_HEADINGS)
        temporary = room_file.with_suffix(".tmp")
        for number, piece in enumerate(pd.read_csv(room_file, usecols=FINAL_HEADINGS, dtype=str,
                                                   keep_default_na=False, chunksize=ROWS_PER_PIECE)):
            piece[FINAL_HEADINGS].to_csv(temporary, mode="a" if number else "w", header=not number, index=False)
        temporary.replace(room_file)
