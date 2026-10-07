"""Player Affinity (quiz rounds 7 and 8, 2026-10-06).

Player Affinity = factor score + connection + penalties, capped 0-100.
- Factor score: six factors 0-10 (scores/*.json, from research/out/*.json and SCORING_BRIEF.md), weighted by the fit to
  Kevin's choices and gut ratings (fit.py -> fit.json, see W). Sum / total * 10. Connection and penalties are scaled by the
  fitted CONN_X and PEN_X.
- Connection (quiz s05 "big boost", s04 "a little", s07 "small boost"): seasons at Kevin's clubs (Liverpool, Dortmund,
  Timbers, Thorns, Republic) +1.2 each up to +8; seasons at clubs he rates under 35 (Man City, PSG, NYCFC, Inter Miami,
  Chelsea, RB Leipzig, Lazio...) -0.3 each down to -3; a US international +2.
- Penalties (best-worst ranking, quiz m1-m9): abuse allegations worst, then racist abuse = match-fixing, then violent
  conduct = authoritarian ambassador, tax fraud, then doping = forced transfer = Saudi move, then rival move. Diving and
  general conduct live in Character. An acquittal or dropped charges cuts a penalty to 30%; an apology to 60% (s06 "counts
  less"); a move made as a coach counts half.
- Era: none. Quiz s02 said "count a bit less", but Kevin has followed closely for under a year and asked that past players
  not be judged through that lens.

Usage: python3 scripts/affinity/players/model.py [--fit]
"""
import json, glob, pathlib, re, sys, unicodedata
root = pathlib.Path(__file__).resolve().parents[3]
here = pathlib.Path(__file__).resolve().parent
# Weights fitted to Kevin's mystery-player choices (quiz rounds 8 and 9) by fit.py, read from fit.json; connection and penalties are scaled by the fit too. No 100-point budget (round 7's
# budget was dropped: Kevin found it hard to use). Fallback values if fit.json is missing.
_fit = json.loads((pathlib.Path(__file__).resolve().parent / 'fit.json').read_text()) if (pathlib.Path(__file__).resolve().parent / 'fit.json').exists() else None
W = _fit['W'] if _fit else {'CH': 25, 'WK': 29, 'LO': 16, 'AB': 4.5, 'ST': 14, 'LE': 12}
CONN_X = _fit['conn'] if _fit else 1.09
PEN_X = _fit['pen'] if _fit else 2.54
# Kevin's own corrections (fixes/): the boost for his favourite positions and factor scores he changed. Fixes win over scores/.
_fx = here / 'fixes' / 'raw' / 'responses' / 'kevin.json'
_fx = json.loads(_fx.read_text()) if _fx.exists() else {}
_fx = _fx.get('data', _fx)
POS_BOOST = _fx['pos'] if _fx.get('pos') is not None else (_fit or {}).get('pos', 3)  # fitted to round 10 (fit.json); 3 before that
FIXES = _fx.get('fix', {})
FAV_POS = {'AM', 'DLP', 'RB', 'LB', 'RWB', 'LWB'}  # quiz 7 s03: playmaker / No. 10 and full-back
SEV = {'b02': 18, 'b01': 14, 'b04': 14, 'b06': 7, 'b12': 7, 'b05': 5, 'b03': 4, 'b08': 3, 'b10': 3, 'b09': 2}
KEVIN = ['liverpool', 'borussia dortmund', 'dortmund', 'portland timbers', 'portland thorns', 'sacramento republic']
GUT = {'Cristiano Ronaldo': 6, 'Erling Haaland': 9, 'Harry Kane': 7, 'Jude Bellingham': 8, 'Kylian Mbappé': 7, 'Lamine Yamal': 7,
       'Lionel Messi': 6, 'Mohamed Salah': 9, 'Vinícius Júnior': 6, 'Virgil van Dijk': 9, 'Christian Pulisic': 4, 'Luka Modrić': 8,
       'Marco Reus': 6, 'Sophia Wilson': 8, 'Zinedine Zidane': 7, 'David Beckham': 5, 'Landon Donovan': 7, 'Megan Rapinoe': 8}
NOW = 2026

def norm(s):
    s = unicodedata.normalize('NFD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\b(fc|cf|sc|afc|ac|the)\b', '', re.sub(r'[^a-z0-9 ]', ' ', s)).split()

# club Affinity from the tracker (every club and its short name). Women's clubs (NWSL) and men's clubs are kept apart:
# a woman's spell at a European club the tracker only rates for its men's side counts as unrated (Kevin, 2026-10-07).
D = json.loads((root / 'data' / 'suite_data.json').read_text())
CLUB, CLUB_W = {}, {}
for k, L in D.items():
    if not isinstance(L, dict) or k == 'unl': continue
    for t in L.get('teams', []):
        a = t['base'] + t.get('bonus', 0)
        for n in {t['name'], t.get('short') or t['name']}: (CLUB_W if k == 'nwsl' else CLUB).setdefault(' '.join(norm(n)), a)
