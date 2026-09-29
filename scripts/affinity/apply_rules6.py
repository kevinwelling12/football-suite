"""Apply the rules re-rate (research/out6, brief RULES6_BRIEF.md) to scores.py and build_usl.py. Run once.
Each hit moves one factor by 1 (kept 0-10) and is recorded in the club's note."""
import json, pathlib, re
root = pathlib.Path(__file__).resolve().parents[2]
SKIP = {('Austin FC', 'R1'): "Precourt faced no real consequence (he got the Austin club)",
        ('Shrewsbury Town', 'R2'): "Spartans is a community club, not a multi-club group",
        ('Detroit City FC', 'R2'): "leaves historic Keyworth; not a clear upgrade"}
IDX = {'C': 0, 'V': 1, 'H': 2, 'O': 3, 'S': 4}
NAME = {'C': 'Culture', 'V': 'Values', 'H': 'History', 'O': 'Ownership', 'S': 'Team'}
hits = {}
for f in sorted((root / 'scripts/affinity/research/out6').glob('*.json')):
    for c in json.loads(f.read_text()):
        for h in c['hits']:
            if (c['name'], h['rule']) not in SKIP: hits.setdefault(c['name'], []).append(h)
done = set()
for path in ['scripts/affinity/scores.py', 'scripts/importers/build_usl.py']:
    p = root / path; src = p.read_text()
    for name, hs in hits.items():
        m = re.search(r"""(['"])%s\1:\((\d+),(\d+),(\d+),(\d+),(\d+),(-?[\d.]+),"([^"]*)"\)""" % re.escape(name), src)
        if not m: continue
        v = [int(x) for x in m.group(2, 3, 4, 5, 6)]; parts = []
        for h in hs:
            i = IDX[h['factor']]; old = v[i]; v[i] = max(0, min(10, v[i] + h['delta']))
            parts.append(f"{h['rule']} {NAME[h['factor']]} {old}->{v[i]}")
        note = m.group(8); note = (note + '; ' if note else '') + 'Rules re-rate 2026-09-30: ' + ', '.join(parts)
        q = m.group(1)
        src = src[:m.start()] + f'{q}{name}{q}:({",".join(map(str, v))},{m.group(7)},"{note}")' + src[m.end():]
        done.add(name); print(name, parts)
    p.write_text(src)
print('missing', set(hits) - done)
