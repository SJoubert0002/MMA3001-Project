"""List the choices a user can pick from, using all lookup files combined.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

from ..preprocessing.read_lookup import read_lookup

def list_rooms(lookup_folders, available_ids=None):
    """List the choices a user can pick from, using all lookup files combined.

    Each room name is one choice. A room name with several floorspace IDs gives one
    choice per ID, e.g. "1.61 (ID ending 5c3a)". If available_ids is given, only choices
    whose ID is in it are listed (e.g. rooms found in new data, or rooms that already
    have a model).

    Input:
        lookup_folders: folders to search for lookup files (see read_lookup).
        available_ids: optional. The floorspace IDs to restrict the list to (see ids_in_folder).

    Output:
        A sorted list of choices, e.g. ["G.20", "G.25"].

    Errors:
        FileNotFoundError if no lookup file is found.
        ValueError if a lookup file's headings are wrong.
    """
    lookup = read_lookup(lookup_folders)
    if available_ids is not None:
        lookup = lookup[lookup["id"].isin(set(available_ids))]
    return sorted(set(lookup["entry"]))
