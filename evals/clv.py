"""Closing line value (CLV) eval: did the app's picks get a better price than the close?

CLV per pick = your price / closing price - 1.
  +0.03 means you got a price 3% better than where the market closed.
Beating the close consistently is the best long-run sign a pick had real edge,
because the closing line is the market's sharpest estimate.

Two kinds of CLV are reported separately and never mixed:
  price: the line didn't move, so it's a straight price comparison (trustworthy)
  line:  the line moved, so the close was translated to your line by the
         model (useful, but only as good as the model doing the translating)

Run it:
    python -m evals.clv --sport nfl
    python -m evals.clv --sport nfl --by source
"""

import argparse
from statistics import median

BASES = ("price", "line")


def clv_summary(values: list[float]) -> dict:
    """Headline numbers for a list of CLV values.

    mean:      average CLV (the main number)
    median:    middle CLV (less swayed by a few huge moves)
    beat_rate: share of picks that beat the close (CLV > 0)
    flat_rate: share that closed at exactly your price (CLV == 0)
    """
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": 0.0, "median": 0.0, "beat_rate": 0.0, "flat_rate": 0.0}
    return {
        "n": n,
        "mean": sum(values) / n,
        "median": median(values),
        "beat_rate": sum(v > 0 for v in values) / n,
        "flat_rate": sum(v == 0 for v in values) / n,
    }


def clv_by_basis(picks: list[dict]) -> dict[str, dict]:
    """clv_summary for each basis. Picks without a final close are skipped."""
    return {
        basis: clv_summary([p["clv"] for p in picks if p.get("clv_basis") == basis and p.get("clv") is not None])
        for basis in BASES
    }


def clv_split(picks: list[dict], field: str, basis: str = "price") -> list[dict]:
    """clv_summary for one basis, per group, biggest group first."""
    from propfein_ai.grouping import group_by

    scored = [p for p in picks if p.get("clv_basis") == basis and p.get("clv") is not None]
    return [{"group": g, **clv_summary([p["clv"] for p in rows])} for g, rows in group_by(scored, field).items()]


def _row(label: str, s: dict, flag: str = "") -> str:
    return (
        f"{label[:24]:<24}  {s['n']:>6,}  {s['mean'] * 100:>+6.2f}%  {s['median'] * 100:>+6.2f}%  "
        f"{s['beat_rate'] * 100:>5.1f}%  {s['flat_rate'] * 100:>5.1f}%{flag}"
    )


HEADER = f"{'':<24}  {'Picks':>6}  {'Mean':>7}  {'Median':>7}  {'Beat':>6}  {'Flat':>6}"


def main() -> None:
    from propfein_ai.data import SPORTS, fetch_settled_singles
    from propfein_ai.grouping import GROUP_FIELDS

    parser = argparse.ArgumentParser(description="Propfein CLV eval")
    parser.add_argument("--sport", default="nfl", choices=sorted(SPORTS))
    parser.add_argument("--by", choices=GROUP_FIELDS, help="split price-basis CLV by this field")
    parser.add_argument("--min-n", type=int, default=30)
    parser.add_argument("--since", help="only picks made on or after this date, YYYY-MM-DD")
    args = parser.parse_args()

    from propfein_ai.filters import since

    picks = since(fetch_settled_singles(args.sport), args.since)
    unscored = sum(p.get("clv") is None for p in picks)

    print(f"\nCLV: {args.sport.upper()}  ({len(picks):,} settled picks, {unscored:,} without a final close)\n")
    print(HEADER)
    print("-" * 66)
    for basis, s in clv_by_basis(picks).items():
        note = "  (model-translated)" if basis == "line" else ""
        print(_row(f"{basis} basis", s, note))

    if args.by:
        print(f"\nPrice-basis CLV by {args.by}\n")
        print(HEADER)
        print("-" * 66)
        for r in clv_split(picks, args.by):
            print(_row(r["group"], r, "" if r["n"] >= args.min_n else "  (small sample)"))

    print("\nMean > 0 means the picks beat the closing price on average.\n")


if __name__ == "__main__":
    main()
