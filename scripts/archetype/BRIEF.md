# Archetype traits (October 2026)

Kevin's clubs are Liverpool, Borussia Dortmund, Portland Timbers, Portland Thorns and Sacramento Republic. The rating is
built on what makes that group what it is. Score EVERY club in your batch, those five included, on each trait from 0 to
10, using the anchors below. Same standard for every club, famous or not. Use research text in scripts/affinity/research/
(evidence only, ignore any numeric scores) and the web. Be concrete: one line of evidence per trait.

1. terrace: an iconic, self-organised singing end or supporters' group that defines matchdays.
   10 Kop / Yellow Wall / Timbers Army level, famous beyond the league; 5 an organised, loud section known in its league; 0 none.
2. city: the club is its city's identity, in a working city that lives through it.
   10 the club is the city's soul and main team (Liverpool, Dortmund, Portland); 5 a well-loved club sharing the city or
   a big-city afterthought; 0 a franchise or club with little local bond.
3. voice: supporters shape the club (member ownership or 50+1, a trust with real power, fan campaigns that changed club
   decisions, supporter groups the club consults). 10 fans own or run it; 5 real, documented influence; 0 none.
4. conscience: supporters and club actively stand for inclusion (anti-racism, anti-fascism, LGBTQ+ inclusion, community
   causes). 10 a defining part of the identity; 5 solid, visible work; 0 none, or a record of discrimination.
5. ground: an atmospheric home ground: compact, steep, loud, usually sold out, central or historic.
   10 Anfield / Westfalenstadion / Providence Park level; 5 a good, well-filled ground; 0 a half-empty bowl or temporary venue.
6. contender: competes for its league's top prizes. 10 champion or perennial contender with major honours in the last
   ~15 years; 5 regular top-half, the odd cup run; 0 relegation-level or no recent success.
7. rituals: anthem, songs, tifo, traditions recognised beyond the club (You'll Never Walk Alone, the log and chainsaw).
   10 world-famous; 5 well known in its league; 0 none.
8. stewardship: owned for the club, not as an asset: 10 member- or locally-owned owners invested in the long term;
   5 conventional private owner, no major issues; 0 state, oligarch, private-equity or multi-club feeder ownership.
9. women: a women's side that is part of the club's identity. 10 a top-tier team that defines the club too (Thorns);
   5 a top-tier or well-supported team; 0 none.
10. intensity: a high-energy, front-foot playing identity (pressing, attacking, tempo) over recent seasons.
    10 defining (Klopp-era Dortmund and Liverpool); 5 mixed; 0 cautious, defensive.

Output: a JSON object {club name: {"terrace": n, "city": n, "voice": n, "conscience": n, "ground": n, "contender": n,
"rituals": n, "stewardship": n, "women": n, "intensity": n, "why": "one line per trait, ' | ' separated", "sources": [urls]}}.
Integers or one decimal. Never invent: if a trait is unknown after a search, give your best estimate and say so in "why".
Do not read docs/, scores.py, params.json, quiz folders, evidence/ or preferences. Edit no other file, no git.
