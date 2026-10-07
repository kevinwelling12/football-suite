"""Quiz round 9: mystery players only. Round 8 showed name recognition steering the real-player head-to-heads (Szoboszlai
over Messi, Mac Allister over Vinícius: familiar names win; no single factor explains more than 55% of those picks), while
the anonymous profiles matched the factors well (80%). So the weights now come from anonymous choices.

30 more profile pairs, picked to be informative under the round-8 profile fit (greedy D-optimal: each new pair adds the most
Fisher information about the weights, and each sits near a toss-up), with an eighth trait for baggage off the pitch so the
penalty scale is set by choices too. A "can't split them" answer counts as half to each side."""
import json, math, random, pathlib
import numpy as np
here = pathlib.Path(__file__).resolve().parent
rnd = random.Random(909)
ATT = [('AB', "Ability", [("World-class", 9.5), ("Very good", 7.5), ("Solid regular", 5.5)]),
       ('CH', "Character", [("Known for charity and speaking up", 9), ("Quiet, no issues", 6), ("Dives, picks fights", 3)]),
       ('WK', "Effort", [("Runs for the team, no ego", 9), ("Coasts at times, big ego", 4)]),
       ('LO', "Career", [("One-club captain", 9.5), ("Moves every few years", 4)]),
       ('ST', "Style", [("Flair that makes you gasp", 9.5), ("Efficient, unspectacular", 5)]),
       ('LE', "Moments", [("Iconic goals and trophies", 9), ("No big moments yet", 4)]),
       ('CO', "Club", [("Plays for one of your clubs", 8), ("No link to your clubs", 0), ("Plays for a club you dislike", -3)]),
       # values in penalty points before scaling (model.SEV): Saudi move 3, tax fraud 5, violent conduct 7
       ('PE', "Off the pitch", [("Clean record", 0), ("Moved to the Saudi league for money", -3), ("Convicted of tax fraud", -5),
                                ("Charged after a street fight", -7)])]
# prior: the round-8 profile-only fit (fit.py on c01-c20): weights per factor point, connection x1.22, penalty x1.0
W = {'CH': 18, 'WK': 30, 'LO': 9, 'AB': 9, 'ST': 16, 'LE': 19}; CONN, PEN, BETA = 1.22, 1.0, 0.2
def x(lv):  # utility features: factor points scaled by weight share, connection, penalty
    v = {a[0]: a[2][i][1] for a, i in zip(ATT, lv)}
    return np.array([10 * W[k] / 100 * v[k] for k in W] + [v['CO'], v['PE']])
coef = np.array([1.0] * 6 + [CONN, PEN])
def info(A, B):
    d = x(A) - x(B); p = 1 / (1 + math.exp(-BETA * coef @ d)); return p * (1 - p) * np.outer(d, d), p
cands = []
while len(cands) < 4000:
    A = [rnd.randrange(len(a[2])) for a in ATT]; B = [rnd.randrange(len(a[2])) for a in ATT]
    n = sum(a != b for a, b in zip(A, B))
    if not 3 <= n <= 5 or not (any(a < b for a, b in zip(A, B)) and any(a > b for a, b in zip(A, B))): continue
    I, p = info(A, B)
    if 0.25 <= p <= 0.75: cands.append((A, B, I))
M = np.eye(8) * 1e-2; pick = []
for _ in range(30):
    j = max(range(len(cands)), key=lambda j: np.linalg.slogdet(M + cands[j][2])[1])
    A, B, I = cands.pop(j); M += I; pick.append((A, B))
items = [dict(id=f'c{j+1:02d}', t='conj', rows=[a[1] for a in ATT], l=[ATT[i][2][v][0] for i, v in enumerate(A)],
              r=[ATT[i][2][v][0] for i, v in enumerate(B)]) for j, (A, B) in enumerate(pick)]
json.dump(dict(items=items), open(here / 'questions.json', 'w'), ensure_ascii=False)
json.dump(dict(att=ATT, conj=pick), open(here / 'key.json', 'w'), ensure_ascii=False, indent=1)
print(len(pick), 'pairs; attribute changes per trait:', [sum(a[i] != b[i] for a, b in pick) for i in range(len(ATT))])
