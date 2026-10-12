"""Blind comparison test: coded facts -> features 0-1 -> one standalone page.

  python3 scripts/blind/build.py      # writes scripts/blind/out/blind_test.html

Inputs: scripts/blind/coded/*.json (facts, CODEBOOK.md), plus objective tables already in the repo: league finishes
(scripts/affinity/research/perf via performance.py), FIFA ranks (research/nations_perf.json), share of domestic players
(research/domestic.json) and the Deloitte Money League order (big4.py MONEY_LEAGUE). Nothing from the Affinity model
(scores, weights, quiz answers, backtests) is read. Every transform is fixed and listed here; the test taker's answers set
every weight.
"""
import json, math, pathlib, sys, glob
root = pathlib.Path(__file__).resolve().parents[2]
here = root / 'scripts' / 'blind'
sys.path.insert(0, str(root / 'scripts' / 'affinity'))
import performance
from big4 import MONEY_LEAGUE

COMPS = [('epl', 'Premier League'), ('ch', 'Championship'), ('cup', 'League One / Two'), ('esp', 'LaLiga'), ('ita', 'Serie A'),
         ('bl', 'Bundesliga'), ('fra', 'Ligue 1'), ('ucl', 'Champions League'), ('mls', 'MLS'), ('usl', 'USL Championship'),
         ('nwsl', 'NWSL'), ('unl', 'Nations League'), ('wc', 'World Cup 2026 nations'), ('xc', 'Other clubs')]
LABEL = dict(COMPS)
PLACES = [  # name, lat, lon (city centre)
 ('Amsterdam', 52.37, 4.90), ('Atlanta', 33.75, -84.39), ('Barcelona', 41.39, 2.17), ('Berlin', 52.52, 13.40), ('Boston', 42.36, -71.06),
 ('Buenos Aires', -34.60, -58.38), ('Cairo', 30.04, 31.24), ('Charlotte', 35.23, -80.84), ('Chicago', 41.88, -87.63),
 ('Columbus', 39.96, -83.00), ('Dallas', 32.78, -96.80), ('Denver', 39.74, -104.99), ('Detroit', 42.33, -83.05), ('Dublin', 53.35, -6.26),
 ('Glasgow', 55.86, -4.25), ('Houston', 29.76, -95.37), ('Kansas City', 39.10, -94.58), ('Lagos', 6.52, 3.38), ('Lisbon', 38.72, -9.14),
 ('London', 51.51, -0.13), ('Los Angeles', 34.05, -118.24), ('Madrid', 40.42, -3.70), ('Manchester', 53.48, -2.24),
 ('Mexico City', 19.43, -99.13), ('Miami', 25.76, -80.19), ('Milan', 45.46, 9.19), ('Minneapolis', 44.98, -93.27),
 ('Montreal', 45.50, -73.57), ('Munich', 48.14, 11.58), ('Nashville', 36.16, -86.78), ('New York', 40.71, -74.01), ('Orlando', 28.54, -81.38),
 ('Paris', 48.86, 2.35), ('Philadelphia', 39.95, -75.17), ('Phoenix', 33.45, -112.07), ('Portland', 45.52, -122.68), ('Rome', 41.90, 12.50),
 ('Sacramento', 38.58, -121.49), ('Salt Lake City', 40.76, -111.89), ('San Diego', 32.72, -117.16), ('San Francisco Bay Area', 37.77, -122.42),
 ('São Paulo', -23.55, -46.63), ('Seattle', 47.61, -122.33), ('Seoul', 37.57, 126.98), ('St. Louis', 38.63, -90.20), ('Sydney', -33.87, 151.21),
 ('Tokyo', 35.68, 139.69), ('Toronto', 43.65, -79.38), ('Vancouver', 49.28, -123.12), ('Washington, D.C.', 38.91, -77.04)]

