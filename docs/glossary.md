# Glossary

Plain-English definitions of the terms used in this repo.

## Building blocks

- **LLM (large language model):** A model like Claude. Strong at reading, reasoning and writing; not trustworthy for producing exact numbers on its own, which is why it never does the pick math here.
- **MCP server (Model Context Protocol):** A small program that gives an LLM *tools* to pull data from a system. It's the plumbing that lets Claude look things up instead of guessing.
- **Tool:** One function on an MCP server, like `get_board` or `get_record`. Each answers one kind of question from the data.
- **Agent:** An LLM running in a loop: decide which tool to call, read the result, call another if needed, then answer. *MCP gives the model access; the agent decides what to do with it.*
- **Structured output:** Making the model answer in a fixed format (JSON) so code can use the result reliably.
- **Read-only role:** A database login that can look but never change anything.

## Measuring quality

- **Eval (evaluation):** An automated test for AI or model behavior. Regular tests check "does the code run"; evals check "is the answer actually good."
- **Ground truth:** The real answer you grade against. Here, what actually happened in the games.
- **Calibration:** When the app says 65%, does it hit about 65% of the time? A model that says 70% but hits 52% is *overconfident*.
- **Expected calibration error (ECE):** One number summarizing calibration: the average gap between stated and actual hit rate, weighted by how many picks are in each bucket. Lower is better; 0 is perfect.
- **CLV (closing line value):** Whether you got a better price than the final line before the game. The best long-term sign a pick had a real edge. Measures *price*, not whether the pick hit.
- **Backtest:** Running a new idea on past games to see if it would have helped, before trusting it on future ones.
- **Faithfulness / hallucination:** A hallucination is the model confidently stating something not in the data. A faithfulness check compares every number the model cites against what its tools returned.
- **Regression run:** Re-running every eval after any change, to catch a "fix" that quietly made something else worse.
- **LLM-as-judge:** Using an LLM to grade another LLM's writing against a rubric, checked against human grades first so you know the judge is fair.
- **Small sample:** Too few examples to trust a result. A bucket with 7 picks can swing wildly by luck; one with 3,000 can't.

## Data and modeling

- **Feature:** One input a model uses, like "WR1 is out" or "last-10 hit rate." Feature discovery means finding new useful inputs.
- **Alias table:** Matches different spellings of the same player or market across sportsbooks.
- **Precision:** Of the matches made, how many were right. Matters most when a wrong answer is worse than no answer.
- **Floating-point error:** Computers store decimals imperfectly, so `0.15 / 0.05` is `2.9999999999999996` in Python, not `3`. Code that buckets or compares decimals has to account for it.
