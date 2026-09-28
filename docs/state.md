# Saved user state (user-data/*.json)

Exported from the claude.ai artifact database (collection `trackers`, one doc per competition +
`suite`). Each doc's fields are JSON **strings** (parse them):
- results: {fixtureId: [hs, as, lockedPickH?, lockedPickA?, lockedFavor?]}  (cup: [hs, as, pensIdx, pickH, pickA, favor])
  null = user cleared a base result.
- settings: per-comp overrides (beta, underdog, drawW, drawAuto, drawW0, halfLife, k, adj:[{i,p,n}])
- favs: [teamIdx...]   status: {id: {p:1 | d:'YYYY-MM-DD', t:'HH:MM' | aw:1}}
- live: {id: {h, a, ph, t, m0}}  (ph '1H'|'HT'|'2H', t = ms of the last tap/typed minute, m0 = minute then;
  older entries {h, a, min, ht?} still load with a fixed minute)   motw: {roundKey: fixtureId|null}   ko: {tieId or tieId-Gn: {hs, as, adv}}
- draws (cup): {fixtureId: [homeIdx, awayIdx]}
- suite doc: {peOutcome, peExact, motwW}
The same structure is what the app writes to localStorage under `football-suite-2627`
(object with results/settings/favs/status/live/motw/ko/draws/suite keyed by competition).
To import: parse each doc and merge into that localStorage object (or your new backend).
