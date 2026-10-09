# Affinity evidence set

One labelled dataset of everything Kevin has told the Affinity model, for fitting and backtesting a single algorithm
across clubs, nations and players. Built read-only from the quiz folders; nothing else in the repo is touched.

- `evidence.json`: `{"meta": {...}, "records": [...]}`, 579 records.
- `build.py`: rebuilds it (`python3 scripts/affinity/evidence/build.py`). Re-run after a new quiz round is added to it.
- `load.py`: loader and filters (`load`, `select`, `clean`, `gut_clubs`, `gut_players`, `pairs`, `backtest_split`).
- `summary.md`: counts, what each round measured, data-quality issues, which records to backtest on.

## Common fields (every record)

| field | meaning |
|---|---|
| `id` | `<round>.<qid>` (q7 gut ratings: `q7.r1.<player>`), unique |
| `type` | `gut`, `pair`, `everyday`, `tradeoff`, `budget`, `maxdiff`, `likert`, `speed`, `values`, `choice`, `attention`, `verdict` |
| `round` | `q2` ... `q12`, `cascadia`, `players_feedback`, `observations`, `review_2026-09-28` |
| `date` | date of the round (ISO) |
| `qid` | question id in that round's bank/key |
| `domain` | `club` (clubs and nations share the club rubric) or `player` |
| `ms` | response time in ms, when recorded (q4-q12, cascadia) |
| `flags` | data-quality and context tags (list below) |
| `source` | file the answer came from |
| `note` | how to read the values |

Answers are stored in canonical orientation: the quiz pages randomised left/right, but saved the key's side, so `a` is
always the key's first item. `shown_first` (`a`/`b`) says which side was displayed first/left, where the order was saved.

## Entities

Real clubs, nations and players carry `entity = {name, kind, ...}`. `name` is the exact key used in
`scripts/affinity/scores.py` `S` or `scripts/importers/build_usl.py` `A` (clubs/nations; `factors_in` says which) and
`data/suite_data.json` (`comps` lists the competitions it appears in; `heritage` = `data/nations_extra.json` clubs), or
in `scripts/affinity/players/ratings.json` (players; `gender`, `active`). All names already matched exactly; no alias
table was needed. `unmapped: true` marks a name that is not in the catalog (also listed in `meta.unmapped`).

## Types

- **gut**: rating of one item. `value` (null if "don't know"), `scale` [lo, hi], `anonymous` (true = shown as a
  description, not a name), `text` (the description shown), `entity` (the real club behind a blind vignette, from the
  hidden key), `model_at_time` (the model's Affinity when the quiz ran, from results.json), `known` (q7).
- **pair**: Kevin chose `a` over `b`. `choice` is `a`, `b`, `tie`, `skip`, `pass_a`/`pass_b`/`pass_both` (did not know
  that player). `y` = 1 (a), 0 (b), 0.5 (tie), null (no choice). `winner` = name for named pairs. `kind`:
  - `club_profile` (q4, q5 DCE): anonymous clubs; `a.attrs` = attribute -> level index, `a.text` = level text,
    `attr_levels` = all level texts.
  - `club_named` (q6, cascadia g1/g2): two real clubs; `model_at_time` per side (q6).
  - `club_dimension` (cascadia): Portland Timbers (a) vs Seattle Sounders FC (b) on one dimension, names hidden;
    `strength` -3..+3 (+ = Portland), `raw_value` as stored, `portland_was` = the card side Portland was on.
  - `player_named` (q8 h, q10): two real players. q10 adds `group`, `tested` (factors meant to differ) and
    `score_diff_a_minus_b` (audited factor scores at build time).
  - `player_profile` (q8 c, q9): anonymous players; `a.values` = hidden 0-10 factor points (CO in Affinity points,
    PE in penalty points before scaling), as used by scripts/affinity/fit.py.
  - `values_profile` (q11, q12): anonymous players equal on the pitch; `a.tags` = the research-tag features exactly as
    quiz11/fit.py and quiz12/fit.py build them (join with players/values/ and players/values2/ tags); `differs_on`.
- **everyday**: an indirect item with hidden construct loadings. `options` = [{text, loadings}], `choice` = index,
  `loadings` = loadings of the pick. Binary this-or-that items (q6 e, q7 picks) store the right option as the
  negated left loadings.
- **tradeoff**: construct vs construct. `a`/`b` = {construct, text}, `winner` = construct. (q4 ipsative pairs, q6 trait
  comparisons, two stated q2 trade-offs.)
- **budget**: `items` = [{construct, text, points}], `total`.
- **maxdiff**: best-worst over 4 items. `items` = [{construct, text}], `worst` = most damaging, `best` = least bad.
- **likert**: `construct`, `value` on `scale`, `sign` (+1 agree = more of the construct), `loading`, `reversed`,
  `check_of` (the items it repeats). Cascadia importance ratings use `construct = cascadia:<dimension>`, scale 0,1,2,3,5.
- **speed**: q5 timed sort. `value` +1 pulls / -1 pushes, `sign` = expected direction, `agrees`, `ms` (faster = stronger).
- **values**: q11/q12 direct "does this change how you feel about a player?". `value` -2..+2, `tag` (research tag it
  maps to, or null), `tag_sign`, `weight_on_tag` = value x tag_sign.
- **choice**: categorical stated rule or setup answer (q7 s01-s08, cascadia r1-r7, g3). `options`, `choice`, `choice_text`.
- **attention**: attention checks; `passed`.
- **verdict**: Kevin's direct judgement on model output. `kind`: `list_position` (players/feedback.json: `verdict`
  agree/maybe/unknown, `list_rank`, `model_at_time`, `label` 1 = model about right), `rule`, `match_observation`
  (players/observations.json, `direction` -1), `factor_override` (his factor calls in the 2026-09-28 re-rate review,
  from research/decisions.py `FACTORS`).

