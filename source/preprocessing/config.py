"""Folders and the exact column headings used by the preprocessing.

Every path is built from ROOT (the repository's main folder), so the code works from any working directory."""
from pathlib import Path

# The repository's main folder (this file is source/preprocessing/config.py).
ROOT = Path(__file__).resolve().parents[2]

# Folders and the exact column headings we expect.

DATA_DIR = ROOT / "data"
OUTPUT_DIR = DATA_DIR / "derived" / "preprocessed"

# Room lookups supplied by the user are kept here, and every lookup in these folders is used.
LOOKUPS_DIR = DATA_DIR / "lookups"
LOOKUP_FOLDERS = [DATA_DIR, LOOKUPS_DIR]

# The live environment for trying your own examples: input from here is returned here (see choose_output).
TEST_DIR = ROOT / "test"

# Files are read in pieces of this many rows so the computer's memory is never overloaded.
ROWS_PER_PIECE = 50_000

# The exact headings (and order) of a raw occupancy file.
RAW_HEADINGS = ["id", "deviceid", "floorspaceid", "occupancystatus", "headcount",
                "collecteddate", "occupancystatuschangedate", "previousoccupancystatus"]

# The exact headings of the room lookup file.
LOOKUP_HEADINGS = ["Building", "Floor/Room", "Area", "ID", "Note", "FloorId", "SpaceId"]

# The columns we read from the raw file. The row "id" is never used, so it is not even read.
KEPT_HEADINGS = ["floorspaceid", "headcount", "collecteddate"]

# The final columns of each room's file. The room ID is only needed to split the rooms apart.
FINAL_HEADINGS = ["headcount", "collecteddate"]
