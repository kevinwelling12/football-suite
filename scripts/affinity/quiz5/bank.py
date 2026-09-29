# Round 5 bank + hidden key. Sub-constructs:
# Culture: CL loud, CY loyal through bad times, CG ground/place. Team: TP intensity, TB player-fan bond, TS stable squad,
# TI icons/long-serving coach. Values: VC community, VA academy/homegrown, VF fan voice, VI causes/identity, VP affordability.
# Plus DECAY (old wrongs fade), TROPHY (trophies over consistency), TR, LOC, NOV, ASSOC_DOWN, WOM, TRIBE, H, O.
import json, random, itertools
E = []
def q(i, p, *opts): E.append(dict(id=i, prompt=p, options=[o[0] for o in opts], key=[o[1] for o in opts]))
q('f01', "What ruins a night out faster?",
  ("A flat, quiet crowd", {'CL': 1.5}), ("A soulless, generic venue", {'CG': 1.5}), ("The performers going through the motions", {'TP': 1.5}))
q('f02', "Your old college team goes 2-10. You…",
  ("Still watch every game", {'CY': 1.5}), ("Watch some", {'CY': .5}), ("Check the scores now and then", {'CY': -1}))
q('f03', "Which coworker do you trust most?",
  ("The one who's been there 15 years", {'TS': 1.5}), ("The one who outworks everyone", {'TP': 1.5}),
  ("The one who remembers everyone's name", {'TB': 1.5}), ("The rising star everyone talks about", {'TI': 1, 'TR': .5}))
q('f04', "Your favorite bar starts charging a $20 cover. You…",
  ("Stop going", {'VP': 1.5}), ("Go less often", {'VP': .5}), ("Pay it if the night is good", {'VP': -1}))
q('f05', "The city is deciding on a stadium subsidy. Residents should…",
  ("Get a binding vote", {'VF': 1.5}), ("Be consulted", {'VF': .5}), ("Leave it to the officials", {'VF': -1}))
q('f06', "At a kids' game, what makes you smile most?",
  ("The kid who never stops running", {'TP': 1.5}), ("A local kid scoring the winner", {'VA': 1.5, 'LOC': .5}), ("The whole team piling on each other after", {'TB': 1.5}))
q('f07', "A brand you like takes a public stand on a cause you support. Effect on you:",
  ("I like them more", {'VI': 1.5}), ("No change", {'VI': 0}), ("I'd rather brands stayed out of it", {'VI': -1}))
q('f08', "Company softball final. Bring in a ringer from outside or play your regulars?",
  ("The regulars", {'VA': 1, 'TS': 1}), ("The ringer", {'TR': 1.5}))
q('f09', "Someone did something bad. It happened 10 years ago instead of 2. How much less does it count?",
  ("Much less", {'DECAY': 1.5}), ("Somewhat less", {'DECAY': .5}), ("The same", {'DECAY': -1.5}))
q('f10', "Which means more on a shelf?",
  ("One championship trophy from 12 years ago", {'TROPHY': 1.5}), ("Five straight years finishing near the top", {'TROPHY': -1.5, 'TR': 1}))
q('f11', "A new friend turns out to be close with someone you really dislike. Your read on the new friend:",
  ("Lower", {'ASSOC_DOWN': 1.5}), ("Slightly lower", {'ASSOC_DOWN': .5}), ("Unaffected", {'ASSOC_DOWN': -1}))
q('f12', "Traveling, you'd rather spend the afternoon…",
  ("At the famous landmark", {'H': 1.5}), ("In the bar where the same locals have met for 30 years", {'CY': 1, 'CG': .5}))
q('f13', "Would you rather be one of 300 regulars or one of 30,000 casual fans?",
  ("One of 300 regulars", {'CY': 1.5}), ("One of 30,000", {'CL': 1.5}))
q('f14', "A charity run comes through your neighborhood. You…",
  ("Run it or volunteer", {'VC': 1.5}), ("Donate", {'VC': .5}), ("Skip it", {'VC': -1}))
