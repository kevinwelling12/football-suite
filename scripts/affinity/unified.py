"""One run for the whole Affinity system, clubs and players together (Kevin, 2026-10-07).

  python3 scripts/affinity/unified.py [--fit]

1. Clubs: rescore.py rebuilds every club and nation, now with players_link.py (Player Affinity for a club's best
   current players lifts Team, for its icons lifts History).
2. Players: players/model.py rates every player; connection reads the club Affinity just written.
   The club side reads Player Affinity without connection, so neither side echoes the other and one pass is exact.
   --fit refits the player weights (players/fit.py) to Kevin's quiz answers first.
3. players/build_lists.py rebuilds the four lists; data/players.json is the copy the app shows (Affinity > Players).
Then python3 scripts/build.py builds the app.
"""
import json, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parents[2]
A = root / 'scripts' / 'affinity'
run = lambda *a: subprocess.run([sys.executable, *map(str, a)], check=True, cwd=root, stdout=subprocess.DEVNULL)
run(A / 'rescore.py')
if '--fit' in sys.argv: run(A / 'players' / 'fit.py')
run(A / 'players' / 'model.py')
run(A / 'players' / 'build_lists.py')
L = json.loads((A / 'players' / 'lists.json').read_text())
keep = lambda p: dict(n=p['n'], a=p['a'], f=p['f'], c=p['c'], p=p['p'], nat=p.get('nat'), pos=p.get('pos'), clubs=p['clubs'][-2:],
                      why=(p.get('why') or '')[:240], pen=[x[:90] for x in p.get('pen', [])][:3], nw=p.get('nw'))
(root / 'data' / 'players.json').write_text(json.dumps({k: [keep(p) for p in v] for k, v in L.items()}, ensure_ascii=False, separators=(',', ':')))
print('unified: clubs rescored, players rated,', sum(map(len, L.values())), 'list entries written to data/players.json')
