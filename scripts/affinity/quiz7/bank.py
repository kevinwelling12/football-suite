"""Quiz round 7: players. Quick picks (hidden construct loadings), gut ratings of named players (the fit target),
best-worst over player baggage, setup questions, and a 100-point budget over the candidate factors (last, so the
stated weights don't prime the gut ratings)."""
import json, pathlib
here = pathlib.Path(__file__).resolve().parent
# constructs: AB ability/peak, ST style/flair, WK work rate/team-first, LO loyalty, BO fan bond, CAP leadership,
# CH conduct, CA causes, LE legacy/moments, TR trophies, CO connection (Kevin's clubs/country), HU humility,
# UN underdog, ERA watched live, W women's game, LOC hometown, MON money moves
PICKS = [
 ('p01', "Ballon d'Or winner", "Captain for 12 seasons", {'AB': 1, 'LO': -1, 'CAP': -1}),
 ('p02', "Nutmegs and no-look passes", "Wins every tackle", {'ST': 1, 'WK': -1}),
 ('p03', "Speaks out against racism", "Scores the winner in a final", {'CA': 1, 'LE': -1}),
 ('p04', "Stays after relegation", "Leaves to win the Champions League", {'LO': 1, 'TR': -1}),
 ('p05', "Academy kid", "Record signing", {'LO': 1, 'AB': -1}),
 ('p06', "Applauds the fans after every loss", "Scores 30 a season", {'BO': 1, 'AB': -1}),
 ('p07', "Quiet, lets his football talk", "Big personality, great quotes", {'HU': 1}),
 ('p08', "Genius who drifts out of some games", "Grinder who never stops running", {'ST': 1, 'AB': 1, 'WK': -1}),
 ('p09', "Funds free school meals", "Wins the treble", {'CA': 1, 'TR': -1}),
 ('p10', "Played for your club", "Best in the world at his position", {'CO': 1, 'AB': -1}),
 ('p11', "One moment everyone remembers", "Ten years of steady excellence", {'LE': 1}),
 ('p12', "Playmaker", "Goal machine", {'ST': 1}),
 ('p13', "Never dives", "Wins penalties for his team", {'CH': 1}),
 ('p14', "Took a pay cut to stay", "Won everything abroad", {'LO': 1, 'TR': -1, 'MON': 1}),
 ('p15', "Retired at his boyhood club", "Last big payday in Saudi Arabia", {'LO': 1, 'MON': 1}),
 ('p16', "Leads by shouting", "Leads by example", {'CAP': 1, 'HU': -1}),
 ('p17', "Openly backs LGBTQ+ fans", "Keeps out of politics", {'CA': 1}),
 ('p18', "Overachiever who got the most from his gifts", "Superstar who delivered", {'UN': 1, 'AB': -1}),
 ('p19', "Flawed genius", "Model professional", {'AB': 1, 'ST': 1, 'CH': -1}),
 ('p20', "You watched his whole career", "A legend from before your time", {'ERA': 1}),
 ('p21', "Pioneer of the women's game", "Star of the men's game", {'W': 1}),
 ('p22', "Hometown hero", "World famous", {'LOC': 1, 'AB': -1}),
 ('p23', "Defender who reads the game", "Winger who beats his man", {'WK': 1, 'ST': -1}),
 ('p24', "Ran the length of the pitch to celebrate with the away end", "Went straight back to the halfway line", {'BO': 1, 'HU': -1}),
]
# gut ratings: the fit target. Active and all-time, men and women, spread over the traits.
ACTIVE = ["Mohamed Salah", "Virgil van Dijk", "Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappé", "Erling Haaland", "Harry Kane",
          "Jude Bellingham", "Lamine Yamal", "Vinícius Júnior", "Marcus Rashford", "Son Heung-min", "Christian Pulisic", "Thomas Müller",
          "Marco Reus", "Luka Modrić", "Neymar", "Sophia Wilson", "Lindsey Horan", "Aitana Bonmatí"]
