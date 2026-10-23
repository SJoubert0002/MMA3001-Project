# 04 - Decision-tree grid on 15-minute slot averages

**Run it (instead of `master.py`).** Run this only *after* the Python check and the clone, virtual-environment and install steps in
[Installation](../../../README.md#2-installation) of the main README, and with the preprocessed room files in
`data\derived\preprocessed\occupancy_streams` (made by running the tool once on the raw export). From the project root
(results are written to `test\output\investigations\04_tree_grid_15min_slots\`, which is git-ignored; the committed CSV is not touched):

```powershell
.\.venv\Scripts\python.exe archive\investigations\04_tree_grid_15min_slots\run.py
```

**Question.** Does averaging each date's readings into 15-minute slots (to remove point-to-point flicker while keeping
fidelity) improve the tree, and does it beat simple baselines on unseen days?

**Setup.** Same subsets as investigation 03 (Mon-Wed, 88 subsets random split, 66 day split), but each date x slot is one
mean value (about 96 per day). Trees: depth 3, 5, 8, unlimited x min leaf 1, 3, 5, 10, 20, 50, 100.
Baselines: zero, one median per subset, and the slot-mean profile (mean of training days at each clock slot).

**Results (mean MAE, slot values).**

| Model | Random split | Whole days held out |
|---|---|---|
| Zero | 1.766 | 1.689 |
| Median constant | 1.145 | 1.118 |
| Slot-mean profile | 1.175 | 1.151 |
| Best tree | **0.955** (depth 3, leaf 1) | **1.098** (depth 3, leaf 20) |

- Random split: the best tree beats the median in 64 of 88 subsets and the slot mean in 85 of 88.
- Day split: the tree beats the median in 36 of 66 subsets and the slot mean in 52 of 66. Depth 3 is consistently best;
  the table is flat for leaf 10-50.

**Conclusion.** Slot averaging removes the flicker (MAE about 1.1 against about 1.75 on raw readings), but for unseen days
time of day alone explains little: the tree is only about 2% better than a constant median. A shallow tree (depth 3, leaf
about 20) is the defensible choice. Full table: `results.csv`.

**Next (not yet run).** Add week of semester and a holiday flag as inputs, scored on whole held-out days; if the MAE does not
fall clearly below 1.1, the remaining error is day-specific and only booking or timetable data would help.

**Reproduce.** `python archive\investigations\04_tree_grid_15min_slots\run.py`
