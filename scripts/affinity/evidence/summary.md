# Evidence summary (built 2026-10-09)

579 records from 12 sources; 531 usable as labels (`load.clean` drops don't-knows, passes, skips, attention checks,
summary-only and scenario records). One name unmapped (George Hemmings, observations.json).

Pairs by kind: club_profile 28, club_named 38, club_dimension 14, player_named 60, player_profile 50, values_profile 48.
Records by type: pair 238, everyday 98, gut 69, tradeoff 48, values 24, speed 22, likert 19, verdict 19, maxdiff 18,
choice 16, budget 6, attention 2.

## What each round measured
| round | domain | constructs |
|---|---|---|
| q2/q3 | club | factor weights, two stated trade-offs (summaries only) |
| q4 Blind Draw | club | everyday (16 constructs), ipsative factor pairs, DCE (C V H O T TR LOC + baggage), 13 blind vignettes |
| q5 Blind Draw II | club | sub-constructs, DECAY, TROPHY, 4 budgets, MaxDiff over 12 baggage types, DCE, 22 speeded phrases, 13 vignettes |
| q6 This or That | club | 20 everyday, 34 trait comparisons, 36 real-club head-to-heads |
| cascadia | club | 14 dimension importances, Portland vs Seattle per dimension, rules, scenarios |
| q7 | player | 24 quick picks, 40 named gut ratings (22 don't know), MaxDiff over player baggage, setup rules, budget |
| q8 | player | 30 named head-to-heads, 20 anonymous profile pairs |
| q9 | player | 30 anonymous profile pairs (D-optimal) with baggage |
| q10 | player | 30 controlled named pairs (15 passed) |
| q11, q12 | player | values pairs (24 each) and direct answers (12 each) |
| verdicts | both | player walkthrough, one observation, 6 factor calls from the 2026-09-28 review |

## Data quality
- Attention checks passed. 4 of 5 reversed repeats consistent (forgiveness splits: forgives changed people, some acts never).
- Cross-round tensions: women's game (watch vs values), old ground vs new ballpark, trophies, how much Greatness counts,
  the old club-connection rule (superseded 2026-10-07).
- Confounds: q6 club pairs follow familiarity (EFL clubs won 18 of 26); q8 named player pairs follow name recognition.
- Leakage: the current model was tuned on nearly all of this. Backtest a rebuilt model leave-one-round-out.

## Best records for backtesting
- Clubs: 26 named gut vignettes (q4, q5), today's model r 0.778. Cascadia dimension pairs (factor signs). q6 pairs only
  with a familiarity covariate. Weights: DCE, trait comparisons, ipsative pairs, budgets, MaxDiff (penalty order).
- Nations: no direct evidence. Fit through shared club constructs; a short nation round would be needed to test.
- Players: q10 controlled pairs (today 9 of 15), q8/q9 profile pairs (weights), q11/q12 values (Character sub-weights),
  q7 gut (r 0.34) and feedback verdicts as weak checks.

## Added 2026-10-09: round 13 (nations)
Read directly by fit.py from quiz13/raw/responses/kevin.json and quiz13/key.json (16 nation gut ratings as rounds q13g, 12 mystery-nation pairs as q13p). Nations now have their own test.
