# Pick 'em backtests (2026-10-10)

- `node scripts/pickem/backtest.js`: pick strategies, walk-forward over every played league match (1,423 at the time).
- `node scripts/pickem/sweep.js`: model settings (half-life, regression k, head-to-head, draw calibration, rho weight).

Walk-forward = the model sees only results from before each match day. Tunable choices are picked on the first half of
each season's match days and judged on the second half. The picks stored in data/suite_data.json (fixture fields 6-7)
are not a fair baseline: for leagues imported mid-season they were computed after the matches were played.

Result (2026-10-10): the current rule (maximise 2 x P(result) + 1 x P(exact)) scored 1.062 points a match and was not
beaten. Every variant scored within noise or worse: never picking a draw 1.057, sharpen/flatten 1.058, favourite by one
1.053, blend with the league's own scorelines 1.041, the draw-zone predicted score 1.031, the most likely exact score 0.868.
Model settings tuned on the first half lost points on the second half (k 25: +25 then -29; half-life 21: +17 then -56).

## Betting market blend (2026-10-10)
`python3 scripts/odds/history.py` then `node scripts/pickem/blend.js`. Over 750 played matches with odds (six European leagues
and MLS, football-data.co.uk): log loss 1.052 model only, 1.022 at w 0.5, 1.016 at 0.75, 1.015 market only; pick 'em 786 -> 813
(0.75) -> 819 (market only) points. Live: mktW 0.8 in the app (Settings), odds from the ESPN sync.
