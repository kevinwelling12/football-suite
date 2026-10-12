# Blind comparison test

A standalone, blind re-rating that does not use the Affinity model. Published as a claude.ai artifact:
https://claude.ai/artifact/HLuS2NNHRvmYuyQb183iCq

- CODEBOOK.md: the plain facts coded for every club, nation and player (no ratings, no weights, no preferences).
- coded/*.json: the facts, coded by research agents from the evidence text only. After coding, every MLS and NWSL club
  was set to relocated = 1 (created as a league franchise) so all batches follow one rule.
- template.html: the 100-question test and its scorer. Every weight starts at 0 and is set by the taker's own answers:
  one-fact questions give starting weights, trade-off pairs refine them (logistic regression pulled to the starting
  weights). Results unlock after all 100 answers.
- build.py: facts -> features 0-1 (fixed transforms, missing facts at the average) -> out/blind_test.html.

`python3 scripts/blind/build.py`, then republish out/blind_test.html to the same artifact.
Answers save per person in the artifact's db (data/users/<id>/answers) and in the browser.
Known gaps: ticket prices are known for very few entities, so that fact moves little; trophy counts for some women
and older players are approximate; sponsor_betting was read slightly differently across batches.

## Accuracy pass (2026-10-12)
Kevin: "do all four ... The goal here is to make it more accurate, not more tailored to my preferences."
- Gap fills (fill/out_*.json, sourced): 2025-26 attendance for all 269 clubs, ticket-price thirds within each league for
  about 220 clubs, league country, corrected soccer capacities, missing caps (batch 1 in; batch 2 follows).
- Consistency pass on coded facts: one rule each for betting and state sponsors, multi-club control (30%+),
  MLS/NWSL titles (no Shields), continental titles, money-league moves (players only, not coaching), trophies,
  violent conduct (in matches only) and racist abuse. Each change is noted in the entity's "notes".
- Domestic trophies weighed by league strength (build.py LEAGUE, approximate UEFA coefficients; England = 1);
  nations' continental titles by confederation.
- Turn-offs: a fact answered "Turn-off" counts double, "Strong turn-off" triple (fixed before any check; same rule in
  the test page).
- validate.py: a held-out check against Kevin's earlier named-club and named-player quiz answers. Report only: nothing
  is tuned to it. On the day: club gut orderings 80% -> 82%, named club pairs 33% -> 44%, nation gut 83% -> 85%,
  named player pairs 50% -> 52%, player gut r 0.27 -> 0.40 (the categories model, partly fitted to these, 90/53/94/68%, 0.33).

## Recount, distance and gut check (2026-10-12)
- Sanctions recounted to one standard for all 355 (SANCTIONS_BRIEF.md, fill/out_sanctions_*.json): discrimination and
  violence 2021-26, financial 2016-26, mapped to bands (0, 1, 2 for 2-3, 3 for 4+ or far-right/deaths).
- Distance on a log scale: 1 at home, 0.64 at 110 km, 0.36 at 800 km, about 0 overseas.
- Gut check (8 named favourites, after the 100): each pick counts as the pick over every other club in its league,
  each league weighing as much as 3 trade-off answers (Kevin: "it shows which clubs one naturally gravitates to").
  Kevin: Liverpool, Real Madrid, Dortmund, Portland Timbers, Portland Thorns, Sacramento Republic; Serie A and Ligue 1
  "don't know". Result: Liverpool, Dortmund, Sacramento #1; Real Madrid #3 (was 9th); Timbers and Thorns #2.
- validate.py on the day: club gut 80%, named club pairs 33%, nation gut 87%, named player pairs 52%, player gut r 0.40.
