"""Quiz round 13: nations (Kevin, 2026-10-09: "do the nation quiz"). No earlier round asked about national teams, so
nation Affinity borrowed everything from clubs. This round gives nations their own evidence.

Part A, 16 blind vignettes: national teams described without names (fans, conduct, history, federation, team, record,
the country's government, Kevin's ancestry), gut-rated 0-10 with a "don't know" option. Hidden key: the nation.
Part B, 12 mystery pairs over 8 attributes, built to price the trade-offs only nations have: a government's record
against winning, ancestry, fans and conduct (plus single-attribute checks).
Part C, 5 direct questions.

Usage: python3 scripts/affinity/quiz13/bank.py [page.html]
"""
import json, pathlib, sys
here = pathlib.Path(__file__).resolve().parent

GUT = [  # (id, nation, description)
 ('g01', 'Japan', "Fans famous for cleaning the stadium after every match. A well-run federation with a long-term plan. Quick, disciplined passing team. Reached the knockouts of the last two World Cups. A free democracy."),
 ('g02', 'Denmark', "Friendly, loud travelling support. The federation pushed human-rights messages at the 2022 World Cup. A close squad that rallied when its playmaker collapsed on the pitch in 2021. One continental title. Missed the 2026 World Cup."),
 ('g03', 'Germany', "Four world titles. A federation that spoke up on human rights in 2022. Precise, pressing team, but out early at the last three World Cups. About 6% of your ancestry is from here."),
 ('g04', 'Portugal', "Ranked in the world's top 5. Built for two decades around one famous, divisive star, now playing in Saudi Arabia. A stable federation. Continental champions in 2016. About 17% of your ancestry is from its Atlantic islands."),
 ('g05', 'Spain', "World champions in 2026 and European champions in 2024, with a young passing side. Its federation president was banned after forcing a kiss on a player at the 2023 Women's World Cup final."),
 ('g06', 'Brazil', "Five world titles, the most of anyone, and the game's most joyful history. Recent teams lean on flair over effort. The federation has had repeated corruption cases and court-ordered leadership changes. Out in the round of 16 in 2026."),
 ('g07', 'Argentina', "World champions in 2022, runners-up in 2026. Some of the most passionate fans anywhere, but players and fans have been sanctioned for racist and homophobic chants. The same federation president since 2017."),
 ('g08', 'Morocco', "The first African team to reach a World Cup semi-final, in 2022; quarter-finals in 2026. Electric home support. A country rated Partly Free, where journalists have been jailed."),
 ('g09', 'Mexico', "A huge, loyal following that fills stadiums across the US. Repeated FIFA sanctions over a homophobic chant. A federation long tied to a TV network. A country rated Partly Free, among the most dangerous for journalists. Round of 16 as a 2026 co-host."),
 ('g10', 'Croatia', "A country of 4 million that reached a World Cup final and a semi-final. Gritty, gifted midfield. Fans repeatedly sanctioned for far-right and racist chants; a former football boss convicted of corruption."),
 ('g11', 'Iran', "Players refused to sing the anthem in 2022 in support of protests at home. A government rated among the least free in the world, which controls the federation and has kept women out of stadiums. A regular World Cup qualifier."),
 ('g12', 'Iceland', "A nation of 380,000 whose thunderclap made its 2016 European run famous. Built from a grassroots coaching programme, once co-managed by a part-time dentist. Hasn't reached a major tournament since 2018."),
 ('g13', 'Canada', "A rising team with a young core; co-hosted the 2026 World Cup and reached the round of 16. Support still finding its identity. The federation was fined over a drone-spying scandal at the 2024 Olympics and fought its players over pay."),
 ('g14', 'Turkey', "One of the loudest crowds in Europe and an exciting young team. A government rated Not Free, with jailed journalists and opponents. Out in the group stage in 2026."),
 ('g15', 'Netherlands', "Home of total football; three World Cup finals, never a win. Liverpool's captain and three teammates are regulars. Orange-clad, party-loving fans and a well-run federation."),
 ('g16', 'England', "Invented the game; one World Cup, in 1966. Third place in 2026. A big, loud away following with a history of hooliganism that still flares at tournaments. A wealthy, well-run federation. About 40% of your ancestry is from here."),
]
# Mystery nations: attribute (code, row label, levels). The key maps each level to model inputs (fit.py).
ATT = [
 ('F', 'Fans', ['Quiet crowds', 'Loyal, steady support', 'One of the loudest followings anywhere']),
 ('V', 'Conduct', ['Fans sanctioned for racist chants, more than once', 'Nothing of note', 'Known for fair play and standing up for causes']),
 ('H', 'History', ['Rarely at big tournaments', 'Some famous runs', 'Former world champions']),
 ('O', 'Federation', ['Run by people close to the government, with corruption cases', 'An ordinary federation', 'Transparent and well run']),
 ('T', 'Team', ['Defensive, built around one star', 'An honest, average side', 'Relentless and united, long-serving coach']),
 ('R', 'Record', ['Rarely qualifies', 'Reaches the knockouts now and then', 'Top 10 in the world']),
 ('G', 'Government', ['A free democracy', 'Partly free: jailed journalists, captured courts', 'Authoritarian: no free elections, political prisoners']),
 ('A', 'Your ancestry', ['None of your ancestry', 'A little of your ancestry (about 5%)', 'A large share of your ancestry (about 15%)']),
]
BASE = dict(F=1, V=1, H=1, O=1, T=1, R=1, G=0, A=0)
PAIRS = [  # (id, changes for A, changes for B, what it tests)
 ('p01', dict(G=1, R=2), dict(G=0, R=0), 'government vs record'),
 ('p02', dict(G=2, F=2, H=2), dict(G=0, F=0, H=0), 'authoritarian vs fans + history'),
 ('p03', dict(A=2, V=0), dict(A=0, V=1), 'ancestry vs racism'),
 ('p04', dict(A=2, G=1), dict(A=0, G=0), 'ancestry vs government'),
 ('p05', dict(V=0, R=2), dict(V=1, R=1), 'racism vs record'),
 ('p06', dict(O=0, T=2), dict(O=2, T=1), 'federation vs team'),
 ('p07', dict(F=2, V=0), dict(F=0, V=2), 'fans vs conduct'),
 ('p08', dict(H=2, T=0), dict(H=0, T=2), 'history vs team'),
 ('p09', dict(G=1, V=2, F=2), dict(G=0, V=1, F=1), 'government vs good conduct + fans'),
 ('p10', dict(R=2), dict(R=0), 'record alone'),
 ('p11', dict(G=0), dict(G=1), 'government alone'),
 ('p12', dict(A=1), dict(A=0), 'ancestry alone'),
]
DIRECT = [
 ('d01', "A country's government jails journalists and opponents. How much should that count against its national team?",
  ["A lot: I'd struggle to root for them", 'Some', 'A little', "Not at all: the team isn't the government"]),
 ('d02', 'Your home nation plays a nation many of your ancestors came from. Who do you root for?',
  ['My home nation, easily', 'My home nation, mostly', 'Depends on the match', 'The nation of my ancestors']),
 ('d03', 'Does this change how you feel about a national team? Many of its players star for clubs you like.', None),
 ('d04', 'Does this change how you feel about a national team? It has been winning a lot lately.', None),
 ('d05', 'Does this change how you feel about a national team? Its fans are sanctioned for homophobic chants.', None),
]
SCALE5 = ['Like them a lot more', 'Like them a bit more', 'No difference', 'Like them a bit less', 'Like them a lot less']

