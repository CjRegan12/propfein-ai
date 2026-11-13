# propfein-ai: eval harness (3)

## Done this session
- Owner asked to move fast: Claude wrote the code this round (owner still learns by running and reading results).
- Loader now returns source, tier, market, side, final CLV and CLV basis.
- calibration: summarize() with signed bias, `--by source|tier|market|side`.
- evals/clv.py: price-basis and model-translated line-basis CLV, never mixed.
- run_evals.py: scoreboard for every sport, saved per run.
- First full run written up in docs/findings.md (2026-11-13), also saved to the Propfein project as claude/eval-findings-nov-2026.md.

## Decisions and why
- Line-basis CLV reported apart and treated as direction only: translated size does not predict hit rate (findings section 4).
- Delivery: Claude never pushes from the cloud clone; commit locally, send a .patch, owner runs `git am --3way` and pushes.

## Next steps
1. App-side follow-ups live in the private propfein-ios repo and need a plan for the owner before building: NFL overs correction, NBA overs correction review, CLV display price-basis only, review weak sources. See docs/findings.md "Recommended app changes".
2. After any app change, owner reruns `python run_evals.py` and `--by side`; add a dated findings section comparing to 2026-11-13.
3. Next eval: parlay/ticket calibration (multi-leg picks are excluded today).
4. Then the MCP server on the public Propfein API, and the faithfulness eval for Claude features.

## Open questions for the user
- Which app fix first: NFL overs or NBA overs correction?
- Owner hasn't explained ECE in his own words yet (interview practice).

## Files touched
- propfein_ai/data.py, propfein_ai/grouping.py, evals/calibration.py, evals/clv.py, run_evals.py, tests/test_splits_and_clv.py: new evals
- docs/findings.md: 2026-11-13 results, Nov 2 section reformatted
- README.md, CLAUDE.md, NOTES.md: docs
