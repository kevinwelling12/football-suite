// Blend betting-market odds into the pick 'em model and backtest it (Kevin, 2026-10-10: "blend in betting market odds").
//
//   node scripts/pickem/blend.js          # needs scripts/odds/history.json (python3 scripts/odds/history.py)
//
// For every played match with odds: market probabilities = 1/odds, margin removed proportionally. A market scoreline
// grid is fitted to them: total goals from the over/under 2.5 price when given (else the model's total), the home-away
// split so the grid's P(home) - P(away) matches the market's, and the draw cell weights scaled so P(draw) matches too.
// The pick uses (1 - w) x model grid + w x market grid; w = 0 is today's model. Same walk-forward model predictions as
// backtest.js; w is chosen on the first half of each season's match days and judged on the second half.
const path = require('path'), fs = require('fs');
const { preds } = require('./backtest.js');
const ODDS = JSON.parse(fs.readFileSync(path.join(__dirname, '../odds/history.json'), 'utf8'));
const KM = 6, sgn = Math.sign, pts = (p, h, a) => (p[0] === h && p[1] === a) ? 3 : (sgn(p[0] - p[1]) === sgn(h - a) ? 2 : 0);
const pois = l => { const v = [Math.exp(-l)]; for (let k = 1; k < KM; k++) v.push(v[k - 1] * l / k); return v; };
function marketGrid(o, lh, la) {
  let iH = 1 / o.H, iD = 1 / o.D, iA = 1 / o.A; const s = iH + iD + iA; const pH = iH / s, pD = iD / s, pA = iA / s;
  let T = lh + la;
  if (o.O && o.U) { const pO = (1 / o.O) / (1 / o.O + 1 / o.U); let lo = 0.5, hi = 6;
    for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2, p = pois(m), under = p[0] + p[1] + p[2]; if (1 - under < pO) lo = m; else hi = m; } T = (lo + hi) / 2; }
  const diff = pH - pA; let lo = -T + 0.05, hi = T - 0.05, g;
  const build = sup => { const a = pois((T + sup) / 2), b = pois((T - sup) / 2); return a.map(x => b.map(y => x * y)); };
  const hd = g => { let H = 0, A = 0; g.forEach((r, h) => r.forEach((v, a) => { if (h > a) H += v; else if (h < a) A += v; })); return H - A; };
  for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (hd(build(m)) < diff) lo = m; else hi = m; }
  g = build((lo + hi) / 2);
  // scale draws to the market's draw probability, wins and losses to theirs
  let H = 0, Dd = 0, A = 0; g.forEach((r, h) => r.forEach((v, a) => { if (h > a) H += v; else if (h === a) Dd += v; else A += v; }));
  return g.map((r, h) => r.map((v, a) => h > a ? v * pH / H : h === a ? v * pD / Dd : v * pA / A));
}
const blend = (x, w) => x.g.map((r, h) => r.map((v, a) => (1 - w) * v + w * x.mg[h][a]));
function evPick(g) {
  let H = 0, Dd = 0, A = 0; g.forEach((r, h) => r.forEach((v, a) => { if (h > a) H += v; else if (h === a) Dd += v; else A += v; }));
  let best = null, be = -1; g.forEach((r, h) => r.forEach((v, a) => { const o = sgn(h - a), e = 2 * (o > 0 ? H : o === 0 ? Dd : A) + v; if (e > be) { be = e; best = [h, a]; } }));
  return { pick: best, H, D: Dd, A };
}
const xs = preds.filter(x => ODDS[x.k] && ODDS[x.k][x.id]).map(x => Object.assign(x, { mg: marketGrid(ODDS[x.k][x.id], x.lh, x.la) }));
const first = x => x.di < x.nd / 2;
function score(sub, w) {
  let p = 0, ll = 0, oc = 0, ex = 0;
  for (const x of sub) { const r = evPick(blend(x, w)), s = pts(r.pick, x.hs, x.as); p += s; if (s >= 2) oc++; if (s === 3) ex++;
    const tot = r.H + r.D + r.A, q = (x.hs > x.as ? r.H : x.hs === x.as ? r.D : r.A) / tot; ll -= Math.log(Math.max(q, 1e-6)); }
  return { p, n: sub.length, ppm: p / sub.length, ll: ll / sub.length, oc: oc / sub.length, ex: ex / sub.length };
}
const W = [0, 0.25, 0.5, 0.75, 1];
const groups = { 'European leagues': x => x.k !== 'mls', MLS: x => x.k === 'mls', All: () => true };
console.log(`${xs.length} played matches with odds (of ${preds.length})`);
const res = {};
for (const [gname, gf] of Object.entries(groups)) {
  const sub = xs.filter(gf), h1 = sub.filter(first), h2 = sub.filter(x => !first(x));
  const best = W.map(w => [w, score(h1, w).ll]).sort((a, b) => a[1] - b[1])[0][0];
  console.log(`\n${gname}: ${sub.length} matches; weight chosen on the first half (lowest log loss): ${best}`);
  for (const w of W) { const a = score(sub, w), b = score(h2, w);
    console.log(`  w=${w}: season ${a.p} pts (${a.ppm.toFixed(3)}/match, result ${(a.oc * 100).toFixed(1)}%, exact ${(a.ex * 100).toFixed(1)}%, log loss ${a.ll.toFixed(4)}) | 2nd half ${b.p} pts, log loss ${b.ll.toFixed(4)}`); }
  res[gname] = best;
}
// paired difference market-only vs model for a noise check
const sub = xs, d = sub.map(x => pts(evPick(blend(x, 0.75)).pick, x.hs, x.as) - pts(evPick(blend(x, 0)).pick, x.hs, x.as));
const m = d.reduce((s, v) => s + v, 0) / d.length, sd = Math.sqrt(d.reduce((s, v) => s + (v - m) ** 2, 0) / (d.length - 1));
console.log(`\nw=0.75 vs model alone: ${(m * d.length).toFixed(0)} pts over ${d.length} matches, standard error ${(sd * Math.sqrt(d.length)).toFixed(0)}`);
