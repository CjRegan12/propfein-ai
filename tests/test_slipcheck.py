"""Tests for the slip-check eval. No database needed."""

from evals.slipcheck import BIG_EDGE, slipcheck_report, tag, verdict


def pick(i, prob, won, ev=0.0, market="player_rush_yds"):
    return {"event": f"e{i}", "player": f"p{i}", "market": market, "side": "over", "prob": prob, "won": won, "ev": ev}


def test_tag_rules():
    assert tag(pick(1, 0.5, True, ev=BIG_EDGE)) == "shaky"
    assert tag(pick(1, 0.5, True, ev=BIG_EDGE - 0.001)) == "solid"
    assert tag(pick(1, 0.5, True, ev=None)) == "solid"
    assert tag(pick(1, 0.5, True, ev=0.3, market="player_anytime_td")) == "unmeasured"
    assert tag(pick(1, 0.5, True, ev=0.3, market="player_rush_yds_alternate")) == "shaky"


def test_report_counts_per_bet():
    # two lines of one player's ladder are one bet
    picks = [pick(1, 0.6, True), {**pick(1, 0.5, True)}, pick(2, 0.4, False), pick(3, 0.3, False, ev=0.2)]
    r = slipcheck_report(picks)
    assert r["solid"]["n"] == 2
    assert r["shaky"]["n"] == 1
    assert r["unmeasured"]["n"] == 0


def test_verdict_says_too_few_before_anything_else():
    picks = [pick(i, 0.3, False, ev=0.2) for i in range(6)] + [pick(100 + i, 0.5, i % 2 == 0) for i in range(400)]
    assert verdict(slipcheck_report(picks)) == "too few Shaky bets to say (6; need 100)"


def test_verdict_pass_fail_and_unclear():
    solid = [pick(1000 + i, 0.5, i % 2 == 0) for i in range(400)]            # hits 50%, says 50%
    shaky_low = [pick(i, 0.30, i % 10 == 0, ev=0.2) for i in range(200)]     # says 30%, hits 10%
    shaky_fine = [pick(i, 0.30, i % 10 < 3, ev=0.2) for i in range(200)]     # says 30%, hits 30%
    solid_off = [pick(1000 + i, 0.5, i % 5 == 0) for i in range(400)]        # says 50%, hits 20%
    assert verdict(slipcheck_report(shaky_low + solid)).startswith("PASS")
    assert verdict(slipcheck_report(shaky_fine + solid)).startswith("FAIL")
    assert verdict(slipcheck_report(shaky_low + solid_off)).startswith("UNCLEAR")
