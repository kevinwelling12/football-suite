# Affinity research brief (re-rate, September 2026)

You are researching football clubs (or national teams) for Kevin's personal Affinity rating: how well a
club aligns with his supporter profile. Read docs/affinity.md and docs/supporter-profile.md first. This
brief turns them into scoring rules. Scores are for the re-rate; weights are applied later, not by you.

## Ground rules
- League-agnostic. Score the club on one absolute scale. A 7 in Culture means the same for a League Two
  club, an MLS club and a Serie A club. Never grade on a curve within a league.
- Research, don't recall. Use web search for current facts (ownership, sponsors, incidents, attendance,
  stadium moves) as of September 2026. Ownership and sponsors change often: verify them.
- Evidence over reputation (Kevin's rule): anchor Culture on attendance, atmosphere reports, away followings;
  anchor Values on documented facts.
- Neutral wording in evidence. State facts, not opinions.
- If you cannot verify something, say so and lower `confidence`. Never invent sources.

## Factors (each 0-10, integers)

### C: Supporter culture
- Main signal: atmosphere (noise, singing sections, choreography, away following).
- A small crowd that is loud and loyal beats a big quiet one. Judge intensity and loyalty, not raw size.
- Loyalty through bad times counts (relegations, bad owners, re-foundings).
- Stadium character counts: a historic ground beats a generic bowl or an NFL/CFL stadium.
- New stadium in the same city: temporary drop, -1 for roughly the first 5 seasons, then none.
  (Existing rule: a recent move for convenience, or sharing an NFL/CFL stadium, is -1.)
- Ultra groups are judged group by group: credit atmosphere; conduct is handled in Values.
- Anchors: 10 = Borussia Dortmund, Union Berlin, Portland Timbers (elite atmosphere and loyalty).
  8 = strong, reliably loud support. 5 = ordinary crowds, occasional atmosphere. 3 = thin or quiet
  crowds, little identity. 1 = barely any support.

### V: Values
Start at 6 (a typical club with no notable positives or negatives) and move with evidence:
- Raise: community trust / charity work of note; real investment in a women's team; a local academy
  pathway into the first team; a formal fan voice (board seats, golden share, fan advisory board with
  power); anti-fascist / left-wing identity; regional identity (Basque, Catalan, Scottish, ...).
- Lower: sports-betting sponsors (shirt, sleeve, stadium, main partner); arms-maker sponsors; sponsors
  owned by authoritarian states (state airlines, tourism boards, state firms); sectarian identity;
  nationalist / right-wing identity; owner-driven political messaging; high ticket prices relative to the
  club's peers (one factor among several); documented poor treatment of fans.
- Crypto/NFT and fossil-fuel sponsors: no effect.
- Women's clubs (NWSL): include the club's player-welfare record (e.g. the 2022 Yates / Sally Q. Yates
  report, NWSL investigations).
- Anchors: 10 = St. Pauli, Oakland Roots-type clubs (values are the identity). 6 = typical. 3 = several
  negatives. 1 = values actively opposed to Kevin's.

### H: History
- Significance first: famous moments, influence on the game, place in football culture. Trophies and age
  support it but do not decide it alone.
- A club liquidated and re-formed by its fans keeps ALL the old club's history (AFC Wimbledon, Newport).
- Clubs in newer leagues get credit for what they grew out of (earlier clubs, leagues, amateur roots),
  e.g. NASL-era names.
- Anchors: 10 = Liverpool, Real Madrid, Athletic Club, Celtic-level significance. 7 = major national
  significance. 5 = solid regional club with some famous moments. 3 = modest history. 1 = brand new.

### O: Ownership
- Ideal: fan / member ownership (supporters' trusts, member clubs, 50+1) = 9-10.
- Conduct counts more than structure: an outside owner who invests sensibly, keeps prices fair and
  listens to fans can score 6-7; a local owner who runs the club badly can score 2-3.
- Anchors: 10 = member-owned (Union Berlin, Athletic Club). 8 = good local fan owner. 5 = ordinary private
  owner, acceptable conduct. 3 = poor conduct, fan protests, instability. 0-1 = state-backed or abusive.
- Structural problems go in adjustments (below), not only in O.

### S: Style of play
- Rewards intensity: pressing, energy, running for each other. Judge the club's recent seasons
  (roughly the last 2-3) and whether it is a lasting club identity.
- Anchors: 9-10 = elite high-press identity. 5 = average. 3 = passive, low-energy.

## Adjustments (points added to the final 0-100 score; list each with evidence)
| type | points | when |
|---|---|---|
| state | -25 | State-backed ownership (sovereign fund or government-controlled owner). |
| lbo | -15 to -20 | Leveraged buyout: purchase debt loaded onto the club. |
| pe | -4 to -8 | Private-equity / sports investment fund as owner or major stakeholder. |
| multiclub | -4 to -8 | Owner runs other clubs (multi-club network). -4 minor stake, -8 the club is a feeder. |
| superleague | -2 / -3 / -5 | Super League signatory: withdrew / withdrew late / still backing. |
| racism | up to -30 | Tolerated racism or far-right fan groups (Lazio -30). Use UEFA/FA sanctions as evidence. |
| violence | up to -30 | Fan violence on the same scale as racism, if recent and repeated or tolerated. |
| overspend | -2 to -6 | Spending well beyond the club's natural income (e.g. PSR/FFP breaches, owner-funded splurges). |
| franchise | -10 to -15 | Relocated or franchised identity (MK Dons -15). |
| government | -10 to -25 | Nations only: the country's government record (human rights, press freedom), scaled like state backing. Use Freedom House / RSF as evidence. |
| other | any | Explain. |

Existing specific rules to keep: gambling = sports-betting sponsors count against Values, casino money
behind an owner does not (Sacramento Republic's tribal-casino ownership is fine). Dortmund: Rheinmetall
counts against Values. Sounders Culture 9 (NFL stadium). Timbers Ownership 5 (judged on today).
Sacramento Republic Ownership 8.

## National teams (Nations League batches)
- C = fan culture of the national team's supporters (atmosphere, away following, loyalty).
- V = federation and fan conduct (discrimination sanctions, violence), plus the Values raises/lowers above
  where they apply (e.g. regional identity).
- H = significance of the national team (World Cups, famous moments, influence).
- O = federation governance (corruption, transparency, independence from government).
- S = playing style of the national team.
- Adjustments: `government` for the country's regime record; `racism` / `violence` for UEFA sanctions.
  (Existing: repeated UEFA discrimination sanctions -8 to -15; authoritarian federation -10.)

## Output
Write ONE JSON file to scripts/affinity/research/out/<batch>.json (the batch name you were given): an array,
one object per club, in the batch order:
```json
{
  "name": "exact name from the batch file",
  "C": {"score": 8, "evidence": "one or two sentences with the key facts"},
  "V": {"score": 6, "evidence": "..."},
  "H": {"score": 7, "evidence": "..."},
  "O": {"score": 5, "evidence": "..."},
  "S": {"score": 6, "evidence": "..."},
  "adjustments": [{"type": "multiclub", "points": -4, "evidence": "..."}],
  "flags": ["anything Kevin should decide or double-check"],
  "confidence": "high | medium | low",
  "sources": ["https://...", "https://..."]
}
```
At least two sources per club, more for anything that triggers an adjustment. Keep evidence short.
Do not edit any other file, do not commit, do not run git.
