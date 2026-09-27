# Affinity (formerly HAI, Heritage Authenticist Index)

Built from a 51-question supporter-profile interview ("the Principled Romantic").
Five factors, 0-10 each, weights from Kevin's own ranking:
Supporter culture 28% · Values 22% · History & identity 18% · Ownership 14% · Style of play 8%
base = weighted sum / 0.90 * 10 + adjustments. Heritage is a tiebreaker: bonus up to +4 clubs, +10 nations.

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
Rescore: edit scripts/affinity/scores.py (USL: scripts/importers/build_usl.py) -> rescore.py -> build.
