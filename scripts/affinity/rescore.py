"""Recompute Affinity (base) for every team in data/suite_data.json from scripts/affinity/scores.py
and the USL dict A in scripts/importers/build_usl.py.
base = (0.23*Culture + 0.26*Values + 0.16*History + 0.10*Ownership + 0.15*Team)/0.90*10 * k + adjustment
Team (slot S) replaced Style of play in quiz round 3: how they play plus team culture.
Displayed Affinity = base + bonus. Clubs get no regional heritage bonus (2026 re-rate); only the hometown
club (Sacramento Republic FC, +4) keeps one. Nations keep their heritage bonus (up to +10).
Track record (clubs only, scripts/affinity/performance.py): the factor score is multiplied by
k = 0.85 + 0.03 * P before adjustments; base is capped at 100. Then Kevin's big-4 items
(scripts/affinity/big4.py: distance, rival markets, ownership ties). Then association pulls
(scripts/affinity/association.py) move linked clubs toward each other, P = recency-weighted success over the last 10 seasons (0-10).
Squad interplay (scripts/affinity/interplay.py) adds up to +/-2 to Team: clubs by homegrown share against their league,
nations by how Kevin rates the clubs their internationals play for.
Players (scripts/affinity/players_link.py): Kevin's Player Affinity for a club's best 5 current players moves Team
(up to +/-1.5) and for its best 5 icons moves History (up to +/-1). Run everything with scripts/affinity/unified.py."""
import ast, json, pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root / 'scripts' / 'affinity'))
from scores import S
import performance as perf
import association as assoc
import big4
import interplay
import players_link
for node in ast.parse((root / 'scripts' / 'importers' / 'build_usl.py').read_text()).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'A':
        S = {**S, **ast.literal_eval(node.value)}
W = {'C': .23, 'V': .26, 'H': .16, 'O': .10, 'S': .15}  # S = Team (was Style of play). Quiz round 5, 2026-09-29 (round 4: 20/27/17/10/16)
HOMETOWN = 'Sacramento Republic FC'
p = root / 'data' / 'suite_data.json'; D = json.loads(p.read_text())
PERF = perf.load()
comps = {}
for key, comp in D.items():
    for t in comp['teams']: comps.setdefault(t['name'], []).append(key)
TR = {}  # name -> (P, season scores)
for name, cs in comps.items():
    if 'unl' not in cs and name in PERF and perf.primary(cs) in perf.APPLIES: TR[name] = perf.track(PERF[name], perf.BAND[perf.primary(cs)])
PL = players_link.bumps(D)  # Player Affinity -> Team (current squad) and History (icons); see players_link.py
DOM = interplay.domestic({n: perf.primary(cs) for n, cs in comps.items() if 'unl' not in cs})
for key, comp in D.items():
    for t in comp['teams']:
        if t['name'] in S:
            C, V, H, O, St, adj, note = S[t['name']]
            t['hai'] = dict(C=C, V=V, H=H, O=O, S=St, adj=adj, note=note)
            if key != 'unl' and t['name'] in DOM:
                b, sh, m = DOM[t['name']]
                St = round(min(10, max(0, St + b)), 1)
                t['hai'].update(S=St, S0=S[t['name']][4], tb=b, dom=[sh, m])
            if key != 'unl' and t['name'] in PL:
                b = PL[t['name']]
                s1 = round(min(10, max(0, St + b['team'])), 1); h1 = round(min(10, max(0, H + b['hist'])), 1)
                dt, dh = round(s1 - St, 2), round(h1 - H, 2); St, H = s1, h1  # what was applied (a 10 can't go higher)
                t['hai'].update(S=St, H=H, H0=S[t['name']][2], py=dict(t=dt, h=dh, sq=[n for n, _ in b['squad'][:3]], ic=[n for n, _ in b['icons'][:3]]))
            k = 1.0
            if key != 'unl' and t['name'] in TR:
                P, xs = TR[t['name']]; k = perf.coef(P)
                t['hai'].update(P=P, k=round(k, 3), ps=xs, pl=PERF[t['name']]['seasons'][0]['s'])
            t['base'] = min(100, max(0, round((W['C']*C + W['V']*V + W['H']*H + W['O']*O + W['S']*St) / 0.90 * 10 * k + adj, 1)))
        if key != 'unl':
            t['bonus'] = 4.0 if t['name'] == HOMETOWN else 0
            if 'bonus0' in t: t['bonus0'] = t['bonus'] / 0.4
