# Question bank + hidden key. Constructs:
# C V H O T = factor weights; TR track-record strength; REC recency; LOC localism; TRIBE rivalry; ASSOC network;
# PEN penalty severity; FORGIVE redemption; UNDER underdog; NOV novelty; WOM women's game; LOYAL stickiness
import json, random
E = []  # everyday (blind) items: (id, prompt, [(label, {construct: loading})])
def q(i, p, *opts): E.append(dict(id=i, prompt=p, options=[o[0] for o in opts], key=[o[1] for o in opts]))
q('e01', "One night in a city you've never visited. Where do you eat?",
  ("The 60-year-old diner the locals swear by", {'H': 1, 'LOC': .5}),
  ("The chef's tasting menu with the best reviews in town", {'TR': 1, 'T': .5}),
  ("The loud, packed taqueria with a line out the door", {'C': 1.5}),
  ("The worker-owned co-op café", {'O': 1.5, 'V': .5}))
q('e02', "Same ticket price. Which show?",
  ("A 300-capacity club where the crowd knows every word", {'C': 1.5}),
  ("An arena show with flawless production", {'TR': 1, 'C': -.5}),
  ("A legendary band's reunion show", {'H': 1.5, 'REC': -1}),
  ("A local band you've followed for years", {'LOC': 1.5, 'LOYAL': .5}))
q('e03', "You need a new coffee mug. You buy it from…",
  ("Whatever store is closest", {'O': -.5}),
  ("The roaster down the street, at twice the price", {'O': 1, 'LOC': 1}),
  ("A company that gives its profits to a cause", {'V': 1.5}),
  ("A brand with a great design, wherever it's from", {'T': .5, 'TR': .5}))
q('e04', "A band you love lands a tour sponsor you really dislike. You…",
  ("Stop listening, at least for a while", {'PEN': 1.5, 'V': .5}),
  ("Keep listening, but it bugs you", {'PEN': .5}),
  ("Don't care; bands need money", {'PEN': -1}),
  ("Judge by how loudly they promote it", {'PEN': .5, 'FORGIVE': .5}))
q('e05', "A restaurant you loved had an awful owner. He sold it; the new owner is great. You…",
  ("Go back right away", {'FORGIVE': 1.5}),
  ("Wait a few months and see", {'FORGIVE': .5}),
  ("Don't go back; the place feels tainted", {'FORGIVE': -1.5}))
q('e06', "Friday night, one movie.",
  ("Rewatch a classic you love", {'H': 1, 'REC': -1}),
  ("The new release everyone is talking about", {'NOV': 1, 'REC': 1}),
  ("Something obscure nobody you know has seen", {'NOV': 1.5, 'UNDER': .5}))
q('e07', "Someone calls an organization \"the best-run in its industry.\" Your first reaction:",
  ("Impressed", {'TR': 1, 'O': -.5}),
  ("Best-run for whom?", {'O': 1.5, 'V': .5}),
  ("I care more about the people in it", {'C': 1, 'T': .5}))
q('e08', "Choosing where to live, all else equal:",
  ("An old neighborhood with character", {'H': 1, 'C': .5}),
  ("A new development where everything works", {'NOV': 1, 'TR': .5}),
  ("Near friends and family", {'ASSOC': 1, 'LOC': 1}))
q('e09', "Pickup game. Which side would you rather be on?",
  ("Runs hard all game and loses 3-2", {'T': 1.5, 'TR': -.5}),
  ("Sits back and wins 1-0", {'TR': 1.5, 'T': -1}))
q('e10', "At a bar, a game on TV you have no stake in. You end up rooting for…",
  ("Whoever is losing", {'UNDER': 1.5}),
  ("The better team; I like quality", {'TR': 1}),
  ("The team with the louder fans", {'C': 1.5}),
  ("The team with a player I like", {'T': 1}))
q('e11', "You have $100 to give away.",
  ("A local food bank", {'LOC': 1, 'V': .5}),
  ("The global charity with the best measured impact", {'V': 1, 'LOC': -1}),
  ("A friend's fundraiser", {'ASSOC': 1.5}))
