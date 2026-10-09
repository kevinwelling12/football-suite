"""Fit the Affinity parameters (params.json) to Kevin's answers and backtest them (rebuild, 2026-10-09).

  python3 scripts/affinity/fit.py            # fit on everything, backtest leave-one-round-out, print the report
  python3 scripts/affinity/fit.py --write    # also save the fitted params.json

Evidence (scripts/affinity/evidence): every round that has a clean label for the score itself.
- Clubs: 26 gut ratings of described clubs (rounds 4-5), as pairwise orderings weighted by the gap in his rating;
  28 choices between anonymous club profiles (rounds 4-5).
- Players: 50 choices between anonymous player profiles (rounds 8-9); 15 controlled named pairs (round 10).
Checks only (confounded, see evidence/summary.md): round 6 named club pairs (familiarity), round 8 named player pairs
(name recognition), round 7 player gut ratings, Timbers above Sounders.

One likelihood for everything: P(a over b) = sigmoid(beta x (A_a - A_b)), A from affinity.py's own functions, so the
fit sees exactly the model that runs. Club and player weights are pulled toward Kevin's stated weights (the prior),
hard-line and connection scales toward 1 (as researched), the team performance share toward its current value.
Player performance share stays 0.4: Kevin's decision (2026-10-07), reported but not refitted.
"""
import json, math, pathlib, sys, copy
import numpy as np
from scipy.optimize import minimize
root = pathlib.Path(__file__).resolve().parents[2]
A = root / 'scripts' / 'affinity'
sys.path.insert(0, str(A)); sys.path.insert(0, str(A / 'evidence'))
import affinity as M
import load as E

P0 = json.loads((A / 'params.json').read_text())
ev = E.load()
R, PL = M.run(P0, write=False)

# ---------------------------------------------------------------- evidence -> model inputs
LV = dict(C=[3, 6, 9.5], V=[3, 6, 9.5], H=[1.5, 5.5, 10], O=[2, 6, 10], T=[3, 5.5, 9])
TRL = [1.5, 5.0, 8.0]          # relegation fight / mid-table / near the top (track record 0-10)
LOCL = [0, 0, 3.4]             # another continent / across the country / two hours away (distance points)
def club_profile(side, rnd):
    a = side['attrs']
    f = {k: LV[k][a[k]] if k in a else 5.5 for k in LV}
    hard = []
    if a.get('BAG') == 1: hard.append(('betting', 'Sportsbook sponsor', 3.0))
    if a.get('BAG') == 2: hard.append(('violence', 'Ultras violence', 12.0))
    if a.get('BAGT') == 1: hard.append(('violence', 'Violence 8 years ago', 6.0))   # older than 5 years counts half
    if a.get('BAGT') == 2: hard.append(('violence', 'Violence last season', 12.0))
    P = TRL[a['TR']] + (0.2 if a.get('TROPHY') == 2 else 0.0)
    conn = [('Distance', LOCL[a['LOC']])] if 'LOC' in a else []
    return dict(f=f, hard=hard, P=P, conn=conn, roots=0)

def club_named(n):
    r = R[n]; return dict(f=r['f'], hard=r['hard'], P=r['P']['P'] if r['P'] else None, conn=r['conn'], roots=r['roots'][1] if r['roots'] else 0)

def player_profile(side):
    v = side['values']
    f = {k: v[k] for k in ('CH', 'WK', 'LO', 'AB', 'LE', 'ST')}
    hard = [('pe', 'Baggage', abs(v.get('PE', 0.0)) * 2.94)] if v.get('PE') else []
    return dict(f=f, hard=hard, conn=[('Connection', v.get('CO', 0.0))] if v.get('CO') else [])

def player_named(n):
    pl = PL[n]; return dict(f=pl['factors'], hard=pl['hard'], conn=pl['conn'])

def club_A(x, p): return M.club_score(x['f'], x['hard'], x['P'], x['conn'], x['roots'], p)[0]
def player_A(x, p): return M.player_score(x['f'], x['hard'], x['conn'], p)[0]