ALLTIME = ["Steven Gerrard", "Francesco Totti", "Paolo Maldini", "Zinedine Zidane", "Diego Maradona", "Johan Cruyff", "Ronaldinho",
           "Thierry Henry", "Roy Keane", "Eric Cantona", "Xavi", "Andrés Iniesta", "Luis Suárez", "Wayne Rooney", "David Beckham",
           "Landon Donovan", "Megan Rapinoe", "Christine Sinclair", "Kenny Dalglish", "Didier Drogba"]
BAG = [('b01', "Racist abuse of an opponent"), ('b02', "Credible domestic-abuse or assault allegations"), ('b03', "A doping ban"),
       ('b04', "Match-fixing or betting breaches"), ('b05', "Tax-fraud conviction"), ('b06', "Biting or violent conduct on the pitch"),
       ('b07', "A reputation for diving"), ('b08', "Forcing a transfer by refusing to play"), ('b09', "Joining his club's bitter rival"),
       ('b10', "Moving to the Saudi league for the money"), ('b11', "Starring for a state-owned club"), ('b12', "Paid ambassador for an authoritarian government")]
SETS = [(0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (0, 4, 8, 6), (1, 5, 9, 11), (2, 7, 10, 3), (0, 9, 6, 10), (1, 7, 4, 11), (2, 5, 8, 3)]
CHOICES = [
 ('s01', "Women players on these lists?", ["In the same lists as the men, rated in their own context", "Their own separate lists", "Leave them out"], 1),
 ('s02', "For the all-time list, players from before your time…", ["Count the same as anyone", "Count a bit less", "Only players I watched"], 1),
 ('s03', "Which players do you most love watching? Pick up to two.", ["Playmaker / No. 10", "Winger", "Striker", "Box-to-box midfielder",
   "Holding midfielder", "Centre-back", "Full-back", "Goalkeeper"], 2),
 ('s04', "A player who spent his best years at a club you dislike (say, Man City)…", ["Counts against him a lot", "Counts against him a little", "Doesn't matter"], 1),
 ('s05', "A player who starred for one of your clubs (Liverpool, Dortmund, Timbers, Thorns, Republic)…", ["Big boost", "Some boost", "No boost"], 1),
 ('s06', "A player who did something bad, apologized and changed…", ["It still counts in full", "It counts less", "It's forgiven"], 1),
 ('s07', "US national team players…", ["Get a boost", "Get a small boost", "No boost"], 1),
 ('s08', "Trophies a player won…", ["Matter a lot", "Matter some", "Barely matter"], 1),
]
BUDGET = [('F_CH', "Character", "Conduct, causes, how he treats people"), ('F_LO', "Loyalty & bond", "One club, long service, connection with fans"),
          ('F_ST', "Joy to watch", "Style, flair, the way he plays"), ('F_WK', "Team player", "Work rate, humility, running for teammates"),
          ('F_AB', "Greatness", "Pure ability at his peak"), ('F_LE', "Legacy", "Moments, influence, trophies"),
          ('F_CO', "Connection", "Played for your clubs or your country")]
items = [dict(id=i, t='pick', l=l, r=r) for i, l, r, _ in PICKS]
items += [dict(id=f'r{g}', t='rate', title=title, players=ps) for g, title, ps in
          [(1, "Active players, part 1", ACTIVE[:10]), (2, "Active players, part 2", ACTIVE[10:]), (3, "All-time, part 1", ALLTIME[:10]), (4, "All-time, part 2", ALLTIME[10:])]]
items += [dict(id=f'm{j+1}', t='maxdiff', opts=[BAG[i][0] for i in s]) for j, s in enumerate(SETS)]
items += [dict(id=i, t='choice', q=q, opts=o, multi=m) for i, q, o, m in CHOICES]
items += [dict(id='budget', t='budget', factors=[dict(k=k, label=l, hint=h) for k, l, h in BUDGET])]
json.dump(dict(items=items, bag=dict(BAG)), open(here / 'questions.json', 'w'), ensure_ascii=False)
json.dump(dict(picks={i: k for i, _, _, k in PICKS}), open(here / 'key.json', 'w'), indent=1)
print(len(items), 'screens')
