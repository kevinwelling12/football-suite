"""Parse Wikipedia tournament squad pages into research/squads.json:
[{tournament, year, nation, player, club_text, club_title, captain}] (national team squads with each player's club).
python3 parse_squads.py <dir with saved .html pages>"""
import sys, json, re, pathlib
from bs4 import BeautifulSoup
YEAR = lambda f: int(re.search(r'(20\d\d)', f).group(1)) if re.search(r'(20\d\d)', f) else 2016  # Centenario = 2016
rows = []
for f in sorted(pathlib.Path(sys.argv[1]).glob('*.html')):
    s = BeautifulSoup(f.read_text(), 'lxml')
    for t in s.select('table.sortable'):
        head = [c.get_text(' ', strip=True) for c in t.select('tr')[0].find_all(['th', 'td'])]
        if 'Club' not in head or 'Player' not in head: continue
        h = t.find_previous('h3')
        if not h: continue
        nation = re.sub(r'\[.*?\]', '', h.get_text(' ', strip=True)).strip()
        ci, pi = head.index('Club'), head.index('Player')
        for r in t.select('tr')[1:]:
            cells = r.find_all(['th', 'td'])
            if len(cells) <= ci: continue
            links = cells[ci].find_all('a')
            club_a = next((a for a in reversed(links) if not a.find('img') and a.get_text(strip=True)), None)
            if not club_a: continue
            ptxt = cells[pi].get_text(' ', strip=True)
            rows.append(dict(tournament=f.stem, year=YEAR(f.stem), nation=nation, player=re.sub(r'\s*\(\s*(captain|vice-captain)\s*\)', '', ptxt).strip(),
                             club_text=club_a.get_text(strip=True), club_title=club_a.get('title', ''), captain='captain' in ptxt and 'vice' not in ptxt))
out = pathlib.Path(__file__).resolve().parents[1] / 'research' / 'squads.json'
out.write_text(json.dumps(rows, ensure_ascii=False, indent=0))
print(len(rows), 'players;', len({(r['tournament'], r['nation']) for r in rows}), 'squads ->', out)
