# Loyalty & bond re-score (Kevin, 2026-10-06)

Kevin's rule: "Young players move about early on as they establish themselves. Expecting a 13-year-old academy signing to
give 20+ years to one club is noble, but not realistic." So judge Loyalty & bond (LO) from the point a player settles,
around age 23, or his first season as a regular starter if earlier.
- Youth moves, loans and moves before about 23 do NOT count against him.
- What counts: years at clubs once settled, staying through bad times, captaincy, the bond with fans, academy players who
  stayed. Lower for forcing transfers, joining a bitter rival, or chasing moves once established (e.g. moving every 2-3
  years at 25-30 for money or trophies). A late-career move abroad or to MLS after a long spell is not disloyal.
- A one-club career still scores highest. Keep the anchors in SCORING_BRIEF.md where they agree with this rule (Totti 10,
  Maldini 10, Gerrard 9.5, Sinclair 9.5, Reus 9, a journeyman 4, Neymar 1.5); Haaland 3 and Mbappé 3 should be
  reconsidered under the rule.
- Examples: Martin Ødegaard (prodigy at Real Madrid at 16, loans to 21, Arsenal since 22 and captain) should rise from 6.5.
  A player who left his first club at 18 then stayed 10 years somewhere is judged on the 10 years.

Input: audit/lo_batchN.json (born, clubs with years, captaincy, fan bond, loyalty notes, money moves, LO_now = the current
score). Use your knowledge and a quick web search only if the clubs list looks wrong. Steps of 0.25, 0-10.
Output: audit/lo_outN.json, an object {"Player Name": {"LO": 7.5, "why": "one short clause"}} for every player in the batch.
Change only players the rule affects; for the rest, return LO_now with why "unchanged". No other files, no git.
