"""Cascadia decider: Portland Timbers vs Seattle Sounders FC. Hidden key: which side is Portland on each card."""
import json, random
rnd = random.Random(1975)
DIMS = [  # id, name for importance, Portland facts, Seattle facts
 ('supporters', "Supporters and atmosphere",
  "Supporter group formed 2001, 5,000+ members. Standing end with drums, smoke and constant chanting; the largest painted tifo in MLS history (2025). Crowds about 22,300 in 2026 (about 88% full). Openly anti-fascist; a 2025 banner for the team's immigrant players.",
  "Main group formed 2005, about 5,000 members (2017). March to the Match behind a marching band. Crowds about 31,700 in 2026, 30% below the 2017 peak. Openly anti-fascist; a 2025 tifo against immigration raids; turned a 2026 banner ban into a fundraiser."),
 ('ground', "The ground",
  "Opened 1926, centenary this year. Soccer-only, downtown, on light rail. About 25,000 seats, artificial turf. Staying put (city agreement to 2035).",
  "Opened 2002. The NFL team's stadium, set up for 37,700 for soccer. Artificial turf. Lease ends 2032; the owner calls it untenable and is weighing a 25,000-seat stadium in a suburb, where half of surveyed fans say they would never go."),
 ('owner', "The owner's conduct",
  "Sole private owner since 2007. A 2022 independent report faulted his handling of the women's team's abuse case; he stepped down as CEO and, under fan pressure, sold the women's team in 2024. No repeat since. Has put $145m of his own money into the stadium.",
  "Local majority owner with minority families; a 25% estate stake is for sale and an outside investor is being sought. 2019 letter equated an anti-fascist flag with the Proud Boys (apologised later). 2025 profanity-laced dressing-down of players over their prize-money protest. Lowest transfer spending in MLS."),
 ('voice', "Fans' say in the club",
  "Supporters' trust gets consultative meetings with the front office; no vote, no seat. Meetings were halted in 2022-23 during the scandal.",
  "Every season-ticket holder votes on whether to keep the general manager (about every 4 years; one is due this fall). An elected fan council meets the owners three times a year. Fan objections helped end a controversial shirt sponsor early."),
 ('community', "Community work and causes",
  "Club community fund with 500+ volunteers in its annual week; the supporters' charity builds community pitches; Pride night. No club statement on immigration raids (the supporters made one).",
  "Foundation building 52 free mini-pitches; a club anti-racism framework; players sat out a match over racial injustice (2020); Pride match."),
 ('sponsors', "Sponsors",
  "Shirt: Bank of America. Sleeve: a dairy co-op. No betting, casino or state-owned partner.",
  "Shirt: a hospital system fans objected to over its policies (ending 2027). Sleeve and pitch naming: a tribal casino with a sportsbook inside."),
 ('women', "The women's team link",
  "Sold its women's team in 2024 after the abuse scandal; now separately owned, still sharing the stadium.",
  "Bought a women's team in 2024 with a private-equity firm that holds the majority; the club runs it."),
 ('coach', "Coach and style of play",
  "Third coach since 2023: a new Catalan coach (Aug 2026) preaching a high press and possession.",
  "A local coach since 2016, a former player from the club's earlier eras. Patient possession, low pressing."),
 ('squad', "Squad stability and icons",
  "Captain at the club since 2011; moderate turnover around him.",
  "Goalkeeper-captain since 2014; a core together for 10 years, including the club's all-time top scorer, a homegrown."),
 ('academy', "Academy and homegrown players",
  "Academy to reserve side to first team; homegrown minutes limited; the youngest scorer in club history came through this year.",
  "The pipeline produced the club's all-time top scorer and, this year, a club-record sale to Atlético Madrid; the first MLS homegrown sold to Europe (2014)."),
 ('record', "Winning and track record",
  "Since 2016: lost MLS Cup finals in 2018 and 2021, won a 2020 tournament; missed the playoffs 3 times in 10 years; 10th in the West now. MLS Cup 2015.",
  "Since 2016: MLS Cups 2016 and 2019, continental champions 2022 (first MLS club), Leagues Cup 2025; playoffs 9 times in 10 years; 9th in the West now after a club-record winless run."),
 ('history', "History and identity",
  "NASL club from 1975, 'Soccer City, USA'; the same ground in every era; 50th anniversary in 2025.",
  "NASL club from 1974 with two Soccer Bowl finals; led MLS attendance from year one; the only US club to have won every trophy available to it."),
 ('practical', "Getting there and following",
  "About 580 miles by road, about 50 nonstop flights a week from Sacramento; downtown ground on light rail; tickets easy to get.",
  "About 750 miles by road, about 88 nonstop flights a week; downtown now, possibly suburban from 2032; tickets easy to get."),
 ('direction', "Where the club is heading",
  "New coach and style; the ground stays; ownership unchanged and still the main source of friction with fans.",
  "Worst run in its history, lowest spending in MLS, a general-manager confidence vote pending, a possible stadium move and a likely ownership change."),
]
cards = []
for d in DIMS:
    port_left = rnd.random() < .5
    cards.append(dict(id=d[0], name=d[1], a=d[2] if port_left else d[3], b=d[3] if port_left else d[2]))
