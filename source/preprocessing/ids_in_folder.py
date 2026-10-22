"""List the floorspace IDs that have a file (preprocessing) or a sub-folder (models) in a folder.

Part of the preprocessing package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path

def ids_in_folder(folder):
    """List the floorspace IDs that have a file (preprocessing) or a sub-folder (models) in a folder.

    Input:
        folder: a folder of room files (e.g. occupancy_streams) or of model folders.

    Output:
        A set of floorspace IDs. Empty if the folder does not exist. "rows_per_room.csv"
        is not a room and is ignored.
    """
    folder = Path(folder)
    if not folder.is_dir():
        return set()
    return {p.stem if p.is_file() else p.name for p in folder.iterdir()
            if p.name != "rows_per_room.csv" and (p.is_dir() or p.suffix == ".csv")}
