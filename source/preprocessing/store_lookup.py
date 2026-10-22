"""Check a supplied room lookup file and keep a copy of it for future runs.

Part of the preprocessing package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
import pandas as pd
from .config import LOOKUP_HEADINGS
from .check_headings import check_headings

def store_lookup(lookup_file, lookups_folder):
    """Check a supplied room lookup file and keep a copy of it for future runs.

    The copy is saved in the lookups folder under a new name (with the date and time),
    so nothing already stored is overwritten. A file identical to one already stored is
    not copied again, but counts as the newest again.

    Input:
        lookup_file: a room lookup CSV with exactly the lookup headings.
        lookups_folder: where lookups are kept (created if needed).

    Output:
        The path of the stored copy.

    Errors:
        ValueError if the headings are wrong. FileNotFoundError if the file is missing.
    """
    check_headings(lookup_file, LOOKUP_HEADINGS)
    folder = Path(lookups_folder)
    folder.mkdir(parents=True, exist_ok=True)
    content = Path(lookup_file).read_bytes()
    for stored in folder.glob("*.csv"):
        if stored.read_bytes() == content:
            stored.touch()
            print(f"This lookup is already stored ({stored.name}); it now counts as the newest.")
            return stored
    stamp = pd.Timestamp.now().strftime("%Y%m%d-%H%M%S")
    target = folder / f"Sensor ID and Locations - OCC (stored {stamp} from {Path(lookup_file).stem}).csv"
    target.write_bytes(content)
    print(f"Stored the lookup as {target.name}")
    return target
