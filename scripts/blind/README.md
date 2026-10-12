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
