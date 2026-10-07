"""Build the four Player Affinity lists (lists.json) and the page from ratings.json (run model.py first).

Usage: python3 scripts/affinity/players/build_lists.py [out.html]
"""
import json, pathlib, re, sys
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here)); import model as M
LABEL = {'b01': 'Racist abuse', 'b02': 'Abuse allegations', 'b03': 'Doping', 'b04': 'Match-fixing', 'b05': 'Tax fraud',
         'b06': 'Violent conduct', 'b08': 'Forced transfer', 'b09': 'Rival move', 'b10': 'Saudi move', 'b12': 'Authoritarian ambassador'}
NWSL = re.compile(r'thorns|kansas city current|orlando pride|washington spirit|north carolina courage|gotham|seattle reign|san diego wave|'
                  r'red stars|chicago stars|angel city|bay fc|utah royals|houston dash|racing louisville|denver summit|boston legacy', re.I)
SIZE = {'ma': 75, 'mt': 75, 'wa': 30, 'wt': 30}

def entry(r, p, s):
    clubs = []
    for c in sorted(p.get('clubs', []), key=lambda c: c.get('from') or 0):
        if c.get('club') and c['club'] not in clubs and not re.search(r'\b(II|B|U\d+|youth|academy)\b', c['club'], re.I): clubs.append(c['club'])
    pen = [f"{LABEL[e['type']]} ({e.get('year', '?')}): {e.get('what', '')}" for e in (p.get('incidents') or []) + (p.get('money_moves') or [])
           if e.get('type') in M.SEV]
    why = re.sub(r'\(?\banchors?\b\)?\s*', '', s.get('why', ''))
    return dict(n=r['name'], a=r['aff'], f=[s[k] for k in ['CH', 'WK', 'LO', 'AB', 'ST', 'LE']], c=r['conn'], ps=r.get('pos', 0), p=r['pen'],
                nat=(p.get('national') or {}).get('team') or p.get('nation'), pos='/'.join(p.get('positions') or []), clubs=clubs,
                why=why, pen=pen, nw=next((c['club'] for c in p.get('clubs', []) if not c.get('to') and NWSL.search(c.get('club') or '')), None))

if __name__ == '__main__':
    facts, scores = M.load()
    R = json.load(open(here / 'ratings.json'))
    L = {k: [] for k in SIZE}
    for r in R:  # already sorted by Affinity
        e = entry(r, facts[r['name']], scores[r['name']]); g = 'w' if r['gender'] in ('F', 'female', 'w', 'W') else 'm'
        for k in (g + 'a', g + 't') if r['active'] else (g + 't',):
            if len(L[k]) < SIZE[k]: L[k].append(e)
    json.dump(L, open(here / 'lists.json', 'w'), ensure_ascii=False, indent=1)
    if len(sys.argv) > 1:
        t = (here / 'page.template.html').read_text()
        pathlib.Path(sys.argv[1]).write_text(t.replace('/*__LISTS__*/', json.dumps(L, ensure_ascii=False)))
    for k, v in L.items(): print(k, len(v), ', '.join(f"{p['n']} {p['a']}" for p in v[:10]))
