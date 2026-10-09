"""Load Kevin's preference evidence (evidence.json) for fitting and backtesting the Affinity model.

    import sys; sys.path.insert(0, 'scripts/affinity/evidence'); import load as E
    ev = E.load()                                   # all records
    E.select(ev, type='pair', kind='club_named')    # filter on any top-level field (value or list/set of values)
    E.clean(ev)                                     # drop passes, don't-knows, failed checks, summary-only records
    E.gut_clubs(ev), E.gut_players(ev)              # [(name, value 0-10, record)] with a real entity
    E.pairs(ev, domain='player', named=True)        # [(a, b, y, record)]: a/b are entity names or profile dicts
    E.backtest_split(ev)                            # {'clubs': [...], 'nations': [...], 'players': [...]} best records per target

Run directly for counts: python3 scripts/affinity/evidence/load.py
"""
import json, pathlib
from collections import Counter
HERE = pathlib.Path(__file__).resolve().parent

def load(path=HERE / 'evidence.json'):
    return json.loads(pathlib.Path(path).read_text())['records']

def meta(path=HERE / 'evidence.json'):
    return json.loads(pathlib.Path(path).read_text())['meta']

def select(recs, **kw):
    def ok(r):
        for k, v in kw.items():
            x = r.get(k)
            if isinstance(v, (list, tuple, set)):
                if x not in v: return False
            elif x != v: return False
        return True
    return [r for r in recs if ok(r)]

DROP_FLAGS = {'dont_know', 'skipped_dont_know', 'summary_only', 'scenario_not_a_club'}
def usable(r):
    """A record carries a label a model can be scored against."""
    if set(r.get('flags', [])) & DROP_FLAGS: return False
    if r['type'] == 'pair': return r.get('y') is not None
    if r['type'] in ('gut', 'likert', 'speed', 'values'): return r.get('value') is not None
    if r['type'] == 'attention': return False
    return True
def clean(recs): return [r for r in recs if usable(r)]

def entity_name(side):
    e = side.get('entity') if isinstance(side, dict) else None
    return e['name'] if e and not e.get('unmapped') else None

def gut(recs, kind):
    out = []
    for r in clean(select(recs, type='gut')):
        e = r.get('entity')
        if e and e['kind'] in kind and not e.get('unmapped'): out.append((e['name'], r['value'], r))
    return out
def gut_clubs(recs): return gut(recs, ('club',))
def gut_nations(recs): return gut(recs, ('nation',))
def gut_players(recs): return gut(recs, ('player',))

def pairs(recs, domain=None, named=None, kinds=None):
    """(a, b, y, record). Named pairs give entity names; profile pairs give the side dicts (attrs/text/values/tags)."""
    out = []
    for r in clean(select(recs, type='pair')):
        if domain and r.get('domain') != domain: continue
        if kinds and r.get('kind') not in kinds: continue
        a, b = entity_name(r['a']), entity_name(r['b'])
        is_named = a is not None and b is not None
        if named is True and not is_named: continue
        if named is False and is_named: continue
        out.append((a if is_named else r['a'], b if is_named else r['b'], r['y'], r))
    return out

def backtest_split(recs):
    """Records best suited to backtest each target (see summary.md for the reasoning)."""
    c = clean(recs)
    clubs = [r for r in c if (r['type'] == 'gut' and r.get('entity', {}).get('kind') == 'club')
             or (r['type'] == 'pair' and r.get('kind') in ('club_named', 'club_dimension'))
             or (r['type'] == 'verdict' and r.get('kind') == 'factor_override' and r['entity']['kind'] == 'club')]
    nations = [r for r in c if r.get('entity', {}).get('kind') == 'nation'
               or any(isinstance(r.get(s), dict) and r[s].get('entity', {}).get('kind') == 'nation' for s in ('a', 'b'))]
    players = [r for r in c if r.get('domain') == 'player' and (
               (r['type'] == 'gut' and r.get('entity')) or (r['type'] == 'pair' and r.get('kind') in ('player_named', 'player_profile', 'values_profile'))
               or (r['type'] == 'verdict' and r.get('kind') == 'list_position'))]
    return dict(clubs=clubs, nations=nations, players=players)

if __name__ == '__main__':
    ev = load()
    print(len(ev), 'records,', len(clean(ev)), 'usable')
    print(Counter((r['round'], r['type']) for r in ev).most_common())
    print({k: len(v) for k, v in backtest_split(ev).items()})
    print('unmapped:', meta()['unmapped'])
