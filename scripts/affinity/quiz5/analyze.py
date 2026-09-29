"""Score The Blind Draw II (quiz round 5).  python3 analyze.py answers.json [before.json]"""
import json, math, sys, statistics as stt
K = json.load(open('key.json')); A = json.load(open(sys.argv[1])); ans, times = A['answers'], A['times']
out = {}
tot, reach = {}, {}
for qid, keys in K['everyday'].items():
    for c in {c for kk in keys for c in kk}:
        vals = [kk.get(c, 0) for kk in keys]; reach[c] = reach.get(c, 0) + max(abs(min(vals)), abs(max(vals)))
    if isinstance(ans.get(qid), int):
        for c, v in keys[ans[qid]].items(): tot[c] = tot.get(c, 0) + v
out['constructs'] = {c: round(tot.get(c, 0) / reach[c], 2) for c in sorted(reach) if reach[c]}
out['attention'] = ans.get('g3') == 2
out['budget'] = {b: dict(zip(K['budget'][b], ans.get(b, []))) for b in K['budget']}
# MaxDiff best-worst scores
bw, n = {}, {}
for m, items in K['maxdiff'].items():
    for it in items: n[it] = n.get(it, 0) + 1
    if m in ans:
        w, b = items[ans[m]['w']], items[ans[m]['b']]; bw[w] = bw.get(w, 0) + 1; bw[b] = bw.get(b, 0) - 1
out['severity'] = dict(sorted(((k, round(bw.get(k, 0) / n[k], 2)) for k in n), key=lambda x: -x[1]))
# DCE
names = ['V', 'C', 'T', 'TR', 'TITLE12', 'CUPLAST', 'O', 'VIOL8', 'VIOLLAST']
def feat(l): return [l[0], l[1], l[2], l[3], l[4] == 1, l[4] == 2, l[5], l[6] == 1, l[6] == 2]
X, y = [], []
for d in K['dce']:
    if d['id'] in ans: X.append([a - b for a, b in zip(feat(d['a']), feat(d['b']))]); y.append(ans[d['id']] == 'a')
beta = [0.0] * len(names); lam = 0.5
for _ in range(60):
    g = [-lam * b for b in beta]; H = [[-lam * (i == j) for j in range(len(names))] for i in range(len(names))]
    for x, t in zip(X, y):
        p = 1 / (1 + math.exp(-sum(b * v for b, v in zip(beta, x))))
        for i in range(len(names)):
            g[i] += (t - p) * x[i]
            for j in range(len(names)): H[i][j] -= p * (1 - p) * x[i] * x[j]
    k = len(names); M = [r[:] + [-gi] for r, gi in zip(H, g)]
    for c in range(k):
        piv = max(range(c, k), key=lambda r: abs(M[r][c])); M[c], M[piv] = M[piv], M[c]
        for r in range(k):
            if r != c: f = M[r][c] / M[c][c]; M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    d = [M[i][k] / M[i][i] for i in range(k)]; beta = [b + e for b, e in zip(beta, d)]
    if max(map(abs, d)) < 1e-7: break
out['dce'] = {nm: round(b, 2) for nm, b in zip(names, beta)}
out['dce_fit'] = f"{sum((sum(b*v for b,v in zip(beta,x))>0)==t for x,t in zip(X,y))}/{len(y)}"
# speeded sort: +1 pull / -1 push; weight faster answers more
sp = {}
for s, (c, sign) in K['speed'].items():
    if s in ans:
        w = max(.5, min(1.5, 2 - times.get(s, 2000) / 2000)); sp.setdefault(c, []).append(ans[s] * sign * w)
out['speed'] = {c: round(stt.mean(v), 2) for c, v in sorted(sp.items())}
out['speed_ms'] = int(stt.median([times[s] for s in K['speed'] if s in times]))
# hold-out vignettes
D = json.load(open('../../../data/suite_data.json')); aff = {}
for c in D.values():
    for t in c['teams']: aff.setdefault(t['name'], t['base'] + t['bonus'])
def r(m, g):
    mg, mm = stt.mean(g), stt.mean(m); return round(sum((a-mm)*(b-mg) for a, b in zip(m, g)) / math.sqrt(sum((a-mm)**2 for a in m) * sum((b-mg)**2 for b in g)), 3)
g = [ans[q] for q in K['rate']]
out['gut'] = {K['rate'][q]: [ans[q], round(aff[K['rate'][q]], 1)] for q in K['rate']}
out['gut_r_now'] = r([aff[K['rate'][q]] for q in K['rate']], g)
if len(sys.argv) > 2:
    b = json.load(open(sys.argv[2])); out['gut_r_before_round4'] = r([b[K['rate'][q]] for q in K['rate']], g)
out['answered'] = len(ans)
print(json.dumps(out, indent=1, ensure_ascii=False))
