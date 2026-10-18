# 01 - Mode vs mean vs median as the slot statistic

**Question.** The every-reading interpolant overfitted. Would the mode of each weekday x 15-minute slot be a better model
than the mean, given outliers matter less than predictability?

**Setup.** Train on 2024 semester 1 or 2, test on the same period in 2025, for G.20 and G.25. Each model is a statistic of
the readings in each weekday x 15-minute slot; ties in the mode go to the lowest value. "Zero" always predicts 0.

**Results (MAE, headcount units).**

| Room, period | Mean | Median | Mode | Zero |
|---|---|---|---|---|
| G.20 sem 1 | 2.94 | 2.76 | 2.91 | 4.43 |
| G.20 sem 2 | 4.26 | 4.04 | 3.77 | 4.30 |
| G.25 sem 1 | 2.59 | 2.55 | 2.16 | 2.56 |
| G.25 sem 2 | 2.32 | 2.07 | 1.95 | 2.47 |

- By RMSE the mean or median was often equal to or better than the mode.
- The mode was 0 in 12-39% of slots.
- Roughness between adjacent slots (mean vs mode): G.20 sem 1 0.46 vs 0.43; G.20 sem 2 0.72 vs 0.93; G.25 sem 1 0.47 vs 0.79;
  G.25 sem 2 0.48 vs 0.73. The mode curve is not consistently smoother.

**Conclusion.** The mode wins on MAE in 3 of 4 cases but the gain is mixed and it is zero-heavy. It was adopted as the saved
model (weekday x slot mode + PCHIP) at the time. Later investigations (03, 04) questioned how well any such model predicts
unseen days.

**Reproduce.** The original script was a throwaway and was not kept; this record holds the numbers.