ALIAS = {'man city': 'manchester city', 'man utd': 'manchester united', 'man united': 'manchester united', 'psg': 'paris saint germain',
         'inter miami': 'inter miami', 'nycfc': 'new york city football club', 'new york city': 'new york city football club',
         'leipzig': 'rb leipzig', 'bayern': 'bayern munich', 'bayern munchen': 'bayern munich', 'spurs': 'tottenham hotspur'}
def club_aff(name, women=False):
    T = CLUB_W if women else CLUB
    n = ' '.join(norm(name)); n = ALIAS.get(n, n)
    if n in T: return T[n]
    hits = [v for c, v in T.items() if n and (c.startswith(n) or n.startswith(c)) and min(len(c), len(n)) >= 5]
    return hits[0] if len(hits) == 1 else None

def seasons(c):
    a, b = c.get('from'), c.get('to') or NOW
    return max(0.5, (b - a)) if a else 0

CONN_CAP = 4  # most a player can gain from club seasons
def per_season(a):
    """Connection per club season, from Kevin's Affinity for the club alone (Kevin, 2026-10-07: "base it solely on Affinity
    rating, not my stated favourites"; every club now gets what Dortmund got). 50 is neutral; up to +0.6 at 85+;
    down to -0.6 at 20 or below."""
    if a is None: return 0.0
    return min(0.6, 0.6 * (a - 50) / 35) if a >= 50 else max(-0.6, -0.3 * (50 - a) / 15)

def connection(p):
    women = p.get('gender') == 'W'
    plus = minus = 0.0
    for c in p.get('clubs', []):
        n = ' '.join(norm(c.get('club')))
        if 'ii' in n.split() or re.search(r'\b(u\d+|youth|academy|reserves)\b', n): continue
        v = per_season(club_aff(c.get('club'), women))
        if v > 0: plus += v * seasons(c)
        else: minus -= v * seasons(c)
    plus = min(plus, CONN_CAP)
    us = 2.0 if (p.get('national') or {}).get('team') in ('USA', 'United States') and ((p.get('national') or {}).get('caps') or 1) else 0
    return min(plus, 8) - min(minus, 3) + us

def fav_pos(p):
    # 1 if his main position is a playmaker or full-back, 0.5 if it's a second position, else 0
    ps = p.get('positions') or []
    return 1.0 if ps and ps[0] in FAV_POS else 0.5 if FAV_POS & set(ps) else 0.0

# Money leagues (Kevin, 2026-10-06: "top players jumping to a 3rd-tier league for oil money ... I want guys that want to
# compete at the highest level"): Saudi, Qatari, Emirati and Chinese Super League clubs. A move there costs by age at the
# move: 29 or younger 7, 30-33 4, 34+ 2 (before scaling). Moves found in the club list count even when the research
# didn't file them as b10. A coach's move keeps the old 3 x 0.5. Counted once per player (the worst).
MONEY = re.compile(r"\bal[- ](nassr|hilal|ittihad|ahli|ettifaq|diriyah|qadsiah|shabab|sadd|duhail|arabi|gharafa|rayyan|wasl|ain|jazira|wahda)\b|"
                   r"shanghai (shenhua|sipg|port)|guangzhou (evergrande|fc)|jiangsu suning|hebei|beijing guoan|tianjin|dalian (yifang|pro)|shandong")
def money_sev(age): return 7 if age <= 29 else 4 if age <= 33 else 2

def penalties(p):  # stacks with no cap (Kevin chose this: several incidents can take a player to 0)
    tot, items = 0.0, []
    born = p.get('born')
    for e in (p.get('incidents') or []) + (p.get('money_moves') or []):
        t = e.get('type'); s = SEV.get(t)
        if not s: continue
        txt = (' '.join(str(e.get(k, '')) for k in ('what', 'outcome'))).lower()
        coach = re.search(r'manag|coach', txt)
        if t == 'b10' and not coach and born and e.get('year'): s = money_sev(e['year'] - born)
        f = 1.0
        if re.search(r'acquit|dismiss|dropped|cleared|closed|not guilty|no charges|charges were|overturned|annulled|quashed', txt): f = 0.3
        elif re.search(r'apolog', txt): f = 0.6
        if t == 'b10' and coach: f *= 0.5
        items.append((t, round(s * f, 1)))
    if born and p.get('gender') != 'W':
        for c in p.get('clubs', []):
            if c.get('from') and MONEY.search((c.get('club') or '').lower()): items.append(('b10', money_sev(c['from'] - born)))
    # one Saudi move or one ambassadorship counts once, however many entries
    seen, out = set(), 0.0
    for t, v in sorted(items, key=lambda x: -x[1]):
        if t in ('b10', 'b12', 'b09', 'b08') and t in seen: continue
        seen.add(t); out += v
    return -out

