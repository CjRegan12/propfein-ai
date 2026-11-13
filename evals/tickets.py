"""Ticket eval: do parlays hit as often as the app says they will?

A 13% ticket should lose most nights, so the hit rate alone says little.
The fair test is expected wins vs actual wins:

    expected wins = sum of the stated chances
    z = (actual - expected) / sqrt(sum of p * (1 - p))

z between -2 and +2: consistent with the stated chances (could be luck).
z below -2: the tickets win less than claimed (overconfident).
z above +2: they win more than claimed.

ROI is one unit a ticket at the payout the app showed. For same-game cards
that payout is the book's likely price, an estimate, so treat ROI as rough.

Run it:
    python -m evals.tickets
    python -m evals.tickets --sport nfl --since 2026-11-07
"""

import argparse
from math import sqrt


def ticket_summary(tickets: list[dict]) -> dict:
    """Headline numbers for a set of settled tickets."""
    n = len(tickets)
    if n == 0:
        return {"n": 0, "stated": 0.0, "hit_rate": 0.0, "expected": 0.0,
                "wins": 0, "z": 0.0, "roi": 0.0, "legs": 0.0}
    expected = sum(t["prob"] for t in tickets)
    wins = sum(bool(t["won"]) for t in tickets)
    spread = sqrt(sum(t["prob"] * (1 - t["prob"]) for t in tickets))
    profit = sum((t["dec"] - 1) if t["won"] else -1 for t in tickets)
    return {
        "n": n,
        "stated": expected / n,
        "hit_rate": wins / n,
        "expected": expected,
        "wins": wins,
        "z": (wins - expected) / spread if spread else 0.0,
        "roi": profit / n,
        "legs": sum(t["legs"] for t in tickets) / n,
    }


def tickets_by(tickets: list[dict], field: str = "tier") -> list[dict]:
    """ticket_summary per group, biggest group first."""
    from propfein_ai.grouping import group_by

    return [{"group": g, **ticket_summary(rows)} for g, rows in group_by(tickets, field).items()]


def verdict(s: dict, min_n: int) -> str:
    if s["n"] < min_n:
        return "too few"
    if s["z"] <= -2:
        return "wins LESS than claimed"
    if s["z"] >= 2:
        return "wins more than claimed"
    return "as claimed"


def print_tickets(rows: list[dict], title: str, min_n: int) -> None:
    print(f"\n{title}\n")
    print(f"{'Tier':<18}  {'Tickets':>7}  {'Legs':>4}  {'Says':>6}  {'Hits':>6}  {'Exp W':>6}  {'Won':>4}  {'z':>5}  {'ROI':>7}  Verdict")
    print("-" * 96)
    for r in rows:
        print(
            f"{r['group'][:18]:<18}  {r['n']:>7,}  {r['legs']:>4.1f}  {r['stated'] * 100:>5.1f}%  "
            f"{r['hit_rate'] * 100:>5.1f}%  {r['expected']:>6.1f}  {r['wins']:>4}  {r['z']:>+5.1f}  "
            f"{r['roi'] * 100:>+6.1f}%  {verdict(r, min_n)}"
        )
    print("\nExp W = wins the stated chances add up to. |z| under 2 = consistent with the claim.")
    print("ROI uses the payout the app showed (an estimate on same-game cards).\n")


def main() -> None:
    from propfein_ai.data import SPORTS, fetch_settled_tickets
    from propfein_ai.filters import since

    parser = argparse.ArgumentParser(description="Propfein ticket (parlay) eval")
    parser.add_argument("--sport", choices=sorted(SPORTS), help="one sport (default: all)")
    parser.add_argument("--by", default="tier", choices=("tier", "sport", "legs"))
    parser.add_argument("--since", help="only tickets made on or after this date, YYYY-MM-DD")
    parser.add_argument("--min-n", type=int, default=20, help="fewer tickets than this = too few")
    args = parser.parse_args()

    tickets = since(fetch_settled_tickets(args.sport), args.since)
    label = (args.sport or "all sports").upper()
    print_tickets(tickets_by(tickets, args.by), f"Tickets by {args.by}: {label}", args.min_n)
    print_tickets([{"group": "ALL", **ticket_summary(tickets)}], "All tickets together", args.min_n)


if __name__ == "__main__":
    main()
