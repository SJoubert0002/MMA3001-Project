# 08 Adopted layout: three periods per year, one SVR per weekday

**Decision.** Following [05](../05_svr_vs_tree_tuning/README.md), [06](../06_holiday_pooling/README.md) and
[07](../07_midsem_break_grouping/README.md), the notebook uses three periods per room and year, each with one RBF SVR per
weekday (Monday-Sunday, never pooled):
- `semester_1` and `semester_2`: the teaching weeks (first to last day, minus the mid-semester break);
- `non_teaching`: every other day (before Semester 1, both mid-semester breaks, the mid-year break, after Semester 2).

Lumping all non-teaching days together was chosen for broad applicability, since other rooms need not behave like G.20 and G.25.
Known cost, from 07: with this rule mid-semester break 2 is modelled with the holidays, which was worse than modelling it with
its semester for these two rooms (1.502 vs 1.156). The alternative is a one-line change in `label_periods`.

**Setup.** `python archive\investigations\08_final_three_period_scores\run.py` (from the project root). 4-fold cross-validation holding out
whole dates, scored against a constant median; fixed settings C 0.3, length 2 h, epsilon 0.1. `results.csv` has every subset.

**Results** (mean absolute error in people, mean over weekdays and years).

| Room | Period | Dates per weekday | SVR | Median |
|---|---|---|---|---|
| G.20 | semester_1 | 10.0 | 1.242 | 1.448 |
| G.20 | semester_2 | 12.0 | 1.879 | 2.047 |
| G.20 | non_teaching | 19.0 | 1.016 | 1.070 |
| G.25 | semester_1 | 10.0 | 0.673 | 0.824 |
| G.25 | semester_2 | 12.0 | 0.889 | 1.171 |
| G.25 | non_teaching | 19.2 | 0.503 | 0.550 |
| **Overall** | | | **0.990** | **1.132** |

- All 112 room, year, period and weekday subsets can be scored (the seven-period layout left 50 unscored); SVR beats the median in 94.
- The gain over a constant is modest in `non_teaching` (G.20 1.016 vs 1.070) and larger in semesters.
- Saturday and Sunday are close to a constant (G.25 Sunday 0.442 vs 0.454).
- G.25 2026 semester 1 is almost level with the median (0.413 vs 0.419); 2026 has only part of the year.
- A stored model reproduces the scikit-learn prediction exactly (G.20 Wednesday 14:07, 2025 semester 1: 2.8347 both ways).
