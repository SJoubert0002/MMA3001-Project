# 07 Mid-semester breaks: model them with the semester or with the other holidays?

**Run it (instead of `master.py`).** Run this only *after* the Python check and the clone, virtual-environment and install steps in
[Installation](../../../README.md#2-installation) of the main README, and with the preprocessed room files in
`data\derived\preprocessed\occupancy_streams` (made by running the tool once on the raw export). From the project root
(results are written to `test\output\investigations\07_midsem_break_grouping\`, which is git-ignored; the committed CSV is not touched):

```powershell
.\.venv\Scripts\python.exe archive\investigations\07_midsem_break_grouping\run.py
```

**Question.** Follow-up to [06](../06_holiday_pooling/README.md). With three models per year in mind (semester 1, semester 2,
holidays), should each mid-semester break be lumped into the semester it interrupts, or into the holiday model?

**Setup.** G.20 and G.25, 2024-2026, 15-minute slot means, SVR with the fixed settings from
[05](../05_svr_vs_tree_tuning/README.md), one weekday at a time. Run from the project root:
`python archive\investigations\07_midsem_break_grouping\run.py`. The break's dates are held out (4 folds by whole date, the same
folds for every scheme) and predicted from:
- **S, with the semester:** the semester's other dates of that year (semester + its break).
- **H, with the holidays:** that year's before semester 1, mid-year break, after semester 2 and both breaks.
- **A, break only:** the break's Monday-Friday fitted together (minimum pooling, the 06 scheme), as a reference.
- Baseline: constant median of S's training dates.

All schemes predict the same 2,219 held-out break slots (break 2 has no 2026 data yet). `results.csv` has every slot.

**Results** (mean absolute error in people).

| Break | S (semester) | H (holidays) | A (break only) | Median | Slots |
|---|---|---|---|---|---|
| mid_semester_break_1 | 0.943 | **0.848** | 0.894 | 0.924 | 956 |
| mid_semester_break_2 | 1.156 | 1.502 | **1.108** | 1.558 | 1,263 |
| **Overall** | 1.064 | 1.220 | **1.016** | 1.285 | 2,219 |

| Room / break | S | H | A | Median |
|---|---|---|---|---|
| G.20 break 1 | **1.179** | 1.258 | 1.350 | 1.265 |
| G.20 break 2 | **1.283** | 1.775 | 1.347 | 1.746 |
| G.25 break 1 | 0.754 | **0.522** | 0.530 | 0.653 |
| G.25 break 2 | 1.076 | 1.329 | **0.956** | 1.439 |

**Findings.**
- **Break 2 clearly belongs with its semester**, not the holidays: S 1.156 vs H 1.502, and H is no better than the median
  (1.558). It holds in both rooms. September is still busy, so a model trained on mostly empty holiday days is wrong.
- **Break 1 is mixed.** H is better overall (0.848 vs 0.943) but only because of G.25 (0.522 vs 0.754, driven by 2024 and
  Monday); on G.20 the semester is better (1.179 vs 1.258). By year, H wins 2024 (0.645 vs 0.945) and S wins 2026 (0.952 vs 1.005).
  A plausible but untested reason is that break 1 is the Easter/Anzac week, which is more holiday-like than break 2.
- Over all 42 room/year/break/weekday cells, S beats H in 25 and loses in 17. Overall S 1.064 vs H 1.220.
- The break-only pooling (A) is best overall (1.016) and beats S in 25 of 42 cells, but only by 0.05, and is the
  specific scheme you wanted to avoid. S is the best of the two schemes that need no break-specific rule.
- Every scheme beats the median overall (1.285), but the margin is small on G.20 break 1 (S 1.179 vs 1.265).

**Conclusion.** With the three-models-a-year layout, put the mid-semester breaks **with their semester**. It is clearly better
for break 2, roughly even on break 1 (H wins there by 0.1 on 956 slots, mostly one room and year), costs no extra rule,
and the semester model has enough dates per weekday to fit. This is based on only two breaks per year over 2-3 years, so it
is weak evidence for break 1 in particular.
