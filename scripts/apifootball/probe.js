// What does API-Football's plan give us for our 12 competitions? (Kevin, 2026-10-11: "Doesn't hurt to see what the free plan offers")
//
//   APIFOOTBALL_KEY=... node scripts/apifootball/probe.js      # about 40 requests (free plan: 100 a day)
//
// For each competition: the season's coverage flags (statistics, lineups, injuries, odds, players), whether a finished
// match carries expected goals (xG) in its statistics, and how many fixtures have pre-match odds (and from how many
// bookmakers). Writes scripts/apifootball/probe.json and prints a summary. The key is read from the environment only.
const fs = require('fs'), path = require('path');
const KEY = process.env.APIFOOTBALL_KEY;
if (!KEY) { console.error('Set APIFOOTBALL_KEY (environment secret).'); process.exit(1); }
const BASE = 'https://v3.football.api-sports.io';
let used = 0;
async function api(p) {
  used++;
  const r = await fetch(BASE + p, { headers: { 'x-apisports-key': KEY } });
  const j = await r.json();
  if (j.errors && Object.keys(j.errors).length) return { error: j.errors, response: [] };
  await new Promise(res => setTimeout(res, 2200));   // free plan: about 30 requests a minute
  return j;
}
// API-Football league ids; European seasons are named by their starting year.
const COMPS = { epl: [39, 2026], ch: [40, 2026], cup: [48, 2026], ucl: [2, 2026], esp: [140, 2026], ita: [135, 2026], bl: [78, 2026],
  fra: [61, 2026], mls: [253, 2026], usl: [255, 2026], nwsl: [254, 2026], unl: [5, 2026] };

(async () => {
  const status = await api('/status');
  const out = { plan: status.response && status.response.subscription, requests: status.response && status.response.requests, comps: {} };
  for (const [k, [id, season]] of Object.entries(COMPS)) {
    const o = out.comps[k] = { id, season };
    const lg = await api(`/leagues?id=${id}&season=${season}`);
    const s = lg.response[0] && lg.response[0].seasons.find(x => x.year === season);
    o.name = lg.response[0] && lg.response[0].league.name;
    o.coverage = s ? s.coverage : (lg.error || 'season not available');
    if (!s) continue;
    const fx = await api(`/fixtures?league=${id}&season=${season}&status=FT`);
    o.finished = fx.response.length; if (fx.error) o.fixturesError = fx.error;
    const last = fx.response.sort((a, b) => b.fixture.timestamp - a.fixture.timestamp)[0];
    if (last) {
      const st = await api(`/fixtures/statistics?fixture=${last.fixture.id}`);
      const types = new Set(st.response.flatMap(t => t.statistics.map(x => x.type)));
      o.statsTypes = [...types]; o.xG = types.has('expected_goals');
      o.sample = `${last.teams.home.name} v ${last.teams.away.name} ${last.fixture.date.slice(0, 10)}`;
    }
    const od = await api(`/odds?league=${id}&season=${season}`);
    o.oddsFixtures = od.results || 0; if (od.error) o.oddsError = od.error;
    o.bookmakers = od.response[0] ? od.response[0].bookmakers.length : 0;
  }
  out.used = used;
  fs.writeFileSync(path.join(__dirname, 'probe.json'), JSON.stringify(out, null, 1));
  console.log('plan', JSON.stringify(out.plan), 'requests', JSON.stringify(out.requests));
  for (const [k, o] of Object.entries(out.comps)) {
    const c = o.coverage && o.coverage.fixtures ? o.coverage : null;
    console.log(`${k.padEnd(5)} ${(o.name || '').padEnd(26)} ` + (c ? `stats ${c.fixtures.statistics_fixtures ? 'y' : 'n'} lineups ${c.fixtures.lineups ? 'y' : 'n'} injuries ${c.injuries ? 'y' : 'n'} odds ${c.odds ? 'y' : 'n'} players ${c.players ? 'y' : 'n'}` : JSON.stringify(o.coverage)) +
      ` | finished ${o.finished ?? '-'} | xG ${o.xG ?? '-'} | odds fixtures ${o.oddsFixtures ?? '-'} (${o.bookmakers || 0} books)`);
  }
  console.log('requests used', used);
})();
