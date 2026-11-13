"""Slip-check eval: do the app's "Shaky" legs really hit less than their number says?

The app's Check my slip feature tags a leg Shaky when its price looks 7% or
more better than fair. A backtest on three NFL seasons found legs like that
hit about 5 points under their stated chance, and legs with no flag hit as
stated. This eval checks the same claim on the live record, where nobody
could have tuned anything:

    python -m evals.slipcheck --sport nfl

Pass signal: Shaky bets hit clearly under their stated chance (bias below
zero, past noise) while Solid bets stay inside noise.

Counted per bet, like the calibration eval. With few Shaky bets on the record
the honest answer is "too few to say", and the eval says so.
"""

import argparse

from evals.calibration import summarize
from propfein_ai.filters import per_bet, since

# Same threshold and markets as the app (its lib/slipcheck.mjs) and the backtest that set them.
BIG_EDGE = 0.07
MEASURED_MARKETS = {
    "player_pass_yds", "player_rush_yds", "player_reception_yds", "player_receptions",
    "player_pass_tds", "h2h", "spreads", "totals",
}
MIN_BETS = 100  # fewer bets than this in a group proves nothing either way


def tag(pick: dict) -> str:
    """The tag the app would give a settled pick: "shaky", "solid" or "unmeasured"."""
    market = str(pick.get("market", "")).removesuffix("_alternate")
    if market not in MEASURED_MARKETS:
        return "unmeasured"
    ev = pick.get("ev")
    if ev is not None and ev >= BIG_EDGE:
        return "shaky"
    return "solid"


def slipcheck_report(picks: list[dict]) -> dict:
    """Calibration of each tag, counted per bet. {"shaky": summary, "solid": summary, "unmeasured": summary}"""
    groups: dict[str, list[dict]] = {"shaky": [], "solid": [], "unmeasured": []}
    for p in picks:
        groups[tag(p)].append(p)
    return {name: summarize(per_bet(rows)) for name, rows in groups.items()}


def verdict(report: dict, min_bets: int = MIN_BETS) -> str:
    """One line on whether the live record backs the Shaky tag."""
    shaky, solid = report["shaky"], report["solid"]
    if shaky["n"] < min_bets:
        return f"too few Shaky bets to say ({shaky['n']}; need {min_bets})"
    shaky_low = shaky["bias"] < 0 and abs(shaky["bias"]) > shaky["noise"]
    solid_ok = solid["n"] >= min_bets and abs(solid["bias"]) <= solid["noise"]
    if shaky_low and solid_ok:
        return "PASS: Shaky bets hit under their number, Solid bets hit as stated"
    if not shaky_low:
        return "FAIL: Shaky bets do not hit clearly under their number"
    return "UNCLEAR: Shaky bets hit low, but Solid bets are off too"


def main() -> None:
    from propfein_ai.data import SPORTS, fetch_settled_singles

    parser = argparse.ArgumentParser(description="Slip-check eval: do Shaky legs hit less than stated?")
    parser.add_argument("--sport", default="nfl", choices=list(SPORTS))
    parser.add_argument("--since", help="only picks made on or after this date, YYYY-MM-DD")
    args = parser.parse_args()

    report = slipcheck_report(since(fetch_settled_singles(args.sport), args.since))
    print(f"\nSlip-check eval, {args.sport.upper()}{f' since {args.since}' if args.since else ''} (per bet)\n")
    print(f"{'Tag':<11}  {'Bets':>6}  {'Says':>6}  {'Hits':>6}  {'Bias':>6}  {'Noise':>6}")
    print("-" * 51)
    for name in ("solid", "shaky", "unmeasured"):
        s = report[name]
        if not s["n"]:
            print(f"{name:<11}  {0:>6}")
            continue
        print(f"{name:<11}  {s['n']:>6,}  {s['stated'] * 100:>5.1f}%  {s['hit_rate'] * 100:>5.1f}%  "
              f"{s['bias'] * 100:>+5.1f}  {s['noise'] * 100:>5.1f}")
    print(f"\n{verdict(report)}\n")


if __name__ == "__main__":
    main()
