"""Build evidence.json: every labelled observation of Kevin's preferences, one record each.

Reads the quiz folders (read-only) and writes only scripts/affinity/evidence/evidence.json.
Usage: python3 scripts/affinity/evidence/build.py
Schema and provenance: README.md in this folder. Loader: load.py.
"""
import ast, glob, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
AFF = HERE.parent
ROOT = AFF.parents[1]
def J(p): return json.loads((AFF / p).read_text()) if not str(p).startswith('/') else json.loads(pathlib.Path(p).read_text())
def raw(r):
    d = J(f'{r}/raw/responses/kevin.json'); return d.get('data', d)
def rel(p): return str((AFF / p).relative_to(ROOT))

# ---------------------------------------------------------------- name catalogs
def literal(path, var):
    for n in ast.parse(path.read_text()).body:
        if isinstance(n, ast.Assign) and any(getattr(t, 'id', None) == var for t in n.targets):
            return ast.literal_eval(n.value)
S = literal(AFF / 'scores.py', 'S')
USL = literal(ROOT / 'scripts/importers/build_usl.py', 'A')
SUITE = json.loads((ROOT / 'data/suite_data.json').read_text())
NE = json.loads((ROOT / 'data/nations_extra.json').read_text())
NATIONS = {t['name'] for t in SUITE['unl']['teams']} | {t['name'] for t in NE['teams']}
COMP = {}
for k in SUITE:
    for t in SUITE[k]['teams']: COMP.setdefault(t['name'], []).append(k)
for c in NE['clubs']: COMP.setdefault(c['name'], []).append('heritage')
CLUBS = (set(S) | set(USL)) - NATIONS
RATINGS = json.loads((AFF / 'players/ratings.json').read_text())
PLAYERS = {r['name']: r for r in RATINGS}
UNMAPPED = []

def ent(name, where, kind=None):
    """Resolve a real name to the catalog. kind: club|nation|player (None = club or nation)."""
    if kind == 'player':
        if name in PLAYERS: return dict(name=name, kind='player', gender=PLAYERS[name]['gender'], active=PLAYERS[name]['active'])
        UNMAPPED.append(dict(name=name, kind='player', where=where, reason='not in players/ratings.json'))
        return dict(name=name, kind='player', unmapped=True)
    if name in NATIONS: return dict(name=name, kind='nation', comps=COMP.get(name, []))
    if name in CLUBS:
        src = 'scores.py' if name in S else 'build_usl.py'
        return dict(name=name, kind='club', comps=COMP.get(name, []), factors_in=src)
    UNMAPPED.append(dict(name=name, kind=kind or 'club', where=where, reason='not in scores.py S / build_usl.py A'))
    return dict(name=name, kind=kind or 'club', unmapped=True)

REC = []
def add(**r):
    r = {k: v for k, v in r.items() if v is not None or k in ('y', 'value', 'winner')}
    r.setdefault('flags', [])
    REC.append(r)
def side(ans, a='l', b='r'):  # canonical answer -> choice / y
    m = {a: ('a', 1.0), b: ('b', 0.0), 't': ('tie', 0.5)}
    if ans in m: return m[ans]
    return ({'skip': 'skip', 'pb': 'pass_both', 'pl': 'pass_a', 'pr': 'pass_b'}.get(ans, ans), None)
def shown(order, qid):  # which canonical side was displayed first/left
    for o in order or []:
        if o.get('id') == qid and 'flip' in o: return 'b' if o['flip'] else 'a'
    return None

