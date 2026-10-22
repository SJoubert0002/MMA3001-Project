"""Name a room for a plot or table.

Part of the analysis package.
"""


def room_label(lookup, room_id):
    """Give a floorspace ID a readable label.

    Input:
        lookup: the table made by read_lookup.
        room_id: a floorspace ID.

    Output:
        The room's name from the lookup (several names are joined with " / "), or the first
        8 characters of the ID if no lookup names it.
    """
    names = sorted(set(lookup.loc[lookup["id"] == room_id, "entry"]))
    return " / ".join(names) or room_id[:8]
