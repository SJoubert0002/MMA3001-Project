"""Check the occupancy file and split it into one CSV file per room.

Part of the preprocessing package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
import pandas as pd
from .config import KEPT_HEADINGS, RAW_HEADINGS, ROWS_PER_PIECE
from .check_headings import check_headings
from .clean_headcount import clean_headcount

def split_by_room(occupancy_file, output_folder):
    """Check the occupancy file and split it into one CSV file per room.

    Every row is kept (nothing is deleted). The unused "id" column is dropped straight
    away; the room ID is kept for now and removed later by drop_room_id. Old room
    files already in the output folder are replaced.

    Checks made on every row: the room ID is not blank, the collection date is a
    real date, and the headcount is valid (see clean_headcount).

    Input:
        occupancy_file: the raw occupancy CSV (must have exactly RAW_HEADINGS).
        output_folder: where the room files are saved (created if needed).

    Output:
        A table with one line per room and its number of rows, which is also saved
        as "rows_per_room.csv" in the output folder.

    Errors:
        ValueError if the headings are wrong, a check fails, or the file is empty.
    """
    check_headings(occupancy_file, RAW_HEADINGS)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    for old_file in output_folder.glob("*.csv"):
        old_file.unlink()

    rows_per_room = {}
    for piece in pd.read_csv(occupancy_file, usecols=KEPT_HEADINGS, dtype=str,
                             keep_default_na=False, chunksize=ROWS_PER_PIECE):
        if (piece["floorspaceid"].str.strip() == "").any():
            raise ValueError("Found a row with no room ID.")
        if pd.to_datetime(piece["collecteddate"], errors="coerce", utc=True).isna().any():
            raise ValueError("Found a row with an invalid collection date.")
        piece["headcount"] = clean_headcount(piece["headcount"])
        for room, rows in piece[KEPT_HEADINGS].groupby("floorspaceid"):
            room_file = output_folder / f"{room}.csv"
            rows.to_csv(room_file, mode="a", header=not room_file.exists(), index=False)
            rows_per_room[room] = rows_per_room.get(room, 0) + len(rows)

    if not rows_per_room:
        raise ValueError("The occupancy file contains no data rows.")
    summary = pd.DataFrame({"room_id": list(rows_per_room), "rows": list(rows_per_room.values())})
    summary.to_csv(output_folder / "rows_per_room.csv", index=False)
    return summary