# ---------------------------------------------------------------- round 4: The Blind Draw (2026-09-29)
def round4():
    r, date = 'q4', '2026-09-29'
    K, Q, A = J('quiz4/key.json'), J('quiz4/questions.json'), J('quiz4/answers.json')
    ans, ms, order = A['answers'], A['times'], A['order']
    res = J('quiz4/results.json'); model_then = {n: a for n, g, a in res['gut']}
    ev = {q['id']: q for q in Q['everyday']}
    partners = {'k1': ['e05', 'e28'], 'k2': ['e12', 'e13'], 'k3': ['e14', 'e21']}
    for qid, keys in K['everyday'].items():
        q, v = ev[qid], ans.get(qid)
        if q.get('attention'):
            add(id=f'{r}.{qid}', type='attention', round=r, date=date, qid=qid, prompt=q['prompt'], value=v,
                correct=1, passed=v == 1, ms=ms.get(qid), source=rel('quiz4/answers.json'))
        elif q.get('check'):
            c = next(iter(keys[0])); sign = 1 if keys[4][c] > 0 else -1
            add(id=f'{r}.{qid}', type='likert', round=r, date=date, qid=qid, domain='club', prompt=q['prompt'],
                construct=c, sign=sign, value=v, scale=[0, 4], scale_labels=q['options'], loading=keys[v].get(c, 0),
                reversed=sign < 0, check_of=partners[qid], ms=ms.get(qid), source=rel('quiz4/answers.json'))
        else:
            add(id=f'{r}.{qid}', type='everyday', round=r, date=date, qid=qid, domain='club', prompt=q['prompt'],
                options=[dict(text=t, loadings=k) for t, k in zip(q['options'], keys)], choice=v,
                loadings=keys[v] if isinstance(v, int) else None, ms=ms.get(qid), source=rel('quiz4/answers.json'))
    pq = {p['id']: p for p in Q['pairs']}
    for qid, (fa, fb) in K['pairs'].items():
        c, y = side(ans[qid], 'a', 'b')
        add(id=f'{r}.{qid}', type='tradeoff', round=r, date=date, qid=qid, domain='club', method='ipsative forced choice',
            a=dict(construct=fa, text=pq[qid]['a']), b=dict(construct=fb, text=pq[qid]['b']), choice=c, y=y,
            winner=fa if y == 1 else fb, shown_first=shown(order, qid), ms=ms.get(qid), source=rel('quiz4/answers.json'))
    at = Q['attrs']
    def prof(lv): return dict(attrs={a['k']: l for a, l in zip(at, lv)}, text={a['k']: a['levels'][l] for a, l in zip(at, lv)})
    for d in K['dce']:
        c, y = side(ans[d['id']], 'a', 'b')
        fl = ['fast_response_under_1s'] if ms.get(d['id'], 9999) < 1000 else []
        add(id=f'{r}.{d["id"]}', type='pair', kind='club_profile', round=r, date=date, qid=d['id'], domain='club',
            a=prof(d['a']), b=prof(d['b']), choice=c, y=y, ms=ms.get(d['id']), flags=fl, source=rel('quiz4/answers.json'),
            attr_levels={a['k']: a['levels'] for a in at},
            note='levels 0-2 ordinal, higher = more of the trait; BAG: 0 nothing, 1 sportsbook shirt sponsor, 2 ultras linked to violence')
    rt = {x['id']: x['text'] for x in Q['rate']}
    for qid, name in K['rate'].items():
        add(id=f'{r}.{qid}', type='gut', round=r, date=date, qid=qid, domain='club', entity=ent(name, f'{r}.{qid}'),
            anonymous=True, text=rt[qid], value=ans[qid], scale=[0, 10], model_at_time=model_then.get(name),
            ms=ms.get(qid), flags=['blind_vignette_recognisable'], source=rel('quiz4/answers.json'))