items = []   # (round, set, a, b, y, weight, scorer)
gut = [(n, v, r['round']) for n, v, r in E.gut_clubs(ev) if n in R]
for rnd in ('q4', 'q5'):
    g = [(n, v) for n, v, rr in gut if rr == rnd]
    pairs = [(a, b, 1.0 if va > vb else 0.0, abs(va - vb)) for i, (a, va) in enumerate(g) for b, vb in g[i + 1:] if va != vb]
    tot = sum(w for *_, w in pairs)
    for a, b, y, w in pairs: items.append((rnd, 'club_gut', club_named(a), club_named(b), y, w * len(g) / tot, 'club', (a, b)))
for a, b, y, r in E.pairs(ev, domain='club', kinds=['club_profile']):
    items.append((r['round'], 'club_dce', club_profile(a, r['round']), club_profile(b, r['round']), y, 1.0, 'club', r['id']))
for a, b, y, r in E.pairs(ev, domain='player', kinds=['player_profile']):
    items.append((r['round'], 'player_profile', player_profile(a), player_profile(b), y, 1.0, 'player', r['id']))
for a, b, y, r in E.pairs(ev, domain='player', named=True):
    if r['round'] == 'q10' and a in PL and b in PL:
        items.append(('q10', 'player_q10', player_named(a), player_named(b), y, 1.0, 'player', (a, b)))
checks = dict(
    q6=[(a, b, y) for a, b, y, r in E.pairs(ev, domain='club', named=True) if r['round'] == 'q6' and a in R and b in R],
    q8=[(a, b, y) for a, b, y, r in E.pairs(ev, domain='player', named=True) if r['round'] == 'q8' and a in PL and b in PL],
    q7=[(n, v) for n, v, r in E.gut_players(ev) if n in PL])

# ---------------------------------------------------------------- parameters
SETS = ['club_gut', 'club_dce', 'player_profile', 'player_q10']
def unpack(t, base=P0):
    p = copy.deepcopy(base); i = 0
    for k in M.CLUB_F: p['club_w'][k] = math.exp(t[i]); i += 1
    for k in M.ROLE_F: p['player_w'][k] = math.exp(t[i]); i += 1
    for k in M.PERF_F: p['perf_w'][k] = math.exp(t[i]); i += 1
    p['club_pi'] = 0.3 / (1 + math.exp(-t[i])); i += 1
    p['hard'] = math.exp(t[i]); i += 1
    p['conn'] = math.exp(t[i]); i += 1
    beta = {s: math.exp(t[i + j]) for j, s in enumerate(SETS)}
    return p, beta
def pack(p):
    t = [math.log(p['club_w'][k]) for k in M.CLUB_F] + [math.log(p['player_w'][k]) for k in M.ROLE_F] + [math.log(p['perf_w'][k]) for k in M.PERF_F]
    t += [math.log(p['club_pi'] / (0.3 - p['club_pi'])), math.log(p['hard']), math.log(p['conn'])] + [math.log(0.15)] * len(SETS)
    return np.array(t)
T0 = pack(P0)
NW = 11  # weights in t
def normw(t):  # weights are scale-free within each group: centre them so the prior compares shapes
    t = t.copy()
    for a, b in ((0, 5), (5, 8), (8, 11)): t[a:b] -= t[a:b].mean()
    return t
LAM = dict(w=100.0, pi=4.0, hard=3.0, conn=3.0, beta=2.0)  # chosen by the leave-one-round-out sweep: Kevin's stated weights generalise best
def loss(t, its):
    p, beta = unpack(t); L = 0.0
    for rnd, s, a, b, y, w, kind, _ in its:
        f = club_A if kind == 'club' else player_A
        z = beta[s] * (f(a, p) - f(b, p))
        L += w * (y * np.logaddexp(0, -z) + (1 - y) * np.logaddexp(0, z))
    d = normw(t) - normw(T0)
    L += LAM['w'] * float((d[:NW] ** 2).sum()) + LAM['pi'] * (t[NW] - T0[NW]) ** 2 + LAM['hard'] * (t[NW + 1] - T0[NW + 1]) ** 2 + LAM['conn'] * (t[NW + 2] - T0[NW + 2]) ** 2
    L += LAM['beta'] * float(((t[NW + 3:] - T0[NW + 3:]) ** 2).sum())  # choice sharpness stays near 0.15 per point
    return L
def fit(its):
    r = minimize(loss, T0, args=(its,), method='L-BFGS-B', options=dict(maxiter=400))
    return r.x

