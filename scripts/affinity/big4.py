"""Kevin's big-4 teams: location, rival markets and ownership ties (Kevin, 2026-09-28).

python3 scripts/affinity/big4.py   # print every club's items

Kevin's teams: Sacramento Kings, San Francisco Giants, San Francisco 49ers, San Jose Sharks.
Rivals (full weight): Lakers; Dodgers; Seahawks, Rams, Cowboys; LA Kings, Ducks, Golden Knights.
Half weight: Athletics (Bay Bridge), Raiders, Packers, Warriors (Kings).

Connection items for the Affinity model (affinity.py adds them up with the other connection items, one cap for all):
- distance from Sacramento (proximity.py): up to +4 for North American clubs (+3 until quiz round 5).
- market: a US club sharing a metro with Kevin's teams +1 (Bay Area: +1 - 0.5 for the Warriors = +0.5); with his rivals -1 per full rival,
  -0.5 per half rival, at most -2. (Seattle was skipped while it carried a rival penalty; that penalty went on 2026-10-02.)
- ownership ties (research in research/big4, BRIEF in BIG4_BRIEF.md): the club's owners also own
  (ownership) or hold a stake in (minority) one of the teams. Kevin's team: +2 ownership, +1 minority.
  Rival: -5 ownership, -2.5 minority, -1 when the club's current owner used to own the rival; half for
  half rivals. Passive fund stakes (Arctos, Sixth Street's revenue deals), stadium concessions and ties
  that ended with an owner who has left are not counted.
"""
import proximity

KEVIN = ['Sacramento Kings', 'San Francisco Giants', 'San Francisco 49ers', 'San Jose Sharks']
RIVAL = {'Los Angeles Lakers': 1, 'Los Angeles Dodgers': 1, 'Seattle Seahawks': 1, 'Los Angeles Rams': 1,
         'Dallas Cowboys': 1, 'Los Angeles Kings': 1, 'Anaheim Ducks': 1, 'Vegas Golden Knights': 1,
         'Athletics': 0.5, 'Las Vegas Raiders': 0.5, 'Green Bay Packers': 0.5, 'Golden State Warriors': 0.5}
BAY = 'Bay Area (Giants, 49ers, Sharks; Warriors)'
LA = 'LA market (Lakers, Dodgers, Rams, Kings, Ducks)'
MARKET = {
    'San Jose Earthquakes': (BAY, 0.5), 'Bay FC': (BAY, 0.5), 'Oakland Roots SC': (BAY, 0.5),
    'Los Angeles Football Club': (LA, -2), 'LA Galaxy': (LA, -2), 'Angel City FC': (LA, -2), 'Orange County SC': (LA, -2),
    'FC Dallas': ('Dallas (Cowboys)', -1), 'Las Vegas Lights FC': ('Las Vegas (Golden Knights, Raiders)', -1.5),
    'Seattle Sounders FC': ('Seattle (Seahawks)', -1), 'Seattle Reign': ('Seattle (Seahawks)', -1),
}
# Republic link (was an adjustment until 2026-10-02): a former Republic player who is a regular at a higher-tier club.
LINKS = {'Los Angeles Football Club': ('Republic link: Aaron Long, a former Republic player', 2.0)}
# "Plastic fan" check (Kevin, 2026-10-09: "I don't want that label"). Glory and brand chasing is the charge, so global
# brands carry a bandwagon pull: Deloitte Football Money League 2026 (2025 revenue) top 5 -3, 6-10 -2, 11-20 -1.
MONEY_LEAGUE = ['Real Madrid', 'Barcelona', 'Bayern Munich', 'Paris Saint-Germain', 'Liverpool', 'Manchester City', 'Arsenal',
                'Manchester United', 'Tottenham Hotspur', 'Chelsea', 'Inter Milan', 'Borussia Dortmund', 'Atlético Madrid',
                'Aston Villa', 'AC Milan', 'Juventus', 'Newcastle United', 'VfB Stuttgart', 'Benfica', 'West Ham United']
# Clubs whose American following is built on celebrity (Beckham and Messi; the Hollywood owners and the TV series): -2.
CELEBRITY = {'Inter Miami CF': 'Celebrity bandwagon (Beckham, Messi)', 'Wrexham': 'Celebrity bandwagon (Hollywood owners, TV series)'}


