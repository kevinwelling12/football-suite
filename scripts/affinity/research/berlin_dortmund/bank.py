"""German decider: 1. FC Union Berlin vs Borussia Dortmund (Kevin, 2026-10-09: "a blind quiz like we did for the
cascadia pair"). Same format as research/cascadia: importance first, then blind head-to-head cards (Club A / Club B,
sides shuffled), rules of thumb, scenarios, and a named gut check at the end. Facts: dossier.md, dims.json.
Hidden key: which side Union is on each card.  Usage: python3 bank.py [page.html]
"""
import json, pathlib, random, sys
here = pathlib.Path(__file__).resolve().parent
rnd = random.Random(1966)
DIMS = json.loads((here / 'dims.json').read_text())
cards, key = [], {}
for d in DIMS:
    union_left = rnd.random() < .5
    cards.append(dict(id=d['id'], name=d['name'], a=d['union'] if union_left else d['dortmund'], b=d['dortmund'] if union_left else d['union']))
    key[d['id']] = 'a' if union_left else 'b'
RULES = [
 ('r1', "One of a club's top-tier partners (pitch-side boards and stadium signage, not the shirt) is an arms maker. How much should that count against it?", ["Not at all", "A little", "A lot", "It nearly rules the club out"]),
 ('r2', "Two clubs are both controlled by their members, but one is also listed on the stock exchange. How much does that difference matter?", ["A lot", "Some", "A little", "Not at all"]),
 ('r3', "A club sells its best young players to richer clubs every year. How does that sit with you?", ["It counts against it", "Neutral: that's how it survives", "It counts in its favour: it develops players"]),
 ('r4', "A club shares an anthem and a fan friendship with Liverpool. How much should that pull you toward it?", ["A lot", "Some", "A little", "Not at all"]),
 ('r5', "One club is easy to watch on US TV at good times, the other harder. How much should that count in which you follow?", ["A lot", "Some", "A little", "Not at all"]),
 ('r6', "Which story means more to you?", ["Rising from nothing on fans' effort", "Decades of winning at the top", "Both equally"]),
]
SCEN = [('s1', "It's 2031. Your club has reached the Champions League four years running, but an arms maker is still one of its top partners."),
        ('s2', "It's 2031. Your club finishes mid-table every year and hasn't won anything, but its ground is still fan-built and packed."),
        ('s3', "It's 2031. Your club was relegated last season, and every home match still sold out.")]
GUT = [('g1', "Union Berlin v Dortmund, nothing else at stake. Who do you want to win?", ["Union Berlin", "Dortmund", "Don't care"]),
       ('g2', "Starting from zero this season, which German club would you pick?", ["Union Berlin", "Dortmund", "Neither"]),
       ('g3', "Would switching your German club from Dortmund to Union feel like a betrayal?", ["Yes", "Somewhat", "No"])]
Q = dict(dims=[dict(id=d['id'], name=d['name']) for d in DIMS], cards=cards, rules=[dict(id=i, q=q, o=o) for i, q, o in RULES],
         scen=[dict(id=i, q=q) for i, q in SCEN], gut=[dict(id=i, q=q, o=o) for i, q, o in GUT])
json.dump(Q, open(here / 'questions.json', 'w'), ensure_ascii=False)
json.dump(key, open(here / 'key.json', 'w'), indent=1)
if len(sys.argv) > 1:
    t = (here / 'page.template.html').read_text().replace('/*__QUESTIONS__*/', json.dumps(Q, ensure_ascii=False))
    pathlib.Path(sys.argv[1]).write_text(t)
print(len(DIMS), 'dims', len(RULES), 'rules', len(SCEN), 'scen', len(GUT), 'gut')
