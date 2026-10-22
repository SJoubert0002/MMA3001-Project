"""Read every room lookup file and combine them into one table of room names and floorspace IDs.

Part of the preprocessing package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
import pandas as pd
from .config import LOOKUP_HEADINGS
from .check_headings import check_headings

def read_lookup(lookup_folders, report=False):
    """Read every room lookup file and combine them into one table of room names and floorspace IDs.

    Lookup files are the files whose name starts with "Sensor ID and Locations - OCC"
    in the given folders (this includes every lookup stored by store_lookup). Rows
    with a blank room name or floorspace ID are ignored. If several files mention the
    same room, the newest file (by its last-modified time) decides which ID(s) the room
    has, and the older files' entries for that room are ignored.

    Input:
        lookup_folders: folders to search for lookup files.
        report: if True, print a note for every room whose IDs were replaced by a newer file.

    Output:
        A table with the columns room, id, source (the file the entry came from) and
        entry (the name a user picks: the room name, or for a room with several
        floorspace IDs, e.g. "1.61 (ID ending 5c3a)", one entry per ID), one line per
        room and floorspace ID.

    Errors:
        FileNotFoundError if no lookup file is found.
        ValueError if any lookup file has the wrong headings.
    """
    files = sorted({p for folder in lookup_folders for p in Path(folder).glob("Sensor ID and Locations - OCC*.csv")},
                   key=lambda p: (p.stat().st_mtime_ns, p.name))
    if not files:
        raise FileNotFoundError("Room lookup file (Sensor ID and Locations - OCC...) not found.")
    newest = {}
    for path in files:
        check_headings(path, LOOKUP_HEADINGS)
        table = pd.read_csv(path, dtype=str, keep_default_na=False)
        table = pd.DataFrame({"room": table["Floor/Room"].str.strip(), "id": table["SpaceId"].str.strip()})
        table = table[(table["room"] != "") & (table["id"] != "")]
        for key, group in table.groupby(table["room"].str.casefold()):
            ids = sorted(set(group["id"]))
            if report and key in newest and newest[key]["ids"] != ids:
                print(f"NOTE: room {group['room'].iloc[0]!r}: {path.name} replaces the IDs from {newest[key]['source']}.")
            newest[key] = {"room": group["room"].iloc[0], "ids": ids, "source": path.name}
    rows = []
    for entry in newest.values():
        ids = entry["ids"]
        length = 4
        while len({i[-length:] for i in ids}) < len(ids) and length < min(len(i) for i in ids):
            length += 1
        for one_id in ids:
            # A room with several floorspace IDs gets one entry per ID, told apart by the end of the ID.
            name = entry["room"] if len(ids) == 1 else f"{entry['room']} (ID ending {one_id[-length:]})"
            rows.append({"room": entry["room"], "id": one_id, "source": entry["source"], "entry": name})
    return pd.DataFrame(rows, columns=["room", "id", "source", "entry"])
