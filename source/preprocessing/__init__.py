"""Preprocessing: check and clean the raw occupancy data and room lookup files.

Run it with `run_preprocessing`; the other modules are its steps (check_headings,
clean_headcount, split_by_room, drop_room_id) and the lookup helpers (read_lookup, store_lookup,
ids_in_folder, find_floorspace_ids, find_unnamed_ids). All paths and headings are in `config`.
"""
