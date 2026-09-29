// Suite model: leagues (with groups), UCL/UNL knockout extensions, and the Carabao Cup engine.
const MODEL = (() => {
  const KMAX = 10;
  const RC_OWN = 0.67, RC_OPP = 1.25;
  const poisVec = l => { const v = new Float64Array(KMAX + 1); v[0] = Math.exp(-l); for (let i = 1; i <= KMAX; i++) v[i] = v[i - 1] * l / i; return v; };
  function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function poisSample(rand, l) { const L = Math.exp(-l); let k = 0, p = rand(); while (p > L) { k++; p *= rand(); } return k; }
  function grid(lh, la, rho) {
    const ph = poisVec(lh), pa = poisVec(la), g = [];
    for (let h = 0; h <= KMAX; h++) { g.push(new Float64Array(KMAX + 1)); for (let a = 0; a <= KMAX; a++) g[h][a] = ph[h] * pa[a]; }
    if (rho) { g[0][0] *= 1 - lh * la * rho; g[0][1] *= 1 + lh * rho; g[1][0] *= 1 + la * rho; g[1][1] *= 1 - rho; }
    let H = 0, D = 0, A = 0;
    for (let h = 0; h <= KMAX; h++) for (let a = 0; a <= KMAX; a++) { const p = g[h][a]; if (h > a) H += p; else if (h === a) D += p; else A += p; }
    return { g, H, D, A };
  }
  const winDraw = (la, lb) => { const r = grid(la, lb, 0); return [r.H, r.D]; };
  // P(a beats b) in a knockout: two legs (combined rates) or single neutral match; extra time = a third of a match; pens 50/50
  function advance(la, lb, laET, lbET, et, pen) {
    const [w, d] = winDraw(la, lb);
    if (!et) return w + pen * d;
    const [w2, d2] = winDraw(laET, lbET);
    return w + d * (w2 + pen * d2);
  }
  function picks(f, S) {
    let pk = null, pkEV = -1; const ev = [];
    for (let h = 0; h <= 5; h++) for (let a = 0; a <= 5; a++) {
      const oo = Math.sign(h - a), p = f.g[h][a], res = oo > 0 ? f.pH : oo === 0 ? f.pD : f.pA;
      const e = S.peOutcome * res + (S.peExact - S.peOutcome) * p;
      ev.push({ h, a, e, p }); if (e > pkEV) { pkEV = e; pk = [h, a]; }
    }
    f.pick = pk; f.pickEV = pkEV; f.evList = ev.sort((x, y) => y.e - x.e).slice(0, 5);
  }
  function scorePick(f, S) {
    const pp = f.pick, po = Math.sign(pp[0] - pp[1]), ao = Math.sign(f.hs - f.as);
    f.pickPts = (pp[0] === f.hs && pp[1] === f.as) ? S.peExact : (po === ao ? S.peOutcome : 0);
  }

  // ============================================================================ leagues
  function run(comp, results, S, status, live) {
    status = status || {}; live = live || {};
    const T = comp.teams, N = T.length, C = comp.cfg;
    const fx = comp.fixtures.map((f, id) => {
      const r = results[id];
      const hs = r !== undefined ? (r ? r[0] : null) : f[4], as = r !== undefined ? (r ? r[1] : null) : f[5];
      const played = Number.isInteger(hs) && Number.isInteger(as);
      const st = status[id] || {}, date = st.d || f[1];
      return { id, mw: f[0], date, h: f[2], a: f[3], hs: played ? hs : null, as: played ? as : null, played, t: Date.parse(date) / 864e5,
               postponed: !played && !!st.p, awarded: played && !!st.aw };
    });
    const playedAll = fx.filter(f => f.played), played = playedAll.filter(f => !f.awarded), nPlayed = playedAll.length;
    const xi = Math.log(2) / S.halfLife;
    const anchor = nPlayed ? Math.max(...played.map(f => f.t)) : fx[0].t;
    let sw = 0, swh = 0, swa = 0;
    for (const f of played) { f.w = Math.exp(-xi * (anchor - f.t)); sw += f.w; swh += f.w * f.hs; swa += f.w * f.as; }
    let homeRate, awayRate;
    if (S.baseW) {
      const sc = nPlayed ? (nPlayed * ((swh + swa) / sw / 2) + S.baseW * S.scPrior) / (nPlayed + S.baseW) : S.scPrior;
      const ha = nPlayed && swa ? (nPlayed * (swh / swa) + S.baseW * S.haPrior) / (nPlayed + S.baseW) : S.haPrior;
      homeRate = sc * 2 * ha / (1 + ha); awayRate = sc * 2 / (1 + ha);
    } else { homeRate = sw ? swh / sw : 1.5; awayRate = sw ? swa / sw : 1.3; }
    const avgRate = (homeRate + awayRate) / 2;
    let att = new Float64Array(N).fill(1), def = new Float64Array(N).fill(1);
    const gf = new Float64Array(N), ga = new Float64Array(N);
    for (const f of played) { gf[f.h] += f.w * f.hs; gf[f.a] += f.w * f.as; ga[f.h] += f.w * f.as; ga[f.a] += f.w * f.hs; }
    for (let it = 0; it < 5; it++) {
      const dA = new Float64Array(N), dD = new Float64Array(N);
      for (const f of played) { dA[f.h] += homeRate * f.w * def[f.a]; dA[f.a] += awayRate * f.w * def[f.h]; dD[f.h] += awayRate * f.w * att[f.a]; dD[f.a] += homeRate * f.w * att[f.h]; }
      const nA = new Float64Array(N), nD = new Float64Array(N);
      for (let i = 0; i < N; i++) { nA[i] = (gf[i] + S.k * avgRate * T[i].pa) / (dA[i] + S.k * avgRate); nD[i] = (ga[i] + S.k * avgRate * T[i].pd) / (dD[i] + S.k * avgRate); }
      const mA = nA.reduce((s, x) => s + x, 0) / N, mD = nD.reduce((s, x) => s + x, 0) / N;
      att = nA.map(x => x / mA); def = nD.map(x => x / mD);
    }
    for (const f of fx) { f.bh = homeRate * att[f.h] * def[f.a]; f.ba = awayRate * att[f.a] * def[f.h]; f.surprise = f.played ? (f.hs - f.as) - (f.bh - f.ba) : 0; }
    for (const f of fx) {
      let same = 0, rev = 0, n = 0;
      for (const g of played) {
        if (f.played && g.t >= f.t) continue;
        if (g.h === f.h && g.a === f.a) { same += g.surprise; n++; } else if (g.h === f.a && g.a === f.h) { rev += g.surprise; n++; }
      }
      const adj = S.h2h ? (same - rev) / (n + S.h2hK) : 0, tot = f.bh + f.ba, sup = f.bh - f.ba + adj;
      f.lh = Math.max(0.05, (tot + sup) / 2); f.la = Math.max(0.05, (tot - sup) / 2);
    }
    let D0 = 0, gsum = 0, obs = 0;
    for (const f of played) { const ph = poisVec(f.lh), pa = poisVec(f.la); for (let k = 0; k <= KMAX; k++) D0 += ph[k] * pa[k]; gsum += -f.lh * f.la * ph[0] * pa[0] - ph[1] * pa[1]; if (f.hs === f.as) obs++; }
    const rhoFit = nPlayed && gsum ? Math.min(0.1, Math.max(-0.3, (obs - D0) / gsum)) : S.rhoPrior;
    const rho = (nPlayed * rhoFit + S.rhoW * S.rhoPrior) / (nPlayed + S.rhoW);
    for (const f of fx) { const r = grid(f.lh, f.la, rho); f.g = r.g; f.pH = r.H; f.pD = r.D; f.pA = r.A; }
    // ---- draw-rate calibration: scale every scoreline grid's draws so the model's average draw chance
    //      over played matches matches the league's observed rate (shrunk toward its long-run norm)
    let drawFactor = 1, drawTarget = null;
    if (S.drawAuto && C.drawPrior) {
      const nP = played.length, obsD = nP ? played.filter(f => f.hs === f.as).length / nP : 0;
      drawTarget = (nP * obsD + S.drawW0 * C.drawPrior) / (nP + S.drawW0);
      const basis = nP ? played : fx;
      const meanPD = d => basis.reduce((s, f) => s + d * f.pD / (1 - f.pD + d * f.pD), 0) / basis.length;
      let lo = 0.3, hi = 3;
      for (let it = 0; it < 50; it++) { const mid = (lo + hi) / 2; if (meanPD(mid) < drawTarget) lo = mid; else hi = mid; }
      drawFactor = (lo + hi) / 2;
      for (const f of fx) {
        const norm = 1 - f.pD + drawFactor * f.pD;
        for (let h = 0; h <= KMAX; h++) for (let a = 0; a <= KMAX; a++) f.g[h][a] = (h === a ? f.g[h][a] * drawFactor : f.g[h][a]) / norm;
        f.pH /= norm; f.pA /= norm; f.pD = f.pD * drawFactor / norm;
      }
    }
    const gaps = fx.map(f => Math.abs(f.pH - f.pA)).sort((x, y) => x - y), drawShare = fx.reduce((s, f) => s + f.pD, 0) / fx.length;
    const pos_ = drawShare * (gaps.length - 1), lo = Math.floor(pos_);
    const drawZone = gaps[lo] + (gaps[Math.min(lo + 1, gaps.length - 1)] - gaps[lo]) * (pos_ - lo);
    for (const f of fx) {
      const o = Math.abs(f.pH - f.pA) < drawZone ? 0 : Math.sign(f.pH - f.pA);
      let best = null, bestP = -1;
      for (let h = 0; h <= 4; h++) for (let a = 0; a <= 4; a++) if (Math.sign(h - a) === o && f.g[h][a] > bestP) { bestP = f.g[h][a]; best = [h, a]; }
      f.pred = best; picks(f, S);
      const rr = results[f.id], src = comp.fixtures[f.id];
      if (f.played && rr && rr.length >= 4) f.pick = [rr[2], rr[3]];
      else if (f.played && rr === undefined && src.length > 6) f.pick = [src[6], src[7]];
      if (f.played && !f.awarded) scorePick(f, S);
    }
    // ---- in-progress matches: final score = current score + goals still to come
    for (const f of fx) {
      const L = live[f.id]; if (f.played || !L) continue;
      const rem = Math.max(0.02, (90 - Math.min(L.min, 90)) / 90);
      // Red cards change the scoring rates for the rest of the match: per player sent off, that side's rate
      // x0.67 and the opponent's x1.25 (Vecer, Kopriva & Ichiba 2009; Titman et al. 2015 find similar).
      const rc = L.rc || [0, 0], nh = Math.min(rc[0], 3), na = Math.min(rc[1], 3);
      const mh = RC_OWN ** nh * RC_OPP ** na, ma = RC_OWN ** na * RC_OPP ** nh;
      f.live = { h: L.h, a: L.a, min: L.min, ht: L.ht, rc: [rc[0], rc[1]], rh: f.lh * rem * mh, ra: f.la * rem * ma };
      const ph = poisVec(f.live.rh), pa = poisVec(f.live.ra);
      let H = 0, D = 0, A = 0, ex = 0, oc = 0; const po = Math.sign(f.pick[0] - f.pick[1]);
      for (let x = 0; x <= KMAX; x++) for (let y = 0; y <= KMAX; y++) {
        const p = ph[x] * pa[y], fh = L.h + x, fa = L.a + y, o = Math.sign(fh - fa);
        if (o > 0) H += p; else if (o === 0) D += p; else A += p;
        if (fh === f.pick[0] && fa === f.pick[1]) ex += p;
        if (o === po) oc += p;
      }
      Object.assign(f.live, { pH: H, pD: D, pA: A, pExact: ex, pOutcome: oc, ev: S.peOutcome * oc + (S.peExact - S.peOutcome) * ex });
    }
    // ---- tables
    const tab = T.map((t, i) => ({ i, group: t.group || '', P: 0, W: 0, D: 0, L: 0, GF: 0, GA: 0, Pts: 0 }));
    for (const f of playedAll) {
      const H = tab[f.h], A = tab[f.a]; H.P++; A.P++; H.GF += f.hs; H.GA += f.as; A.GF += f.as; A.GA += f.hs;
      if (f.hs > f.as) { H.W++; A.L++; H.Pts += 3; } else if (f.hs < f.as) { A.W++; H.L++; A.Pts += 3; } else { H.D++; A.D++; H.Pts++; A.Pts++; }
    }
    // points adjustments (deductions or awards) from Settings
    for (const a of (S.adj || [])) if (tab[a.i]) { tab[a.i].Pts += a.p; tab[a.i].adj = (tab[a.i].adj || 0) + a.p; tab[a.i].adjNote = [tab[a.i].adjNote, a.n].filter(Boolean).join('; '); }
    const key = r => r.Pts * 1e6 + (r.GF - r.GA + 300) * 1e3 + r.GF;
    const games = {}; for (const f of fx) { games[f.h] = (games[f.h] || 0) + 1; games[f.a] = (games[f.a] || 0) + 1; }
    for (const r of tab) {
      const peers = C.grouped ? tab.filter(o => o.group === r.group) : tab;
      r.pos = 1 + peers.filter(o => key(o) > key(r)).length;
      r.gpos = r.pos;
      r.opos = 1 + tab.filter(o => key(o) > key(r)).length;
      const same = peers.filter(o => key(o) === key(r)).length;
      r.avgRank = r.pos - 1 + (same + 1) / 2;
      r.left = games[r.i] - r.P; r.max = r.Pts + 3 * r.left;
    }
    for (const r of tab) {
      const peers = C.grouped ? tab.filter(o => o.group === r.group) : tab;
      const out = peers.filter(o => o.Pts > r.max).length, catch_ = peers.filter(o => o !== r && o.max > r.Pts).length;
      r.status = '';
      for (const s of C.status) {
        if (s.type === 'doom' && out >= s.k) { r.status = s.label; r.statusBad = true; break; }
        if (s.type === 'clinch' && catch_ < s.k) { r.status = s.label; break; }
      }
    }
    const byGroup = {}; for (const r of tab) (byGroup[r.group] = byGroup[r.group] || []).push(r);
    const order = C.grouped ? Object.keys(byGroup).sort().flatMap(g => byGroup[g].sort((x, y) => x.pos - y.pos)) : [...tab].sort((x, y) => x.pos - y.pos);
    // ---- simulation
    const rem = fx.filter(f => !f.played);
    const cums = rem.map(f => { const c = new Float64Array(36); let s = 0, k = 0; for (let h = 0; h <= 5; h++) for (let a = 0; a <= 5; a++) { s += f.g[h][a]; c[k++] = s; } return c; });
    const NS = S.sims, R = rem.length;
    const outcome = new Int8Array(NS * R), gr = new Int8Array(NS * N), orank = new Int8Array(NS * N), finalPts = new Float64Array(NS * N);
    const rand = rng(20260926 + nPlayed * 7 + N);
    const pts = new Float64Array(N), gd = new Float64Array(N), gfs = new Float64Array(N);
    const groups = C.grouped ? Object.keys(byGroup) : [''];
    const members = groups.map(g => tab.filter(r => r.group === g).map(r => r.i));
    const all = [...Array(N).keys()];
    const ko = C.knockout ? makeKO(C.knockout, att, def, avgRate, homeRate, awayRate, { ko: S.koRes, done: rem.length === 0 }) : null;
    const koCount = ko ? {} : null;
    if (ko) for (const z of ko.zones) koCount[z] = new Float64Array(N);
    const cmp = (x, y) => (pts[y] - pts[x]) || (gd[y] - gd[x]) || (gfs[y] - gfs[x]) || (x - y);
    for (let s = 0; s < NS; s++) {
      for (const r of tab) { pts[r.i] = r.Pts; gd[r.i] = r.GF - r.GA; gfs[r.i] = r.GF; }
      for (let m = 0; m < R; m++) {
        const f = rem[m]; let h, a;
        if (f.live) { h = f.live.h + poisSample(rand, f.live.rh); a = f.live.a + poisSample(rand, f.live.ra); }
        else { const c = cums[m], u = rand() * c[35]; let k = 0; while (k < 35 && c[k] < u) k++; h = Math.floor(k / 6); a = k % 6; }
        gd[f.h] += h - a; gd[f.a] += a - h; gfs[f.h] += h; gfs[f.a] += a;
        if (h > a) { pts[f.h] += 3; outcome[s * R + m] = 1; } else if (h < a) { pts[f.a] += 3; outcome[s * R + m] = 3; } else { pts[f.h]++; pts[f.a]++; outcome[s * R + m] = 2; }
      }
      const groupOrders = members.map(mm => [...mm].sort(cmp));
      groupOrders.forEach(go => go.forEach((t, k) => { gr[s * N + t] = k + 1; }));
      const ov = C.satOrder === 'groupFirst' ? [...all].sort((x, y) => (gr[s * N + x] - gr[s * N + y]) || cmp(x, y)) : [...all].sort(cmp);
      ov.forEach((t, k) => { orank[s * N + t] = k + 1; finalPts[s * N + t] = pts[t]; });
      if (ko) { const res = ko.play(rand, ov, groupOrders, groups, pts, gd, gfs); for (const z of ko.zones) for (const t of res[z]) koCount[z][t]++; }
    }
    const Z = C.zones;
    const rk = (s, t, z) => z.scope === 'group' ? gr[s * N + t] : orank[s * N + t];
    for (const r of tab) {
      r.odds = {}; let sumPos = 0; const fp = [];
      for (const z of Z) r.odds[z.key] = 0;
      for (let s = 0; s < NS; s++) { sumPos += C.grouped ? gr[s * N + r.i] : orank[s * N + r.i]; fp.push(finalPts[s * N + r.i]); for (const z of Z) if (z.test(rk(s, r.i, z))) r.odds[z.key]++; }
      for (const z of Z) r.odds[z.key] /= NS;
      if (ko) for (const z of ko.zones) r.odds[z] = koCount[z][r.i] / NS;
      fp.sort((x, y) => x - y); r.projLow = fp[Math.floor(0.1 * NS)]; r.projHigh = fp[Math.floor(0.9 * NS)];
      r.avgSimPos = sumPos / NS;
      r.projPts = r.Pts + rem.reduce((s, f) => s + (f.h === r.i ? 3 * f.pH + f.pD : f.a === r.i ? 3 * f.pA + f.pD : 0), 0);
      r.projW = r.W; r.projD = r.D; r.projL = r.L; r.projGD = r.GF - r.GA;
      for (const f of rem) {
        if (f.h === r.i) { r.projW += f.pH; r.projD += f.pD; r.projL += f.pA; r.projGD += f.lh - f.la; }
        else if (f.a === r.i) { r.projW += f.pA; r.projD += f.pD; r.projL += f.pH; r.projGD += f.la - f.lh; }
      }
    }
    const pkey = r => r.projPts * 1e3 + r.projGD;
    for (const r of tab) { const peers = C.grouped ? tab.filter(o => o.group === r.group) : tab; r.projPos = 1 + peers.filter(o => pkey(o) > pkey(r)).length; }
    // ---- importance
    let maxRaw = 0; const IZ = Z.filter(z => z.w);
    rem.forEach((f, m) => {
      f.imp = {};
      for (const [side, team, win, loss] of [['h', f.h, 1, 3], ['a', f.a, 3, 1]]) {
        let nw = 0, nl = 0, nd = 0; const cw = {}, cl = {}, cd = {}; for (const z of Z) { cw[z.key] = 0; cl[z.key] = 0; cd[z.key] = 0; }
        for (let s = 0; s < NS; s++) {
          const o = outcome[s * R + m], rr = z => z.test(rk(s, team, z));
          if (o === win) { nw++; for (const z of Z) if (rr(z)) cw[z.key]++; }
          else if (o === loss) { nl++; for (const z of Z) if (rr(z)) cl[z.key]++; }
          else { nd++; for (const z of Z) if (rr(z)) cd[z.key]++; }
        }
        let raw = 0; const parts = {}, cond = {};
        for (const z of Z) {
          const pw = nw ? cw[z.key] / nw : null, pl = nl ? cl[z.key] / nl : null, pdr = nd ? cd[z.key] / nd : null;
          cond[z.key] = { pw, pl, pd: pdr };
          if (!z.w) continue;
          const d = pw != null && pl != null ? Math.abs(pw - pl) : 0; parts[z.key] = d; if (d >= S.impFloor) raw += z.w * d;
        }
        f.imp[side] = { raw, parts, cond }; maxRaw = Math.max(maxRaw, raw);
      }
    });
    const alpha = Math.min(1, nPlayed / (fx.length * S.impRamp));
    const lineScore = p => Math.max(...C.lines.map(([ln, w]) => w / (1 + Math.abs(p - ln))));
    for (const f of fx) {
      if (!f.played) { f.impH = maxRaw ? f.imp.h.raw / maxRaw : 0; f.impA = maxRaw ? f.imp.a.raw / maxRaw : 0; f.importance = Math.max(f.impH, f.impA); f.mattersTo = f.importance === 0 ? null : (f.impH >= f.impA ? f.h : f.a); }
      const lh = lineScore(tab[f.h].avgSimPos), la = lineScore(tab[f.a].avgSimPos);
      f.levH = f.played ? lh : alpha * f.impH + (1 - alpha) * lh; f.levA = f.played ? la : alpha * f.impA + (1 - alpha) * la;
    }
    const hai = T.map(t => t.base + t.bonus);
    const favDrawW = favor(fx, hai, S, results, comp, drawTarget);
    // ---- satisfaction: interim overall ranking vs HAI order
    const ovNow = C.satOrder === 'groupFirst' ? [...tab].sort((x, y) => (x.pos - y.pos) || (key(y) - key(x))) : [...tab].sort((x, y) => key(y) - key(x));
    const sat = satisfaction(ovNow.map(r => r.i), hai);
    const pe = played.reduce((s, f) => s + (f.pickPts || 0), 0);
    return { kind: 'league', fx, tab, order, rem, att, def, homeRate, awayRate, avgRate, rho, drawFactor, drawTarget, favDrawW, nPlayed, satisfaction: sat, hai, pickemPts: pe, favHits: played.filter(f => f.favorHit).length, byGroup };
  }
  function satisfaction(orderIdx, hai) {
    const N = orderIdx.length, hr = [...hai.keys()].sort((x, y) => hai[y] - hai[x]);
    const raw = orderIdx.reduce((s, t, k) => s + (N - k) * hai[t], 0);
    const worst = hr.reduce((s, t, k) => s + (k + 1) * hai[t], 0), best = hr.reduce((s, t, k) => s + (N - k) * hai[t], 0);
    return (raw - worst) / (best - worst) * 100;
  }
  function favor(fx, hai, S, results, comp, drawTarget) {
    // Affinity pick: each outcome's score = Affinity x (1 + stakes weight x stakes); the side the model rates
    // less likely to win gets a small underdog lean, which only decides close calls.
    const ul = S.underdog || 0;
    const sc = f => {
      const hh = hai[f.h], ha = hai[f.a], lh = f.levH || 0, la = f.levA || 0;
      let n = hh * (1 + S.beta * lh), p = ha * (1 + S.beta * la);
      if (f.pH != null && f.pA != null) { if (f.pH < f.pA) n *= 1 + ul; else if (f.pA < f.pH) p *= 1 + ul; }
      return { n, p, d0: Math.min(hh, ha) * (1 + S.beta * (lh + la) / 2) };
    };
    let drawW = S.drawW;
    if (S.drawAuto && drawTarget != null) {
      const pool = fx.filter(f => f.h != null && f.a != null && !f.played), base_ = pool.length ? pool : fx.filter(f => f.h != null && f.a != null);
      const ratios = base_.map(f => { const s = sc(f); return s.d0 > 0 ? Math.max(s.n, s.p) / s.d0 : Infinity; }).sort((x, y) => x - y);
      if (ratios.length) drawW = ratios[Math.min(ratios.length - 1, Math.max(0, Math.round(drawTarget * ratios.length) - 1))] * (1 + 1e-9);
    }
    for (const f of fx) {
      if (f.h == null || f.a == null) continue;
      const s = sc(f), n = s.n, o = drawW * s.d0, p = s.p;
      f.favored = n >= o ? (n >= p ? 'H' : 'A') : (o >= p ? 'D' : 'A');
      f.favorScores = { H: n, D: o, A: p };
      const rr = results[f.id], src = comp.fixtures[f.id];
      if (f.played && rr && rr.length >= 5) f.favored = rr[4];
      else if (f.played && rr === undefined && src && src.length > 8) f.favored = src[8];
      if (f.played && !f.awarded) { const res = f.hs > f.as ? 'H' : f.hs < f.as ? 'A' : 'D'; f.favorHit = res === f.favored; }
    }
    return drawW;
  }


  // ============================================================================ league playoffs (NWSL, MLS)
  function poStruct(kind) {
    const T = [];
    if (kind === 'nwslpo') {
      [[1, 8], [4, 5], [2, 7], [3, 6]].forEach(([a, b], i) => T.push({ id: 'QF' + (i + 1), round: 'Quarterfinals', kind: 'single', a: { seed: a }, b: { seed: b } }));
      T.push({ id: 'SF1', round: 'Semifinals', kind: 'single', a: { w: 'QF1' }, b: { w: 'QF2' } }, { id: 'SF2', round: 'Semifinals', kind: 'single', a: { w: 'QF3' }, b: { w: 'QF4' } });
      T.push({ id: 'F', round: 'Championship', kind: 'single', neutral: true, a: { w: 'SF1' }, b: { w: 'SF2' } });
    } else if (kind === 'uslpo') {
      for (const c of ['East', 'West']) {
        [[1, 8], [4, 5], [2, 7], [3, 6]].forEach(([a, b], i) => T.push({ id: `QF-${c}-${i + 1}`, round: 'Conference quarterfinals', conf: c, kind: 'single', a: { seed: a, conf: c }, b: { seed: b, conf: c } }));
        T.push({ id: `SF-${c}-1`, round: 'Conference semifinals', conf: c, kind: 'single', a: { w: `QF-${c}-1` }, b: { w: `QF-${c}-2` } },
               { id: `SF-${c}-2`, round: 'Conference semifinals', conf: c, kind: 'single', a: { w: `QF-${c}-3` }, b: { w: `QF-${c}-4` } },
               { id: 'CF-' + c, round: 'Conference final', conf: c, kind: 'single', a: { w: `SF-${c}-1` }, b: { w: `SF-${c}-2` } });
      }
      T.push({ id: 'CUP', round: 'USL Championship Final', kind: 'single', byPts: true, a: { w: 'CF-East' }, b: { w: 'CF-West' } });
    } else {
      for (const c of ['East', 'West']) {
        T.push({ id: 'WC-' + c, round: 'Wild card', conf: c, kind: 'pens', a: { seed: 8, conf: c }, b: { seed: 9, conf: c } });
        [[{ seed: 1, conf: c }, { w: 'WC-' + c }], [{ seed: 4, conf: c }, { seed: 5, conf: c }], [{ seed: 2, conf: c }, { seed: 7, conf: c }], [{ seed: 3, conf: c }, { seed: 6, conf: c }]]
          .forEach(([a, b], i) => T.push({ id: `R1-${c}-${i + 1}`, round: 'Round One', conf: c, kind: 'bo3', a, b }));
        T.push({ id: `SF-${c}-1`, round: 'Conference semifinals', conf: c, kind: 'single', a: { w: `R1-${c}-1` }, b: { w: `R1-${c}-2` } },
               { id: `SF-${c}-2`, round: 'Conference semifinals', conf: c, kind: 'single', a: { w: `R1-${c}-3` }, b: { w: `R1-${c}-4` } },
               { id: 'CF-' + c, round: 'Conference final', conf: c, kind: 'single', a: { w: `SF-${c}-1` }, b: { w: `SF-${c}-2` } });
      }
      T.push({ id: 'CUP', round: 'MLS Cup', kind: 'single', byPts: true, a: { w: 'CF-East' }, b: { w: 'CF-West' } });
    }
    return T;
  }
  // seedOf(slot) -> team index; seedNum[team] -> seed number (lower = better); pts[team] for MLS Cup hosting.
  // decide(tie, host, visitor) -> winner or null. Returns ties with host/visitor/winner filled where known.
  function poResolve(kind, seedOf, seedNum, pts, decide) {
    const W = {}, out = [];
    for (const t of poStruct(kind)) {
      const side = s => s.seed ? seedOf(s) : (W[s.w] ?? null);
      let a = side(t.a), b = side(t.b), h = a, v = b;
      if (a != null && b != null) {
        const aHost = t.byPts ? (pts[a] >= pts[b]) : (seedNum[a] <= seedNum[b]);
        h = aHost ? a : b; v = aHost ? b : a;
      }
      const win = h != null && v != null ? decide(t, h, v) : null;
      if (win != null) W[t.id] = win;
      out.push(Object.assign({}, t, { h, v, winner: win }));
    }
    return out;
  }
  function poProbs(att, def, homeRate, awayRate) {
    const avg = (homeRate + awayRate) / 2;
    const game = (h, v, neutral) => { const a = neutral ? avg : homeRate, b = neutral ? avg : awayRate; return [a * att[h] * def[v], b * att[v] * def[h]]; };
    const pens = (h, v) => { const [lh, lv] = game(h, v); const [w, d] = winDraw(lh, lv); return w + 0.5 * d; };
    const single = (h, v, neutral) => { const [lh, lv] = game(h, v, neutral); return advance(lh, lv, lh / 3, lv / 3, true, 0.5); };
    return { game, pens, single };
  }
  // result of one real match: {hs, as, adv:'H'|'A'} -> 1 if host side won
  const realWin = r => r.hs > r.as ? 1 : r.hs < r.as ? 0 : (r.adv === 'H' ? 1 : r.adv === 'A' ? 0 : null);

  // ---------------------------------------------------------------------------- knockouts (UCL, UNL)
  function makeKO(kind, att, def, avg, home, away, extra) {
    extra = extra || {};
    const N = att.length, cache2 = new Map(), cacheN = new Map();
    const two = (i, j) => { const k = i * N + j; if (!cache2.has(k)) cache2.set(k, advance((home + away) * att[i] * def[j], (home + away) * att[j] * def[i], avg * att[i] * def[j] / 3, avg * att[j] * def[i] / 3, true, 0.5)); return cache2.get(k); };
    const one = (i, j) => { const k = i * N + j; if (!cacheN.has(k)) cacheN.set(k, advance(avg * att[i] * def[j], avg * att[j] * def[i], avg * att[i] * def[j] / 3, avg * att[j] * def[i] / 3, true, 0.5)); return cacheN.get(k); };
    const tie = (rand, i, j, fn) => rand() < fn(i, j) ? i : j;
    if (kind === 'ucl') return {
      zones: ['r16', 'qf', 'sf', 'final', 'win'],
      play(rand, ov) {
        const at = p => ov[p - 1], coin = () => rand() < 0.5;
        const po = [[9, 10, 23, 24], [11, 12, 21, 22], [13, 14, 19, 20], [15, 16, 17, 18]].map(([a, b, c, d]) => {
          const [x, y] = coin() ? [c, d] : [d, c];
          return [tie(rand, at(a), at(x), two), tie(rand, at(b), at(y), two)];
        });
        const seeds = [[1, 2, 3], [3, 4, 2], [5, 6, 1], [7, 8, 0]];
        const r16 = [];
        for (const [a, b, pi] of seeds) { const w = coin() ? po[pi] : [po[pi][1], po[pi][0]]; r16.push([at(a), w[0]], [at(b), w[1]]); }
        const w16 = r16.map(([x, y]) => tie(rand, x, y, two));
        const qf = [[w16[0], w16[7]], [w16[3], w16[4]], [w16[1], w16[6]], [w16[2], w16[5]]].map(([x, y]) => tie(rand, x, y, two));
        const sf = [tie(rand, qf[0], qf[1], two), tie(rand, qf[2], qf[3], two)];
        const champ = tie(rand, sf[0], sf[1], one);
        return { r16: [...ov.slice(0, 8), ...po.flat()], qf: w16, sf: qf, final: sf, win: [champ] };
      } };
    if (kind === 'nwslpo' || kind === 'mlspo' || kind === 'uslpo') {
      const P = poProbs(att, def, home, away), koRes = extra.ko || {};
      return {
        zones: kind === 'nwslpo' ? ['sf', 'final', 'champ'] : ['csf', 'cf', 'final', 'champ'],
        play(rand, ov, go, groups, pts) {
          const seedNum = {}; let seedOf;
          if (kind === 'nwslpo') { ov.forEach((t, i) => { seedNum[t] = i + 1; }); seedOf = s => ov[s.seed - 1]; }
          else { const byC = {}; groups.forEach((g, i) => { byC[g] = go[i]; go[i].forEach((t, j) => { seedNum[t] = j + 1; }); }); seedOf = s => byC[s.conf][s.seed - 1]; }
          const useReal = !!extra.done;
          const decide = (t, h, v) => {
            if (t.kind === 'bo3') {
              let wh = 0, wv = 0;
              for (let g = 1; g <= 3 && wh < 2 && wv < 2; g++) {
                const r = useReal ? koRes[`${t.id}-G${g}`] : null, hostIsH = g !== 2;
                let hw = r ? realWin(r) : null;
                if (hw == null) { const p = hostIsH ? P.pens(h, v) : 1 - P.pens(v, h); hw = rand() < p ? 1 : 0; }
                else if (!hostIsH) hw = 1 - hw;
                if (hw) wh++; else wv++;
              }
              return wh >= 2 ? h : v;
            }
            const r = useReal ? koRes[t.id] : null; let hw = r ? realWin(r) : null;
            if (hw == null) hw = rand() < (t.kind === 'pens' ? P.pens(h, v) : P.single(h, v, t.neutral)) ? 1 : 0;
            return hw ? h : v;
          };
          const ties = poResolve(kind, seedOf, seedNum, pts, decide), out = {};
          for (const z of this.zones) out[z] = [];
          for (const t of ties) {
            if (kind === 'nwslpo') { if (t.round === 'Quarterfinals') out.sf.push(t.winner); if (t.round === 'Semifinals') out.final.push(t.winner); if (t.id === 'F') out.champ.push(t.winner); }
            else { if (t.round === 'Round One' || t.round === 'Conference quarterfinals') out.csf.push(t.winner); if (t.round === 'Conference semifinals') out.cf.push(t.winner); if (t.round === 'Conference final') out.final.push(t.winner); if (t.id === 'CUP') out.champ.push(t.winner); }
          }
          return out;
        } };
    }
    if (kind === 'unl2') {
      const der = []; const perm = (a, k) => { if (k === 4) { if (a.every((v, i) => v !== i)) der.push([...a]); return; } for (let i = k; i < 4; i++) { [a[k], a[i]] = [a[i], a[k]]; perm(a, k + 1); [a[k], a[i]] = [a[i], a[k]]; } };
      perm([0, 1, 2, 3], 0);
      const shuffle = (rand, arr) => { const a = [...arr]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
      return {
        zones: ['finals', 'final', 'win', 'up', 'down', 'po'],
        play(rand, ov, go, groups, pts, gd, gfs) {
          const L = x => groups.map((g, i) => [g, go[i]]).filter(([g]) => g[0] === x).sort((p, q) => p[0] < q[0] ? -1 : 1).map(([, o]) => o);
          const A = L('A'), B = L('B'), C = L('C'), Dd = L('D');
          const rankAcross = ts => [...ts].sort((x, y) => (pts[y] - pts[x]) || (gd[y] - gd[x]) || (gfs[y] - gfs[x]) || (rand() - 0.5));
          const out = { finals: [], final: [], win: [], up: [], down: [], po: [] };
          // League A knockouts
          const d = der[Math.floor(rand() * der.length)];
          const qf = A.map((g, i) => tie(rand, g[0], A[d[i]][1], two));
          out.finals = qf;
          const p = Math.floor(rand() * 3), pairs = [[[0, 1], [2, 3]], [[0, 2], [1, 3]], [[0, 3], [1, 2]]][p];
          const sf = pairs.map(([x, y]) => tie(rand, qf[x], qf[y], one)); out.final = sf; out.win = [tie(rand, sf[0], sf[1], one)];
          // A relegation and A/B play-offs
          const thirds = rankAcross(A.map(g => g[2])), fourths = rankAcross(A.map(g => g[3]));
          out.down.push(fourths[2], fourths[3]);
          const aPO = shuffle(rand, [thirds[2], thirds[3], fourths[0], fourths[1]]), bRun = shuffle(rand, B.map(g => g[1]));
          out.po.push(...aPO, ...bRun);
          aPO.forEach((a, i) => { const w = tie(rand, bRun[i], a, two); if (w === bRun[i]) { out.up.push(bRun[i]); out.down.push(a); } });
          out.up.push(...B.map(g => g[0]));
          // B/C play-offs
          const bLast = shuffle(rand, B.map(g => g[3])), cRun = shuffle(rand, C.map(g => g[1]));
          out.po.push(...bLast, ...cRun);
          bLast.forEach((b, i) => { const w = tie(rand, cRun[i], b, two); if (w === cRun[i]) { out.up.push(cRun[i]); out.down.push(b); } });
          out.up.push(...C.map(g => g[0]));
          for (const g of Dd) out.up.push(...g);
          return out;
        } };
    }
    if (kind === 'unl') {
      const der = []; const perm = (a, k) => { if (k === 4) { if (a.every((v, i) => v !== i)) der.push([...a]); return; } for (let i = k; i < 4; i++) { [a[k], a[i]] = [a[i], a[k]]; perm(a, k + 1); [a[k], a[i]] = [a[i], a[k]]; } };
      perm([0, 1, 2, 3], 0);
      return {
        zones: ['finals', 'final', 'win'],
        play(rand, ov, go) {
          const W = go.map(g => g[0]), Rn = go.map(g => g[1]), d = der[Math.floor(rand() * der.length)];
          const qf = W.map((w, i) => tie(rand, w, Rn[d[i]], two));
          const p = Math.floor(rand() * 3), pairs = [[[0, 1], [2, 3]], [[0, 2], [1, 3]], [[0, 3], [1, 2]]][p];
          const sf = pairs.map(([x, y]) => tie(rand, qf[x], qf[y], one));
          return { finals: qf, final: sf, win: [tie(rand, sf[0], sf[1], one)] };
        } };
    }
    return null;
  }

  // ============================================================================ cup (Carabao)
  function runCup(comp, results, draws, S) {
    const T = comp.teams, P = comp.params, N = T.length;
    const hai = T.map(t => t.base + t.bonus);
    const fx = comp.fixtures.map((f, id) => {
      const r = results[id], d = draws[id];
      const h = d ? d[0] : f[3], a = d ? d[1] : f[4];
      const hs = r !== undefined ? (r ? r[0] : null) : f[5], as = r !== undefined ? (r ? r[1] : null) : f[6];
      const pens = r !== undefined ? (r ? r[2] : null) : f[7];
      const played = Number.isInteger(hs) && Number.isInteger(as);
      return { id, round: f[0], tie: f[1], mw: f[0], date: f[2], h, a, hs: played ? hs : null, as: played ? as : null, pens, played, t: Date.parse(f[2]) / 864e5 };
    });
    const rated = i => i != null && T[i].att != null;
    const neutral = f => f.round === 'Final';
    const byRound = r => fx.filter(f => f.round === r);
    // leg pairing for semi-finals
    const legs = {}; for (const f of fx) if (f.round.startsWith('Semi-final')) (legs[f.tie] = legs[f.tie] || {})[f.round.endsWith('1') ? 1 : 2] = f;
    for (const s in legs) { const l1 = legs[s][1], l2 = legs[s][2]; if (l1 && l2) { if (l1.h != null) { l2.h = l1.a; l2.a = l1.h; } } }
    const lam = (i, j, venue) => (venue === 'neutral' ? (P.homeRate + P.awayRate) / 2 : venue === 'home' ? P.homeRate : P.awayRate) * T[i].att * T[j].dfn;
    for (const f of fx) {
      f.winner = null;
      if (f.round === 'Final' && f.h == null && legs[1] && legs[2] && legs[1][2] && legs[2][2] && legs[1][2].winner != null && legs[2][2].winner != null) { f.h = legs[1][2].winner; f.a = legs[2][2].winner; }
      if (f.played && !f.round.endsWith('leg 1')) {
        if (f.round === 'Semi-final leg 2') { const l1 = legs[f.tie][1]; if (l1 && l1.played) { const aggH = f.hs + l1.as, aggA = f.as + l1.hs; f.winner = aggH > aggA ? f.h : aggH < aggA ? f.a : f.pens; } }
        else f.winner = f.hs > f.as ? f.h : f.hs < f.as ? f.a : f.pens;
      }
      if (rated(f.h) && rated(f.a)) {
        const v = neutral(f) ? 'neutral' : 'home';
        f.lh = lam(f.h, f.a, v); f.la = lam(f.a, f.h, v === 'home' ? 'away' : 'neutral');
        const r = grid(f.lh, f.la, 0); f.g = r.g; f.pH = r.H; f.pD = r.D; f.pA = r.A;
        picks(f, S);
        const o = Math.abs(f.pH - f.pA) < 0.10 ? 0 : Math.sign(f.pH - f.pA); let best = null, bp = -1;
        for (let h = 0; h <= 4; h++) for (let a = 0; a <= 4; a++) if (Math.sign(h - a) === o && f.g[h][a] > bp) { bp = f.g[h][a]; best = [h, a]; }
        f.pred = best;
        const rr = results[f.id]; if (f.played && rr && rr.length >= 5) f.pick = [rr[3], rr[4]];
        if (f.played) scorePick(f, S);
      }
    }
    // tie advance probabilities
    const ADV1 = (i, j) => { const [w, d] = winDraw(lam(i, j, 'home'), lam(j, i, 'away')); return w + P.pen * d; };
    const ADV2 = (i, j) => { const [w, d] = winDraw(lam(i, j, 'home') + lam(i, j, 'away'), lam(j, i, 'home') + lam(j, i, 'away')); return w + P.pen * d; };
    const ADVF = (i, j) => advance(lam(i, j, 'neutral'), lam(j, i, 'neutral'), lam(i, j, 'neutral') / 3, lam(j, i, 'neutral') / 3, true, P.pen);
    for (const f of fx) {
      if (!(rated(f.h) && rated(f.a)) || f.winner != null) continue;
      if (f.round === 'Final') f.advH = ADVF(f.h, f.a);
      else if (f.round === 'Semi-final leg 2') {
        const l1 = legs[f.tie][1];
        if (l1 && l1.played) { const m = l1.hs - l1.as; let p = 0, dd = 0; const ph = poisVec(f.lh), pa = poisVec(f.la); for (let x = 0; x <= KMAX; x++) for (let y = 0; y <= KMAX; y++) { const pr = ph[x] * pa[y]; if (x - y > m) p += pr; else if (x - y === m) dd += pr; } f.advH = p + P.pen * dd; }
        else f.advH = ADV2(f.h, f.a);
      } else if (f.round === 'Semi-final leg 1') f.advH = 1 - ADV2(f.a, f.h);
      else f.advH = ADV1(f.h, f.a);
    }
    // alive clubs
    const lost = new Set(); for (const f of fx) if (f.winner != null && !f.round.endsWith('leg 1')) lost.add(f.winner === f.h ? f.a : f.h);
    const alive = T.map((t, i) => i).filter(i => rated(i) && !lost.has(i));
    // simulation
    const NS = S.sims, rand = rng(4242 + fx.filter(f => f.played).length);
    const cnt = { qf: new Float64Array(N), sf: new Float64Array(N), final: new Float64Array(N), win: new Float64Array(N) };
    const roundTies = r => byRound(r);
    const r4 = roundTies('Fourth round'), qfT = roundTies('Quarter-final'), sf2 = roundTies('Semi-final leg 2'), fin = roundTies('Final')[0];
    const qfKnown = qfT.every(f => f.h != null && f.a != null), sfKnown = sf2.every(f => f.h != null && f.a != null);
    const winIn = new Map(); r4.concat(qfT, sf2, [fin]).forEach(f => winIn.set(f.id, []));
    const shuffle = arr => { const a = [...arr]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
    const decide = (f, x, y, fn) => { if (f && f.winner != null) return f.winner; if (f && f.h === x && f.a === y && f.advH != null) return rand() < f.advH ? x : y; return rand() < fn(x, y) ? x : y; };
    const tieWins = {}; for (const f of r4.concat(qfT, sf2, [fin])) tieWins[f.id] = { h: 0, hw: 0, a: 0, aw: 0 };
    for (let s = 0; s < NS; s++) {
      const w4 = r4.map(f => decide(f, f.h, f.a, ADV1));
      w4.forEach(t => cnt.qf[t]++);
      const pairUp = (ties, winners) => {
        const fixed = ties.map(f => (f.h != null && f.a != null) ? [f.h, f.a] : null);
        const used = new Set(fixed.filter(Boolean).flat()); const rest = shuffle(winners.filter(t => !used.has(t))); let j = 0;
        return fixed.map(p => p || [rest[j++], rest[j++]]);
      };
      const qp = pairUp(qfT, w4);
      const wq = qp.map(([x, y], k) => decide(qfT[k].h === x && qfT[k].a === y ? qfT[k] : null, x, y, ADV1));
      wq.forEach(t => cnt.sf[t]++);
      const sfTies = sf2.map(f => ({ h: f.h, a: f.a }));
      const sp = pairUp(sfTies, wq);
      const ws = sp.map(([x, y], k) => decide(sf2[k].h === x && sf2[k].a === y ? sf2[k] : null, x, y, ADV2));
      ws.forEach(t => cnt.final[t]++);
      const champ = decide(fin && fin.h === ws[0] && fin.a === ws[1] ? fin : null, ws[0], ws[1], ADVF);
      cnt.win[champ]++;
      // importance bookkeeping: P(cup | team wins its current tie)
      r4.forEach((f, k) => { if (f.winner != null) return; const tw = tieWins[f.id]; if (w4[k] === f.h) { tw.h++; if (champ === f.h) tw.hw++; } else { tw.a++; if (champ === f.a) tw.aw++; } });
      qfT.forEach((f, k) => { if (f.winner != null || f.h == null || f.a == null) return; const tw = tieWins[f.id]; if (wq[k] === f.h) { tw.h++; if (champ === f.h) tw.hw++; } else { tw.a++; if (champ === f.a) tw.aw++; } });
      sf2.forEach((f, k) => { if (f.winner != null || f.h == null || f.a == null) return; const tw = tieWins[f.id]; if (ws[k] === f.h) { tw.h++; if (champ === f.h) tw.hw++; } else { tw.a++; if (champ === f.a) tw.aw++; } });
      if (fin && fin.h === ws[0] && fin.a === ws[1] && fin.winner == null) { const tw = tieWins[fin.id]; if (champ === fin.h) { tw.h++; tw.hw++; } else { tw.a++; tw.aw++; } }
    }
    let maxRaw = 0;
    for (const f of fx) {
      const tw = tieWins[f.id]; if (!tw || f.winner != null || f.h == null || f.a == null || f.pH == null) continue;
      f.rawH = tw.h ? tw.hw / tw.h : 0; f.rawA = tw.a ? tw.aw / tw.a : 0; maxRaw = Math.max(maxRaw, f.rawH, f.rawA);
    }
    for (const f of fx) if (f.rawH !== undefined) {
      f.impH = maxRaw ? f.rawH / maxRaw : 0; f.impA = maxRaw ? f.rawA / maxRaw : 0; f.importance = Math.max(f.impH, f.impA); f.mattersTo = f.impH >= f.impA ? f.h : f.a;
      const l1 = f.round === 'Semi-final leg 2' ? legs[f.tie][1] : null; if (l1 && !l1.played) { l1.importance = f.importance; l1.mattersTo = f.mattersTo; }
    }
    // favored pick: higher HAI
    for (const f of fx) {
      if (f.h == null || f.a == null) continue;
      const ul = S.underdog || 0, dogH = f.advH != null ? f.advH < 0.5 : null;
      const sh = hai[f.h] * (dogH === true ? 1 + ul : 1), sa = hai[f.a] * (dogH === false ? 1 + ul : 1);
      f.favored = sh >= sa ? 'H' : 'A';
      const rr = results[f.id]; if (f.played && rr && rr.length >= 6) f.favored = rr[5];
      if (f.winner != null) f.favorHit = (f.favored === 'H' ? f.h : f.a) === f.winner;
    }
    const odds = T.map((t, i) => ({ i, qf: cnt.qf[i] / NS, sf: cnt.sf[i] / NS, final: cnt.final[i] / NS, win: cnt.win[i] / NS }));
    const stage = i => 1 + odds[i].qf + odds[i].sf + odds[i].final + odds[i].win;
    const al = alive.length ? alive : [];
    const stages = [5, 4, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1];
    const hs_ = al.map(i => hai[i]).sort((x, y) => y - x);
    const raw = al.reduce((s, i) => s + stage(i) * hai[i], 0);
    const best = stages.reduce((s, v, k) => s + v * (hs_[k] || 0), 0), worst = stages.reduce((s, v, k) => s + v * (hs_[hs_.length - 1 - k] || 0), 0);
    const sat = best > worst ? (raw - worst) / (best - worst) * 100 : 50;
    const scored = fx.filter(f => f.played && f.pickPts !== undefined);
    return { kind: 'cup', fx, odds, alive, lost, satisfaction: sat, hai, pickemPts: scored.reduce((s, f) => s + f.pickPts, 0), nPlayed: fx.filter(f => f.played).length,
             favHits: fx.filter(f => f.favorHit).length, favTotal: fx.filter(f => f.favorHit !== undefined).length, legs };
  }
  return { run, runCup, grid, poResolve, poProbs, poStruct, realWin };
})();
if (typeof module !== 'undefined') module.exports = MODEL;
