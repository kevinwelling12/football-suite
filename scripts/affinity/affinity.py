"""Affinity: one model for every club, women's club, nation and player (rebuild, 2026-10-09).

  python3 scripts/affinity/affinity.py          # score everything, write data/suite_data.json, nations_extra.json, players.json
  python3 scripts/affinity/fit.py               # refit params.json to Kevin's quiz answers and backtest it

How a score is made (the same four steps for everything):

  1. Character  Q = weighted average of the character factors x 10              (0-100)
                clubs and nations: Values, Culture, History, Team, Ownership; players: Character, Team player, Loyalty
  2. Hard lines Q+ = Q - hard x (sum of hard-line points), floored at 0          (no cap: several can take Q to 0)
  3. Performance R = recent record 0-10 x 10: a club's last 10 seasons, a nation's ranking and tournaments, a player's
                Greatness, Legacy and Joy to watch. Blended geometrically: A0 = 100 x (Q+/100)^(1-pi) x (R/100)^pi,
                so a weak side drags the total down. pi is small for teams (Kevin: winning matters little) and 0.4 for
                players ("all while delivering performances worthy of the highlight reels and the history books").
  4. Connection A = A0 + conn x (sum of connection items, capped) + roots
                connection: distance, Kevin's other teams, rival markets, linked clubs, brand pulls, club seasons (players);
                roots: hometown club, home nation, ancestry (nations).

Parameters live in params.json (fitted by fit.py); measurements come from inputs.py.
"""
import json, math, pathlib, sys
root = pathlib.Path(__file__).resolve().parents[2]
A = root / 'scripts' / 'affinity'
sys.path.insert(0, str(A))
import inputs as I

PARAMS = json.loads((A / 'params.json').read_text())
CLUB_F = ('V', 'C', 'H', 'T', 'O')
ROLE_F = ('CH', 'WK', 'LO')
PERF_F = ('AB', 'LE', 'ST')

# ---------------------------------------------------------------- the model
def character(f, w):
    return sum(w[k] * f[k] for k in w) / sum(w.values()) * 10

def blend(Q, hard_pts, R, pi, p=PARAMS):
    """Steps 2 and 3. R None -> neutral record."""
    q = max(0.0, min(100.0, Q - p['hard'] * hard_pts))
    r = 10 * max(p['perf_floor'], min(10.0, p['perf_neutral'] if R is None else R))
    if q <= 0: return 0.0, q
    return 100 * (q / 100) ** (1 - pi) * (r / 100) ** pi, q

def connect(items, p=PARAMS):
    raw = sum(v for _, v in items)
    return max(-p['conn_cap'], min(p['conn_cap'], p['conn'] * raw))

def club_score(f, hard, P, conn_items, roots, p=PARAMS, pi=None):
    Q = character(f, p['club_w'])
    a0, q = blend(Q, sum(x[2] for x in hard), P, p['club_pi'] if pi is None else pi, p)
    k = connect(conn_items, p)
    if q <= 0: return 0.0, dict(Q=round(Q, 1), Qh=0.0, A0=0.0, K=0.0)  # hard lines took everything: nothing left to connect
    return max(0.0, min(100.0, a0 + k + roots)), dict(Q=round(Q, 1), Qh=round(q, 1), A0=round(a0, 1), K=round(k, 1))

def player_score(f, hard, conn_items, p=PARAMS):
    Q = character(f, p['player_w'])
    R = sum(p['perf_w'][k] * f[k] for k in PERF_F) / sum(p['perf_w'].values())
    a0, q = blend(Q, sum(x[2] for x in hard), R, p['player_pi'], p)
    k = connect(conn_items, p)
    if q <= 0: return 0.0, dict(Q=round(Q, 1), Qh=0.0, R=round(R * 10, 1), A0=0.0, K=0.0)
    return max(0.0, min(100.0, a0 + k)), dict(Q=round(Q, 1), Qh=round(q, 1), R=round(R * 10, 1), A0=round(a0, 1), K=round(k, 1))

# ---------------------------------------------------------------- connection for players: the clubs they played for
def per_season(a):
    """Kevin, 2026-10-07: "base it solely on Affinity rating, not my stated favourites". 50 is neutral; up to +0.6 a
    season at 85+, down to -0.6 at 20 or below."""
    if a is None: return 0.0
    return min(0.6, 0.6 * (a - 50) / 35) if a >= 50 else max(-0.6, -0.3 * (50 - a) / 15)

def player_conn(pl, club_aff, club_aff_w):
    import re
    p = pl['facts']; women = p.get('gender') == 'W'; plus = minus = 0.0; best = []
    for c in p.get('clubs', []):
        n = ' '.join(I.PM.norm(c.get('club')))
        if 'ii' in n.split() or re.search(r'\b(u\d+|youth|academy|reserves)\b', n): continue
        a = lookup(c.get('club'), club_aff_w if women else club_aff)
        v = per_season(a) * I.PM.seasons(c)
        if v > 0: plus += v
        else: minus -= v
        if abs(v) >= 0.05: best.append((c.get('club'), v))
    items = []
    if plus: items.append(('Club seasons', round(min(plus, 4.0), 1)))
    if minus: items.append(('Seasons at clubs you rate low', -round(min(minus, 3.0), 1)))
    if (p.get('national') or {}).get('team') in ('USA', 'United States'): items.append(('US international', 2.0))
    return items

