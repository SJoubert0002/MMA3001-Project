# Archived notebook cell: Monday readings in 2024 Semester 1 against their 15-minute slot averages
# and a PCHIP curve through the averages. Superseded by fitting through every reading by date.
# It relied on SLOT_MINUTES (= 15), floorspace_ids, calendar, read_room_data and label_periods
# from the old weekly-average version of pre-Processing.ipynb.
from scipy.interpolate import PchipInterpolator

import matplotlib.pyplot as plt

room_ids = floorspace_ids
if not room_ids:
    raise ValueError("No room IDs are available to plot.")

fig, axes = plt.subplots(len(room_ids), 1, figsize=(12, 4 * len(room_ids)), squeeze=False)
axes = axes.ravel()

for ax, (room_name, room_id) in zip(axes, room_ids.items()):
    data, times = read_room_data(room_id, OUTPUT_DIR / "occupancy_streams")
    periods = label_periods(times, calendar)

    # Keep Monday readings in 2024 Semester 1, excluding the mid-semester break.
    mask = (times.dt.year == 2024) & (times.dt.dayofweek == 0) & (periods == "semester_1")
    monday = pd.DataFrame({
        "time": times[mask],
        "headcount": pd.to_numeric(data.loc[mask, "headcount"], errors="coerce").to_numpy()
    }).dropna(subset=["headcount"])

    if monday.empty:
        ax.set_title(f"{room_name}: no Monday readings in 2024 Semester 1")
        continue

    monday["minute"] = (
        monday["time"].dt.hour * 60
        + monday["time"].dt.minute
        + monday["time"].dt.second / 60
    )
    monday["slot"] = monday["time"].dt.floor(f"{SLOT_MINUTES}min").dt.strftime("%H:%M")

    slot_averages = monday.groupby("slot")["headcount"].mean().reset_index()
    slot_averages["minute"] = pd.to_datetime(
        slot_averages["slot"], format="%H:%M"
    ).dt.hour * 60 + pd.to_datetime(
        slot_averages["slot"], format="%H:%M"
    ).dt.minute
    slot_averages = slot_averages.sort_values("minute")

    ax.scatter(monday["minute"], monday["headcount"], s=8, alpha=0.18,
               label="Individual readings")
    ax.scatter(slot_averages["minute"], slot_averages["headcount"], s=28,
               color="darkorange", label="15-minute slot averages")

    if len(slot_averages) >= 2:
        curve = PchipInterpolator(slot_averages["minute"], slot_averages["headcount"])
        x_curve = pd.Series(
            [slot_averages["minute"].min() + i
             for i in range(int(slot_averages["minute"].max() - slot_averages["minute"].min()) + 1)]
        )
        ax.plot(x_curve, curve(x_curve), color="crimson", linewidth=2,
                label="PCHIP fitted curve")

    ax.set_title(f"{room_name} — Mondays, 2024 Semester 1")
    ax.set_xlabel("Time of day")
    ax.set_ylabel("Headcount")
    ax.set_xticks(range(0, 1441, 120))
    ax.set_xticklabels([f"{hour:02d}:00" for hour in range(0, 25, 2)])
    ax.grid(True, alpha=0.25)
    ax.legend()

plt.tight_layout()
plt.show()
