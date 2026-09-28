# Affinity (formerly HAI, Heritage Authenticist Index)

Built from a 51-question supporter-profile interview ("the Principled Romantic").
Five factors, 0-10 each, weights from Kevin's own ranking (re-rate 2026-09):
Values 26% · Supporter culture 26% · History & identity 14% · Ownership 12% · Team 12%
(quiz round 3; before: 28 / 26 / 16 / 12 / Style 8; originally 22 / 28 / 18 / 14 / 8).
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
