# Affinity: one model for clubs, nations, players and leagues

Rebuilt 2026-10-09 (Kevin: "build one monolithic model across all teams, nations, players, leagues ... get rid of this
piecemeal system"). The rules and judgements it honours, in Kevin's words, are in docs/preferences.md. The earlier,
step-by-step history of the model is in git (docs/affinity.md before 2026-10-09) and docs/supporter-profile.md.

## Live model: the blind test (since 2026-10-12)
Kevin, after comparing his blind-test results with the model below: "ship the blind model. It's probably less biased."
Live Affinity now comes from scripts/blind (README.md there): researched facts only (CODEBOOK.md, coded/*.json),
weighted by Kevin's own answers to the 100-question blind test (answers/kevin.json). `python3 scripts/blind/live.py`
writes data/suite_data.json, nations_extra.json, players.json and the weights (params.json "blind"); then build.
To update: retake the test, copy the new answers into answers/kevin.json, rerun live.py.
Comparison with the model below on the day: rank agreement 0.72 for clubs and nations, 0.75 for players
(scripts/blind/comparison_2026-10-12.md). The categories model below is kept as history and still runs, but nothing
reads its output any more: do not run affinity.py over the live data.

## Run it
- `python3 scripts/affinity/affinity.py`: scores every club, women's club, nation and player; writes data/suite_data.json
  (base, bonus, hai), data/nations_extra.json, data/players.json and players/ratings.json. Then `python3 scripts/build.py`.
- `python3 scripts/affinity/fit.py [--write]`: refits params.json to Kevin's answers (scripts/affinity/evidence) and
  prints the leave-one-round-out backtest. Needs numpy and scipy. Refit after a new quiz round.
- After the nightly sync conflicts on suite_data.json: take main's file and rerun affinity.py.

## The model: one weighted average (since 2026-10-12)
Kevin, 2026-10-12: "I want to get rid of all the bonuses and penalties. I want the ratings to live entirely within the
categories and their weights ... K.I.S.S." So there is one step:

**Affinity = 10 x the weighted average of eight ratings out of 10.** Weights in params.json, fitted by fit.py.

| Clubs, women's clubs, nations | weight | Players | weight |
|---|---|---|---|
| Integrity | 32% | Integrity | 24% |
| Culture | 13% | Team player | 17% |
| Connection | 13% | Character | 15% |
| Values | 12% | Connection | 11% |
| Record | 11% | Loyalty | 9% |
| Team | 7% | Greatness | 8% |
| History | 7% | Legacy | 8% |
| Ownership | 5% | Joy to watch | 7% |

- **Integrity** (new): 10 for a clean record, minus each documented wrong. Clubs and nations: the 6th field in scores.py
  (and build_usl.py), with the items in the note ("Racism -0.9; Super League -0.5"); inputs.py flags a value that differs
  from its items. Converted from the old hard lines at 0.36 Integrity points per hard-line point (racism x1.25, private
  equity and multi-club x0.7, the old type weights), so State-backed -25 became -9 and a 2021 Super League exit -0.5.
  Players: computed from their incidents (inputs.py P_POINTS, in Integrity points: abuse 14, racist abuse and
  match-fixing 11, violent conduct and authoritarian ambassador 5.6, tax fraud 4, doping 3.2, forced transfer and a
  money-league move 2.4 (5.6 / 3.2 / 1.6 by age), rival move 1.6; acquittal 30%, apology 60%).
- **Record**: a club's last 10 league seasons (performance.py; 5 when not judged), a nation's FIFA ranking and last
  tournaments. Players have no separate record: Greatness, Legacy and Joy to watch are ratings like the others.
- **Connection** (new as a rating): 5 with no tie, plus 0.8 per connection point (params k_per_point), within 0-10.
  Points: distance from Sacramento, Kevin's other teams and their rivals (big4.py), linked clubs (association.py), brand
  and bandwagon pulls; for players the clubs they played for. Roots count as connection points: hometown +4, home
  nation +20 (nations) or +5 (US internationals), ancestry (nations 0.3 per %, cap 7.5; clubs and players 0.2 per %, cap 5).
- **Bonuses** are gone: exceptional good work now sits in the ratings. Clubs: Values +0.45 x the researched points
  (baked into scores.py, e.g. "Values +2.3 for Fans re-founded the club"); players: Character, the same 0.45
  (players/audit/good_work.json, applied with the values tags in players/model.py).
- Team includes the squad interplay and the best current players; History includes the icons (players_link.py).
- The scale is narrower than before (a linear average has no floor at 0): Manchester City 0 -> 35, Athletic Club 92 -> 89.
  Thresholds tied to the scale moved with it (old x0.58 + 37): disliked club 50 -> 66 (association.py), player club
  seasons neutral 50 -> 66 (affinity.py per_season), nation club links 63 / 35 -> 73.5 / 57 (interplay.py), player
  neutral 60 -> 71.5 (players_link.py), "clubs you'd enjoy" 65 -> 75 (app Leagues).
- In the app, base = A minus what roots add and bonus = what roots add (drawn apart in the lists).
- **Leagues**: a league's Affinity is its median club's, shown with how many clubs reach 75.
- **Years ahead** (active player lists only) is unchanged and is not part of Affinity.

Backtest of the switch (leave-one-round-out, 372 items; old model with hard lines and bonuses -> one weighted average):
deciders 13 -> 13 of 19, named player pairs 9 -> 12 of 15, nation gut 15.1 -> 15.1 of 16, mystery nations 11 -> 11 of 12,
club gut 23.8 -> 23.2 of 26, club profiles 24 -> 24 of 28, player profiles 38 -> 39 of 48. Checks: gut r 0.786 -> 0.786,
real-club pairs 19 -> 19 of 36, named player pairs 20 -> 19 of 29, player gut r 0.372 -> 0.345, Timbers +0.4 -> +0.6 over
Sounders; Dortmund over Union and Napoli over Fiorentina hold. One rerate: Oakland Roots Values 10 -> 8.8 (the only club at
10 from research alone; a Common Goal pledge sits with Freiburg and Union, 10 is for clubs their fans saved).

Parameters: scripts/affinity/params.json. Inputs: inputs.py (measurements only), players/model.py (player research
loader), performance.py, big4.py + proximity.py, association.py, interplay.py, players_link.py, heritage.json.
The sections below describe the earlier model (hard lines, geometric record blend) and stay as history.

## Backtest (2026-10-09)
Evidence: 579 recorded answers (scripts/affinity/evidence, summary.md). Fitted on the 238 that label the score itself:
26 club gut ratings, 28 anonymous club profiles, 50 anonymous player profiles, 15 controlled named player pairs.
Leave-one-round-out (each quiz round predicted by a fit on the others):

| | rebuilt | before |
|---|---|---|
| held-out log loss (lower is better) | 0.425 | 0.462 |
| club gut orderings | 89% | 90% |
| anonymous club profiles | 79% | 75% |
| anonymous player profiles | 79% | 75% |
| controlled named player pairs (round 10) | 9 of 15 | 9 of 15 |

Checks on the final scores (not fitted): club gut correlation 0.80 (was 0.78; same rank order, rho 0.81, but the clubs
he rated 0-3 now sit further down); round 6 real-club pairs 19 of 36 (was 16); round 8 named player pairs 18 of 29 (same);
player gut ratings r 0.36 (was 0.34). Timbers above Sounders on merit (77.7 v 77.1).

What the sweep showed:
- Kevin's stated weights generalise better than refitted ones (strong prior won on every held-out round).
- Penalties should be harsher: freeing the hard-line scale improved every setting; it settled at 1.66, then 1.95 with the nations round.
- Separate penalty scales for clubs and players fit no better than one.

## Nations round (quiz 13, 2026-10-09)
16 blind national teams rated 0-10, 12 mystery-nation pairs, 5 direct questions (scripts/affinity/quiz13).
- Out of sample, before it saw any of it, the model ranked his 16 gut ratings at rho 0.88 (r 0.80) and called 10 of
  12 pairs; refitted with the round, 11 of 12. His top: Denmark 8; Japan, Germany, Portugal, Netherlands 7. Bottom:
  Croatia and Turkey 1, Iran and Argentina 2.
- A free democracy won every pair it was in: over a top-10 record, over loud fans plus a world-title history, over a
  large share of his ancestry, over good conduct plus loud fans. Racism beat ancestry and winning. A well-run
  federation beat a relentless team; a relentless team beat world-champion history.
- Direct: a government that jails journalists counts "a lot"; home nation vs ancestral nation "depends on the match";
  players at clubs he likes "a lot more"; winning lately "a bit more"; homophobic chants "a lot less".
- Effect: the shared hard-line scale rose to 1.95 and the team record share to 0.10; Kevin kept the US home bonus at +20.

## German decider (2026-10-09)
Union Berlin v Dortmund, blind, the Cascadia format (scripts/affinity/research/berlin_dortmund: sourced dossier, cards,
answers). Weighted by his importance ratings: Dortmund +8 of +/-100 (record strongly, ground, academy, history, direction)
against Union on sponsors, community, owner, fan voice, women's team, squad. Gut: Dortmund, and switching to Union would
not feel like a betrayal. Scenarios: Champions League with an arms partner 8, mid-table fan-built ground 7, relegated and
sold out 4. Rules: arms partner "a little", stock listing "a little", selling young players neutral, shared anthem with
Liverpool "some", easy to watch on US TV "a lot" (both clubs share the US deal).
Both deciders (Portland over Seattle, Dortmund over Union) and their six scenarios joined the fit (round 'dec'; held out,
the model already called 9 of 10). Team record share 0.10 -> 0.124. Dortmund 81.0 over Union 80.2; Timbers 77.2 over
Sounders 77.1, still on merit.

## Italian decider (2026-10-09)
Napoli, Fiorentina, Atalanta, three-way and more blind (no names, trophy counts or years; scripts/affinity/research/italian).
Ranked by his importance weights: Atalanta +6, Napoli +2, Fiorentina -8 (each card: best +1, worst -1). Atalanta first on
community, academy, sponsors, squad, voice, ground; Napoli on supporters, record, following, direction; Fiorentina on
owner and women's team. Gut: he'd follow Atalanta. Rules: second club "a little", pending trial "about half", American
owners neither way, racist chants and brawls worse than an ultras-owner feud.
Applied like Cascadia (factor changes where his rankings contradicted the model): Atalanta Values 6 -> 7; Napoli Values
7 -> 6.5, Ownership 5 -> 4.5 (owner's false-accounting trial at half). The three rankings and three scenarios joined the
fit, but the refit (record share 0.14) matched fewer decider items (15 of 19 vs 17) and put Seattle above Portland, so
params.json keeps the record share at 0.124 (do not refit with --write without checking the deciders and Timbers v
Sounders). Result: Atalanta 71.1, Napoli 69.8, Fiorentina 68.6.
Then the dossier's ultras findings were added as hard lines, at the usual scale (Kevin: "It should count no?"): Atalanta
racism -3 (2023 end closure) and violence -4 (2025 brawl, group broken up by bans); Napoli violence -3 (about 200 fans
detained abroad, 2026); Fiorentina racism -2 (2023 suspended closure, a five-year ban). Result: Fiorentina 65.5, Napoli
65.2, Bologna 64.0, Atalanta 58.8 (6th).

## Decisions taken in the rebuild
- Nations now have a record (FIFA ranking and tournaments) like clubs and players. Small nations are ranked among all
  211 FIFA members, so they aren't judged against the top of the world.
- Liverpool, Dortmund and Celtic linked through You'll Never Walk Alone (Kevin's own example, 2026-09-28).
- Retired: rescore.py, unified.py, players/fit.py, players/build_lists.py, the track-record multiplier, the separate
  player penalty scale and caps per add-on (big4 +/-6, player connection inside the role score). One-off migration
  scripts moved to scripts/affinity/archive/. The quiz banks (quiz4-12) are history: some import the v1 player model.

## Open questions for Kevin
- Desailly's tabloid-only allegation still counts in full; national-team switching is not tagged.
- Incident decay (old wrongs fade) is in the evidence (round 5) but club incidents carry no dates, so it isn't applied.