def lookup(name, T):
    n = ' '.join(I.PM.norm(name)); n = I.PM.ALIAS.get(n, n)
    if n in T: return T[n]
    hits = [v for c, v in T.items() if n and (c.startswith(n) or n.startswith(c)) and min(len(c), len(n)) >= 5]
    return hits[0] if len(hits) == 1 else None

# ---------------------------------------------------------------- run everything
def run(p=PARAMS, write=True):
    import interplay, association, players_link
    D = json.loads((root / 'data' / 'suite_data.json').read_text())
    X = json.loads((root / 'data' / 'nations_extra.json').read_text())
    comps = {}
    for key, comp in D.items():
        for t in comp['teams']: comps.setdefault(t['name'], []).append(key)
    nations = {t['name'] for t in D['unl']['teams']} | {t['name'] for t in X['teams']}
    clubs = [n for n in comps if n not in nations] + [t['name'] for t in X.get('clubs', [])]

    # players first, without connection (their clubs aren't scored yet; connection is added at the end)
    PL = I.players()
    for n, pl in PL.items():
        pl['a_nc'], _ = player_score(pl['factors'], pl['hard'], [], p)
    bumps = players_link.bumps(D, {n: (pl['a_nc'], pl['facts']) for n, pl in PL.items()})
    dom = interplay.domestic({n: I.perf.primary(cs) for n, cs in comps.items() if n not in nations})

    # clubs
    R = {}
    for n in clubs:
        f, hard, notes = I.club_measures(n)
        f0 = dict(f); sub = {}
        if n in dom:
            b, sh, m = dom[n]; f['T'] = round(min(10, max(0, f['T'] + b)), 1); sub['dom'] = [b, sh, m]
        if n in bumps:
            b = bumps[n]; t1 = round(min(10, max(0, f['T'] + b['team'])), 1); h1 = round(min(10, max(0, f['H'] + b['hist'])), 1)
            sub['py'] = dict(t=round(t1 - f['T'], 2), h=round(h1 - f['H'], 2), sq=[x for x, _ in b['squad'][:3]], ic=[x for x, _ in b['icons'][:3]])
            f['T'], f['H'] = t1, h1
        P = I.club_perf(n, comps.get(n))
        conn = I.club_conn(n)
        roots = (('Hometown', p['home_club']) if n == I.HOMETOWN else None)
        R[n] = dict(f=f, f0=f0, sub=sub, hard=hard, notes=notes, P=P, conn=conn, roots=roots)
    def score_club(n, extra=()):
        r = R[n]
        return club_score(r['f'], r['hard'], r['P']['P'] if r['P'] else None, list(r['conn']) + list(extra),
                          r['roots'][1] if r['roots'] else 0, p)
    pre = {n: score_club(n)[0] for n in clubs}
    links = association.pulls(pre, set())
    for n in clubs:
        if n in links: R[n]['conn'] = list(R[n]['conn']) + [(f'Linked to {y}', v) for y, v in links[n][1]]
        R[n]['A'], R[n]['parts'] = score_club(n)

    # nations: squads at clubs Kevin rates (Team), recent record, ancestry and home
    club_aff = {n: R[n]['A'] for n in clubs}
    NL = interplay.nation_links(club_aff, nations)
    for n in nations:
        f, hard, notes = I.club_measures(n); f0 = dict(f); sub = {}
        if n in NL:
            b, top = NL[n]; f['T'] = round(min(10, max(0, f['T'] + b)), 1); sub['clubs'] = [[c, k, v] for c, k, v in top]; sub['tb'] = b
        P = I.nation_perf(n)
        if n == I.HOME_NATION: roots = ('Home nation', p['home_nation'])
        elif I.HERITAGE.get(n): roots = ('Heritage', round(min(p['heritage_cap'], p['heritage_per_pct'] * I.HERITAGE[n]), 1))
        else: roots = None
        R[n] = dict(f=f, f0=f0, sub=sub, hard=hard, notes=notes, P=P, conn=[], roots=roots, nation=True)
        R[n]['A'], R[n]['parts'] = club_score(f, hard, P['P'] if P else None, [], roots[1] if roots else 0, p)

    # players: connection from the clubs just scored
    CA, CW = {}, {}
    for key, comp in D.items():
        if key == 'unl': continue
        for t in comp['teams']:
            for nm in {t['name'], t.get('short') or t['name']}: (CW if key == 'nwsl' else CA).setdefault(' '.join(I.PM.norm(nm)), R[t['name']]['A'])
    for n, pl in PL.items():
        pl['conn'] = player_conn(pl, CA, CW)
        pl['A'], pl['parts'] = player_score(pl['factors'], pl['hard'], pl['conn'], p)
    if write: write_out(D, X, R, PL, p)
    return R, PL

