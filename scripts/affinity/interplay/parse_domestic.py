"""Domestic share per club and season from cached Wikipedia pages (fetch_squads.py): the share of squad-list
players whose flag is the club's own country. -> research/domestic.json {club: [{s, age, share, n}]}
python3 parse_domestic.py <cache dir>"""
import json, re, sys, pathlib, urllib.parse
from bs4 import BeautifulSoup
here = pathlib.Path(__file__).parent
T = json.loads((here / 'fetch_plan.json').read_text())
rows = json.loads((here.parent / 'family' / 'clubs.json').read_text()); comp = {r[0]: r[1] for r in rows}; co = {r[0]: r[3] for r in rows}
CAL = {'mls', 'nwsl', 'usl'}
WALES = {'Swansea City', 'Cardiff City', 'Wrexham', 'Newport County'}
COUNTRY = {'USA': 'United States', 'Türkiye': 'Turkey', 'Czechia': 'Czech Republic'}
cache = pathlib.Path(sys.argv[1])
BAD_H = re.compile(r'statistic|transfer|loan|appearance|scorer|goal|disciplin|award|contract|staff|management|kit|result|fixture|in\b|out\b|reserve|academy|youth|women|b team|ii\b', re.I)
GOOD_H = re.compile(r'squad|roster|players|first.team|current', re.I)
def flag(img):
    m = re.search(r'Flag_of_(.+?)\.svg', img.get('resource', '') + img.get('src', ''))
    if not m: return None
    n = urllib.parse.unquote(m.group(1)).replace('_', ' ')
    n = re.sub(r'\s*\(.*\)$', '', n); n = re.sub(r'^the ', '', n)
    return n
def squad_flags(html):
    s = BeautifulSoup(html, 'lxml')
    # tables that come after a squad-like heading (and before the next heading)
    for h in s.find_all(['h2', 'h3', 'h4']):
        t = h.get_text(' ', strip=True)
        if not GOOD_H.search(t) or BAD_H.search(t): continue
        fl, seen = [], set()
        for el in h.find_all_next():
            if el.name in ('h2', 'h3') or (el.name == 'h4' and fl): break
            if el.name == 'table':
                head = el.find('tr').get_text(' ', strip=True) if el.find('tr') else ''
                if re.search(r'\bFee\b|Transferred|Loaned', head): continue
                for tr in el.find_all('tr'):
                    if id(tr) in seen or tr.find('tr'): continue
                    seen.add(id(tr))
                    img = tr.select_one('span.flagicon img, img[resource*="Flag_of"]')
                    if img and (f := flag(img)): fl.append(f)
        if len(fl) >= 11: return fl
    return None
out = {}
for n, t in T.items():
    home = 'Wales' if n in WALES else COUNTRY.get(co[n], co[n])
    ss = []
    pages = [(t, 0, 'now')] + [((f'{2025 - i} {t} season' if comp[n] in CAL else f'{2025 - i}–{str(2026 - i)[2:]} {t} season'), i + 1 if comp[n] not in CAL else i + 1, str(2025 - i)) for i in range(0, 10, 2)]
    for title, age, lab in pages:
        f = cache / (title.replace('/', '_') + '.html')
        if not f.exists() or not f.stat().st_size: continue
        fl = squad_flags(f.read_text())
        if fl: ss.append({'s': lab, 'age': age, 'share': round(sum(x == home for x in fl) / len(fl), 3), 'n': len(fl)})
    if ss: out[n] = ss
(here.parent / 'research' / 'domestic.json').write_text(json.dumps(out, ensure_ascii=False, indent=0))
print(len(out), 'clubs with data of', len(T))
