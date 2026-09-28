// Pull results, kickoff times and date moves from ESPN's public scoreboard API into data/suite_data.json.
//
//   node scripts/sync/espn.js                 # last 10 days of results, next 21 days of kickoffs, all competitions
//   node scripts/sync/espn.js --dry           # report only, write nothing
//   node scripts/sync/espn.js --comp epl,mls --back 40 --ahead 0
//
// Rules (docs/sync.md): only fixtures without a base result get one. A base result ESPN disagrees with is
// reported, never replaced. Kevin's own entries live in his synced state, not here: the app flags any of
// them that disagree with the base result. New results carry the pick 'em score and Affinity pick the model
// gave before the match (fixture slots 6-8), the same layout as the results that came with the tracker.
// Extra time, penalties outside the cup, postponements and unknown team names are reported, not applied.
// Writes the report to stdout and, with --report FILE, as markdown to FILE.
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '../..');
const MODEL = require(path.join(root, 'src/model.js'));
const { COMPS_CFG, compCfg } = require(path.join(root, 'src/config.js'));
const ALIAS = require('./espn_aliases.json');   // ESPN name -> tracker name, for names the matcher can't pair

const LEAGUE = { epl: 'eng.1', ch: 'eng.2', cup: 'eng.league_cup', ucl: 'uefa.champions', esp: 'esp.1', ita: 'ita.1', bl: 'ger.1',
  fra: 'fra.1', mls: 'usa.1', usl: 'usa.usl.1', nwsl: 'usa.nwsl', unl: 'uefa.nations' };
// Fixture dates are the local match date: US leagues in Eastern time, everything else in UK time.
const TZ = { mls: 'America/New_York', usl: 'America/New_York', nwsl: 'America/New_York' };
const DAY = 864e5;

const argv = process.argv.slice(2), opt = n => { const i = argv.indexOf('--' + n); return i < 0 ? null : argv[i + 1]; };
const DRY = argv.includes('--dry'), BACK = +(opt('back') ?? 10), AHEAD = +(opt('ahead') ?? 21), REPORT = opt('report');
const COMPS = (opt('comp') || Object.keys(LEAGUE).join(',')).split(',');
const today = opt('today') ? Date.parse(opt('today')) : Date.now();
const dataFile = path.join(root, 'data/suite_data.json');
const D = JSON.parse(fs.readFileSync(dataFile, 'utf8'));

const ymd = t => new Date(t).toISOString().slice(0, 10);
const localDate = (k, iso) => new Intl.DateTimeFormat('en-CA', { timeZone: TZ[k] || 'Europe/London' }).format(new Date(iso));
const norm = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/ø/gi, 'o').replace(/ß/g, 'ss').toLowerCase().replace(/\b(fc|afc|cf|sc|ac|club|de|the)\b/g, '').replace(/[^a-z0-9]/g, '');

async function get(url, tries = 4) {
  for (let i = 0; ; i++) {
    try { const r = await fetch(url); if (r.ok) return await r.json(); if (r.status < 500) return null; } catch (e) { if (i >= tries) throw e; }
    if (i >= tries) return null;
    await new Promise(res => setTimeout(res, 1000 * 2 ** i));
  }
}
// ESPN's soccer scoreboard only answers one day at a time. Its calendar lists the days with matches.
async function events(league, from, to) {
  const base = `https://site.api.espn.com/apis/site/v2/sports/soccer/${league}/scoreboard`;
  const first = await get(base);
  const lg = first && first.leagues && first.leagues[0];
  // Leagues list match days; cups and UEFA competitions list stages instead, so those get asked day by day.
  const days = (lg && lg.calendarType === 'day' && lg.calendar || [])
    .map(c => typeof c === 'string' ? c : c.startDate || c.value).filter(Boolean).map(c => ymd(Date.parse(c)));
  const want = []; for (let t = from; t <= to; t += DAY) want.push(ymd(t));
  // Calendar days are UTC midnights of local match days; also ask for the next UTC day to catch late US kickoffs.
  const cal = new Set(days.flatMap(d => [d, ymd(Date.parse(d) + DAY)]));
  const ask = days.length ? want.filter(d => cal.has(d)) : want;
  const out = new Map();
  for (let i = 0; i < ask.length; i += 6) {
    const got = await Promise.all(ask.slice(i, i + 6).map(d => get(`${base}?dates=${d.replace(/-/g, '')}`)));
    for (const j of got) for (const e of (j && j.events) || []) out.set(e.id, e);
  }
  return [...out.values()].map(e => {
    const c = e.competitions[0], side = w => c.competitors.find(x => x.homeAway === w);
    const h = side('home'), a = side('away'), st = (c.status || e.status).type;
    const team = x => ({ name: x.team.displayName, short: x.team.shortDisplayName, abbr: x.team.abbreviation, loc: x.team.location });
    return { id: e.id, date: c.date || e.date, timeValid: c.timeValid !== false, state: st.state, status: st.name, detail: st.description,
      h: team(h), a: team(a), hs: parseInt(h.score, 10), as: parseInt(a.score, 10), hso: h.shootoutScore, aso: a.shootoutScore,
      hw: h.winner, aw: a.winner };
  });
}

