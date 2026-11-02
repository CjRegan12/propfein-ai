"""Tests for the calibration eval. No database needed.

Run: python -m pytest
Every test starts failing. Your job is to make them all pass.
"""

import pytest

from evals.calibration import bucket_for, calibration_table, expected_calibration_error


# --- TODO 1: bucket_for -----------------------------------------------------

@pytest.mark.parametrize(
    "prob, expected",
    [
        (0.534, 0.50),
        (0.50, 0.50),
        (0.55, 0.55),   # exactly on an edge belongs to the higher bucket
        (0.5499, 0.50),
        (0.15, 0.15),   # trap: in Python, 0.15 / 0.05 == 2.9999999999999996
        (0.35, 0.35),   # same trap: 0.35 / 0.05 == 6.999999999999999
        (0.049, 0.0),
        (0.0, 0.0),
        (0.97, 0.95),
        (1.0, 0.95),    # a 100% pick goes in the top bucket
    ],
)
def test_bucket_for(prob, expected):
    assert bucket_for(prob) == expected


def test_bucket_for_custom_width():
    assert bucket_for(0.534, width=0.10) == 0.50
    assert bucket_for(0.67, width=0.10) == 0.60


# --- TODO 2: calibration_table ----------------------------------------------

def pick(prob, won):
    return {"key": f"{prob}-{won}", "prob": prob, "won": won}


def test_calibration_table_groups_and_sorts():
    picks = [
        pick(0.62, True),
        pick(0.51, True),
        pick(0.53, False),
        pick(0.52, False),
    ]
    table = calibration_table(picks)

    assert [row["bucket"] for row in table] == [0.50, 0.60]

    fifty = table[0]
    assert fifty["n"] == 3
    assert fifty["stated"] == pytest.approx(0.52)
    assert fifty["hit_rate"] == pytest.approx(1 / 3)
    assert fifty["gap"] == pytest.approx(1 / 3 - 0.52)

    sixty = table[1]
    assert sixty["n"] == 1
    assert sixty["hit_rate"] == pytest.approx(1.0)
    assert sixty["gap"] == pytest.approx(1.0 - 0.62)


def test_calibration_table_empty():
    assert calibration_table([]) == []


# --- TODO 3: expected_calibration_error -------------------------------------

def test_ece_is_weighted_by_pick_count():
    table = [
        {"bucket": 0.50, "n": 90, "stated": 0.52, "hit_rate": 0.50, "gap": -0.02},
        {"bucket": 0.60, "n": 10, "stated": 0.62, "hit_rate": 0.72, "gap": 0.10},
    ]
    # 0.9 * 0.02 + 0.1 * 0.10 = 0.028
    assert expected_calibration_error(table) == pytest.approx(0.028)


def test_ece_perfect_and_empty():
    perfect = [{"bucket": 0.5, "n": 4, "stated": 0.5, "hit_rate": 0.5, "gap": 0.0}]
    assert expected_calibration_error(perfect) == 0.0
    assert expected_calibration_error([]) == 0.0
