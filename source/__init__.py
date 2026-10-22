"""Source code of the headcount estimator.

Packages:
    source.preprocessing: checks and cleans the raw occupancy and lookup files.
    source.analysis: builds, saves, scores and queries the per-period regression models, and the optional plots.

Every function is in its own module of the same name, so import it explicitly, e.g.
`from source.analysis.get_headcount import get_headcount`. Use the root master.py to run everything.
"""
