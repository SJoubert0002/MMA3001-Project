# Archive: how the final preprocessing and model came to be

This folder is the project's record of the work that led to the current code (`source\`, run by `master.py`) and the saved
models in `data\models\`. Nothing here is used at run time. It exists to show, for the project brief, which alternatives were
tried, how they were validated, and why each was kept or dropped.

**The final design in one paragraph.** Input: a room name and a time. Occupancy readings are split by room and labelled with
one of three periods per year (`semester_1`, `semester_2`, `non_teaching`) using the user's semester calendar. Each period
and weekday gets one RBF support-vector regression of headcount on time of day, fitted to 15-minute slot averages
(C 0.3, length scale 2 h, epsilon 0.1). Only the support vectors are stored, so answering a query needs no scikit-learn.
Final score (investigation 08): MAE 0.990 against 1.132 for a constant median, on whole held-out dates, in 112 of 112
subsets.

## Layout

| Path | Contents |
|---|---|
| `investigations\` | Numbered, reproducible experiments (README, `run.py`, result CSVs) that chose the model. Index: [investigations\README.md](investigations/README.md). |
| `notebooks\` | The earlier notebooks and one stray cell, superseded by the overhaul, plus `pre-Processing_final_notebook.ipynb`: the last single-notebook form of the preprocessing and model (one function per cell), kept as the immediate predecessor of `source\`. It runs from the project root and writes its models to `models\` in place. The archive also held `derived\` (outputs of the earlier occupancy analyses) and `.rewrite_notebook.js`; both are now git-ignored (kept locally only). The notebook's own paths assume the old layout (`derived\`, `models\` and the calendar in the project root); the investigation scripts redirect them to `data\` through `_common.py`. |
| `working_tree_diff_summary.txt` | A git diff statistic captured before the overhaul (git-ignored). |

Reproduce any investigation (02 to 08) from the project root, *after* the Python check and the clone, virtual-environment and install steps in [Installation](../README.md#2-installation) of the main README, e.g. `.\.venv\Scripts\python.exe archive\investigations\05_svr_vs_tree_tuning\run.py`. Each investigation's own README gives its exact line.
They need the archived notebook `notebooks\pre-Processing_final_notebook.ipynb` and the preprocessed room files in `data\derived\preprocessed\occupancy_streams` (made by `master.py`).

## Decision timeline

| Step | What was tried | Outcome | Evidence |
|---|---|---|---|
| 1 | Early notebooks: audit data, test semester-phase hypotheses, plot raw readings | Informed the problem framing; the work was descriptive, not predictive. Replaced by a "room and time in, headcount out" tool. | `notebooks\` |
| 2 | Interpolating curves (PCHIP) through every reading, then through slot averages | Overfitted: a curve through every reading reproduces sensor flicker. | Described in 01 and 03 |
| 3 | Weekday x 15-minute slot mean, median or mode, then PCHIP | Mode won MAE in 3 of 4 cases but not RMSE, was zero-heavy and not smoother. | 01 |
| 4 | Is overnight occupancy a time-zone error? | No; flicker. Timestamps and clock changes are correct. | 02 |
| 5 | Decision-tree grid on raw readings | A random split rewards tiny leaves (leakage); on whole unseen dates a tree is no better than a constant median. | 03 |
| 6 | Same on 15-minute slot averages | MAE about 1.1 rather than 1.75; tree only about 2% better than the median. | 04 |
| 7 | RBF SVR vs tree, tuned by date-grouped cross-validation | SVR chosen on theory and score (1.031 vs tree 1.046 vs median 1.180); flat tuning surface. | 05 |
| 8 | How to model non-teaching periods | One lumped model per year vs per break vs no pooling, then mid-semester break placement. | 06, 07 |
| 9 | Final layout (3 periods, all non-teaching days together) | Adopted for broad applicability across rooms; known cost on mid-semester break 2. | 08 |

## Archived items, annotated

Each entry gives the objective, the reason it was not carried forward (or what it decided), and where it serves the brief.

### Notebooks (`notebooks\`)

| File | Objective | Why not carried forward | Brief relevance |
|---|---|---|---|
| `pre-Processing_v1.ipynb` | First version of preprocessing (parse environmental and occupancy CSVs, write per-room streams) with built-in unit tests and read benchmarks, plus a raw scatter of Monday-Friday headcounts per room and semester. | The notebook was one 45,000-character cell: hard to read, test or reuse. Superseded by one function per cell with strict inputs. | Inputs and data handling; early validation (unit tests) and timing. |
| `semester_cycle_occupancy_investigation.ipynb` | Test three hypotheses with a data audit: H1 semester phases differ in occupancy, H2 which weeks drop, H3 daily peaks occur around noon. Compared against persistence baselines. | Descriptive; its "final evidence and conclusion" section was never completed. The project moved to prediction of headcount for a given room and time. Its audit findings were kept: uneven start/end dates, out-of-order rows (4 to 1,317 per room), explicit UTC offsets on every row, no missing headcounts. | Engineering problem; data quality; limitations. |
| `pre-Processing_occupancy-investigation.ipynb` | The same H1-H3 design as the one above, run on a shared five-room window (May to Dec 2024), with a weekly occupancy plot across rooms. | Same reason. Left unfinished. | Same. |
| `slot_average_plot_cell.py` | Plot Monday semester 1 2024 readings against 15-minute slot averages and a PCHIP curve. | Superseded by modelling with an SVR on slot averages. | Alternatives (interpolation) and visual validation. |

### `working_tree_diff_summary.txt`
Diff statistic of derived outputs and the old notebook before the overhaul. Kept only as a record of how much the earlier
work was replaced. It carries no results.

### Investigations (`investigations\`)

| # | Objective | Key result | Why it did not (or did) decide the design | Brief section |
|---|---|---|---|---|
| 01 | Is the mode a better slot statistic than mean or median? | Mode lowest MAE in 3 of 4 cases; not better by RMSE; zero in 12-39% of slots. | Adopted briefly, then discarded: later whole-date testing showed no slot statistic predicts unseen days well, and the mode is unstable. No script survives. | Alternatives |
| 02 | Time zone or sensor noise behind overnight counts? | Offsets +11/+10 switch correctly; 62% of G.25 overnight readings above 0; flicker pattern. | Not a model choice. Decided against a time-zone fix. Open: whether to set overnight counts to NaN. | Data, limitations |
| 03 | Best tree leaf/depth on raw readings. | Random split favours depth 8, leaf 20 (1.407); on whole days 1.94-1.98 vs median 1.77. | Rejected as a method: random splits leak because neighbouring readings are near-duplicates. Lesson: score by whole date. | Validation |
| 04 | Does 15-minute averaging help? | MAE about 1.1; tree beats median in 36 of 66 subsets. | Slot averaging kept. The tree gained only about 2%, so a better model class was sought. | Validation, alternatives |
| 05 | Choose and tune the model (SVR vs tree). | Median 1.180, best tree 1.046, SVR 1.031; chosen on 2024, tested on 2025-26: 1.003, 0.910, 0.896. Flat surface (about 0.004). | **Decided**: RBF SVR. Tree kept as the rival: steps suit timetables but no smoothness prior. | Computational approach, alternatives |
| 06 | Pool non-teaching periods: lumped holiday vs minimum pooling vs none. | Overall 0.689 (lumped) vs 0.698 vs median 0.747; break 2 worse when lumped (0.979 vs 0.696). No pooling equals minimum pooling where scorable but cannot score the breaks. | Lumping chosen for broad applicability: minimum pooling is specific to this calendar. | Alternatives, assumptions |
| 07 | Put mid-semester breaks with the semester or with the holidays. | With semester 1.064, with holidays 1.220, break-only 1.016, median 1.285. | Evidence favoured the semester for break 2. The user chose to lump them with other non-teaching days regardless, accepting the cost. A one-line change in `label_periods` reverses it. | Assumptions, limitations |
| 08 | Score the final layout. | SVR 0.990 vs median 1.132; better in 94 of 112 subsets; all scorable. | Final result of record. | Validation |

## Validation method and its limits

- **Method.** Every model is scored by 4-fold cross-validation grouped by whole date, so a date never sits in both train
  and test. Metric: mean absolute error in headcount units, averaged over subsets (room x year x period x weekday).
  Baselines: a constant median, the zero model, and the slot-mean profile.
- **It did influence selection**: it exposed the leakage in 03, selected the SVR in 05 and settled pooling in 06-07. A
  selection-bias check chose settings on 2024 and scored them on 2025-26.
- **What it cannot establish.** The settings were tuned on G.20 and G.25 only. The other three rooms were scored afterwards
  with the same settings (see Limitations below), but nothing here shows how a room of a different kind, size or sensor
  would behave. Years are not independent evidence of future semesters. The 2026 data is partial. Sensor accuracy is
  unknown: no ground-truth counts exist. The absolute gain over a median (about 12-17%) is modest because the day-to-day
  variation is not explained by time of day alone.

## Limitations and lessons

Decisions the author made on the open technical questions, with the reasoning, so the report can quote them.

- **Overnight sensor noise (stated limitation, not cleaned).** Overnight (00:00-05:00) counts look like flicker (02), but
  there is no ground truth (access logs, door counts) to prove a count false, so none are removed or set to NaN. The
  model therefore inherits any such noise; its effect is damped by the 15-minute slot averaging and the SVR's
  epsilon-insensitive loss, but it is not eliminated.
- **Unnamed rooms.** The lookup is the only link between a room name and a floorspace ID. A user can only query a room that
  has data or a saved model and that a lookup names; otherwise they are told to supply data or a lookup (the notebook prints
  a CLARIFICATION NEEDED message). Nothing is guessed. The lookup file is labelled "Invalid" in its name because its
  SpaceFloorIDs were reported incorrect; names are therefore only as reliable as that mapping.
- **Mid-semester break 2 (known trade-off).** Mid-semester breaks are lumped with the other non-teaching days for broad
  applicability, since the same break pattern cannot be assumed in other rooms. Investigation 07 shows break 2 belongs with
  its semester (about 1.50 for the lumped model vs 1.16 for a median in G.20 and G.25; with the semester 1.064, with the
  holidays 1.220); break 1 is about even. The alternative is a one-line change in `label_periods`, and the same reasoning
  would apply to any other non-teaching period.
- **Scaling (documented, not built in).** The SVR constants C (0.3) and epsilon (0.1) are in headcount units and were tuned
  on rooms with mean headcount about 3-4.5. A much busier room might gain a little from scaling them with the room's typical
  count. This is not built in: MAE is about 1 anyway, the surface is flat (about 0.004 across a wide grid, 05), and a
  scaling rule would add settings and bloat the model for a gain that may never occur. Evidence so far: across the five
  rooms in the data (mean headcount 2.3-4.5, 95th percentile 5-14, maximum 15-72) the fixed settings beat the median in every
  room.
- **Rooms beyond G.20 and G.25.** Only those two have verified names, but models for the other three IDs are built and
  stored with them so they are available if later data or a lookup names them, and as evidence for the scaling point. Scored
  with the unchanged settings: 245 subsets over all five rooms, SVR MAE 0.806 vs 0.968 for a median, better in 205. The
  quieter rooms have lower MAE (about 0.5-0.9) than G.20 (about 1.0-1.9). One unnamed room has 2024 data only. These
  scores are not an independent test, since the settings were fixed before these rooms were scored.
- **Environment.** Developed and tested in a venv on Python 3.14.5 with numpy 2.5, pandas 3.0, scikit-learn 1.9, matplotlib
  3.11 and scipy 1.18 (the versions used for every result here).

Lessons from the process:- Random-split scores overstate accuracy for time series; use whole-date holdout.
- Time of day and period explain little of the variation; further gains would need booking or timetable data, which was
  deliberately excluded to keep the inputs minimal.
- Several earlier exploratory scripts (interpolation, mode test) were throwaways; only their numbers survive in 01.

## AI use (for the brief's reflection)

An AI coding assistant (GitHub Copilot) helped write the notebook functions, the investigation scripts and these notes.
The author set the direction and made the decisions: abandoning the first approach, dropping environmental data, rejecting
extra inputs, choosing the SVR, lumping the non-teaching periods and requiring whole-date scoring. The assistant also
made errors that were caught and corrected, for example claiming 1-2 dates per break weekday when there is exactly one.
*(Author to review and amend this section; the exact tools and extent of use should be stated in the final report.)*
