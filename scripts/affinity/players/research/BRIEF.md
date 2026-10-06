# Player Affinity: fact research (October 2026)

Kevin (Sacramento) rates clubs with an Affinity model (docs/affinity.md, docs/supporter-profile.md). We are building a
player version: two ranked lists, active players and all-time, 50-100 each. Kevin is answering a player questionnaire
now; the scoring formula will be fitted to his answers. Your job is only the FACTS each factor will be scored from.
Do not score players. Be neutral and specific.

## What Kevin cares about (from 6 quiz rounds; context for what to look for, not for judging)
- Character first: conduct, causes (anti-racism, community, LGBTQ+ allyship, charity), how a player treats people.
  Hard lines: racism, credible abuse/violence allegations. Also wary of authoritarian-state money (Saudi league moves,
  state-owned clubs, paid ambassadorships). "Some mistakes should follow a person for good."
- Loyalty and the player-fan bond: one-club players, long-serving captains ("same captain for 12 seasons" was his
  strongest pull), academy graduates, players who stayed through bad times, celebrate with fans.
- Team first and humble over big egos; but he picked "Genius" over "Grinder": he loves flair and creativity too.
- History/legacy: iconic moments, influence on the game. Trophies matter less than story.
- His clubs: Liverpool, Borussia Dortmund, Portland Timbers, Portland Thorns, Sacramento Republic FC. Club Affinity
  (0-100) for reference, top: Athletic Club 99, Thorns 88, Union Berlin 86, Republic 85, Bodø/Glimt 85, Liverpool 85,
  Dortmund 83, Bayern 81, Real Sociedad 81, AFC Wimbledon 81, Freiburg 80, Timbers 80, Osasuna 79, Sounders 79,
  Köln 78, Stuttgart 78, PSV 77, Celta 77, Werder 77, Detroit City 77, KC Current 76, HSV 75, Betis 75, Schalke 75,
  Sporting CP 75, Gladbach 74, Napoli 74, Barcelona 73, Leeds 72. Lowest: Man City 14, PSG 26, NYCFC 26, Inter Miami 28,
  Chelsea 29, RB Leipzig 32, Lazio 22. Nations: Scotland 84, Netherlands 80, Wales 79, Denmark 78, USA 77, Norway 76,
  Japan 76, Germany 75, England 74.

## Output
One JSON file at scripts/affinity/players/research/out/<batch>.json: an array, one object per player:
{
 "name": "Common name", "full_name": "...", "gender": "M|W", "active": true,           // active = playing as of Oct 2026
 "born": 1992, "nation": "Egypt", "positions": ["RW"],
 "clubs": [{"club": "Liverpool", "from": 2017, "to": null, "apps": 400, "captain": false, "academy": false}],
 "longest_club": "Liverpool", "longest_years": 9, "one_club": false,
 "captaincy": "Liverpool vice-captain 2023-; Egypt captain 2022-",
 "national": {"team": "Egypt", "caps": 105, "goals": 60, "captain": true},
 "honours": "2 PL, 1 UCL, ... (short)", "awards": "Ballon d'Or podiums etc. (short)",
 "moments": ["1-3 iconic moments, with year"],
 "style": ["inverted winger", "elite finisher", "presser"], "work_rate": "high|medium|low (reputation, one line)",
 "ego": "humble|neutral|big (one line why)",
 "fan_bond": "one line: celebrated/known bond with fans, stayed after defeats, fan favourite or not",
 "loyalty_notes": "stayed through relegation / forced a transfer / joined a rival / returned home, with years",
 "causes": ["specific: Rashford free school meals 2020; ..."],
 "incidents": [{"year": 2011, "type": "b01", "what": "racially abused Evra, 8-match ban", "outcome": "apologised later?", "source": "url"}],
 "money_moves": [{"year": 2023, "what": "joined Al-Nassr (Saudi PIF-owned)", "type": "b10|b11|b12"}],
 "links": "ties to Kevin's clubs or nations above (e.g. 'Liverpool 2017-'), else ''",
 "sources": ["2-4 URLs for anything not common knowledge"],
 "confidence": "high|medium|low"
}
Incident/money types: b01 racist abuse, b02 credible domestic-abuse/assault allegations (note acquittals), b03 doping ban,
b04 match-fixing/betting breaches, b05 tax fraud conviction, b06 biting/violent conduct, b07 diving reputation,
b08 forced a transfer by refusing to play, b09 joined his club's bitter rival, b10 Saudi league move, b11 played for a
state-owned club (Man City, PSG, Newcastle since 2021, Saudi PIF clubs), b12 paid ambassador for an authoritarian
government (e.g. Qatar 2022, Saudi tourism). Also note other notable incidents with type "other".

## Method
- Use your own knowledge for well-known facts; verify recent ones (2025-26 transfers, retirements, new incidents) with a
  quick web search. About one search per player at most, more only when a fact is contested. Wikipedia is fine.
- Accuracy over completeness: leave a field "" or [] rather than guess. Mark confidence.
- Women's players are judged in the women's game context (pay, pioneering, the equal-pay fight count as causes).
- Do not edit any other file, do not commit, do not run git.
