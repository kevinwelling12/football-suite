"""Inputs for the Affinity model (scripts/affinity/affinity.py). Measurements only: nothing here decides a score.

Every entity (club, women's club, nation, player) is described the same way:
  factors     0-10 research scores (clubs and nations: C V H O T; players: CH WK LO for the role side, AB LE ST for performance)
  perf        track record 0-10, or None when it isn't judged (see performance.py)
  hard        hard lines: [(type, label, points)]  points > 0 = how much it costs before the model's scale
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

# ---------------------------------------------------------------- hard lines
# Club and nation hard lines are researched per club (points in scores.py notes). The minor ones were folded into the
# factors on 2026-10-02 (the note keeps what was moved): unfold them so factors are pure measurements again and every
# cost shows as a hard line. Same arithmetic: the model subtracts hard lines from the character score, which is what
# the fold did.
TYPE = {'Racism': 'racism', 'Fan violence': 'violence', 'State-backed': 'state', 'Government record': 'government',
        'Private equity': 'pe', 'Leveraged buyout': 'lbo', 'Super League': 'superleague', 'Multi-club': 'multiclub',
        'Overspend': 'overspend', 'Franchise': 'franchise', "Owner's fortune from sports betting": 'betting_owner',
        "Owner's fortune from arms making": 'arms_owner', 'Other': 'other'}
FACTOR = {'Ownership': 'O', 'History': 'H', 'Values': 'V'}
PER = {'O': 1.0 / 0.9, 'H': 1.6 / 0.9, 'V': 2.6 / 0.9}  # Affinity points per factor point when the fold was made
_FOLD = re.compile(r"([A-Z][^,>]*?) (-?\d+(?:\.\d+)?) -> (Ownership|History|Values) ([+-]\d+(?:\.\d+)?)(?:, Values ([+-]\d+(?:\.\d+)?))?")
_ITEM = re.compile(r'^(.*?)\s*([+-]\d+(?:\.\d+)?)$')

def club_measures(name):
    """-> (factors dict, hard [(type, label, points)], notes [str]) from scores.py, with folds undone."""
    C, V, H, O, T, adj, note = SCORES[name]
    f = dict(C=C, V=V, H=H, O=O, T=T); hard, notes = [], []
    for part in [p.strip() for p in note.split(';') if p.strip()]:
        if part.startswith('Folded'):
            for lab, pts, fac, d, dv in _FOLD.findall(part.split(': ', 1)[1]):
                f[FACTOR[fac]] = round(f[FACTOR[fac]] - float(d), 1)
                if dv: f['V'] = round(f['V'] - float(dv), 1)
                hard.append((TYPE.get(lab, 'other'), lab if lab != 'Other' else 'Conduct', -float(pts)))
            continue
        m = _ITEM.match(part)
        if m and m.group(1) and not part.startswith(('Rules', 'Cascadia')):
            hard.append((TYPE.get(m.group(1), 'other'), m.group(1), -float(m.group(2))))
        else:
            notes.append(part)
    if abs(sum(-p for t, l, p in hard if t not in ('multiclub', 'overspend', 'franchise', 'betting_owner', 'arms_owner', 'other')) - adj) > 0.05 \
       and not any(p.startswith('Folded') for p in note.split(';')):
        notes.append(f'unparsed adjustment {adj}')
    for k in f: f[k] = max(0.0, min(10.0, f[k]))
    return f, hard, notes

# ---------------------------------------------------------------- heritage and roots
_H = json.loads((A / 'heritage.json').read_text())
HERITAGE = {}
for _r, _pct in _H['regions'].items():
    for _n, _sh in _H['split'][_r].items(): HERITAGE[_n] = HERITAGE.get(_n, 0) + _pct * _sh

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
# Severities on the character scale (Kevin's best-worst ranking, quiz round 7; points fitted in round 9 and kept).
P_POINTS = {'b02': 53, 'b01': 41, 'b04': 41, 'b06': 21, 'b12': 21, 'b05': 15, 'b03': 12, 'b08': 9, 'b09': 6, 'b10': 9}
def money_points(age): return 21 if age <= 29 else 12 if age <= 33 else 6   # 7 / 4 / 2 severity units x 2.94

def player_hard(p):
    """Itemised hard lines for a player, the same rules as before: acquittal or dropped charges 30%, apology 60%, a move
    made as a coach half; one money-league move, ambassadorship, rival move or forced transfer counts once; no cap."""
    items = []; born = p.get('born')
    for e in (p.get('incidents') or []) + (p.get('money_moves') or []):
        t = e.get('type')
        if t not in P_POINTS: continue
        txt = ' '.join(str(e.get(k, '')) for k in ('what', 'outcome')).lower(); coach = re.search(r'manag|coach', txt)
        pts = P_POINTS[t]
        if t == 'b10' and not coach and born and e.get('year'): pts = money_points(e['year'] - born)
        f = 1.0
        if re.search(r'acquit|dismiss|dropped|cleared|closed|not guilty|no charges|charges were|overturned|annulled|quashed', txt): f = 0.3
        elif re.search(r'apolog', txt): f = 0.6
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
                      factors={k: s[k] for k in ('CH', 'WK', 'LO', 'AB', 'LE', 'ST')}, hard=player_hard(p))
    return out