# ---------------------------------------------------------------- round 5: The Blind Draw II (2026-09-29)
def round5():
    r, date = 'q5', '2026-09-29'
    K, Q, A = J('quiz5/key.json'), J('quiz5/questions.json'), J('quiz5/answers.json')
    ans, ms = A['answers'], A['times']
    res = J('quiz5/results.json')
    ev = {q['id']: q for q in Q['everyday']}
    partners = {'g1': ['f09', 'f20'], 'g2': ['f10']}
    for qid, keys in K['everyday'].items():
        q, v = ev[qid], ans.get(qid)
        if q.get('attention'):
            add(id=f'{r}.{qid}', type='attention', round=r, date=date, qid=qid, prompt=q['prompt'], value=v, correct=2,
                passed=v == 2, ms=ms.get(qid), source=rel('quiz5/answers.json'))
        elif q.get('check'):
            c = next(iter(keys[0])); sign = 1 if keys[4][c] > 0 else -1
            add(id=f'{r}.{qid}', type='likert', round=r, date=date, qid=qid, domain='club', prompt=q['prompt'], construct=c,
                sign=sign, value=v, scale=[0, 4], scale_labels=q['options'], loading=keys[v].get(c, 0), reversed=sign < 0,
                check_of=partners[qid], ms=ms.get(qid), source=rel('quiz5/answers.json'))
        else:
            add(id=f'{r}.{qid}', type='everyday', round=r, date=date, qid=qid, domain='club', prompt=q['prompt'],
                options=[dict(text=t, loadings=k) for t, k in zip(q['options'], keys)], choice=v, loadings=keys[v],
                ms=ms.get(qid), source=rel('quiz5/answers.json'))
    bq = {b['id']: b for b in Q['budget']}
    for bid, cons in K['budget'].items():
        pts = ans[bid]
        add(id=f'{r}.{bid}', type='budget', round=r, date=date, qid=bid, domain='club', prompt=bq[bid]['prompt'],
            items=[dict(construct=c, text=t, points=p) for c, t, p in zip(cons, bq[bid]['items'], pts)], total=sum(pts),
            ms=ms.get(bid), source=rel('quiz5/answers.json'))
    mq = {m['id']: m for m in Q['maxdiff']}
    for mid, items in K['maxdiff'].items():
        a = ans[mid]
        add(id=f'{r}.{mid}', type='maxdiff', round=r, date=date, qid=mid, domain='club', prompt='Of these four, which is worst, and which is least bad?',
            items=[dict(construct=c, text=t) for c, t in zip(items, mq[mid]['items'])], worst=items[a['w']], best=items[a['b']],
            polarity='baggage: worst = most damaging, best = least bad', ms=ms.get(mid), source=rel('quiz5/answers.json'))
    at = Q['attrs']
    def prof(lv): return dict(attrs={a['k']: l for a, l in zip(at, lv)}, text={a['k']: a['levels'][l] for a, l in zip(at, lv)})
    for d in K['dce']:
        c, y = side(ans[d['id']], 'a', 'b')
        add(id=f'{r}.{d["id"]}', type='pair', kind='club_profile', round=r, date=date, qid=d['id'], domain='club',
            a=prof(d['a']), b=prof(d['b']), choice=c, y=y, ms=ms.get(d['id']), source=rel('quiz5/answers.json'),
            attr_levels={a['k']: a['levels'] for a in at},
            note='levels 0-2; TROPHY: 0 none in 20 years, 1 league title 12 years ago, 2 cup last season (nominal); BAGT: 0 clean, 1 ultras violence 8 years ago, 2 last season')
    sq = {s['id']: s['text'] for s in Q['speed']}
    for sid, (c, sign) in K['speed'].items():
        fl = []
        if sid == 's17': fl.append('ambiguous_wording')  # "Ultras banned for violence": a ban can read as the club acting well
        if sid == 's22': fl.append('conflicts_with_q5.b2_old_ground_50')
        add(id=f'{r}.{sid}', type='speed', round=r, date=date, qid=sid, domain='club', text=sq[sid], construct=c, sign=sign,
            value=ans[sid], agrees=ans[sid] == sign, ms=ms.get(sid), flags=fl, source=rel('quiz5/answers.json'),
            note='value +1 pulls me in, -1 pushes me away; sign = expected direction if the construct is liked; faster = stronger')
    rt = {x['id']: x['text'] for x in Q['rate']}
    for qid, name in K['rate'].items():
        add(id=f'{r}.{qid}', type='gut', round=r, date=date, qid=qid, domain='club', entity=ent(name, f'{r}.{qid}'),
            anonymous=True, text=rt[qid], value=ans[qid], scale=[0, 10], model_at_time=res['gut'][name][1],
            ms=ms.get(qid), flags=['blind_vignette_recognisable', 'holdout_for_round4_model'], source=rel('quiz5/answers.json'))

# ---------------------------------------------------------------- round 6: This or That (2026-09-29)
def round6():
    r, date = 'q6', '2026-09-29'
    K, Q, A = J('quiz6/key.json'), J('quiz6/questions.json'), J('quiz6/answers.json')
    ans, ms = A['answers'], A['times']; q = {x['id']: x for x in Q}
    for qid, load in K['everyday'].items():
        v = ans[qid]; neg = {k: -x for k, x in load.items()}
        add(id=f'{r}.{qid}', type='everyday', round=r, date=date, qid=qid, domain='club', prompt='This or that',
            options=[dict(text=q[qid]['l'], loadings=load), dict(text=q[qid]['r'], loadings=neg)], choice=0 if v == 'l' else 1,
            loadings=load if v == 'l' else neg, ms=ms.get(qid), source=rel('quiz6/answers.json'))
    for qid, (ca, cb) in K['traits'].items():
        c, y = side(ans[qid])
        add(id=f'{r}.{qid}', type='tradeoff', round=r, date=date, qid=qid, domain='club', method='paired comparison of club traits',
            a=dict(construct=ca, text=q[qid]['l']), b=dict(construct=cb, text=q[qid]['r']), choice=c, y=y,
            winner=ca if y == 1 else cb, ms=ms.get(qid), source=rel('quiz6/answers.json'))
    for qid, (na, nb, aa, ab) in K['clubs'].items():
        c, y = side(ans[qid])
        add(id=f'{r}.{qid}', type='pair', kind='club_named', round=r, date=date, qid=qid, domain='club',
            a=dict(entity=ent(na, f'{r}.{qid}'), model_at_time=aa), b=dict(entity=ent(nb, f'{r}.{qid}'), model_at_time=ab),
            choice=c, y=y, winner=na if y == 1 else nb, ms=ms.get(qid), flags=['familiarity_bandwidth_confound'],
            source=rel('quiz6/answers.json'), note='pairs drawn within 8 Affinity points, different leagues; ~2.6 s per pick')

