# Affinity (formerly HAI, Heritage Authenticist Index)

Built from a 51-question supporter-profile interview ("the Principled Romantic").
Five factors, 0-10 each, weights from Kevin's own ranking (re-rate 2026-09):
Values 26% · Supporter culture 23% · History & identity 16% · Team 15% · Ownership 10%
(quiz round 5, 2026-09-29; round 4: 27 / 20 / 17 / 16 / 10; round 3: 26 / 26 / 14 / 12 / 12; before: 28 / 26 / 16 / 12 / Style 8; originally 22 / 28 / 18 / 14 / 8).
base = weighted sum / 0.90 * 10 * track record coefficient + adjustments.
Bonus: nations keep a heritage tiebreaker up to +10. Clubs have no regional bonus; only the hometown club
(Sacramento Republic FC) gets +4.

Rules decided with Kevin (apply consistently):
- State-backed ownership: -25. Tolerated racism/far-right fan groups: up to -30 (Lazio -30).
  Nations with repeated UEFA discrimination sanctions: -8 to -15. Authoritarian federations: -10.
- Multi-club networks: -4 to -8. Super League signatories: -2 (withdrew) / -3 (withdrew late) / -5 (still backing).
- Gambling: sports-betting sponsors count against a club; casino/gaming money behind an owner does not
  (Sacramento Republic's tribal-casino ownership is fine).
- Arms-manufacturer sponsorship counts against values (Dortmund -1 values, Rheinmetall).
- Stadium rule: stadium character counts in Culture (historic ground > NFL stadium). A stadium counts
  against a club only if the move was recent and for convenience (West Ham, Sassuolo, NFL/CFL-stadium
  MLS/NWSL clubs: -1 Culture), not if it has been home for decades (Roma/Lazio, Monaco, Napoli).
- Culture should be anchored on evidence (attendance, atmosphere), not reputation (USL recalibration).
- Hometown rule: the club of the city Kevin has lived in all his life (Sacramento Republic FC) gets the
  full club heritage bonus +4. Only club this applies to.
- Specific calls: Timbers ownership 5 (judge on today); Sounders culture 9 (NFL stadium); Sacramento
  ownership 8.
Quiz round 2 (neutral questions, 2026-09): see docs/supporter-profile.md. It refines how each factor is judged.
Re-rate 2026-09 (research in scripts/affinity/research, answers in REVIEW.md), rules added:
- Satellites of a state-controlled group: half the state penalty (-12), plus multi-club.
- Multi-club: only the owner's secondary clubs pay; the flagship gets 0. Private equity and multi-club add up. No cap on stacks.
- Leveraged buyout -8 to -10. Private equity -4 to -8, only real PE funds (not US sports investment groups).
- Fan violence up to -30, same scale as racism. Nations: government record -5 to -25 (Freedom House / RSF).
- Sponsors: casino brands count half as much as sportsbooks; an owner who owns the betting sponsor counts worse;
  state tourism boards and state firms of any non-Free country count in full; signed future deals count now.
- Penalties from a previous owner are dropped. Franchise -10 also for RB Leipzig and NC Courage.
Quiz round 3 (players and team culture, 2026-09-28; research in scripts/affinity/research/out3, applied by team.py):
- Team replaces Style of play (slot S in scores.py): how they play, the player-fan bond, a stable humble squad,
  current icons (only while at the club), a defining long-serving coach; women's clubs also player activism.
- Values: player conduct and the club's response; -2 for standing by a player facing credible abuse or violence
  allegations (not after an acquittal); +1 for homegrown players unless the academy is already credited.
  Staff and owner conduct toward players (welfare, pay, exile groups) counts in Ownership.
- Rivals of clubs Kevin follows: Schalke, Bayern, Seattle Sounders, Seattle Reign, Vancouver -5; Everton -2.
- Republic link +2: a former Republic player who is a regular at a higher-tier club (now LAFC, Aaron Long).
Rescore: edit scripts/affinity/scores.py (USL: scripts/importers/build_usl.py) -> rescore.py -> build.

Track record (2026-09-28, scripts/affinity/performance.py; data in scripts/affinity/research/perf, brief PERF_BRIEF.md):
- Clubs only. A coefficient, not a sixth factor: k = 0.80 + 0.04 * P multiplies the factor score before
  adjustments (P 0 -> x0.80, 5 -> x1.00, 10 -> x1.20; widened from +/-10% on 2026-09-28 so a strong record
  can overturn a small factor lead, e.g. Dortmund now above Union Berlin). Penalties are not scaled. Affinity is capped at 100.
- P (0-10) = the last 10 completed league seasons, averaged with a 3-season half-life (last season counts 1,
  three seasons ago 0.5, nine ago 0.125). Older success counts for nothing here; History covers heritage.
- Each season is judged against the tier the club is analysed in: top flights 1, Championship and USL Championship 2,
  League One/Two as one band (3-4). In the band: 8.5 * (1 - p^1.5), p = 0 first, 1 last (steady top-half
  finishes score close to a title, a relegation fight scores low). One tier above: 8.5-10; two or more: 10.
  One tier below: up to 4.5; two or more: 0. Trophies add: league title 1.5, main cup 1, league cup 0.5,
  Champions League / CONCACAF Champions Cup 2, Europa / Conference League 1 (capped at 10).
- Seasons before a club existed score 3 (no consistency shown yet). NWSL 2020 (no regular season) is left out.
- Refresh once a year after the seasons end: add the new season to perf/*.json (drop the oldest), then rescore.

Association (2026-09-28, scripts/affinity/association.py; links in scripts/affinity/links.json after Kevin's review;
research in scripts/affinity/research/assoc, brief ASSOC_BRIEF.md):
- Two-way pull: each linked club moves a share of the gap toward its partner's Affinity. strong 15% (one supporter
  base: Timbers / Thorns), medium 8% (formal fan friendship, shared ritual like You'll Never Walk Alone), light 4%.
  A club's link weights add up to at most 15% (many links average instead of stacking); total capped at +/-5;
  computed once on the Affinity before any pull.
- Direction: a club always gains from a partner rated above it, and only loses to a partner below 50 (a club Kevin
  dislikes): Liverpool isn't dragged down by Mainz, but an ultras twinning with Lazio costs Inter and Real Madrid.
- 56 ties in links.json: the research minus low-confidence ties (incl. stadium-only US pairs) and kit-heritage ties.
- Pairs where both clubs carry a rival penalty are skipped (Sounders / Reign). Ownership ties never count.

Location & big-4 (2026-09-28, scripts/affinity/big4.py + proximity.py; research in research/big4, BIG4_BRIEF.md):
- Kevin's teams: Kings, Giants, 49ers, Sharks. Rivals: Lakers, Dodgers, Seahawks, Rams, Cowboys, LA Kings, Ducks,
  Golden Knights; half weight: A's, Raiders, Packers, Warriors.
- Distance: North American clubs +3 * (1 - miles/800) from Sacramento (Republic excluded: hometown +4).
- Market: Bay Area clubs +0.5 (+1 for Kevin's teams, -0.5 Warriors); LA-market clubs -2; Dallas -1; Las Vegas -1.5 (skipped for clubs with a rival penalty).
- Ownership ties: Kevin's team +2 ownership / +1 minority (Leeds, Huddersfield, Republic, Thorns, Whitecaps, Bay FC);
  rival -3 ownership / -1.5 minority / -1 former owner, half for half rivals (Arsenal, Rapids, Galaxy, Bournemouth,
  Lorient, LAFC, Earthquakes, Birmingham, Marseille). Passive fund stakes and ended ties don't count.
  Chelsea: BlueCo's Dodgers/Lakers owners bought out by Clearlake (Sept 2026), so no penalty.
- Added like an adjustment, capped at +/-4, before the association pull.

World Cup 2026 nations (2026-09-28; research in scripts/affinity/research/wc, WC_BRIEF.md):
- The 32 non-UEFA nations of the 48-team field are scored like the UEFA nations (factors in scores.py, metadata and
  World Cup results in data/nations_extra.json, filled by rescore.py). They show on the Nations League Affinity tab
  (filter: All / World Cup 2026 / Nations League) and in the overall ranking, with a breakdown-only card.
- Government penalty only for Partly Free / Not Free countries, as for UEFA (Argentina, Colombia, US, Senegal: 0).
- United States: home nation +10 (the nations' maximum, like England's heritage +10).

Quiz round 4 "The Blind Draw" (2026-09-29; scripts/affinity/quiz4, results in docs/supporter-profile.md):
- Weights now Values 27, Culture 20, History 17, Team 16, Ownership 10 (half quiz evidence, half the round-3 weights).
- Fan violence penalties doubled (cap -30): Galatasaray -16, Fenerbahçe -16, Roma/Inter -12, Frankfurt/Feyenoord/Porto -10.
- Rival ownership (big-4) -5 / minority -2.5 (was -3 / -1.5); big-4 item cap +/-6.
- Track record: kept at +/-20%; half-life 4 seasons (was 3).
- Brighton: owner's fortune from sports betting -3.

Quiz round 5 "The Blind Draw II" (2026-09-29; scripts/affinity/quiz5, findings in docs/supporter-profile.md):
- Weights Values 26, Culture 23, History 16, Team 15, Ownership 10 (half round 4, half his 100-coin budget split).
- Track record +/-15% (k = 0.85 + 0.03 P). Distance bonus up to +4 (was +3).
- Penalties re-balanced to his worst/least-bad ranking (racism > state > PE = LBO = violence > Super League >
  overspend = betting = arms > multi-club > relocation): fan violence 1.5x the pre-round-4 values (round 4 had 2x),
  private equity x1.5, leveraged buyout x1.2, Super League x1.5, multi-club x0.75, franchise/relocation x0.4
  (MK Dons -6, RB Leipzig -4, NC Courage -4).
- For the next re-rate (needs research, not applied): sub-weights inside the factors and decay of old incidents
  (see BRIEF.md, "Round 5 sub-weights").

Track record reference and "what you can follow" (2026-09-29):
- Track record: clubs outside North America are judged against the top flight (Kevin: "tier 1, mid-table or higher
  regularly, with occasional runs at championships, cups and Champions League-type competitions"). Lower-tier football
  counts only regionally, so USL Championship clubs keep their own tier. League One/Two clubs dropped 12-16 points.
- Bandwidth is not Affinity: following a club needs context of its competitions. The ranking and Affinity tabs tag
  "Your leagues" (Premier League, Bundesliga, MLS, NWSL, USL Championship) and "Meets your clubs" (only in the Champions
  League or Carabao Cup), with an "In your competitions" filter. The tags never change the score (tested: adding
  points for them lowered the gut-rating fit).

Cascadia decider (2026-09-30; scripts/affinity/research/cascadia: sourced dossier, questionnaire, answers):
Portland vs Seattle, weighted head-to-head on 14 dimensions: Portland +8 (of +/-100). Portland on ground, sponsors,
direction, owner conduct, history; Seattle on fan voice, academy, community, stability, women's link, coach, record;
supporters even. Gut: Portland; switching would not feel like betrayal. Applied: Timbers Ownership 5->6; Sounders
Culture 9->8, History 8->7, Ownership 6->5. Neutral (no rival penalty): Timbers 82.4, Sounders 81.6.
Rules from it, for the whole engine (next re-rate):
- Sharing an NFL stadium counts a little (the existing -1 Culture rule stands).
- Owner misconduct with consequences and no repeat counts about half.
- A casino sponsor with a sportsbook inside counts partly (as the casino rule: half a sportsbook).
- Announced plans (stadium move, ownership change) count now, fully.
- Formal fan power (e.g. a vote on the GM) matters some.
- A women's team majority-owned by private equity but run by the club is better than none.
- A long-serving coach matters more than the style of play.
Rules re-rate (2026-09-30; brief research/RULES6_BRIEF.md, findings research/out6, applied by apply_rules6.py):
every club checked against four rules, each hit exactly +/-1 on one factor. R1 owner's past misconduct with
consequences, no repeat -> +1; R2 announced stadium move (+1 welcomed upgrade, -1 opposed/worse) or sale
(-1 private equity/multi-club/opposed owner, +1 fans or respected local); R3 coach 5+ seasons -> Team +1,
3+ permanent coaches in 3 seasons -> Team -1; R4 uncounted casino-with-sportsbook sponsor -> Values -1.
43 hits on 40 clubs (26 coach churn, 12 stadium, 2 sale, 1 owner-past, 2 casino); 3 rejected on review
(Austin R1, Shrewsbury R2, Detroit City R2). Gut fit on the 26 vignettes 0.723 -> 0.728.

Squad interplay (2026-09-30, Kevin's idea; scripts/affinity/interplay.py, applied in rescore.py): an additive bump of up
to +/-2 on the Team factor, recency-weighted with the track record's 4-year half-life.
- Nations, club links: every national-team squad at 20 tournaments since 2016 (World Cups, Euros, Copa América, Gold Cup,
  AFCON, Asian Cup; research/squads.json, parsed from Wikipedia by interplay/parse_squads.py). A player counts by how
  Kevin rates his club: above 63 Affinity up to +1 (at 90), below 35 down to -1 (at 15), neutral between; captains 1.5x;
  per squad scaled to 23. bump = link / 3. Netherlands +1.6 (Liverpool, van Dijk captain; PSV), Germany +2 (Bundesliga
  clubs), United States +0.7, England -0.2 (Man City call-ups outweigh Liverpool's). Small UEFA nations with no
  tournament squads: none.
- Clubs, homegrown share: share of the squad from the club's own country (Welsh clubs count England too, Canadian
  clubs the US), current squad plus every other season back to 2016 (research/domestic.json from Wikipedia squad
  lists: interplay/fetch_squads.py, parse_domestic.py). z-score against the club's own league x 0.8, scaled down when
  only the current squad is known. Athletic Club 90% (league 60%) +1.6, Bodø/Glimt +1.1, Liverpool 27% (league 34%)
  -0.6, LAFC and FC Cincinnati about -1.8.
Gut fit on the 26 vignettes 0.728 -> 0.732.

Tenths re-rate (2026-09-30; brief research/DECIMAL_BRIEF.md, findings research/out7, applied by apply_tenths.py):
Culture, Values, History and Ownership now carry one decimal for every club and nation. A refinement, not a re-rate:
each value stays within 0.4 of its old whole number (k.0 = a typical k), placed against every entry with the same
score across the tracker (research/decimal_bands.json). 641 of 1,360 values moved off .0 (mostly ±0.2-0.3). Average
Affinity change 0.55; biggest: Arsenal and Shakhtar +2.1, Angers -2.0. History drifted up slightly in every batch
(+0.02 to +0.17 on average), too small and too even to recentre. Gut fit on the 26 vignettes 0.732 -> 0.723.
Team keeps its whole-number base plus the squad-interplay bump.

Rival penalties removed (2026-10-02, Kevin): the flat club penalties for his teams' rivals are gone (Bayern Munich,
Schalke 04, Seattle Sounders, Seattle Reign, Vancouver Whitecaps -5; Everton -2). Local-market and ownership items
(big-4) stay. With no rival flags left, association now links Sounders and Reign, and the big-4 market items apply to
those clubs like any other: Seattle clubs now take the Seahawks market item (-1, as Dallas for the Cowboys).
Effect: Sounders 78.6 -> 82.6 (above the Timbers, 81.3, on track record and homegrown share), Bayern 83.2 -> 88.2.
Gut fit unchanged (0.723).

Add-on review (2026-10-02, Kevin; each add-on tested by removing it and rerunning the gut test):
- Track record: +/-5% (k = 0.95 + 0.01 P), top-flight clubs only, the USL Championship counted as top flight (no
  promotion/relegation in the US). Championship and lower English clubs get no coefficient: judged against the top
  flight they scored near zero and took the full x0.85 (AFC Wimbledon, Wrexham). Gut fit: +/-15% everyone 0.723,
  +/-5% top flight 0.776, none 0.788.
- Minor penalties folded into factors (fold_minor.py): multi-club and overspend -> Ownership, franchise -> History,
  betting owner and 'Other' conduct -> Values, converted at the factor's weight; what a factor at 0 cannot absorb spills
  into Values. Hard lines stay as adjustments (racism, state ownership, fan violence, private equity, leveraged
  buyouts, Super League, government record): without them the gut fit drops to 0.560.
- Connection = distance, rival/local markets, ownership ties to Kevin's teams, association links, Republic link (now a
  big4.py item), hometown and heritage. Shown as one group; kept as adjustments, not a weighted factor: a Connection
  factor (5-10%) fitted worse (0.77-0.78), as three quarters of clubs have no connection data.
- Result: Timbers 79.7 (13th) above Sounders 78.6 (17th) on merit; Republic 4th; AFC Wimbledon 11th.

Player Affinity (2026-10-06; scripts/affinity/players: model.py, fit.py, fit.json, research/, scores/, ratings.json, lists.json;
quiz rounds 7 and 8 in scripts/affinity/quiz7, quiz8; page: claude.ai artifact "Player Affinity"):
- Pool: ~300 players researched (facts: clubs and years, captaincy, moments, style, causes, incidents, money moves; research/BRIEF.md)
  and scored on six factors 0-10 against fixed anchors (SCORING_BRIEF.md): Character, Team player, Loyalty & bond, Greatness,
  Joy to watch, Legacy.
- Weights come from anonymous choices only (round 7's 100-point budget was dropped: Kevin found it hard to use). Round 8's
  real-player head-to-heads turned out to follow name recognition (familiar names won; no factor explained more than 55% of
  those picks), so fit.py fits a logit model to the 50 mystery-player pairs of rounds 8 and 9 (round 9: 30 pairs chosen for
  information, plus a baggage trait and a "can't split them" answer). Result in fit.json: Team player 29, Character 25,
  Loyalty 16, Joy 14, Legacy 12, Greatness 4.5; connection x1.09, penalties x2.54. Leave-one-out 77% of 48 decided pairs
  (round-8 fit with names: 65%). As checks: it calls 17 of 29 named head-to-heads and tracks the gut ratings at r 0.36.
- Connection (adjustment, then x1.02): +1.2 per season at Liverpool, Timbers, Thorns, Republic, +0.6 at Dortmund (half weight
  from 2026-10-06: Kevin's pull to Dortmund hasn't materialised like Liverpool's) (max +8); -0.3 per season at clubs he
  rates under 35 (max -3); US international +2.
- Penalties (then x2.54) from his best-worst ranking: abuse allegations 18, racist abuse 14, match-fixing 14, violent conduct 7, authoritarian
  ambassador 7, tax fraud 5, doping 4, Saudi move 3, forced transfer 3, rival move 2. Dropped/acquitted 30%, apology 60%,
  a move made as a coach half. Diving and general conduct sit in Character. Penalties stack with no cap (Kevin, 2026-10-06:
  "shitheads need not apply"), so several incidents can take a player to 0.
- No era discount: Kevin has followed closely for under a year, so past players are judged on the record alone.
- Position: a boost for a main position of playmaker or full-back (quiz 7 s03), half for a second position (POS_BOOST).
  Fitted to round 10 at +7.2 (it went his way in 4 of 5 pairs where position differed); was +3 before. Refit after the
  loyalty and money-league changes (2026-10-06): +5.9, weights unchanged, leave-one-out 75% (named pairs 9 of 15).
- Independent audit (audit/): a second set of scorers re-scored all 306 blind from the facts plus web checks (AUDIT_BRIEF.md);
  scores are averaged, gaps over 1.5 settled by a third pass (adjudicated.json). They also checked every incident: 31
  corrections (victims filed as offenders, wrong types, dropped or acquitted cases) and 18 added, applied by model.load().
  Borderline additions kept (Claude's call, Kevin had no view): Keegan 1974 fight with Bremner (b06, both sent off and
  banned), Matthäus 1984 Gladbach to Bayern (b09, the 1970s title rivalry; he had signed before the 1984 cup final vs Bayern).
- Round 10 (quiz10/, 2026-10-06): 30 named pairs from one setting each (two Liverpool players, two stars with no link to his
  clubs...), one or two factors apart, with pass buttons. He passed on 15 (all the Liverpool greats, most stars and women),
  so he knows his clubs' current players and a few stars. On the 15 he answered, the factors called 8 (Joy to watch 5 of 7,
  position 4 of 5, Team player only 3 of 7): his picks between players he watches weekly follow his own impressions more than
  the researched scores. fit.py adds these 15 to the 48 mystery pairs; weights barely moved (CH 25, WK 28, LO 17, AB 5,
  ST 15, LE 11; connection x1.02, penalties x2.75); leave-one-out 73% overall.
- Money leagues (Kevin, 2026-10-06, after Firmino: "I want guys that want to compete at the highest level, not collect a fat
  paycheck against minor leaguers"): a move to a Saudi, Qatari, Emirati or Chinese Super League club costs by age at the move,
  7 at 29 or younger, 4 at 30-33, 2 at 34+ (before x2.75), found from the club list too (Coutinho, Xavi, Raúl, Drogba,
  Batistuta, Weah). Coaches keep 3 x 0.5. Men only.
- Top-10 walkthrough feedback (Kevin's verdicts and notes, player by player): players/feedback.json.
- Connection follows club Affinity alone (Kevin, 2026-10-07: "apply the Dortmund change to all clubs; base it solely on
  Affinity rating, not my stated favourites"): every club 0.6 * (a - 50) / 35 a season up to +0.6, -0.3 * (50 - a) / 15 down to
  -0.6; gains capped at +4 (CONN_CAP; +8 tried: leave-one-out 70%, +4: 71%; the version with followed clubs at +1.2 scored 73-75%),
  losses at -3. Women's clubs read only NWSL ratings; a woman's spell at a European club rated only for its men's side is neutral.
  Refit: CH 25, WK 28, LO 16.5, AB 5, ST 15, LE 10.5; connection x0.98, penalties x2.83, position +7.2.
- Values (quiz round 11, quiz11/, 2026-10-07): 24 mystery pairs differing only off the pitch + 12 direct questions; logit
  weights (quiz11/fit.json; agree with 23 of 24 picks): betting -3.1, refused Pride -2.8, rainbow armband +2.5, speaks on
  racism +2.3, left campaign +2.2, right campaign -1.8, fair play +1.2, funds schools +1.1, private life +0.3, criticises
  FIFA/owners -0.2. Every player tagged on these by research agents (players/values/, BRIEF.md, cited). Character =
  research score + VALUES_X * sum(weight * tag), clipped 0-10 (VALUES_X 0.3, doubled to 0.6 at Kevin's request; LOO 73%) (an average with a neutral 6 was tried and dropped: it pulled
  untagged good characters down). Refit: leave-one-out 75%.
- Values round 12 (quiz12/, 2026-10-07): pairs (agree 24 of 24): indiscipline -2.8, feuds -2.3, rows with fans -2.0,
  taunts -1.7, women's game +1.3, time with fans +1.2, private jet -0.9, mental health +0.9, climate +0.2, Common Goal 0
  (fitted -0.5, floored). Direct (as stated): refugees, union, honest, fan-owned club, outside interests, youth mentor +2;
  badge-kiss exit, referee disputes -2; contract or move pushed through the media -4 (Kevin: "one is business, the other
  is manipulation"; talks behind closed doors are not penalised). Tags in players/values2/ (cited). The shift adds to round 11's.
  Note: forcing a move is also a b08 penalty, so contract_media double-counts a little for strikers like Isak, Dembélé.
- Position boost removed (Kevin, 2026-10-07: position "matters very little"): POS_BOOST 0, fit.py fixes it at 0. Refit:
  CH 25, WK 27, LO 17, AB 5, ST 16, LE 10; connection x0.93, penalties x2.93; leave-one-out 71% (73% with the boost).
- Lists: separate men's and women's (his choice), active and all-time (all-time includes active players).

Clubs and players together (2026-10-07, Kevin: "full integration of the player and club sides with bilateral influence"):
- One run: `python3 scripts/affinity/unified.py [--fit]` rescores every club (rescore.py), rates every player
  (players/model.py, --fit refits the weights first), rebuilds the lists and writes data/players.json for the app.
- Club -> player: a player's connection is the Affinity of each club he played for (players/model.py, per_season).
- Player -> club (scripts/affinity/players_link.py): the best 5 current players move Team by 1.5 * sum(x) / (n + 4),
  the best 5 icons (4+ seasons there) move History by 1.0 * sum(x) / (n + 3), x = (A - 60) / 15 clipped to +/-1.
  A leaves out connection, so neither side echoes the other and one pass is exact. Best 5 only, because the pool
  covers Kevin's clubs down to the third keeper but other clubs only through their stars. hai.py in suite_data
  records the applied amounts (a factor at 10 can't go higher), shown as "Players" and "Icons" in the club sheet.
- First run: 87 of 308 clubs moved, by at most about 2: Thorns 88 -> 90, Kansas City Current 75.7 -> 77.1,
  Liverpool 84.6 -> 85.8, Dortmund 83.1 -> 84.4, Bayern 80.9 -> 82.0, Arsenal 59.9 -> 61.3; PSG 26.1 -> 24.9,
  Inter Miami 28.1 -> 27.3.
- App: Affinity view has a Clubs & nations / Players switch; Players shows the four lists with each player's breakdown.
