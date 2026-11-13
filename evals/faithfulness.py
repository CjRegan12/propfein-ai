"""Faithfulness eval: does every number the AI cites match the tool data?

The model is never trusted with numbers. This check reads an answer, pulls out
every number it states, and looks each one up in the data the tools returned
for that answer. A number that is not in the data (after allowing for rounding
and for a 0.61 chance being written as 61%) is "unsupported".

    python -m evals.faithfulness --cases results/agent_log.jsonl

Each line of the cases file is one logged agent call:
    {"question": "...", "tool_results": [ ...the tools' JSON answers... ], "answer": "..."}

Pass signal: zero unsupported numbers. This is deterministic code, no LLM judge.

What it does not catch: a correct number attached to the wrong thing ("Smith
hit 61%" when 61% was Jones's). That needs the explanation-quality eval.
"""

import argparse
import json
import re
from pathlib import Path

# A number as written: optional sign, digits with optional thousands commas, optional decimals, optional %.
# "percent", "points" and "pts" count like %: a bias of -0.035 is written "-3.5 points".
NUMBER = re.compile(r"(?<![\w.])([+\-\u2212]?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(\s?%|\s(?:percent(?:age)?|points?|pts)\b)?(?![\w]|\.\d)", re.IGNORECASE)
# Things that look like numbers but are not claims about the data.
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b")
ORDINAL = re.compile(r"\b\d+(?:st|nd|rd|th)\b", re.IGNORECASE)


def numbers_in_text(text: str) -> list[dict]:
    """Every number stated in a piece of text.

    Each item: {"raw": "61%", "value": 61.0, "percent": True, "decimals": 0}
    """
    cleaned = ORDINAL.sub(" ", DATE.sub(" ", text))
    found = []
    for m in NUMBER.finditer(cleaned):
        sign, whole, frac, pct = m.groups()
        value = float(whole.replace(",", "") + (frac or ""))
        if sign in ("-", "−"):
            value = -value
        found.append({
            "raw": sign + whole + (frac or "") + ("%" if pct and "%" in pct else ""),
            "value": value,
            "percent": bool(pct),
            "decimals": len(frac) - 1 if frac else 0,
        })
    return found


def numbers_in_data(data) -> list[float]:
    """Every number anywhere inside the tools' JSON answers (booleans are not numbers)."""
    out = []
    if isinstance(data, bool) or data is None:
        return out
    if isinstance(data, (int, float)):
        return [float(data)]
    if isinstance(data, str):
        # numbers inside strings count too: dates and ids are data the model may quote
        return [n["value"] for n in numbers_in_text(data)]
    if isinstance(data, dict):
        data = list(data.values())
    for item in data:
        out.extend(numbers_in_data(item))
    return out


def _rounds_to(actual: float, stated: float, decimals: int) -> bool:
    """True if `actual`, rounded the way the text was written, gives `stated`.

    Half a unit of the last written digit is allowed, so 0.6123 supports
    "61.2" and "61" but not "62".
    """
    half_step = 0.5 * 10 ** (-decimals)
    return abs(actual - stated) <= half_step + 1e-9


def supported(claim: dict, data_numbers: list[float]) -> bool:
    """Is one stated number backed by the data?

    A percent ("61%", "3.5 points") may come from a 0-to-1 fraction in the data
    (0.61, 0.035) or from a number already in that unit ("28 points" is also just 28). A signed number may match its data value
    either with its sign or, for "+", without one. Nothing else is tried: no
    sums, no differences, no 100-minus. A number the model worked out itself
    is unsupported on purpose.
    """
    value, decimals = claim["value"], claim["decimals"]
    for actual in data_numbers:
        candidates = [actual]
        if claim["percent"]:
            candidates.append(actual * 100)
        if any(_rounds_to(c, value, decimals) for c in candidates):
            return True
    return False


def check_answer(answer: str, tool_results, question: str = "") -> dict:
    """Check one answer. Numbers the user typed in the question are allowed back."""
    data_numbers = numbers_in_data(tool_results) + [n["value"] for n in numbers_in_text(question)]
    claims = numbers_in_text(answer)
    missing = [c["raw"] for c in claims if not supported(c, data_numbers)]
    return {"cited": len(claims), "unsupported": missing, "faithful": not missing}


def run(cases: list[dict]) -> dict:
    """Check every logged call. Returns totals plus each failing case."""
    results = [check_answer(c.get("answer", ""), c.get("tool_results"), c.get("question", "")) for c in cases]
    failures = [{"case": i, **r} for i, r in enumerate(results) if not r["faithful"]]
    cited = sum(r["cited"] for r in results)
    bad = sum(len(r["unsupported"]) for r in results)
    return {
        "cases": len(cases),
        "faithful_cases": len(cases) - len(failures),
        "numbers_cited": cited,
        "numbers_unsupported": bad,
        "passed": bad == 0,
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Faithfulness eval: every cited number must match the tool data")
    parser.add_argument("--cases", required=True, help="JSONL file of logged agent calls")
    args = parser.parse_args()

    lines = Path(args.cases).read_text(encoding="utf-8").splitlines()
    report = run([json.loads(line) for line in lines if line.strip()])

    print(f"\nFaithfulness: {report['faithful_cases']} of {report['cases']} answers fully supported")
    print(f"Numbers cited: {report['numbers_cited']}, unsupported: {report['numbers_unsupported']}")
    for f in report["failures"]:
        print(f"  case {f['case']}: not in the tool data -> {', '.join(f['unsupported'])}")
    print("PASS" if report["passed"] else "FAIL", "(pass = zero unsupported numbers)\n")


if __name__ == "__main__":
    main()
