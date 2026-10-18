# 05 - RBF SVR vs decision tree: choosing and tuning the model

**Question.** Which one-input regression (time of day only) has the soundest theoretical backing, and which settings should
be fixed in the notebook so that no user input beyond a room and a time is needed?

**Choice on theory: RBF SVR.** Its epsilon-insensitive loss acts like a median (L1) fit, so small noise and outliers are
ignored, which matches scoring by MAE and the preference for predictability over outliers. Its kernel smoothing has a
regularisation justification, it has only three settings (C, gamma, epsilon), and the stored model is small. A tree has steps
that suit timetables but no smoothness prior. The tree was kept as the main rival.

**Setup.** G.20 and G.25, 2024-2026, Monday to Wednesday, 15-minute slot means, one regression per room x year x period x
weekday (66 subsets; mid-semester breaks have fewer than 4 days per weekday and are excluded). Every setting is scored by
4-fold cross-validation grouped by date, so a date is never split between train and test, and the score is averaged over all
subsets so one global setting can be shipped. As a selection-bias check, settings were chosen on 2024 subsets and scored on
2025-2026 subsets.
- SVR grid: C 0.1-3, kernel length scale 1-6 h (gamma = 1 / (2 x length^2)), epsilon 0.01-0.2.
- Tree grid: depth 2-6, min leaf 5-100, squared-error or absolute-error criterion.
- A first, narrower SVR grid put the best values on its edge, so the grid was extended once.

**Results (mean slot MAE, headcount units).**

| Model | All 66 subsets | Chosen on 2024, tested on 2025-2026 (42 subsets) |
|---|---|---|
| Predict zero | 1.791 | - |
| Median constant | 1.180 | 1.003 |
| Slot-mean profile | 1.192 | - |
| Best tree (depth 3, min leaf 10, absolute error) | 1.046 | 0.910 (depth 4, leaf 20) |
| **Best SVR (C 0.3, length 3 h, eps 0.03)** | **1.031** | **0.896** (C 0.3, length 2 h, eps 0.03) |

- SVR beats the tree in 53 of 66 subsets and the median in 58 of 66; on the 2025-2026 check it beats the median in 37 of 42
  (tree 34 of 42).
- The tree benefits from the absolute-error criterion, which agrees with the SVR's median-like behaviour.
- By period (SVR / tree / median): semester 1 1.078 / 1.101 / 1.318; semester 2 1.591 / 1.612 / 1.887; before semester 1
  0.691 / 0.690 / 0.752; mid-year break 0.795 / 0.806 / 0.830; after semester 2 0.975 / 0.993 / 1.042.
- **The SVR surface is flat.** Best-of-others MAE by setting: C 0.1 to 3 gives 1.031-1.033; length 1 to 6 h gives 1.031-1.035;
  epsilon 0.01 to 0.1 gives 1.031 and 0.2 gives 1.035. Any setting in that range is within about 0.004 of the best.

**Conclusion / recommended fixed settings.** RBF SVR with C = 0.3, kernel length scale 2 h (gamma = 0.125 per hour squared) and
epsilon = 0.1, which lie inside every searched range and on the flat plateau. Gains over a constant median are real on
semesters (about 15%) but modest overall, and every model leaves most of the day-to-day variation unexplained.

**Caveats.**
- C and epsilon are in headcount units, so a much busier room (counts of hundreds) would need them scaled with the typical
  headcount; the two rooms here have means of a few people.
- Mid-semester breaks and Thursday to Sunday were not scored; the same settings would be reused there.

**Full table.** `results.csv` (one row per subset and setting).

**Reproduce.** `python archive\investigations\05_svr_vs_tree_tuning\run.py` (about 20 seconds).
