"""Check and process a new occupancy file, and work out which rooms it contains.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

from ..preprocessing.drop_room_id import drop_room_id
from ..preprocessing.find_floorspace_ids import find_floorspace_ids
from ..preprocessing.ids_in_folder import ids_in_folder
from .list_rooms import list_rooms
from ..preprocessing.split_by_room import split_by_room

def load_new_data(new_data_file, scratch_folder, lookup_folders):
    """Check and process a new occupancy file, and work out which rooms it contains.

    The file goes through the same steps as the original data (exact headings, valid
    times and headcounts, one file per room, room ID dropped). The processed files are
    saved in a scratch folder. Room IDs in the file that are not in the lookup file
    (or have no data there) are reported and cannot be chosen.

    Input:
        new_data_file: a new occupancy CSV with exactly the raw headings.
        scratch_folder: an empty folder to hold the processed room files.
        lookup_folders: folders to search for the room lookup file.

    Output:
        A sorted list of the room names found in the new data.

    Errors:
        ValueError if the headings or data are wrong, or no room in the file can be named.
        FileNotFoundError if the lookup file is missing.
    """
    split_by_room(new_data_file, scratch_folder)
    drop_room_id(scratch_folder)
    found_ids = ids_in_folder(scratch_folder)
    rooms = list_rooms(lookup_folders, found_ids)
    named = {find_floorspace_ids([room], lookup_folders, found_ids)[room] for room in rooms}
    for unnamed in sorted(found_ids - named):
        print(f"CLARIFICATION NEEDED: floorspace ID {unnamed} is in the new data but no lookup gives it a single room name, "
              f"so it was skipped. Supply a lookup naming it to include it.")
    if not rooms:
        raise ValueError("None of the rooms in the new data can be matched to a room name.")
    return rooms
