"""Recompute Affinity (base) for every team in data/suite_data.json from scripts/affinity/scores.py
and the USL dict A in scripts/importers/build_usl.py.
base = (0.26*Culture + 0.26*Values + 0.14*History + 0.12*Ownership + 0.12*Team)/0.90*10 + adjustment
Team (slot S) replaced Style of play in quiz round 3: how they play plus team culture.
Displayed Affinity = base + bonus. Clubs get no regional heritage bonus (2026 re-rate); only the hometown
club (Sacramento Republic FC, +4) keeps one. Nations keep their heritage bonus (up to +10).
Track record (clubs only, scripts/affinity/performance.py): the factor score is multiplied by
k = 0.90 + 0.02 * P before adjustments, P = recency-weighted success over the last 10 seasons (0-10)."""
import ast, json, pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root / 'scripts' / 'affinity'))
from scores import S
import performance as perf
for node in ast.parse((root / 'scripts' / 'importers' / 'build_usl.py').read_text()).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'A':
        S = {**S, **ast.literal_eval(node.value)}
W = {'C': .26, 'V': .26, 'H': .14, 'O': .12, 'S': .12}  # S = Team (was Style of play)
HOMETOWN = 'Sacramento Republic FC'
p = root / 'data' / 'suite_data.json'; D = json.loads(p.read_text())
PERF = perf.load()
comps = {}
for key, comp in D.items():
    for t in comp['teams']: comps.setdefault(t['name'], []).append(key)
TR = {}  # name -> (P, season scores)
for name, cs in comps.items():
    if 'unl' not in cs and name in PERF: TR[name] = perf.track(PERF[name], perf.BAND[perf.primary(cs)])
for key, comp in D.items():
    for t in comp['teams']:
        if t['name'] in S:
            C, V, H, O, St, adj, note = S[t['name']]
            t['hai'] = dict(C=C, V=V, H=H, O=O, S=St, adj=adj, note=note)
            k = 1.0
            if key != 'unl' and t['name'] in TR:
                P, xs = TR[t['name']]; k = perf.coef(P)
                t['hai'].update(P=P, k=round(k, 3), ps=xs, pl=PERF[t['name']]['seasons'][0]['s'])
            t['base'] = max(0, round((W['C']*C + W['V']*V + W['H']*H + W['O']*O + W['S']*St) / 0.90 * 10 * k + adj, 1))
        if key != 'unl':
            t['bonus'] = 4.0 if t['name'] == HOMETOWN else 0
            if 'bonus0' in t: t['bonus0'] = t['bonus'] / 0.4
p.write_text(json.dumps(D, ensure_ascii=False, separators=(',', ':')))
print('rescored')
