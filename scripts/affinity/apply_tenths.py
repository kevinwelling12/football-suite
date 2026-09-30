"""Apply the tenths re-rate (research/out7, brief research/DECIMAL_BRIEF.md) to scores.py and build_usl.py.
Each of C, V, H, O becomes one decimal within 0.4 of the old whole number (clamped, kept in 0-10). Team is untouched.
Run once: python3 scripts/affinity/apply_tenths.py"""
import json, pathlib, re
root = pathlib.Path(__file__).resolve().parents[2]
new = {}
for f in sorted((root / 'scripts/affinity/research/out7').glob('*.json')):
    for c in json.loads(f.read_text()): new[c['name']] = c
NUM = r'(-?\d+(?:\.\d+)?)'
fixed, done = [], set()
for path in ['scripts/affinity/scores.py', 'scripts/importers/build_usl.py']:
    p = root / path; src = p.read_text()
    def sub(m):
        q, name = m.group(1), m.group(2)
        if name not in new: return m.group(0)
        v = [float(x) for x in m.group(3, 4, 5, 6)]; r = new[name]
        for i, k in enumerate('CVHO'):
            x = r.get(k)
            if x is None: continue
            lo, hi = max(0, v[i] - .4), min(10, v[i] + .4)
            y = round(min(hi, max(lo, float(x))), 1)
            if y != round(float(x), 1): fixed.append((name, k, x, y))
            v[i] = y
        done.add(name)
        fmt = lambda x: str(int(x)) if x == int(x) else str(x)
        return f'{q}{name}{q}:({",".join(fmt(x) for x in v)},{m.group(7)},{m.group(8)},{m.group(9)})'
    src = re.sub(r"""(['"])([^'"]+)\1:\(""" + NUM + ',' + NUM + ',' + NUM + ',' + NUM + ',' + NUM + ',' + NUM + r',("[^"]*")\)', sub, src)
    p.write_text(src)
print('applied', len(done), 'of', len(new), '; clamped to band:', fixed)
print('missing', sorted(set(new) - done))
