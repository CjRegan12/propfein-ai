"""The MCP server: wires the plain tool functions to the official MCP Python SDK.

Run it (Claude Desktop does this for you once it is in its config):

    python -m propfein_mcp

It talks over stdio, so nothing in this file may print to stdout: the SDK owns
that stream. Every tool is read-only.
"""

from mcp.server import MCPServer

from propfein_mcp import tools
from propfein_mcp.client import ApiError, PropfeinClient

mcp = MCPServer("propfein")
_client: PropfeinClient | None = None


def client() -> PropfeinClient:
    global _client
    if _client is None:
        _client = PropfeinClient.from_env()
    return _client


def call(fn, *args, **kwargs) -> dict:
    """Run one tool and turn an API error into a message the model can act on."""
    try:
        return fn(client(), *args, **kwargs)
    except ApiError as e:
        raise RuntimeError(f"Propfein API: {e.message}") from None


@mcp.tool()
def get_board(sport: str | None = None, source: str | None = None, limit: int = 25) -> dict:
    """Propfein's open picks on games that have not started, soonest first.

    Each pick has the player, market, side (pick), line, price (American odds),
    book, and `probability`: the chance Propfein stated. Quote these numbers
    exactly; never estimate a probability yourself.

    Args:
        sport: nfl, nba, nhl, mlb or ncaaf. Leave empty for every sport.
        source: only picks from one source (for example shelf or trend).
        limit: how many picks to return, 1 to 200.
    """
    return call(tools.get_board, sport, source, limit)


@mcp.tool()
def get_tickets(sport: str | None = None, tier: str | None = None, limit: int = 10) -> dict:
    """Propfein's open tickets (parlays) with every leg, newest first.

    `probability` is the stated chance the whole ticket wins and
    `decimal_price` is the payout it showed.

    Args:
        sport: nfl, nba, nhl, mlb or ncaaf. Leave empty for every sport.
        tier: one ticket type, for example cash, slate or script_short.
        limit: how many tickets to return, 1 to 50.
    """
    return call(tools.get_tickets, sport, tier, limit)


@mcp.tool()
def get_player_history(sport: str, player: str, stat: str | None = None, line: float | None = None, games: int = 10) -> dict:
    """A player's most recent games with his box-score stats.

    Give `stat` and `line` to also get `against_line`: how many of those games
    went over, under or landed on the line. That count is a fact about his
    past games, not a prediction. Call it once without `stat` to see which
    stat names this player has.

    Args:
        sport: nfl, nba, nhl or mlb.
        player: his full name as a sportsbook lists it.
        stat: a stat name from the `stats` list, for example points or rush_yds.
        line: the number to compare against, for example 24.5.
        games: how many recent games, 1 to 40.
    """
    return call(tools.get_player_history, sport, player, stat, line, games)


@mcp.tool()
def get_record(sport: str | None = None, date_from: str | None = None, date_to: str | None = None, by: str = "all",
               side: str | None = None, market: str | None = None, source: str | None = None,
               price_min: int | None = None, price_max: int | None = None, per_bet: bool = True) -> dict:
    """How Propfein's settled picks did against what it said (calibration).

    Each group has `bets`, `stated` (average stated chance), `hit_rate`,
    `bias` (hit_rate minus stated; below zero means overconfident) and
    `noise`. A bias smaller than the noise could be luck: say so instead of
    calling it a finding.

    Args:
        sport: nfl, nba, nhl, mlb or ncaaf. Leave empty for every sport.
        date_from: first day, YYYY-MM-DD.
        date_to: last day, YYYY-MM-DD.
        by: split the answer by all, source, tier, market, side or price.
        side: only over, under or team picks.
        market: only one market, for example player_rush_yds.
        source: only one pick source.
        price_min: lowest American odds to include, for example -200.
        price_max: highest American odds to include, for example -150.
        per_bet: count each player-game-side once (true, the honest count) or every line (false).
    """
    return call(tools.get_record, sport, date_from, date_to, by, side, market, source, price_min, price_max, per_bet)


@mcp.tool()
def get_clv_report(sport: str | None = None, date_from: str | None = None, date_to: str | None = None, by: str = "all",
                   side: str | None = None, market: str | None = None, source: str | None = None,
                   price_min: int | None = None, price_max: int | None = None) -> dict:
    """Closing-line value: did the picks beat the final market price?

    `price.mean` is the average of (pick price / closing price - 1) for picks
    whose number did not move. `moved` picks only report a direction
    (`moved_in_favour`), never a size, because that size is a model
    translation and does not predict results.

    Args: the same filters as get_record (without per_bet).
    """
    return call(tools.get_clv_report, sport, date_from, date_to, by, side, market, source, price_min, price_max)


@mcp.tool()
def get_ticket_record(sport: str | None = None, date_from: str | None = None, date_to: str | None = None) -> dict:
    """How settled tickets (parlays) did, by tier.

    `expected_wins` is the stated chances added up; compare it with `wins`.
    `z` between -2 and 2 means the results are consistent with the stated
    chances. Tiers with few tickets prove nothing either way.

    Args:
        sport: nfl, nba, nhl, mlb or ncaaf. Leave empty for every sport.
        date_from: first day, YYYY-MM-DD.
        date_to: last day, YYYY-MM-DD.
    """
    return call(tools.get_ticket_record, sport, date_from, date_to)


@mcp.tool()
def explain_pick(pick_id: str) -> dict:
    """The recorded inputs behind one pick or ticket, and how it ended.

    Returns each leg with the stated `probability`, the books' own number
    (`books_probability`), which books it was priced from, the result, and the
    closing-line comparison once it is final. Use only these inputs when
    explaining a pick; do not add reasons that are not in the data.

    Args:
        pick_id: an `id` from get_board or get_tickets.
    """
    return call(tools.explain_pick, pick_id)


@mcp.tool()
def get_results(sport: str, date: str) -> dict:
    """Finished games and final scores for one sport on one date.

    Args:
        sport: nfl, nba, nhl, mlb or ncaaf.
        date: the game's date in US Eastern time, YYYY-MM-DD.
    """
    return call(tools.get_results, sport, date)


def main() -> None:
    client()  # fail now, with a clear message, if the settings are missing
    mcp.run(transport="stdio")
