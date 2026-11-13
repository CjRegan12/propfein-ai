"""Tests for the ticket (parlay) eval. No database needed."""

from math import sqrt

import pytest

from evals.tickets import ticket_summary, tickets_by, verdict


def t(prob, won, dec, tier="cash", legs=2):
    return {"prob": prob, "won": won, "dec": dec, "tier": tier, "legs": legs}


def test_expected_vs_actual_wins():
    s = ticket_summary([t(0.2, True, 5.0), t(0.2, False, 5.0), t(0.4, False, 2.5)])
    assert s["n"] == 3
    assert s["expected"] == pytest.approx(0.8)
    assert s["wins"] == 1
    assert s["z"] == pytest.approx((1 - 0.8) / sqrt(0.16 + 0.16 + 0.24))
    # one win paying 4 units profit, two losses: (4 - 2) / 3
    assert s["roi"] == pytest.approx(2 / 3)


def test_empty_and_certain():
    assert ticket_summary([])["n"] == 0
    # spread is 0 when every chance is 0 or 1: z must not divide by zero
    assert ticket_summary([t(1.0, True, 1.01)])["z"] == 0.0


def test_tickets_by_tier_biggest_first():
    rows = tickets_by([t(0.3, True, 3, "cash"), t(0.3, False, 3, "cash"), t(0.1, False, 9, "script")])
    assert [r["group"] for r in rows] == ["cash", "script"]
    assert rows[0]["n"] == 2


def test_verdict_bands():
    assert verdict({"n": 5, "z": -3}, 20) == "too few"
    assert verdict({"n": 50, "z": -2.5}, 20) == "wins LESS than claimed"
    assert verdict({"n": 50, "z": 2.1}, 20) == "wins more than claimed"
    assert verdict({"n": 50, "z": 0.4}, 20) == "as claimed"
