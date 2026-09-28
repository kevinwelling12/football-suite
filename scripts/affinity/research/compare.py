"""Validate the re-rate research outputs and compare them with the current Affinity scores.

python3 scripts/affinity/research/compare.py [--weights C,V,H,O,S] [--md out.md] [--dir out|final]

Checks (runbook step 2): every batch name present, scores are integers 0-10, >= 2 sources, adjustment
types from the brief. Calibration (step 3): per-factor mean by batch and the anchor clubs. Report
(step 4): flags, low-confidence entries, biggest changes in displayed Affinity.

Old = scores.py / build_usl.py with the old weights and the current heritage bonus.
New = research scores with the proposed weights; clubs lose the regional bonus (Sacramento keeps +4),
nations keep theirs. Nothing is written back.
"""
import ast, json, pathlib, statistics, sys

root = pathlib.Path(__file__).resolve().parents[3]
R = root / 'scripts' / 'affinity' / 'research'
sys.path.insert(0, str(root / 'scripts' / 'affinity'))
from scores import S as OLD

# USL scores live in build_usl.py as dict A; read it without running the builder.
src = (root / 'scripts' / 'importers' / 'build_usl.py').read_text()
for node in ast.parse(src).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'A':
        OLD.update(ast.literal_eval(node.value))

OLD_W = dict(C=28, V=22, H=18, O=14, S=8)
NEW_W = dict(C=26, V=28, H=16, O=12, S=8)
args = sys.argv[1:]
if '--weights' in args:
    NEW_W = dict(zip('CVHOS', map(int, args[args.index('--weights') + 1].split(','))))
MD = args[args.index('--md') + 1] if '--md' in args else None
OUT = args[args.index('--dir') + 1] if '--dir' in args else 'out'
TYPES = {'state', 'lbo', 'pe', 'multiclub', 'superleague', 'racism', 'violence', 'overspend', 'franchise',
         'government', 'other'}
F = 'CVHOS'


def base(f, adj, w):
    return max(0, round(sum(w[k] * f[k] for k in F) / sum(w.values()) * 10 + adj, 1))


# current heritage bonus, per team name, from the built data
bonus = {}
for comp in json.loads((root / 'data' / 'suite_data.json').read_text()).values():
    for t in comp['teams']:
        bonus[t['name']] = t.get('bonus') or 0

errors, rows, by_batch = [], [], {}
for bf in sorted(R.glob('b[0-9][0-9]-*.json')):
    batch = bf.stem
    names = [e['name'] for e in json.loads(bf.read_text())]
    of = R / OUT / f'{batch}.json'
    if not of.exists():
        errors.append(f'{batch}: no output yet'); continue
    out = {e.get('name'): e for e in json.loads(of.read_text())}
    for n in names:
        if n not in out:
            errors.append(f'{batch}: missing {n}'); continue
    for n in set(out) - set(names):
        errors.append(f'{batch}: unexpected name {n}')
    for n in names:
        e = out.get(n)
        if not e: continue
        f = {}
        for k in F:
            s = (e.get(k) or {}).get('score')
            if not isinstance(s, int) or not 0 <= s <= 10:
                errors.append(f'{batch}: {n} {k} score {s!r}')
            f[k] = s if isinstance(s, (int, float)) else 0
        if len(e.get('sources') or []) < 2:
            errors.append(f'{batch}: {n} has {len(e.get("sources") or [])} source(s)')
        adj = 0
        for a in e.get('adjustments') or []:
            if a.get('type') not in TYPES:
                errors.append(f'{batch}: {n} adjustment type {a.get("type")!r}')
            if not isinstance(a.get('points'), (int, float)):
                errors.append(f'{batch}: {n} adjustment points {a.get("points")!r}')
            else:
                adj += a['points']
        nation = batch.startswith(('b10', 'b11'))
        old = OLD.get(n)
        old_disp = None
        if old:
            o = dict(zip(F, old[:5]))
            old_disp = round(base(o, old[5], OLD_W) + bonus.get(n, 0), 1)
        nb = bonus.get(n, 0) if nation else (4.0 if n == 'Sacramento Republic FC' else 0)
        new_disp = round(base(f, adj, NEW_W) + nb, 1)
        r = dict(batch=batch, name=n, f=f, adj=adj, old=old, old_disp=old_disp, new_disp=new_disp,
                 flags=e.get('flags') or [], conf=e.get('confidence'), adjs=e.get('adjustments') or [])
        rows.append(r); by_batch.setdefault(batch, []).append(r)

