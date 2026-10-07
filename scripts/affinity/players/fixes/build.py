"""Score corrections and the position boost (2026-10-06): a page where Kevin sets the size of the boost for his favourite
positions (quiz round 7, s03: playmaker and full-back) and corrects my factor scores for players he knows.
Answers come back to raw/responses/kevin.json and model.py applies them.

Usage: python3 scripts/affinity/players/fixes/build.py out.html
"""
import json, pathlib, re, sys
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent)); import model as M
K = ['CH', 'WK', 'LO', 'AB', 'ST', 'LE']
facts, scores = M.load()
# players he likely knows (as in quiz8/bank.py) plus his round-7 gut ratings
KNOWN = list(M.GUT) + json.loads((here / 'known.json').read_text())
def kevin_club(p):
    return any(any(k in ' '.join(M.norm(c.get('club'))) for k in M.KEVIN) for c in p.get('clubs', []))
rows = []
for n, p in facts.items():
    if n not in scores: continue
    s = scores[n]; r = M.rate(p, s)
    grp = 0 if kevin_club(p) and p.get('active') else 1 if n in KNOWN or kevin_club(p) else 2
    clubs = [c['club'] for c in sorted(p.get('clubs', []), key=lambda c: c.get('from') or 0) if c.get('club')]
    rows.append(dict(n=n, g=grp, w=p.get('gender') == 'W', act=bool(p.get('active')), f=[s[k] for k in K], c=r['conn'], p=r['pen'],
                     pos='/'.join(p.get('positions') or []), fav=M.fav_pos(p), clubs=list(dict.fromkeys(clubs))[-2:],
                     why=re.sub(r'\(?\banchors?\b\)?\s*', '', s.get('why', ''))))
rows.sort(key=lambda r: (r['g'], -M.rate(facts[r['n']], scores[r['n']])['aff']))
data = dict(W=M.W, players=rows)
t = (here / 'page.template.html').read_text().replace('/*__DATA__*/', json.dumps(data, ensure_ascii=False))
pathlib.Path(sys.argv[1]).write_text(t)
print(len(rows), 'players;', sum(r['g'] == 0 for r in rows), 'at your clubs,', sum(r['g'] == 1 for r in rows), 'known;',
      sum(r['fav'] == 1 for r in rows), 'playmakers/full-backs (main position),', sum(r['fav'] == .5 for r in rows), 'as a second position')