function teamMatcher(k, teams) {
  const byName = new Map(teams.map((t, i) => [t.name, i]));
  const keys = teams.map(t => [t.name, t.short].filter(Boolean).map(norm));
  return x => {
    for (const n of [x.name, x.short, x.loc]) if (n && byName.has(ALIAS[n])) return byName.get(ALIAS[n]);
    for (const n of [x.name, x.short, x.loc].filter(Boolean).map(norm)) {
      const hits = keys.map((ks, i) => ks.includes(n) ? i : -1).filter(i => i >= 0);
      if (hits.length === 1) return hits[0];
    }
    return -2;
  };
}

// Pick 'em score and Affinity pick the model gives each unplayed fixture right now (default settings).
function picksNow(k) {
  const L = D[k], p = L.params || {};
  const comp = { teams: L.teams, fixtures: L.fixtures, params: p, cfg: compCfg(k, p) };
  const S = { sims: 50, impFloor: 0.05, impRamp: 0.25, drawAuto: 1, drawW0: 60, halfLife: p.halfLife || 56, k: p.k || 10, h2h: p.h2h ?? 1,
    h2hK: p.h2hK || 10, rhoPrior: p.rhoPrior ?? -0.13, rhoW: p.rhoW || 300, beta: 0.3, underdog: 0.05, drawW: p.drawW ?? 1.05,
    haPrior: p.haPrior, scPrior: p.scPrior, baseW: p.baseW || 0, peOutcome: 2, peExact: 3, koRes: {} };
  return MODEL.run(comp, {}, S, Object.assign({}, L.statusDefault), {}).fx;
}

