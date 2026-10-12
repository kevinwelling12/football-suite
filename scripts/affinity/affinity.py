"""Affinity: one model for every club, women's club, nation and player (rebuilt 2026-10-09, categories only 2026-10-12).

  python3 scripts/affinity/affinity.py          # score everything, write data/suite_data.json, nations_extra.json, players.json
  python3 scripts/affinity/fit.py               # refit the weights to Kevin's quiz answers and backtest them

One step: Affinity = 10 x the weighted average of eight ratings out of 10 (weights in params.json, fitted by fit.py).
  clubs and nations  Values, Culture, History, Team, Ownership, Integrity, Record, Connection
  players            Character, Team player, Loyalty, Greatness, Legacy, Joy to watch, Integrity, Connection
Integrity is 10 for a clean record, docked by documented wrongs (inputs.py). Record is the track record (a club's last
10 seasons, a nation's ranking and tournaments; 5 when not judged). Connection is 5 when there is none, moved by
k_per_point per connection point (distance, Kevin's other teams, rival markets, linked clubs, a player's clubs) and roots
(hometown, home nation, ancestry), within 0-10. No penalties or bonuses outside the ratings (Kevin, 2026-10-12: "I want
the ratings to live entirely within the categories and their weights").

Measurements come from inputs.py.
"""
import json, math, pathlib, sys
root = pathlib.Path(__file__).resolve().parents[2]
A = root / 'scripts' / 'affinity'
sys.path.insert(0, str(A))
import inputs as I

PARAMS = json.loads((A / 'params.json').read_text())
NOW_YEAR = 2026
CLUB_F = ('V', 'C', 'H', 'T', 'O', 'I', 'R', 'K')
PLAYER_F = ('CH', 'WK', 'LO', 'AB', 'LE', 'ST', 'I', 'K')

# ---------------------------------------------------------------- the model
def weighted(f, w):
    return sum(w[k] * f[k] for k in w) / sum(w.values()) * 10

def connection(items, roots=0.0, p=PARAMS):
    """Connection out of 10: 5 = none; each point of connection items (capped) and roots moves it k_per_point."""
    raw = max(-p['conn_cap'], min(p['conn_cap'], sum(v for _, v in items)))
    return round(max(0.0, min(10.0, 5 + p['k_per_point'] * (raw + roots))), 2)

def record(P, p=PARAMS):
    return p['record_neutral'] if P is None else max(0.0, min(10.0, P))

def club_score(f, P, conn_items, roots, p=PARAMS):
    g = dict(f, R=record(P, p), K=connection(conn_items, roots, p))
    return max(0.0, min(100.0, weighted(g, p['club_w']))), g

def player_score(f, conn_items, p=PARAMS, roots=0):
    g = dict(f, K=connection(conn_items, roots, p))
    return max(0.0, min(100.0, weighted(g, p['player_w']))), g

