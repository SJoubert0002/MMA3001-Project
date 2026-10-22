"""Master file: estimate the headcount of a room at a time.

Every run answers from the saved models in data/models; a data file (--data or the pop-up) is
preprocessed and its models are used as well. Nothing is read from data/ automatically.
Plots are optional and chosen in a pop-up.

Usage:
    python master.py                                  pop-ups ask for new files, then the room and time
    python master.py G.20 "2025-04-09 14:00"          no pop-ups for the question
    python master.py G.20 "2025-04-09 14:00" --data new.csv --lookup lookup.csv --label trial
    python master.py --plots all                      also show every optional plot (the queried day's model
                                                      over its raw readings, for new and training data)

Where the outputs go depends on where the --data file is kept:
    data/    its models are saved in data/models for later predictions (the only place models are kept from)
    test/    everything is returned to test/output/<file name>/; data/models is not changed
    other    the models are used for that answer only and discarded
"""

import argparse
import contextlib
import shutil
import sys
import tempfile
from pathlib import Path

from source.analysis.ask_files import ask_files
from source.analysis.ask_inputs import ask_inputs
from source.analysis.ask_plots import ask_plots, PLOT_CHOICES
from source.analysis.choose_output import choose_output
from source.analysis.config import MODELS_DIR
from source.analysis.describe_answer import describe_answer
from source.analysis.get_headcount import get_headcount
from source.analysis.list_rooms import list_rooms
from source.analysis.load_new_data import load_new_data
from source.analysis.plot_new_data_day import plot_new_data_day
from source.analysis.plot_training_day import plot_training_day, TRAINING_STREAMS
from source.analysis.read_semester_calendar import read_semester_calendar
from source.preprocessing.config import DATA_DIR
from source.preprocessing.ids_in_folder import ids_in_folder
from source.preprocessing.store_lookup import store_lookup


def show_plots(kinds, room, time_text, calendar, new_data, lookup_folders):
    """Show the chosen optional plots in windows: the model of the queried day over that day's raw readings.

    Input:
        kinds: a list of "new" and/or "training".
        room: the room name asked about.
        time_text: the time asked about, YYYY-MM-DD HH:MM.
        calendar: the dictionary made by read_semester_calendar.
        new_data: None if no data file was given, otherwise (preprocessed folder, models folder, label).
        lookup_folders: folders searched for lookup files.

    Output:
        None. A plot that cannot be drawn (for example no preprocessed training data) prints why and is skipped.

    Errors:
        None raised.
    """
    if "new" in kinds:
        if new_data is None:
            print("The new-data plot needs a data file (--data or the pop-up); skipped.")
        else:
            streams, models, label = new_data
            plot_new_data_day(room, time_text, calendar, streams, models, label, lookup_folders)
    if "training" in kinds:
        try:
            plot_training_day(room, time_text, calendar, lookup_folders=lookup_folders)
        except FileNotFoundError as error:
            print(f"Training-data plot skipped: {error}")


@contextlib.contextmanager
def work_folders(out):
    """Provide the folder for processed room files and the models folder of a run (see choose_output).

    Folders that choose_output leaves as None are temporary and removed afterwards. The test folder's
    processed files are cleared first so that old files of other rooms are not mixed in.

    Input:
        out: the dictionary made by choose_output.

    Output:
        (streams folder, models folder), valid inside the with-block.

    Errors:
        None.
    """
    with tempfile.TemporaryDirectory() as temporary:
        streams = out["streams_folder"]
        if streams is None:
            streams = Path(temporary) / "streams"
        elif Path(streams).exists():
            shutil.rmtree(streams)
        models = out["models_folder"] or Path(temporary) / "models"
        yield Path(streams), Path(models)