# ---------------------------------------------------------------- Cascadia decider (2026-09-30)
def cascadia():
    r, date, base = 'cascadia', '2026-09-30', 'research/cascadia'
    K, Q, A = J(f'{base}/key.json'), J(f'{base}/questions.json'), J(f'{base}/answers.json')
    ans, ms = A['answers'], A['times']
    POR, SEA = ent('Portland Timbers', r), ent('Seattle Sounders FC', r)
    dims = {d['id']: d['name'] for d in Q['dims']}
    for d, name in dims.items():
        add(id=f'{r}.i_{d}', type='likert', round=r, date=date, qid=f'i_{d}', domain='club', prompt='How much does this matter in choosing between two clubs?',
            construct=f'cascadia:{d}', text=name, value=ans[f'i_{d}'], scale=[0, 5], scale_labels={'0': 'Not at all', '1': 'A little', '2': 'Some', '3': 'A lot', '5': 'Decisive'},
            ms=ms.get(f'i_{d}'), source=rel(f'{base}/answers.json'), note='importance rated before seeing any facts')
    cards = {c['id']: c for c in Q['cards']}
    for d, por_side in K.items():
        v = ans[d]; pp = -v if por_side == 'a' else v  # page: negative = card A; pp positive = Portland preferred
        c = 'a' if pp > 0 else 'b' if pp < 0 else 'tie'
        add(id=f'{r}.{d}', type='pair', kind='club_dimension', round=r, date=date, qid=d, domain='club', dimension=d, dimension_name=dims[d],
            a=dict(entity=POR, text=cards[d]['a' if por_side == 'a' else 'b']), b=dict(entity=SEA, text=cards[d]['b' if por_side == 'a' else 'a']),
            choice=c, y=1.0 if pp > 0 else 0.0 if pp < 0 else 0.5, strength=pp, strength_scale=[-3, 3], raw_value=v, portland_was=por_side,
            ms=ms.get(d), flags=['names_hidden_until_end'], source=rel(f'{base}/answers.json'),
            note='strength: +3 strongly Portland ... -3 strongly Seattle (page stored -3 = strongly card A)')
    for rq in Q['rules']:
        v = ans[rq['id']]
        add(id=f'{r}.{rq["id"]}', type='choice', round=r, date=date, qid=rq['id'], domain='club', prompt=rq['q'], options=rq['o'],
            choice=v, choice_text=rq['o'][v], ms=ms.get(rq['id']), source=rel(f'{base}/answers.json'))
    for s in Q['scen']:
        add(id=f'{r}.{s["id"]}', type='gut', round=r, date=date, qid=s['id'], domain='club', anonymous=True, text=s['q'],
            value=ans[s['id']], scale=[0, 10], ms=ms.get(s['id']), flags=['scenario_not_a_club'], source=rel(f'{base}/answers.json'),
            note='How happy would you be as a fan? 0-10')
    for g in Q['gut']:
        v = ans[g['id']]
        if g['id'] in ('g1', 'g2'):
            add(id=f'{r}.{g["id"]}', type='pair', kind='club_named', round=r, date=date, qid=g['id'], domain='club', prompt=g['q'],
                a=dict(entity=POR), b=dict(entity=SEA), choice=['a', 'b', 'tie'][v], y=[1.0, 0.0, 0.5][v], winner=['Portland Timbers', 'Seattle Sounders FC', None][v],
                ms=ms.get(g['id']), flags=['existing_supporter_of_a'], source=rel(f'{base}/answers.json'))
        else:
            add(id=f'{r}.{g["id"]}', type='choice', round=r, date=date, qid=g['id'], domain='club', prompt=g['q'], options=g['o'],
                choice=v, choice_text=g['o'][v], ms=ms.get(g['id']), source=rel(f'{base}/answers.json'))

