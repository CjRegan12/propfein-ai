"""Splitting picks into groups (by source, side, market, ...)."""

GROUP_FIELDS = ("source", "tier", "market", "side")


def group_by(rows: list[dict], field: str) -> dict[str, list[dict]]:
    """Split rows into piles by one field, biggest pile first.

    group_by([{"side": "over"}, {"side": "under"}, {"side": "over"}], "side")
    -> {"over": [..2 rows..], "under": [..1 row..]}
    """
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(str(row.get(field, "unknown")), []).append(row)
    return dict(sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])))
