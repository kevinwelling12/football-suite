# Bonus candidates (October 2026)

Kevin asked for bonuses that mirror hard lines: a sourced "exceptional act" with a size, added to character the way a
hard line comes off it. Today is 12 October 2026. Read docs/preferences.md first (his rules and words win), especially
B3 (Values), the player values tags, and his tiebreaker note (item 21): "players that are good with fans, humble, and
active in the community ... players I can cheer for and be proud to wear their jersey ... its history and the people
behind it and involved with it make me proud to be a supporter."

## The bar
A bonus is for documented, sustained, exceptional good work that goes BEYOND what the factor scores already credit.
Values (clubs) and Character (players, including the round 11-12 values tags) already reward ordinary community work,
foundations, anti-racism statements, women's teams and the like. Only propose a bonus when the act is clearly above
that: national or international impact, a real cost to the club or player, or years of leadership. Check the current
factor score first: a club already at Values 9-10 or a player at Character 9.5+ needs an act that the score can't hold.
Most clubs and players get none. Aim for a short, defensible list (roughly 10-25 per batch).

## Schedule (points before the model's scale; hard lines run 2-30, bonuses stay smaller)
Clubs:
- Fans saved, re-founded or bought the club and still run it (beyond the Ownership score): 3-5
- A club-led campaign with national impact sustained over years (anti-racism, refugees, LGBTQ+ inclusion, a justice
  campaign such as Hillsborough): 2-4
- Pioneering the women's game or equal treatment (pay, facilities, welfare) well beyond peers: 2-3
- An exceptional humanitarian act at real cost (e.g. giving away a major gate or prize): 1-2
Players:
- Built and led a major cause with measurable impact (a national policy change, hospitals or schools funded and
  built, a movement others joined): 4-6
- Spoke out or stood up for what is right at real personal cost (career, money, safety): 3-5
- Sustained community or humanitarian work over many years, clearly beyond peers: 2-3
Old acts don't fade (good work stays), but a later hard-line act doesn't erase or offset a bonus either; both stand.

## Output
scripts/affinity/research/bonuses/<batch>.json, an array of candidates only:
{"name": "exact name as in the tracker", "kind": "club|player", "label": "short label, e.g. 'Free school meals campaign'",
 "points": 4, "year": "2020-21", "why": "one or two neutral sentences: what, impact, why it's beyond the factor score",
 "current_factor": "e.g. Values 8.2 / Character 9.5", "sources": ["url"], "confidence": "high|medium|low"}
Neutral wording, never invent sources. Do not edit any other file, do not commit, do not run git. Final reply: one line
per candidate (name, label, points).
