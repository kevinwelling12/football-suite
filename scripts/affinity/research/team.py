"""Quiz round 3 (players and team culture): validate out3/ and preview the new Affinity.

python3 scripts/affinity/research/team.py [--write]

Takes final/<batch>.json (the agreed re-rate) and applies out3/<batch>.json:
Team (T) replaces Style, Values += V_delta (clamped 0-10), rival penalties, Republic link +2.
New weights (of 90): Values 26, Culture 26, History 14, Ownership 12, Team 12.
With --write, saves final3/<batch>.json in the same layout as final/ (S holds the Team score).
"""
import copy, json, pathlib, statistics, sys

root = pathlib.Path(__file__).resolve().parents[3]
R = root / 'scripts' / 'affinity' / 'research'
OLD_W = dict(C=26, V=28, H=16, O=12, S=8)
NEW_W = dict(C=26, V=26, H=14, O=12, S=12)
RIVALS = {'Schalke 04': -5, 'Bayern Munich': -5, 'Seattle Sounders FC': -5, 'Seattle Reign': -5,
          'Vancouver Whitecaps FC': -5, 'Everton': -2}
HOMETOWN = 'Sacramento Republic FC'
F = 'CVHOS'

# Kevin's answers to the round 3 review (2026-09-28).
# Values change from players, overriding the agent's V_delta: name -> (points, reason)
V_OVERRIDE = {
    # Standing by: not after an acquittal (or a closed investigation without charge)
    'Real Madrid': (0, 'Asencio acquitted Sept 2026'),
    'Fleetwood Town': (0, 'Ched Evans acquitted at the 2016 retrial'),
    'Iceland': (0, 'Gudmundsson acquitted; Sigurdsson investigation dropped without charge'),
    # Staff and owner conduct toward players moves to Ownership (O_DELTA below)
    'Seattle Sounders FC': (0, 'owner conduct moved to Ownership'),
    'Philadelphia Union': (0, 'Tanner moved to Ownership; Wagner slur ban (2023) is outside the 3-season window'),
    'Chelsea': (-1, 'Enzo Fernandez chant; training-group exile moved to Ownership'),
    'Paris Saint-Germain': (-2, 'standing by Hakimi; Mbappe wages and exclusions moved to Ownership'),
    'Barcelona': (0, 'ter Stegen treatment and registrations moved to Ownership'),
    'Mainz 05': (0, 'El Ghazi dismissal moved to Ownership'),
    'Rayo Vallecano': (0, 'missing medical services moved to Ownership'),
    'Sheffield United': (0, 'Cusack case (coach, club inquiry) moved to Ownership'),
    # Previous owner (Chansiri): dropped under the previous-owner rule
    'Sheffield Wednesday': (0, 'late wages under the previous owner'),
    # Homegrown +1 dropped where Values already credits the academy pathway
    'Crewe Alexandra': (0, 'academy already in Values'), 'SC Freiburg': (0, 'academy already in Values'),
    'Athletic Club': (0, 'cantera already in Values'), 'Celta Vigo': (0, 'academy already in Values'),
    'Osasuna': (0, 'academy already in Values'), 'Real Sociedad': (0, 'academy already in Values'),
    'Shakhtar Donetsk': (0, 'academy already in Values'),
}
# Staff and owner conduct toward players: Ownership change, name -> (points, reason)
O_DELTA = {
    'Seattle Sounders FC': (-1, 'owner confronted players over their 2025 prize-money protest'),
    'Philadelphia Union': (-1, 'sporting director Tanner suspended for sexist, anti-gay and racist remarks'),
    'Chelsea': (-1, 'players exiled to a separate training group (PFA intervened)'),
    'Paris Saint-Germain': (-1, 'Mbappe unpaid wages (about EUR 61m ordered) and player exclusions'),
    'Barcelona': (-1, 'ter Stegen disciplinary case, players left unregistered'),
    'Mainz 05': (-1, 'El Ghazi dismissal ruled unfair'),
    'Rayo Vallecano': (-1, 'squad complaint to AFE over missing medical services'),
    'Sheffield United': (-1, 'Maddy Cusack case: warned about the coach, flawed club inquiry'),
}
# Republic link: regulars only. None = not yet checked (agent value used, flagged in the report).
# Checked 2026-09-27 against ESPN league lineups. Only clubs in a higher tier than Republic (USL Championship)
# count: a former Republic player who moved up. USL clubs with Republic regulars (Colorado Springs, Monterey Bay,
# New Mexico, San Antonio, Tampa Bay, Pittsburgh, Indy Eleven) get nothing.
REPUBLIC_REGULARS = {
    'Los Angeles Football Club',        # Aaron Long, captain, starts when fit
}


def score(e, w, nation, bonus):
    f = {k: e[k]['score'] for k in F}
    adj = sum(a['points'] for a in e['adjustments'])
    b = bonus.get(e['name'], 0) if nation else (4.0 if e['name'] == HOMETOWN else 0)
    return round(max(0, sum(w[k] * f[k] for k in F) / 90 * 10 + adj) + b, 1)


