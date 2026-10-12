"""Inputs for the Affinity model (scripts/affinity/affinity.py). Measurements only: nothing here decides a score.

Every entity (club, women's club, nation, player) is described the same way:
  factors     0-10 research scores (clubs and nations: C V H O T I; players: CH WK LO AB LE ST I)
  perf        track record 0-10, or None when it isn't judged (see performance.py)
  integrity   0-10, docked by documented wrongs (items: [(label, points off)])
  conn        connection items: [(label, points)]  signed
  roots       hometown / home nation / ancestry: (label, points)

Sources: scores.py (clubs, nations), importers/build_usl.py (USL), research/perf (track records), big4.py (location and
Kevin's other teams), association.py (linked clubs), interplay.py (homegrown share, national squads), players/ (player
research, audit, values tags), heritage.json (ancestry).
"""
import ast, json, pathlib, re, sys
root = pathlib.Path(__file__).resolve().parents[2]
A = root / 'scripts' / 'affinity'
sys.path.insert(0, str(A)); sys.path.insert(0, str(A / 'players'))
from scores import S as _S
import performance as perf
import big4

for node in ast.parse((root / 'scripts' / 'importers' / 'build_usl.py').read_text()).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'A':
        _S = {**_S, **ast.literal_eval(node.value)}
SCORES = _S
HOMETOWN = 'Sacramento Republic FC'
HOME_NATION = 'United States'

# ---------------------------------------------------------------- integrity
# Integrity (0-10) is a rating like the others: 10 for a clean record, docked for each documented wrong (racism, fan
# violence, state or private-equity ownership, a leveraged buyout, the Super League, multi-club, overspending, a
# franchise move, a government's record for nations). It is the 6th field in scores.py; the note lists each item with
# what it takes off ("Racism -0.9"). Replaced the hard lines and bonuses on 2026-10-12 (docs/affinity.md).
_ITEM = re.compile(r'^(.*?)\s*-(\d+(?:\.\d+)?)$')

def club_measures(name):
    """-> (factors dict C V H O T I, integrity items [(label, points off)], notes [str]) from scores.py."""
    C, V, H, O, T, I, note = SCORES[name]
    f = dict(C=C, V=V, H=H, O=O, T=T, I=I); items, notes = [], []
    for part in [p.strip() for p in note.split(';') if p.strip()]:
        m = _ITEM.match(part)
        if m and m.group(1) and not part.startswith(('Rules', 'Cascadia')): items.append((m.group(1), float(m.group(2))))
        else: notes.append(part)
    if abs(max(0.0, 10 - sum(x for _, x in items)) - I) > 0.05: notes.append(f'Integrity {I} differs from its items')
    for k in f: f[k] = max(0.0, min(10.0, f[k]))
    return f, items, notes

# ---------------------------------------------------------------- heritage and roots
_H = json.loads((A / 'heritage.json').read_text())
HERITAGE = {}
for _r, _pct in _H['regions'].items():
    for _n, _sh in _H['split'][_r].items(): HERITAGE[_n] = HERITAGE.get(_n, 0) + _pct * _sh
REGION_PCT = dict(_H['regions'])
CLUB_REGION = dict(_H.get('club_regions', {}))   # club -> its Ancestry region (clubs get that region's share, 2026-10-12)
NATION_ALIAS = {'Ireland': 'Republic of Ireland', 'Czechia': 'Czech Republic'}
def nation_share(team): return HERITAGE.get(NATION_ALIAS.get(team, team), 0)

# ---------------------------------------------------------------- track records
PERF = perf.load()

def club_perf(name, comps):
    """Track record P (0-10) against the club's reference tier, or None (not judged: Championship and below)."""
    if name not in PERF: return None
    pk = perf.primary(comps) if comps else 'ucl'
    if comps and pk not in perf.APPLIES: return None
    P, xs = perf.track(PERF[name], perf.BAND.get(pk, (1, 1)))
    return dict(P=P, ps=xs, pl=PERF[name]['seasons'][0]['s'])

_NP = A / 'research' / 'nations_perf.json'
RESULT = {'champions': 10, 'runners-up': 8.5, 'third place': 7.5, 'fourth place': 7, 'semi-finals': 7, 'quarter-finals': 6,
          'round of 16': 4.5, 'round of 32': 3.5, 'group stage': 2, 'did not qualify': 0}
