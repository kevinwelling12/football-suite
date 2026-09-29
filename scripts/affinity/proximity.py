"""Proximity: US and Canadian clubs near Sacramento get a small bonus (Kevin, 2026-09-28).

python3 scripts/affinity/proximity.py   # print distances and bonuses

bonus = 4 * (1 - miles / 800), 0 beyond 800 miles (straight line from Sacramento to the club's stadium).
Bay Area clubs get about +3.6, Los Angeles +2.2, Portland +1.6, Seattle +0.9. Sacramento Republic is left out:
it already has the hometown +4. Clubs outside North America get nothing.
"""
import math

HOME = (38.58, -121.49)  # Sacramento
MAX, RANGE = 4.0, 800.0  # max 3 until quiz round 5
SKIP = {'Sacramento Republic FC'}
# Stadium coordinates (lat, lon)
AT = {
    'Atlanta United': (33.76, -84.40), 'Austin FC': (30.39, -97.72), 'CF Montréal': (45.56, -73.55),
    'Charlotte FC': (35.23, -80.85), 'Chicago Fire FC': (41.86, -87.62), 'Colorado Rapids': (39.81, -104.89),
    'Columbus Crew': (39.97, -83.02), 'D.C. United': (38.87, -77.01), 'FC Cincinnati': (39.11, -84.52),
    'FC Dallas': (33.16, -96.84), 'Houston Dynamo FC': (29.75, -95.35), 'Inter Miami CF': (25.79, -80.25),
    'LA Galaxy': (33.86, -118.26), 'Los Angeles Football Club': (34.01, -118.29), 'Minnesota United FC': (44.95, -93.17),
    'Nashville SC': (36.13, -86.77), 'New England Revolution': (42.09, -71.26), 'New York City Football Club': (40.76, -73.84),
    'Orlando City': (28.54, -81.39), 'Philadelphia Union': (39.83, -75.38), 'Portland Timbers': (45.52, -122.69),
    'Real Salt Lake': (40.58, -111.89), 'Red Bull New York': (40.74, -74.15), 'San Diego FC': (32.78, -117.12),
    'San Jose Earthquakes': (37.35, -121.93), 'Seattle Sounders FC': (47.60, -122.33), 'Sporting Kansas City': (39.12, -94.82),
    'St. Louis CITY SC': (38.63, -90.21), 'Toronto FC': (43.63, -79.42), 'Vancouver Whitecaps FC': (49.28, -123.11),
    'Angel City FC': (34.01, -118.29), 'Bay FC': (37.35, -121.93), 'Boston Legacy': (42.31, -71.09),
    'Chicago Stars': (42.07, -87.69), 'Denver Summit': (39.74, -104.99), 'Gotham FC': (40.74, -74.15),
    'Houston Dash': (29.75, -95.35), 'Kansas City Current': (39.11, -94.59), 'North Carolina Courage': (35.79, -78.78),
    'Orlando Pride': (28.54, -81.39), 'Portland Thorns': (45.52, -122.69), 'Racing Louisville': (38.26, -85.74),
    'San Diego Wave': (32.78, -117.12), 'Seattle Reign': (47.60, -122.33), 'Utah Royals': (40.58, -111.89),
    'Washington Spirit': (38.87, -77.01), 'Birmingham Legion FC': (33.51, -86.81), 'Brooklyn FC': (40.57, -73.98),
    'Charleston Battery': (32.79, -79.94), 'Colorado Springs Switchbacks FC': (38.84, -104.82), 'Detroit City FC': (42.40, -83.05),
    'El Paso Locomotive FC': (31.76, -106.49), 'FC Tulsa': (36.16, -95.99), 'Hartford Athletic': (41.76, -72.69),
    'Indy Eleven': (39.77, -86.16), 'Las Vegas Lights FC': (36.17, -115.14), 'Lexington SC': (38.04, -84.50),
    'Loudoun United FC': (39.10, -77.56), 'Louisville City FC': (38.26, -85.74), 'Miami FC': (25.75, -80.37),
    'Monterey Bay FC': (36.65, -121.81), 'New Mexico United': (35.08, -106.65), 'Oakland Roots SC': (37.75, -122.20),
    'Orange County SC': (33.66, -117.76), 'Phoenix Rising FC': (33.45, -112.07), 'Pittsburgh Riverhounds': (40.44, -80.01),
    'Rhode Island FC': (41.88, -71.38), 'Sacramento Republic FC': (38.58, -121.51), 'San Antonio FC': (29.42, -98.49),
    'Sporting JAX': (30.33, -81.66), 'Tampa Bay Rowdies': (27.77, -82.63),
}


def miles(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))


def bonus(name):
    """-> (bonus, miles) or None"""
    if name not in AT or name in SKIP:
        return None
    d = miles(HOME, AT[name])
    return round(max(0.0, MAX * (1 - d / RANGE)), 1), round(d)


if __name__ == '__main__':
    for n in sorted(AT, key=lambda n: miles(HOME, AT[n])):
        b = bonus(n)
        if b and b[0]: print(f'+{b[0]:.1f}  {b[1]:4} mi  {n}')
