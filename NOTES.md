# propfein-ai: calibration eval (2)

## Done this session
- Owner connected locally with the read-only login (pulled 6,618 settled NFL singles).
- Owner hand-wrote bucket_for, calibration_table, expected_calibration_error; all 15 tests pass.
- First real eval run: NFL ECE 3.59 points. Written up in docs/findings.md.
- Spec doc "Propfein AI Layer Spec": https://claude.ai/artifact/QkHwuunqhVP45goBeqKQDS

## Decisions and why
- NFL first: most data, only sport with an injury table.
- results/ stays git-ignored; findings are committed as dated sections in docs/findings.md.
- Owner writes eval logic; teaching style that works: try it in the Python scratchpad (>>>) first, then move it into the file. He's new to the terminal: be explicit about PS prompt vs >>> vs Notepad, and about indentation (Col 5 / Col 9 in Notepad's status bar).
- One MCP server, built later on the public Propfein API.

## Next steps
1. Extend calibration: add `--by source` and `--by side` (over vs under) options to `evals/calibration.py` to test the selection-bias hypothesis in docs/findings.md (45-60% buckets overconfident by 3-5 points). Needs the loader in `propfein_ai/data.py` to also return `source` and the leg's `name` (Over/Under). Scaffold + tests by Claude, grouping logic by the owner.
2. Run calibration for nba and nhl and add sections to docs/findings.md.
3. Then CLV eval (`evals/clv.py`) from `ef_paper.clv_snap` (clvFinal, clv), same TODO-plus-tests style.
4. Small cleanup for the owner to do: replace hardcoded `19` in bucket_for with a value derived from `width`.

## Open questions for the user
- Owner hasn't yet explained ECE in his own words (interview practice); ask again.
- Still owes the NBA quiz: picks say 52.7% but hit 57.2%, good, bad or neither?
- Is "Check my slip" Pro-only or one free check a day? News/injury source and budget?

## Files touched
- evals/calibration.py: owner implemented the three TODO functions
- docs/findings.md: NFL calibration baseline write-up (owner)
- NOTES.md: handoff update
