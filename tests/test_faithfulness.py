"""Tests for the faithfulness eval. No database, no LLM."""

from evals.faithfulness import check_answer, numbers_in_data, numbers_in_text, run

BOARD = {"picks": [{"player": "Sample Player One", "line": 24.5, "price": -118, "probability": 0.6123}],
         "record": {"bets": 1267, "stated": 0.5376, "hit_rate": 0.5028, "bias": -0.0348}}


def values(text):
    return [n["value"] for n in numbers_in_text(text)]


def test_reads_percents_odds_decimals_and_thousands():
    assert values("He is 61% to clear 24.5 at -118 over 1,267 bets") == [61.0, 24.5, -118.0, 1267.0]
    assert numbers_in_text("61.2%")[0] == {"raw": "61.2%", "value": 61.2, "percent": True, "decimals": 1}
    assert values("a bias of −3.5 points and +120") == [-3.5, 120.0]


def test_dates_ordinals_and_words_with_digits_are_not_claims():
    assert values("On 2026-11-07 and 11/13 the 3rd pick, v157, id a1b2") == []


def test_data_numbers_include_nested_values_but_not_booleans():
    assert sorted(numbers_in_data({"a": [1, {"b": 2.5}], "c": True, "d": None, "e": "line 7.5"})) == [1.0, 2.5, 7.5]


def test_a_faithful_answer_passes():
    answer = "Sample Player One is 61% to go over 24.5 at -118. Overs hit 50.3% against a stated 53.8% across 1,267 bets, a bias of -3.5 points."
    assert check_answer(answer, BOARD) == {"cited": 7, "unsupported": [], "faithful": True}


def test_rounding_must_match_the_written_precision():
    assert check_answer("61.2% to hit", BOARD)["faithful"]
    assert check_answer("61% to hit", BOARD)["faithful"]
    assert not check_answer("62% to hit", BOARD)["faithful"]
    assert not check_answer("61.3% to hit", BOARD)["faithful"]


def test_a_number_the_model_worked_out_itself_is_flagged():
    # 100 - 61 = 39 is the model doing math: not allowed, even though it is "right"
    r = check_answer("There is a 39% chance it misses.", BOARD)
    assert r == {"cited": 1, "unsupported": ["39%"], "faithful": False}


def test_an_invented_number_is_flagged_and_named():
    r = check_answer("He has cleared this in 8 of his last 10.", BOARD)
    assert r["unsupported"] == ["8", "10"]


def test_numbers_from_the_question_may_be_repeated():
    r = check_answer("Over the last 10 games, he is 61% to clear 24.5.", BOARD, question="How has he done over his last 10 games?")
    assert r["faithful"]


def test_a_percent_does_not_match_a_bare_fraction_by_accident():
    # 0.6123 supports "61%" but the plain number 61 only matches if 61 itself is in the data
    assert not check_answer("He scored 61 last night.", {"probability": 0.6123})["faithful"]
    assert check_answer("He scored 61 last night.", {"points": 61})["faithful"]


def test_run_totals_and_lists_failures():
    report = run([
        {"question": "", "tool_results": BOARD, "answer": "61% at -118."},
        {"question": "", "tool_results": BOARD, "answer": "A lock at 75%."},
        {"question": "", "tool_results": BOARD, "answer": "No numbers here."},
    ])
    assert (report["cases"], report["faithful_cases"], report["numbers_cited"], report["numbers_unsupported"]) == (3, 2, 3, 1)
    assert report["passed"] is False
    assert report["failures"] == [{"case": 1, "cited": 1, "unsupported": ["75%"], "faithful": False}]