# ---------------------------------------------------------------- round 7: players (2026-10-06)
def round7():
    r, date = 'q7', '2026-10-06'
    K, Q, A = J('quiz7/key.json'), J('quiz7/questions.json'), raw('quiz7')
    ans, ms, order = A['answers'], A['times'], A['order']
    items = {i['id']: i for i in Q['items']}; bag = Q['bag']
    for qid, load in K['picks'].items():
        v = ans[qid]; neg = {k: -x for k, x in load.items()}
        add(id=f'{r}.{qid}', type='everyday', round=r, date=date, qid=qid, domain='player', prompt='Quick pick (gut only)',
            options=[dict(text=items[qid]['l'], loadings=load), dict(text=items[qid]['r'], loadings=neg)], choice=0 if v == 'l' else 1,
            loadings=load if v == 'l' else neg, shown_first=shown(order, qid), ms=ms.get(qid), source=rel('quiz7/raw/responses/kevin.json'))
    for g in ('r1', 'r2', 'r3', 'r4'):
        for name, v in ans[g].items():
            dk = v == 'dk'
            add(id=f'{r}.{g}.{name}', type='gut', round=r, date=date, qid=g, domain='player', entity=ent(name, f'{r}.{g}', 'player'),
                anonymous=False, value=None if dk else v, known=not dk, scale=[0, 10], screen_ms=ms.get(g),
                model_at_time=None, flags=['dont_know'] if dk else [], source=rel('quiz7/raw/responses/kevin.json'),
                note=items[g]['title'] + "; ms is for the whole 10-player screen")
    for j in range(1, 10):
        m = items[f'm{j}']; a = ans[f'm{j}']
        add(id=f'{r}.m{j}', type='maxdiff', round=r, date=date, qid=f'm{j}', domain='player', prompt='Which counts most against a player, which least?',
            items=[dict(construct=o, text=bag[o]) for o in m['opts']], worst=a['worst'], best=a['best'],
            polarity='baggage: worst = counts most against, best = counts least', ms=ms.get(f'm{j}'), source=rel('quiz7/raw/responses/kevin.json'))
    for s in [i for i in Q['items'] if i['t'] == 'choice']:
        v = ans[s['id']]
        add(id=f'{r}.{s["id"]}', type='choice', round=r, date=date, qid=s['id'], domain='player', prompt=s['q'], options=s['opts'],
            choice=v, choice_text=[s['opts'][x] for x in v] if isinstance(v, list) else s['opts'][v], multi=s['multi'] > 1,
            ms=ms.get(s['id']), source=rel('quiz7/raw/responses/kevin.json'))
    b = items['budget']; pts = ans['budget']
    add(id=f'{r}.budget', type='budget', round=r, date=date, qid='budget', domain='player', prompt='Split 100 points over what makes a player yours',
        items=[dict(construct=f['k'], text=f"{f['label']}: {f['hint']}", points=pts[f['k']]) for f in b['factors']], total=sum(pts.values()),
        ms=ms.get('budget'), flags=['kevin_found_format_hard', 'dropped_from_fit'], source=rel('quiz7/raw/responses/kevin.json'),
        note='F_CH Character, F_WK Team player, F_LO Loyalty & bond, F_ST Joy to watch, F_AB Greatness, F_LE Legacy, F_CO Connection')

# ---------------------------------------------------------------- rounds 8-9: players by choice (2026-10-06)
def player_profiles(r, folder, date, flags_extra=()):
    K, Q, A = J(f'{folder}/key.json'), J(f'{folder}/questions.json'), raw(folder)
    ans, ms, order = A['answers'], A['times'], A.get('order')
    att = K['att']
    def prof(lv):
        return dict(attrs={a[0]: l for a, l in zip(att, lv)}, text={a[0]: a[2][l][0] for a, l in zip(att, lv)},
                    values={a[0]: a[2][l][1] for a, l in zip(att, lv)})
    for i, (la, lb) in enumerate(K['conj']):
        qid = f'c{i+1:02d}'; c, y = side(ans.get(qid))
        add(id=f'{r}.{qid}', type='pair', kind='player_profile', round=r, date=date, qid=qid, domain='player', a=prof(la), b=prof(lb),
            choice=c, y=y, shown_first=shown(order, qid), ms=ms.get(qid), flags=list(flags_extra), source=rel(f'{folder}/raw/responses/kevin.json'),
            note='values: hidden factor points 0-10 (CO in Affinity points, PE in penalty points before scaling); level 0 is the better level')
def round8():
    r, date = 'q8', '2026-10-06'
    K, A = J('quiz8/key.json'), raw('quiz8'); ans, ms, order = A['answers'], A['times'], A['order']
    for i, (a, b) in enumerate(K['pairs']):
        qid = f'h{i+1:02d}'; c, y = side(ans.get(qid))
        add(id=f'{r}.{qid}', type='pair', kind='player_named', round=r, date=date, qid=qid, domain='player',
            a=dict(entity=ent(a, f'{r}.{qid}', 'player')), b=dict(entity=ent(b, f'{r}.{qid}', 'player')), choice=c, y=y,
            winner=a if y == 1 else b if y == 0 else None, shown_first=shown(order, qid), ms=ms.get(qid),
            flags=['name_recognition_confound'] + (['skipped_dont_know'] if c == 'skip' else []), source=rel('quiz8/raw/responses/kevin.json'),
            note='pairs chosen to differ on 2+ factors in opposite directions; everything else (connection, baggage) uncontrolled')
    player_profiles(r, 'quiz8', date, ['no_baggage_attribute'])