# Improvements (2026-10-12, Kevin: "do all four"): FAIR = True fills researched gaps (fill/out_*.json: attendance,
# capacity, ticket price, league country, caps) and weighs domestic trophies by league strength. False reproduces the
# first shipped version, for comparison.
FAIR = True
# League strength for domestic titles and cups: UEFA association coefficients (2021-26, approximate) scaled to England = 1;
# MLS and NWSL set at the level of a mid-ranked European league. Continental club titles: UEFA 1, CONCACAF 0.3.
LEAGUE = {'England': 1.0, 'Spain': 0.9, 'Italy': 0.9, 'Germany': 0.85, 'France': 0.75, 'Netherlands': 0.6, 'Portugal': 0.6,
          'Belgium': 0.5, 'Turkey': 0.45, 'Czech Republic': 0.4, 'Czechia': 0.4, 'Greece': 0.38, 'Scotland': 0.35, 'Austria': 0.35,
          'Switzerland': 0.33, 'Norway': 0.33, 'Denmark': 0.33, 'Poland': 0.3, 'Ukraine': 0.3, 'Israel': 0.28, 'Serbia': 0.25,
          'Croatia': 0.25, 'Sweden': 0.25, 'Cyprus': 0.25, 'Hungary': 0.2, 'Slovakia': 0.2, 'Romania': 0.2, 'Slovenia': 0.18,
          'Azerbaijan': 0.18, 'Bulgaria': 0.15, 'Republic of Ireland': 0.1, 'Ireland': 0.1, 'Northern Ireland': 0.08,
          'Lithuania': 0.08, 'Wales': 0.06, 'United States': 0.35, 'Canada': 0.35}
NA = {'United States', 'Canada'}
# Continental titles for nations, by confederation strength (World Cups count 1 each).
CONFED = {'CONMEBOL': 1.0, 'UEFA': 1.0, 'CAF': 0.5, 'AFC': 0.5, 'CONCACAF': 0.4, 'OFC': 0.1}
NATION_CONFED = {**{n: 'CONMEBOL' for n in ('Argentina', 'Brazil', 'Colombia', 'Ecuador', 'Paraguay', 'Uruguay', 'Chile', 'Peru', 'Bolivia', 'Venezuela')},
                 **{n: 'CONCACAF' for n in ('Mexico', 'United States', 'Canada', 'Panama', 'Haiti', 'Curaçao', 'Costa Rica', 'Jamaica', 'Honduras')},
                 **{n: 'OFC' for n in ('New Zealand',)},
                 **{n: 'AFC' for n in ('Australia', 'Iran', 'Iraq', 'Japan', 'Jordan', 'Qatar', 'Saudi Arabia', 'South Korea', 'Uzbekistan')},
                 **{n: 'CAF' for n in ('Algeria', 'Cape Verde', 'DR Congo', 'Egypt', 'Ghana', 'Ivory Coast', 'Morocco', 'Senegal', 'South Africa', 'Tunisia')}}

def cl(x): return max(0.0, min(1.0, x))
def num(v): return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
def lg(n, cap): return cl(math.log1p(n) / math.log1p(cap)) if n is not None else None

def load(prefix):
    out = []
    for f in sorted(glob.glob(str(here / 'coded' / f'{prefix}_*.json'))): out += json.load(open(f))
    if FAIR:   # researched gap fills override nulls (and clearly wrong capacities)
        patch = {}
        for f in sorted(glob.glob(str(here / 'fill' / ('out_clubs_*.json' if prefix == 'clubs' else 'out_caps_*.json')))):
            patch.update(json.load(open(f)))
        for x in out:
            p = patch.get(x['name']) or {}
            for k in ('avg_attendance', 'capacity', 'ticket_price', 'country', 'caps', 'nation'):
                if p.get(k) is not None and (k in ('avg_attendance', 'capacity', 'ticket_price', 'country') or x.get(k) is None): x[k] = p[k]
        if prefix == 'clubs':   # sanctions recounted to one standard (SANCTIONS_BRIEF.md), mapped to the codebook's 0-3 bands
            sanc = {}
            for f in sorted(glob.glob(str(here / 'fill' / 'out_sanctions_*.json'))): sanc.update(json.load(open(f)))
            for x in out:
                s = sanc.get(x['name'])
                if not s: continue
                d, v = s.get('discr_n') or 0, s.get('viol_n') or 0
                x['discrimination'] = 3 if s.get('far_right') or d >= 4 else 2 if d >= 2 else d
                x['violence'] = 3 if s.get('deaths') or v >= 4 else 2 if v >= 2 else v
                if x['kind'] != 'nation': x['financial_breaches'] = s.get('fin_n') or 0
    return out

