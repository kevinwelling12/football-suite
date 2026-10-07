# Player Affinity: factor scoring (October 2026)

Read scripts/affinity/players/research/BRIEF.md for context on Kevin and the research files. You now SCORE players from
the research facts (plus your own knowledge and a quick search where a fact is missing). Six factors, 0-10, one decimal.
Connection to Kevin's clubs, era, and the hard-line incidents (racist abuse, abuse allegations, match-fixing, violent
conduct, authoritarian ambassadorships, tax fraud, doping, Saudi moves, state-owned clubs) are NOT part of these
scores: they are applied separately from the research fields. Don't double count them.

Women are scored against the women's game (Marta's peak is a 10 in Greatness; pioneering and the equal-pay fight count).

## Factors and anchors (use the anchors to keep the scale consistent across batches)
CH Character: how the player treats people, conduct short of the hard lines, causes and public stances.
   Raise: community work, charity, anti-racism, LGBTQ+ allyship, speaking up for players/fans/workers, humility in public.
   Lower: gamesmanship and diving, dissent and tantrums, feuds, arrogance, mocking opponents, support for authoritarian or
   far-right politics, anti-LGBTQ+ remarks, partisan stunts on the pitch. Also record notable public stances (left or right).
   Anchors: Megan Rapinoe 9.5, Marcus Rashford 9.5, Juan Mata 9.5, Mohamed Salah 8.5, a decent pro with no causes or
   issues 6.0, Sergio Ramos 4.0, Neymar 3.5 (antics, diving reputation; tax issues are separate).
WK Team player: work rate, running for teammates, humility, leading by example, no ego.
   Anchors: N'Golo Kanté 10, Thomas Müller 9, Jordan Henderson 9, Virgil van Dijk 8, Lionel Messi 6, Cristiano Ronaldo 4,
   Zlatan Ibrahimović 3, Neymar 2.5.
LO Loyalty & bond: years at the main club, one-club careers, long captaincy, academy graduates, staying through bad times,
   the bond with fans. Lower for forcing transfers, joining a bitter rival, chasing moves.
   Anchors: Francesco Totti 10, Paolo Maldini 10, Steven Gerrard 9.5, Christine Sinclair 9.5, Marco Reus 9,
   Mohamed Salah 7, a journeyman 4, Erling Haaland 3, Kylian Mbappé 3, Neymar 1.5.
AB Greatness: ability at the peak.
   Anchors: Pelé, Maradona, Messi, Cristiano Ronaldo 10; Zidane 9.5; Haaland 9; Salah 9; van Dijk 9; Reus 7.5;
   Pulisic 6.5; a solid top-flight regular 5.5. Women: Marta 10, Aitana Bonmatí 9.5, Christine Sinclair 9, Megan Rapinoe 8.5.
ST Joy to watch: flair, creativity, entertainment. Kevin loves playmakers (No. 10s) and attacking full-backs.
   Anchors: Ronaldinho 10, Messi 10, Andrés Iniesta 9.5, Lamine Yamal 9.5, Luka Modrić 9, Trent Alexander-Arnold 8,
   Erling Haaland 6, N'Golo Kanté 5, a no-frills centre-back 4.
LE Legacy: iconic moments, influence on the game, place in football culture; trophies count some.
   Anchors: Pelé, Maradona, Cruyff, Messi 10; Zidane 9.5; Steven Gerrard 8.5; Megan Rapinoe 9 (women's context);
   Erling Haaland 6; Lamine Yamal 5; a solid international with one famous moment 4.

## Output
scripts/affinity/players/scores/<batch>.json: an array in the research file's order, one object per player:
{"name": "...", "CH": 8.5, "WK": 7.0, "LO": 7.0, "AB": 9.0, "ST": 8.0, "LE": 8.0,
 "stances": ["2020: took the knee, spoke on racism", "..."],
 "why": "CH +2.5 Salah Foundation, humble; LO 7 nine years at Liverpool, left 2026; ..."}
Keep "why" to one short clause per factor. Neutral wording. If the research has a factual error you are sure of, note it
in "why" as "FIX: ...". Do not edit any other file, do not commit, do not run git.