def brand(name):
    if name in MONEY_LEAGUE:
        r = MONEY_LEAGUE.index(name) + 1
        return (f'Global brand (Money League #{r})', -3 if r <= 5 else -2 if r <= 10 else -1)
    if name in CELEBRITY:
        return (CELEBRITY[name], -2)


# (club, team, kind, why)
TIES = [
    ('Leeds United', 'San Francisco 49ers', 'ownership', 'Owned by 49ers Enterprises'),
    ('Rangers', 'San Francisco 49ers', 'minority', '49ers Enterprises is in the owning consortium'),
    ('Huddersfield Town', 'Sacramento Kings', 'minority', 'Owner Kevin Nagle is a Kings minority owner'),
    ('Sacramento Republic FC', 'Sacramento Kings', 'minority', 'Managing partner Kevin Nagle is a Kings minority owner'),
    ('Portland Thorns', 'Sacramento Kings', 'minority', 'Owners (the Bhathal family) are Kings investors'),
    ('Vancouver Whitecaps FC', 'San Francisco Giants', 'minority', 'Co-owner Jeff Mallett is a Giants principal owner'),
    ('Bay FC', 'San Francisco Giants', 'minority', 'Majority owner Sixth Street holds about 10% of the Giants'),
    ('Arsenal', 'Los Angeles Rams', 'ownership', 'Kroenke owns the Rams'),
    ('Colorado Rapids', 'Los Angeles Rams', 'ownership', 'Kroenke owns the Rams'),
    ('LA Galaxy', 'Los Angeles Kings', 'ownership', 'AEG owns the LA Kings'),
    ('Bournemouth', 'Vegas Golden Knights', 'ownership', 'Bill Foley owns the Golden Knights'),
    ('Lorient', 'Vegas Golden Knights', 'ownership', 'Bill Foley owns the Golden Knights'),
    ('Los Angeles Football Club', 'Los Angeles Dodgers', 'minority', 'Guber and Magic Johnson are Dodgers co-owners'),
    ('Los Angeles Football Club', 'Golden State Warriors', 'minority', 'Guber, Tsao, Karsh and Schneider are Warriors co-owners'),
    ('San Jose Earthquakes', 'Athletics', 'ownership', 'John Fisher owns the Athletics'),
    ('Birmingham City', 'Las Vegas Raiders', 'minority', 'Wagner and Brady hold about 10% of the Raiders'),
    ('Marseille', 'Los Angeles Dodgers', 'former', 'Owner Frank McCourt owned the Dodgers until 2012'),
]
PTS = {'ownership': (2, -5), 'minority': (1, -2.5), 'former': (0, -1)}  # rival -3/-1.5 until quiz round 4
SHORT = {'Sacramento Kings': 'Kings', 'San Francisco Giants': 'Giants', 'San Francisco 49ers': '49ers',
         'San Jose Sharks': 'Sharks', 'Los Angeles Rams': 'Rams', 'Los Angeles Kings': 'LA Kings',
         'Vegas Golden Knights': 'Golden Knights', 'Los Angeles Dodgers': 'Dodgers', 'Athletics': "A's",
         'Las Vegas Raiders': 'Raiders', 'Golden State Warriors': 'Warriors'}


def items(name):
    """-> [(label, points), ...]"""
    out = []
    p = proximity.bonus(name)
    if p and p[0]:
        out.append((f'{p[1]} mi from Sacramento', p[0]))
    if name in MARKET:
        out.append(MARKET[name])
    if name in LINKS:
        out.append(LINKS[name])
    if brand(name):
        out.append(brand(name))
    for club, team, kind, why in TIES:
        if club != name:
            continue
        good, bad = PTS[kind]
        pts = good if team in KEVIN else round(bad * RIVAL[team], 1)
        if pts:
            short = SHORT.get(team, team)
            out.append((why if short in why else f'{why} ({short})', pts))
    return out


if __name__ == '__main__':
    import json, pathlib
    D = json.loads((pathlib.Path(__file__).resolve().parents[2] / 'data' / 'suite_data.json').read_text())
    seen = {t['name'] for c in D.values() for t in c['teams']}
    rows = [(round(sum(p for _, p in its), 1), n, its) for n in seen for its in [items(n)] if its]
    for tot, n, its in sorted(rows, key=lambda x: -x[0]):
        print(f'{tot:+5.1f}  {n:28} ' + '; '.join(f'{l} {p:+g}' for l, p in its))