# Kevin's big-4 teams: distance from Sacramento, rival markets, ownership ties (big4.py). hai.us = items.
for key, comp in D.items():
    for t in comp['teams']:
        h = t.get('hai')
        if not h or key == 'unl': continue
        its = big4.items(t['name'], 'Rival' in h.get('note', ''))
        if its:
            h.update(us=[[l, v] for l, v in its], usTot=big4.total(its))
            t['base'] = min(100, max(0, round(t['base'] + h['usTot'], 1)))
# Association: second pass, on Affinity before any pull (hai.assoc = total pull, hai.links = per partner).
pre, rivals, seen = {}, set(), set()
for key, comp in D.items():
    for t in comp['teams']:
        pre.setdefault(t['name'], t['base'] + t['bonus'])
        if 'Rival' in (t.get('hai') or {}).get('note', ''): rivals.add(t['name'])
PULL = assoc.pulls(pre, rivals)
for key, comp in D.items():
    for t in comp['teams']:
        if t['name'] in PULL and t.get('hai'):
            tot, ps = PULL[t['name']]
            t['hai'].update(assoc=tot, links=[[y, v] for y, v in ps])
            t['base'] = min(100, max(0, round(t['base'] + tot, 1)))
# Squad interplay for nations: how Kevin rates the clubs their internationals play for (after clubs are final).
club_aff = {t['name']: t['base'] + t['bonus'] for k2, c2 in D.items() if k2 != 'unl' for t in c2['teams']}
px = root / 'data' / 'nations_extra.json'
nations = {t['name'] for t in D['unl']['teams']} | ({t['name'] for t in json.loads(px.read_text())['teams']} if px.exists() else set())
NL = interplay.nation_links(club_aff, nations)
def nation_bump(t):
    if t['name'] not in NL: return
    b, top = NL[t['name']]; h = t['hai']; s0 = h['S']; St = round(min(10, max(0, s0 + b)), 1)
    t['base'] = min(100, max(0, round(t['base'] + W['S'] * (St - s0) / 0.90 * 10, 1)))
    h.update(S=St, S0=s0, tb=b, clubs=[[c, n, v] for c, n, v in top])
for t in D['unl']['teams']:
    if t.get('hai'): nation_bump(t)
# Nations outside the Nations League (2026 World Cup field): data/nations_extra.json, same factors, no track record.
# Heritage bonus: the United States is Kevin's home nation (+10, the nations' maximum).
NATION_BONUS = {'United States': (10.0, 'Home nation')}
px = root / 'data' / 'nations_extra.json'
if px.exists():
    X = json.loads(px.read_text())
    for t in X['teams']:
        C, V, H, O, St, adj, note = S[t['name']]
        t['hai'] = dict(C=C, V=V, H=H, O=O, S=St, adj=adj, note=note)
        t['base'] = min(100, max(0, round((W['C']*C + W['V']*V + W['H']*H + W['O']*O + W['S']*St) / 0.90 * 10 + adj, 1)))
        t['bonus'], t['region'] = NATION_BONUS.get(t['name'], (0, ''))
        nation_bump(t)
    px.write_text(json.dumps(X, ensure_ascii=False, indent=1))
p.write_text(json.dumps(D, ensure_ascii=False, separators=(',', ':')))
print('rescored')
