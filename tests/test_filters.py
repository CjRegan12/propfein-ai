"""Tests for the date filter and the one-bet-per-player-game count."""

from datetime import datetime, timezone

import pytest

from evals.calibration import summarize
from propfein_ai.filters import per_bet, since


def row(event, player, prob, won, side="over", market="player_rush_yds", at="2026-11-08T18:00:00+00:00"):
    return {"event": event, "player": player, "market": market, "side": side,
            "prob": prob, "won": won, "at": at}


def test_per_bet_collapses_ladder_rungs():
    picks = [
        row("g1", "Daniels", 0.60, False),
        row("g1", "Daniels", 0.55, False),
        row("g1", "Daniels", 0.50, True),
        row("g1", "Daniels", 0.45, False, side="under"),
        row("g2", "Daniels", 0.52, True),
    ]
    bets = per_bet(picks)
    assert len(bets) == 3
    g1_over = next(b for b in bets if b["event"] == "g1" and b["side"] == "over")
    assert g1_over["lines"] == 3
    assert g1_over["prob"] == pytest.approx(0.55)
    assert g1_over["won"] == pytest.approx(1 / 3)


def test_since_accepts_strings_and_datetimes():
    picks = [
        row("a", "x", 0.5, True, at="2026-11-06T23:59:00+00:00"),
        row("b", "x", 0.5, True, at=datetime(2026, 11, 7, 1, tzinfo=timezone.utc)),
    ]
    assert [p["event"] for p in since(picks, "2026-11-07")] == ["b"]
    assert since(picks, None) == picks


def test_noise_shrinks_with_more_bets():
    small = summarize([row(str(i), "x", 0.5, i % 2 == 0) for i in range(25)])
    big = summarize([row(str(i), "x", 0.5, i % 2 == 0) for i in range(2500)])
    assert small["noise"] == pytest.approx(0.2)
    assert big["noise"] == pytest.approx(0.02)
