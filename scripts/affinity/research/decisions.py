"""Apply Kevin's review answers (2026-09-28, see REVIEW.md) to the research outputs.

Reads out/<batch>.json, writes final/<batch>.json. The research files are never edited.
python3 scripts/affinity/research/decisions.py && python3 scripts/affinity/research/compare.py --dir final
"""
import copy, json, pathlib

R = pathlib.Path(__file__).resolve().parent
(R / 'final').mkdir(exist_ok=True)

# Factor overrides: name -> {factor: score}
FACTORS = {
    'Sacramento Republic FC': {'C': 9, 'H': 6},   # Q: Culture 9, History 6
    'Portland Thorns': {'V': 8},                   # Q: judge on today
    'Reading': {'V': 5},                           # casino sponsor, half weight
    'Leicester City': {'V': 5},                    # casino/crypto sponsor, half weight
    'Cardiff City': {'V': 4},                      # Partly Free state tourism board counts in full
}

# Adjustment overrides: name -> list of (type, new points or None to drop, note)
ADJ = {
    # State reach: satellites of a state-controlled group get half (-12)
    'Troyes': [('state', -12, 'satellite of state-controlled City Football Group')],
    'New York City Football Club': [('state', -12, 'satellite of state-controlled City Football Group')],
    # Multi-club: only secondary clubs pay; the owner's flagship gets 0
    'Manchester City': [('multiclub', None, 'flagship of City Football Group')],
    'Chelsea': [('multiclub', None, 'flagship of BlueCo')],
    'Roma': [('multiclub', None, 'Friedkin flagship (Everton, Cannes secondary)')],
    'CF Montréal': [('multiclub', None, 'Saputo flagship (Bologna secondary)')],
    'D.C. United': [('multiclub', None, 'Levien/Kaplan flagship (Swansea secondary)')],
    'Chicago Fire FC': [('multiclub', None, 'Mansueto flagship (Lugano secondary)')],
    'Udinese': [('multiclub', None, 'Pozzo flagship (Watford secondary)')],
    'Burnley': [('multiclub', None, 'Velocity flagship (Espanyol secondary)')],
    'Leeds United': [('multiclub', None, '49ers Enterprises flagship in Europe (Rangers secondary)')],
    'Aston Villa': [('multiclub', None, 'V Sports flagship (Vitoria SC secondary)')],
    'Bournemouth': [('multiclub', None, 'Black Knight flagship (Lorient, Hibernian secondary)')],
    'Brighton': [('multiclub', None, 'Bloom flagship (Union SG secondary)')],
    'Manchester United': [('multiclub', None, 'INEOS flagship (Nice secondary)')],
    'Southampton': [('multiclub', None, 'Sport Republic flagship (Goztepe, Valenciennes secondary)')],
    'Leicester City': [('multiclub', None, 'King Power flagship (OH Leuven secondary)')],
    'Stockport County': [('multiclub', None, 'owner flagship (Debrecen secondary)')],
    'AC Milan': [('multiclub', None, 'RedBird flagship (Toulouse secondary)')],
    'Napoli': [('multiclub', None, 'De Laurentiis flagship (Bari secondary)')],
    'Paris Saint-Germain': [('multiclub', None, 'QSI flagship (Braga stake secondary)')],
    'RB Leipzig': [('multiclub', None, 'Red Bull flagship in the top tier (New York, Salzburg secondary)')],
    'Washington Spirit': [('multiclub', None, 'Kang flagship (Lyon, London City secondary)')],
    'Huddersfield Town': [('multiclub', None, 'Nagle: two independent clubs, not a network')],
    'Swansea City': [('multiclub', -4, 'Levien/Kaplan secondary club (D.C. United flagship)')],
    # Private equity: only real PE funds count
    'Liverpool': [('pe', None, 'FSG / 1892 Holdings are sports investment groups, not PE funds')],
    'Charlton Athletic': [('pe', None, 'Global Football Partners is an investor group, not a PE fund')],
    'Walsall': [('pe', None, 'Trivela is a sports investment group, not a PE fund')],
    # Nations: Partly Free middle step asked for Ukraine and Moldova
    'Ukraine': [('government', -5, 'wartime measures drive the Freedom House score')],
    'Moldova': [('government', -5, 'Partly Free, RSF 31st')],
    # Previous owners: judge the club on its current owner
    'Everton': [('overspend', None, 'breach under the previous owner (Moshiri)')],
    # Franchise: both apply
    'North Carolina Courage': [('franchise', -10, 'Western New York Flash moved to North Carolina (2017)')],
}
# LBO: smaller scale, -8 to -10
ADJ['Manchester United'] += [('lbo', -10, 'Glazer purchase debt still on the club (smaller LBO scale)')]
ADJ['Burnley'] += [('lbo', -8, 'ALK purchase debt on the club (smaller LBO scale)')]
ADJ['Aston Villa'] += [('pe', None, 'Atairos is a sports investment group, not a PE fund')]
ADJ['Leeds United'] += [('pe', None, '49ers Enterprises is a sports investment group, not a PE fund')]

seen = set()
for bf in sorted(R.glob('b[0-9][0-9]-*.json')):
    out = json.loads((R / 'out' / f'{bf.stem}.json').read_text())
    for e in out:
        n = e['name']
        for k, v in FACTORS.get(n, {}).items():
            e[k] = dict(e[k], score=v, evidence=e[k]['evidence'] + f' [Review: set to {v}.]')
            seen.add(n)
        for typ, pts, note in ADJ.get(n, []):
            seen.add(n)
            adjs = [a for a in e['adjustments'] if a['type'] != typ]
            if pts is not None:
                old = next((a for a in e['adjustments'] if a['type'] == typ), None)
                ev = (old['evidence'] + ' ' if old else '') + f'[Review: {note}.]'
                adjs.append({'type': typ, 'points': pts, 'evidence': ev})
            e['adjustments'] = adjs
            e.setdefault('review', []).append(f'{typ}: {pts if pts is not None else "dropped"} ({note})')
    (R / 'final' / f'{bf.stem}.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')

missing = (set(FACTORS) | set(ADJ)) - seen
print('applied;', 'unmatched names: ' + ', '.join(sorted(missing)) if missing else 'all names matched')
