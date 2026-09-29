"""Quiz round 6: rapid-fire this or that. Everyday (blind), club traits (paired comparison), real clubs head to head."""
import json, random, itertools, pathlib
root = pathlib.Path(__file__).resolve().parents[3]
rnd = random.Random(606)
EV = [  # (id, left, right, {construct: +1 if left, -1 if right})
 ('e01', "Diner", "Chain restaurant", {'H': 1, 'O': 1}), ('e02', "Vinyl", "Streaming", {'H': 1, 'NOV': -1}),
 ('e03', "Small club gig", "Stadium show", {'CL': 1}), ('e04', "Hometown", "Big city", {'LOC': 1}),
 ('e05', "Underdog", "Favorite", {'UNDER': 1, 'TR': -1}), ('e06', "Classic", "New release", {'H': 1, 'NOV': -1}),
 ('e07', "Local brewery", "Famous brand", {'LOC': 1, 'O': 1}), ('e08', "Same barber", "Whoever's open", {'LOYAL': 1}),
 ('e09', "Co-op grocery", "Big-box store", {'O': 1, 'V': 1}), ('e10', "Grinder", "Genius", {'TP': 1, 'TI': -1}),
 ('e11', "Road trip", "Flight", {'LOC': 1}), ('e12', "Old ballpark", "New ballpark", {'CG': 1, 'NOV': -1}),
 ('e13', "Win ugly", "Lose beautifully", {'TR': 1, 'TP': -1}), ('e14', "Team captain", "Star player", {'TS': 1, 'TI': -1}),
 ('e15', "Forgive", "Remember", {'DECAY': 1}), ('e16', "Singing", "Watching", {'CL': 1, 'T': -1}),
 ('e17', "Cause", "Trophy", {'V': 1, 'TR': -1}), ('e18', "Roots", "Results", {'H': 1, 'TR': -1}),
 ('e19', "Neighborhood bar", "Rooftop bar", {'CY': 1, 'LOC': 1}), ('e20', "Hand-me-down", "Brand new", {'H': 1, 'NOV': -1})]
TR_ = [('CL', "A loud singing section"), ('CG', "A 100-year-old ground"), ('CY', "Crowds that stay through relegation"),
       ('CA', "A huge away following"), ('VC', "Serious community work"), ('VW', "A real women's team"), ('VI', "A strong anti-racist stance"),
       ('VA', "Academy kids in the team"), ('VP', "Cheap tickets"), ('O', "Owned by its fans"), ('TP', "Relentless pressing"),
       ('TB', "Players who hug the fans"), ('TS', "Same captain for 10 years"), ('H', "A legendary history"), ('TR', "Near the top most years"),
       ('LOC', "Two hours from home"), ('TROPHY', "A trophy last season"), ('TI', "A coach who stays and defines the club")]
pairs = list(itertools.combinations(range(len(TR_)), 2)); rnd.shuffle(pairs)
cnt = [0] * len(TR_); TP = []
for a, b in pairs:
    if cnt[a] < 4 and cnt[b] < 4: TP.append((a, b)); cnt[a] += 1; cnt[b] += 1
    if len(TP) == 34: break
# club head-to-heads: clubs close in Affinity, spread across leagues
D = json.loads((root / 'data' / 'suite_data.json').read_text()); aff, lg = {}, {}
PRI = ['epl', 'esp', 'ita', 'bl', 'fra', 'mls', 'nwsl', 'ch', 'usl', 'ucl', 'cup']
for k in PRI:
    for t in D[k]['teams']: aff.setdefault(t['name'], t['base'] + t['bonus']); lg.setdefault(t['name'], k)
pool = sorted(aff, key=lambda n: -aff[n])[:200]
CP, used = [], {}
tries = 0
while len(CP) < 36 and tries < 100000:
    tries += 1; a, b = rnd.sample(pool, 2)
    if abs(aff[a] - aff[b]) > 8 or lg[a] == lg[b] or used.get(a, 0) >= 1 or used.get(b, 0) >= 1: continue
    CP.append((a, b)); used[a] = used.get(a, 0) + 1; used[b] = used.get(b, 0) + 1
items = [dict(id=i, l=l, r=r) for i, l, r, _ in EV] + [dict(id=f't{j+1:02d}', l=TR_[a][1], r=TR_[b][1]) for j, (a, b) in enumerate(TP)] \
      + [dict(id=f'c{j+1:02d}', l=a, r=b, club=1) for j, (a, b) in enumerate(CP)]
json.dump(items, open('questions.json', 'w'), ensure_ascii=False)
json.dump(dict(everyday={i: k for i, _, _, k in EV}, traits={f't{j+1:02d}': [TR_[a][0], TR_[b][0]] for j, (a, b) in enumerate(TP)},
               clubs={f'c{j+1:02d}': [a, b, round(aff[a], 1), round(aff[b], 1)] for j, (a, b) in enumerate(CP)}), open('key.json', 'w'), ensure_ascii=False, indent=1)
print(len(EV), len(TP), len(CP), len(items))
