"""Decide where the outputs of a run go, from where its input data came from.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

from pathlib import Path
from ..preprocessing.config import DATA_DIR, LOOKUPS_DIR, LOOKUP_FOLDERS, TEST_DIR
from .config import MODELS_DIR


def choose_output(data_file="", lookup_file=""):
    """Decide where the models, processed room files and lookup copy of a run are kept.

    Models kept for later predictions must come only from data in the data folder. So:
        - data file in the data folder: models are saved in data/models (kept for later runs); the
          processed room files are temporary.
        - data file in the test folder: everything is returned to the test folder, in
          test/output/<file name>/ (models/ and streams/), and nothing is added to data/models. The test
          folder is a live environment for making your own examples.
        - data file anywhere else: the models are temporary and discarded after the run, so nothing
          outside the data folder is ever stored for later predictions.
        - no data file: the saved models in data/models are used and nothing is built.
    A lookup file in the test folder is copied to test/lookups and used for that run only; any other
    lookup is copied to data/lookups as before.

    Input:
        data_file: the new occupancy file given by the user, or "" if none.
        lookup_file: the new lookup file given by the user, or "" if none.

    Output:
        A dictionary with
            mode: "saved" (no data file), "data", "test" or "other";
            models_folder: where models are saved (None for "other" and "saved"; "other" uses a temporary folder);
            streams_folder: where processed room files are kept (None means use a temporary folder);
            lookups_folder: where a supplied lookup is copied;
            lookup_folders: the folders searched for lookups in this run;
            note: a sentence telling the user where the outputs went (empty if nothing to say).

    Errors:
        None.
    """
    lookups_folder = LOOKUPS_DIR
    lookup_folders = list(LOOKUP_FOLDERS)
    test_lookups = TEST_DIR / "lookups"
    if lookup_file and _is_inside(lookup_file, TEST_DIR):
        lookups_folder = test_lookups
    if lookups_folder == test_lookups or (data_file and _is_inside(data_file, TEST_DIR)):
        lookup_folders.append(test_lookups)

    result = {"mode": "saved", "models_folder": MODELS_DIR, "streams_folder": None, "lookups_folder": lookups_folder,
              "lookup_folders": lookup_folders, "note": ""}
    if not data_file:
        return result
    if _is_inside(data_file, DATA_DIR):
        result["mode"] = "data"
        result["note"] = f"Models built from {Path(data_file).name} are saved in data/models for later predictions."
    elif _is_inside(data_file, TEST_DIR):
        work = TEST_DIR / "output" / "".join(c if c.isalnum() else "-" for c in Path(data_file).stem)
        result.update(mode="test", models_folder=work / "models", streams_folder=work / "streams")
        result["note"] = f"Test data: outputs are returned to {work}; data/models is not changed."
    else:
        result.update(mode="other", models_folder=None)
        result["note"] = ("The data file is outside the data folder, so its models are not stored for later "
                          "predictions. Put it in data/ to keep them, or in test/ to keep the outputs there.")
    return result


def _is_inside(file, folder):
    """True if the file is inside the folder (or its sub-folders)."""
    return Path(file).resolve().is_relative_to(Path(folder).resolve())
