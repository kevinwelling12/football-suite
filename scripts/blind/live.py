"""Live Affinity from the blind model (Kevin, 2026-10-12: "ship the blind model. It's probably less biased.").

  python3 scripts/blind/live.py                 # score with scripts/blind/answers/kevin.json, write data/ for the app
  python3 scripts/build.py

Affinity = the blind test's score: each fact (coded in coded/*.json, scaled 0-1 by build.py) times the weight Kevin's
own test answers give it, placed between the lowest and highest score those weights allow (0-100). The weights come
from the same method as the test page (questions.js reads the questions from template.html): one-fact answers set a
starting weight (answer / 3), trade-off pairs adjust them by logistic regression pulled back toward those starts.
Retake the test, save the new answers to answers/kevin.json, and rerun this to update everything.
"""
import json, math, pathlib, re, subprocess, sys
here = pathlib.Path(__file__).resolve().parent
root = here.parents[1]
sys.path.insert(0, str(here))
import build

Q = json.loads(subprocess.check_output(['node', str(here / 'questions.js')]))
ANS = json.loads((here / 'answers' / 'kevin.json').read_text())['answers']

def weights(feats, prefix, pairs, pair_prefix, a=ANS):
    """Port of weights() in template.html: same start, same pairs, same learning rate and iterations."""
    w0 = {f[0]: (a.get(prefix + f[0]) / 3 if isinstance(a.get(prefix + f[0]), (int, float)) else 0.0) for f in feats}
    w = dict(w0); obs = []
    for i, (pa, pb) in enumerate(pairs):
        r = a.get(f'{pair_prefix}{i + 1}')
        if not isinstance(r, (int, float)): continue
        d = {}
        for k, v in pa: d[k] = d.get(k, 0) + v
        for k, v in pb: d[k] = d.get(k, 0) - v
        obs.append((d, (r + 2) / 4))
    K, LAM, LR = 3, 0.5, 0.05
    for _ in range(2000):
        g = {k: 2 * LAM * (w[k] - w0[k]) for k in w}
        for d, y in obs:
            z = sum(w[k] * v for k, v in d.items()); p = 1 / (1 + math.exp(-K * z))
            for k, v in d.items(): g[k] += K * (p - y) * v
        for k in w: w[k] -= LR * g[k]
    return w

def turnoffs(w, feats, prefix, a=ANS):
    """A serious wrong costs more than one fact's worth: a fact answered "Turn-off" counts double and "Strong turn-off"
    triple (Kevin, 2026-10-12: "do all four"). Weight x (1 + strength beyond slight), only on negative weights."""
    out = dict(w)
    for f in feats:
        v = a.get(prefix + f[0])
        if isinstance(v, (int, float)) and v <= -2 and out[f[0]] < 0: out[f[0]] *= 1 + (-v - 1)
    return out

def haversine(a, b):
    t = math.radians; dl, dn = t(b[0] - a[0]), t(b[1] - a[1])
    h = math.sin(dl / 2) ** 2 + math.cos(t(a[0])) * math.cos(t(b[0])) * math.sin(dn / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))

def near(km):
    """Closeness on a log scale (Kevin, 2026-10-12): 1 at home, 0.64 at 110 km (Oakland from Sacramento), 0.36 at 800 km,
    0.13 across the US, about 0 in Europe. 1 - ln(1 + km/10) / ln(1 + 10000/10), floored at 0."""
    return max(0.0, 1 - math.log1p(km / 10) / math.log1p(1000))

def scorer(w):
    lo = sum(v for v in w.values() if v < 0); hi = sum(v for v in w.values() if v > 0); span = hi - lo
    def score(f):
        s = sum(w[k] * f.get(k, 0) for k in w)
        parts = sorted(((k, round(f.get(k, 0), 2), round(100 * w[k] * f.get(k, 0) / span, 1)) for k in w), key=lambda x: -abs(x[2]))
        return round(100 * (s - lo) / span, 1), [p for p in parts if abs(p[2]) >= 0.3]
    return score

