"""Player Affinity (quiz round 7, 2026-10-06).

Player Affinity = factor score + connection + penalties - era, capped 0-100.
- Factor score: six factors 0-10 (scores/*.json, from research/out/*.json and SCORING_BRIEF.md), weighted by Kevin's
  blend of his 100-point budget and the fit to his gut ratings (see W). Sum / total * 10.
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
# Half his 100-point budget (CH 30, WK 20, LO 15, AB 10, ST 10, LE 10), half the weights that best fit his 18 gut ratings
# (CH 20, WK 5, AB 76; leave-one-out r 0.81): the same stated/revealed split as the club rounds. Gut fit r 0.62.
W = {'CH': 25, 'WK': 12.5, 'LO': 7.5, 'AB': 43, 'ST': 5, 'LE': 5}
SEV = {'b02': 18, 'b01': 14, 'b04': 14, 'b06': 7, 'b12': 7, 'b05': 5, 'b03': 4, 'b08': 3, 'b10': 3, 'b09': 2}
KEVIN = ['liverpool', 'borussia dortmund', 'dortmund', 'portland timbers', 'portland thorns', 'sacramento republic']
GUT = {'Cristiano Ronaldo': 6, 'Erling Haaland': 9, 'Harry Kane': 7, 'Jude Bellingham': 8, 'Kylian Mbappé': 7, 'Lamine Yamal': 7,
       'Lionel Messi': 6, 'Mohamed Salah': 9, 'Vinícius Júnior': 6, 'Virgil van Dijk': 9, 'Christian Pulisic': 4, 'Luka Modrić': 8,
       'Marco Reus': 6, 'Sophia Wilson': 8, 'Zinedine Zidane': 7, 'David Beckham': 5, 'Landon Donovan': 7, 'Megan Rapinoe': 8}
NOW = 2026

def norm(s):
    s = unicodedata.normalize('NFD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\b(fc|cf|sc|afc|ac|the)\b', '', re.sub(r'[^a-z0-9 ]', ' ', s)).split()

# club Affinity from the tracker (every club and its short name)
D = json.loads((root / 'data' / 'suite_data.json').read_text())
CLUB = {}
for k, L in D.items():
    if not isinstance(L, dict) or k == 'unl': continue
    for t in L.get('teams', []):
        a = t['base'] + t.get('bonus', 0)
        for n in {t['name'], t.get('short') or t['name']}: CLUB.setdefault(' '.join(norm(n)), a)
ALIAS = {'man city': 'manchester city', 'man utd': 'manchester united', 'man united': 'manchester united', 'psg': 'paris saint germain',
         'inter miami': 'inter miami', 'nycfc': 'new york city football club', 'new york city': 'new york city football club',
         'leipzig': 'rb leipzig', 'bayern': 'bayern munich', 'bayern munchen': 'bayern munich', 'spurs': 'tottenham hotspur'}
def club_aff(name):
    n = ' '.join(norm(name)); n = ALIAS.get(n, n)
    if n in CLUB: return CLUB[n]
    hits = [v for c, v in CLUB.items() if n and (c.startswith(n) or n.startswith(c)) and min(len(c), len(n)) >= 5]
    return hits[0] if len(hits) == 1 else None

def seasons(c):
    a, b = c.get('from'), c.get('to') or NOW
    return max(0.5, (b - a)) if a else 0

def connection(p):
    plus = minus = 0.0
    for c in p.get('clubs', []):
        n = ' '.join(norm(c.get('club')))
        if any(k in n for k in KEVIN) and 'ii' not in n.split(): plus += 1.2 * seasons(c)
        else:
            a = club_aff(c.get('club'))
            if a is not None and a < 35: minus += 0.3 * seasons(c)
    us = 2.0 if (p.get('national') or {}).get('team') in ('USA', 'United States') and ((p.get('national') or {}).get('caps') or 1) else 0
    return min(plus, 8) - min(minus, 3) + us

def penalties(p):
    tot, items = 0.0, []
    for e in (p.get('incidents') or []) + (p.get('money_moves') or []):
        t = e.get('type'); s = SEV.get(t)
        if not s: continue
        txt = (' '.join(str(e.get(k, '')) for k in ('what', 'outcome'))).lower()
        f = 1.0
        if re.search(r'acquit|dismiss|dropped|cleared|closed|not guilty|no charges|charges were', txt): f = 0.3
        elif re.search(r'apolog', txt): f = 0.6
        if t == 'b10' and re.search(r'manag|coach', txt): f *= 0.5
        items.append((t, round(s * f, 1))); tot += s * f
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

def load():
    facts = {}
    for f in sorted(glob.glob(str(here / 'research' / 'out' / '*.json'))):
        for p in json.load(open(f)):
            if p['name'] in facts and len(json.dumps(facts[p['name']])) >= len(json.dumps(p)): continue
            facts[p['name']] = p
    scores = {}
    for f in sorted(glob.glob(str(here / 'scores' / '*.json'))):
        for s in json.load(open(f)): scores.setdefault(s['name'], s)
    return facts, scores

def rate(p, s, w=W):
    base = sum(w[k] * s[k] for k in w) / sum(w.values()) * 10
    c, pen, e = connection(p), penalties(p), era(p)
    return dict(name=p['name'], gender=p.get('gender'), active=bool(p.get('active')), base=round(base, 1), conn=round(c, 1),
                pen=round(pen, 1), era=round(e, 1), aff=round(max(0, min(100, base + c + pen + e)), 1), **{k: s[k] for k in W})

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
