"""Player -> club influence (Kevin, 2026-10-07: "full integration of the player and club sides with bilateral influence").

Club -> player already exists: a player's connection is the Affinity of each club he played for (players/model.py).
Player -> club, here: each club's Team factor moves with its current squad and its History factor with its icons,
by Kevin's Player Affinity for them. No echo: the player score used here leaves out connection (the part that comes
from the clubs), so the two sides never feed back into each other and one pass each is exact.

- Squad (Team, slot S): every current player in the pool, x = (A - 60) / 15 clipped to +/-1, A = Player Affinity
  without connection. bump = 1.5 * sum(x) / (n + 4), so one or two players move a club a little and a full squad up
  to +/-1.5 (the +4 is a prior of four neutral players). Only a club's best 5 count: the pool covers Kevin's clubs
  down to the third keeper but other clubs only through their stars, so comparing whole squads would punish the clubs
  researched most deeply. Best 5 against best 5 is fair to both.
- Icons (History, slot H): former players who spent 4+ seasons there, best 5, same x, bump = 1.0 * sum(x) / (n + 3), +/-1.
Women play for NWSL sides only in the tracker; a woman's European club has no women's rating, so it is skipped.

Usage (normally via scripts/affinity/unified.py): import players_link; players_link.bumps(D) -> {team: dict}
"""
import json, pathlib, sys
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here / 'players')); import model as M
NEUTRAL, SPREAD, TOP = 60.0, 15.0, 5

def _resolver(D):
    men, women = {}, {}
    for k, L in D.items():
        if k == 'unl': continue
        for t in L['teams']:
            for n in {t['name'], t.get('short') or t['name']}: (women if k == 'nwsl' else men).setdefault(' '.join(M.norm(n)), t['name'])
    def find(club, w):
        T = women if w else men
        n = ' '.join(M.norm(club)); n = M.ALIAS.get(n, n)
        if n in T: return T[n]
        hits = {v for c, v in T.items() if n and (c.startswith(n) or n.startswith(c)) and min(len(c), len(n)) >= 5}
        return hits.pop() if len(hits) == 1 else None
    return find

def scores():
    """name -> (Player Affinity without connection, facts)"""
    facts, sc = M.load()
    out = {}
    for n, p in facts.items():
        if n not in sc: continue
        r = M.rate(p, sc[n])
        out[n] = (max(0.0, min(100.0, r['base'] + r['pen'] + r['pos'])), p)
    return out

def bumps(D):
    find, S = _resolver(D), scores()
    squad, icons = {}, {}
    for n, (a, p) in S.items():
        w = p.get('gender') == 'W'
        for c in p.get('clubs', []):
            team = find(c.get('club') or '', w)
            if not team: continue
            if p.get('active') and not c.get('to'): squad.setdefault(team, {})[n] = a
            elif M.seasons(c) >= 4: icons.setdefault(team, {})[n] = a
    x = lambda a: max(-1.0, min(1.0, (a - NEUTRAL) / SPREAD))
    out = {}
    for team in set(squad) | set(icons):
        top = lambda d: sorted(d.items(), key=lambda t: -t[1])[:TOP]
        sq, ic = top(squad.get(team, {})), top(icons.get(team, {}))
        tb = 1.5 * sum(x(a) for _, a in sq) / (len(sq) + 4) if sq else 0.0
        hb = 1.0 * sum(x(a) for _, a in ic) / (len(ic) + 3) if ic else 0.0
        out[team] = dict(team=round(tb, 2), hist=round(hb, 2),
                         squad=[[n, round(a, 1)] for n, a in sq], icons=[[n, round(a, 1)] for n, a in ic])
    return out

if __name__ == '__main__':
    D = json.loads((here.parents[1] / 'data' / 'suite_data.json').read_text())
    B = bumps(D)
    for t, b in sorted(B.items(), key=lambda kv: -(abs(kv[1]['team']) + abs(kv[1]['hist'])))[:25]:
        print(f"{t:28s} team {b['team']:+.2f} ({len(b['squad'])} shown) hist {b['hist']:+.2f}  {[s[0] for s in b['squad'][:3]]} | {[s[0] for s in b['icons'][:3]]}")
    print(len(B), 'clubs touched')
