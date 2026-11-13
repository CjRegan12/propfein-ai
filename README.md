# propfein-ai

The evaluation and AI layer for [Propfein](https://propfein.app), a sports data analysis app for iOS.

Propfein shows bettors player props and parlays along with the probability each one hits. This repo answers the question that matters most about those numbers: **are they honest?** It holds an eval harness that grades the app's picks against what actually happened, and later the Claude-powered layer (an MCP server and agent features) that explains picks and checks users' parlays.

The app itself lives in a separate private repo. This repo connects to its database through a **read-only login**: it can only `SELECT` from a fixed set of tables, every session is forced read-only, and queries time out after 30 seconds, so nothing here can change production data or slow down the live app.

## Core rule

**The LLM never does the pick math.** Probabilities, hit rates and ticket building stay deterministic code. Claude works around the engine: fixing inputs, adding context, and explaining outputs. Every claim it makes gets checked against the data.

## What's here

| Path | What it is |
| --- | --- |
| `run_evals.py` | One command: every eval, every sport, one scoreboard |
| `evals/calibration.py` | Calibration eval: when the app says 65%, does it hit about 65%? |
| `evals/clv.py` | Closing line value eval: do picks beat the closing price? |
| `evals/tickets.py` | Ticket eval: do parlays win as often as they claim? |
| `propfein_ai/grouping.py` | Splits picks by source, tier, market or side |
| `propfein_ai/db.py` | Read-only database connection |
| `propfein_ai/data.py` | Loads settled picks for evals |
| `tests/` | Tests for every eval (no database needed) |
| `results/` | Eval output, saved per run (git-ignored) |
| `docs/glossary.md` | Plain-English definitions of the AI and eval terms used here |

## Evals

| Eval | Status | Measures |
| --- | --- | --- |
| Calibration | Done | Stated probability vs actual hit rate, by 5% bucket, plus expected calibration error (ECE) and signed bias; splittable by source, tier, market and side |
| Closing line value | Done | Whether picks beat the final market price, with true price moves and model-translated line moves reported separately |
| Tickets | Done | Parlays: expected wins vs actual wins per tier, with a z-score and ROI at the shown price |
| Scoreboard | Done | Every eval for every sport in one command, saved per run for regression comparisons |
| Faithfulness | Planned | Every number the AI cites matches the data |
| Check my slip | Planned | Do legs the agent flags as weak actually hit less? |

## Setup (Windows, PowerShell)

```powershell
git clone https://github.com/CjRegan12/propfein-ai
cd propfein-ai
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # then fill in DATABASE_URL
```

Run the tests (no database needed):

```powershell
python -m pytest
```

Run everything (the regression run):

```powershell
python run_evals.py
```

Run one eval, optionally split by `source`, `tier`, `market` or `side`:

```powershell
python -m evals.calibration --sport nfl
python -m evals.calibration --sport nfl --by side --per-bet
python -m evals.clv --sport nfl --by source
python -m evals.tickets
python run_evals.py --since 2026-11-07
```

`--per-bet` counts each player-game-side once (the record saves several lines of one player's ladder, which win or lose together); use it whenever you judge whether a bias is real. `--since` cuts to picks made after an app change.

## Roadmap

1. Eval harness: calibration, then closing line value, then a one-command regression run
2. MCP server on top of the public Propfein API
3. Claude features in Propfein Pro: Ask, Check my slip, Why this pick, weekly recap
4. LLM-assisted feature discovery, gated by backtests
