# Findings

Newest first. Every number comes from `python run_evals.py` or an eval command run on the date shown.

## 2026-11-13 (evening): Which warning signs on a parlay leg mean anything

Before building a "Check my slip" feature, seven candidate warning signs were tested on three NFL seasons (about 46,000 bets, counted per bet). The rules, the flags and the pass bar were written down before any result was looked at: a flag passes only if its legs hit at least 3 points under their stated chance on a held-out season, past noise, with the same direction on the other two.

| Warning sign | Held-out gap | Noise | Verdict |
| --- | --- | --- | --- |
| Price looks 7%+ too good | -4.7 | 1.9 | **Pass** |
| Plus-money price the app rates above break-even | -2.8 | 1.5 | Fail (bar was 3.0) |
| Line moved against it since morning | -2.9 | 3.0 | Fail (one season, inside noise) |
| Lone outlier price | +2.0 | 1.6 | Fail |
| Alternate line only one book posts | +0.4 | 1.1 | Fail |
| Modelled price | +1.7 | 0.7 | Fail |
| Heavy juice (shorter than -220) | +1.9 | 1.1 | Fail (hits more than stated) |

- One sign survived. Legs whose price looked 7%+ too good said 25.8% and hit 21.1% on the held-out season, and ran 5.6 points under on the other two.
- Legs with no flag were honest: said 49.7%, hit 49.8% over 43,007 bets.
- The plus-money flag missed the bar by 0.2 points. The bar was not moved after the fact.
- A player's recent record, streak and matchup were not candidates: an earlier backtest showed they do not beat the line.

**Live record check** (`python -m evals.slipcheck --sport nfl`): the record holds only 6 bets that would be tagged Shaky, so the eval answers "too few to say". The 2,137 untagged bets say 55.3% and hit 54.4% (bias -0.9, noise 2.2): consistent with the backtest. This eval becomes meaningful as tagged bets accumulate.

## 2026-11-13 (afternoon): Tickets win as often as they claim

First ticket (parlay) eval, `python -m evals.tickets`. A long-shot ticket should lose most of the time, so the test is expected wins (the stated chances added up) against actual wins, with z = (won - expected) / spread. |z| under 2 is consistent with the claim.

