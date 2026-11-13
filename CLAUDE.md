# propfein-ai

Public eval harness and (later) MCP server for Propfein, a sports data analysis iOS app. The app lives in the private repo CjRegan12/propfein-ios. Frame Propfein as a sports data analysis app in anything public.

## Commands (owner is on Windows / PowerShell)

- Tests: `python -m pytest` (no database needed)
- All evals, all sports: `python run_evals.py`
- Calibration eval: `python -m evals.calibration --sport nfl [--by source|tier|market|side]` (sports: nfl, nba, nhl, mlb, ncaaf)
- CLV eval: `python -m evals.clv --sport nfl [--by ...]`. CLV = your decimal / close decimal - 1; basis "line" is model-translated, always reported apart from "price".
- Faithfulness eval: `python -m evals.faithfulness --cases <file.jsonl>` (lines of `{question, tool_results, answer}`)
- MCP server: `python -m propfein_mcp` (stdio; `PROPFEIN_API_URL=mock` for sample data). Setup: `docs/mcp-setup.md`
- Delivery: Claude never pushes from the cloud clone. Commit locally, send a .patch, the owner runs `git am --3way` and pushes.
- Setup: `python -m venv .venv`, `.venv\Scripts\Activate.ps1`, `pip install -r requirements.txt`, copy `.env.example` to `.env`

## Environment

- `DATABASE_URL` in local `.env` only: read-only Postgres role `propfein_ai_ro` on the Supabase "edgefinder" project, via the session pooler (user `propfein_ai_ro.<project-ref>`).
- The role can only SELECT ef_paper, ef_games, ef_player_games, ef_lines_hist, ef_line_history, ef_nfl_injuries, ef_nfl_roster, ef_nfl_weeks, ef_team_prior. Sessions are forced read-only, 30s statement timeout, 3 connections max. RLS limits ef_paper to the app's main record account, so code never filters by user.
- Setup and undo SQL for the role were run by the owner in the Supabase SQL editor (an agent attempt to apply it as a migration was blocked). Changes to the role go through the owner the same way.

## Rules

- The LLM never does pick or probability math; evals and pricing stay deterministic code.
- Never commit secrets, project refs, user ids or raw data. `.env`, `data/` and `results/*` are git-ignored.
- Learning-first: the owner hand-writes the Python eval logic (TODO functions with hints and tests). Don't fill in TODOs for him; scaffold, test and review instead.
- One MCP server only, built on top of the public Propfein API (shared with the Group Sweat app), not directly on the database. The read-only role is for bulk eval queries.

## MCP server (propfein_mcp/)

- `client.py` (GET only, stdlib) and `tools.py` (plain functions) hold all the logic and are tested without the SDK; `server.py` only wires them to the official `mcp` SDK v2 (`from mcp.server import MCPServer`, `mcp.run(transport="stdio")`). A new tool is a function in tools.py, a wrapper in server.py and a route in mock_data.json; a test holds the three in step.
- Never write the protocol by hand: the 2026-07-28 MCP spec removed the initialize handshake (`server/discover`, per-request `_meta`), and the SDK handles both eras.
- Nothing in server.py may print to stdout (the protocol owns it).
- `mock_data.json` is invented data only. No real player, pick or result goes in the repo.
- The API itself lives in the private app repo (function `propfein-api`). Its record numbers mirror these evals; if an eval's counting rule changes, the API's database functions change too.
- Faithfulness is strict on purpose: a number the model derived (100 minus a chance, a difference) is unsupported even when it is right.

## Gotchas

- Float bucketing: `0.15 / 0.05 == 2.9999999999999996`; round before `floor`. Tests cover it.
- Paper record has duplicate `key` rows; loaders use `distinct on (key) ... order by key, at desc`.
- PyPI and npm are both blocked from the cloud agent workspace, so psycopg and the `mcp` SDK can't be installed or run there; the DB path and `propfein_mcp/server.py` are only exercised on the owner's machine.
