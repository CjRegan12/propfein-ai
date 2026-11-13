"""Tests for grouping, calibration splits and the CLV eval. No database needed."""

import pytest

from evals.calibration import calibration_by, summarize
from evals.clv import clv_by_basis, clv_split, clv_summary
from propfein_ai.grouping import group_by


def pick(prob, won, **extra):
    return {"key": f"{prob}-{won}-{extra}", "prob": prob, "won": won, **extra}


# --- grouping -------------------------------------------------------------

def test_group_by_biggest_first_then_name():
    rows = [{"side": "under"}, {"side": "over"}, {"side": "over"}, {"side": "team"}]
    groups = group_by(rows, "side")
    assert list(groups) == ["over", "team", "under"]
    assert len(groups["over"]) == 2


def test_group_by_missing_field():
    assert list(group_by([{}], "side")) == ["unknown"]


# --- calibration splits ---------------------------------------------------

def test_summarize_bias_is_signed():
    picks = [pick(0.6, False), pick(0.6, True), pick(0.6, False), pick(0.6, False)]
    s = summarize(picks)
    assert s["n"] == 4
    assert s["stated"] == pytest.approx(0.6)
    assert s["hit_rate"] == pytest.approx(0.25)
    assert s["bias"] == pytest.approx(-0.35)   # overconfident
    assert s["ece"] == pytest.approx(0.35)


def test_summarize_empty():
    assert summarize([])["n"] == 0


def test_calibration_by_splits_groups():
    picks = [
        pick(0.5, True, side="over"),
        pick(0.5, True, side="over"),
        pick(0.5, False, side="under"),
    ]
    rows = calibration_by(picks, "side")
    assert [r["group"] for r in rows] == ["over", "under"]
    assert rows[0]["hit_rate"] == pytest.approx(1.0)
    assert rows[1]["bias"] == pytest.approx(-0.5)


# --- CLV ------------------------------------------------------------------

def test_clv_summary():
    s = clv_summary([0.02, -0.01, 0.0, 0.05])
    assert s["n"] == 4
    assert s["mean"] == pytest.approx(0.015)
    assert s["median"] == pytest.approx(0.01)
    assert s["beat_rate"] == pytest.approx(0.5)
    assert s["flat_rate"] == pytest.approx(0.25)


def test_clv_summary_empty():
    assert clv_summary([]) == {"n": 0, "mean": 0.0, "median": 0.0, "beat_rate": 0.0, "flat_rate": 0.0}


def test_clv_by_basis_never_mixes_and_skips_unscored():
    picks = [
        pick(0.5, True, clv=0.02, clv_basis="price"),
        pick(0.5, True, clv=0.30, clv_basis="line"),
        pick(0.5, True, clv=None, clv_basis=None),
    ]
    out = clv_by_basis(picks)
    assert out["price"]["n"] == 1 and out["price"]["mean"] == pytest.approx(0.02)
    assert out["line"]["n"] == 1 and out["line"]["mean"] == pytest.approx(0.30)


def test_clv_split_uses_price_basis_only():
    picks = [
        pick(0.5, True, clv=0.04, clv_basis="price", source="usage"),
        pick(0.5, True, clv=-0.02, clv_basis="price", source="card"),
        pick(0.5, True, clv=0.90, clv_basis="line", source="usage"),
    ]
    rows = {r["group"]: r for r in clv_split(picks, "source")}
    assert rows["usage"]["n"] == 1 and rows["usage"]["mean"] == pytest.approx(0.04)
    assert rows["card"]["mean"] == pytest.approx(-0.02)
