# propfein-ai

Public eval harness and (later) MCP server for Propfein, a sports data analysis iOS app. The app lives in the private repo CjRegan12/propfein-ios. Frame Propfein as a sports data analysis app in anything public.

## Commands (owner is on Windows / PowerShell)

- Tests: `python -m pytest` (no database needed)
- Calibration eval: `python -m evals.calibration --sport nfl` (sports: nfl, nba, nhl, mlb, ncaaf)
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

## Gotchas

- Float bucketing: `0.15 / 0.05 == 2.9999999999999996`; round before `floor`. Tests cover it.
- Paper record has duplicate `key` rows; loaders use `distinct on (key) ... order by key, at desc`.
- PyPI is blocked from the cloud agent workspace, so psycopg can't be installed or run there; the DB path is only exercised on the owner's machine.
