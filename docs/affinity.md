# Affinity: one model for clubs, nations, players and leagues

Rebuilt 2026-10-09 (Kevin: "build one monolithic model across all teams, nations, players, leagues ... get rid of this
piecemeal system"). The rules and judgements it honours, in Kevin's words, are in docs/preferences.md. The earlier,
step-by-step history of the model is in git (docs/affinity.md before 2026-10-09) and docs/supporter-profile.md.

## Run it
- `python3 scripts/affinity/affinity.py`: scores every club, women's club, nation and player; writes data/suite_data.json
  (base, bonus, hai), data/nations_extra.json, data/players.json and players/ratings.json. Then `python3 scripts/build.py`.
- `python3 scripts/affinity/fit.py [--write]`: refits params.json to Kevin's answers (scripts/affinity/evidence) and
  prints the leave-one-round-out backtest. Needs numpy and scipy. Refit after a new quiz round.
- After the nightly sync conflicts on suite_data.json: take main's file and rerun affinity.py.

## The model (same four steps for everything)
1. **Character** Q = weighted average of the character factors x 10 (0-100).
   - Clubs, women's clubs, nations: Values, Culture, History, Team, Ownership. Weights are Kevin's stated weights
     (round 5: 26 / 23 / 16 / 15 / 10 of 90); the fit left them in place.
   - Players: Character (with his values tags, rounds 11-12), Team player, Loyalty (fitted in rounds 8-10).
   - Measurements are pure: the minor penalties folded into the factors on 2026-10-02 were unfolded back into hard lines.
     Team includes the squad interplay (homegrown share for clubs, club links for nations) and the best current players;
     History includes the icons (players_link.py).
2. **Hard lines** come off character: Q+ = Q - hard x (points), floored at 0, no cap ("shitheads need not apply").
   One list for every entity: racism, abuse, match-fixing, state ownership or a government's record, violence, private
   equity, leveraged buyouts, the Super League, money-league moves, betting or arms money, overspending, multi-club
   feeders, relocation. Club points are researched per club (scores.py notes); player points follow Kevin's best-worst
   ranking (inputs.py P_POINTS; acquittal 30%, apology 60%). One scale, `hard` = 1.95 (1.66 before the nations round): fitted separately,
   clubs and players both landed at 1.65-1.7, and a separate weight for a government's record fit no better (round 13). If hard lines take character to 0, nothing is added back.
3. **Record** R = recent record 0-10, blended geometrically: A0 = 100 x (Q+/100)^(1-pi) x (R x 10/100)^pi, so a weak side
   drags the total down.
   - Clubs: the last 10 league seasons (performance.py, top flight and USL only; others are not judged and get the
     neutral 5). Nations: FIFA ranking percentile and the last two World Cups and continental championship
     (research/nations_perf.json). pi = 0.10 for teams ("winning matters little").
   - Players: Greatness 40%, Legacy 35%, Joy to watch 25%; pi = 0.4, Kevin's decision ("all while delivering
     performances worthy of the highlight reels and the history books").
4. **Connection and roots** A = A0 + conn x (connection, capped at +/-10) + roots.
   - Connection: distance from Sacramento, Kevin's other teams and their rivals (big4.py), linked clubs (association.py,
     links.json), the plastic-fan pulls (global brands, celebrity bandwagons), the Republic link; for players the clubs
     they played for, by how Kevin rates them, and US internationals.
   - Roots: Sacramento Republic +4 (hometown), the United States +20 (home nation), ancestry 0.4 per % up to +10 (nations).
   - In the app, base = A - roots and bonus = roots.
- **Leagues**: a league's Affinity is its median club's, shown with how many clubs reach 65 (app: Affinity > Leagues;
  the mean was dropped 2026-10-09 because a few heavily penalised clubs skewed it).

Parameters: scripts/affinity/params.json. Inputs: inputs.py (measurements only), players/model.py (player research
loader), performance.py, big4.py + proximity.py, association.py, interplay.py, players_link.py, heritage.json.

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
