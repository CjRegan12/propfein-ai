"""Calibration eval: when the app says 65%, does it hit about 65%?

How it works:
  1. Load every settled single pick for a sport (probability shown + result).
  2. Group picks into 5% buckets by the probability the app showed.
  3. For each bucket, compare the average stated probability to the actual hit rate.
  4. Boil it down to one number: expected calibration error (ECE).

Run it:
    python -m evals.calibration --sport nfl

Check your work:
    python -m pytest
"""

import argparse
import json
from datetime import date
from pathlib import Path

BUCKET_WIDTH = 0.05


# ---------------------------------------------------------------------------
# TODO 1: bucket_for
# ---------------------------------------------------------------------------
def bucket_for(prob: float, width: float = BUCKET_WIDTH) -> float:
    """Return the lower edge of the bucket a probability falls in.

    Examples (width 0.05):
        0.534 -> 0.50
        0.55  -> 0.55
        0.049 -> 0.0
        1.0   -> 0.95   (a 100% pick goes in the top bucket, not a new one)

    Hints:
      - math.floor(prob / width) tells you which bucket number it's in.
      - Multiply back by width to get the edge.
      - Computers store decimals imperfectly. Try this in Python:
        0.15 / 0.05 gives 2.9999999999999996, not 3, so floor() would
        drop a 15% pick into the 10% bucket. Rounding prob / width to
        ~9 decimal places BEFORE flooring fixes it.
      - Round the final edge to 2 decimal places too (0.55 vs 0.5500000000000001).
      - Handle prob == 1.0 so it doesn't create a 1.00 bucket.
    """
    raise NotImplementedError("TODO 1: write bucket_for")


# ---------------------------------------------------------------------------
# TODO 2: calibration_table
# ---------------------------------------------------------------------------
def calibration_table(picks: list[dict], width: float = BUCKET_WIDTH) -> list[dict]:
    """Group picks by bucket and compare stated probability to reality.

    Each pick looks like: {"key": "...", "prob": 0.534, "won": True}

    Return one dict per bucket that has at least one pick, sorted by bucket:
        {
            "bucket":   0.50,   # lower edge from bucket_for
            "n":        3,      # number of picks in the bucket
            "stated":   0.52,   # average of the probabilities the app showed
            "hit_rate": 0.333,  # wins / n
            "gap":      -0.187, # hit_rate - stated (negative = overconfident)
        }

    Hints:
      - A dict of lists works well: {bucket: [pick, pick, ...]}.
        dict.setdefault(key, []) or collections.defaultdict(list) both help.
      - True counts as 1 and False as 0, so sum(p["won"] for p in group)
        counts the wins.
      - sorted(your_dict) gives the buckets in order.
    """
    raise NotImplementedError("TODO 2: write calibration_table")


# ---------------------------------------------------------------------------
# TODO 3: expected_calibration_error
# ---------------------------------------------------------------------------
def expected_calibration_error(table: list[dict]) -> float:
    """One-number summary: the average size of the gap, weighted by pick count.

    ECE = sum over buckets of (n / total_n) * abs(gap)

    0.0 means perfectly calibrated. 0.03 means the app is off by
    about 3 percentage points on a typical pick.

    Why weighted: a bucket with 3,000 picks matters far more than one with 7.
    Return 0.0 if the table is empty.
    """
    raise NotImplementedError("TODO 3: write expected_calibration_error")


# ---------------------------------------------------------------------------
# Runner (already done): loads data, prints the report, saves results
# ---------------------------------------------------------------------------
def print_report(sport: str, table: list[dict], ece: float, min_n: int) -> None:
    total = sum(row["n"] for row in table)
    print(f"\nCalibration: {sport.upper()}  ({total:,} settled single picks)\n")
    print(f"{'Bucket':>9}  {'Picks':>6}  {'Says':>6}  {'Hits':>6}  {'Gap':>7}")
    print("-" * 42)
    for row in table:
        low = row["bucket"] * 100
        label = f"{low:.0f}-{low + BUCKET_WIDTH * 100:.0f}%"
        flag = "" if row["n"] >= min_n else "  (small sample)"
        print(
            f"{label:>9}  {row['n']:>6,}  "
            f"{row['stated'] * 100:>5.1f}%  {row['hit_rate'] * 100:>5.1f}%  "
            f"{row['gap'] * 100:>+6.1f}{flag}"
        )
    print(f"\nExpected calibration error: {ece * 100:.2f} points\n")


def save_results(sport: str, table: list[dict], ece: float) -> Path:
    out = Path("results") / f"calibration_{sport}_{date.today()}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"sport": sport, "ece": ece, "buckets": table}, indent=2))
    return out


def main() -> None:
    from propfein_ai.data import SPORTS, fetch_settled_singles

    parser = argparse.ArgumentParser(description="Propfein calibration eval")
    parser.add_argument("--sport", default="nfl", choices=sorted(SPORTS))
    parser.add_argument(
        "--min-n", type=int, default=30, help="flag buckets with fewer picks than this"
    )
    args = parser.parse_args()

    picks = fetch_settled_singles(args.sport)
    table = calibration_table(picks)
    ece = expected_calibration_error(table)
    print_report(args.sport, table, ece, args.min_n)
    print(f"Saved: {save_results(args.sport, table, ece)}")


if __name__ == "__main__":
    main()
