"""Stop with an error if a file's column headings are not exactly as expected.

Part of the preprocessing package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
import pandas as pd

def check_headings(csv_file, expected_headings):
    """Stop with an error if a file's column headings are not exactly as expected.

    Only the heading row is read, so this is fast even for huge files.

    Input:
        csv_file: the file to check.
        expected_headings: the list of headings the file must have, in order.

    Output:
        Nothing if the headings match exactly.

    Errors:
        ValueError if any heading is missing, extra, renamed or in a different order.
    """
    found = list(pd.read_csv(csv_file, nrows=0).columns)
    if found != list(expected_headings):
        raise ValueError(f"{Path(csv_file).name} has the wrong column headings.\n"
                         f"  Expected: {list(expected_headings)}\n  Found:    {found}")
