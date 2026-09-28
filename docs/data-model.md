# Data model (data/suite_data.json)

Top-level keys = competition keys: epl, ucl, cup, mls, usl, bl, nwsl, esp, ita, fra, ch, unl.

Per league competition:
- teams[]: name, short, abbr, color (chip colour, chosen to read on black), group (conference/group),
  pa/pd (preseason attack/defence priors), base (Affinity before bonus), bonus (heritage tiebreaker),
  region (heritage/hometown label), hai {C,V,H,O,S,adj,note} (Affinity factors; clubs also P track record 0-10,
  k its coefficient, ps the 10 season scores oldest to newest, pl the latest season label), elo (Nations League).
- fixtures[]: [round, 'YYYY-MM-DD', homeIdx, awayIdx, hs|null, as|null, lockedPickH, lockedPickA, lockedFavor]
  (the last three only on matches that were played when the data was built). **Fixture id = index.**
- kick: { "<fixtureId>": ["YYYY-MM-DDTHH:MMZ", confirmed 0|1] }
- params: halfLife, k, h2h, h2hK, rhoPrior, rhoW, beta, drawW, haPrior, scPrior, baseW, zoneW{}
- tv: US broadcaster string. statusDefault (optional): default status per fixture (e.g. postponed).

Carabao Cup (cup): teams[] (92 clubs; att/dfn ratings for the rated ones; tier), fixtures[]:
[round, tie, date, homeIdx, awayIdx, hs, as, pensWinnerIdx].

Competition config (zones, statuses, colours, knockout kind, drawPrior, headline) is in src/config.js.
