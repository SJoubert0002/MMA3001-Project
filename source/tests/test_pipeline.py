"""Tests of the preprocessing and analysis functions, on small synthetic data.

Run from the project root:  python -m pytest source/tests
The tests never write into data/ or test/; they use pytest's temporary folders.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from source.analysis.choose_output import choose_output
from source.analysis.config import MODEL_HEADINGS, SLOT_MINUTES
from source.analysis.describe_answer import describe_answer
from source.analysis.evaluate_model import evaluate_model
from source.analysis.fit_svr import fit_svr
from source.analysis.get_headcount import get_headcount
from source.analysis.make_model import make_model
from source.analysis.model_error import model_error
from source.analysis.predict_svr import predict_svr
from source.analysis.read_semester_calendar import read_semester_calendar
from source.analysis.read_time import read_time
from source.analysis.slot_means import slot_means
from source.preprocessing.check_headings import check_headings
from source.preprocessing.config import DATA_DIR, TEST_DIR


def synthetic_readings(dates):
    """Readings every minute from 09:00 to 17:00 on the given dates, peaking at 13:00."""
    times, counts = [], []
    for date in dates:
        minutes = pd.date_range(f"{date} 09:00", f"{date} 17:00", freq="min", tz="Australia/Melbourne")
        times.extend(minutes)
        counts.extend(10 - np.abs((minutes.hour + minutes.minute / 60) - 13) * 2)
    return pd.Series(times), pd.Series(counts)


MONDAYS = ["2024-03-04", "2024-03-11", "2024-03-18", "2024-03-25"]


def test_check_headings_is_strict(tmp_path):
    good, bad = tmp_path / "good.csv", tmp_path / "bad.csv"
    good.write_text("a,b\n1,2\n")
    bad.write_text("b,a\n1,2\n")
    check_headings(good, ["a", "b"])
    with pytest.raises(ValueError):
        check_headings(bad, ["a", "b"])


def test_read_time_accepts_only_the_exact_format():
    assert read_time("2025-04-09 14:00").hour == 14
    for text in ["2025-04-09T14:00", "09/04/2025 14:00", "2025-02-30 10:00", "", "2025-04-06 02:30"]:
        with pytest.raises(ValueError):
            read_time(text)


def test_slot_means_average_into_slots():
    times, counts = synthetic_readings(MONDAYS[:1])
    slots = slot_means(times, counts)
    assert slots.hour.iloc[0] == 9.0 and len(slots) == 8 * 60 // SLOT_MINUTES + 1


def test_make_model_headings_dates_and_error():
    times, counts = synthetic_readings(MONDAYS)
    model = make_model(times, counts)
    assert list(model.columns) == MODEL_HEADINGS
    assert set(model.weekday) == {0} and (model.dates == 4).all() and (model.cv_mae >= 0).all()
    assert model_error(model, 0)[1] == 4
    assert model_error(model, 3) is None


def test_weekday_with_too_few_dates_gets_no_model():
    times, counts = synthetic_readings(MONDAYS[:2])
    assert make_model(times, counts).empty


def test_saved_model_matches_scikit_learn():
    times, counts = synthetic_readings(MONDAYS)
    model = make_model(times, counts)
    slots = slot_means(times, counts)
    fitted = fit_svr(slots.hour, slots.headcount)
    for hour in (9.5, 13.0, 16.25):
        moment = pd.Timestamp("2024-03-04", tz="Australia/Melbourne") + pd.Timedelta(hours=hour)
        expected = float(predict_svr(fitted, np.array([hour]))[0])
        assert evaluate_model(model, moment) == pytest.approx(expected, abs=1e-6)


def test_evaluate_model_rejects_wrong_headings():
    with pytest.raises(ValueError):
        evaluate_model(pd.DataFrame({"weekday": [0]}), read_time("2024-03-04 12:00"))


def test_choose_output_routes_by_input_location(tmp_path):
    assert choose_output()["mode"] == "saved"
    inside_data = choose_output(DATA_DIR / "new.csv")
    assert inside_data["mode"] == "data" and inside_data["models_folder"].parts[-2:] == ("data", "models")
    inside_test = choose_output(TEST_DIR / "mine.csv")
    assert inside_test["mode"] == "test" and TEST_DIR in inside_test["models_folder"].parents
    elsewhere = choose_output(tmp_path / "other.csv")
    assert elsewhere["mode"] == "other" and elsewhere["models_folder"] is None


def test_get_headcount_from_saved_models_reports_its_error():
    calendar = read_semester_calendar([DATA_DIR])
    details = {}
    value = get_headcount("G.20", "2025-04-09 14:07", calendar, details=details)
    assert value == pytest.approx(2.8, abs=0.1)
    assert details["period"] == "semester_1" and details["dates"] >= 3 and details["cv_mae"] > 0
    text = describe_answer("G.20", "2025-04-09 14:07", value, details)
    assert "typically within" in text and details["model_file"] in text


def test_get_headcount_errors_are_loud():
    calendar = read_semester_calendar([DATA_DIR])
    with pytest.raises(ValueError):
        get_headcount("G.20", "2099-04-09 14:00", calendar)
    with pytest.raises(ValueError):
        get_headcount("Nowhere", "2025-04-09 14:00", calendar)