q('f15', "Your niece's league funds the boys' program twice as well as the girls'. Should it be equal?",
  ("Yes, exactly equal", {'WOM': 1.5}), ("Closer than it is", {'WOM': .5}), ("Follow the demand", {'WOM': -1}))
q('f16', "Whose jersey do you buy: a so-so player from your hometown or a superstar from elsewhere?",
  ("The hometown player", {'LOC': 1, 'VA': 1}), ("The superstar", {'TI': 1.5}))
q('f17', "Which leader do you follow?",
  ("The one who has stayed 15 years", {'TI': 1.5, 'TS': .5}), ("The brilliant newcomer", {'NOV': 1.5}), ("Whoever the group chooses", {'VF': 1.5}))
q('f18', "Two-hour rain delay. What keeps you in your seat?",
  ("The people around you singing through it", {'CL': 1.5}), ("You've never left early in your life", {'CY': 1.5}), ("The chance of a great finish", {'TR': .5, 'TROPHY': .5}))
q('f19', "An old ballpark with posts in the way, or a new one with perfect views?",
  ("The old one", {'CG': 1.5, 'H': .5}), ("The new one", {'CG': -1, 'NOV': 1}))
q('f20', "A public figure apologizes for something from 8 years ago. How much do you hold it against them now?",
  ("Barely", {'DECAY': 1.5}), ("A bit", {'DECAY': .5}), ("Fully", {'DECAY': -1.5}))
q('f21', "Your team's star leaves for a rival and speaks kindly of your club. You…",
  ("Still cheer for him", {'TRIBE': -1, 'TB': .5}), ("Wish him well; he's theirs now", {'TRIBE': .5}), ("Boo him forever", {'TRIBE': 1.5}))
q('f22', "How much do you care whether places you spend money let customers have a say?",
  ("A lot", {'VF': 1.5, 'O': .5}), ("Some", {'VF': .5}), ("Not at all", {'VF': -1}))
q('f23', "Highlight reel. Which moment gets you?",
  ("A 40-yard screamer", {'TI': 1.5}), ("A defender sprinting 60 yards to make the tackle", {'TP': 1.5}), ("Players running to the fans after the goal", {'TB': 1.5}))
q('f24', "A new restaurant opens in a historic building and keeps the old sign. Does the old sign matter to you?",
  ("Yes, a lot", {'H': 1, 'CG': 1}), ("A little", {'H': .5}), ("No", {'H': -1, 'NOV': .5}))
L = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]
def k(i, p, c, sign): E.append(dict(id=i, prompt=p, options=L, key=[{c: sign * v} for v in (-1.5, -.75, 0, .75, 1.5)], check=True))
k('g1', "Old wrongs should count as much as recent ones.", 'DECAY', -1)
k('g2', "A trophy outweighs years of steady success.", 'TROPHY', 1)
E.append(dict(id='g3', prompt="Quick check that you're reading: pick \"Corner flag\".", options=["Goal post", "Penalty spot", "Corner flag", "Halfway line"], key=[{}] * 4, attention=2))

# constant-sum budgets
BUD = [
 dict(id='b1', prompt="You're starting a new club in a city you love. Split 100 coins.", items=[
   ("An electric supporters' section", 'C'), ("Community programs and a real women's team", 'V'), ("Honoring the history of the club it replaces", 'H'),
   ("Shares so the fans own it", 'O'), ("A relentless young squad and a coach who stays", 'T'), ("Scouting to win right away", 'TR')]),
 dict(id='b2', prompt="A club you love can protect only some of what it has. Split 100 points.", items=[
   ("Its old ground", 'CG'), ("Its loud singing section", 'CL'), ("Crowds that stay through bad years", 'CY'), ("Its huge away following", 'CA')]),
 dict(id='b3', prompt="What should a club spend its good-cause budget on? Split 100.", items=[
   ("Community work in its city", 'VC'), ("Its women's team", 'VW'), ("An academy for local kids", 'VA'), ("A real voice for fans in decisions", 'VF'),
   ("Standing up on social issues", 'VI'), ("Keeping tickets affordable", 'VP')]),
 dict(id='b4', prompt="What makes you love a team? Split 100.", items=[
   ("Pressing and running for each other", 'TP'), ("Players who connect with the fans", 'TB'), ("The same core squad year after year", 'TS'), ("An icon or a coach who defines the club", 'TI')]),
]
# best-worst (MaxDiff) on baggage: 12 items, 9 sets of 4, each item 3 times
BAG = [('racism', "Tolerates racist fan groups"), ('violence', "Ultras with a record of violence"), ('state', "Owned by an authoritarian state's fund"),
       ('lbo', "Bought with debt loaded onto the club"), ('pe', "Owned by a private-equity fund"), ('betting', "A sportsbook on the shirt"),
       ('arms', "An arms maker as a sponsor"), ('superleague', "Signed up for a breakaway super league"), ('multiclub', "A feeder club in a multi-club network"),
       ('overspend', "Spends far beyond its income"), ('franchise', "Moved here from another city"), ('politics', "Owner uses the club for political messaging")]
