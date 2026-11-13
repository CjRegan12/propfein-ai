# propfein-ai: eval harness, MCP server (7)

## Done this session
- Ticket (parlay) eval shipped earlier today; findings in docs/findings.md.
- The evals found inflated CLV numbers in the app; the app fix (v190, private repo) is live.
- Built the Propfein API v1 in the private app repo (function `propfein-api`, read-only, Bearer keys). Not deployed yet: the owner deploys.
- Built the MCP server here: `propfein_mcp/` (client, 8 tools, SDK wiring, invented mock data), docs/mcp-setup.md.
- Built the faithfulness eval: evals/faithfulness.py (deterministic; pass = zero unsupported numbers).
- 50 tests pass.
- Later the same day: the MCP server ran in Claude Desktop on the live API (first faithfulness run on a real answer: 80 numbers, 76 supported, 4 derived by the model and flagged; decision: keep it strict). Added evals/slipcheck.py for the app's new Check my slip tags; 54 tests pass.

## Decisions and why
- MCP server is Python, not TypeScript as the spec first said: one language in the repo, the owner is learning Python, and pytest already runs here.
- Uses the official `mcp` SDK v2 for the protocol; the 2026-07-28 spec changed the handshake, so hand-rolling it would break.
- Tool logic is SDK-free so it is testable in the cloud workspace (PyPI is blocked there).
- Faithfulness is strict: derived numbers fail. Loosen only with a test that shows why.
- Judge any bias per bet; line-basis CLV is direction only (unchanged).

## Next steps
1. Done: API deployed, key made, MCP server running in Claude Desktop (Microsoft Store install: its config is under AppData\Local\Claude-Data, not the documented path).
2. Strict faithfulness means the API should return subtotals so the model never adds rows itself (ticket record: the two big tiers vs the rest).
3. After it works in Claude Desktop: save 20 to 30 real question/answer/tool-result sets to results/agent_log.jsonl and run the faithfulness eval. That is the first agent eval number.
4. API phase 2 (plan first): live scores, legs match and odds, which the Group Sweat app needs.
5. Pro features (Ask, Check my slip, Why this pick, recap) come after the app's 1.0 and need an Anthropic API key.
6. Still open: recheck NFL rush yards with `--since 2026-11-07` in a few weeks.

## Open questions for the user
- Has the owner explained ECE in his own words yet? (interview practice)
- Why did NBA overs drop from +5.9 to +2.0 under per-bet counting? (quiz)

## Files touched
- propfein_mcp/*: new MCP server
- evals/faithfulness.py, tests/test_faithfulness.py, tests/test_mcp_tools.py: new
- README.md, CLAUDE.md, NOTES.md, .env.example, requirements.txt, docs/mcp-setup.md: docs and setup
