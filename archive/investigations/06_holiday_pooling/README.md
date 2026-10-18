# 06 Holiday pooling: one model per period vs one lumped holiday model

**Question.** For the non-teaching periods, is it better to fit each period on its own (with only the pooling needed to fit the
one-week mid-semester breaks) or to lump all of a year's holiday dates into one model per weekday?

**Setup.** G.20 and G.25, 2024-2026, 15-minute slot means, SVR with the fixed settings from [05](../05_svr_vs_tree_tuning/README.md).
Run from the project root: `python archive\investigations\06_holiday_pooling\run.py`.
- **A, minimum pooling:** each period is its own model, each weekday alone; the mid-semester breaks (one date per weekday per
  year) have Monday-Friday fitted together.
- **B, one holiday model:** before semester 1, both mid-semester breaks, the mid-year break and after semester 2 of a year are lumped,
  each weekday (Mon-Sun) fitted alone.
- **C, no pooling:** each period and weekday alone, for every period. Added after A and B were first compared., the same folds for both schemes, so both predict exactly the same 39,074 held-out slots.
  Baseline: constant median of B's training dates.

**Results** (mean absolute error in people; `results.csv` has every slot).

| Period | A (min pooling) | B (holiday) | Median | Slots |
|---|---|---|---|---|
| before_semester_1 | 0.647 | 0.643 | 0.690 | 12,169 |
| mid_semester_break_1 | 0.844 | 0.808 | 0.892 | 1,318 |
| mid_year_break | 0.643 | 0.621 | 0.689 | 11,589 |
| mid_semester_break_2 | **0.696** | 0.979 | 1.180 | 730 |
| after_semester_2 | 0.778 | 0.764 | 0.811 | 13,268 |
| **Overall** | 0.698 | 0.689 | 0.747 | 39,074 |

**Findings.**
- **No pooling (C) is identical to A everywhere it can be scored.** A only differs from C on the mid-semester breaks, so
  on the long holidays (37,026 slots) A = C exactly (0.693 overall). The "specificity" of A is therefore confined to the two
  breaks, which is the only place any pooling is applied.
- **No pooling cannot score the mid-semester breaks at all:** each weekday has one date per year, so holding it out leaves
  nothing to train on. A model for those weeks could only be fitted from a single day per weekday, and its accuracy could
  not be measured. Scheme A's break 2 figure (0.696) is its only measured accuracy there.
- On the slots every scheme can score, B beats A/C by 0.014 (0.679 vs 0.693), by 0.004-0.022 per period. This is small and
  sits inside the noise of a 15-minute-slot MAE, but B is ahead in every period and both rooms, except G.20 before
  semester 1 (1.104 vs 1.100).
- Mid-semester break 1 is slightly better under B (0.808 vs 0.844), in both rooms.
- Mid-semester break 2 is the exception: B is much worse (0.979 vs 0.696, and barely better than the median, 1.180). Under B
  it is predicted from mostly summer/winter holiday days, but in September the room is still busy.
  This holds in both rooms (G.25: 0.961 vs 0.619; G.20: 1.013 vs 0.844). It rests on only 730 slots, about two years of one week.
- Sat-Sun: B 0.363, A 0.376, median 0.365, so no model beats a constant at weekends.

**Conclusion.** Pooling the long holidays is a small gain, not a necessity (no pooling works there). Pooling is only
*needed* for the mid-semester breaks, where no pooling is unscoreable, and the lumped holiday model is worse than A for break 2. A is not
more specific on the long holidays; it differs only on the breaks. The next scheme to test is three groups per year: semester 1,
semester 2 and the long holidays, with the breaks pooled across the two breaks, or left with the semester they interrupt.
