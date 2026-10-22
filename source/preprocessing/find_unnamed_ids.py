"""List floorspace IDs that have data or models but no room name in any lookup.

Part of the preprocessing package; see the function's docstring for its input, output and errors.
"""

from .read_lookup import read_lookup

def find_unnamed_ids(lookup_folders, available_ids):
    """List floorspace IDs that have data or models but no room name in any lookup.

    Their models are kept, and they become usable as soon as a lookup names them.

    Input:
        lookup_folders: folders to search for lookup files.
        available_ids: the floorspace IDs that have data or models (see ids_in_folder).

    Output:
        A sorted list of floorspace IDs.
    """
    return sorted(set(available_ids) - set(read_lookup(lookup_folders)["id"]))
