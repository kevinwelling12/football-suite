"""Quiz round 11: personal values (Kevin, 2026-10-07: "a quiz that explores personal values alignment").
Character is one factor today, scored by research against fixed anchors. This round asks which off-pitch values move Kevin,
so Character can be rebuilt from his own weights.

Part A, 24 mystery pairs: two players equal on the pitch, differing on one or two values traits (his rule from round 10:
limit the variables). Part B, 12 direct questions: "does this change how you feel about a player?" on a five-point scale.
Traits and levels (level 0 listed first; hidden values are only labels, the fit uses dummies)."""
import json, random, pathlib, itertools
here = pathlib.Path(__file__).resolve().parent
rnd = random.Random(1111)
ATT = [
    ('causes', "Social causes", ["Speaks out on racism and inequality", "Keeps out of social issues"]),
    ('pride', "LGBTQ+", ["Wears the rainbow armband, backs Pride", "No public stance", "Refused to wear a Pride shirt"]),
    ('party', "Party politics", ["Campaigns for a left-leaning candidate", "No party politics", "Campaigns for a right-leaning candidate"]),
    ('give', "Giving back", ["Funds schools and clinics back home", "Occasional charity visits"]),
    ('sport', "Sportsmanship", ["Plays fair, helps opponents up", "Dives and wastes time"]),
    ('life', "Lifestyle", ["Private, low-key", "Flashy, big social media brand"]),
    ('power', "Speaking up", ["Criticises FIFA and owners in public", "Never criticises the game's bosses"]),
    ('ads', "Sponsors", ["No betting or crypto deals", "Fronts a betting app"]),
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
    ('s01', 'A player takes the knee or wears an anti-racism message'),
    ('s02', 'A player wears the rainbow captain\'s armband'),
    ('s03', 'A player publicly backs a left-leaning politician'),
    ('s04', 'A player publicly backs a right-leaning politician'),
    ('s05', 'A player talks openly about their faith'),
    ('s06', 'A player talks openly about mental health'),
    ('s07', 'A player criticises FIFA or their club\'s owners'),
    ('s08', 'A player fronts a betting or crypto brand'),
    ('s09', 'A player has a huge social media brand and a flashy lifestyle'),
    ('s10', 'A player funds a hospital or school in his home town'),
    ('s11', 'A player is known for diving'),
    ('s12', 'A player switches national teams to another country they qualify for'),
]
items += [dict(id=i, t='scale', q=q) for i, q in SCALE]
json.dump(dict(items=items), open(here / 'questions.json', 'w'), ensure_ascii=False)
json.dump(dict(att=ATT, pairs=key), open(here / 'key.json', 'w'), ensure_ascii=False, indent=1)
print(len(pairs), 'trade-off pairs,', len(singles), 'single-trait pairs,', len(SCALE), 'direct; trait uses', use)
