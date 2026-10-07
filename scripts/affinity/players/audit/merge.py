"""Merge the independent audit (audit/out/*.json) with the first scoring (scores/).

- Scores: where the two scorers are within 1.5 points, the merged score is the average. Wider gaps go to adjudication
  (audit/adjudicated.json, written by a third scorer who sees both and the reasons); until then the average stands.
- Incidents: verdicts and missing incidents are written to audit/incidents.json, which model.load() applies to the facts.

Usage: python3 scripts/affinity/players/audit/merge.py
"""
import json, glob, pathlib, sys
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent)); import model as M
K = ['CH', 'WK', 'LO', 'AB', 'ST', 'LE']
_, scores = M.load(raw=True)
audit = {a['name']: a for f in sorted(glob.glob(str(here / 'out' / '*.json'))) for a in json.load(open(f))}
adj = json.loads((here / 'adjudicated.json').read_text()) if (here / 'adjudicated.json').exists() else {}
merged, gaps, inc = {}, [], {}
for n, a in audit.items():
    if n not in scores: print('unknown name', n); continue
    s = scores[n]; m = {}
    for k in K:
        d = a[k] - s[k]
        if abs(d) > 1.5 and k not in adj.get(n, {}): gaps.append(dict(name=n, k=k, first=s[k], audit=a[k], first_why=s.get('why', ''), audit_why=a.get('why', '')))
        m[k] = adj.get(n, {}).get(k, round((a[k] + s[k]) / 2 * 4) / 4)
    merged[n] = dict(m, why=s.get('why', ''), audit_why=a.get('why', ''))
    bad = [v for v in a.get('incidents', []) if v.get('verdict') != 'ok']
    if bad or a.get('missing'): inc[n] = dict(verdicts=bad, missing=a.get('missing', []))
json.dump(merged, open(here / 'merged.json', 'w'), ensure_ascii=False, indent=1)
json.dump(inc, open(here / 'incidents.json', 'w'), ensure_ascii=False, indent=1)
json.dump(gaps, open(here / 'gaps.json', 'w'), ensure_ascii=False, indent=1)
diff = [abs(audit[n][k] - scores[n][k]) for n in merged for k in K]
print(f'{len(merged)} players merged; mean gap {sum(diff) / len(diff):.2f}; {len(gaps)} gaps over 1.5 to adjudicate;',
      f'{sum(len(v["verdicts"]) for v in inc.values())} incident corrections, {sum(len(v["missing"]) for v in inc.values())} added')
