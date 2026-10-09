# Data model (data/suite_data.json)

Top-level keys = competition keys: epl, ucl, cup, mls, usl, bl, nwsl, esp, ita, fra, ch, unl.

Per league competition:
- teams[]: name, short, abbr, color (chip colour, chosen to read on black), group (conference/group),
  pa/pd (preseason attack/defence priors), base (Affinity without roots), bonus (roots: hometown, home nation,
  heritage), region (roots label for nations), elo (Nations League), hai (written by scripts/affinity/affinity.py):
  C V H O S factors (S = Team; S0/H0 before squad and icon bumps, tb/dom/clubs/py the bumps), Q character, hard
  [[label, points]], A0 after record, conn [[label, points]] and K their capped total, P record 0-10 (clubs: ps season
  scores oldest to newest, pl latest season; nations: rank, wc2026, cont), notes.
- fixtures[]: [round, 'YYYY-MM-DD', homeIdx, awayIdx, hs|null, as|null, lockedPickH, lockedPickA, lockedFavor]
  (the last three only on matches that were played when the data was built). **Fixture id = index.**
- kick: { "<fixtureId>": ["YYYY-MM-DDTHH:MMZ", confirmed 0|1] }
- params: halfLife, k, h2h, h2hK, rhoPrior, rhoW, beta, drawW, haPrior, scPrior, baseW, zoneW{}
- tv: US broadcaster string. statusDefault (optional): default status per fixture (e.g. postponed).

Carabao Cup (cup): teams[] (92 clubs; att/dfn ratings for the rated ones; tier), fixtures[]:
[round, tie, date, homeIdx, awayIdx, hs, as, pensWinnerIdx].

Competition config (zones, statuses, colours, knockout kind, drawPrior, headline) is in src/config.js.

data/nations_extra.json (Affinity pages only, bundled as EXTRA; `clubs` holds the heritage clubs: {name, short, abbr, color, league, region, base, bonus, hai}): {wc: {nation: World Cup 2026 result}, teams: [{name, short, abbr,
color, confed, base, bonus, region, hai}]} for the 2026 World Cup nations outside the Nations League.