lines = []
p = lines.append
p(f'Weights old {OLD_W}  new {NEW_W}')
p(f'\nValidation: {len(rows)} entries, {len(errors)} problem(s)')
for x in errors: p('  ' + x)

p('\nMean factor score by batch (new / old on the same clubs)')
p('batch'.ljust(30) + ''.join(k.rjust(11) for k in F) + '   adj')
for b, rs in by_batch.items():
    cells = []
    for k in F:
        nm = statistics.mean(r['f'][k] for r in rs)
        olds = [dict(zip(F, r['old'][:5]))[k] for r in rs if r['old']]
        cells.append(f'{nm:4.1f}/{statistics.mean(olds):4.1f}' if olds else f'{nm:4.1f}/  - ')
    p(b.ljust(30) + ''.join(c.rjust(11) for c in cells) + f'{statistics.mean(r["adj"] for r in rs):6.1f}')

ANCHORS = [('Borussia Dortmund', 'C', 10), ('Union Berlin', 'C', 10), ('Portland Timbers', 'C', 10),
           ('Union Berlin', 'O', 10), ('Athletic Club', 'O', 10), ('Liverpool', 'H', 10),
           ('Real Madrid', 'H', 10), ('Athletic Club', 'H', 10), ('Seattle Sounders FC', 'C', 9),
           ('Portland Timbers', 'O', 5), ('Sacramento Republic FC', 'O', 8)]
idx = {r['name']: r for r in rows}
p('\nAnchors')
for n, k, want in ANCHORS:
    got = idx[n]['f'][k] if n in idx else None
    p(f'  {"ok " if got == want else "OFF"} {n} {k} = {got} (want {want})')
for n, want in [('Lazio', ('racism', -30)), ('Milton Keynes Dons', ('franchise', -15))]:
    got = [(a['type'], a['points']) for a in idx[n]['adjs']] if n in idx else None
    p(f'  {"ok " if got and want in got else "OFF"} {n} adjustments {got} (want {want})')

ch = sorted((r for r in rows if r['old_disp'] is not None), key=lambda r: r['new_disp'] - r['old_disp'])
p('\nBiggest drops (displayed Affinity, old -> new)')
for r in ch[:25]:
    p(f'  {r["name"]:28} {r["old_disp"]:5.1f} -> {r["new_disp"]:5.1f} ({r["new_disp"] - r["old_disp"]:+.1f})  '
      f'{"".join(str(r["f"][k]).rjust(3) for k in F)} adj {r["adj"]}')
p('\nBiggest rises')
for r in ch[::-1][:25]:
    p(f'  {r["name"]:28} {r["old_disp"]:5.1f} -> {r["new_disp"]:5.1f} ({r["new_disp"] - r["old_disp"]:+.1f})  '
      f'{"".join(str(r["f"][k]).rjust(3) for k in F)} adj {r["adj"]}')
new_only = [r['name'] for r in rows if r['old'] is None]
if new_only: p(f'\nNo old score: {", ".join(new_only)}')

p('\nLow confidence: ' + ', '.join(r['name'] for r in rows if r['conf'] == 'low'))
p('\nFlags')
for r in rows:
    for fl in r['flags']:
        p(f'  [{r["batch"][:3]}] {r["name"]}: {fl}')

text = '\n'.join(lines)
print(text)
if MD:
    pathlib.Path(MD).write_text(text + '\n')
