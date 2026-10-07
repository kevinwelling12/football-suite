"""Quiz round 10: named head-to-heads with the confounders held still (Kevin, 2026-10-06).

Round 8's named pairs differed on everything at once, so name recognition decided them. Here each pair is drawn from one
setting (two current Liverpool players, two Dortmund players, two from Portland or Sacramento, two stars with no link to
his clubs, two Liverpool greats) so club connection, position boost and baggage match, and the two players differ clearly
on one or two factors (1.25+ points on the audited scores) and little on the rest (1 point or less). The pass buttons
("don't know X well enough") are data too: they show who he knows, and picks are checked for a pull toward the known name.
"""
import json, pathlib, random, sys, itertools
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / 'players')); import model as M
rnd = random.Random(1010)
facts, scores = M.load()
K = ['CH', 'WK', 'LO', 'AB', 'ST', 'LE']
R = {n: M.rate(facts[n], scores[n]) for n in facts if n in scores}
def cur(n): return ' '.join(c['club'] for c in facts[n].get('clubs', []) if not c.get('to')).lower()
def ever(n, k): return any(k in (c.get('club') or '').lower() for c in facts[n].get('clubs', []))
clean = lambda n: R[n]['pen'] == 0
def lfc_seasons(n): return sum(M.seasons(c) for c in facts[n].get('clubs', []) if 'liverpool' in (c.get('club') or '').lower())
FAM = {'GK': 'GK', 'CB': 'CB', 'SW': 'CB', 'RB': 'FB', 'LB': 'FB', 'RWB': 'FB', 'LWB': 'FB', 'DM': 'CM', 'CM': 'CM', 'DLP': 'CM',
       'AM': 'AM', 'RW': 'W', 'LW': 'W', 'W': 'W', 'RM': 'W', 'LM': 'W', 'ST': 'ST', 'CF': 'ST', 'FW': 'ST', 'SS': 'ST'}
def fam(n): ps = facts[n].get('positions') or ['?']; return FAM.get(ps[0], ps[0])
nolink = lambda n: facts[n].get('active') and abs(R[n]['conn']) < .5
GROUPS = [  # (key, label, members, how many pairs, tolerance on the other factors, only these factors may differ)
    ('lfc', 'Two Liverpool players', [n for n in R if facts[n].get('active') and 'liverpool' in cur(n)], 7, 1.5, None),
    ('bvb', 'Two Dortmund players', [n for n in R if facts[n].get('active') and 'dortmund' in cur(n)], 4, 1.5, None),
    ('pdx', 'Two from Portland or Sacramento', [n for n in R if facts[n].get('active') and any(k in cur(n) for k in ('portland', 'sacramento'))], 5, 1.0, None),
    ('lvl', 'Same kind of player, different level', [n for n in R if nolink(n)], 6, 1.0, {'AB'}),
    ('star', 'Two stars, no link to your clubs', [n for n in R if nolink(n) and scores[n]['AB'] >= 7.5], 12, 1.0, None),
    ('lgd', 'Two Liverpool greats', [n for n in R if not facts[n].get('active') and lfc_seasons(n) >= 4], 4, 1.0, None),
]
NAMES = {'POS': 'Playmaker/full-back', 'CH': 'Character', 'WK': 'Team player', 'LO': 'Loyalty & bond', 'AB': 'Greatness', 'ST': 'Joy to watch', 'LE': 'Legacy'}
used, cover, items, done = {}, {k: 0 for k in K + ['POS']}, [], set()
for key, label, mem, want, tol, only in GROUPS:
    mem = [n for n in mem if clean(n)]
    cands = []
    for a, b in itertools.combinations(mem, 2):
        if facts[a].get('gender') != facts[b].get('gender'): continue
        posd = M.fav_pos(facts[a]) - M.fav_pos(facts[b])  # playmaker / full-back boost differs: counts as one of the variables
        if abs(R[a]['conn'] - R[b]['conn']) > 2: continue
        d = {k: scores[a][k] - scores[b][k] for k in K}
        big = [k for k in K if abs(d[k]) >= 1.25]
        var = big + (['POS'] if posd else [])
        if not 1 <= len(var) <= 2 or any(abs(d[k]) > tol for k in K if k not in big) or (only and set(var) - only): continue
        if only and 'AB' in only and (abs(d['AB']) < 1.5 or fam(a) != fam(b)): continue
        d['POS'] = posd; cands.append((a, b, var, d))
    rnd.shuffle(cands); got = 0
    while got < want and cands:
        # favour factors tested least so far, players used least, trade-offs (two factors pulling opposite ways)
        def val(c):
            a, b, big, d = c
            trade = len(big) == 2 and d[big[0]] * d[big[1]] < 0
            if key in ('lfc', 'bvb') and 'POS' in big and cover['POS'] >= 4: return -99
            return -min(cover[k] for k in big) * 3 - used.get(a, 0) * 2 - used.get(b, 0) * 2 + trade * 2
        c = max(cands, key=val); cands.remove(c); a, b, big, d = c
        if used.get(a, 0) >= 2 or used.get(b, 0) >= 2 or (a, b) in done: continue
        done.add((a, b))
        used[a] = used.get(a, 0) + 1; used[b] = used.get(b, 0) + 1
        for k in big: cover[k] += 1
        items.append(dict(id=f'n{len(items)+1:02d}', g=label, l=a, r=b, test=big, d={k: round(v, 2) for k, v in d.items()})); got += 1
    print(f'{label}: {got} of {want} ({len(mem)} players)')
json.dump(dict(items=[dict(id=i['id'], g=i['g'], l=i['l'], r=i['r']) for i in items]), open(here / 'questions.json', 'w'), ensure_ascii=False)
json.dump(items, open(here / 'key.json', 'w'), ensure_ascii=False, indent=1)
print(len(items), 'pairs; factor tested:', cover)
for i in items: print(f"  {i['g'][:14]:14s} {i['l']} v {i['r']}: " + ', '.join(f"{NAMES[k]} {i['d'][k]:+.2f}" for k in i['test']))