rnd = random.Random(55)
best = None
for _ in range(20000):
    idx = list(range(12)) * 3; rnd.shuffle(idx)
    sets = [sorted(idx[i:i + 4]) for i in range(0, 36, 4)]
    if any(len(set(s)) < 4 for s in sets): continue
    pairs = {}
    for s in sets:
        for a, b in itertools.combinations(s, 2): pairs[(a, b)] = pairs.get((a, b), 0) + 1
    score = len(pairs) - 3 * sum(v - 1 for v in pairs.values())
    if not best or score > best[0]: best = (score, sets)
MD = [dict(id=f'm{i+1:02d}', items=[rnd.sample(s, 4)][0]) for i, s in enumerate(best[1])]
# DCE round 2: TR vs trophies vs values, and how old a violence incident is
ATTR = [('V', 'Stands for', ["Little beyond winning", "A decent community club", "Known for its causes"]),
        ('C', 'Crowd', ["Quiet", "Solid and loyal", "One of the loudest anywhere"]),
        ('T', 'Team', ["Passive, big turnover", "Honest, average side", "Relentless, long-serving captain"]),
        ('TR', 'Last 10 years', ["Fighting relegation most years", "Steady mid-table", "Near the top most years"]),
        ('TROPHY', 'Trophies', ["None in 20 years", "A league title 12 years ago", "A cup last season"]),
        ('O', 'Owners', ["An investment fund", "A private owner who runs it well", "Its members"]),
        ('BAGT', 'Record', ["Clean", "Ultras violence 8 years ago", "Ultras violence last season"])]
rnd = random.Random(77); D = []
while len(D) < 12:
    a = [rnd.randrange(3) for _ in ATTR]; b = [rnd.randrange(3) for _ in ATTR]
    sa = [x if i < 6 else 2 - x for i, x in enumerate(a)]; sb = [x if i < 6 else 2 - x for i, x in enumerate(b)]
    if sum(x != y for x, y in zip(a, b)) < 4 or all(x >= y for x, y in zip(sa, sb)) or all(y >= x for x, y in zip(sa, sb)): continue
    if abs(sum(sa) - sum(sb)) > 2: continue
    D.append(dict(id=f'c{len(D)+1:02d}', a=a, b=b))
# speeded sort (latency-weighted): phrase -> construct, sign (+ = should pull)
SP = [('s01', "Pyro and flags at kickoff", 'CL', 1), ('s02', "Members vote for the president", 'VF', 1), ('s03', "Sold out for 40 straight years", 'CY', 1),
      ('s04', "Academy kids in the first team", 'VA', 1), ('s05', "Signed a global superstar", 'TI', 1), ('s06', "Back-to-back titles", 'TR', 1),
      ('s07', "Stadium named after a bank", 'O', -1), ('s08', "Founded in 2019", 'NOV', 1), ('s09', "Players stayed after a 5-0 loss to thank the fans", 'TB', 1),
      ('s10', "Presses from the first minute", 'TP', 1), ('s11', "Same captain for 12 seasons", 'TS', 1), ('s12', "Ticket prices frozen for a decade", 'VP', 1),
      ('s13', "Owned by a hedge fund", 'O', -1), ('s14', "Fans marched against racism", 'VI', 1), ('s15', "Plays in an NFL stadium", 'CG', -1),
      ('s16', "Two hours from Sacramento", 'LOC', 1), ('s17', "Ultras banned for violence", 'PEN', -1), ('s18', "Won the league on the last day", 'UNDER', 1),
      ('s19', "Women's team sells out", 'WOM', 1), ('s20', "Shirt sponsor is a Gulf state airline", 'PEN', -1), ('s21', "Relegated, and crowds grew", 'CY', 1),
      ('s22', "A 100-year-old wooden stand", 'CG', 1)]