| Tier | Tickets | Says | Hits | Expected wins | Won | z | ROI (shown price) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| All tickets | 384 | 24.9% | 25.0% | 95.8 | 96 | +0.03 | -8.3% |
| Cash (Tonight's tickets) | 160 | 36.0% | 37.5% | 57.6 | 60 | +0.41 | +5.2% |
| Game Script (v114) | 122 | 13.2% | 13.9% | 16.1 | 17 | +0.25 | +9.1% |
| NHL script short | 17 | 38.9% | 41.2% | 6.6 | 7 | +0.19 | +0.9% |
| NHL script mid | 16 | 25.2% | 12.5% | 4.0 | 2 | -1.17 | -51.6% |
| Stacks (retired) | 15 | 22.4% | 6.7% | 3.4 | 1 | -1.48 | -65.4% |
| NBA script short | 13 | 39.4% | 53.8% | 5.1 | 7 | +1.07 | +12.3% |
| NBA script long | 13 | 9.3% | 0.0% | 1.2 | 0 | -1.15 | -100% |

- Across all 384 settled tickets the app expected 95.8 wins and got 96. The joint chances (legs plus the measured correlation tables) are honest.
- The two big tiers are both on target. Their positive ROI is inside noise: one ticket's payout swings so much that 160 tickets give an ROI band of roughly +/-23 points, so this says nothing yet about profit.
- Every small tier is inside noise (|z| under 1.5). The new NBA and NHL Game Script tiers started Nov 11; recheck them after a few weeks.
- Pushes and voids are left out (a ticket with a pushed leg is a no-result by the app's own rule).

## 2026-11-13: All-sport scoreboard, NFL overs, and a CLV caveat

### Scoreboard

| Sport | Picks | Says | Hits | Bias | ECE | CLV (price) | CLV (line, model) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NFL | 6,821 | 53.4% | 50.7% | -2.8 | 3.6 | +0.59% | +2.91% |
| NBA | 1,351 | 53.3% | 56.8% | +3.6 | 5.9 | +1.20% | +1.93% |
| NHL | 1,319 | 57.2% | 57.2% | +0.0 | 4.3 | +0.58% | +5.12% |
| MLB | 393 | 52.1% | 50.1% | -1.9 | 8.5 | +0.97% | +14.54% |
| NCAAF | 112 | 44.0% | 47.3% | +3.4 | 11.3 | +1.79% | -4.50% |

Bias = hit rate minus stated probability (negative = overconfident). MLB and NCAAF are too small to act on.

### 1. NFL overconfidence is mostly overs

| NFL side | Picks | Says | Hits | Bias | ECE |
| --- | --- | --- | --- | --- | --- |
| Over | 4,207 | 52.7% | 49.1% | -3.6 | 4.8 |
| Under | 2,094 | 56.2% | 54.7% | -1.6 | 2.1 |
| Team | 520 | 48.3% | 47.5% | -0.8 | 3.9 |

NFL overs are 62% of NFL picks and hit 3.6 points below what the app states. Unders are close to honest. This narrows the Nov 2 finding: the mid-range overconfidence is mainly an overs problem. (See section 5: the significance here was overstated, and the cause is rush yards.)

### 2. NBA leans the other way

| NBA side | Picks | Says | Hits | Bias |
| --- | --- | --- | --- | --- |
| Under | 662 | 55.3% | 59.2% | +3.9 |
| Over | 464 | 51.0% | 56.9% | +5.9 |
| Team | 225 | 52.0% | 49.8% | -2.2 |

NBA props hit more often than stated, overs most of all. Counted by lines, not bets, so treat as unproven until rerun with `--per-bet`.

**Rerun per bet (same day):** under 401 bets, +2.4 (noise 5.0); over 301 bets, +2.0 (noise 5.8); team 89 bets, +2.1 (noise 10.6). Every side is inside noise: the +5.9 came from counting ladder rungs. No change to the NBA lean (v133) is supported. Possible cause: the NBA overs correction added in the H2 history work now overcorrects. NHL props are within about 1 point on both sides.

### 3. Price CLV is small but positive everywhere

Picks beat the closing price by about 0.6% (NFL, NHL) to 1.2% (NBA) when the line did not move. About half of price-basis picks close at exactly the same price (median 0%). By NFL source, `card` (+1.7%) and `team` (+1.6%) beat the close most; `usage` (+0.2%), `usageshare` (+0.3%) and `lowline` (-0.2%) barely move it.

### 4. Line-basis CLV: the sign is real, the size is not

When the line moves, the close is translated to the pick's line by the model. Those numbers look far better than real price moves (NFL +2.9% vs +0.6%, MLB +14.5%). Test: if the size were real, picks with bigger translated CLV should hit more often.

| Line-basis CLV (NFL, NBA, NHL) | Picks | Says | Hits | Bias |
| --- | --- | --- | --- | --- |
| 0% or worse | 1,123 | 51.5% | 46.7% | -4.8 |
| 0 to 5% | 739 | 52.0% | 52.8% | +0.8 |
| 5 to 15% | 937 | 51.8% | 52.7% | +1.0 |
| 15% or more | 391 | 51.9% | 52.7% | +0.7 |

Picks whose line moved against them hit 6 points less, so the direction is meaningful. But 0-5%, 5-15% and 15%+ all hit about the same, so the translated size carries no extra information and overstates edge. Line-basis CLV should not be shown or summed as if it were real price CLV.

### 5. Correction (same day): count bets, not lines, and the fix already exists

Two claims above were too strong.

**The pick counts overstate certainty.** The record saves several lines for one player in one game (one game had Jayden Daniels rush overs at 34.5, 35.5, 37.5 and 38.5). Those win or lose together. Counted once per player-game-side, NFL overs are **1,267 bets over 100 games**, not 4,207 independent picks, and the bias is -3.5 against a noise band of about +/-2.8: still past noise, but only just, not "4 to 5 standard errors". The evals now have `--per-bet` for this, and the scoreboard always counts bets.

**The miss is rush yards, and the app already corrected it.** Per bet:

| NFL market, side | Bets | Says | Hits | Bias | Noise |
| --- | --- | --- | --- | --- | --- |
| Rush yards over | 359 | 54.7% | 46.7% | -8.1 | 5.3 |
| Rush yards under | 197 | 60.9% | 65.3% | +4.4 | 7.1 |
| Reception yards over | 754 | 53.3% | 50.9% | -2.4 | 3.6 |
| Reception yards under | 339 | 61.5% | 64.3% | +2.7 | 5.4 |
| Pass yards over | 101 | 55.9% | 58.2% | +2.3 | 10.0 |

Overs too high and unders too low on the same stat means the app's line for rushing sat too high. The app found the same thing in four seasons of history and shipped a fix on Nov 6-7 (v157: every NFL rush-yards chance moved 0.10 log-odds toward the under, about 2.5 points). Nearly all of the rush picks above were made before v157; only 17 rush picks have been recorded since. So this eval independently confirms the v157 problem, and cannot yet say whether v157's size is enough. The record's legs do not store the lean, so before/after is split by date (`--since 2026-11-07`).

### Recommended next steps

1. NFL rush yards: no new app change now. v157 is measured on four seasons; 359 live bets is not enough to override it. Re-check with `python -m evals.calibration --sport nfl --by market --per-bet --since 2026-11-07` once a few weeks have settled, and only then judge whether 0.10 is too small.
2. NBA: recheck with `--per-bet` before reading anything into the +5.9 on overs; the same line-counting applies.
3. CLV display: anywhere the app shows or totals CLV, use price-basis only, or show line-basis as direction only.
4. Sources: `usage`, `usageshare` and `lowline` show almost no price edge; worth checking whether they earn their spot on the board.

## 2026-11-02: NFL calibration baseline

6,618 settled single picks. Expected calibration error: **3.59 points**.

| Range | Picks | Says | Hits | Gap |
| --- | --- | --- | --- | --- |
| 45-50% | 1,109 | 49.1% | 44.3% | -4.8 |
| 50-55% | 3,860 | 51.4% | 48.1% | -3.4 |
| 55-60% | 381 | 57.0% | 53.8% | -3.2 |
| 60-65% | 304 | 62.5% | 64.5% | +1.9 |
| 65-70% | 168 | 67.5% | 72.0% | +4.5 |
| 90-95% | 144 | 92.6% | 93.1% | +0.4 |

- Picks stated between 45% and 60% (about 80% of all picks) hit 3 to 5 points less than stated. At this sample size the gap is far larger than random noise.
- Picks stated at 60% and above are well calibrated or slightly underconfident.
- Leading hypothesis: selection bias (winner's curse). Picks are saved because they look good, so the selected set runs optimistic.
- Next: split by pick source and by over vs under to find what drives the gap. (Done 2026-11-13: mostly overs.)
