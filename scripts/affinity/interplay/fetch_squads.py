"""Fetch Wikipedia pages for domestic-share research: each club's article (current squad) and its season pages
for every other season back to 2016 (2024-25, 2022-23, ... or 2025, 2023, ... for calendar leagues).
Polite: one request every 2 s, backs off on 429. Pages cached in <cache dir>; re-runs skip cached pages.
python3 fetch_squads.py <cache dir>"""
import json, sys, time, pathlib, urllib.request, urllib.parse
here = pathlib.Path(__file__).parent
T = json.loads((here / 'wiki_titles.json').read_text())
T.update({'SV Elversberg': 'SV 07 Elversberg', 'Portland Thorns': 'Portland Thorns FC', 'Racing Louisville': 'Racing Louisville FC',
          'Rhode Island FC': 'Rhode Island FC', 'Sporting JAX': 'Sporting JAX', 'Accrington Stanley': 'Accrington Stanley F.C.',
          'York City': 'York City F.C.', 'Brooklyn FC': 'Brooklyn FC'})
rows = json.loads((here.parent / 'family' / 'clubs.json').read_text()); comp = {r[0]: r[1] for r in rows}
CAL = {'mls', 'nwsl', 'usl'}
cache = pathlib.Path(sys.argv[1]); cache.mkdir(parents=True, exist_ok=True)
def get(title):
    f = cache / (title.replace('/', '_') + '.html')
    if f.exists(): return
    u = 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(title.replace(' ', '_'))
    for i in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'football-suite research (personal project)'}), timeout=40) as r:
                f.write_bytes(r.read()); break
        except urllib.error.HTTPError as e:
            if e.code == 404: f.write_text(''); break
            time.sleep(30 * (i + 1))
        except Exception:
            time.sleep(10 * (i + 1))
    time.sleep(2)
todo = []
for n, t in T.items():
    todo.append(t)
    for i in range(0, 10, 2):
        todo.append(f'{2025 - i} {t} season' if comp[n] in CAL else f'{2025 - i}–{str(2026 - i)[2:]} {t} season')
for k, t in enumerate(todo):
    get(t)
    if k % 50 == 0: print(k, len(todo), t, flush=True)
(here / 'fetch_plan.json').write_text(json.dumps(T, ensure_ascii=False, indent=0))
print('done', len(todo))
