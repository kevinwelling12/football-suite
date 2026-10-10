// Model-setting sweep for pick 'em (walk-forward, same scoring as backtest.js). Settings are judged on the second half
// of each season's match days after choosing on the first half.
const path = require('path'), fs = require('fs');
const root = path.resolve(__dirname, '../..');
const MODEL = require(path.join(root, 'src/model.js'));
const { ORDER, COMPS_CFG, compCfg } = require(path.join(root, 'src/config.js'));
const D = JSON.parse(fs.readFileSync(path.join(root, 'data/suite_data.json'), 'utf8'));
const sgn = Math.sign, pts = (p, h, a) => (p[0] === h && p[1] === a) ? 3 : (sgn(p[0] - p[1]) === sgn(h - a) ? 2 : 0);
function run(over) {
  const out = { h1: 0, h2: 0, n1: 0, n2: 0 };
  for (const k of ORDER) {
    if (COMPS_CFG[k].cup) continue;
    const d = D[k], comp = { teams: d.teams, fixtures: d.fixtures, params: d.params || {}, cfg: compCfg(k, d.params) }, p = comp.params;
    const S = Object.assign({ sims: 1, impFloor: .05, impRamp: .25, drawAuto: 1, drawW0: 60, halfLife: p.halfLife || 56, k: p.k || 10, h2h: p.h2h ?? 1,
      h2hK: p.h2hK || 10, rhoPrior: p.rhoPrior ?? -0.13, rhoW: p.rhoW || 300, beta: .3, underdog: .05, drawW: p.drawW ?? 1.05, haPrior: p.haPrior,
      scPrior: p.scPrior, baseW: p.baseW || 0, peOutcome: 2, peExact: 3, koRes: {} }, over);
    const played = d.fixtures.map((f, id) => ({ id, date: f[1], hs: f[4], as: f[5] })).filter(f => Number.isInteger(f.hs) && Number.isInteger(f.as));
    const days = [...new Set(played.map(f => f.date))].sort();
    days.forEach((day, di) => {
      const res = {}; for (const f of played) if (f.date >= day) res[f.id] = null;
      const r = MODEL.run(comp, res, S, {}, {});
      for (const f of played.filter(f => f.date === day)) { const s = pts(r.fx[f.id].pick, f.hs, f.as); if (di < days.length / 2) { out.h1 += s; out.n1++; } else { out.h2 += s; out.n2++; } }
    });
  }
  return out;
}
const base = run({}); console.log('current settings', JSON.stringify(base));
const tests = [['halfLife', [21, 35, 90, 150, 365]], ['k', [3, 6, 15, 25, 40]], ['h2h', [0]], ['drawAuto', [0]], ['rhoW', [30, 1000]]];
for (const [key, vals] of tests) for (const v of vals) { const o = run({ [key]: v }); console.log(`${key}=${v}`, `h1 ${o.h1 - base.h1 >= 0 ? '+' : ''}${o.h1 - base.h1}`, `h2 ${o.h2 - base.h2 >= 0 ? '+' : ''}${o.h2 - base.h2}`, `(of ${base.n1}/${base.n2} matches)`); }