bonus = {}
for comp in json.loads((root / 'data' / 'suite_data.json').read_text()).values():
    for t in comp['teams']:
        bonus[t['name']] = t.get('bonus') or 0

errors, rows, flags = [], [], []
if '--write' in sys.argv:
    (R / 'final3').mkdir(exist_ok=True)
for bf in sorted(R.glob('b[0-9][0-9]-*.json')):
    batch, nation = bf.stem, bf.stem.startswith(('b10', 'b11'))
    fin = json.loads((R / 'final' / f'{batch}.json').read_text())
    of = R / 'out3' / f'{batch}.json'
    if not of.exists():
        errors.append(f'{batch}: no output yet'); continue
    o3 = {e.get('name'): e for e in json.loads(of.read_text())}
    new = []
    for e in fin:
        n, x = e['name'], o3.get(e['name'])
        if not x:
            errors.append(f'{batch}: missing {n}'); continue
        t = (x.get('T') or {}).get('score')
        vd = (x.get('V_delta') or {}).get('points', 0)
        if not isinstance(t, int) or not 0 <= t <= 10: errors.append(f'{batch}: {n} T {t!r}')
        if not isinstance(vd, int) or not -5 <= vd <= 2: errors.append(f'{batch}: {n} V_delta {vd!r}')
        if len(x.get('sources') or []) < 2: errors.append(f'{batch}: {n} sources {len(x.get("sources") or [])}')
        if not isinstance(t, int) or not isinstance(vd, int): continue
        m = copy.deepcopy(e)
        m['S'] = {'score': t, 'evidence': x['T'].get('evidence', '')}
        vev = x['V_delta'].get('evidence', '')
        if n in V_OVERRIDE:
            vd, why = V_OVERRIDE[n]
            vev = f'{vev} [Review: {vd:+d}, {why}.]'
        if vd:
            v = max(0, min(10, e['V']['score'] + vd))
            m['V'] = {'score': v, 'evidence': e['V']['evidence'] + f' [Players: {vd:+d}. {vev}]'}
        if n in O_DELTA:
            od, why = O_DELTA[n]
            m['O'] = {'score': max(0, min(10, e['O']['score'] + od)), 'evidence': e['O']['evidence'] + f' [Players: {od:+d}, {why}.]'}
        if n in RIVALS:
            m['adjustments'] = m['adjustments'] + [{'type': 'rival', 'points': RIVALS[n], 'evidence': 'Rival of a club Kevin follows.'}]
        link = (x.get('republic_link') or {}).get('value')
        if REPUBLIC_REGULARS is not None:
            link = n in REPUBLIC_REGULARS
        if link and n != HOMETOWN:
            m['adjustments'] = m['adjustments'] + [{'type': 'republic', 'points': 2, 'evidence': x['republic_link'].get('evidence', '')}]
        m['team'] = {k: x.get(k) for k in ('icons', 'coach', 'flags', 'confidence', 'sources')}
        new.append(m)
        rows.append(dict(name=n, batch=batch, s=e['S']['score'], t=t, vd=vd,
                         old=score(e, OLD_W, nation, bonus), new=score(m, NEW_W, nation, bonus), conf=x.get('confidence')))
        flags += [f'[{batch[:3]}] {n}: {fl}' for fl in x.get('flags') or []]
    if '--write' in sys.argv:
        (R / 'final3' / f'{batch}.json').write_text(json.dumps(new, ensure_ascii=False, indent=1) + '\n')

print(f'Validation: {len(rows)} entries, {len(errors)} problem(s)')
for x in errors: print('  ' + x)
if not rows: sys.exit()
print('\nTeam vs old Style, mean by batch')
for b in sorted({r['batch'] for r in rows}):
    rs = [r for r in rows if r['batch'] == b]
    print(f'  {b:30} T {statistics.mean(r["t"] for r in rs):4.1f}  S {statistics.mean(r["s"] for r in rs):4.1f}  '
          f'V_delta total {sum(r["vd"] for r in rs):+d}')
ch = sorted(rows, key=lambda r: r['new'] - r['old'])
fmt = lambda r: f'  {r["name"]:28} {r["old"]:5.1f} -> {r["new"]:5.1f} ({r["new"] - r["old"]:+.1f})  S {r["s"]} -> T {r["t"]}  V {r["vd"]:+d}'
print('\nBiggest drops'); [print(fmt(r)) for r in ch[:15]]
print('\nBiggest rises'); [print(fmt(r)) for r in ch[::-1][:15]]
print('\nKevin\'s clubs')
for n in ['Liverpool', 'Borussia Dortmund', 'Portland Timbers', 'Portland Thorns', HOMETOWN]:
    [print(fmt(r)) for r in rows if r['name'] == n]
print('\nV_delta != 0: ' + ', '.join(f'{r["name"]} {r["vd"]:+d}' for r in rows if r['vd']))
print('Low confidence: ' + ', '.join(r['name'] for r in rows if r['conf'] == 'low'))
print('\nFlags'); [print('  ' + f) for f in flags]