# blind vignettes (hold-out test of the round-4 model)
R = [('v01', 'Napoli', "A southern city's only big club. Fanatical crowd. Won two league titles in recent years. A flamboyant film-producer owner."),
     ('v02', 'Sunderland', "A shipbuilding city's club that drew 40,000 even in the third tier. A documentary followed its fall. A young side just won promotion back to the top."),
     ('v03', 'Leeds United', "A one-city giant owned by the investment arm of your NFL team. A fierce, sometimes hostile crowd. Up and down between divisions."),
     ('v04', 'Marseille', "The loudest stadium in its country; once won Europe's top prize. Owned by a former owner of your baseball team's biggest rival. Regular fan clashes."),
     ('v05', 'Chelsea', "A big-city club controlled by a private-equity firm. Spent over a billion on young players on very long contracts. Loud in patches."),
     ('v06', 'Celta Vigo', "A coastal club with a famously loyal crowd, a steady stream of academy players and left-leaning ultras. The coach came up through its youth teams."),
     ('v07', 'Juventus', "The most successful club in its country, owned by an industrial dynasty. Tied to a match-fixing scandal and a breakaway league. Quiet modern stadium."),
     ('v08', 'PSV Eindhoven', "Founded by an electronics company for its workers. Wins its league often. Modern but loud ground. Sells its best players every year."),
     ('v09', 'Detroit City FC', "Started by supporters as an amateur team in 2012. Plays in a restored high-school stadium with a raucous, left-leaning supporters' group. Now pro in the second tier."),
     ('v10', 'Oakland Roots SC', "A mission-driven club founded in 2018 near you. Artists and activists among the owners. Struggling on the field; plays in a borrowed ballpark."),
     ('v11', 'Sporting CP', "A member-owned capital-city club whose academy produced world stars. Won its league recently with a young coach. Ultras groups with a violent past."),
     ('v12', 'Monterey Bay FC', "A small club two hours from you, founded in 2021. A small seaside stadium. Mostly losing seasons so far."),
     ('v13', 'Manchester City', "Owned by a Gulf royal family's state group. Won almost everything for a decade. Charged with over 100 breaches of finance rules.")]
json.dump(dict(everyday=[{k2: v for k2, v in x.items() if k2 != 'key'} for x in E],
               budget=[dict(id=b['id'], prompt=b['prompt'], items=[t for t, _ in b['items']]) for b in BUD],
               maxdiff=[dict(id=m['id'], items=[BAG[i][1] for i in m['items']]) for m in MD],
               attrs=[dict(k=a[0], label=a[1], levels=a[2]) for a in ATTR], dce=D,
               speed=[dict(id=i, text=t) for i, t, _, _ in SP], rate=[dict(id=i, text=t) for i, _, t in R]), open('questions.json', 'w'), ensure_ascii=False)
json.dump(dict(everyday={x['id']: x['key'] for x in E}, budget={b['id']: [c for _, c in b['items']] for b in BUD},
               maxdiff={m['id']: [BAG[i][0] for i in m['items']] for m in MD}, attrs=[a[0] for a in ATTR], dce=D,
               speed={i: [c, s] for i, _, c, s in SP}, rate={i: c for i, c, _ in R}), open('key.json', 'w'), indent=1)
n = len(E) + len(BUD) + len(MD) + len(D) + len(SP) + len(R)
print(len(E), len(BUD), len(MD), len(D), len(SP), len(R), '=', n, 'maxdiff pair score', best[0])
