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
from propfein_ai.filters import per_bet, since


def score_sport(sport: str, start: str | None = None) -> dict:
    picks = since(fetch_settled_singles(sport), start)
    # calibration counts each player-game once (honest noise); CLV is per line
    return {"sport": sport, "calibration": summarize(per_bet(picks)), "clv": clv_by_basis(picks)}


def print_scoreboard(rows: list[dict], start: str | None) -> None:
    print(f"\nPropfein eval scoreboard{f' (since {start})' if start else ''}\n")
    print(f"{'Sport':<6}  {'Bets':>6}  {'Says':>6}  {'Hits':>6}  {'Bias':>6}  {'Noise':>6}  {'ECE':>5}  {'CLV price':>9}  {'CLV line':>9}")
    print("-" * 78)
    for r in rows:
        c, p, l = r["calibration"], r["clv"]["price"], r["clv"]["line"]
        print(
            f"{r['sport'].upper():<6}  {c['n']:>6,}  {c['stated'] * 100:>5.1f}%  {c['hit_rate'] * 100:>5.1f}%  "
            f"{c['bias'] * 100:>+5.1f}  {c['noise'] * 100:>5.1f}  {c['ece'] * 100:>5.1f}  "
            f"{p['mean'] * 100:>+8.2f}%  {l['mean'] * 100:>+8.2f}%"
        )
    print("\nBets = one per player-game-side. Bias < 0 = overconfident; inside +/- Noise could be luck.")
    print("CLV line is model-translated: trust its direction, not its size.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all Propfein evals")
    parser.add_argument("--sports", nargs="+", default=list(SPORTS), choices=list(SPORTS))
    parser.add_argument("--since", help="only picks made on or after this date, YYYY-MM-DD")
    args = parser.parse_args()

    rows = [score_sport(s, args.since) for s in args.sports]
    print_scoreboard(rows, args.since)

    from evals.tickets import print_tickets, tickets_by
    from propfein_ai.data import fetch_settled_tickets

    tickets = since(fetch_settled_tickets(), args.since)
    ticket_rows = tickets_by(tickets)
    print_tickets(ticket_rows, "Tickets by tier (all sports)", 20)

    out = Path("results") / f"scoreboard_{date.today()}{f'_since_{args.since}' if args.since else ''}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"singles": rows, "tickets": ticket_rows}, indent=2, default=str))
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