q('e12', "A friend's close friend turns out to be a real jerk. How much does it change how you see your friend?",
  ("A lot", {'ASSOC': 1.5, 'PEN': .5}),
  ("A little", {'ASSOC': .5}),
  ("Not at all", {'ASSOC': -1}))
q('e13', "You learn a friend is close with someone you admire. Do you like your friend more?",
  ("Yes, noticeably", {'ASSOC': 1.5}),
  ("A little", {'ASSOC': .5}),
  ("No", {'ASSOC': -1}))
q('e14', "Your favorite bakery was bought by a private-equity chain. Nothing has changed yet. You…",
  ("Keep buying, same as ever", {'O': -1}),
  ("Buy less and look around", {'O': 1}),
  ("Stop right away", {'O': 1.5, 'PEN': 1}))
q('e15', "How often do you root for something because it's from Sacramento or Northern California?",
  ("All the time", {'LOC': 1.5}),
  ("Sometimes", {'LOC': .5}),
  ("Rarely", {'LOC': -1}))
q('e16', "A stranger in a Dodgers cap holds a door for you. Does the cap register?",
  ("Yes, and it colors the moment", {'TRIBE': 1.5}),
  ("I notice it and shrug", {'TRIBE': .5}),
  ("Wouldn't even notice", {'TRIBE': -1}))
q('e17', "A musician you've loved for 10 great albums puts out a weak one. Your view of them:",
  ("Unchanged; the body of work speaks", {'REC': -1.5, 'H': .5}),
  ("Slightly lower", {'REC': .5}),
  ("You're only as good as your latest", {'REC': 1.5, 'TR': .5}))
q('e18', "A local band gets big and moves to LA. You…",
  ("Stay a proud fan", {'FORGIVE': .5, 'LOYAL': 1}),
  ("Feel they aren't ours anymore", {'LOC': 1, 'TRIBE': 1}),
  ("Never cared where they were from", {'LOC': -1}))
q('e19', "Two equal products. One company's CEO says something political you strongly disagree with. You…",
  ("Buy the other one", {'V': 1.5, 'PEN': .5}),
  ("Depends how bad it was", {'V': .5}),
  ("Doesn't factor in", {'V': -1}))
q('e20', "Tickets to something big. You'd pay 20% more for…",
  ("A seat in the loudest section", {'C': 1.5}),
  ("A better view of the action", {'T': 1}),
  ("Neither; cheapest seat is fine", {'C': -.5}))
q('e21', "A small company you like is bought by a tech giant. You feel…",
  ("Happy for them", {'O': -1}),
  ("Worried about what comes next", {'O': 1}),
  ("You've already lost interest", {'O': 1, 'PEN': .5}))
q('e22', "Ideal trip:",
  ("Somewhere with deep history", {'H': 1.5}),
  ("Somewhere nobody you know has been", {'NOV': 1.5}),
  ("Back to a favorite place", {'LOYAL': 1.5}))
q('e23', "One jersey to hang on the wall:",
  ("A throwback from a famous old season", {'H': 1.5, 'REC': -1}),
  ("This season's, with the current captain", {'REC': 1, 'T': .5}))
q('e24', "Same sport, same drama, same night, one ticket: women's game or men's?",
  ("Women's", {'WOM': 1.5}),
  ("Men's", {'WOM': -1}),
  ("Coin flip", {'WOM': .5}))
q('e25', "At work you'd rather be on…",
  ("A steady team you've known for years", {'T': 1, 'LOYAL': .5}),
  ("A rotating cast of the best people available", {'TR': 1, 'T': -.5}))
q('e26', "A new stadium, a new club, a new neighborhood. How long before it feels real to you?",
  ("Right away", {'NOV': 1.5}),
  ("A few years", {'NOV': .5}),
  ("A decade or more", {'NOV': -1, 'H': 1}))