# ---------------------------------------------------------------- connection for players: the clubs they played for
def per_season(a):
    """Kevin, 2026-10-07: "base it solely on Affinity rating, not my stated favourites". 66 is neutral; up to +0.6 a
    season at 86+, down to -0.6 at 48 or below (the old 50 / 85 / 20 on the one-step scale, 2026-10-12)."""
    if a is None: return 0.0
    return min(0.6, 0.6 * (a - 66) / 20) if a >= 66 else max(-0.6, -0.3 * (66 - a) / 9)

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
        pl['a_nc'], _ = player_score(pl['factors'], [], p)
    bumps = players_link.bumps(D, {n: (pl['a_nc'], pl['facts']) for n, pl in PL.items()})
    dom = interplay.domestic({n: I.perf.primary(cs) for n, cs in comps.items() if n not in nations})

    # clubs
    R = {}
    for n in clubs:
        f, items, notes = I.club_measures(n)
        f0 = dict(f); sub = {}
        if n in dom:
            b, sh, m = dom[n]; f['T'] = round(min(10, max(0, f['T'] + b)), 1); sub['dom'] = [b, sh, m]
        if n in bumps:
            b = bumps[n]; t1 = round(min(10, max(0, f['T'] + b['team'])), 1); h1 = round(min(10, max(0, f['H'] + b['hist'])), 1)
            sub['py'] = dict(t=round(t1 - f['T'], 2), h=round(h1 - f['H'], 2), sq=[x for x, _ in b['squad'][:3]], ic=[x for x, _ in b['icons'][:3]])
            f['T'], f['H'] = t1, h1
        P = I.club_perf(n, comps.get(n))
        conn = I.club_conn(n)
        rg = I.CLUB_REGION.get(n)
        roots = (('Hometown', p['home_club']) if n == I.HOMETOWN else
                 (f'Heritage: {rg} {I.REGION_PCT[rg]}%', round(min(p['club_heritage_cap'], p['club_heritage_per_pct'] * I.REGION_PCT[rg]), 1)) if rg else None)
        R[n] = dict(f=f, f0=f0, sub=sub, items=items, notes=notes, P=P, conn=conn, roots=roots)
    def score_club(n, extra=()):
        r = R[n]
        return club_score(r['f'], r['P']['P'] if r['P'] else None, list(r['conn']) + list(extra), r['roots'][1] if r['roots'] else 0, p)
    pre = {n: score_club(n)[0] for n in clubs}
    links = association.pulls(pre, set())
    for n in clubs:
        if n in links: R[n]['conn'] = list(R[n]['conn']) + [(f'Linked to {y}', v) for y, v in links[n][1]]
        R[n]['A'], R[n]['parts'] = score_club(n)

    # nations: squads at clubs Kevin rates (Team), recent record, ancestry and home
    club_aff = {n: R[n]['A'] for n in clubs}
    NL = interplay.nation_links(club_aff, nations)
    for n in nations:
        f, items, notes = I.club_measures(n); f0 = dict(f); sub = {}
        if n in NL:
            b, top = NL[n]; f['T'] = round(min(10, max(0, f['T'] + b)), 1); sub['clubs'] = [[c, k, v] for c, k, v in top]; sub['tb'] = b
        P = I.nation_perf(n)
        if n == I.HOME_NATION: roots = ('Home nation', p['home_nation'])
        elif I.HERITAGE.get(n): roots = ('Heritage', round(min(p['heritage_cap'], p['heritage_per_pct'] * I.HERITAGE[n]), 1))
        else: roots = None
        R[n] = dict(f=f, f0=f0, sub=sub, items=items, notes=notes, P=P, conn=[], roots=roots, nation=True)
        R[n]['A'], R[n]['parts'] = club_score(f, P['P'] if P else None, [], roots[1] if roots else 0, p)

    # players: connection from the clubs just scored
    CA, CW = {}, {}
    for key, comp in D.items():
        if key == 'unl': continue
        for t in comp['teams']:
            for nm in {t['name'], t.get('short') or t['name']}: (CW if key == 'nwsl' else CA).setdefault(' '.join(I.PM.norm(nm)), R[t['name']]['A'])
    for n, pl in PL.items():
        pl['conn'] = player_conn(pl, CA, CW)
        nat = (pl['facts'].get('national') or {}).get('team') or pl['facts'].get('nation')
        sh = I.nation_share(nat)
        if nat in ('USA', I.HOME_NATION): pl['roots'] = ('Home nation: United States', p['player_home_nation'])   # Kevin, 2026-10-12: level with England
        else: pl['roots'] = (f'Heritage: {nat} {round(sh) if sh >= 1 else round(sh, 1)}%', round(min(p['player_heritage_cap'], p['player_heritage_per_pct'] * sh), 1)) if sh else None
        pl['A'], pl['parts'] = player_score(pl['factors'], pl['conn'], p, pl['roots'][1] if pl['roots'] else 0)
    if write: write_out(D, X, R, PL, p)
    return R, PL

# ---------------------------------------------------------------- outputs (shapes the app reads)
def roots_gain(r, p):
    """Affinity points that roots (hometown, home nation, ancestry) add through Connection: shown apart in the lists."""
    if not r['roots']: return 0.0
    g = r['parts']; w = p['club_w']
    k0 = connection(r['conn'], 0, p)
    return round(w['K'] * (g['K'] - k0) / sum(w.values()) * 10, 1)

def hai(r, p):
    g = r['parts']
    h = dict(C=g['C'], V=g['V'], H=g['H'], O=g['O'], S=g['T'], I=g['I'], R=g['R'], K=g['K'],
             items=[[l, -x] for l, x in r['items']], conn=[[l, round(v, 1)] for l, v in r['conn'] if round(v, 1)])
    if r['roots']: h['roots'] = [r['roots'][0], r['roots'][1]]
    if r['f0']['T'] != g['T']: h['S0'] = r['f0']['T']
    if r['f0']['H'] != g['H']: h['H0'] = r['f0']['H']
    if r['P']:
        h['P'] = r['P']['P']
        for k in ('ps', 'pl', 'rank', 'wc2026', 'cont'):
            if r['P'].get(k) is not None: h[k] = r['P'][k]
    if 'dom' in r['sub']: h['tb'], h['dom'] = r['sub']['dom'][0], r['sub']['dom'][1:]
    if 'py' in r['sub']: h['py'] = r['sub']['py']
    if 'clubs' in r['sub']: h['tb'], h['clubs'] = r['sub']['tb'], r['sub']['clubs']
    if r['notes']: h['notes'] = r['notes']
    if r['roots'] and not r.get('nation'): h['rl'] = r['roots'][0]
    return h