def nation_perf(name):
    """Recent record of a national team (0-10): FIFA ranking (half) and the last World Cups and continental
    championship (half). A nation is judged on its recent body of work, like a club."""
    if not _NP.exists(): return None
    for x in json.loads(_NP.read_text()):
        if x['name'] != name: continue
        rk = x.get('fifa_rank')
        r = 10 * max(0.0, 1 - (rk - 1) / 210) if rk else None   # percentile among FIFA's 211 members
        res = [RESULT.get((x.get(k) or '').lower()) for k in ('wc2026', 'wc2022')] + [RESULT.get(((x.get('continental') or {}).get('result') or '').lower())]
        w = [1.0, 0.5, 0.8]; t = [(a, b) for a, b in zip(res, w) if a is not None]
        tour = sum(a * b for a, b in t) / sum(b for _, b in t) if t else None
        parts = [v for v in (r, tour) if v is not None]
        if not parts: return None
        return dict(P=round(sum(parts) / len(parts), 1), rank=rk, wc2026=x.get('wc2026'), cont=x.get('continental'))
    return None

# ---------------------------------------------------------------- connection items (clubs)
def club_conn(name):
    """Location, Kevin's other teams, rival markets, the Republic link, brand pulls (big4.py)."""
    return [(l, v) for l, v in big4.items(name)]

# ---------------------------------------------------------------- players
import model as PM  # players/model.py: research loader (audit, loyalty overlays, values tags, incident corrections)
P_LABEL = {'b01': 'Racist abuse', 'b02': 'Abuse allegations', 'b03': 'Doping', 'b04': 'Match-fixing', 'b05': 'Tax fraud',
           'b06': 'Violent conduct', 'b08': 'Forced transfer', 'b09': 'Rival move', 'b10': 'Money-league move', 'b12': 'Authoritarian ambassador'}
# Integrity points off per incident (Kevin's best-worst ranking, quiz round 7; sizes fitted in round 9, moved onto the
# 0-10 Integrity scale on 2026-10-12). Integrity = 10 minus the items, floored at 0.
P_POINTS = {'b02': 14, 'b01': 11, 'b04': 11, 'b06': 5.6, 'b12': 5.6, 'b05': 4, 'b03': 3.2, 'b08': 2.4, 'b09': 1.6, 'b10': 2.4}
def money_points(age): return 5.6 if age <= 29 else 3.2 if age <= 33 else 1.6

def player_items(p):
    """Integrity items for a player: acquittal or dropped charges 30%, apology 60%, a move
    made as a coach half; one money-league move, ambassadorship, rival move or forced transfer counts once; no cap."""
    items = []; born = p.get('born')
    for e in (p.get('incidents') or []) + (p.get('money_moves') or []):
        t = e.get('type')
        if t not in P_POINTS: continue
        if t == 'b10' and p.get('gender') == 'W': continue   # money-league moves apply to men only (B13)
        txt = ' '.join(str(e.get(k, '')) for k in ('what', 'outcome')).lower(); coach = re.search(r'manag|coach', txt)
        pts = P_POINTS[t]
        if t == 'b10' and not coach and born and e.get('year'): pts = money_points(e['year'] - born)
        f = 1.0
        if re.search(r'acquit|dismiss|dropped|cleared|closed|not guilty|no charges|charges were|overturned|annulled|quashed', txt): f = 0.3
        elif re.search(r'apolog', txt) and not re.search(r'\b(no|not|never|without|refused to)\s+(\w+\s+)?apolog', txt): f = 0.6
        if t == 'b10' and coach: f *= 0.5
        items.append((t, f"{P_LABEL[t]} ({e.get('year', '?')})", round(pts * f, 1), e.get('what', '')))
    if born and p.get('gender') != 'W':
        for c in p.get('clubs', []):
            if c.get('from') and PM.MONEY.search((c.get('club') or '').lower()):
                items.append(('b10', f"Money-league move ({c['from']})", money_points(c['from'] - born), c.get('club')))
    out, seen = [], set()
    for it in sorted(items, key=lambda x: -x[2]):
        if it[0] in ('b10', 'b12', 'b09', 'b08') and it[0] in seen: continue
        seen.add(it[0]); out.append(it)
    return out

def players():
    facts, sc = PM.load()
    out = {}
    for n, p in facts.items():
        if n not in sc: continue
        s = {**sc[n], **PM.FIXES.get(n, {})}
        out[n] = dict(name=n, kind='player', gender=p.get('gender'), active=bool(p.get('active')), facts=p, scores=s,
                      factors={k: s[k] for k in ('CH', 'WK', 'LO', 'AB', 'LE', 'ST')}, items=player_items(p))
        out[n]['factors']['I'] = round(max(0.0, 10 - sum(x[2] for x in out[n]['items'])), 1)
    return out
