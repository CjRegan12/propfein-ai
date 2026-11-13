# propfein-ai: eval harness (4)

## Done this session
- Owner asked to move fast: Claude wrote the code this round (owner still learns by running and reading results).
- Loader now returns source, tier, market, side, final CLV and CLV basis.
- calibration: summarize() with signed bias, `--by source|tier|market|side`.
- evals/clv.py: price-basis and model-translated line-basis CLV, never mixed.
- run_evals.py: scoreboard for every sport, saved per run.
- First full run written up in docs/findings.md (2026-11-13), also saved to the Propfein project as claude/eval-findings-nov-2026.md.
- NFL overs follow-up: the miss is rush yards (per bet -8.1, noise 5.3), already corrected in the app by v157 (Nov 6-7); almost no post-v157 data yet. Added --since and --per-bet; corrected findings section 5.

## Decisions and why
- Judge any bias per bet (one per player-game-side): the record saves ladder rungs that win or lose together.
- No new app change for rush yards until post-v157 data settles; v157 is measured on four seasons of history.
- Line-basis CLV reported apart and treated as direction only: translated size does not predict hit rate (findings section 4).
- Delivery: Claude never pushes from the cloud clone; commit locally, send a .patch, owner runs `git am --3way` and pushes.

## Next steps
1. In a few weeks: `python -m evals.calibration --sport nfl --by market --per-bet --since 2026-11-07` to check v157's size. Also rerun NBA with --per-bet before reading the +5.9.
2. App-side follow-ups live in the private propfein-ios repo and need a plan for the owner before building: CLV display price-basis only, review weak sources. See docs/findings.md "Recommended next steps".
3. After any app change, owner reruns `python run_evals.py` and `--by side`; add a dated findings section comparing to 2026-11-13.
4. Next eval: parlay/ticket calibration (multi-leg picks are excluded today).
5. Then the MCP server on the public Propfein API, and the faithfulness eval for Claude features.

## Open questions for the user
- Whether to tackle the CLV display (price-basis only) in the app next.
- Owner hasn't explained ECE in his own words yet (interview practice).

## Files touched
- propfein_ai/data.py, propfein_ai/grouping.py, evals/calibration.py, evals/clv.py, run_evals.py, tests/test_splits_and_clv.py: new evals
- docs/findings.md: 2026-11-13 results, Nov 2 section reformatted
- README.md, CLAUDE.md, NOTES.md: docs