def levels(ch): d = dict(BASE); d.update(ch); return d
items, key = [], dict(att=ATT, gut={}, pairs=[], direct={})
for i, n, txt in GUT:
    items.append(dict(id=i, t='gut', q=txt)); key['gut'][i] = n
for i, a, b, what in PAIRS:
    A, B = levels(a), levels(b)
    items.append(dict(id=i, t='conj', rows=[r for _, r, _ in ATT], l=[lv[A[c]] for c, _, lv in ATT], r=[lv[B[c]] for c, _, lv in ATT]))
    key['pairs'].append(dict(id=i, A=A, B=B, tests=what))
for i, q, opts in DIRECT:
    items.append(dict(id=i, t='choice', q=q, opts=opts or SCALE5)); key['direct'][i] = opts or SCALE5
json.dump(dict(items=items), open(here / 'questions.json', 'w'), ensure_ascii=False)
json.dump(key, open(here / 'key.json', 'w'), ensure_ascii=False, indent=1)
if len(sys.argv) > 1:
    pathlib.Path(sys.argv[1]).write_text((here / 'page.template.html').read_text().replace('/*__QUESTIONS__*/', json.dumps(dict(items=items), ensure_ascii=False)))
print(len(GUT), 'vignettes,', len(PAIRS), 'pairs,', len(DIRECT), 'direct')
