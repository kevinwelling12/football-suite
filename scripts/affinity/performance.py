"""Track record: a coefficient on Affinity for consistent recent success.

python3 scripts/affinity/performance.py        # print the ranking and the biggest movers

Input: scripts/affinity/research/perf/*.json (last 10 completed league seasons per club, most recent first,
plus trophies; brief in research/PERF_BRIEF.md).

Each season scores 0-10 against a reference tier: the top flight for every club outside North America;
USL Championship clubs (regional interest) against tier 2. (Until 2026-09-29 the Championship was judged
against tier 2 and League One/Two against tiers 3-4.)
- inside the band: 8.5 * (1 - p^1.5), p = 0 for 1st, 1 for last (a Two-tier band stacks the tiers).
  Concave on purpose: steady top-half finishes score close to a title, the relegation fight scores low.
- one tier above the band: 8.5 + 1.5 * (1 - p); two or more above: 10.
- one tier below: 4.5 * (1 - p^1.5), so winning promotion beats a relegation fight; two or more below: 0.
- trophies that season add: league title 1.5 (in, above or one tier below the band), main cup 1, league cup 0.5,
  Champions League / CONCACAF Champions Cup 2, Europa / Conference League 1. Capped at 10.
- a season the club did not exist: 3 (a new club has not shown consistency yet). A season with no
  regular season (NWSL 2020) is left out.
Seasons are averaged with a 4-season half-life (last season weight 1, four seasons ago 0.5, nine ago 0.21);
3 seasons until quiz round 4 (Kevin leans nostalgic: judges by the body of work, not the latest season).

Coefficient: k = 0.95 + 0.01 * P, so P 0 -> x0.95, P 5 -> x1.00, P 10 -> x1.05 (2026-10-02: the gut test fitted
0.723 at +/-15% and 0.776 at +/-5% for top-flight clubs; was 0.85 + 0.03 P). History: +/-10% (2026-09-28), +/-20% (Kevin,
so Dortmund passes Union), +/-15% after quiz round 5 (2026-09-29): every method there (budget split, trade-offs, everyday
items) ranked winning low, and gut ratings of 26 anonymous clubs fitted best with a small effect; 15% keeps Dortmund
above Union Berlin.
It multiplies the weighted factor score, before adjustments (penalties are not scaled). Nations: no track record.
"""
import json, pathlib

root = pathlib.Path(__file__).resolve().parents[2]
PERF = root / 'scripts' / 'affinity' / 'research' / 'perf'
HALF_LIFE = 4
EMPTY = 3.0
TROPHY = {'league': 1.5, 'cup': 1.0, 'league_cup': 0.5, 'continental': 2.0, 'continental2': 1.0}
# Band of tiers each app league is judged against. Clubs only in the Champions League: their own top flight.
BAND = {'epl': (1, 1), 'esp': (1, 1), 'ita': (1, 1), 'bl': (1, 1), 'fra': (1, 1), 'mls': (1, 1), 'nwsl': (1, 1),
        'ucl': (1, 1), 'ch': (1, 1), 'usl': (2, 2), 'cup': (1, 1)}
# Kevin (2026-09-29): clubs outside North America are judged against the top flight (tier 1, mid-table or higher
# regularly, occasional cup and European runs). Lower-tier football only counts for regional clubs, so the USL
# keeps its own tier. Until then the Championship was judged against tier 2 and League One/Two against tiers 3-4.
PRIMARY = ['epl', 'esp', 'ita', 'bl', 'fra', 'mls', 'nwsl', 'ch', 'usl', 'ucl', 'cup']


def load():
    out = {}
    for f in sorted(PERF.glob('*.json')):
        for c in json.loads(f.read_text()):
            out[c['name']] = c
    return out


def season_score(s, band, trophies):
    lo, hi = band
    t, pos, of = s.get('tier'), s.get('pos'), s.get('of')
    if t is None:
        return None
    if not pos or not of:  # no regular season (NWSL 2020): left out of the average
        return 'skip'
    p = 0.0 if of <= 1 else min(1.0, max(0.0, (pos - 1) / (of - 1)))
    if t < lo:
        x = 8.5 + 1.5 * (1 - p) if lo - t == 1 else 10.0
    elif t <= hi:
        bp = ((t - lo) + p) / (hi - lo + 1)
        x = 8.5 * (1 - bp ** 1.5)
    elif t - hi == 1:
        x = 4.5 * (1 - p ** 1.5)
    else:
        x = 0.0
    for tr in trophies:
        if tr['s'] != s['s']:
            continue
        if tr['type'] == 'league' and t > hi + 1:
            continue
        x += TROPHY.get(tr['type'], 0)
    return min(10.0, x)


def track(club, band):
    """-> (P, [season scores oldest..newest, None for no season])"""
    seasons = club['seasons'][:10]
    tr = club.get('trophies', [])
    xs = [season_score(s, band, tr) for s in seasons]
    num = den = 0.0
    for i, x in enumerate(xs):
        if x == 'skip':
            continue
        w = 0.5 ** (i / HALF_LIFE)
        num += w * (EMPTY if x is None else x); den += w
    return round(num / den, 1), [None if x in (None, 'skip') else round(x, 1) for x in reversed(xs)]


# Applies to top-flight clubs only (USL Championship counts: no promotion/relegation in the US). Championship and
# lower English clubs get no coefficient: they were judged against the top flight and scored near zero.
APPLIES = {'epl', 'esp', 'ita', 'bl', 'fra', 'mls', 'nwsl', 'ucl', 'usl'}


def coef(P):
    return 0.95 + 0.01 * P


def primary(comps):
    return next((c for c in PRIMARY if c in comps), comps[0])


if __name__ == '__main__':
    D = json.loads((root / 'data' / 'suite_data.json').read_text())
    comps = {}
    for k, c in D.items():
        for t in c['teams']:
            comps.setdefault(t['name'], []).append(k)
    P = load()
    rows = []
    for name, cs in comps.items():
        if 'unl' in cs:
            continue
        if name not in P:
            print('missing', name); continue
        pk = primary(cs)
        v, xs = track(P[name], BAND[pk])
        rows.append((v, name, pk, xs))
    rows.sort(reverse=True)
    for v, name, pk, xs in rows:
        print(f'{v:4.1f}  x{coef(v):.3f}  {pk:4} {name:32} {" ".join("  -" if x is None else f"{x:3.0f}" for x in xs)}')
