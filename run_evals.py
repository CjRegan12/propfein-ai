"""Run every eval for every sport and print one scoreboard.

    python run_evals.py
    python run_evals.py --sports nfl nba

Re-run after any change to the model or prompts: this is the regression run.
Results are saved to results/scoreboard_<date>.json so runs can be compared.
"""

import argparse
import json
from datetime import date
from pathlib import Path

from evals.calibration import summarize
from evals.clv import clv_by_basis
from propfein_ai.data import SPORTS, fetch_settled_singles


def score_sport(sport: str) -> dict:
    picks = fetch_settled_singles(sport)
    return {"sport": sport, "calibration": summarize(picks), "clv": clv_by_basis(picks)}


def print_scoreboard(rows: list[dict]) -> None:
    print("\nPropfein eval scoreboard\n")
    print(f"{'Sport':<6}  {'Picks':>6}  {'Says':>6}  {'Hits':>6}  {'Bias':>6}  {'ECE':>5}  {'CLV price':>9}  {'CLV line':>9}")
    print("-" * 70)
    for r in rows:
        c, p, l = r["calibration"], r["clv"]["price"], r["clv"]["line"]
        print(
            f"{r['sport'].upper():<6}  {c['n']:>6,}  {c['stated'] * 100:>5.1f}%  {c['hit_rate'] * 100:>5.1f}%  "
            f"{c['bias'] * 100:>+5.1f}  {c['ece'] * 100:>5.1f}  "
            f"{p['mean'] * 100:>+8.2f}%  {l['mean'] * 100:>+8.2f}%"
        )
    print("\nBias < 0 = overconfident. ECE in points. CLV = average price beat vs the close.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all Propfein evals")
    parser.add_argument("--sports", nargs="+", default=list(SPORTS), choices=list(SPORTS))
    args = parser.parse_args()

    rows = [score_sport(s) for s in args.sports]
    print_scoreboard(rows)

    out = Path("results") / f"scoreboard_{date.today()}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, indent=2))
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