def club_features(c, perf, ranks, dom):
    nation = c['kind'] == 'nation'; f = {}
    if not FAIR:
        n = sum(num(c.get(k)) or 0 for k in (('league_titles', 'cups') if nation else ('league_titles', 'cups', 'continental')))
    elif nation:
        n = (num(c.get('league_titles')) or 0) + (num(c.get('cups')) or 0) * CONFED[NATION_CONFED.get(c['name'], 'UEFA')]
    else:
        country = c.get('country') or ''
        n = ((num(c.get('league_titles')) or 0) + (num(c.get('cups')) or 0)) * LEAGUE.get(country, 0.2) \
            + (num(c.get('continental')) or 0) * (0.3 if country in NA else 1.0)
    f['trophies'] = lg(n, 10 if nation else 60)
    if nation:
        rk = ranks.get(c['name']); f['recent'] = cl(1 - (rk - 1) / 210) if rk else None
    else:
        ss = [s for s in (perf.get(c['name']) or {}).get('seasons', []) if s.get('pos') and s.get('of', 0) > 1][:5]
        f['recent'] = sum((s['of'] - s['pos']) / (s['of'] - 1) for s in ss) / len(ss) if ss else None
    fy = num(c.get('founded')); f['old'] = cl((2026 - fy) / 150) if fy else None
    f['atmos'] = num(c.get('atmosphere')) / 3 if num(c.get('atmosphere')) is not None else None
    av, cap = num(c.get('avg_attendance')), num(c.get('capacity'))
    f['crowd'] = cl(av / 50000) if av else None
    f['full'] = cl(av / cap) if av and cap else None
    f['brand'] = cl(1 - MONEY_LEAGUE.index(c['name']) / 30) if c['name'] in MONEY_LEAGUE else 0.0
    g = num(c.get('fan_governance')); f['fangov'] = g / 3 if g is not None else None
    f['rescue'] = float(bool(c.get('fan_rescue')))
    ot = c.get('owner_type')
    for k, t in (('own_local', 'local_private'), ('own_foreign', 'foreign_private'), ('own_us', 'us_sports_group'),
                 ('own_pe', 'private_equity'), ('own_state', 'state'), ('own_corp', 'corporate')):
        f[k] = 1.0 if ot == t else 0.0
    f['mc_sec'] = 1.0 if c.get('multi_club') == 'secondary' else 0.0
    f['mc_flag'] = 1.0 if c.get('multi_club') == 'flagship' else 0.0
    f['debt'] = float(bool(c.get('debt_buyout')))
    f['esl'] = {'none': 0, 'left_quickly': 1 / 3, 'left_late': 2 / 3, 'still_backing': 1}.get(c.get('super_league'), 0)
    for k, s in (('discr', 'discrimination'), ('viol', 'violence')):
        f[k] = num(c.get(s)) / 3 if num(c.get(s)) is not None else 0.0
    f['fin'] = cl((num(c.get('financial_breaches')) or 0) / 3)
    f['reloc'] = float(bool(c.get('relocated')))
    f['bet'] = float(bool(c.get('sponsor_betting'))); f['ssp'] = float(bool(c.get('sponsor_state'))); f['arms'] = float(bool(c.get('sponsor_arms')))
    tp = num(c.get('ticket_price')); f['cheap'] = (2 - tp) / 2 if tp is not None else None
    w = num(c.get('womens_team')); f['women'] = w / 3 if w is not None else None
    f['equal'] = float(bool(c.get('equal_treatment')))
    cm = num(c.get('community')); f['comm'] = cm / 2 if cm is not None else None
    st = num(c.get('style')); f['attack'] = st / 2 if st is not None else None
    my = num(c.get('manager_years')); f['stable'] = cl(my / 8) if my is not None else None
    sa = num(c.get('stadium_age')); f['ground'] = cl(sa / 80) if sa is not None else None
    d = dom.get(c['name']); f['domestic'] = d[0]['share'] if d else None
    gv = num(c.get('government')); f['gov'] = gv / 3 if nation and gv is not None else 0.0
    return f