def write_out(D, X, R, PL, p):
    for key, comp in D.items():
        for t in comp['teams']:
            r = R.get(t['name'])
            if not r: continue
            bonus = roots_gain(r, p)   # 'bonus' = what roots add (drawn apart in the lists); base + bonus = Affinity
            t['base'] = round(r['A'] - bonus, 1); t['bonus'] = bonus
            if key == 'unl' and r['roots']: t['region'] = r['roots'][0]
            t['hai'] = hai(r, p)
            t.pop('bonus0', None)
    for t in X['teams'] + X.get('clubs', []):
        r = R[t['name']]; bonus = roots_gain(r, p)
        t['base'] = round(r['A'] - bonus, 1); t['bonus'] = bonus; t['hai'] = hai(r, p)
        if r['roots'] and r.get('nation'): t['region'] = r['roots'][0]
    (root / 'data' / 'suite_data.json').write_text(json.dumps(D, ensure_ascii=False, separators=(',', ':')))
    (root / 'data' / 'nations_extra.json').write_text(json.dumps(X, ensure_ascii=False, indent=1))
    write_players(PL, p)

def runway(f, p=PARAMS):
    """Years ahead at the top level, for the active lists only (Kevin, 2026-10-12: "I want to find players I'll be able to
    follow for years to come at the top level"). +max at age_full or younger, 0 at age_zero, -max by age_full + 2 x
    (age_zero - age_full); goalkeepers count gk_shift years younger. All-time lists and Affinity itself are unchanged."""
    r = p.get('runway', {}); born = f.get('born')
    if not born or not r: return 0.0
    age = NOW_YEAR - born - (r.get('gk_shift', 3) if 'GK' in (f.get('positions') or []) else 0)
    mx, a0, az = r.get('max', 4), r.get('age_full', 22), r.get('age_zero', 28.5)
    return round(max(-mx, min(mx, mx * (az - age) / (az - a0))), 1)

def write_players(PL, p):
    import re
    NWSL = re.compile(r'thorns|kansas city current|orlando pride|washington spirit|north carolina courage|gotham|seattle reign|san diego wave|'
                      r'red stars|chicago stars|angel city|bay fc|utah royals|houston dash|racing louisville|denver summit|boston legacy', re.I)
    SIZE = {'ma': 75, 'mt': 75, 'wa': 30, 'wt': 30}
    L = {k: [] for k in SIZE}
    ratings = []; act = {}
    for n, pl in sorted(PL.items(), key=lambda kv: -kv[1]['A']):
        f = pl['facts']; s = pl['scores']
        clubs = []
        for c in sorted(f.get('clubs', []), key=lambda c: c.get('from') or 0):
            if c.get('club') and c['club'] not in clubs and not re.search(r'\b(II|B|U\d+|youth|academy)\b', c['club'], re.I): clubs.append(c['club'])
        gp = pl['parts']
        e = dict(n=n, a=round(pl['A'], 1), f=[round(gp[k], 1) for k in ('CH', 'WK', 'LO', 'AB', 'ST', 'LE', 'I', 'K')],
                 nat=(f.get('national') or {}).get('team') or f.get('nation'), pos='/'.join(f.get('positions') or []), clubs=clubs[-2:],
                 why=re.sub(r'\(?\banchors?\b\)?\s*', '', s.get('why', ''))[:240],
                 pen=[[f"{l}: {w}"[:90], -x] for _, l, x, w in pl['items']][:4], cn=[[l, v] for l, v in pl['conn']],
                 nw=next((c['club'] for c in f.get('clubs', []) if not c.get('to') and NWSL.search(c.get('club') or '')), None))
        if pl.get('roots'): e['h'] = pl['roots'][1]; e['hl'] = pl['roots'][0]
        if s.get('CH_values'): e['cv'] = s['CH_values']
        g = 'w' if pl['gender'] in ('F', 'female', 'w', 'W') else 'm'
        if len(L[g + 't']) < SIZE[g + 't']: L[g + 't'].append(e)
        if pl['active']:   # the active lists rank by Affinity plus the years ahead at the top level
            ya = runway(f, p) if pl['A'] > 0 else 0.0
            act.setdefault(g + 'a', []).append(dict(e, a=round(pl['A'] + ya, 1), aff=round(pl['A'], 1), ya=ya))
        ratings.append(dict(name=n, gender=pl['gender'], active=pl['active'], aff=round(pl['A'], 1), **{k: round(v, 2) for k, v in gp.items()},
                            conn=pl['conn'], integrity=[[l, x] for _, l, x, _ in pl['items']], roots=pl.get('roots')))
    for k, xs in act.items(): L[k] = sorted(xs, key=lambda e: -e['a'])[:SIZE[k]]
    (root / 'data' / 'players.json').write_text(json.dumps(L, ensure_ascii=False, separators=(',', ':')))
    (A / 'players' / 'ratings.json').write_text(json.dumps(ratings, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    R, PL = run()
    top = sorted(R.items(), key=lambda kv: -kv[1]['A'])[:10]
    print('scored', len(R), 'clubs and nations,', len(PL), 'players')
    print('top:', ', '.join(f"{n} {r['A']:.1f}" for n, r in top))
