"""The tools the MCP server offers, as plain functions.

Each takes a PropfeinClient and returns the API's data unchanged. Nothing here
(and nothing in the model that calls these) works out a probability, a hit
rate or a price: every number comes from the API, which gets it from
deterministic code. That is the project's core rule.

Kept free of the MCP SDK on purpose, so these are tested with plain pytest.
"""

from propfein_mcp.client import PropfeinClient

SPORTS = "nfl, nba, nhl, mlb or ncaaf"


def get_board(client: PropfeinClient, sport: str | None = None, source: str | None = None, limit: int = 25) -> dict:
    """Open picks on games that have not started, soonest game first."""
    return client.get("/v1/board", {"sport": sport, "source": source, "limit": limit})


def get_tickets(client: PropfeinClient, sport: str | None = None, tier: str | None = None, limit: int = 10) -> dict:
    """Open tickets (parlays) with every leg."""
    return client.get("/v1/tickets", {"sport": sport, "tier": tier, "limit": limit})


def get_player_history(client: PropfeinClient, sport: str, player: str, stat: str | None = None,
                       line: float | None = None, games: int = 10) -> dict:
    """A player's recent games. With stat and line, also his record against that line."""
    return client.get("/v1/players/history", {"sport": sport, "player": player, "stat": stat, "line": line, "limit": games})


def _filters(sport, date_from, date_to, side, market, source, price_min, price_max) -> dict:
    return {"sport": sport, "from": date_from, "to": date_to, "side": side, "market": market,
            "source": source, "price_min": price_min, "price_max": price_max}


def get_record(client: PropfeinClient, sport: str | None = None, date_from: str | None = None, date_to: str | None = None,
               by: str = "all", side: str | None = None, market: str | None = None, source: str | None = None,
               price_min: int | None = None, price_max: int | None = None, per_bet: bool = True) -> dict:
    """Calibration of settled picks: stated chance against actual hit rate."""
    return client.get("/v1/record", {**_filters(sport, date_from, date_to, side, market, source, price_min, price_max),
                                     "by": by, "per_bet": per_bet})


def get_clv_report(client: PropfeinClient, sport: str | None = None, date_from: str | None = None, date_to: str | None = None,
                   by: str = "all", side: str | None = None, market: str | None = None, source: str | None = None,
                   price_min: int | None = None, price_max: int | None = None) -> dict:
    """Closing-line value of settled picks."""
    return client.get("/v1/record/clv", {**_filters(sport, date_from, date_to, side, market, source, price_min, price_max), "by": by})


def get_ticket_record(client: PropfeinClient, sport: str | None = None, date_from: str | None = None,
                      date_to: str | None = None) -> dict:
    """Tickets by tier: expected wins against actual wins."""
    return client.get("/v1/record/tickets", {"sport": sport, "from": date_from, "to": date_to})


def explain_pick(client: PropfeinClient, pick_id: str) -> dict:
    """Everything recorded about one pick or ticket: its inputs and how it ended."""
    pick_id = str(pick_id).strip()
    if not pick_id or "/" in pick_id or "?" in pick_id:
        raise ValueError("pick_id must be an id from get_board or get_tickets")
    return client.get(f"/v1/picks/{pick_id}")


def get_results(client: PropfeinClient, sport: str, date: str) -> dict:
    """Finished games and scores for one sport on one date (US Eastern)."""
    return client.get("/v1/results", {"sport": sport, "date": date})
