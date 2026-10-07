"""Quiz round 12: more values, new topics (Kevin, 2026-10-07: "do another one on different topics").
Character is one factor today, scored by research against fixed anchors. This round asks which off-pitch values move Kevin,
so Character can be rebuilt from his own weights.

Part A, 24 mystery pairs: two players equal on the pitch, differing on one or two values traits (his rule from round 10:
limit the variables). Part B, 12 direct questions: "does this change how you feel about a player?" on a five-point scale.
Traits and levels (level 0 listed first; hidden values are only labels, the fit uses dummies)."""
import json, random, pathlib, itertools
here = pathlib.Path(__file__).resolve().parent
rnd = random.Random(1212)
ATT = [
    ('wgame', "Women's game", ["Champions the women's game and equal pay", "No public stance"]),
    ('climate', "Climate", ["Climate activist, lives it (e.g. low-carbon travel)", "No public stance", "Flies private jets for short hops"]),
    ('mind', "Mental health", ["Talks openly about mental health", "Keeps it private"]),
    ('fans', "With fans", ["Stops for every autograph and selfie", "Polite but distant", "Rows with fans online"]),
    ('respect', "Opponents", ["Doesn't celebrate against former clubs", "Taunts opposing fans"]),
    ('team', "Dressing room", ["Backs the coach and teammates in public", "Public feuds with coach or teammates"]),
    ('disc', "Discipline", ["Model professional", "Drink-driving or late-night partying in season"]),
    ('pledge', "Common Goal", ["Gives 1% of wages to Common Goal", "No pledge"]),
]
pairs = []
cands = []
for i, j in itertools.combinations(range(len(ATT)), 2):  # two traits differ
    for li in itertools.combinations(range(len(ATT[i][2])), 2):
        for lj in itertools.combinations(range(len(ATT[j][2])), 2):
            # trade-off: A better on trait i, B better on trait j
            cands.append(((i, li[0], li[1]), (j, lj[1], lj[0])))
rnd.shuffle(cands)
use = {k: 0 for k in range(len(ATT))}
for c in sorted(cands, key=lambda c: rnd.random()):
    (i, ai, bi), (j, aj, bj) = c
    if use[i] >= 6 or use[j] >= 6: continue
    pairs.append(c); use[i] += 1; use[j] += 1
    if len(pairs) == 20: break
singles = []  # one trait differs: does that trait matter at all
for i in rnd.sample(range(len(ATT)), 4):
    a, b = rnd.sample(range(len(ATT[i][2])), 2); singles.append(((i, a, b),))
def profile(diffs):
    base = {k: 1 if len(ATT[k][2]) == 3 else rnd.randrange(2) for k in range(len(ATT))}  # neutral level for 3-level traits
    A, B = dict(base), dict(base)
    for k, a, b in diffs: A[k], B[k] = a, b
    return [A[k] for k in range(len(ATT))], [B[k] for k in range(len(ATT))]
items, key = [], []
for n, d in enumerate(pairs + singles):
    A, B = profile(d)
    items.append(dict(id=f'v{n+1:02d}', t='conj', rows=[a[1] for a in ATT], l=[ATT[k][2][x] for k, x in enumerate(A)],
                      r=[ATT[k][2][x] for k, x in enumerate(B)]))
    key.append(dict(id=f'v{n+1:02d}', A=A, B=B, diff=[ATT[k][0] for k, *_ in d]))
SCALE = [  # part B: direct
    ('s01', 'A player supports refugees or migrants in public'),
    ('s02', 'A player leads or backs the players\' union in a fight over pay or conditions'),
    ('s03', 'A player kisses the badge, then asks for a transfer'),
    ('s04', 'A player pushes for a new contract through the media'),
    ('s05', 'A player gives honest, unguarded interviews'),
    ('s06', 'A player is vegan or lives very sustainably'),
    ('s07', 'A player plays on through injury for the team'),
    ('s08', 'A player owns or invests in a lower-league or fan-owned club'),
    ('s09', 'A player studies for a degree or has big interests outside football'),
    ('s10', 'A player retires from the national team early to focus on their club'),
    ('s11', 'A player has a public dispute with a referee after the match'),
    ('s12', 'A player becomes a coach or mentor at their old youth club'),
]
items += [dict(id=i, t='scale', q=q) for i, q in SCALE]
json.dump(dict(items=items), open(here / 'questions.json', 'w'), ensure_ascii=False)
json.dump(dict(att=ATT, pairs=key), open(here / 'key.json', 'w'), ensure_ascii=False, indent=1)
print(len(pairs), 'trade-off pairs,', len(singles), 'single-trait pairs,', len(SCALE), 'direct; trait uses', use)
