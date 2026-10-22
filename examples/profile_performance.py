"""Time, profile and memory-measure the three stages of the tool.

Stages: preprocessing the raw export (optional, needs the raw file), building the models of
one room from its preprocessed stream, and answering one query. Each stage is run with
cProfile (top functions by cumulative time), tracemalloc (peak Python-allocated memory) and
the process's peak working set. Everything is written to reports/performance.txt. It uses
temporary folders, so the project's data/models/ folder is untouched.

Run from anywhere:  python examples/profile_performance.py
"""

import cProfile
import io
import pstats
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from source.analysis.build_models import build_models
from source.analysis.get_headcount import get_headcount
from source.analysis.read_semester_calendar import read_semester_calendar
from source.preprocessing.config import DATA_DIR
from source.preprocessing.run_preprocessing import run_preprocessing

RAW_FILE = DATA_DIR / "5occupancySensor_MayToDec2024_9MRows.csv"
STREAMS = DATA_DIR / "derived" / "preprocessed" / "occupancy_streams"
ROOM_ID = "cca1ac3e"  # G.20; matched by prefix below
REPORT = Path(__file__).resolve().parents[1] / "reports" / "performance.txt"
QUERY_REPEATS = 200


def peak_working_set_mb():
    """Return the peak working set of this process in MB (Windows only; None elsewhere)."""
    try:
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]

        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        kernel32, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb)
        return counters.PeakWorkingSetSize / 1e6
    except Exception:
        return None


def measure(name, function, lines):
    """Run function three ways (timed, profiled, memory-traced) and append the findings to lines.

    Input:
        name: the stage's name.
        function: a function with no arguments.
        lines: the list of report lines to extend.
    """
    start = time.perf_counter()
    function()
    seconds = time.perf_counter() - start

    profiler = cProfile.Profile()
    profiler.runcall(function)
    text = io.StringIO()
    pstats.Stats(profiler, stream=text).strip_dirs().sort_stats("cumulative").print_stats(12)

    tracemalloc.start()
    function()
    peak = tracemalloc.get_traced_memory()[1] / 1e6
    tracemalloc.stop()

    lines += [f"== {name} ==", f"wall time: {seconds:.3f} s",
              f"peak Python allocations (tracemalloc): {peak:.1f} MB", "",
              "cProfile, top 12 by cumulative time:", text.getvalue().strip(), ""]


def main():
    """Measure the stages and write reports/performance.txt."""
    calendar = read_semester_calendar([DATA_DIR])
    room = next(path.stem for path in STREAMS.glob("*.csv") if path.stem.startswith(ROOM_ID))
    lines = [f"Python {sys.version.split()[0]}", ""]

    with tempfile.TemporaryDirectory() as models:
        measure("build the models of one room (G.20)", lambda: build_models(room, calendar, STREAMS, Path(models)), lines)
        lines.append(f"models saved for G.20: {len(list(Path(models).rglob('*.csv')))} files")
        lines.append("")
        measure("answer one query (get_headcount, saved model)",
                lambda: [get_headcount("G.20", "2025-04-09 14:00", calendar) for _ in range(QUERY_REPEATS)], lines)
        lines.append(f"(the query stage above runs the query {QUERY_REPEATS} times; divide by {QUERY_REPEATS})")
        lines.append("")

    if RAW_FILE.exists():
        with tempfile.TemporaryDirectory() as out:
            start = time.perf_counter()
            run_preprocessing(str(RAW_FILE), output_folder=out)
            lines += ["== preprocess the raw export ==", f"wall time: {time.perf_counter() - start:.1f} s",
                      f"raw file size: {RAW_FILE.stat().st_size / 1e6:.0f} MB (tracemalloc is not used here: it slows the run)", ""]
    else:
        lines += ["== preprocess the raw export ==", "skipped: the raw file is not in data/", ""]

    working_set = peak_working_set_mb()
    if working_set is not None:
        lines.append(f"peak working set of the whole process: {working_set:.0f} MB")
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
