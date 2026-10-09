"""Italian decider: Napoli, Fiorentina and Atalanta, Kevin's top three in Serie A (2026-10-09: "across my top 3 teams this
time ... even more blind than the last two"). Cascadia format, three clubs per card (A/B/C shuffled per card), ranked on
each card; facts written without names, trophy counts or years (dims.json, dossier.md). Rules and scenarios: rules.json.
Hidden key: which club is A, B and C on each card.  Usage: python3 bank.py [page.html]
"""
import json, pathlib, random, sys
here = pathlib.Path(__file__).resolve().parent
rnd = random.Random(1926)
CLUBS = ['napoli', 'fiorentina', 'atalanta']
DIMS = json.loads((here / 'dims.json').read_text())
R = json.loads((here / 'rules.json').read_text())
cards, key = [], {}
for d in DIMS:
    order = CLUBS[:]; rnd.shuffle(order)
    cards.append(dict(id=d['id'], name=d['name'], t=[d[c] for c in order]))
    key[d['id']] = dict(zip('abc', order))
NAMES = ['Napoli', 'Fiorentina', 'Atalanta']
GUT = [('g1', 'A three-way mini-league between them, nothing else at stake. Who do you most want to win it?', NAMES + ["Don't care"]),
       ('g2', 'Which of the three would you least like to see win it?', NAMES + ["Don't care"]),
       ('g3', 'Starting from zero this season, which Italian club would you follow?', NAMES + ['None of them'])]
Q = dict(dims=[dict(id=d['id'], name=d['name']) for d in DIMS], cards=cards, rules=R['rules'], scen=R['scenarios'],
         gut=[dict(id=i, q=q, o=o) for i, q, o in GUT])
json.dump(Q, open(here / 'questions.json', 'w'), ensure_ascii=False)
json.dump(key, open(here / 'key.json', 'w'), indent=1)
if len(sys.argv) > 1:
    pathlib.Path(sys.argv[1]).write_text((here / 'page.template.html').read_text().replace('/*__QUESTIONS__*/', json.dumps(Q, ensure_ascii=False)))
print(len(DIMS), 'dims', len(R['rules']), 'rules', len(R['scenarios']), 'scen', len(GUT), 'gut')
