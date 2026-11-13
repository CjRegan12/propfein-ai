"""Shaping picks before an eval: date cut-offs and one bet per player-game.

Why per-bet matters: the record saves several lines for the same player in
the same game (rush over 34.5, 35.5, 37.5 ...). Those win or lose together,
so counting them separately makes a result look far more certain than it is.
per_bet() collapses each (game, player, market, side) into one bet whose
chance and result are the averages of its lines.
"""

from datetime import date, datetime


def since(picks: list[dict], start: str | None) -> list[dict]:
    """Keep picks made on or after start (YYYY-MM-DD). None keeps everything."""
    if not start:
        return picks
    cut = date.fromisoformat(start)

    def day(p):
        at = p.get("at")
        if isinstance(at, datetime):
            return at.date()
        return date.fromisoformat(str(at)[:10])

    return [p for p in picks if day(p) >= cut]


def per_bet(picks: list[dict]) -> list[dict]:
    """One row per game, player, market and side, averaged over its lines."""
    groups: dict[tuple, list[dict]] = {}
    for p in picks:
        k = (p.get("event"), p.get("player"), p.get("market"), p.get("side"))
        groups.setdefault(k, []).append(p)

    out = []
    for rows in groups.values():
        first = rows[0]
        n = len(rows)
        out.append({
            **first,
            "prob": sum(r["prob"] for r in rows) / n,
            "won": sum(r["won"] for r in rows) / n,
            "lines": n,
        })
    return out
