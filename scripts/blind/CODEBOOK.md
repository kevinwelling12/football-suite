# Blind comparison model: fact codebook

This codebook turns research into plain facts. It holds no ratings, weights or opinions. Whoever takes the blind test
decides what each fact is worth. Code what is true as of October 2026.

## Rules for coders
- Record facts, never judgements. "Owned by a sovereign wealth fund" is a fact. "Bad owner" is not.
- Do NOT read or use: docs/, scripts/affinity/scores.py, scripts/importers/build_usl.py, params.json, any quiz*/ folder,
  evidence/, preferences, the factor "score" numbers in research files, "adjustments" points, "flags" that judge, or
  anything that says what someone likes. Read the "evidence" text, facts, sources and research notes only.
- Sources you may read: scripts/affinity/research/** (evidence text and facts only), scripts/affinity/players/research/**,
  scripts/affinity/players/audit/incidents.json and hardlines_review.json (facts about incidents), and the web if a fact
  is missing and quick to confirm. Never invent. Unknown = null.
- Same standard for every entity. Don't favour famous clubs or players.
- Every field below is required in the output (null allowed where marked).

## Clubs (men's and women's) and nations: output object
```
{"name": exact name as given,
 "kind": "club" | "womens_club" | "nation",
 "lat": stadium latitude (2 decimals), "lon": stadium longitude (2 decimals),   // nations: the national stadium
 "founded": year,                                    // nations: year the federation was founded
 "league_titles": int,      // top-flight national league titles (women's clubs: top-flight women's titles). Nations: World Cup titles
 "cups": int,               // major domestic cups (national cup, league cup; not super cups). Nations: continental championship titles
 "continental": int,        // continental club titles (European Cup/UCL, CONCACAF Champions, NWSL n/a = 0, UEL/Cup Winners' Cup count).
                            //   Nations: World Cup appearances
 "seasons_top_flight_last10": int 0-10,              // nations: tournaments (World Cup + continental) qualified for since 2016
 "avg_attendance": int | null,                       // latest season, home league average
 "capacity": int | null,
 "atmosphere": 0-3,         // 0 quiet/sparse, 1 ordinary, 2 known for loud organised support, 3 renowned among the loudest in the world
 "stadium_age": int | null, // years the club has played at its current home ground (nations: years at main national stadium)
 "fan_governance": 0-3,     // 0 no formal fan say, 1 fan board or minority trust stake, 2 members hold a majority vote (50+1, socios),
                            //   3 fan- or member-owned outright. Nations: 0
 "owner_type": "local_private" | "foreign_private" | "us_sports_group" | "private_equity" | "state" | "corporate" |
               "members" | "federation",
 "multi_club": "none" | "flagship" | "secondary",    // part of a multi-club network; flagship = the parent club
 "debt_buyout": 0 | 1,       // purchase debt loaded onto the club (leveraged buyout)
 "super_league": "none" | "left_quickly" | "left_late" | "still_backing",   // 2021 European Super League
 "discrimination": 0-3,      // racism/homophobia by club or fans, last ~5 years: 0 none found, 1 one sanction or case,
                             //   2 several sanctions/cases, 3 tolerated far-right/racist identity or repeated sanctions over years
 "violence": 0-3,            // fan violence last ~5 years: 0 none found, 1 one serious incident, 2 repeated sanctions/organised fights,
                             //   3 deaths, or repeated bans and organised ultra violence
 "financial_breaches": int,  // points deductions, licence or spending-rule breaches in the last 10 years
 "relocated": 0 | 1,         // moved city, or created/rebranded as a franchise or company team
 "sponsor_betting": 0 | 1,   // betting company as shirt sponsor or main partner now
 "sponsor_state": 0 | 1,     // a state-owned company (airline, tourism board, oil) as shirt or stadium sponsor now
 "sponsor_arms": 0 | 1,      // an arms maker as a sponsor or the owner's main fortune
 "ticket_price": 0-2 | null, // 0 among the cheapest in its league, 1 typical, 2 among the most expensive
 "womens_team": 0-3,         // 0 none, 1 below top tier, 2 top tier, 3 top tier and among the strongest/best funded.
                             //   Nations, the women's national team: 1 exists, 2 regular at major tournaments, 3 a world power
 "equal_treatment": 0 | 1,   // documented equal pay or equal facilities for women's side (nations: equal pay agreement)
 "community": 0-2,           // 0 standard community trust work, 1 notable programme or campaign, 2 national-impact campaign sustained for years
 "fan_rescue": 0 | 1,        // fans saved, re-founded or bought the club in its history
 "style": 0-2 | null,        // current play: 0 defensive/direct, 1 balanced, 2 attacking/possession, known for entertaining
 "manager_years": float | null, // current head coach's tenure in years
 "government": 0-3 | null,   // NATIONS ONLY (clubs null): 0 free democracy, 1 flawed (Freedom House Free but issues),
                             //   2 Partly Free, 3 Not Free / authoritarian
 "notes": "one line of the main facts behind discrimination/violence/owner/government codes, neutral wording"}
```

## Players: output object
```
{"name": exact name,
 "born": year, "gender": "M" | "W", "active": true | false, "position": "GK" | "DF" | "MF" | "FW",
 "nation": national team,
 "major_trophies": int,      // league titles + continental club titles + World Cups + continental national titles
 "world_cup_wins": int,
 "individual": 0-3,          // 0 none, 1 team-of-season level, 2 Ballon d'Or/World Player top-10 or league player of the year,
                             //   3 Ballon d'Or / FIFA Best winner
 "caps": int | null,
 "longest_club_years": int,  // most consecutive years at one senior club
 "clubs_count": int,         // senior clubs (exclude youth, B teams, loans under a season)
 "one_club": 0 | 1,
 "captain": 0-2,             // 0 no, 1 club or national captain, 2 long-time captain of both or a defining captain
 "work_rate": 0-2,           // 0 known for low effort, 1 normal, 2 known for exceptional work rate / unselfish play
 "humility": 0-2,            // 0 known for arrogance/ego clashes, 1 neutral, 2 known for humility
 "fan_relations": 0-2,       // 0 known for poor relations with fans, 1 normal, 2 famous for time with fans / fan bond
 "charity": 0-2,             // 0 none known, 1 notable charity/community work, 2 major cause with measurable impact
 "speaks_out": 0 | 1,        // publicly stood up on a social issue (racism, equality, human rights) at some cost
 "flair": 0-2,               // 0 functional, 1 skilful, 2 famous entertainer (dribbles, tricks, spectacular goals)
 "red_card_violence": int,   // incidents of violent conduct off the ball (punch, headbutt, bite, assault on field)
 "abuse_allegation": 0-2,    // 0 none, 1 credible allegation (charged, acquitted or dropped), 2 convicted or settled
 "racist_abuse": 0-2,        // 0 none, 1 alleged/apologised, 2 banned or convicted
 "doping": 0 | 1, "match_fixing": 0 | 1, "tax_fraud": 0 | 1,
 "criminal_other": 0 | 1,    // other conviction (e.g. drink driving causing harm)
 "money_league": 0 | 1,      // moved to a Saudi, Qatari, Emirati or Chinese club for money
 "rival_move": 0 | 1,        // moved directly between bitter rivals
 "authoritarian_ambassador": 0 | 1,  // paid ambassador for an authoritarian state
 "forced_transfer": 0 | 1,   // went on strike or forced a move
 "notes": "one neutral line on any incident codes"}
```
