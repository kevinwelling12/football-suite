"""Quiz round 8: players by choice only (replaces round 7's 100-point budget, which Kevin found hard).
Head-to-heads between real players he likely knows (pairs picked to differ on the factors), and anonymous profile
pairs (a choice experiment over the six factors plus connection). Weights are fitted from the choices."""
import json, random, pathlib, sys
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / 'players')); import model as M
rnd = random.Random(808)
facts, scores = M.load()
K = ['CH', 'WK', 'LO', 'AB', 'ST', 'LE']
# players he likely knows: rated in round 7, his clubs' current players, USMNT/Thorns, the biggest active names
KNOWN = [n for n in M.GUT if M.GUT[n] is not None] + ["Andy Robertson", "Alisson Becker", "Trent Alexander-Arnold", "Florian Wirtz", "Alexander Isak",
  "Dominik Szoboszlai", "Alexis Mac Allister", "Ryan Gravenberch", "Cody Gakpo", "Luis Díaz", "Darwin Núñez", "Roberto Firmino", "Jordan Henderson",
  "Gregor Kobel", "Nico Schlotterbeck", "Serhou Guirassy", "Emre Can", "Julian Brandt", "Jadon Sancho", "Thomas Müller", "Son Heung-min",
  "Kevin De Bruyne", "Rodri", "Bukayo Saka", "Declan Rice", "Cole Palmer", "Bruno Fernandes", "Robert Lewandowski", "Pedri", "Neymar",
  "Luis Suárez", "Weston McKennie", "Tyler Adams", "Diego Chará", "Lindsey Horan", "Trinity Rodman", "Alex Morgan", "Christine Sinclair",
  "Olivia Moultrie", "Naomi Girma", "Mallory Swanson", "Sam Kerr", "Lamine Yamal", "Achraf Hakimi", "N'Golo Kanté", "Martin Ødegaard"]
KNOWN = [n for n in dict.fromkeys(KNOWN) if n in scores and n in facts]
def vec(n):
    r = M.rate(facts[n], scores[n]); return [scores[n][k] for k in K] + [r['conn'], r['pen']]
pairs, used = [], {}
cands = [(a, b) for i, a in enumerate(KNOWN) for b in KNOWN[i + 1:] if facts[a].get('gender') == facts[b].get('gender')]
rnd.shuffle(cands)
for a, b in cands:
    va, vb = vec(a), vec(b)
    d = [x - y for x, y in zip(va, vb)]
    # informative: the two differ clearly on at least two factors in opposite directions (a real trade-off)
    if not (any(x >= 1.5 for x in d[:6]) and any(x <= -1.5 for x in d[:6])): continue
    if used.get(a, 0) >= 2 or used.get(b, 0) >= 2: continue
    pairs.append((a, b)); used[a] = used.get(a, 0) + 1; used[b] = used.get(b, 0) + 1
    if len(pairs) == 30: break
# anonymous profiles: 7 attributes, levels with hidden values on the 0-10 factor scale (connection in Affinity points)
ATT = [('AB', "Ability", [("World-class", 9.5), ("Very good", 7.5), ("Solid regular", 5.5)]),
       ('CH', "Character", [("Known for charity and speaking up", 9), ("Quiet, no issues", 6), ("Dives, picks fights", 3)]),
       ('WK', "Effort", [("Runs for the team, no ego", 9), ("Coasts at times, big ego", 4)]),
       ('LO', "Career", [("One-club captain", 9.5), ("Moves every few years", 4)]),
       ('ST', "Style", [("Flair that makes you gasp", 9.5), ("Efficient, unspectacular", 5)]),
       ('LE', "Moments", [("Iconic goals and trophies", 9), ("No big moments yet", 4)]),
       ('CO', "Club", [("Plays for one of your clubs", 8), ("No link to your clubs", 0), ("Plays for a club you dislike", -3)])]
conj = []
while len(conj) < 20:
    A = [rnd.randrange(len(a[2])) for a in ATT]; B = [rnd.randrange(len(a[2])) for a in ATT]
    diff = sum(x != y for x, y in zip(A, B))
    # a real trade-off: each profile is better on at least one trait (level 0 is the best on every attribute)
    if diff < 3 or diff > 5 or not (any(x < y for x, y in zip(A, B)) and any(x > y for x, y in zip(A, B))): continue
    conj.append((A, B))
items = [dict(id=f'h{j+1:02d}', t='h2h', l=a, r=b) for j, (a, b) in enumerate(pairs)]
items += [dict(id=f'c{j+1:02d}', t='conj', rows=[a[1] for a in ATT], l=[ATT[i][2][x][0] for i, x in enumerate(A)], r=[ATT[i][2][x][0] for i, x in enumerate(B)])
          for j, (A, B) in enumerate(conj)]
json.dump(dict(items=items), open(here / 'questions.json', 'w'), ensure_ascii=False)
json.dump(dict(att=[(k, lab, lv) for k, lab, lv in ATT], conj=conj, pairs=pairs), open(here / 'key.json', 'w'), ensure_ascii=False, indent=1)
print(len(pairs), 'head-to-heads,', len(conj), 'profile pairs;', len(KNOWN), 'known players')