# ---------------------------------------------------------------- scoring held-out items
def evaluate(p, its):
    out = {}
    for s in SETS:
        xs = [(a, b, y, w, kind) for _, ss, a, b, y, w, kind, _ in its if ss == s and y != 0.5]
        if not xs: continue
        f = lambda x, kind: club_A(x, p) if kind == 'club' else player_A(x, p)
        hit = sum(w * ((f(a, k) > f(b, k)) == (y > .5)) for a, b, y, w, k in xs); tot = sum(w for *_, w, _ in xs)
        out[s] = (hit, tot)
    return out
def fmt(e): return ', '.join(f"{s} {h:.1f}/{t:.1f} ({h / t:.0%})" for s, (h, t) in e.items())

def check_report(p):
    Rp = {n: M.club_score(r['f'], r['hard'], r['P']['P'] if r['P'] else None, r['conn'], r['roots'][1] if r['roots'] else 0, p)[0] for n, r in R.items()}
    Pp = {n: M.player_score(pl['factors'], pl['hard'], pl['conn'], p)[0] for n, pl in PL.items()}
    q6 = sum((Rp[a] > Rp[b]) == (y > .5) for a, b, y in checks['q6'] if y != .5)
    q8 = sum((Pp[a] > Pp[b]) == (y > .5) for a, b, y in checks['q8'] if y != .5)
    g = [(Rp[n], v) for n, v, _ in gut]; q7 = [(Pp[n], v) for n, v in checks['q7']]
    return dict(gut_r=round(float(np.corrcoef(*zip(*g))[0, 1]), 3), q7_r=round(float(np.corrcoef(*zip(*q7))[0, 1]), 3),
                q6=f"{q6}/{sum(1 for *_, y in checks['q6'] if y != .5)}", q8=f"{q8}/{sum(1 for *_, y in checks['q8'] if y != .5)}",
                timbers=round(Rp['Portland Timbers'] - Rp['Seattle Sounders FC'], 1))

if __name__ == '__main__':
    print(f'{len(items)} fitting items:', {s: sum(1 for it in items if it[1] == s) for s in SETS})
    rounds = sorted({it[0] for it in items})
    print('\nleave-one-round-out backtest (held-out round predicted by a fit on the others):')
    tot_new = {}; tot_old = {}
    for rnd in rounds:
        tr = [it for it in items if it[0] != rnd]; te = [it for it in items if it[0] == rnd]
        p, _ = unpack(fit(tr)); en, eo = evaluate(p, te), evaluate(P0, te)
        print(f'  {rnd}: rebuilt {fmt(en)} | current params {fmt(eo)}')
        for s, (h, t) in en.items(): tot_new[s] = [a + b for a, b in zip(tot_new.get(s, [0, 0]), (h, t))]
        for s, (h, t) in eo.items(): tot_old[s] = [a + b for a, b in zip(tot_old.get(s, [0, 0]), (h, t))]
    print('  total rebuilt:', fmt(tot_new)); print('  total current:', fmt(tot_old))
    t = fit(items); p, beta = unpack(t)
    print('\nfit on everything:')
    print('  club weights', {k: round(v / sum(p['club_w'].values()) * 100, 1) for k, v in p['club_w'].items()}, 'performance share', round(p['club_pi'], 3))
    print('  player role', {k: round(v / sum(p['player_w'].values()) * 100, 1) for k, v in p['player_w'].items()},
          'performance', {k: round(v / sum(p['perf_w'].values()) * 100, 1) for k, v in p['perf_w'].items()})
    print('  hard-line scale', round(p['hard'], 2), 'connection scale', round(p['conn'], 2))
    print('  in-sample', fmt(evaluate(p, items)))
    print('  checks rebuilt', check_report(p)); print('  checks current', check_report(P0))
    if '--write' in sys.argv:
        out = copy.deepcopy(p)
        for g in ('club_w', 'player_w', 'perf_w'):
            s = sum(out[g].values()); out[g] = {k: round(v / s * 100, 1) for k, v in out[g].items()}
        for k in ('club_pi', 'hard', 'conn'): out[k] = round(out[k], 3)
        out['fit'] = dict(date='2026-10-09', items=len(items), checks=check_report(p))
        (A / 'params.json').write_text(json.dumps(out, indent=1))
        print('wrote params.json')