def round9():
    player_profiles('q9', 'quiz9', '2026-10-06', ['d_optimal_near_tossup'])

# ---------------------------------------------------------------- round 10: controlled named pairs (2026-10-06)
def round10():
    r, date = 'q10', '2026-10-06'
    K, A = J('quiz10/key.json'), raw('quiz10'); ans, ms, order = A['answers'], A['times'], A.get('order')
    for it in K:
        qid = it['id']; c, y = side(ans.get(qid))
        fl = ['controlled_setting']
        if c.startswith('pass'): fl.append('dont_know')
        add(id=f'{r}.{qid}', type='pair', kind='player_named', round=r, date=date, qid=qid, domain='player', group=it['g'],
            a=dict(entity=ent(it['l'], f'{r}.{qid}', 'player')), b=dict(entity=ent(it['r'], f'{r}.{qid}', 'player')), choice=c, y=y,
            winner=it['l'] if y == 1 else it['r'] if y == 0 else None, tested=it['test'], score_diff_a_minus_b=it['d'],
            shown_first=shown(order, qid), ms=ms.get(qid), flags=fl, source=rel('quiz10/raw/responses/kevin.json'),
            note='score_diff from the audited player scores at build time (POS = position-boost difference); pass_a/pass_b = did not know that player')

# ---------------------------------------------------------------- rounds 11-12: personal values (2026-10-07)
V11 = ['causes', 'armband', 'refused_pride', 'left', 'right', 'gives', 'fair', 'private', 'speaks_up', 'betting']
def f11(lv):
    c, pr, pa, g, sp, li, po, ad = lv
    return dict(zip(V11, [int(x) for x in (c == 0, pr == 0, pr == 2, pa == 0, pa == 2, g == 0, sp == 0, li == 0, po == 0, ad == 1)]))
V12 = ['wgame', 'climate', 'private_jet', 'mental_health', 'fans_close', 'fans_rows', 'taunts', 'feuds', 'indiscipline', 'common_goal']
def f12(lv):
    wg, cl, mh, fa, re_, tm, di, cg = lv
    return dict(zip(V12, [int(x) for x in (wg == 0, cl == 0, cl == 2, mh == 0, fa == 0, fa == 2, re_ == 1, tm == 1, di == 1, cg == 0)]))
# direct question -> research tag (players/values, values2) and sign (+1: the statement is the tag being true)
TAG11 = {'s01': ('causes', 1), 's02': ('armband', 1), 's03': ('left', 1), 's04': ('right', 1), 's05': (None, 1), 's06': ('mental_health', 1),
         's07': ('speaks_up', 1), 's08': ('betting', 1), 's09': ('private', -1), 's10': ('gives', 1), 's11': ('fair', -1), 's12': (None, 1)}
TAG12 = {'s01': ('refugees', 1), 's02': ('union', 1), 's03': ('badge_kiss_exit', 1), 's04': ('contract_media', 1), 's05': ('honest', 1),
         's06': ('climate', 1), 's07': (None, 1), 's08': ('fan_owned_club', 1), 's09': ('outside_interests', 1), 's10': (None, 1),
         's11': ('ref_disputes', 1), 's12': ('youth_mentor', 1)}
SC = {'++': 2, '+': 1, '0': 0, '-': -1, '--': -2}
def values_round(r, folder, date, feat, tags):
    K, Q, A = J(f'{folder}/key.json'), J(f'{folder}/questions.json'), raw(folder)
    ans, ms, order = A['answers'], A['times'], A.get('order'); att = K['att']; qs = {i['id']: i for i in Q['items']}
    for p in K['pairs']:
        qid = p['id']; c, y = side(ans.get(qid))
        def prof(lv): return dict(attrs={a[0]: l for a, l in zip(att, lv)}, text={a[0]: a[2][l] for a, l in zip(att, lv)}, tags=feat(lv))
        single = len(p['diff']) == 1
        fl = ['single_trait_dominance_check'] if single else []
        if single:
            k = [a[0] for a in att].index(p['diff'][0]); good = 'a' if p['A'][k] < p['B'][k] else 'b'
            if c in ('a', 'b') and c != good: fl.append('picked_worse_level')
        add(id=f'{r}.{qid}', type='pair', kind='values_profile', round=r, date=date, qid=qid, domain='player', a=prof(p['A']), b=prof(p['B']),
            differs_on=p['diff'], choice=c, y=y, shown_first=shown(order, qid), ms=ms.get(qid), flags=fl,
            source=rel(f'{folder}/raw/responses/kevin.json'), note='players equal on the pitch; level 0 is the better level of each trait')
    for sid, (tag, sign) in tags.items():
        v = ans[sid]
        add(id=f'{r}.{sid}', type='values', round=r, date=date, qid=sid, domain='player', prompt='Does this change how you feel about a player?',
            text=qs[sid]['q'], tag=tag, tag_sign=sign, value=SC[v], raw_value=v, scale=[-2, 2],
            weight_on_tag=None if tag is None else SC[v] * sign, ms=ms.get(sid),
            flags=[] if tag else ['no_research_tag'], source=rel(f'{folder}/raw/responses/kevin.json'),
            note='value: ++ like a lot more 2 ... -- like a lot less -2; weight_on_tag = value * tag_sign')