def scores(fair=True, detail=False):
    """-> (clubs {name: score}, players {name: score}); with detail, also the parts and the inputs main() writes.
    fair=False reproduces the first shipped version (no gap fills, raw trophy counts, every fact at its own weight)."""
    build.FAIR = fair
    wc = weights(Q['CF'], 'c_', Q['CP'], 'cp'); wp = weights(Q['PF'], 'p_', Q['PP'], 'pp')
    if fair: wc, wp = turnoffs(wc, Q['CF'], 'c_'), turnoffs(wp, Q['PF'], 'p_')
    home = next((p for p in build.PLACES if p[0] == ANS.get('home')), None); nat = ANS.get('nation') or ''
    clubs, players = build.rows()
    sc, sp = scorer(wc), scorer(wp)
    S = {}
    for c in clubs:
        f = dict(c['f'])
        f['near'] = near(haversine(home[1:], c['ll'])) if home and c['ll'] else 0.0
        f['home'] = 1.0 if c['k'] == 'nation' and c['n'] == nat else 0.0
        S[c['n']] = sc(f)
    SP = {}
    for p in players:
        f = dict(p['f']); f['homenat'] = 1.0 if nat and p['nat'] == nat else 0.0
        SP[p['n']] = sp(f)
    if detail: return S, SP, players, wc, wp
    return {n: v[0] for n, v in S.items()}, {n: v[0] for n, v in SP.items()}

def main():
    S, SP, players, wc, wp = scores(True, detail=True)
    D = json.loads((root / 'data' / 'suite_data.json').read_text())
    X = json.loads((root / 'data' / 'nations_extra.json').read_text())
    for t in [t for c in D.values() for t in c['teams']] + X['teams'] + X.get('clubs', []):
        a, parts = S[t['name']]
        t['base'], t['bonus'] = a, 0
        t['hai'] = dict(blind=1, fx=parts)
        t.pop('bonus0', None)
        if 'region' in t and str(t['region']).startswith(('Heritage', 'Home nation', 'Hometown')): t.pop('region')
    (root / 'data' / 'suite_data.json').write_text(json.dumps(D, ensure_ascii=False, separators=(',', ':')))
    (root / 'data' / 'nations_extra.json').write_text(json.dumps(X, ensure_ascii=False, indent=1))

    # players: the research facts give clubs and the NWSL tag for the lists
    sys.path.insert(0, str(root / 'scripts' / 'affinity' / 'players'))
    import model as PM
    facts, _ = PM.load()
    NWSL = re.compile(r'thorns|kansas city current|orlando pride|washington spirit|north carolina courage|gotham|seattle reign|san diego wave|'
                      r'red stars|chicago stars|angel city|bay fc|utah royals|houston dash|racing louisville|denver summit|boston legacy', re.I)
    SIZE = {'ma': 75, 'mt': 75, 'wa': 30, 'wt': 30}; L = {k: [] for k in SIZE}
    rated = []
    for p in players:
        a, parts = SP[p['n']]; fa = facts.get(p['n'], {})
        clubs_ = []
        for c in sorted(fa.get('clubs', []), key=lambda c: c.get('from') or 0):
            if c.get('club') and c['club'] not in clubs_ and not re.search(r'\b(II|B|U\d+|youth|academy)\b', c['club'], re.I): clubs_.append(c['club'])
        e = dict(n=p['n'], a=a, nat=p['nat'], pos=p['pos'], clubs=clubs_[-2:], fx=parts[:8],
                 nw=next((c['club'] for c in fa.get('clubs', []) if not c.get('to') and NWSL.search(c.get('club') or '')), None))
        rated.append((p, e))
    rated.sort(key=lambda x: -x[1]['a'])
    for p, e in rated:
        g = 'w' if p['g'] == 'W' else 'm'
        if len(L[g + 't']) < SIZE[g + 't']: L[g + 't'].append(e)
        if p['a'] and len(L[g + 'a']) < SIZE[g + 'a']: L[g + 'a'].append(e)
    (root / 'data' / 'players.json').write_text(json.dumps(L, ensure_ascii=False, separators=(',', ':')))

    lab = lambda feats: {f[0]: f[2] for f in feats}
    P = json.loads((root / 'scripts' / 'affinity' / 'params.json').read_text())
    P['blind'] = dict(date='2026-10-12', club={lab(Q['CF'])[k]: round(v, 2) for k, v in sorted(wc.items(), key=lambda kv: -kv[1])},
                      player={lab(Q['PF'])[k]: round(v, 2) for k, v in sorted(wp.items(), key=lambda kv: -kv[1])},
                      labels=dict(club=lab(Q['CF']), player=lab(Q['PF'])))
    (root / 'scripts' / 'affinity' / 'params.json').write_text(json.dumps(P, indent=1, ensure_ascii=False))
    top = sorted(S.items(), key=lambda kv: -kv[1][0])[:8]
    print('scored', len(S), 'clubs and nations,', len(players), 'players; top:', ', '.join(f'{n} {s[0]}' for n, s in top))

if __name__ == '__main__':
    main()
