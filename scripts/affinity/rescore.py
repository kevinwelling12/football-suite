"""Recompute Affinity (base) for every team in data/suite_data.json from scripts/affinity/scores.py.
base = (0.28*Culture + 0.22*Values + 0.18*History + 0.14*Ownership + 0.08*Style)/0.90*10 + adjustment
Displayed Affinity = base + bonus (heritage tiebreaker). USL scores live in scripts/importers/build_usl.py (dict A)."""
import json, pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root / 'scripts' / 'affinity'))
from scores import S
W = {'C': .28, 'V': .22, 'H': .18, 'O': .14, 'S': .08}
p = root / 'data' / 'suite_data.json'; D = json.loads(p.read_text())
for comp in D.values():
    for t in comp['teams']:
        if t['name'] in S:
            C, V, H, O, St, adj, note = S[t['name']]
            t['hai'] = dict(C=C, V=V, H=H, O=O, S=St, adj=adj, note=note)
            t['base'] = max(0, round((W['C']*C + W['V']*V + W['H']*H + W['O']*O + W['S']*St) / 0.90 * 10 + adj, 1))
p.write_text(json.dumps(D, ensure_ascii=False, separators=(',', ':')))
print('rescored')
