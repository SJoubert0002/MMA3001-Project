"""A complete, fully optioned analysis of the project data.

Builds and tunes the models on the two verified rooms (G.20 and G.25), then scores the other three
rooms as held-out test rooms. Every optional plot is saved as a PNG and every table as a CSV in
examples/output/. It uses its own models folder, so the project's data/models/ folder is untouched.

Run from anywhere:  python examples/full_analysis.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")  # save the plots to files; no windows

from source.analysis.build_all_models import build_all_models
from source.analysis.plot_fits import plot_fits
from source.analysis.plot_raw_readings import plot_raw_readings
from source.analysis.plot_saved_models import plot_saved_models
from source.analysis.plot_score_comparison import plot_score_comparison
from source.analysis.read_semester_calendar import read_semester_calendar
from source.analysis.room_label import room_label
from source.analysis.score_rooms import score_rooms
from source.analysis.summarise_scores import summarise_scores
from source.preprocessing.config import DATA_DIR, LOOKUP_FOLDERS, OUTPUT_DIR
from source.preprocessing.find_floorspace_ids import find_floorspace_ids
from source.preprocessing.ids_in_folder import ids_in_folder
from source.preprocessing.read_lookup import read_lookup
from source.preprocessing.run_preprocessing import run_preprocessing

RAW_FILE = DATA_DIR / "5occupancySensor_MayToDec2024_9MRows.csv"
BUILD_ROOMS = ["G.20", "G.25"]
OUTPUT = Path(__file__).resolve().parent / "output"


def main():
    """Run the full analysis and save everything in examples/output/.

    Input:
        None. Reads the raw data in data/, the semester calendar and the lookup files.

    Output:
        None. Prints the results and saves: scores.csv (every subset),         models/ (the example's own models)
                and the PNG plots. (build_all_models can also save the readings split by period; that is large, so it is off here.)

    Errors:
        FileNotFoundError if the raw occupancy file is missing.
    """
    OUTPUT.mkdir(exist_ok=True)
    calendar = read_semester_calendar([DATA_DIR])
    summary, redone = run_preprocessing(RAW_FILE)
    print(f"Preprocessing {'done' if redone else 'already up to date'}:\n{summary.to_string(index=False)}\n")
    streams = OUTPUT_DIR / "occupancy_streams"

    all_ids = ids_in_folder(streams)
    build_ids = set(find_floorspace_ids(BUILD_ROOMS, LOOKUP_FOLDERS, all_ids).values())
    test_ids = sorted(all_ids - build_ids)
    lookup = read_lookup(LOOKUP_FOLDERS)
    print("Build rooms:", [room_label(lookup, i) for i in sorted(build_ids)])
    print("Held-out test rooms:", [room_label(lookup, i) for i in test_ids], "\n")

    built = build_all_models(calendar, streams, OUTPUT / "models")
    built.to_csv(OUTPUT / "models_built.csv", index=False)
    print(f"Built {len(built)} models (all rooms) in {OUTPUT / 'models'}\n")

    scores, fits = score_rooms(calendar, streams, LOOKUP_FOLDERS)
    scores["group"] = scores["room_id"].map(lambda i: "build rooms" if i in build_ids else "held-out test rooms")
    scores.to_csv(OUTPUT / "scores.csv", index=False)
    summarise_scores(scores, group_column="group")

    plot_saved_models(OUTPUT / "models", LOOKUP_FOLDERS, save_folder=OUTPUT / "plots")
    plot_raw_readings(calendar, streams, LOOKUP_FOLDERS, save_folder=OUTPUT / "plots")
    plot_fits(fits, save_folder=OUTPUT / "plots")
    plot_score_comparison(scores, OUTPUT / "plots" / "score_comparison.png")
    print(f"\nSaved tables and plots in {OUTPUT}")


if __name__ == "__main__":
    main()