RULES = [
 ('r1', "A club plays in an NFL stadium it shares. How much should that count against its supporter culture?",
  ["Not at all", "A little", "A lot", "It nearly rules the club out"]),
 ('r2', "An owner mishandled an abuse case years ago, faced consequences, is still in charge, and nothing similar has happened since. How much should it still count?",
  ["Fully, as if it were new", "About half", "Only if it happens again", "Not at all"]),
 ('r3', "A sponsor is a tribal casino that has a sportsbook inside. Should it count like a betting sponsor?",
  ["Yes, fully", "Partly", "No"]),
 ('r4', "A club's announced plans (a likely stadium move, an ownership change) haven't happened yet. Should they count now?",
  ["Yes, fully", "Partly", "Only once they happen"]),
 ('r5', "Fans can vote out the general manager, versus consultation only. How much should formal fan power matter?",
  ["A lot", "Some", "A little", "Not at all"]),
 ('r6', "A club's women's team is majority-owned by private equity but run by the club. Compared with having no women's team:",
  ["Better", "About the same", "Worse"]),
 ('r7', "Which matters more to you in a team?",
  ["A coach who has been there 10 years", "The style they play", "Both equally"]),
]
SCEN = [('s1', "It's 2031. Your club has won two trophies in five years, but now plays in a new 25,000-seat stadium in a suburb."),
        ('s2', "It's 2031. Your club hasn't won anything, but its ground is still packed, loud and 105 years old."),
        ('s3', "It's 2031. Your club's owner is the same one fans once told to sell, and the club has been decent but trophyless.")]
GUT = [('g1', "A Cascadia derby with nothing else at stake. Who do you want to win?", ["Portland", "Seattle", "Don't care"]),
       ('g2', "If you were starting from zero this season, which would you pick?", ["Portland Timbers", "Seattle Sounders", "Neither"]),
       ('g3', "Would switching from the Timbers to the Sounders feel like a betrayal?", ["Yes", "Somewhat", "No"])]
json.dump(dict(dims=[dict(id=d[0], name=d[1]) for d in DIMS], cards=cards, rules=[dict(id=i, q=q, o=o) for i, q, o in RULES],
               scen=[dict(id=i, q=q) for i, q in SCEN], gut=[dict(id=i, q=q, o=o) for i, q, o in GUT]), open('questions.json', 'w'), ensure_ascii=False)
json.dump({c['id']: ('a' if c['a'] == d[2] else 'b') for c, d in zip(cards, DIMS)}, open('key.json', 'w'), indent=1)
print(len(DIMS), 'dims', len(cards), 'cards', len(RULES), 'rules', len(SCEN), 'scen', len(GUT), 'gut')
