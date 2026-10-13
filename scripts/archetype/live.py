"""Affinity from an archetype: the perfect club you'd get by combining the best of Kevin's clubs (2026-10-12).

  python3 scripts/archetype/live.py    # writes data/suite_data.json, data/players.json, params.json "favs"; then build

Kevin: "base the rating on an archetypically perfect club that would result from combining the best qualities of the named
clubs, focusing most on the traits they share." Traits (BRIEF.md) are scored 0-10 for every club by research (out/*.json),
plus geography (near Sacramento). Each trait's weight is how many of Kevin's clubs have it strongly (7 or more of 10), so
traits all five share count five times one only a single club has. Below the weakest of his clubs on any trait
costs as if all five shared it (the shared floor). The archetype scores 10 on every trait: a club's
Affinity is 100 x its weighted trait average / 10. Kevin's clubs then sit at the top of their leagues (PRIORITY).
Players: half the seasons-weighted Affinity of their clubs, half character (as before).
"""
import json, math, pathlib, sys, glob
here = pathlib.Path(__file__).resolve().parent
root = here.parents[1]
import importlib.util
_spec = importlib.util.spec_from_file_location('favs_live', root / 'scripts' / 'favs' / 'live.py')
favs = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(favs)   # lift(), players, character rule

CHOSEN = ['Liverpool', 'Borussia Dortmund', 'Portland Timbers', 'Portland Thorns', 'Sacramento Republic FC']
TRAITS = ['terrace', 'city', 'voice', 'conscience', 'ground', 'contender', 'rituals', 'stewardship', 'women', 'intensity', 'geography']
LABEL = dict(terrace='Iconic singing end', city="The city's club", voice='Supporters have a say', conscience='Inclusive fan culture',
             ground='Great home ground', contender='Contender', rituals='Rituals and tifo', stewardship='Run for the club',
             women="Women's side", intensity='High-energy football', geography='Near Sacramento')
HOME = (38.58, -121.49)
STRONG = 7

def km(a, b):
    t = math.radians; dl, dn = t(b[0] - a[0]), t(b[1] - a[1])
    h = math.sin(dl / 2) ** 2 + math.cos(t(a[0])) * math.cos(t(b[0])) * math.sin(dn / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))

def geography(ll):
    """10 within 150 km of Sacramento, 7 on the West Coast (1,200 km), 4 elsewhere in North America (5,000 km), 0 overseas."""
    if not ll: return 0
    d = km(HOME, ll)
    return 10 if d <= 150 else 7 if d <= 1200 else 4 if d <= 5000 else 0

def traits():
    T = {}
    for f in sorted(glob.glob(str(here / 'out' / '*.json'))): T.update(json.load(open(f)))
    ll = {c['name']: (c['lat'], c['lon']) if c.get('lat') is not None else None
          for f in glob.glob(str(root / 'scripts' / 'blind' / 'coded' / 'clubs_*.json')) for c in json.load(open(f))}
    for n, t in T.items(): t['geography'] = geography(ll.get(n))
    return T

def model():
    T = traits()
    w = {k: sum(1 for c in CHOSEN if (T[c].get(k) or 0) >= STRONG) for k in TRAITS}
    W = sum(w.values())
    # Shared floor (Kevin, 2026-10-12): on every trait, falling below the weakest of his clubs costs as if all five shared
    # it (weight 5). None of his clubs is state, oligarch or private-equity owned, so that now costs heavily.
    floor = {k: min(T[c].get(k) or 0 for c in CHOSEN) for k in TRAITS}
    S = {}
    for n, t in T.items():
        parts = [(k, round((t.get(k) or 0) / 10, 2), round(100 * w[k] * (t.get(k) or 0) / 10 / W, 1)) for k in TRAITS if w[k]]
        parts += [('below_' + k, round((t.get(k) or 0) / 10, 2), -round(100 * len(CHOSEN) * (floor[k] - (t.get(k) or 0)) / 10 / W, 1))
                  for k in TRAITS if (t.get(k) or 0) < floor[k]]
        S[n] = (round(max(0.0, sum(p[2] for p in parts)), 1), sorted(parts, key=lambda p: -p[2]))
    return S, w, T

if __name__ == '__main__':
    S, w, T = model()
    favs.CHOSEN = CHOSEN
    favs.model = lambda: (S, w)            # reuse favs' writer: lift to top of league, players, params
    favs.LABEL = LABEL
    favs.main()
    P = json.loads((root / 'scripts' / 'affinity' / 'params.json').read_text())
    P['favs'] = dict(date='2026-10-12', model='archetype', chosen=CHOSEN,
                     weights={LABEL[k]: v for k, v in sorted(w.items(), key=lambda kv: -kv[1]) if v})
    P['blind']['labels']['club'] = {**LABEL, **{'below_' + k: f'{v}: below all your clubs' for k, v in LABEL.items()}}
    (root / 'scripts' / 'affinity' / 'params.json').write_text(json.dumps(P, indent=1, ensure_ascii=False))
    print('weights (clubs of 5 with the trait):', {LABEL[k]: v for k, v in w.items()})
    for c in CHOSEN: print(' ', c, S[c][0], {k: T[c].get(k) for k in TRAITS})
