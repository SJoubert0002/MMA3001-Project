# Saved models

One small CSV per room, year and period. `get_headcount` reads these directly, so a fresh clone can answer a
room-and-time query without the raw data or scikit-learn (only numpy and pandas). They are tracked in git on purpose.

## Naming

`data\models\<room id>\<year>_<period>.csv`

- `<room id>`: the floorspace ID. G.20 = `cca1ac3e-f81f-4ebb-aa2b-8b0bf3e9e53b` and G.25 = `227f1068-9e41-469f-bef0-275f27a0bdba`
  are the only IDs the lookup names. The other three (`0f3f37f8…`, `3e5a14df…`, `941f0352…`) are in the data but unnamed.
  Their models are built and stored too, in case a later lookup or data names them; until then they cannot be chosen by
  room name and appear in the room list by the start of their ID.
- `<period>`: `semester_1`, `semester_2` or `non_teaching` (everything outside teaching weeks, including both mid-semester
  breaks), as labelled from `Semester Calendar.csv`.
- New data never overwrites a file: it is saved as `<year>_<period>_<label>.csv`. A query that supplies new data is answered
  from the model built from it; a query without new data uses the unlabelled model, or, if the period has none, the newest
  labelled one.

## File format

One RBF support-vector regression per weekday, stored as its support vectors.

| Column | Meaning |
|---|---|
| `weekday` | 0 = Monday ... 6 = Sunday |
| `support_hour` | Time of day of a support vector, in hours (0-24) |
| `dual_coef` | Its weight in the kernel sum |
| `intercept` | The model's constant term (repeated on each row of that weekday) |
| `dates` | How many dates of that weekday the regression was trained on (repeated on each row) |
| `cv_mae` | The weekday's cross-validated mean absolute error in people: how far a 15-minute average typically is from the model on dates it was not trained on (repeated on each row). Gives each answer its uncertainty (`model_error`) |

Prediction at hour `t` is `intercept + sum(dual_coef * exp(-gamma * (t - support_hour)^2))`, with
`gamma = 1 / (2 x SVR_LENGTH_HOURS^2)`, evaluated by `evaluate_model`. A weekday with fewer than
`SVR_MIN_DATES` (3) dates has no rows and returns no answer. The headings are checked exactly, so models made before
`dates` and `cv_mae` were added are rejected and must be rebuilt (`build_all_models`).

## Provenance

| Item | Value |
|---|---|
| Rooms | All 5 floorspace IDs in the data; only G.20 and G.25 have names in the lookup. The 3e5a14df room has 2024 data only. |
| Data | Raw occupancy readings 2023-11 to 2026-04-22; 2026 is partial |
| Calendar | `data\Semester Calendar.csv` (2024-2026) |
| Slot width | 15 minutes (`SLOT_MINUTES`); each date's readings averaged per slot |
| SVR settings | C 0.3, length scale 2 h, epsilon 0.1 (`SVR_C`, `SVR_LENGTH_HOURS`, `SVR_EPSILON`) |
| Built by | `build_models` in `source\analysis\build_models.py` |
| Score | G.20 and G.25: MAE 0.990 vs 1.132 for a constant median. All five rooms: 0.793 vs 0.948, better in 215 of 259 subsets (`examples\output\scores.csv`) |

## Rebuilding

Run `build_all_models` on the preprocessed room files (made by `run_preprocessing` from the raw data in `data\`). Rebuild
only when the settings, the period definitions or the data change, and replace the whole set together so the folder
shows one coherent set. If the constants in `source\analysis\config.py` change, update the Provenance table above.