def era(p):
    # Dropped (Kevin, 2026-10-06): he has followed closely for under a year, so not knowing a past player says nothing
    # about the player. All-time players are judged on the record alone.
    return 0

def load(raw=False):
    """Facts and scores. Unless raw, the independent audit is applied: merged scores (audit/merged.json) and incident
    corrections (audit/incidents.json: dropped, retyped, new outcomes, missing incidents added)."""
    facts = {}
    for f in sorted(glob.glob(str(here / 'research' / 'out' / '*.json'))):
        for p in json.load(open(f)):
            if p['name'] in facts and len(json.dumps(facts[p['name']])) >= len(json.dumps(p)): continue
            facts[p['name']] = p
    scores = {}
    for f in sorted(glob.glob(str(here / 'scores' / '*.json'))):
        for s in json.load(open(f)): scores.setdefault(s['name'], s)
    if raw: return facts, scores
    a = here / 'audit'
    if (a / 'merged.json').exists():
        for n, m in json.loads((a / 'merged.json').read_text()).items():
            if n in scores: scores[n] = {**scores[n], **{k: m[k] for k in W}}
    for f in sorted(a.glob('lo_out*.json')):  # Loyalty re-scored from when a player settles (Kevin, 2026-10-06; LO_BRIEF.md)
        for n, v in json.loads(f.read_text()).items():
            if n in scores: scores[n] = {**scores[n], 'LO': v['LO']}
    # Character = research score shifted by Kevin's values (quiz round 11 weights x the values tags in values/out*.json):
    # + 0.3 * sum(weight * tag), clipped 0-10 (Kevin, 2026-10-07). A shift, not an average: an untagged player keeps his
    # research score (averaging with a neutral 6 dragged good characters down and lifted bad ones).
    vw = here.parent / 'quiz11' / 'fit.json'
    if vw.exists():
        VW = json.loads(vw.read_text())['w']
        for f in sorted((here / 'values').glob('out*.json')):
            for n, tg in json.loads(f.read_text()).items():
                if n not in scores: continue
                v = sum(VW[k] * float(tg.get(k) or 0) for k in VW)
                ch = max(0.0, min(10.0, scores[n]['CH'] + 0.3 * v))
                scores[n] = {**scores[n], 'CH_research': scores[n]['CH'], 'CH_values': round(0.3 * v, 2), 'CH': round(ch, 2)}
    if (a / 'incidents.json').exists():
        for n, fx in json.loads((a / 'incidents.json').read_text()).items():
            if n not in facts: continue
            p = dict(facts[n]); inc, mon = list(p.get('incidents') or []), list(p.get('money_moves') or [])
            allv = inc + mon; drop = set()
            for v in fx.get('verdicts', []):
                i = v.get('i')
                if not isinstance(i, int) or i >= len(allv): continue
                e = allv[i] = dict(allv[i])
                if v['verdict'] == 'wrong': drop.add(i)
                elif v['verdict'] == 'retype' and v.get('type'): e['type'] = v['type']
                elif v['verdict'] == 'outcome' and v.get('outcome'): e['outcome'] = v['outcome']
            p['incidents'] = [e for i, e in enumerate(allv[:len(inc)]) if i not in drop] + list(fx.get('missing', []))
            p['money_moves'] = [e for i, e in enumerate(allv[len(inc):], len(inc)) if i not in drop]
            facts[n] = p
    return facts, scores

def rate(p, s, w=W):
    s = {**s, **FIXES.get(p['name'], {})}
    base = sum(w[k] * s[k] for k in w) / sum(w.values()) * 10
    c, ps, pen, e = CONN_X * connection(p), POS_BOOST * fav_pos(p), PEN_X * penalties(p), era(p)
    return dict(name=p['name'], gender=p.get('gender'), active=bool(p.get('active')), base=round(base, 1), conn=round(c, 1),
                pos=round(ps, 1), pen=round(pen, 1), era=round(e, 1), aff=round(max(0, min(100, base + c + ps + pen + e)), 1),
                **{k: s[k] for k in W})

def pearson(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n
    sx = sum((a - mx) ** 2 for a in x) ** .5; sy = sum((b - my) ** 2 for b in y) ** .5
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)

if __name__ == '__main__':
    facts, scores = load()
    rows = [rate(facts[n], scores[n]) for n in facts if n in scores]
    print(f'{len(rows)} scored of {len(facts)} researched')
    g = [r for r in rows if r['name'] in GUT]
    if len(g) >= 5:
        print('gut fit r = %.3f over %d players' % (pearson([r['aff'] for r in g], [GUT[r['name']] for r in g]), len(g)))
        for r in sorted(g, key=lambda r: -GUT[r['name']]): print(f"  {r['name']:20s} gut {GUT[r['name']]}  model {r['aff']:5.1f}  (base {r['base']} conn {r['conn']} pen {r['pen']} era {r['era']})")
    json.dump(sorted(rows, key=lambda r: -r['aff']), open(here / 'ratings.json', 'w'), ensure_ascii=False, indent=1)
