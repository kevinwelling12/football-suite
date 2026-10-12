"""Affinity from Kevin's chosen clubs (2026-10-12, Kevin: "base the entire affinity ratings on my chosen clubs. Look at the
factors that they share and use that as the basis for rating all other clubs and players ... Lets get back to basics.").

  python3 scripts/favs/live.py      # writes data/suite_data.json scores, data/players.json, params.json "favs"; then build

Clubs: every club is described by the researched facts in scripts/blind (coded/*.json, scaled 0-1 by blind/build.py,
plus distance from Sacramento). For each fact: how far the chosen clubs sit from the average club (in standard
deviations), times how much they agree with each other (1 - their spread / everyone's spread, at least 0). A club's score
is the sum over facts of that weight times how far the club sits from the average, scaled 0-100 across all clubs.
Players: the average score of the clubs they played for, weighted by seasons at each.
"""
import json, math, pathlib, re, sys
here = pathlib.Path(__file__).resolve().parent
root = here.parents[1]
sys.path.insert(0, str(root / 'scripts' / 'blind'))
import build, live as blind

CHOSEN = ['Liverpool', 'Real Madrid', 'Borussia Dortmund', 'Portland Timbers', 'Portland Thorns', 'Sacramento Republic FC']
HOME = (38.58, -121.49)   # Sacramento
LABEL = {f[0]: f[2] for f in blind.Q['CF']}
SKIP = {'home', 'gov'}     # national-team facts

def model():
    clubs, _ = build.rows()
    clubs = [c for c in clubs if c['k'] != 'nation']
    for c in clubs: c['f']['near'] = blind.near(blind.haversine(HOME, c['ll'])) if c['ll'] else 0.0
    keys = [k for k in clubs[0]['f'] if k not in SKIP]
    fav = [c for c in clubs if c['n'] in CHOSEN]
    mu = {k: sum(c['f'][k] for c in clubs) / len(clubs) for k in keys}
    sd = {k: math.sqrt(sum((c['f'][k] - mu[k]) ** 2 for c in clubs) / len(clubs)) or 1e-9 for k in keys}
    w = {}
    for k in keys:
        m = sum(c['f'][k] for c in fav) / len(fav); s = math.sqrt(sum((c['f'][k] - m) ** 2 for c in fav) / len(fav))
        w[k] = (m - mu[k]) / sd[k] * max(0.0, 1 - s / sd[k])
    raw = {}
    for c in clubs:
        parts = [(k, round(c['f'][k], 2), w[k] * (c['f'][k] - mu[k]) / sd[k]) for k in keys]
        raw[c['n']] = (sum(p[2] for p in parts), parts)
    lo, hi = min(v[0] for v in raw.values()), max(v[0] for v in raw.values()); span = hi - lo
    S = {}
    for n, (s, parts) in raw.items():
        parts = sorted(((k, x, round(100 * v / span, 1)) for k, x, v in parts), key=lambda p: -abs(p[2]))
        S[n] = (round(100 * (s - lo) / span, 1), [p for p in parts if abs(p[2]) >= 0.5])
    return S, w

def main():
    S, w = model()
    D = json.loads((root / 'data' / 'suite_data.json').read_text())
    for c in D.values():
        for t in c['teams']:
            a, parts = S.get(t['name'], (50.0, []))
            t['base'], t['bonus'], t['hai'] = a, 0, dict(blind=1, fx=parts[:12])
    (root / 'data' / 'suite_data.json').write_text(json.dumps(D, ensure_ascii=False, separators=(',', ':')))

    # players: seasons-weighted average of their clubs' scores
    sys.path.insert(0, str(root / 'scripts' / 'affinity' / 'players')); sys.path.insert(0, str(root / 'scripts' / 'affinity'))
    import model as PM
    from affinity import lookup
    T = {' '.join(PM.norm(n)): v[0] for n, v in S.items()}
    facts, _ = PM.load()
    _, players = build.rows()
    NWSL = re.compile(r'thorns|kansas city current|orlando pride|washington spirit|north carolina courage|gotham|seattle reign|san diego wave|'
                      r'red stars|chicago stars|angel city|bay fc|utah royals|houston dash|racing louisville|denver summit|boston legacy', re.I)
    SIZE = {'ma': 75, 'mt': 75, 'wa': 30, 'wt': 30}; L = {k: [] for k in SIZE}; rated = []
    for p in players:
        fa = facts.get(p['n'], {}); tot = 0.0; acc = 0.0; per = {}
        for c in fa.get('clubs', []):
            nm = c.get('club') or ''
            if re.search(r'\b(II|B|U\d+|youth|academy|reserves)\b', nm, re.I): continue
            a = lookup(nm, T); yrs = PM.seasons(c)
            if a is None or not yrs: continue
            acc += a * yrs; tot += yrs; per[nm] = per.get(nm, 0) + yrs
        if not tot: continue
        score = round(acc / tot, 1)
        fx = sorted(((n, round(y / tot, 2), round(lookup(n, T) * y / tot, 1)) for n, y in per.items()), key=lambda x: -x[2])
        clubs_ = [c['club'] for c in sorted(fa.get('clubs', []), key=lambda c: c.get('from') or 0) if c.get('club')]
        e = dict(n=p['n'], a=score, nat=p['nat'], pos=p['pos'], clubs=list(dict.fromkeys(clubs_))[-2:], fx=fx[:6],
                 nw=next((c['club'] for c in fa.get('clubs', []) if not c.get('to') and NWSL.search(c.get('club') or '')), None))
        rated.append((p, e))
    rated.sort(key=lambda x: -x[1]['a'])
    for p, e in rated:
        g = 'w' if p['g'] == 'W' else 'm'
        if len(L[g + 't']) < SIZE[g + 't']: L[g + 't'].append(e)
        if p['a'] and len(L[g + 'a']) < SIZE[g + 'a']: L[g + 'a'].append(e)
    (root / 'data' / 'players.json').write_text(json.dumps(L, ensure_ascii=False, separators=(',', ':')))

    P = json.loads((root / 'scripts' / 'affinity' / 'params.json').read_text())
    P['favs'] = dict(date='2026-10-12', chosen=CHOSEN, weights={LABEL.get(k, k): round(v, 2) for k, v in sorted(w.items(), key=lambda kv: -abs(kv[1])) if abs(v) >= 0.05})
    P['blind']['labels']['club']['near'] = 'Near Sacramento'
    (root / 'scripts' / 'affinity' / 'params.json').write_text(json.dumps(P, indent=1, ensure_ascii=False))
    print('weights:', P['favs']['weights'])
    print('top:', ', '.join(f'{n} {v[0]}' for n, v in sorted(S.items(), key=lambda kv: -kv[1][0])[:15]))

if __name__ == '__main__':
    main()