# ---------------------------------------------------------------- outputs (shapes the app reads)
def hai(r, p):
    f = r['f']; parts = r['parts']
    h = dict(C=f['C'], V=f['V'], H=f['H'], O=f['O'], S=f['T'], Q=parts['Q'], A0=parts['A0'],
             hard=[[l, -round(p['hard'] * x, 1)] for _, l, x in r['hard']],
             conn=[[l, round(v, 1)] for l, v in r['conn'] if round(v, 1)], K=parts['K'])
    if r['f0']['T'] != f['T']: h['S0'] = r['f0']['T']
    if r['f0']['H'] != f['H']: h['H0'] = r['f0']['H']
    if r['P']:
        h['P'] = r['P']['P']
        for k in ('ps', 'pl', 'rank', 'wc2026', 'cont'):
            if r['P'].get(k) is not None: h[k] = r['P'][k]
    if 'dom' in r['sub']: h['tb'], h['dom'] = r['sub']['dom'][0], r['sub']['dom'][1:]
    if 'py' in r['sub']: h['py'] = r['sub']['py']
    if 'clubs' in r['sub']: h['tb'], h['clubs'] = r['sub']['tb'], r['sub']['clubs']
    if r['notes']: h['notes'] = r['notes']
    return h

def write_out(D, X, R, PL, p):
    for key, comp in D.items():
        for t in comp['teams']:
            r = R.get(t['name'])
            if not r: continue
            bonus = r['roots'][1] if r['roots'] else 0
            t['base'] = round(r['A'] - bonus, 1); t['bonus'] = bonus
            if key == 'unl' and r['roots']: t['region'] = r['roots'][0]
            t['hai'] = hai(r, p)
            t.pop('bonus0', None)
    for t in X['teams'] + X.get('clubs', []):
        r = R[t['name']]; bonus = r['roots'][1] if r['roots'] else 0
        t['base'] = round(r['A'] - bonus, 1); t['bonus'] = bonus; t['hai'] = hai(r, p)
        if r['roots'] and r.get('nation'): t['region'] = r['roots'][0]
    (root / 'data' / 'suite_data.json').write_text(json.dumps(D, ensure_ascii=False, separators=(',', ':')))
    (root / 'data' / 'nations_extra.json').write_text(json.dumps(X, ensure_ascii=False, indent=1))
    write_players(PL, p)

def write_players(PL, p):
    import re
    NWSL = re.compile(r'thorns|kansas city current|orlando pride|washington spirit|north carolina courage|gotham|seattle reign|san diego wave|'
                      r'red stars|chicago stars|angel city|bay fc|utah royals|houston dash|racing louisville|denver summit|boston legacy', re.I)
    SIZE = {'ma': 75, 'mt': 75, 'wa': 30, 'wt': 30}
    L = {k: [] for k in SIZE}
    ratings = []
    for n, pl in sorted(PL.items(), key=lambda kv: -kv[1]['A']):
        f = pl['facts']; s = pl['scores']
        clubs = []
        for c in sorted(f.get('clubs', []), key=lambda c: c.get('from') or 0):
            if c.get('club') and c['club'] not in clubs and not re.search(r'\b(II|B|U\d+|youth|academy)\b', c['club'], re.I): clubs.append(c['club'])
        e = dict(n=n, a=round(pl['A'], 1), f=[s[k] for k in ('CH', 'WK', 'LO', 'AB', 'ST', 'LE')], c=pl['parts']['K'],
                 p=-round(p['hard'] * sum(x[2] for x in pl['hard']), 1), rm=pl['parts']['Qh'], pf=pl['parts']['R'],
                 nat=(f.get('national') or {}).get('team') or f.get('nation'), pos='/'.join(f.get('positions') or []), clubs=clubs[-2:],
                 why=re.sub(r'\(?\banchors?\b\)?\s*', '', s.get('why', ''))[:240],
                 pen=[f"{l}: {w}"[:90] for _, l, _, w in pl['hard']][:3],
                 nw=next((c['club'] for c in f.get('clubs', []) if not c.get('to') and NWSL.search(c.get('club') or '')), None))
        g = 'w' if pl['gender'] in ('F', 'female', 'w', 'W') else 'm'
        for k in ((g + 'a', g + 't') if pl['active'] else (g + 't',)):
            if len(L[k]) < SIZE[k]: L[k].append(e)
        ratings.append(dict(name=n, gender=pl['gender'], active=pl['active'], aff=round(pl['A'], 1), **pl['parts'],
                            conn=pl['conn'], hard=[[l, x] for _, l, x, _ in pl['hard']]))
    (root / 'data' / 'players.json').write_text(json.dumps(L, ensure_ascii=False, separators=(',', ':')))
    (A / 'players' / 'ratings.json').write_text(json.dumps(ratings, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    R, PL = run()
    top = sorted(R.items(), key=lambda kv: -kv[1]['A'])[:10]
    print('scored', len(R), 'clubs and nations,', len(PL), 'players')
    print('top:', ', '.join(f"{n} {r['A']:.1f}" for n, r in top))
