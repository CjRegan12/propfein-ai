# propfein-ai: calibration eval (1)

## Done this session
- Spec doc "Propfein AI Layer Spec" (Claude Doc, https://claude.ai/artifact/QkHwuunqhVP45goBeqKQDS): phases, evals, timing around the 1.0 release.
- Read-only DB role `propfein_ai_ro` created by the owner and verified: reads the 9 eval tables, writes none, can't see ef_config/ef_auth/ef_bets/ef_guest_writes, ef_paper limited to the main record account.
- Repo scaffolded and pushed to main: db connection, settled-singles loader, `evals/calibration.py` with 3 TODO functions, 17 tests (fail on stubs, pass with a reference solution), README, docs/glossary.md.

## Decisions and why
- NFL first: ~5,600 settled singles and the only sport with an injury table.
- Calibration (stated % vs hit %) plus CLV as ground truths; calibration is what users care about.
- MCP server waits for the public Propfein API and is built on it once, shared with Group Sweat.
- Owner writes the eval logic himself (portfolio + Python/interview practice for FDE / AI engineer roles).
- AI work stays off the iOS app until after 1.0 (App Store submit targeted Nov 23); user features ship with Pro later.

## Next steps
1. Owner implements `bucket_for`, `calibration_table`, `expected_calibration_error` in `evals/calibration.py` until `python -m pytest` is green; review his code (don't write it for him).
2. Owner runs `python -m evals.calibration --sport nfl`. Check his output against an answer key computed with the Supabase MCP (same filters as `SETTLED_SINGLES_SQL`, bucket `floor(fair_prob*20)/20`); don't write the numbers here, the owner reads this repo. There's a notable finding in the largest bucket to talk through with him.
3. If the DB connection errors on his machine, debug `propfein_ai/db.py` / pooler URL (never run here before).
4. Then: CLV eval (`evals/clv.py`) from `ef_paper.clv_snap` (clvFinal, clv), same TODO-plus-tests style.

## Open questions for the user
- Is "Check my slip" Pro-only or one free check a day?
- Which news/injury source and monthly budget for the agent?
- Still owes the quiz answer: NBA picks say 52.7% but hit 57.2%, good, bad or neither?

## Files touched
- .gitignore, .env.example, requirements.txt: secrets/data kept out, deps
- propfein_ai/db.py, propfein_ai/data.py: read-only connection and picks loader
- evals/calibration.py: calibration eval with 3 TODOs and finished runner
- tests/test_calibration.py: 17 tests including float bucketing trap
- README.md, docs/glossary.md: recruiter-facing overview and term definitions
- CLAUDE.md, NOTES.md: handoff
