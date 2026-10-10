// Pick 'em strategy backtest (Kevin, 2026-10-10: "Maximizing expected points is a safe strategy, but not a strong one.
// Let's try some different strategies and backtest them on the season thus far.")
//
//   node scripts/pickem/backtest.js            # all league competitions, walk-forward
//
// Walk-forward: for every match day, the model is rerun with only the results known before that day (later results
// masked), exactly as the app would have seen it. Each strategy then picks a score for that day's matches, and picks are
// scored the app's way (peOutcome 2 for the right result, peExact 3 for the exact score). Tunable strategies are tuned
// on the first half of the season's match days and judged on the second half, so the comparison is out of sample.
const path = require('path'), fs = require('fs');
const root = path.resolve(__dirname, '../..');
const MODEL = require(path.join(root, 'src/model.js'));
const { ORDER, COMPS_CFG, compCfg } = require(path.join(root, 'src/config.js'));
const D = JSON.parse(fs.readFileSync(path.join(root, 'data/suite_data.json'), 'utf8'));
const PO = 2, PE = 3, KM = 6;
const DEF = { sims: 1, impFloor: 0.05, impRamp: 0.25, drawAuto: 1, drawW0: 60 };
const Sfor = p => Object.assign({}, DEF, { halfLife: p.halfLife || 56, k: p.k || 10, h2h: p.h2h ?? 1, h2hK: p.h2hK || 10, rhoPrior: p.rhoPrior ?? -0.13,
  rhoW: p.rhoW || 300, beta: 0.3, underdog: 0.05, drawW: p.drawW ?? 1.05, haPrior: p.haPrior, scPrior: p.scPrior, baseW: p.baseW || 0, peOutcome: PO, peExact: PE, koRes: {} });
const sgn = Math.sign;
const pts = (p, h, a) => (p[0] === h && p[1] === a) ? PE : (sgn(p[0] - p[1]) === sgn(h - a) ? PO : 0);

// ---------------------------------------------------------------- collect walk-forward predictions
const preds = [];   // {k, date, h, a, g (6x6 probs), pH, pD, pA, pred, locked, emp (league scoreline counts before), dayIdx, nDays}
for (const k of ORDER) {
  if (COMPS_CFG[k].cup) continue;
  const d = D[k], comp = { teams: d.teams, fixtures: d.fixtures, params: d.params || {}, cfg: compCfg(k, d.params) };
  const S = Sfor(comp.params);
  const played = d.fixtures.map((f, id) => ({ id, date: f[1], hs: f[4], as: f[5], lk: f.length > 6 ? [f[6], f[7]] : null }))
    .filter(f => Number.isInteger(f.hs) && Number.isInteger(f.as));
  const days = [...new Set(played.map(f => f.date))].sort();
  days.forEach((day, di) => {
    const results = {};
    for (const f of played) if (f.date >= day) results[f.id] = null;   // unknown on the morning of `day`
    const r = MODEL.run(comp, results, S, {}, {});
    const emp = {};
    for (const f of played) if (f.date < day) { const key = `${Math.min(f.hs, 5)}-${Math.min(f.as, 5)}`; emp[key] = (emp[key] || 0) + 1; }
    for (const f of played.filter(f => f.date === day)) {
      const m = r.fx[f.id], g = [];
      for (let h = 0; h < KM; h++) { g.push([]); for (let a = 0; a < KM; a++) g[h].push(m.g[h][a]); }
      preds.push({ k, id: f.id, date: day, hs: f.hs, as: f.as, g, pH: m.pH, pD: m.pD, pA: m.pA, pred: m.pred, ev: m.pick, locked: f.lk, emp, di, nd: days.length, lh: m.lh, la: m.la });
    }
  });
}

if (require.main !== module) { module.exports = { preds }; return; }
// ---------------------------------------------------------------- strategies (each: x -> [h, a])
const cells = g => { const c = []; for (let h = 0; h < KM; h++) for (let a = 0; a < KM; a++) c.push([h, a, g[h][a]]); return c; };
const outP = g => { let H = 0, Dd = 0, A = 0; for (const [h, a, p] of cells(g)) (h > a ? H += p : h === a ? Dd += p : A += p); return [H, Dd, A]; };
function evPick(g, filter) {
  const [H, Dd, A] = outP(g); let best = null, be = -1;
  for (const [h, a, p] of cells(g)) { if (filter && !filter(h, a)) continue; const o = sgn(h - a), r = o > 0 ? H : o === 0 ? Dd : A; const e = PO * r + (PE - PO) * p; if (e > be) { be = e; best = [h, a]; } }
  return best;
}
const norm = g => { const s = g.flat().reduce((x, y) => x + y, 0); return g.map(r => r.map(v => v / s)); };
const blendEmp = (x, w) => { const n = Object.values(x.emp).reduce((s, v) => s + v, 0) || 1;
  return norm(x.g.map((r, h) => r.map((v, a) => (1 - w) * v + w * ((x.emp[`${h}-${a}`] || 0) + 0.5) / (n + 18)))); };
