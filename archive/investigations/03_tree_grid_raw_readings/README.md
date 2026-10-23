# 03 - Decision-tree grid on raw readings

**Run it (instead of `master.py`).** Run this only *after* the Python check and the clone, virtual-environment and install steps in
[Installation](../../../README.md#2-installation) of the main README, and with the preprocessed room files in
`data\derived\preprocessed\occupancy_streams` (made by running the tool once on the raw export). From the project root
(results are written to `test\output\investigations\03_tree_grid_raw_readings\`, which is git-ignored; the committed CSVs are not touched):

```powershell
.\.venv\Scripts\python.exe archive\investigations\03_tree_grid_raw_readings\run.py
```

**Question.** With one input (time of day), which minimum leaf size and maximum depth give the lowest error for a decision tree
fitted to each period's Mondays, Tuesdays and Wednesdays?

**Setup.** G.20 and G.25, 2024-2026, every period; one tree per (room, year, period, weekday), 94 subsets (66 with at least
5 days for the day split). Grid: min leaf 1, 5, 20, 50, 100, 200, 500, 1000, 2000 x max depth 4, 8, unlimited.
- Random split: 80% of readings train, 20% held out (seed 0).
- Day split: 20% of whole dates held out (seed 1).
- Baseline: the training median as a constant.

**Results (mean MAE).**

| min leaf | depth 4 | depth 8 | unlimited |
|---|---|---|---|
| 1 | 1.468 | 1.422 | 1.824 |
| 5 | 1.470 | 1.414 | 1.530 |
| 20 | 1.469 | **1.407** | 1.425 |
| 50 | 1.480 | 1.423 | 1.423 |
| 100 | 1.506 | 1.457 | 1.454 |
| 200 | 1.554 | 1.514 | 1.512 |
| 500 | 1.670 | 1.647 | 1.646 |
| 1000 | 1.776 | 1.761 | 1.761 |
| 2000 | 1.906 | 1.898 | 1.898 |

Random-split median baseline: 1.75. Whole-day hold-out: trees score 1.94-1.98 (best: depth 4, leaf 50, 1.942), versus a
median baseline of 1.77.

**Conclusion.** The random split flatters small leaves because neighbouring readings are near-duplicates. On unseen days a
one-input tree does not beat a constant median, and leaf size changes MAE by under 0.05. Full tables:
`results_random_split.csv`, `results_day_split.csv`.

**Reproduce.** `python archive\investigations\03_tree_grid_raw_readings\run.py` (about 1.5 minutes).