def headcount(room, time_text, data_file="", lookup_file="", label="", calendar=None, details=None):
    """Estimate the headcount of a room at a time (the whole pipeline, without pop-ups or plots).

    Where the outputs go depends on where the data file is (see choose_output): a file in data/
    adds models to data/models, a file in test/ returns everything to test/output/, and a file
    anywhere else is used for this answer only.

    Input:
        room: the room name, e.g. "G.20".
        time_text: the time, YYYY-MM-DD HH:MM (Melbourne time).
        data_file: optional. A new raw occupancy CSV; models are built from it, never replacing existing ones.
        lookup_file: optional. A room lookup CSV; a copy is kept (data/lookups, or test/lookups if it is in test/).
        label: a short name for the new data (default: the data file's name).
        calendar: optional. The dictionary made by read_semester_calendar (read if not given).
        details: optional. An empty dictionary filled with the model used and its error (see get_headcount).

    Output:
        The expected headcount, or None if the models have no data for that weekday.

    Errors:
        ValueError if the time, room or files are invalid.
        FileNotFoundError if there is no model for that period and no data was supplied.
    """
    calendar = calendar or read_semester_calendar([DATA_DIR])
    out = choose_output(data_file, lookup_file)
    if lookup_file:
        store_lookup(lookup_file, out["lookups_folder"])
    if not data_file:
        return get_headcount(room, time_text, calendar, lookup_folders=out["lookup_folders"], details=details)
    print(out["note"])
    label = label or "".join(c if c.isalnum() else "-" for c in Path(data_file).stem)
    with work_folders(out) as (streams, models):
        load_new_data(data_file, streams, out["lookup_folders"])
        return get_headcount(room, time_text, calendar, new_data_folder=streams, label=label,
                             models_folder=models, lookup_folders=out["lookup_folders"], details=details)


def main(argv=None):
    """Command-line entry point: ask for anything not given, answer, then offer the optional plots.

    Input:
        argv: optional list of arguments (default: the command line).

    Output:
        0 on success, 1 if there was an error or no answer.

    Errors:
        None raised; errors are printed.
    """
    parser = argparse.ArgumentParser(description="Estimate the headcount of a room at a time.")
    parser.add_argument("room", nargs="?", help='room name, e.g. "G.20"')
    parser.add_argument("time", nargs="?", help='time, "YYYY-MM-DD HH:MM" (Melbourne time)')
    parser.add_argument("--data", default="", help="new raw occupancy CSV")
    parser.add_argument("--lookup", default="", help="room lookup CSV")
    parser.add_argument("--label", default="", help="short name for the new data")
    parser.add_argument("--plots", choices=["ask", "none", "all"], default="ask",
                        help="optional plots: ask in a pop-up (default), none, or all")
    args = parser.parse_args(argv)
    if bool(args.room) != bool(args.time):
        parser.error("give both the room and the time, or neither")
    interactive = not args.room

    try:
        calendar = read_semester_calendar([DATA_DIR])
        data_file, lookup_file = args.data, args.lookup
        if interactive and not (data_file or lookup_file):
            files = ask_files()
            if files is None:
                print("Cancelled.")
                return 1
            data_file, lookup_file = files
        out = choose_output(data_file, lookup_file)
        if lookup_file:
            store_lookup(lookup_file, out["lookups_folder"])
        value = None
        if data_file:
            print(out["note"])

        with work_folders(out) as (streams, models):
            if data_file:
                rooms = load_new_data(data_file, streams, out["lookup_folders"])
            else:
                rooms = list_rooms(out["lookup_folders"], ids_in_folder(MODELS_DIR))
            room, time_text = args.room, args.time
            if interactive:
                answer = ask_inputs(rooms)
                if answer is None:
                    print("Cancelled.")
                    return 1
                room, time_text = answer
            label = args.label or "".join(c if c.isalnum() else "-" for c in Path(data_file).stem)
            details = {}
            value = get_headcount(room, time_text, calendar, new_data_folder=streams if data_file else None,
                                  label=label, models_folder=models if data_file else None,
                                  lookup_folders=out["lookup_folders"], details=details)
            if value is not None:
                print(describe_answer(room, time_text, value, details))

            kinds = {"none": [], "all": ["new", "training"], "ask": None}[args.plots]
            if kinds is None:
                available = {k: v for k, v in PLOT_CHOICES.items()
                             if (data_file or k != "new") and (k != "training" or any(TRAINING_STREAMS.glob("*.csv")))}
                kinds = ask_plots(available) if interactive and available else []
            show_plots(kinds, room, time_text, calendar, (streams, models, label) if data_file else None,
                       out["lookup_folders"])
        return 0 if value is not None else 1
    except (ValueError, FileNotFoundError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
