# 02 - Overnight headcounts and the time zone

**Question.** G.20 semester 1 2024 Monday readings show people at midnight. Is that a timestamp error?

**Setup.** `run.py` checks the UTC offsets stored in the raw timestamps, the hour-by-hour mean headcount before and after the
7 April 2024 clock change, and how non-zero readings between 00:00 and 05:00 behave (March-May 2024, G.20 and G.25).

**Results.**
- The raw timestamps carry their own Melbourne offset: `+11` before 7 Apr 2024 and `+10` after, switching correctly (same
  in 2025 and 2026). There is no one-hour shift. Occupancy starts around 08:00 in both halves of the semester.
- Overnight readings, 00:00-05:00:

| Room | Readings | Share above 0 | Share 3 or more | Max |
|---|---|---|---|---|
| G.20 | 815 | 47% | 0.7% | 3 |
| G.25 | 8,939 | 62% | 22% | 16 |

- 75-83% of consecutive overnight readings differ from the previous one, which is flicker, not someone sitting still.
- G.20's non-zero overnight runs are very short (median under a minute, longest 17 min). G.25 has one run of about 300 min.
- G.20 peaked at 17:00-19:00 (mean 6-7) before 7 Apr but at 09:00-10:00 afterwards: a timetable or sensor change.

**Conclusion.** Not a time-zone error; overnight counts look like sensor noise. Not proven: confirming would need access
logs, the raw `occupancystatus` and `deviceid` columns, or neighbouring rooms. Open decision: whether to set implausible
overnight counts to NaN, and the G.25 five-hour run is worth checking in the raw file.

**Reproduce.** `python archive\investigations\02_overnight_and_timezone_check\run.py`
