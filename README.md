# MMA3001-Project: expected room headcount from occupancy-sensor history

Give the code a **room name** and a **time** and it returns the **expected headcount** of that room at that time.
The answer comes from a saved regression model of the room for the semester period the time falls in. The models were built
from occupancy-sensor history and the university's semester calendar. You can also supply new sensor data, in which case
models are built from it.

This README is about **using** the tool: its inputs, outputs, formats and every error it can raise. The entry point is
[master.py](master.py).

---

## Contents

1. [What it does and does not do](#1-what-it-does-and-does-not-do)
2. [Installation](#2-installation)
3. [Running it](#3-running-it)
4. [Inputs and required formats](#4-inputs-and-required-formats)
5. [Outputs](#5-outputs)
6. [Errors and their causes](#6-errors-and-their-causes)
7. [Where outputs go (data, test, anywhere else)](#7-where-outputs-go)
8. [Optional plots](#8-optional-plots)
9. [Calling it from Python](#9-calling-it-from-python)
10. [How it works](#10-how-it-works)
11. [Saved model format](#11-saved-model-format)
12. [Settings](#12-settings)
13. [Results and limitations](#13-results-and-limitations)
14. [The full example](#14-the-full-example)
15. [Tests and documentation](#15-tests-and-documentation)
16. [Repository layout](#16-repository-layout)
17. [AI acknowledgement](#17-ai-acknowledgement)
18. [Licence and references](#18-licence-and-references)

---

## 1. What it does and does not do

**Provides:** the *typical* headcount of a room for a weekday, time of day and semester period, learned from past sensor
readings, with a typical-error range.

**Does not provide:**

- a forecast of one specific day (public holidays, exams, events and timetable changes are not inputs);
- room capacity, bookings, or the reason a room is busy;
- a verified count of people. The sensors have no ground truth available here.

The only inputs are the room, the time and (optionally) new data. The semester calendar is the only other input.

## 2. Installation

**Step 0: install 64-bit Python 3.13 or 3.14 (Windows).** Download the **Windows installer (64-bit)** from
<https://www.python.org/downloads/windows/>. Tick **"Add python.exe to PATH"** and keep **"tcl/tk and IDLE"** ticked (the
pop-ups need it). **32-bit Python does not work**: pandas and
scikit-learn have no 32-bit Windows builds, and `pip install` fails with a Visual Studio / `vswhere.exe` error. Check in a
new PowerShell window:

```powershell
py --version                                              # Python 3.13.x or 3.14.x
py -c "import struct; print(struct.calcsize('P')*8, 'bit')"   # must print 64 bit
```

**Python versions.**

| Version | Status |
|---|---|
| 3.14 (3.14.5) | **Tested**: all results, tests and examples. |
| 3.13 (3.13.17, 64-bit) | **Tested**: install, pop-ups, queries and a `test.csv` run in both `data/` and `test/`. |
| 3.12 | *Expected to work* (not tested): the pinned numpy 2.5.4 and scipy 1.18.1 require Python 3.12 or later, and no code here needs anything newer. |
| 3.11 | *Possible but not with these pins* (not tested): pandas, scikit-learn and matplotlib support 3.11 but the pinned numpy and scipy do not. Install the unpinned packages (`pip install numpy pandas scikit-learn matplotlib`) instead. |
| 3.10 and older | *Not expected to work*: the pinned pandas 3 line needs 3.11 or later. |
| 3.15 and later | *Unknown* (not tested): depends on whether the pinned packages publish wheels for it. |

If `python` says *"Python was not found; run without arguments to install from the Microsoft Store"*, that is only the
Microsoft Store shortcut. Use `py` as below, or turn the shortcut off in *Settings > Apps > Advanced app settings > App
execution aliases* ("App Installer python.exe").

**Step 1: get the code and install the packages.** Copy the whole block into PowerShell:

```powershell
git clone https://github.com/SJoubert0002/MMA3001-Project.git
cd MMA3001-Project                       # every command below is run from this folder
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r environment\requirements.txt
```

- Without git, use the green **Code > Download ZIP** button on the repository page, extract it, and open PowerShell in the
  extracted folder (in File Explorer, click the address bar, type `powershell`, press Enter).
- If `git clone` says the folder already exists, you cloned before: `cd MMA3001-Project` and run `git pull` instead.
- `environment\requirements-lock.txt` installs the exact versions used for every result (Python 3.14) in place of `environment\requirements.txt`.
- The environment's `python.exe` is called directly, so no activation (and no execution-policy change) is needed. If you prefer
  to activate it and PowerShell says *"running scripts is disabled"*, run
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` first, then `.\.venv\Scripts\Activate.ps1`.
- If a `.venv` was made with the wrong Python, delete it (`Remove-Item -Recurse -Force .venv`) and repeat Step 1.

**Step 2: run it.**

```powershell
.\.venv\Scripts\python.exe master.py
```

Three pop-ups open in turn (see [section 3](#3-running-it)). Leave both file boxes empty and click **Continue**, choose
**G.20**, type `2025-04-09 14:00`, click **OK**, then **No plots**. To skip the pop-ups:

```powershell
.\.venv\Scripts\python.exe master.py G.20 "2025-04-09 14:00"
```

Expected output (the model files come with the clone, so no raw data is needed):

```
Expected headcount in G.20 at 2025-04-09 14:00: 2.8 people (typically within 1.4 of the model; about 1.5 to 4.2)
  model:  2025_semester_1.csv (2025 semester_1, Wednesday regression)
  basis:  12 dates of that weekday in the period; ...
```

All later commands in this README use `.\.venv\Scripts\python.exe` for the same reason.

The raw sensor export is **not** included in the repository (it is too large). Without it you can query the saved models
(rooms G.20, G.25 and three unnamed IDs, years 2023 to 2026; the 2026 periods are partial), run the tests, and use your own data in the format of
[section 4](#4-inputs-and-required-formats). The full example needs the raw export and cannot be run from a fresh clone.

The versions listed in `environment/` are the ones tested; see the Python version table above.

| Package | Needed for |
|---|---|
| numpy, pandas | everything, including answering from saved models |
| scikit-learn | building models and scoring (not needed to answer from saved models) |
| matplotlib | optional plots |
| tkinter | pop-ups (ships with the standard Windows Python installer) |
| pytest | the tests |
| pdoc | regenerating `source/docs/` |

A fresh clone already contains the saved models in [data/models/](data/models/README.md), so a query works with no raw data.

## 3. Running it

Run these from the repository folder, after the setup in section 2. Every command uses the environment's own Python
(`.\.venv\Scripts\python.exe`), so it works even if `python` is not recognised on your machine.

```powershell
.\.venv\Scripts\python.exe master.py                                          # pop-ups: optional new files, then room and time, then optional plots
.\.venv\Scripts\python.exe master.py G.20 "2025-04-09 14:00"                  # no question pop-ups; the plots pop-up is skipped
.\.venv\Scripts\python.exe master.py G.20 "2025-04-09 14:00" --plots all      # also show every optional plot
.\.venv\Scripts\python.exe master.py G.20 "2025-04-09 14:00" --data new.csv --lookup lookup.csv --label trial
```

(If you have activated the environment, `python master.py ...` is the same thing.)

| Argument | Meaning |
|---|---|
| `room` (optional, positional) | room name, e.g. `G.20`. Give it together with `time`, or give neither. |
| `time` (optional, positional) | `"YYYY-MM-DD HH:MM"`, Melbourne time. Quote it (it contains a space). |
| `--data FILE` | a new raw occupancy CSV. Models are built from it and used for the answer. |
| `--lookup FILE` | a room lookup CSV. A checked copy is kept for future runs. |
| `--label NAME` | short name for the new data (default: the data file's name with non-alphanumerics replaced by `-`). Becomes part of the model file name. |
| `--plots ask|none|all` | `ask` (default): pop-up after the answer when run interactively, no plots when a room and time were given. `none`: no plots. `all`: every plot that applies. |

**Pop-up mode (no room and time given).** Three windows can open in turn:

1. *New files*: optionally choose a raw occupancy CSV and/or a room lookup CSV. Skip both to use only the saved models.
   (Skipped when `--data` or `--lookup` is given.)
2. *Room and time*: choose a room from the list and type the time.
3. *Plots*: tick the plots to show. Closing the window or pressing "No plots" shows nothing. The *new data* option appears only
   if you gave a data file, and the *training data* option only if the raw export has been preprocessed into
   `data/derived/preprocessed/occupancy_streams/` (not the case on a fresh clone); with nothing to offer, this window is skipped.

Closing or cancelling the first two windows prints `Cancelled.` and exits with code 1.

**Exit code:** `0` when an answer was printed, `1` otherwise (error, cancelled, or no regression for that weekday).

## 4. Inputs and required formats

Strictness is the rule: a file whose column headings are not **exactly** as below (same names, same order, no extra columns)
is rejected with an error naming the file and showing the expected and found headings.

### 4.1 Room name

Text, e.g. `G.20`. Matched case-insensitively against the **Floor/Room** column of the lookup. If a name belongs to several
floorspace IDs, the pop-up lists one choice per ID (e.g. `1.61 (ID ending 5c3a)`) and the command line stops with an error
listing the choices. Rooms with data but no name in any lookup appear in the pop-up by the start of their ID.

The saved models cover five floorspace IDs: G.20 (`cca1ac3e-...`), G.25 (`227f1068-...`) and three unnamed IDs beginning
`0f3f37f8`, `941f0352` and `3e5a14df`.

### 4.2 Time

`YYYY-MM-DD HH:MM`, 24-hour, read as **Australia/Melbourne** local time.

- `2025-04-09 14:00` is valid. Single-digit months and days such as `2025-4-9 14:00` are also accepted.
- Seconds, other separators, 12-hour clocks, or a date that does not exist are rejected.
- Daylight-saving clock changes: a local time that does not exist (spring forward) or occurs twice (fall back) is rejected.
- The year must be in the semester calendar (currently 2021 to 2026).

### 4.3 Raw occupancy data (optional, `--data`)

A CSV with exactly these headings, in this order:

```
id, deviceid, floorspaceid, occupancystatus, headcount, collecteddate, occupancystatuschangedate, previousoccupancystatus
```

| Column | Used | Requirement |
|---|---|---|
| `floorspaceid` | yes | the room's floorspace ID; no blanks |
| `headcount` | yes | whole number, 0 or more; blank allowed (treated as missing) |
| `collecteddate` | yes | timestamp with its own UTC offset, e.g. `2024-05-01T09:15:00+10:00`; no invalid values |
| all others | no | must be present as headings, contents are ignored |

The file may be large (a 1.5 GB, 9-million-row export is processed in about a minute) because it is read in pieces of 50,000 rows.

### 4.4 Room lookup (optional, `--lookup`; one is always needed)

File name like `Sensor ID and Locations - OCC*.csv`, exactly these headings:

```
Building, Floor/Room, Area, ID, Note, FloorId, SpaceId
```

It maps the room name (`Floor/Room`) to the floorspace ID (`ID`). The tracked lookup is in `data/`. A lookup you supply is checked
and copied to `data/lookups/` (or `test/lookups/` if it came from `test/`), never overwriting an existing copy. All stored
lookups are combined; if they disagree on an ID, the newest file wins.

### 4.5 Semester calendar (always read)

`data/Semester Calendar.csv`, exactly these headings:

```
year, semester, start_date, end_date, break_start, break_end
```

Dates are `YYYY-MM-DD`. One line per semester (1 or 2); the break is the mid-semester break. Every year present needs both
semesters. To query a new year, add its two lines.

Rules checked: end not before start; break inside the semester; no repeated year and semester; both semesters per year;
semester 2 starts after semester 1 ends.

## 5. Outputs

### 5.1 The answer (printed)

```
Expected headcount in G.20 at 2025-04-09 14:00: 2.8 people (typically within 1.4 of the model; about 1.5 to 4.2)
  model:  2025_semester_1.csv (2025 semester_1, Wednesday regression)
  basis:  12 dates of that weekday in the period; the error is the model's cross-validated mean absolute error on dates it was not trained on
```

- **Headcount**: a number, never below 0. Sensors report whole people, the model's value is a smoothed average, so it is not an integer.
- **Typical error**: the model's cross-validated mean absolute error (whole-day average) and the range it gives. It is too wide
  overnight and too narrow at peak times.
- **Model and basis**: which saved file answered, and how many dates of that weekday it was trained on.
- **Caution**: printed when the model was trained on fewer than 6 dates.
- **No answer (`None`)**: if the period has fewer than 3 dates of that weekday, nothing is printed except the exit code 1.

### 5.2 Files written

| When | What |
|---|---|
| A raw file is given from `data/` | preprocessed streams in `data/derived/preprocessed/occupancy_streams/<floorspace id>.csv` (`headcount, collecteddate`) plus `rows_per_room.csv`, and models in `data/models/<floorspace id>/<year>_<period>_<label>.csv` |
| A raw file is given from `test/` | everything in `test/output/<file name>/{streams,models}` |
| A raw file is given from elsewhere | temporary folders, deleted after the run |
| No raw file | nothing is written |
| A lookup is given | a checked copy in `data/lookups/` or `test/lookups/` |

Preprocessing is skipped, with a message, if the streams are newer than the raw file. Models built from new data **never overwrite** existing models.

## 6. Errors and their causes

Errors are printed as `ERROR: <message>` and the exit code is 1. Nothing is guessed.

| Message (start) | Cause | Fix |
|---|---|---|
| `Time '...' is not valid. Write it as YYYY-MM-DD HH:MM` | wrong format, impossible date, or a clock-change hour that does not exist or repeats | use a real Melbourne time in the format |
| `The year N is not in the semester calendar` | the time's year has no calendar lines | add both semesters of that year to `Semester Calendar.csv` |
| `... has the wrong column headings. Expected: [...] Found: [...]` | occupancy, lookup or calendar file with different headings (names, order, extra or missing) | correct the headings |
| `Semester calendar file ... not found` / `Room lookup file ... not found` | the file is not in `data/` (or `data/lookups/`) | restore it |
| `Invalid line in Semester Calendar.csv` | a blank or badly formatted date or semester number | fix the line |
| `Year N semester S has dates that end before they start` / `the break must be inside the semester` / `appears more than once` | calendar rule broken | fix the calendar |
| `Year N needs both semester 1 and semester 2` / `semester 2 must start after semester 1 ends` | calendar rule broken | fix the calendar |
| `Headcounts must be whole numbers of 0 or more (or blank)` | text, negative or fractional headcount in new data | clean the data |
| `Found a row with no room ID` | a blank `floorspaceid` in new data | clean the data |
| `Found a row with an invalid collection date` | an unreadable `collecteddate` | clean the data |
| `The occupancy file contains no data rows` | headings only | supply data |
| `[Errno 2] No such file or directory: ...` / `Occupancy file not found` | the `--data` or `--lookup` path is wrong | correct the path |
| `REJECTED: 'X' has no matching data ...` followed by `No matching data: none of the requested rooms ...` | the room name is not in any lookup, or has no data or models | check the spelling, or supply a lookup |
| `Room 'X' has several floorspace IDs. Choose one of: ...` | one name shared by several IDs | choose by ID (use the pop-up) |
| `None of the rooms in the new data can be matched to a room name` | no `floorspaceid` in the new data is in any lookup | supply a lookup with `--lookup` |
| `There are no rooms to choose from` | no lookup and no models | restore `data/` |
| `The new data has no readings for <room> in <year> <period>` | the new file does not cover the queried period | supply data for that period |
| `No saved model for <room> in <year> <period>. Supply a data file covering that period.` | no model exists for that room and period | supply a data file with `--data` |
| `Model headings are [...], expected [...]` / `The model has a blank or non-numeric value` | an old or edited model file (models built before the error columns were added are rejected) | rebuild with `build_all_models` |
| `Plots: Training-data plot skipped: ...` / `The new-data plot needs a data file; skipped` | a plot that cannot be drawn. Not an error: the answer is still printed | run preprocessing on the raw file, or give `--data` |
| *(exit 1 with no message)* | fewer than 3 dates of that weekday in the period's model | supply more data |

## 7. Where outputs go

Decided by `choose_output` from where the `--data` file is kept:

| Data file is in | Models | Streams | Notes |
|---|---|---|---|
| `data/` | stored in `data/models/` for later queries | `data/derived/preprocessed/` | the **only** place models are kept from |
| `test/` | `test/output/<file name>/models` | `test/output/<file name>/streams` | live sandbox for your own experiments; `data/models` is not changed |
| anywhere else | temporary | temporary | used for this answer only |
| (none) | saved models in `data/models/` | none | |

Saved models are only ever extracted from inputs in `data/`. Everything in `test/` except `.gitkeep` is git-ignored.

## 8. Optional plots

Both plots show **the model of the queried period's weekday drawn over the raw headcount readings of that specific day**, with the
typical-error band and the period's other dates of the same weekday in faint grey.

| Plot | Needs | Shows |
|---|---|---|
| New data | `--data` (or the pop-up file) | the model built from the new data over that day's raw readings in the new data |
| Training data | the preprocessed training streams in `data/derived/preprocessed/occupancy_streams/` (made by running preprocessing on the raw export) | the saved model over that day's raw readings. A date outside the training data shows the model alone. |

A plot that cannot be drawn prints why and is skipped.

## 9. Calling it from Python

```python
from master import headcount
headcount("G.20", "2025-04-09 14:00")                                        # saved models
headcount("G.20", "2025-04-09 14:00", data_file="new.csv", label="trial")    # build from new data first
```

`headcount(room, time_text, data_file="", lookup_file="", label="", calendar=None, details=None)` returns the headcount or `None`.
Pass an empty dict as `details` to receive `model_file, year, period, weekday, dates, cv_mae`. It raises `ValueError` or
`FileNotFoundError` for the errors in [section 6](#6-errors-and-their-causes). Every function in `source/` has a docstring with
Input, Output and Errors sections ([source/docs/](source/docs/index.html) is the same as HTML).

## 10. How it works

1. **Preprocess** the raw file: check headings; read in pieces; keep `floorspaceid, headcount, collecteddate`; clean headcounts;
   split into one file per room.
2. **Label periods.** Every reading is placed in a year and one of three periods from the calendar: `semester_1`, `semester_2`
   (each excluding its mid-semester break) and `non_teaching` (everything else, including the break).
3. **Average into 15-minute slots** for each date.
4. **Fit** one RBF support-vector regression (SVR) per weekday per period, of headcount against hour of day. Only the support
   vectors are saved.
5. **Score** by 4-fold cross-validation over dates (not readings), against a constant-median baseline. The mean absolute error is
   stored in the model as the typical error.
6. **Query:** find the period of the time, load the model, evaluate it at the time of day, apply the weekday's error.

## 11. Saved model format

`data/models/<floorspace id>/<year>_<period>[_<label>].csv` (37 files across 5 rooms). Exact headings:

```
weekday, support_hour, dual_coef, intercept, dates, cv_mae
```

One block of rows per weekday (0 = Monday): the support vectors' hours and coefficients, the intercept, the number of dates
trained on and the cross-validated error. `<label>` marks a model built from new data. See [data/models/README.md](data/models/README.md)
for provenance and rebuild rules. Models without `dates` and `cv_mae` are rejected.

## 12. Settings

In `source/analysis/config.py`: SVR penalty `C = 0.3`, kernel length 2 hours, epsilon 0.1 people, 15-minute slots, 4 folds,
at least 3 dates per weekday, timezone `Australia/Melbourne`. Folders and the exact raw headings are in `source/preprocessing/config.py`.

## 13. Results and limitations

Cross-validated on whole dates (mean absolute error in people; baseline = constant median):

| Rooms | SVR | Baseline | Weekday-period cells where SVR wins |
|---|---|---|---|
| G.20 and G.25 (built on) | 0.990 | 1.132 | 94 of 112 |
| Held-out three rooms | 0.644 | 0.809 | 121 of 147 |
| All five | 0.793 | 0.948 | 215 of 259 |

Performance (measured by [examples/profile_performance.py](examples/profile_performance.py); full output in [reports/performance.txt](reports/performance.txt)):
a query from saved models takes about 20 ms in the function (about 0.7 s for the process); preprocessing a 1.5 GB, 9-million-row file
takes about 65 s; building the 8 models of one room takes about 13 s (peak 290 MB of Python allocations); building all 37 models takes about
71 s; the whole process peaks at about 630 MB; the full example takes about 314 s. The profiler shows where the time goes: building a room is
about half timestamp parsing (`pandas.to_datetime`) and about a quarter SVR fitting and cross-validation; a query is dominated by
re-reading the small lookup file on every call (about 30%) and labelling the period from the calendar (about 40%), not by the model.

**Limitations**

- Typical values, not forecasts of a given day.
- The sensors have no ground truth; the room assignment of the sensor IDs is unverified.
- The error is a whole-day average: too wide overnight, too narrow at peak times.
- Weekdays with fewer than 3 dates return no answer; fewer than 6 dates are flagged.
- Calendar years only 2021 to 2026; data covers 2023-11-23 to 2026-04-22. The room `3e5a14df` has 2024 data only.
- A period with no data in a room has no model and needs a data file.

## 14. The full example

[examples/full_analysis.py](examples/full_analysis.py) builds on G.20 and G.25, scores the other three rooms as held out, and saves every
table and plot in `examples/output/` (see [examples/README.md](examples/README.md)). It is large and is for further investigation
only, as a reference for what to expect from the output. It reads the raw export `data/5occupancySensor_MayToDec2024_9MRows.csv`
(git-ignored; supply your own) and does not touch `data/models/`.

## 15. Tests and documentation

```powershell
.\.venv\Scripts\python.exe -m pytest source/tests -p no:cacheprovider      # 10 tests, about 2 seconds
.\.venv\Scripts\python.exe -m pytest source/tests -v --no-header -p no:cacheprovider --durations=0 --junitxml=reports\test_report.xml   # regenerate the test report
.\.venv\Scripts\python.exe -m pdoc source master.py -o source/docs         # regenerate the HTML docs
.\.venv\Scripts\python.exe examples\profile_performance.py                 # regenerate reports\performance.txt (needs the raw export for the preprocessing stage)
```

The tests use small synthetic readings in temporary folders and never write to `data/` or `test/`. The last test report is in
[reports/](reports/test_report.txt): `test_report.txt` (readable) and `test_report.xml` (JUnit).

## 16. Files and their use

| Path | Use |
|---|---|
| [master.py](master.py) | Entry point: answers a room-and-time query, with optional new data and plots. |
| [README.md](README.md) | This guide. |
| [LICENSE](LICENSE) | GNU GPL v3 licence. |
| [environment/requirements.txt](environment/requirements.txt) / [environment/requirements-lock.txt](environment/requirements-lock.txt) | Package versions used / the same with every dependency pinned. |
| `environment/.python-version` | Python version used (3.14). Tools such as pyenv and uv only read this from the repository root; copy it there if you use them. |
| `.gitignore` | Keeps raw data, derived files, the test sandbox, bytecode and environments out of git. |
| [data/Semester Calendar.csv](data/Semester%20Calendar.csv) | Input: semester and mid-semester-break dates (2021-2026) that define the periods. |
| `data/Sensor ID and Locations - OCC (...).csv` | Input: maps room names to floorspace IDs. |
| [data/models/](data/models/README.md) | The 37 saved models, `<floorspace id>/<year>_<period>[_<label>].csv`, read by every query. |
| `data/.gitkeep` | Keeps `data/` in a clone; put raw exports here. |
| `test/.gitkeep` | Keeps the empty `test/` sandbox (see [section 7](#7-where-outputs-go)). |
| `source/preprocessing/` | Checks and cleans raw files: `config`, `check_headings`, `clean_headcount`, `drop_room_id`, `find_floorspace_ids`, `find_unnamed_ids`, `ids_in_folder`, `read_lookup`, `run_preprocessing`, `split_by_room`, `store_lookup`. |
| `source/analysis/` | Models and queries. Pop-ups: `ask_files`, `ask_inputs`, `ask_plots`. Reading: `read_time`, `read_semester_calendar`, `read_room_data`, `list_rooms`, `room_label`, `load_new_data`. Periods: `find_period`, `label_periods`, `split_into_periods`, `slot_means`. Models: `fit_svr`, `predict_svr`, `score_svr`, `make_model`, `build_models`, `build_all_models`, `evaluate_model`, `model_error`. Answering: `get_headcount`, `describe_answer`, `choose_output`. Scoring: `score_rooms`, `summarise_scores`. Plots: `plot_day_against_model`, `plot_new_data_day`, `plot_training_day` (master file); `plot_fits`, `plot_raw_readings`, `plot_saved_models`, `plot_score_comparison` (example). `config` holds the settings. |
| [source/tests/test_pipeline.py](source/tests/test_pipeline.py) | The 10 pytest tests. |
| [source/docs/](source/docs/index.html) | Generated HTML API documentation (open `index.html`). |
| [examples/full_analysis.py](examples/full_analysis.py) | The full analysis: build on G.20 and G.25, test on the other three. |
| [examples/README.md](examples/README.md) | Describes the example and its outputs. |
| [examples/profile_performance.py](examples/profile_performance.py) | Times, profiles and memory-measures preprocessing, model building and a query. |
| [examples/compare_models.py](examples/compare_models.py) | Scores the SVR against a shallow tree, the slot-mean profile and the constant median (accuracy, fit and predict time, stored size). |
| [reports/](reports/test_report.txt) | `test_report.txt` / `test_report.xml` (pytest results) `performance.txt` (timings, profiler output, memory) and `model_comparison.txt` (SVR against the alternatives). |
| [archive/](archive/README.md) | For anyone interested: earlier notebooks and the numbered investigations (`investigations/01` to `08`, each with a README, `run.py` and results) that led to the final design. Not needed to use the tool. |
| `examples/output/` | The example's saved output: `scores.csv`, `models_built.csv`, `models/` and 16 PNG plots. |

## 17. AI acknowledgement

GitHub Copilot, an AI coding assistant running in Visual Studio Code, was used in an interactive chat throughout the project. The author set the direction and the assistant implemented what was specified. Its work included: preprocessing the raw occupancy export (cleaning, period labelling and splitting into per-room files); writing and running the investigation scripts that compared mean, median and mode lookups, decision trees and RBF support-vector regression, and tabulating their cross-validated results; splitting the original notebook into one function per module with a single entry point (`master.py`); the pop-up windows, input validation, output routing and plots; the docstrings, this README, the pdoc HTML documentation, the pytest tests, and the profiling and model-comparison scripts and their reports; diagnosing installation problems on a clean machine; guiding the creation of the zipped clone; and drafting the written report from the repository's own results. Most of the code and prose was written by the assistant on the author's instruction. Prompts and relevant project context were shared with the service to provide this assistance.

The author defined the problem (a tool whose only inputs are a room name and a time), decided to reset the early analysis, removed the environmental data from scope, and made the design decisions: whole-date cross-validation, the three-period layout and its known cost for mid-semester break 2, and which files are public. Suggestions were reviewed rather than accepted automatically: results come from re-runnable scripts, README examples and error messages were produced by running the code, and a fresh clone was installed and run from this README on a clean Python install. This caught real assistant errors, including a zip method that omitted the `.git` folder, an assumed Desktop path, install instructions that failed on a clean machine, a personal file path in the generated documentation, and early model choices that did not hold up under whole-date validation. The author remains responsible for the project's design, implementation, analysis and conclusions.

## 18. Licence and references

GNU GPL v3, see [LICENSE](LICENSE).
