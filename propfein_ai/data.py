"""Loading eval data from the database.

Each function returns plain Python lists of dicts, so the eval code
stays simple and testable without a database.
"""

from propfein_ai.db import connect

# Sport keys as stored by the odds feed.
SPORTS = {
    "nfl": "americanfootball_nfl",
    "nba": "basketball_nba",
    "nhl": "icehockey_nhl",
    "mlb": "baseball_mlb",
    "ncaaf": "americanfootball_ncaaf",
}

# Settled single-leg picks from the app's paper record.
#  - distinct on (key): the same pick can be saved twice; keep the latest copy
#  - jsonb_array_length(legs) = 1: singles only (parlays get their own eval later)
#  - prob: the probability the app showed for the pick
#  - side: over / under for props and totals, team for moneylines and spreads
#  - clv / clv_basis: only filled once the closing line is final.
#      clv = your price / closing price - 1 (positive = you beat the close)
#      basis "price" = same line, pure price comparison
#      basis "line"  = the line moved, so the close was translated to your
#                      line by the model (model-dependent, reported separately)
SETTLED_SINGLES_SQL = """
    select distinct on (key)
        key,
        fair_prob::float                              as prob,
        status = 'won'                                as won,
        coalesce(source, 'unknown')                   as source,
        coalesce(tier, 'unknown')                     as tier,
        coalesce(legs -> 0 ->> 'market', 'unknown')   as market,
        case legs -> 0 ->> 'name'
            when 'Over'  then 'over'
            when 'Under' then 'under'
            else 'team'
        end                                           as side,
        case when (clv_snap ->> 'clvFinal')::boolean
             then (clv_snap ->> 'clv')::float end     as clv,
        case when (clv_snap ->> 'clvFinal')::boolean
             then coalesce(clv_snap ->> 'clvBasis', 'price') end as clv_basis
    from ef_paper
    where status in ('won', 'lost')
      and jsonb_array_length(legs) = 1
      and fair_prob is not null
      and legs -> 0 ->> 'sport' = %(sport)s
    order by key, at desc
"""


def fetch_settled_singles(sport: str) -> list[dict]:
    """Return settled single picks for one sport.

    Each item looks like:
        {"key": "...", "prob": 0.534, "won": True, "source": "usage",
         "tier": "strong", "market": "player_rush_yds", "side": "over",
         "clv": 0.021, "clv_basis": "price"}
    """
    if sport not in SPORTS:
        raise ValueError(f"Unknown sport {sport!r}. Use one of: {', '.join(SPORTS)}")

    with connect() as conn, conn.cursor() as cur:
        cur.execute(SETTLED_SINGLES_SQL, {"sport": SPORTS[sport]})
        columns = [c.name for c in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
