"""Are the overnight headcounts a time-zone error or sensor noise? (Mar-May 2024, G.20 and G.25.)
Checks the UTC offsets stored in the raw timestamps, the hour-by-hour mean headcount before/after the
7 Apr 2024 clock change, and how overnight non-zero readings behave (flicker, run lengths)."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))
from _common import ROOMS

streams = Path("derived/preprocessed/occupancy_streams")
for rid, room in ROOMS.items():
    d = pd.read_csv(streams / f"{rid}.csv", dtype=str)
    offsets = d.collecteddate.str[-3:]
    print(f"\n=== {room} ===")
    print("UTC offsets present:", offsets.value_counts().to_dict())
    print("first/last timestamp per offset:\n", d.groupby(offsets).collecteddate.agg(["min", "max"]).to_string())
    t = pd.to_datetime(d.collecteddate, utc=True, format="ISO8601").dt.tz_convert("Australia/Melbourne")
    h = pd.to_numeric(d.headcount, errors="coerce")
    ok = h.notna() & (t.dt.year == 2024) & t.dt.month.between(3, 5)
    t, h = t[ok].reset_index(drop=True), h[ok].reset_index(drop=True)
    weekday = t.dt.dayofweek < 5
    for label, sel in [("before 7 Apr", t < pd.Timestamp("2024-04-07", tz="Australia/Melbourne")),
                       ("after 7 Apr", t >= pd.Timestamp("2024-04-07", tz="Australia/Melbourne"))]:
        print(f"mean headcount by local hour, weekdays, {label}:", h[weekday & sel].groupby(t[weekday & sel].dt.hour).mean().round(2).to_dict())
    night = t.dt.hour < 5
    both = night & night.shift(1, fill_value=False)
    changed = (h.diff().abs() > 0) & both
    nonzero = (h > 0) & night
    runs = pd.DataFrame({"run": (nonzero != nonzero.shift()).cumsum()[nonzero], "t": t[nonzero]}).groupby("run").t.agg(
        lambda s: (s.max() - s.min()).total_seconds() / 60)
    print(f"00:00-05:00 readings: {night.sum()}; share >0: {(h[night] > 0).mean():.3f}; share >=3: {(h[night] >= 3).mean():.3f}; max: {h[night].max()}")
    print(f"share of consecutive overnight readings that change value: {changed.sum() / max(1, both.sum()):.3f}")
    print(f"non-zero overnight runs: {len(runs)}; median {runs.median():.1f} min; longest {runs.max():.1f} min; runs >=120 min: {(runs >= 120).sum()}")
