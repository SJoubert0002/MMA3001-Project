"""Turn a column of headcounts (text) into numbers, leaving blanks as "missing".

Part of the preprocessing package; see the function's docstring for its input, output and errors.
"""

import pandas as pd

def clean_headcount(headcounts):
    """Turn a column of headcounts (text) into numbers, leaving blanks as "missing".

    A blank (or the words nan / null / none) becomes a missing value, never zero.

    Input:
        headcounts: a column of headcounts as text.

    Output:
        The same column as numbers, with missing values left empty.

    Errors:
        ValueError if any entry is not a whole number of 0 or more.
    """
    text = headcounts.str.strip().str.casefold()
    is_blank = text.isin(["", "nan", "null", "none"])
    numbers = pd.to_numeric(text.mask(is_blank), errors="coerce")
    if (numbers.isna() & ~is_blank).any() or (numbers < 0).any() or ((numbers % 1) != 0).any():
        raise ValueError("Headcounts must be whole numbers of 0 or more (or blank).")
    return numbers
