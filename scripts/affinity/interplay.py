"""Squad interplay: a small additive bump (up to +/-2) on the Team factor, from who plays where.

Nations (club link): national-team squads at the 20 tournaments since 2016 (research/squads.json, parsed from
Wikipedia by interplay/parse_squads.py). Each player counts by how Kevin rates his club: clubs above 63 Affinity
count up to +1 (at 90), clubs below 35 down to -1 (at 15), everything between is neutral; captains count 1.5x.
Per squad the sum is scaled to 23 players; squads are averaged with a 4-year half-life (like the track record).
bump = link / 3, capped at +/-2. Liverpool's four Dutch internationals (van Dijk captain) lift the Netherlands.

Clubs (homegrown share): share of the squad eligible for the club's own national team, current squad plus every
other season back to 2016 (research/domestic.json, from Wikipedia squad lists by interplay/parse_domestic.py),
4-season half-life. Compared with the club's own league (z-score): bump = 0.8 * z, capped at +/-2, and scaled down
when few seasons are known (full at a recency weight of 2, e.g. the current squad plus one season). Welsh clubs count
English players as domestic, Canadian clubs American ones. Athletic Club (Basque players only) is near the top.
"""
import json, math, re, unicodedata, collections, pathlib
root = pathlib.Path(__file__).resolve().parents[2]
RES = root / 'scripts' / 'affinity' / 'research'
HALF = 4.0
ALIAS = {'Brighton & Hove Albion F.C.': 'Brighton', 'Athletic Bilbao': 'Athletic Club', 'Los Angeles FC': 'Los Angeles Football Club',
         'New York City FC': 'New York City Football Club', 'New York Red Bulls': 'Red Bull New York'}
SKIP = {'Barcelona S.C.', 'Juventus Next Gen', 'New York Red Bulls II'}
def _norm(s): return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower())

def g(aff):
    return min(1.0, (aff - 63) / 27) if aff > 63 else max(-1.0, (aff - 35) / 20) if aff < 35 else 0.0

def nation_links(aff, nations):
    """aff: club -> Affinity. -> {nation: (bump, [(club, players, contribution), ...] top contributors)}"""
    f = RES / 'squads.json'
    if not f.exists(): return {}
    N = {_norm(n): n for n in aff}
    def club(r):
        if r['club_title'] in SKIP: return None
        return ALIAS.get(r['club_title']) or N.get(_norm(r['club_text'])) or N.get(_norm(re.sub(r'\s*\(.*\)', '', r['club_title'])))
    sq = collections.defaultdict(list)
    for r in json.loads(f.read_text()):
        if r['nation'] in nations: sq[(r['nation'], r['tournament'], r['year'])].append(r)
    out = {}
    for n in nations:
        num = den = 0.0; by = collections.defaultdict(lambda: [0, 0.0])
        for (nn, t, y), ps in sq.items():
            if nn != n: continue
            w = 0.5 ** ((2026 - y) / HALF); s = 0.0
            for r in ps:
                c = club(r)
                if not c: continue
                v = g(aff[c]) * (1.5 if r['captain'] else 1) * 23 / len(ps)
                s += v; by[c][0] += 1; by[c][1] += w * v
            num += w * s; den += w
        if not den: continue
        L = num / den; bump = max(-2.0, min(2.0, L / 3))
        top = sorted(((c, k, v / den / 3) for c, (k, v) in by.items() if abs(v) > 1e-9), key=lambda x: -abs(x[2]))[:4]
        out[n] = (round(bump, 1), [(c, k, round(v, 2)) for c, k, v in top])
    return out

def domestic(primary):
    """primary: club -> league key. -> {club: (bump, share, league mean)}"""
    f = RES / 'domestic.json'
    if not f.exists(): return {}
    D = json.loads(f.read_text()); share = {}
    for c, ss in D.items():
        num = den = 0.0
        for s in ss:
            if s.get('share') is None: continue
            w = 0.5 ** (s['age'] / HALF); num += w * s['share']; den += w
        if den: share[c] = (num / den, min(1.0, den / 2))
    # peer group: the club's own league; Champions League-only clubs against all European top flights
    peers = collections.defaultdict(list)
    for c, (x, _) in share.items():
        k = primary.get(c)
        if k: peers[k].append(x)
    ucl_pool = [x for c, (x, _) in share.items() if primary.get(c) in ('epl', 'bl', 'esp', 'ita', 'fra', 'ucl')]
    out = {}
    for c, (x, conf) in share.items():
        k = primary.get(c)
        if not k: continue
        P = ucl_pool if k == 'ucl' else peers[k]
        if len(P) < 5: continue
        m = sum(P) / len(P); sd = math.sqrt(sum((p - m) ** 2 for p in P) / len(P)) or 1
        out[c] = (round(max(-2.0, min(2.0, 0.8 * (x - m) / sd * conf)), 1), round(x, 2), round(m, 2))
    return out
