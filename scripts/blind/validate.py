"""Held-out check: how well do Affinity rankings agree with Kevin's past quiz answers about NAMED clubs and players?

  python3 scripts/blind/validate.py

The blind model never saw these answers (it is fitted only to the blind test), so this is a true held-out test for it.
The categories model was fitted to some of them (marked "in its fit"), so its numbers flatter it. Named answers are also
confounded by familiarity (evidence/summary.md): treat this as a sanity check, not a target.
Sets: club gut ratings (rounds 4-5, as pairs), named club pairs (round 6), nation gut ratings (round 13, as pairs),
named player pairs (rounds 8 and 10), player gut ratings (round 7, rank correlation).
"""
import json, pathlib, sys
from scipy.stats import spearmanr
root = pathlib.Path(__file__).resolve().parents[2]
A = root / 'scripts' / 'affinity'
sys.path.insert(0, str(A / 'evidence'))
import load as E

ev = E.load()

def pairs_from_gut(g):
    return [(a, b, 1.0 if va > vb else 0.0, abs(va - vb)) for i, (a, va) in enumerate(g) for b, vb in g[i + 1:] if va != vb]

def sets():
    S = {}
    gut = [(n, v) for n, v, r in E.gut_clubs(ev)]
    S['club gut (r4-5)'] = ('club', pairs_from_gut([(n, v) for n, v, r in E.gut_clubs(ev) if r['round'] == 'q4'])
                           + pairs_from_gut([(n, v) for n, v, r in E.gut_clubs(ev) if r['round'] == 'q5']))
    S['named club pairs (r6)'] = ('club', [(a, b, y, 1.0) for a, b, y, r in E.pairs(ev, domain='club', named=True) if r['round'] == 'q6' and y != .5])
    q13 = A / 'quiz13'
    if (q13 / 'raw' / 'responses' / 'kevin.json').exists():
        a = json.loads((q13 / 'raw' / 'responses' / 'kevin.json').read_text()); a = a.get('data', a)['answers']
        k = json.loads((q13 / 'key.json').read_text())
        S['nation gut (r13)'] = ('club', pairs_from_gut([(n, a[i]) for i, n in k['gut'].items() if isinstance(a.get(i), (int, float))]))
    S['named player pairs (r8, r10)'] = ('player', [(a, b, y, 1.0) for a, b, y, r in E.pairs(ev, domain='player', named=True)
                                                    if r['round'] in ('q8', 'q10') and y != .5])
    S['player gut (r7)'] = ('player_gut', [(n, v) for n, v, r in E.gut_players(ev)])
    return S

def score(S, clubs, players):
    out = {}
    for name, (kind, xs) in S.items():
        if kind == 'player_gut':
            xs = [(n, v) for n, v in xs if n in players]
            out[name] = f"r={spearmanr([players[n] for n, _ in xs], [v for _, v in xs])[0]:.2f} (n={len(xs)})"
            continue
        T = clubs if kind == 'club' else players
        xs = [(a, b, y, w) for a, b, y, w in xs if a in T and b in T]
        hit = sum(w for a, b, y, w in xs if (T[a] > T[b]) == (y > .5)); tot = sum(w for *_, w in xs)
        out[name] = f"{hit / tot:.0%} of {len(xs)}"
    return out

def live_tables():
    D = json.loads((root / 'data' / 'suite_data.json').read_text()); X = json.loads((root / 'data' / 'nations_extra.json').read_text())
    clubs = {t['name']: t['base'] + t['bonus'] for c in D.values() for t in c['teams']}
    clubs.update({t['name']: t['base'] + t['bonus'] for t in X['teams'] + X.get('clubs', [])})
    P = json.loads((root / 'data' / 'players.json').read_text())
    return clubs, P

if __name__ == '__main__':
    S = sets()
    sys.path.insert(0, str(here := pathlib.Path(__file__).resolve().parent))
    import live
    for label, kw in (('blind, as shipped', dict(fair=False)), ('blind, improved', dict(fair=True))):
        clubs, players = live.scores(**kw)
        print(f'{label}:', score(S, clubs, players))
    sys.path.insert(0, str(A)); sys.argv = ['x']
    import affinity as M
    R, PL = M.run(write=False)
    print('categories model (in its fit for r4-5, r10, r13):', score(S, {n: r['A'] for n, r in R.items()}, {n: p['A'] for n, p in PL.items()}))
