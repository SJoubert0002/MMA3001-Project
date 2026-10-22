"""Predicted headcount at the given hours (never below 0).

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

import numpy as np

def predict_svr(fitted, hours):
    """Predicted headcount at the given hours (never below 0)."""
    return np.maximum(fitted.predict(np.asarray(hours, dtype=float).reshape(-1, 1)), 0)