const sharpen = (g, t) => norm(g.map(r => r.map(v => Math.pow(v, t))));
function drawScale(g, f) { const s = g.map((r, h) => r.map((v, a) => h === a ? v * f : v)); return norm(s); }
function topOutcome(g) { const o = outP(g); const i = o.indexOf(Math.max(...o)); return [1, 0, -1][i]; }
function modeIn(g, o) { let b = null, bp = -1; for (const [h, a, p] of cells(g)) if (sgn(h - a) === o && p > bp) { bp = p; b = [h, a]; } return b; }

const S = {
  'Current (max expected points)': x => x.ev,
  'Most likely exact score': x => { let b = null, bp = -1; for (const [h, a, p] of cells(x.g)) if (p > bp) { bp = p; b = [h, a]; } return b; },
  'Predicted score (draw-zone)': x => x.pred,
  'Most likely result, then its likeliest score': x => modeIn(x.g, topOutcome(x.g)),
  'Never pick a draw': x => evPick(x.g, (h, a) => h !== a),
  'Favourite to win by one': x => { const o = topOutcome(x.g); return o === 0 ? [1, 1] : o > 0 ? [2, 1] : [1, 2]; },
};
const TUNED = {
  'Blend with the league\'s actual scorelines': { grid: [0.1, 0.2, 0.3, 0.5, 0.7], f: (x, w) => evPick(blendEmp(x, w)) },
  'Sharpen or flatten the model': { grid: [0.6, 0.8, 1.2, 1.5, 2], f: (x, t) => evPick(sharpen(x.g, t)) },
  'Draw weighting': { grid: [0.6, 0.8, 1.2, 1.4, 1.7], f: (x, c) => evPick(drawScale(x.g, c)) },
};

// ---------------------------------------------------------------- score
const first = x => x.di < x.nd / 2;
function tally(fn, xs) {
  let p = 0, oc = 0, ex = 0, dr = 0; const per = {};
  for (const x of xs) { const pk = fn(x), s = pts(pk, x.hs, x.as); p += s; if (s >= PO) oc++; if (s === PE) ex++; if (pk[0] === pk[1]) dr++;
    per[x.k] = (per[x.k] || 0) + s; }
  return { p, n: xs.length, oc, ex, dr, per };
}
const H1 = preds.filter(first), H2 = preds.filter(x => !first(x));
const rows = [];
for (const [name, fn] of Object.entries(S)) rows.push({ name, all: tally(fn, preds), h2: tally(fn, H2) });
for (const [name, T] of Object.entries(TUNED)) {
  const best = T.grid.map(v => [v, tally(x => T.f(x, v), H1).p]).sort((a, b) => b[1] - a[1])[0][0];
  rows.push({ name: `${name} (${best}, tuned on first half)`, all: tally(x => T.f(x, best), preds), h2: tally(x => T.f(x, best), H2) });
}
const lockedXs = preds.filter(x => x.locked);
const fmt = t => `${t.p} pts in ${t.n} (${(t.p / t.n).toFixed(3)}/match) result ${(t.oc / t.n * 100).toFixed(1)}% exact ${(t.ex / t.n * 100).toFixed(1)}% draws picked ${(t.dr / t.n * 100).toFixed(0)}%`;
console.log(`${preds.length} played league matches, walk-forward; ${H2.length} in the second half of each season`);
console.log(`actual draw rate ${(preds.filter(x => x.hs === x.as).length / preds.length * 100).toFixed(1)}%`);
for (const r of rows.sort((a, b) => b.h2.p - a.h2.p)) console.log(`\n${r.name}\n  2nd half: ${fmt(r.h2)}\n  season:   ${fmt(r.all)}`);
console.log(`\nPicks actually locked in the app (${lockedXs.length} matches): ${fmt(tally(x => x.locked, lockedXs))}`);
console.log(`Current strategy on the same matches: ${fmt(tally(S['Current (max expected points)'], lockedXs))}`);
const pr = {}; for (const r of rows) pr[r.name] = r.all.per; console.log('\nby competition (season points):'); console.log(JSON.stringify(pr, null, 0));

