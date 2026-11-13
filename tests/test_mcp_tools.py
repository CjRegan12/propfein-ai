"""Tests for the MCP server's client and tools. No network, no database, no MCP SDK."""

import io
import json
import urllib.error

import pytest

from propfein_mcp import tools
from propfein_mcp.client import ApiError, PropfeinClient

KEY = "pf_" + "k" * 40


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def recording_opener(answer: dict, seen: list):
    def opener(request, timeout):
        seen.append(request)
        return FakeResponse(json.dumps(answer).encode())
    return opener


def client(answer=None, seen=None):
    return PropfeinClient("https://api.example.test", KEY, opener=recording_opener(answer or {"data": {"ok": True}}, seen if seen is not None else []))


def test_every_request_is_a_get_with_the_bearer_key():
    seen = []
    tools.get_board(client(seen=seen), sport="nfl", limit=5)
    r = seen[0]
    assert r.get_method() == "GET"
    assert r.full_url == "https://api.example.test/v1/board?sport=nfl&limit=5"
    assert r.get_header("Authorization") == f"Bearer {KEY}"
    assert r.data is None


def test_record_passes_every_filter_and_drops_empty_ones():
    seen = []
    tools.get_record(client(seen=seen), sport="nba", date_from="2026-10-13", by="side", side="over", price_min=-200, price_max=-150)
    assert seen[0].full_url == ("https://api.example.test/v1/record?sport=nba&from=2026-10-13&side=over"
                                "&price_min=-200&price_max=-150&by=side&per_bet=true")
    tools.get_record(client(seen=seen), per_bet=False)
    assert seen[1].full_url == "https://api.example.test/v1/record?by=all&per_bet=false"


def test_tools_return_the_api_data_unchanged():
    data = {"total": 1, "picks": [{"player": "A", "probability": 0.6123}]}
    assert tools.get_board(client({"data": data})) == data


def test_api_error_carries_the_api_message_and_never_the_key():
    def opener(request, timeout):
        body = json.dumps({"error": {"code": "bad_request", "message": "unknown sport"}}).encode()
        raise urllib.error.HTTPError(request.full_url, 400, "Bad Request", {}, io.BytesIO(body))
    c = PropfeinClient("https://api.example.test", KEY, opener=opener)
    with pytest.raises(ApiError) as e:
        tools.get_board(c, sport="cricket")
    assert (e.value.status, e.value.code, e.value.message) == (400, "bad_request", "unknown sport")
    assert KEY not in str(e.value)


def test_unreachable_and_malformed_answers_are_api_errors():
    def down(request, timeout):
        raise urllib.error.URLError("no route")
    with pytest.raises(ApiError) as e:
        tools.get_board(PropfeinClient("https://api.example.test", KEY, opener=down))
    assert e.value.code == "unreachable" and KEY not in str(e.value)
    with pytest.raises(ApiError):
        tools.get_board(client({"nope": 1}))


def test_plain_http_is_refused_so_the_key_never_travels_unencrypted():
    with pytest.raises(ValueError):
        PropfeinClient("http://api.example.test", KEY)


def test_explain_pick_refuses_an_id_that_could_change_the_path():
    for bad in ["", "abc/../../v1/board", "id?x=1"]:
        with pytest.raises(ValueError):
            tools.explain_pick(client(), bad)


def test_mock_mode_answers_every_tool_with_sample_data():
    c = PropfeinClient("mock")
    assert tools.get_board(c)["total"] == 2
    assert tools.get_tickets(c)["tickets"][0]["tier"] == "cash"
    assert tools.get_player_history(c, "nba", "Sample Player One", "points", 24.5)["against_line"]["over"] == 2
    assert tools.get_record(c, by="side")["groups"][0]["group"] == "over"
    assert tools.get_clv_report(c)["groups"][0]["price"]["picks"] == 300
    assert tools.get_ticket_record(c)["groups"][0]["wins"] == 26
    assert tools.explain_pick(c, "00000000-0000-4000-8000-000000000001")["status"] == "won"
    assert tools.get_results(c, "nba", "2030-01-14")["games"][0]["status"] == "final"


def test_the_server_offers_exactly_the_tested_tools():
    """server.py needs the MCP SDK, so read it as text: each tool there must call a tested function."""
    import re
    from pathlib import Path
    src = (Path(__file__).parent.parent / "propfein_mcp" / "server.py").read_text(encoding="utf-8")
    offered = re.findall(r"@mcp\.tool\(\)\ndef (\w+)\(", src)
    called = re.findall(r"return call\(tools\.(\w+),", src)
    assert offered == called
    assert sorted(offered) == sorted(n for n in dir(tools) if n.startswith(("get_", "explain_")))
    assert "print(" not in src  # stdout belongs to the protocol
