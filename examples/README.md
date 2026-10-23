# Example: a complete, fully optioned analysis

**Run it (instead of `master.py`).** Optional: this folder exists to be *viewed*, and its committed outputs are the reference. Running these scripts **overwrites** them (`examples\output\`, `reports\performance.txt`, `reports\model_comparison.txt`). If you do run them, do so only *after* the Python check and the clone, virtual-environment and install steps in
[Installation](../README.md#2-installation) of the main README. From the project root:

```powershell
.\.venv\Scripts\python.exe examples\full_analysis.py          # the full analysis below; needs the raw export in data\
.\.venv\Scripts\python.exe examples\compare_models.py         # SVR vs tree vs slot-mean vs median; needs the preprocessed room files
.\.venv\Scripts\python.exe examples\profile_performance.py    # timings, profiler and memory; writes reports\performance.txt
```

`full_analysis.py` runs every stage of the project on the real data and saves everything, so the results can be inspected
without opening a window.

> **For further investigation only.** `examples\output\` is committed as a reference for what a full run produces. It is
> large (several MB of plots and models) and is not needed to use the project, so it is not part of the everyday workflow;
> regenerate it with the command below if you want your own copy.

```powershell
.\.venv\Scripts\python.exe examples\full_analysis.py        # about 5 minutes; needs the raw export in data\
```

## What it does

1. **Preprocessing** (`run_preprocessing`): the raw occupancy file in `data\` becomes one small file per room.
2. **Build rooms:** G.20 and G.25 are the two rooms whose headcount location is verified. The settings (C 0.3, length scale
   2 h, epsilon 0.1) were tuned on them.
3. **Held-out test rooms:** the other three rooms in the data (floorspace IDs beginning `0f3f37f8`, `941f0352`, `3e5a14df`) are
   scored with the same settings, never used for tuning.
4. **Models** for every room are built into `output\models\` (its own copy; the project's `data\models\` folder is not touched).
5. **Scoring** (`score_rooms`, `summarise_scores`): 4-fold cross-validation holding out whole dates, SVR against a constant
   median, for every room, year, period and weekday.
6. **Plots**, all optional in the master file but all produced here (`plot_saved_models`, `plot_raw_readings`, `plot_fits`).

## Output (`output\`)

| File | Contents |
|---|---|
| `scores.csv` | one line per room, year, period and weekday: dates, SVR MAE, median MAE, group (build or held-out) |
| `models_built.csv` | one line per model built |
| `models\<floorspace id>\*.csv` | the example's models (format in [../data/models/README.md](../data/models/README.md)) |
| `plots\saved_models_*.png` | each saved model's weekday regressions |
| `plots\raw_readings_*.png` | every raw Monday reading in semester 1 2024, per room |
| `plots\fits_*_2025.png` | slot means and fitted regression, per room, for 2025 |
| `plots\score_comparison.png` | SVR against the median baseline, by room and period |

## Results (as run)

| Group | SVR MAE | Median MAE | Subsets better |
|---|---|---|---|
| Build rooms (G.20, G.25) | 0.990 | 1.132 | 94 of 112 |
| Held-out test rooms | 0.644 | 0.809 | 121 of 147 |
| All | 0.793 | 0.948 | 215 of 259 |

Caveat: "held-out" means not used to choose the settings. Each subset is still scored by cross-validation on its own room's
dates, so this does not test applying one room's model to another room (the sensors' room assignment is unverified for the
three unnamed rooms).
