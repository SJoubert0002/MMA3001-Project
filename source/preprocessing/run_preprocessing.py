"""Run the whole preprocessing of the raw occupancy data.

Part of the preprocessing package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
import pandas as pd
from .config import OUTPUT_DIR, FINAL_HEADINGS
from .split_by_room import split_by_room
from .drop_room_id import drop_room_id


def run_preprocessing(raw_file, output_folder=OUTPUT_DIR, force=False):
    """Preprocess one raw occupancy file into one small file per room.

    The file is chosen by the caller (never searched for). It is checked (exact headings, valid
    times and headcounts), split into one CSV per room, and the room ID column is removed (the file
    name carries the room). If the room files were already made from that same file and have not been
    changed since, the work is skipped (the room files are still checked), so repeating the step is
    cheap. Use force to redo it.

    Input:
        raw_file: the raw occupancy CSV to process.
        output_folder: the folder to hold the preprocessed files; the room files go in its
            "occupancy_streams" sub-folder (default: derived/preprocessed).
        force: True to redo the preprocessing even if it looks up to date.

    Output:
        A pair (summary, redone). summary is a table of room IDs and their number of rows;
        redone is True if the raw file was processed now and False if it was already up to date.

    Errors:
        FileNotFoundError if the file does not exist.
        ValueError if the occupancy file has the wrong headings or invalid values.
    """
    raw_file = Path(raw_file)
    if not raw_file.is_file():
        raise FileNotFoundError(f"Occupancy file not found: {raw_file}")
    streams = Path(output_folder) / "occupancy_streams"
    summary_file = streams / "rows_per_room.csv"
    if not force and summary_file.is_file() and summary_file.stat().st_mtime_ns >= raw_file.stat().st_mtime_ns:
        room_files = [p for p in streams.glob("*.csv") if p.name != "rows_per_room.csv"]
        # Up to date only if every room file has already lost its room ID column.
        if room_files and all(list(pd.read_csv(p, nrows=0).columns) == FINAL_HEADINGS for p in room_files):
            return pd.read_csv(summary_file), False
    summary = split_by_room(raw_file, streams)
    drop_room_id(streams)
    return summary, True