q('e27', "You hear a TV show's lead actor was cruel to the crew. You…",
  ("Stop watching", {'PEN': 1.5, 'V': .5}),
  ("Depends how bad", {'PEN': .5}),
  ("Keep watching; art and artist are separate", {'PEN': -1}))
q('e28', "Someone did something wrong years ago and has clearly changed. You judge them by…",
  ("Who they are now", {'FORGIVE': 1.5}),
  ("Both, about equally", {'FORGIVE': .5}),
  ("The past; it sticks", {'FORGIVE': -1.5}))
q('e29', "Game night. Which kind of board game?",
  ("Long, careful strategy", {'TR': 1}),
  ("Chaos and late comebacks", {'UNDER': 1, 'T': .5}),
  ("Everyone plays together against the game", {'C': 1, 'V': .5}))
q('e30', "You've used the same barber for years. A better, cheaper one opens next door. You…",
  ("Stay put", {'LOYAL': 1.5}),
  ("Try the new one once", {'LOYAL': -.5, 'NOV': .5}),
  ("Switch", {'LOYAL': -1.5, 'TR': .5}))
# consistency (reversed) and attention
L = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]
def k(i, p, c, sign): E.append(dict(id=i, prompt=p, options=L, key=[{c: sign * v} for v in (-1.5, -.75, 0, .75, 1.5)], check=True))
k('k1', "Some mistakes should follow a person for good.", 'FORGIVE', -1)
k('k2', "Who someone spends time with tells me little about them.", 'ASSOC', -1)
k('k3', "If the product stays the same, who owns the company doesn't matter to me.", 'O', -1)
E.append(dict(id='k4', prompt="Everyone likes a halftime snack. To show you're reading, pick \"Orange slices\".",
  options=["Hot dog", "Orange slices", "Pretzel", "Nothing"], key=[{}, {}, {}, {}], attention=1))

# forced choice (ipsative), factor vs factor
P = []
def p(i, a, fa, b, fb): P.append(dict(id=i, a=a, b=b, fa=fa, fb=fb))
p('p01', "I'd rather be somewhere loud and alive.", 'C', "I'd rather be somewhere I agree with.", 'V')
p('p02', "A great night out beats a great story.", 'C', "A place with a story beats a great night out.", 'H')
p('p03', "The crowd makes the place.", 'C', "Who runs the place matters more than who shows up.", 'O')
p('p04', "At a game, I end up watching the fans.", 'C', "At a game, I watch the players.", 'T')
p('p05', "What something stands for now matters most.", 'V', "What something has been through matters most.", 'H')
p('p06', "Good values are enough, whoever is in charge.", 'V', "Values don't last without the right people in charge.", 'O')
p('p07', "I'd rather cheer for good people.", 'V', "I'd rather cheer for people who leave everything out there.", 'T')
p('p08', "Roots matter more than management.", 'H', "Management matters more than roots.", 'O')
p('p09', "I love a legend.", 'H', "I love a grinder.", 'T')
p('p10', "Give me a well-run organization.", 'O', "Give me a team that plays with heart.", 'T')
p('p11', "Consistency over years impresses me.", 'TR', "One magical season impresses me.", 'UNDER')
p('p12', "Home is where my loyalties start.", 'LOC', "Loyalty follows what I believe in, wherever it is.", 'V')

# discrete choice experiment
ATTR = [('C', 'Crowd', ["Quiet, polite crowd", "Solid, loyal crowd", "One of the loudest grounds anywhere"]),
        ('V', 'Stands for', ["Little beyond winning", "A decent community club", "Known for its causes: community, a real women's team, a fan voice"]),
        ('H', 'Story', ["Founded 8 years ago", "A century old, a few famous moments", "A legendary name in the game"]),
        ('O', 'Owners', ["An investment fund", "A private owner who runs it well", "Owned by its members"]),
        ('T', 'Team', ["Sits deep, big squad turnover", "An honest, average side", "Relentless press, long-serving captain"]),
        ('TR', 'Last 10 years', ["Fighting relegation most years", "Steady mid-table", "Near the top most years"]),
        ('LOC', 'Where', ["On another continent", "Across the country", "Two hours' drive away"]),
        ('BAG', 'Also', ["Nothing else to note", "A sportsbook on the shirt", "Ultras linked to violence"])]
