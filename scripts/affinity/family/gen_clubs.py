"""Regenerate clubs.json for the Family Club Draft from data/suite_data.json and research/out (history and
fan-culture blurbs). Run after a re-rate, then build.py.
Row: [name, comp, league label, country, colour, abbr, C, V, H, O, S, adj, P, miles from Sacramento or None,
      history, fans, kevin]. adj leaves out Kevin's own items (rivals, the Republic link); kevin holds them."""
import json, glob, re, pathlib
root = pathlib.Path(__file__).resolve().parents[3]
D = json.loads((root / 'data/suite_data.json').read_text())
PR = ['epl', 'bl', 'esp', 'ita', 'fra', 'mls', 'nwsl', 'ch', 'usl', 'ucl', 'cup']
UCL = {'AEK Athens':'Greece', 'Bodø/Glimt':'Norway', 'Club Brugge':'Belgium', 'Fenerbahçe':'Türkiye', 'Feyenoord':'Netherlands',
       'Galatasaray':'Türkiye', 'LASK':'Austria', 'PSV Eindhoven':'Netherlands', 'Porto':'Portugal', 'Sabah':'Azerbaijan',
       'Shakhtar Donetsk':'Ukraine', 'Slavia Prague':'Czechia', 'Slovan Bratislava':'Slovakia', 'Sporting CP':'Portugal', 'Viking':'Norway'}
CO = {'epl':'England', 'ch':'England', 'cup':'England', 'bl':'Germany', 'esp':'Spain', 'ita':'Italy', 'fra':'France', 'mls':'USA', 'nwsl':'USA', 'usl':'USA'}
LG = {'epl':'Premier League', 'ch':'Championship (England tier 2)', 'cup':'English lower leagues', 'bl':'Bundesliga', 'esp':'LaLiga', 'ita':'Serie A',
      'fra':'Ligue 1', 'mls':'MLS', 'nwsl':"NWSL (women's)", 'usl':'USL Championship', 'ucl':'Champions League'}
CANADA = {'CF Montréal', 'Toronto FC', 'Vancouver Whitecaps FC'}
ev = {}
for f in glob.glob(str(root / 'scripts/affinity/research/out/b0*.json')):
    for c in json.load(open(f)): ev[c['name']] = c
def cut(s, n):
    s = re.sub(r'\s+', ' ', s or '').strip()
    if len(s) <= n: return s
    out = ''
    for p in re.split(r'(?<=[.;])\s', s):
        if len(out) + len(p) + 1 > n: break
        out = (out + ' ' + p).strip()
    return (out or s[:n].rsplit(' ', 1)[0] + '…').rstrip(';')
def kevin_part(note):
    tot = 0.0
    for p in (note or '').split(';'):
        m = re.match(r'\s*(Rival|Republic link) ([+-][\d.]+)', p)
        if m: tot += float(m.group(2))
    return tot
rows, seen = [], set()
for k in PR:
    for t in D[k]['teams']:
        n = t['name']
        if n in seen: continue
        seen.add(n); h = t['hai']
        mi = next((int(m.group(1).replace(',', '')) for lab, _ in h.get('us') or [] for m in [re.match(r'([\d,]+) mi from Sacramento', lab)] if m), None)
        if n == 'Sacramento Republic FC': mi = 0
        kv = kevin_part(h.get('note')); e = ev.get(n, {})
        rows.append([n, k, LG[k], 'Canada' if n in CANADA else UCL.get(n) or CO[k], t.get('color') or '#888888', t.get('abbr') or '',
                     h['C'], h['V'], h['H'], h['O'], h['S'], round(h['adj'] - kv, 1), h['P'], mi,
                     cut(e.get('H', {}).get('evidence', ''), 210), cut(e.get('C', {}).get('evidence', ''), 170), kv])
(pathlib.Path(__file__).parent / 'clubs.json').write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')))
print(len(rows), 'clubs;', [r[0] + ' ' + str(r[16]) for r in rows if r[16]])
