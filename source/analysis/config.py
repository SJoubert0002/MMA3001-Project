"""Fixed settings of the analysis: periods, model headings and the regression's settings."""
from ..preprocessing.config import DATA_DIR

# Analysis setup.
TIMEZONE = "Australia/Melbourne"
MODELS_DIR = DATA_DIR / "models"

# The exact headings of the semester calendar file. The break dates are the mid-semester break.
CALENDAR_HEADINGS = ["year", "semester", "start_date", "end_date", "break_start", "break_end"]

# The three periods of a year: the two semesters' teaching weeks and everything else.
PERIOD_NAMES = ["semester_1", "semester_2", "non_teaching"]

# The exact headings of a saved model file. A model holds, for each weekday, the support vectors of one RBF regression.
MODEL_HEADINGS = ["weekday", "support_hour", "dual_coef", "intercept", "dates", "cv_mae"]
SLOT_MINUTES = 15
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Fixed regression settings (no user input needed).
SVR_C = 0.3               # penalty for errors outside the epsilon band (headcount units)
SVR_LENGTH_HOURS = 2.0    # kernel length scale: readings further apart than this have little influence on each other
SVR_EPSILON = 0.1         # errors smaller than this (in people) are ignored
SVR_MIN_DATES = 3         # fewest dates a weekday needs to be modelled or scored
SVR_FOLDS = 4             # cross-validation folds when scoring (reduced to the number of dates if fewer)

# How a time must be written when asking for a headcount.
TIME_FORMAT = "%Y-%m-%d %H:%M"

# Defaults of the optional plots: the raw-readings plot shows every reading of one weekday of one period,
# and the fit plot shows one year (every year is scored in the table).
RAW_PLOT_YEAR = 2024
RAW_PLOT_PERIOD = "semester_1"
RAW_PLOT_WEEKDAY = 0      # 0 = Monday
FIT_PLOT_YEAR = 2025