def round11(): values_round('q11', 'quiz11', '2026-10-07', f11, TAG11)
def round12(): values_round('q12', 'quiz12', '2026-10-07', f12, TAG12)

# ---------------------------------------------------------------- verdicts
def verdicts():
    fb = J('players/feedback.json')
    for i, f in enumerate(fb):
        if f['name'] == '(rule)':
            add(id=f'fb.{i:02d}', type='verdict', kind='rule', round='players_feedback', date='2026-10-06', domain='player',
                note=f['note'], source=rel('players/feedback.json'))
            continue
        add(id=f'fb.{i:02d}', type='verdict', kind='list_position', round='players_feedback', date='2026-10-06', domain='player',
            entity=ent(f['name'], 'players/feedback.json', 'player'), list_rank=f['rank'], model_at_time=f['aff'],
            verdict=f['verdict'], note=f['note'], flags=['dont_know'] if f['verdict'] == 'unknown' else [], source=rel('players/feedback.json'),
            label={'agree': 1, 'maybe': 1, 'unknown': None}.get(f['verdict']),
            hint='verdict on the player\'s place in the top-10 list (rank in the list he was shown); agree = model about right')
    for i, o in enumerate(J('players/observations.json')):
        add(id=f'obs.{i:02d}', type='verdict', kind='match_observation', round='observations', date=o['date'], domain='player',
            entity=ent(o['player'], 'players/observations.json', 'player'), club=ent(o['club'], 'players/observations.json'),
            text=o['note'], signal=o['signal'], context=o['match'], pulling_for=o['pulling_for'], direction=-1,
            source=rel('players/observations.json'))
    # Kevin's factor calls in the 2026-09-28 re-rate review (research/decisions.py FACTORS, answers to REVIEW.md)
    FACT = literal(AFF / 'research/decisions.py', 'FACTORS')
    names = {'C': 'Culture', 'V': 'Values', 'H': 'History', 'O': 'Ownership'}
    for n, fs in FACT.items():
        for k, v in fs.items():
            add(id=f'review.{n}.{k}', type='verdict', kind='factor_override', round='review_2026-09-28', date='2026-09-28', domain='club',
                entity=ent(n, 'research/decisions.py'), factor=k, factor_name=names.get(k, k), value=v, scale=[0, 10],
                flags=['superseded_by_later_rerates'], source=rel('research/decisions.py'),
                note='Kevin set this factor score in the re-rate review; later re-rates (rules, tenths, folds) moved scores since')

# ---------------------------------------------------------------- doc-only summaries (no raw answers kept)
def doc_summaries():
    src = 'docs/supporter-profile.md'
    add(id='q3.weights_first', type='budget', round='q3', date='2026-09-28', domain='club', prompt='Factor weights, first answer (of 90)',
        items=[dict(construct=c, points=p) for c, p in (('V', 26), ('C', 24), ('H', 14), ('O', 10), ('T', 16))], total=90,
        flags=['summary_only', 'order_inferred'], source=src,
        note='"first quiz answer was 26 / 24 / 14 / 10 / 16"; order assumed Values, Culture, History, Ownership, Team as in the sentence before')
    add(id='q2.tradeoff1', type='tradeoff', round='q2', date='2026-09-28', domain='club', method='stated trade-off (summary)',
        a=dict(construct='C', text='Elite atmosphere under a private-equity fund'), b=dict(construct='O', text='Fan-owned club with a quiet crowd'),
        choice='a', y=1.0, winner='C', flags=['summary_only'], source=src)
    add(id='q2.tradeoff2', type='tradeoff', round='q2', date='2026-09-28', domain='club', method='stated trade-off (summary)',
        a=dict(construct='V', text='Strong community values'), b=dict(construct='H', text='Big history with poor conduct'),
        choice='a', y=1.0, winner='V', flags=['summary_only'], source=src)

