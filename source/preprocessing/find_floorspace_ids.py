"""Turn room names (e.g. "G.20") into the floorspace IDs used in the occupancy data.

Part of the preprocessing package; see the function's docstring for its input, output and errors.
"""

from .read_lookup import read_lookup

def find_floorspace_ids(room_names, lookup_folders, available_ids):
    """Turn room names (e.g. "G.20") into the floorspace IDs used in the occupancy data.

    Each name is matched against the room names of all lookup files combined (see
    read_lookup; the newest file wins if they disagree). Capital letters and spaces
    around a name do not matter. A room is "covered" if it has a floorspace ID in the
    lookup AND that ID is in the list of available IDs (rooms that have data or a
    saved model). Rooms that are not covered are reported in a message and skipped, so
    the analysis can carry on with the rooms that are covered.

    Input:
        room_names: the rooms the user is interested in, e.g. ["G.20", "G.25"].
        lookup_folders: folders to search for lookup files.
        available_ids: the floorspace IDs that have data or models (see ids_in_folder).

    Output:
        A dictionary of {room name: floorspace ID} for the covered rooms only.

    Errors:
        FileNotFoundError if no lookup file is found.
        ValueError if a lookup's headings are wrong, a room name has several floorspace
            IDs (the error lists the choices, e.g. "1.61 (ID ending 5c3a)"), or none of
            the requested rooms are covered.
    """
    lookup = read_lookup(lookup_folders)
    lookup_names = lookup["entry"].str.casefold()

    covered = {}
    for room in room_names:
        ids = sorted(set(lookup.loc[lookup_names == room.strip().casefold(), "id"]))
        if not ids:
            options = sorted(set(lookup.loc[lookup["room"].str.casefold() == room.strip().casefold(), "entry"]))
            if options:
                raise ValueError(f"Room {room!r} has several floorspace IDs. Choose one of: {options}")
        if not ids:
            print(f"REJECTED: {room!r} has no matching data (no floorspace ID for it in the lookup files).")
        elif ids[0] not in set(available_ids):
            print(f"REJECTED: {room!r} has no matching data (its floorspace ID {ids[0]} has no readings or model).")
        else:
            covered[room] = ids[0]
    if not covered:
        raise ValueError("No matching data: none of the requested rooms have a floorspace ID with data, so there is nothing to analyse.")
    return covered