const report = [];
async function syncComp(k) {
  const L = D[k], cup = !!COMPS_CFG[k].cup, T = L.teams, F = L.fixtures, kick = L.kick = L.kick || {};
  const I = cup ? { date: 2, h: 3, a: 4, hs: 5, as: 6 } : { date: 1, h: 2, a: 3, hs: 4, as: 5 };
  const evs = await events(LEAGUE[k], today - BACK * DAY, today + AHEAD * DAY);
  const team = teamMatcher(k, T), used = new Set();
  const R = { results: [], disagree: [], times: [], dates: [], unknown: new Set(), unmatched: [], skipped: [] };
  const lab = f => `${T[f[I.h]].short || T[f[I.h]].name} v ${T[f[I.a]].short || T[f[I.a]].name}`;
  const pending = [];
  for (const e of evs.sort((x, y) => x.date.localeCompare(y.date))) {
    const h = team(e.h), a = team(e.a);
    if (h < 0) R.unknown.add(e.h.name); if (a < 0) R.unknown.add(e.a.name);
    if (h < 0 || a < 0) continue;
    const t = Date.parse(e.date);
    const cands = F.map((f, id) => ({ f, id })).filter(({ f, id }) => f[I.h] === h && f[I.a] === a && !used.has(id))
      .sort((x, y) => Math.abs(Date.parse(x.f[I.date]) - t) - Math.abs(Date.parse(y.f[I.date]) - t));
    if (!cands.length) { R.unmatched.push(`${e.h.name} v ${e.a.name} ${e.date.slice(0, 10)}`); continue; }
    const { f, id } = cands[0]; used.add(id);
    const hasBase = Number.isInteger(f[I.hs]) && Number.isInteger(f[I.as]);
    if (e.state === 'post') {
      if (!/FULL_TIME|STATUS_FINAL$|FINAL_PEN/.test(e.status) || !Number.isInteger(e.hs)) { R.skipped.push(`${lab(f)} ${f[I.date]}: ${e.detail}`); continue; }
      // Pick 'em counts the 90-minute score: only cup ties below the final go straight to penalties.
      if (/FINAL_PEN/.test(e.status) && (!cup || f[0] === 'Final')) { R.skipped.push(`${lab(f)} ${f[I.date]}: ${e.detail}`); continue; }
      if (hasBase) { if (f[I.hs] !== e.hs || f[I.as] !== e.as) R.disagree.push(`${lab(f)} ${f[I.date]}: tracker ${f[I.hs]}–${f[I.as]}, ESPN ${e.hs}–${e.as}`); continue; }
      pending.push({ id, e });
      continue;
    }
    if (hasBase) continue;
    if (e.status === 'STATUS_POSTPONED' || e.status === 'STATUS_CANCELED') { R.skipped.push(`${lab(f)} ${f[I.date]}: ${e.detail}`); continue; }
    if (e.state !== 'pre') continue;
    const d = localDate(k, e.date);
    if (d !== f[I.date]) { R.dates.push(`${lab(f)}: ${f[I.date]} → ${d}`); f[I.date] = d; }
    if (e.timeValid) {
      const iso = new Date(e.date).toISOString().slice(0, 16) + 'Z', old = kick[id];
      if (!old || old[0] !== iso || !old[1]) { R.times.push(`${lab(f)}: ${old ? old[0] + (old[1] ? '' : ' (TBC)') : 'none'} → ${iso}`); kick[id] = [iso, 1]; }
    }
  }
  if (pending.length) {
    const fx = cup ? null : picksNow(k);
    for (const { id, e } of pending) {
      const f = F[id];
      f[I.hs] = e.hs; f[I.as] = e.as;
      const d = localDate(k, e.date);
      if (d !== f[I.date]) { R.dates.push(`${lab(f)}: ${f[I.date]} → ${d} (played)`); f[I.date] = d; }
      if (cup) f[7] = e.hs === e.as ? (e.hso > e.aso || e.hw ? f[I.h] : f[I.a]) : null;
      else if (fx[id].pick) { f.length = 6; f.push(fx[id].pick[0], fx[id].pick[1], fx[id].favored || 'H'); }
      R.results.push(`${lab(f)} ${e.hs}–${e.as}${cup && f[7] != null ? ` (${T[f[7]].short || T[f[7]].name} on pens)` : ''}`);
    }
  }
  if (R.results.length || R.times.length || R.dates.length) L.synced = ymd(today);
  report.push({ k, name: COMPS_CFG[k].name, events: evs.length, ...R, unknown: [...R.unknown] });
}

(async () => {
  for (const k of COMPS) {
    try { await syncComp(k); } catch (e) { report.push({ k, name: COMPS_CFG[k].name, error: String(e) }); }
  }
  const lines = [];
  let changed = 0;
  for (const r of report) {
    if (r.error) { lines.push(`## ${r.name}\nError: ${r.error}\n`); continue; }
    changed += r.results.length + r.times.length + r.dates.length;
    const parts = [`## ${r.name}`, `${r.events} ESPN matches checked. ${r.results.length} new results, ${r.times.length} kickoff times set, ${r.dates.length} date moves.`];
    const list = (title, xs) => { if (xs.length) parts.push(`${title}:`, ...xs.map(x => `- ${x}`)); };
    list('New results', r.results); list('Date moves', r.dates); list('Kickoff times', r.times);
    list('DISAGREES with the tracker (not changed)', r.disagree); list('Not applied', r.skipped);
    list('Team names with no match (add to scripts/sync/espn_aliases.json)', r.unknown); list('No fixture found', r.unmatched.slice(0, 10));
    lines.push(parts.join('\n') + '\n');
  }
  const text = `# ESPN sync ${ymd(today)}${DRY ? ' (dry run)' : ''}\n\n` + lines.join('\n');
  console.log(text);
  if (REPORT) fs.writeFileSync(REPORT, text);
  if (!DRY && changed) {
    // Python writes the file so the rest of it stays byte-identical (Python keeps floats like 0.0; JSON.stringify doesn't).
    // Only fixtures, kick and synced change; they hold no floats.
    const patch = Object.fromEntries(report.filter(r => !r.error && (r.results.length || r.times.length || r.dates.length))
      .map(r => [r.k, { fixtures: D[r.k].fixtures, kick: D[r.k].kick, synced: D[r.k].synced }]));
    require('child_process').execFileSync('python3', ['-c', `import json,sys
f=sys.argv[1]; D=json.load(open(f)); P=json.load(sys.stdin)
for k,v in P.items(): D[k].update(v)
open(f,'w').write(json.dumps(D,ensure_ascii=False,separators=(',',':')))`, dataFile], { input: JSON.stringify(patch) });
  }
  if (report.some(r => r.error)) process.exitCode = 1;
})();