for f in (round4, round5, round6, cascadia, round7, round8, round9, round10, round11, round12, verdicts, doc_summaries): f()

CONSTRUCTS = {
 'club': {'C': 'Supporter culture', 'V': 'Values', 'H': 'History & identity', 'O': 'Ownership', 'T': 'Team (was Style, slot S in scores.py)',
          'TR': 'Track record (winning over ~10 years)', 'TROPHY': 'Trophies over steady success', 'REC': 'Recency (latest season over body of work)',
          'LOC': 'Localism / distance from Sacramento', 'TRIBE': 'Rivalry tribalism', 'ASSOC': 'Association (judged by company kept)',
          'ASSOC_DOWN': 'Association, negative side', 'PEN': 'Penalty severity', 'FORGIVE': 'Forgiveness / redemption', 'DECAY': 'Old wrongs fade',
          'UNDER': 'Underdog', 'NOV': 'Novelty', 'WOM': "Women's game", 'LOYAL': 'Stickiness / loyalty', 'BAG': 'q4 DCE baggage attribute',
          'BAGT': 'q5 DCE violence recency attribute',
          'CL': 'Culture: loud section', 'CY': 'Culture: loyal through bad times', 'CG': 'Culture: ground / place', 'CA': 'Culture: away following',
          'TP': 'Team: pressing/intensity', 'TB': 'Team: player-fan bond', 'TS': 'Team: stable squad / long captain', 'TI': 'Team: icons / defining coach',
          'VC': 'Values: community', 'VW': "Values: women's team", 'VA': 'Values: academy / homegrown', 'VF': 'Values: fan voice',
          'VI': 'Values: causes / identity', 'VP': 'Values: affordability',
          'racism': 'Tolerates racist fan groups', 'violence': 'Ultras violence', 'state': 'Authoritarian state owner', 'lbo': 'Leveraged buyout',
          'pe': 'Private equity owner', 'betting': 'Sportsbook sponsor', 'arms': 'Arms-maker sponsor', 'superleague': 'Super League signatory',
          'multiclub': 'Multi-club feeder', 'overspend': 'Overspending', 'franchise': 'Relocated franchise', 'politics': 'Owner political messaging',
          'cascadia:<dim>': 'Cascadia decider dimension (supporters, ground, owner, voice, community, sponsors, women, coach, squad, academy, record, history, practical, direction)'},
 'player': {'CH': 'Character', 'WK': 'Team player / work rate', 'LO': 'Loyalty & bond', 'AB': 'Greatness (ability)', 'ST': 'Joy to watch (style)',
            'LE': 'Legacy', 'CO': 'Connection to Kevin\'s clubs', 'PE': 'Off-pitch penalty', 'POS': 'Position boost (removed 2026-10-07)',
            'q7 picks only': {'BO': 'fan bond', 'CAP': 'vocal leadership', 'CA': 'causes (NOT club away following)', 'TR': 'trophies (NOT club track record)',
                              'HU': 'humility', 'UN': 'underdog/overachiever', 'ERA': 'watched live', 'W': "women's game", 'LOC': 'hometown', 'MON': 'money moves (+ = refuses money)'},
            'F_*': 'q7 budget factors (F_CH, F_LO, F_ST, F_WK, F_AB, F_LE, F_CO)',
            'b01-b12': 'q7 player baggage (see players/model.py SEV)',
            'values tags': V11 + V12 + ['refugees', 'union', 'badge_kiss_exit', 'contract_media', 'honest', 'fan_owned_club', 'outside_interests', 'ref_disputes', 'youth_mentor']},
}
out = dict(meta=dict(
    built_from='scripts/affinity/evidence/build.py', schema='scripts/affinity/evidence/README.md', subject='Kevin (Sacramento)',
    records=len(REC), unmapped=UNMAPPED, constructs=CONSTRUCTS,
    name_catalogs=dict(clubs_nations='scripts/affinity/scores.py S + scripts/importers/build_usl.py A (+ data/suite_data.json, data/nations_extra.json)',
                       players='scripts/affinity/players/ratings.json'),
    not_available=['Round 1 (51-question interview) and rounds 2-3 (multiple choice): no raw answers kept, only summaries in docs/affinity.md and docs/supporter-profile.md (a few encoded with flag summary_only)',
                   'Family Club Draft (scripts/affinity/family): deprecated family questionnaire, no answers stored, not Kevin-specific']),
    records=REC)
(HERE / 'evidence.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
from collections import Counter
print(len(REC), 'records'); print(Counter(r['type'] for r in REC)); print('unmapped', UNMAPPED)