## Constructs

`meta.constructs` is the glossary. Club factors use the scores.py letters C V H O plus T for Team (stored in slot S of
the tuple). Sub-constructs: CL CY CG CA (culture), TP TB TS TI (team), VC VW VA VF VI VP (values); others TR, TROPHY,
REC, LOC, TRIBE, ASSOC, ASSOC_DOWN, PEN, FORGIVE, DECAY, UNDER, NOV, WOM, LOYAL; baggage codes (racism, state, pe, ...).
Player factors: CH WK LO AB ST LE plus CO, PE. **Collisions**: in q7 picks `CA` = causes, `TR` = trophies and `LOC` =
hometown, not the club meanings; use `domain` with the code (`player.CA` vs `club.CA`).

## Flags

`dont_know`, `skipped_dont_know`; `blind_vignette_recognisable` (Kevin said the "anonymous" clubs were often
recognisable); `holdout_for_round4_model`; `familiarity_bandwidth_confound` (q6 club pairs); `name_recognition_confound`
(q8 named pairs); `controlled_setting` (q10); `fast_response_under_1s`; `ambiguous_wording`; `conflicts_with_<id>`;
`single_trait_dominance_check`, `picked_worse_level`; `no_baggage_attribute` (q8 profiles); `d_optimal_near_tossup` (q9);
`no_research_tag`; `kevin_found_format_hard`, `dropped_from_fit` (q7 budget); `names_hidden_until_end`,
`existing_supporter_of_a` (cascadia); `scenario_not_a_club`; `summary_only`, `order_inferred` (from docs, no raw answer);
`superseded_by_later_rerates`.

## Provenance

| round | date | source (scripts/affinity/...) | content |
|---|---|---|---|
| q2, q3 | 2026-09-28 | docs/supporter-profile.md | summaries only; 3 records with `summary_only` |
| q4 Blind Draw | 2026-09-29 | quiz4/answers.json, key.json, questions.json, results.json | 75 |
| q5 Blind Draw II | 2026-09-29 | quiz5/answers.json, key.json, questions.json, results.json | 87 |
| q6 This or That | 2026-09-29 | quiz6/answers.json, key.json, questions.json | 90 |
| cascadia | 2026-09-30 | research/cascadia/answers.json, key.json, questions.json | 41 |
| q7 players | 2026-10-06 | quiz7/raw/responses/kevin.json, key.json, questions.json | 82 |
| q8, q9, q10 | 2026-10-06 | quizN/raw/responses/kevin.json, key.json | 50, 30, 30 |
| q11, q12 values | 2026-10-07 | quizN/raw/responses/kevin.json, key.json, questions.json | 36, 36 |
| verdicts | 2026-09-28 to 10-06 | players/feedback.json, players/observations.json, research/decisions.py | 19 |

Not available: round 1 (the 51-question interview) and the raw answers of rounds 2-3 (only summaries survive); the
deprecated family questionnaire (scripts/affinity/family) stores no answers.

## Could not map

- `George Hemmings` (Aston Villa, players/observations.json): not in players/ratings.json; kept with `unmapped: true`.
- By design, anonymous profiles (q4/q5 DCE clubs, q8/q9 players, q11/q12 values players) and the cascadia scenarios have
  no real entity. The q4/q5 vignettes do map (hidden key).
- Cascadia dimensions (`cascadia:<dim>`), q7 budget factors (`F_*`) and q7 pick constructs have no exact scores.py
  field; the glossary gives the nearest factor.
- Rank numbers in players/feedback.json repeat (two 8s, two 10s): they are positions in different lists (not recorded which).