def player_features(p):
    f = {}
    f['trophies'] = lg(num(p.get('major_trophies')) or 0, 40)
    f['awards'] = (num(p.get('individual')) or 0) / 3
    f['wc'] = cl(num(p.get('world_cup_wins')) or 0)
    caps = num(p.get('caps')); f['caps'] = cl(caps / 120) if caps is not None else None
    f['loyal'] = cl((num(p.get('longest_club_years')) or 0) / 15)
    f['oneclub'] = float(bool(p.get('one_club')))
    for k, s, m in (('captain', 'captain', 2), ('work', 'work_rate', 2), ('humble', 'humility', 2), ('fans', 'fan_relations', 2),
                    ('charity', 'charity', 2), ('flair', 'flair', 2), ('abuse', 'abuse_allegation', 2), ('racism', 'racist_abuse', 2)):
        v = num(p.get(s)); f[k] = v / m if v is not None else None
    f['speak'] = float(bool(p.get('speaks_out')))
    f['viol'] = cl((num(p.get('red_card_violence')) or 0) / 2)
    f['doping'] = float(bool(p.get('doping'))); f['fixing'] = float(bool(p.get('match_fixing')))
    f['crime'] = float(bool(p.get('tax_fraud') or p.get('criminal_other')))
    for k, s in (('money', 'money_league'), ('rival', 'rival_move'), ('ambass', 'authoritarian_ambassador'), ('forced', 'forced_transfer')):
        f[k] = float(bool(p.get(s)))
    b = num(p.get('born'))
    f['young'] = cl((34 - (2026 - b)) / 13) if b and p.get('active') else 0.0
    return f

def fill(rows):
    """Missing facts count at the average of all entries (the build has no opinion about them)."""
    keys = {k for r in rows for k in r['f']}
    for k in keys:
        xs = [r['f'][k] for r in rows if r['f'].get(k) is not None]; m = sum(xs) / len(xs) if xs else 0.5
        for r in rows:
            if r['f'].get(k) is None: r['f'][k] = m
    for r in rows: r['f'] = {k: round(v, 3) for k, v in r['f'].items()}

def rows():
    """-> (clubs, players): every entity with its features 0-1 (missing facts at the average)."""
    # The test's pool and its leagues are frozen as they were when Kevin took it (comps.json, 2026-10-12): the tracker
    # now follows six competitions, but the weights and the gut check were fitted on this pool.
    comps = json.loads((here / 'comps.json').read_text())
    perf = performance.load()
    ranks = {x['name']: x.get('fifa_rank') for x in json.loads((root / 'scripts/affinity/research/nations_perf.json').read_text())}
    dom = json.loads((root / 'scripts/affinity/research/domestic.json').read_text())
    clubs = []
    for c in load('clubs'):
        cs = comps.get(c['name'], ['xc'])
        ll = [c['lat'], c['lon']] if num(c.get('lat')) is not None and num(c.get('lon')) is not None else None
        clubs.append(dict(n=c['name'], k=c['kind'], comps=cs, label=LABEL.get(cs[0], ''), ll=ll, f=club_features(c, perf, ranks, dom)))
    players = []
    for p in load('players'):
        players.append(dict(n=p['name'], g=p.get('gender') or 'M', a=bool(p.get('active')), pos=p.get('position'), nat=p.get('nation'),
                            f=player_features(p)))
    fill(clubs); fill(players)
    return clubs, players

def main():
    clubs, players = rows()
    nations = sorted(c['n'] for c in clubs if c['k'] == 'nation')
    used = {k for c in clubs for k in c['comps']}
    data = dict(places=[list(p) for p in PLACES], nations=nations, comps=[list(c) for c in COMPS if c[0] in used], clubs=clubs, players=players)
    html = (here / 'template.html').read_text().replace('/*__DATA__*/', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    (here / 'out').mkdir(exist_ok=True)
    (here / 'out' / 'blind_test.html').write_text(html)
    print(f'{len(clubs)} clubs and nations, {len(players)} players -> scripts/blind/out/blind_test.html ({len(html):,} bytes)')

if __name__ == '__main__':
    main()