rnd = random.Random(2026)
D = []
while len(D) < 16:
    a = [rnd.randrange(3) for _ in ATTR]; b = [rnd.randrange(3) for _ in ATTR]
    diff = sum(x != y for x, y in zip(a, b))
    # utility-ish direction for dominance check (BAG: 0 best)
    sa = [x if i < 7 else 2 - x for i, x in enumerate(a)]; sb = [x if i < 7 else 2 - x for i, x in enumerate(b)]
    if diff < 4 or all(x >= y for x, y in zip(sa, sb)) or all(y >= x for x, y in zip(sa, sb)): continue
    if sum(sa) - sum(sb) not in (-2, -1, 0, 1, 2): continue
    D.append(dict(id=f'd{len(D)+1:02d}', a=a, b=b))

# blind profiles (gut rating 0-10); club = model name, hidden
R = [('r01', 'Union Berlin', "Fans rebuilt their stadium with their own hands. Member-owned. Reached the top European competition recently, now mid-table. One of the loudest crowds in its country."),
     ('r02', 'Brighton', "Owned by a professional gambler turned betting-data entrepreneur who runs it prudently. Modern stadium, polite crowd. Punches far above its size year after year and sells a star every summer."),
     ('r03', 'Wrexham', "An ancient small-town club bought by two Hollywood actors, with a documentary series. Three promotions in a row. Tickets cost more; the crowd is bigger and louder."),
     ('r04', 'Bodø/Glimt', "A club from a small town above the Arctic Circle. Artificial pitch, relentless pressing, a local coach for years. Went from the second tier to a European semi-final. Small, fervent crowd."),
     ('r05', 'Newcastle United', "A huge, passionate one-club city. Owned by the sovereign wealth fund of an authoritarian state. Won a trophy recently after decades without one."),
     ('r06', 'Inter Miami CF', "Founded eight years ago by a global superstar. Signed the world's most famous player. An investment firm is among the owners. Crowd full of celebrities."),
     ('r07', 'AFC Wimbledon', "Formed by fans after their club was moved to another city. Rose from the ninth tier. Owned by its supporters' trust. Small new stadium."),
     ('r08', 'Galatasaray', "One of the most intimidating atmospheres in the world. Wins its league often. A record of fan violence. Spends beyond its means."),
     ('r09', 'Athletic Club', "Fields only players from its own region. Never relegated in over 90 years. Member-owned. Roaring crowd. Won a cup recently after 40 years."),
     ('r10', 'Arsenal', "A historic big-city giant owned by the family who own an NFL rival of your team. Winning again with a young homegrown core. Expensive tickets."),
     ('r11', 'Bay FC', "A women's club founded three years ago near you by former national-team players. Majority owner is an investment firm. Still building a crowd."),
     ('r12', 'Real Madrid', "The most decorated club in the world. Member-owned. Its president pushed a breakaway league. Star signings every year."),
     ('r13', 'Lazio', "A historic capital-city club. Its best-known ultras group has far-right ties and the club has been sanctioned for racism repeatedly. Proud, loud crowd.")]
json.dump(dict(everyday=[{k2: v for k2, v in x.items() if k2 != 'key'} for x in E],
               pairs=[dict(id=x['id'], a=x['a'], b=x['b']) for x in P],
               attrs=[dict(k=a[0], label=a[1], levels=a[2]) for a in ATTR], dce=D,
               rate=[dict(id=i, text=t) for i, _, t in R]), open('questions.json', 'w'), ensure_ascii=False)
json.dump(dict(everyday={x['id']: x['key'] for x in E}, pairs={x['id']: [x['fa'], x['fb']] for x in P},
               attrs=[a[0] for a in ATTR], dce=D, rate={i: c for i, c, _ in R}), open('key.json', 'w'), indent=1)
print(len(E), len(P), len(D), len(R), '=', len(E) + len(P) + len(D) + len(R))
