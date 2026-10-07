# Values tagging, round 12 (Kevin, 2026-10-07)

Tag each player on these off-pitch traits from quiz round 12. Facts only, documented in reliable sources; when unsure or
nothing is known, use 0. Neutral wording. Today is October 2026. Check with a web search anything you tag non-zero.
Do not read scores/, ratings.json, lists.json or other outputs. Value 1 = clearly true, 0.5 = partly or once, 0 = no/unknown.

- wgame: publicly champions the women's game or equal pay (men: backing equal pay, investing in women's clubs; women: leading it).
- climate: climate or environmental activism, or a notably sustainable life (e.g. Bellerín, Forest Green investment).
- private_jet: publicly known for private-jet use for short trips or a lavish high-carbon lifestyle.
- mental_health: talks openly about their own or others' mental health.
- fans_close: known for time with fans (autographs, visits, replying to young fans).
- fans_rows: rows or insults fans online or in person.
- taunts: taunts opposing fans or celebrates provocatively against former clubs.
- feuds: public feuds with their coach or teammates (interviews, social media, walk-outs).
- indiscipline: drink-driving, driving bans, late-night partying in season, club discipline for conduct off the pitch.
- common_goal: pledged 1% (or more) of wages to Common Goal.
- refugees: publicly supports refugees or migrants (campaigns, statements, foundations).
- union: led or publicly backed the players' union in a fight over pay or conditions (incl. national-team pay strikes).
- badge_kiss_exit: kissed the badge or pledged loyalty, then soon asked for or forced a transfer.
- contract_media: pushed for a new contract or a move through the media.
- honest: known for honest, unguarded interviews.
- fan_owned_club: owns or invests in a lower-league, community or fan-owned club.
- outside_interests: studied for a degree or has notable interests or careers outside football (art, business, writing).
- ref_disputes: public disputes with referees after matches (fines or bans for comments count).
- youth_mentor: coaches or mentors at their old youth club or academy.

Input values2/batchN.json. Output values2/outN.json: {"Player Name": {"wgame": 0, ..., "youth_mentor": 0, "notes": "one short
clause per non-zero tag, with year"}} for every player in the batch, exact names. Check the JSON parses. No other files, no git.
