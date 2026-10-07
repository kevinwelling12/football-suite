# Player Affinity: independent audit (October 2026)

You are an independent second scorer. Another researcher already scored these players; you must NOT read their work.
Do not open scripts/affinity/players/scores/, ratings.json, lists.json, fit.json, audit/out/ files other than your own,
or any page template. Work only from: research/BRIEF.md (context on Kevin), SCORING_BRIEF.md (the factors and anchors:
use them exactly, they fix the scale), your batch file audit/batches/bNN.json (the research facts per player), web search,
and your own knowledge.

The research facts were gathered quickly and contain errors. Treat them as leads, not truth. Verify with a web search
anything that moves a score by a point or more: years at clubs, captaincy, how a player left a club, public causes,
on-field reputation. Today is October 2026.

## Part 1: scores
Score each player on the six factors in SCORING_BRIEF.md (CH, WK, LO, AB, ST, LE), 0-10, steps of 0.5. Connection to
Kevin's clubs, era, and the hard-line incidents are applied separately: do not fold them into the scores.

## Part 2: baggage check
Penalties are large in this model, so the incident record matters. For each entry in the player's "incidents" and
"money_moves" lists (index i, in order, incidents first then money_moves), give a verdict:
- "ok": it happened as described and the type is right.
- "wrong": it didn't happen, is about someone else, or is too minor for its type (e.g. one red card filed as violent conduct).
- "retype": it happened but belongs to another type (give "type").
- "outcome": it happened but the outcome is wrong or missing: charges dropped, acquitted, case closed, or the player
  publicly apologised (give the corrected "outcome" text, with words like acquitted / dropped / closed / apologised).
Types: b01 racist abuse by the player; b02 abuse allegations (sexual or domestic); b03 doping; b04 match-fixing;
b05 tax fraud (conviction or settlement); b06 violent conduct (assault, street fight, a deliberate injuring act on the
pitch that drew a long ban); b08 forced a transfer (strike, refusing to play); b09 joined a bitter rival directly;
b10 moved to the Saudi league for money (as player or manager); b12 paid ambassador for an authoritarian state.
Then list hard-line incidents the research missed ("missing"), each with a source URL. Only real, documented events.

## Output
Write audit/out/bNN.json (same NN as your batch): an array in batch order, one object per player:
{"name": "...", "CH": 7.5, "WK": 7.0, "LO": 6.0, "AB": 8.0, "ST": 7.5, "LE": 6.5,
 "why": "one short clause per factor, neutral wording",
 "incidents": [{"i": 0, "verdict": "ok"}, {"i": 1, "verdict": "outcome", "outcome": "charges dropped 2019", "note": "..."}],
 "missing": [{"type": "b06", "year": 2014, "what": "...", "outcome": "...", "source": "https://..."}]}
Use the exact "name" from the batch file. Do not edit any other file, do not commit, do not run git.
