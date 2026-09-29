# Re-rate with round-5 sub-weights (September 2026)

Kevin's quiz round 5 (docs/supporter-profile.md, "Quiz round 5") split three Affinity factors into parts. You score
those parts for every club in your batch. History and Ownership are not re-scored. Read BRIEF.md (anchors,
league-agnostic rule, women's clubs judged within the women's game) and the "Round 5 sub-weights" section at its end.

Start from the earlier research for your batch: scripts/affinity/research/out/<batch>.json (the September re-rate:
Culture, Values, adjustments with evidence) and out3/<batch>.json (Team, player conduct). Reuse that evidence; search
only to fill gaps or check facts that may have changed. Budget roughly 2-3 searches per club.

## Parts to score (integers 0-10, each with one short evidence sentence)
Culture
- CG ground: character and history of the stadium, how it feels. A modern ground with good sightlines and real
  atmosphere can score well; an NFL/CFL stadium or a soulless bowl scores low. 10 = Anfield, Westfalenstadion, Bombonera-type.
- CL loudness: singing sections, choreography, noise. 10 = Dortmund's Yellow Wall, Union Berlin, Timbers Army.
- CY loyalty through bad years: crowds that held or grew through relegations, bad owners, re-foundings (attendance
  in bad seasons vs good ones). 10 = Sunderland in League One, AFC Wimbledon, St. Pauli-type.
- CA away following: size and noise of away support relative to the club's size.
Values (positives; start each at 5 = typical)
- VC community work (community trust, local programmes of note)
- VW women's team: real investment in a women's side (for a women's club: investment in its players, facilities, pay)
- VI causes and identity: anti-racism, anti-fascist or left-leaning identity, regional identity, speaking up
  (lower for sectarian, nationalist or right-wing identity, or owner-driven politics)
- VA academy: local academy pathway into the first team, homegrown players
- VP affordability: ticket prices relative to the club's peers (10 = cheapest, frozen or capped prices)
- VF fan voice: board seats, golden share, member votes, real fan advisory power
- Vneg: points to subtract (0 to -4) for what Values already counted against: sportsbook, arms-maker or
  authoritarian-state sponsors, player conduct and the club's response, poor treatment of fans. Evidence required.
Team
- TB player-fan bond: players celebrate with fans, stay after defeats, show up in the community
- TS stable squad: low churn, long-serving captain and core
- TI icon or defining coach: a current icon inseparable from the club, or a long-serving coach who defines it
- TP pressing and intensity: how they play, running for each other (last 3 seasons)

## Incidents (for decay)
For each racism or fan-violence adjustment the club has (see scripts/affinity/scores.py or
scripts/importers/build_usl.py; the note says e.g. "Fan violence -12"), report the year of the most recent serious
incident or sanction, and whether the behaviour is ongoing (repeated in the last 3 seasons).

## Output
Write ONE JSON file: scripts/affinity/research/out5/<batch>.json, an array in batch order:
```json
{"name": "exact name", "CG": {"score": 7, "evidence": "..."}, "CL": {...}, "CY": {...}, "CA": {...},
 "VC": {...}, "VW": {...}, "VI": {...}, "VA": {...}, "VP": {...}, "VF": {...}, "Vneg": {"points": -1, "evidence": "..."},
 "TB": {...}, "TS": {...}, "TI": {...}, "TP": {...},
 "incidents": [{"type": "violence", "last_year": 2024, "ongoing": true, "evidence": "..."}],
 "confidence": "high | medium | low", "sources": ["https://..."]}
```
Neutral wording, facts as of September 2026. Do not edit any other file, do not commit, do not run git.
