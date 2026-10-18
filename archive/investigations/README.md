# Investigations archive

One folder per investigation, in the order they were run. Each holds a short write-up (`README.md`), the script that
produced the results (`run.py`, run from the project root) and the saved result tables. Nothing here changes the
notebook or the saved models. Scripts use the notebook's own functions through [_common.py](_common.py), so they need
`pre-Processing.ipynb` and the preprocessed room files in `derived\preprocessed\occupancy_streams`.

| # | Question | Finding |
|---|---|---|
| [01](01_mode_vs_mean_median/README.md) | Is the mode (or median) a better slot statistic than the mean? | Mode had the lowest MAE in 3 of 4 cases, but not by RMSE, and was not reliably smoother. |
| [02](02_overnight_and_timezone_check/README.md) | Are overnight headcounts a time-zone error? | No. Timestamps and clock changes are right; overnight counts behave like sensor flicker. |
| [03](03_tree_grid_raw_readings/README.md) | Which decision-tree leaf size/depth fits raw readings best? | Depth 8, leaf 20-50 on a random split, but on unseen days a tree is no better than a constant. |
| [04](04_tree_grid_15min_slots/README.md) | Does averaging into 15-minute slots help? | MAE falls to about 1.1, but on unseen days the tree still only ties the median constant. |
| [05](05_svr_vs_tree_tuning/README.md) | Which model to ship, and with which fixed settings? | RBF SVR (C 0.3, length 2 h, epsilon 0.1) beats the best tree and the median; the surface is flat, so tuning is not delicate. |
| [06](06_holiday_pooling/README.md) | One model per period, or one lumped holiday model per year? | Lumping is equal or slightly better on the long holidays and break 1, but clearly worse on mid-semester break 2. |
| [07](07_midsem_break_grouping/README.md) | Model a mid-semester break with its semester or with the holidays? | With the semester: clearly better for break 2, roughly even for break 1. |
| [08](08_final_three_period_scores/README.md) | How does the adopted layout (semester 1, semester 2, all non-teaching days; SVR per weekday) score? | MAE 0.990 vs 1.132 for a constant, every subset scorable. Mid-semester breaks go with the holidays by choice, at a known cost for break 2. |

**Conventions for new investigations:** copy a folder as a template; keep the question, setup, results table, and
conclusion in the README; save the full result table as CSV; never overwrite an earlier folder.

**Decision:** extra inputs (week of semester, holiday flags) will not be added; only the semester calendar the user already
supplies is used.
