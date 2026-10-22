"""Shared helper for the investigation scripts.

load_notebook_functions() runs the function cells of the archived notebook (archive/notebooks/pre-Processing_final_notebook.ipynb) (skipping the
pop-up, the run cell and the plots) and returns their namespace, so an investigation uses
exactly the same reading, period-labelling and calendar code as the notebook.
Run the scripts from the project root: python archive\\investigations\\<folder>\\run.py
"""
import json
from pathlib import Path

ROOMS = {"cca1ac3e-f81f-4ebb-aa2b-8b0bf3e9e53b": "G.20", "227f1068-9e41-469f-bef0-275f27a0bdba": "G.25"}


NOTEBOOK = Path(__file__).resolve().parents[1] / "notebooks" / "pre-Processing_final_notebook.ipynb"


def load_notebook_functions(notebook=NOTEBOOK):
    cells = ["".join(c["source"]) for c in json.load(open(notebook, encoding="utf-8"))["cells"] if c["cell_type"] == "code"]
    names = {}
    for code in cells:
        if "split_by_room(occupancy_file" in code or "ask_files()" in code or "plt." in code:
            continue
        if "build_models(floorspace_id" in code and "def " not in code:
            continue
        try:
            exec(code, names)
        except Exception:
            pass
    # The archived notebook assumed the old layout; point it at the current data folder.
    root = Path(__file__).resolve().parents[2]
    names["DATA_DIR"] = root / "data"
    names["OUTPUT_DIR"] = root / "data" / "derived" / "preprocessed"
    names["calendar"] = names["read_semester_calendar"]([names["DATA_DIR"]])
    return names
