# Hard-line re-assessment (October 2026)

Kevin asked to re-assess every hard-line penalty on clubs and players. Today is 12 October 2026. A hard line is a
penalty taken off a club's or player's character score before anything else ("shitheads need not apply"); points here
are BEFORE the model's scale (x1.98 for clubs; players use their own severities). Read docs/preferences.md sections B3,
B5, B7 and the player "Penalties" section first: they are Kevin's rules, in his words, and they win over this brief.

## Clubs: the schedule (points before scale; use it to make lines consistent across the whole tracker)
| type (label in scores.py) | when | points |
|---|---|---|
| Racism | tolerated far-right or racist fan identity, or repeated discrimination sanctions over years | 10-30 |
| Racism | more than one discrimination sanction or case in the last ~5 years | 4-8 |
| Racism | a single recent sanction or case, club acted firmly | 2-3 |
| Fan violence | deaths, organised and repeated ultra violence, multiple UEFA/national bans | 8-12 |
| Fan violence | repeated sanctions or organised fights in the last ~5 years | 3-6 |
| Fan violence | a single recent serious incident | 2 |
| State-backed | sovereign fund or government-controlled owner | 25 (satellite of a state group 12) |
| Private equity | a real PE / investment fund owner or major stake (not US sports groups) | 6-12 |
| Leveraged buyout | purchase debt loaded on the club | 10-12 |
| Super League | signed 2021, withdrew within days 3; withdrew late 4; still backing 7.5 | 3 / 4 / 7.5 |
| Multi-club | a SECONDARY club in a multi-club network (the flagship pays 0) | 3-6 |
| Overspend, Franchise, owner's betting or arms fortune, Other | as recorded (several are folded into factors, see "Folded" notes) | as is unless wrong |

Rules that apply to every line:
- Old wrongs fade (Kevin, round 5): an incident older than about 5 years counts HALF unless the behaviour continues.
  Apply it and say so ("2018, not repeated: half"). Repeated or ongoing behaviour keeps full weight.
- Penalties from a previous owner are dropped once the owner has gone. Owner misconduct with consequences and no
  repeat counts half.
- Announced plans count now (a signed takeover by a state or PE owner counts; rumours do not).
- Club response matters: a club that bans offenders and acts sits at the low end of a band; denial or complicity at
  the high end (or a separate Values cut, which you may propose).
- The model also weights types after this: racism x1.25, private equity and multi-club x0.7 (params hard_x). Don't
  pre-adjust for that; give the schedule points.

## Players
Severities are fixed by type (scripts/affinity/inputs.py P_POINTS; acquittal or dropped charges 30%, apology 60%, a
move as a coach half; one money-league move, ambassadorship, rival move or forced transfer counts once; money-league
moves scale with age). Your job for players is the FACTS: is each incident real, correctly typed (b01 racist abuse,
b02 credible abuse/assault allegations, b03 doping, b04 match-fixing/betting, b05 tax fraud conviction, b06
violent conduct, b08 forced transfer, b09 joined bitter rival, b10 money-league move, b12 authoritarian ambassador),
with the right year and outcome (convicted, acquitted, dropped, apologised)? A red card for a bad tackle is not "violent
conduct" unless it was violence (a punch, headbutt, bite, assault) or a pattern; ordinary indiscipline is not a hard
line. Players' incidents live in scripts/affinity/players/research/out/*.json with corrections in
scripts/affinity/players/audit/incidents.json; the inputs you get list each line with the incident text.

## Output
scripts/affinity/research/hardlines/<batch>.json, an array, one object per entity you change or confirm:
{"name": "exact name",
 "verdict": "confirmed" | "adjust" | "add" | "remove",
 "lines": [{"label": "Racism", "from": 2, "to": 3, "year": 2023, "why": "one neutral sentence", "sources": ["url"]}],
 "values_note": "optional: a Values change you'd propose instead of or beside a line",
 "confidence": "high|medium|low"}
For players, "lines" items are incidents: {"type": "b06", "year": 2019, "from": "kept|new", "to": "keep|drop|retype:b0x|outcome:apologised|...", "why", "sources"}.
Include every entity that currently has a line (confirmed or not). Add entries for entities without a line only when
you found one that belongs. Neutral wording, never invent sources, mark anything unverified. Do not edit any other file,
do not commit, do not run git. In your final reply, list every proposed change in one line each.
