# Findings

Newest first. Every number comes from `python run_evals.py` or an eval command run on the date shown.

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

NFL overs are 62% of NFL picks and hit 3.6 points below what the app states. With 4,207 picks that is roughly 4 to 5 standard errors from zero, so it is not noise. Unders are close to honest. This narrows the Nov 2 finding: the mid-range overconfidence is mainly an overs problem.

### 2. NBA leans the other way

| NBA side | Picks | Says | Hits | Bias |
| --- | --- | --- | --- | --- |
| Under | 662 | 55.3% | 59.2% | +3.9 |
| Over | 464 | 51.0% | 56.9% | +5.9 |
| Team | 225 | 52.0% | 49.8% | -2.2 |

NBA props hit more often than stated, overs most of all. Smaller sample (about 2.5 standard errors for overs), so treat as likely, not proven. Possible cause: the NBA overs correction added in the H2 history work now overcorrects. NHL props are within about 1 point on both sides.

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

### Recommended app changes (need a plan before building)

1. NFL overs: shrink stated probability toward the market for NFL overs, or add an overs correction like the NBA one, then re-check with `--by side`.
2. NBA: review the NBA overs correction; it may now understate picks.
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
