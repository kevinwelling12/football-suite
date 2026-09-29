"""Score The Blind Draw (quiz round 4) against the hidden key.  python3 analyze.py answers.json"""
import json, math, sys, statistics as stt
K = json.load(open('key.json')); A = json.load(open(sys.argv[1]))
ans, times = A['answers'], A.get('times', {})
out = {}
# 1. Everyday constructs: sum of loadings of the picked option, scaled by the max reachable per construct.
tot, reach = {}, {}
for qid, keys in K['everyday'].items():
    cons = {c for kk in keys for c in kk}
    for c in cons:
        vals = [kk.get(c, 0) for kk in keys]; reach[c] = reach.get(c, 0) + max(abs(min(vals)), abs(max(vals)))
    if qid in ans and isinstance(ans[qid], int):
        for c, v in keys[ans[qid]].items(): tot[c] = tot.get(c, 0) + v
out['constructs'] = {c: round(tot.get(c, 0) / reach[c], 2) for c in sorted(reach)}   # -1..1
out['attention'] = ans.get('k4') == 1
# consistency: reversed items vs their partners
def pick(q): return K['everyday'][q][ans[q]] if q in ans else {}
cons = {}
for kq, c, partners in (('k1', 'FORGIVE', ['e05', 'e28']), ('k2', 'ASSOC', ['e12', 'e13']), ('k3', 'O', ['e14', 'e21'])):
    if kq in ans:
        a = pick(kq).get(c, 0); b = stt.mean([pick(p).get(c, 0) for p in partners if p in ans] or [0])
        cons[c] = 'consistent' if a * b > 0 or abs(a - b) < 1 else 'inconsistent'
out['consistency'] = cons
# 2. Forced choice: wins per factor (Bradley-Terry-lite)
wins, apps = {}, {}
for qid, (fa, fb) in K['pairs'].items():
    for f in (fa, fb): apps[f] = apps.get(f, 0) + 1
    if qid in ans: w = fa if ans[qid] == 'a' else fb; wins[w] = wins.get(w, 0) + 1
out['pairs'] = {f: f'{wins.get(f, 0)}/{apps[f]}' for f in apps}
# 3. DCE: conditional logit, ridge, Newton
attrs = K['attrs']; X, y = [], []
def feat(lv): return [lv[i] for i in range(7)] + [1 if lv[7] == 1 else 0, 1 if lv[7] == 2 else 0]
names = attrs[:7] + ['BET', 'VIOL']
for d in K['dce']:
    if d['id'] in ans:
        fa, fb = feat(d['a']), feat(d['b']); X.append([a - b for a, b in zip(fa, fb)]); y.append(1 if ans[d['id']] == 'a' else 0)
beta = [0.0] * len(names); lam = 0.5
for _ in range(50):
    g = [-lam * b for b in beta]; H = [[-lam if i == j else 0 for j in range(len(names))] for i in range(len(names))]
    for x, t in zip(X, y):
        z = sum(b * v for b, v in zip(beta, x)); p = 1 / (1 + math.exp(-z))
        for i in range(len(names)):
            g[i] += (t - p) * x[i]
            for j in range(len(names)): H[i][j] -= p * (1 - p) * x[i] * x[j]
    # solve H d = -g (Gaussian elimination)
    n = len(names); M = [row[:] + [-gi] for row, gi in zip(H, g)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c])); M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r != c and M[c][c]:
                f = M[r][c] / M[c][c]; M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    d = [M[i][n] / M[i][i] for i in range(n)]; beta = [b + di for b, di in zip(beta, d)]
    if max(abs(v) for v in d) < 1e-6: break
out['dce'] = {n: round(b, 2) for n, b in zip(names, beta)}
out['dce_fit'] = f"{sum((sum(b*v for b,v in zip(beta,x))>0)==(t==1) for x,t in zip(X,y))}/{len(y)} choices predicted"
# 4. Gut ratings vs model Affinity
D = json.load(open('../../../data/suite_data.json')); aff = {}
for c in D.values():
    for t in c['teams']: aff.setdefault(t['name'], t['base'] + t['bonus'])
rows = [(K['rate'][q], ans[q], aff[K['rate'][q]]) for q in K['rate'] if q in ans]
out['gut'] = [(n, g, round(a, 1)) for n, g, a in rows]
if len(rows) > 2:
    gs, ms = [r[1] for r in rows], [r[2] for r in rows]
    mg, mm = stt.mean(gs), stt.mean(ms)
    cov = sum((a - mg) * (b - mm) for a, b in zip(gs, ms)); out['gut_r'] = round(cov / math.sqrt(sum((a-mg)**2 for a in gs) * sum((b-mm)**2 for b in ms)), 2)
# 5. timing
sec = {'e': 'everyday', 'k': 'everyday', 'p': 'pairs', 'd': 'dce', 'r': 'rate'}
tm = {}
for q, ms in times.items(): tm.setdefault(sec[q[0]], []).append(ms)
out['median_ms'] = {s: int(stt.median(v)) for s, v in tm.items()}
out['answered'] = len(ans)
print(json.dumps(out, indent=1))
