"""Historical betting odds for played matches, for backtesting the pick 'em blend (2026-10-10).

  python3 scripts/odds/history.py      # writes scripts/odds/history.json and reports unmatched rows

Source: football-data.co.uk (season 2026-27 files for the Premier League E0, Championship E1, Bundesliga D1, LaLiga SP1,
Serie A I1, Ligue 1 F1; MLS from new/USA.csv). Pre-match average odds (AvgH/D/A, Avg>2.5/<2.5) where given, else closing
averages (MLS has closing only). Matched to tracker fixtures by date (+/-1 day) and normalised team names.
"""
import csv, io, json, pathlib, re, unicodedata, urllib.request, datetime
root = pathlib.Path(__file__).resolve().parents[2]
D = json.loads((root / 'data' / 'suite_data.json').read_text())
FILES = {'epl': 'mmz4281/2627/E0.csv', 'ch': 'mmz4281/2627/E1.csv', 'bl': 'mmz4281/2627/D1.csv', 'esp': 'mmz4281/2627/SP1.csv',
         'ita': 'mmz4281/2627/I1.csv', 'fra': 'mmz4281/2627/F1.csv', 'mls': 'new/USA.csv'}
ALIAS = {'man united': 'manchester united', 'man city': 'manchester city', "nott'm forest": 'nottingham forest', 'wolves': 'wolverhampton wanderers',
         'tottenham': 'tottenham hotspur', 'newcastle': 'newcastle united', 'west ham': 'west ham united', 'brighton': 'brighton',
         'sheffield weds': 'sheffield wednesday', 'sheffield united': 'sheffield united', 'qpr': 'queens park rangers', 'west brom': 'west bromwich albion',
         "m'gladbach": 'borussia monchengladbach', 'ein frankfurt': 'eintracht frankfurt', 'fc koln': '1. fc koln', 'leverkusen': 'bayer leverkusen',
         'dortmund': 'borussia dortmund', 'bayern munich': 'bayern munich', 'union berlin': 'union berlin', 'st pauli': 'st. pauli',
         'ath madrid': 'atletico madrid', 'ath bilbao': 'athletic club', 'betis': 'real betis', 'sociedad': 'real sociedad', 'vallecano': 'rayo vallecano',
         'celta': 'celta vigo', 'espanol': 'espanyol', 'la coruna': 'deportivo la coruna', 'paris sg': 'paris saint-germain', 'st etienne': 'saint-etienne',
         'inter': 'inter milan', 'milan': 'ac milan', 'roma': 'roma', 'verona': 'hellas verona',
         'mainz': 'mainz 05', 'santander': 'racing santander', 'atlanta utd': 'atlanta united', 'los angeles fc': 'los angeles football club', 'los angeles galaxy': 'la galaxy', 'new york city': 'new york city football club',
         'new york red bulls': 'red bull new york', 'st. louis city': 'st. louis city sc', 'dc united': 'd.c. united', 'montreal': 'cf montreal'}
def norm(s):
    s = unicodedata.normalize('NFD', s or '').encode('ascii', 'ignore').decode().lower().strip()
    s = ALIAS.get(s, s)
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\b(fc|afc|cf|sc|ac|club|de|the|cd|ud|sd|rc|ssc|as|us|sv|vfb|vfl|tsg|1|hotspur|albion|city|town|united)\b', '', s))
def full(s):  # alias, then compare the whole name (so Manchester United and Manchester City stay apart)
    s = unicodedata.normalize('NFD', s or '').encode('ascii', 'ignore').decode().lower().strip()
    return re.sub(r'[^a-z0-9]', '', ALIAS.get(s, s))
def fl(x):
    try: return float(x)
    except: return None
out, miss = {}, []
for k, f in FILES.items():
    raw = urllib.request.urlopen(urllib.request.Request('https://www.football-data.co.uk/' + f, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read().decode('utf-8-sig')
    rows = list(csv.DictReader(io.StringIO(raw)))
    if k == 'mls': rows = [r for r in rows if r.get('League') == 'MLS' and r.get('Season') == '2026']
    T = D[k]['teams']; idx = {}
    exact = {full(n): i for i, t in enumerate(T) for n in {t['name'], t.get('short') or t['name']}}
    for i, t in enumerate(T):
        for n in {t['name'], t.get('short') or t['name']}: idx.setdefault(norm(n), i)
    fx = {}
    for fid, x in enumerate(D[k]['fixtures']): fx.setdefault((x[2], x[3]), []).append((fid, x[1]))
    out[k] = {}
    for r in rows:
        hn, an = r.get('HomeTeam') or r.get('Home'), r.get('AwayTeam') or r.get('Away')
        h, a = exact.get(full(hn), idx.get(norm(hn))), exact.get(full(an), idx.get(norm(an)))
        if h is None or a is None: miss.append((k, hn if h is None else '', an if a is None else '')); continue
        d = datetime.datetime.strptime(r['Date'], '%d/%m/%Y' if len(r['Date']) == 10 else '%d/%m/%y').date()
        cand = [fid for fid, ds in fx.get((h, a), []) if abs((datetime.date.fromisoformat(ds) - d).days) <= 1]
        if not cand: miss.append((k, f'{hn} v {an} {d}', 'no fixture')); continue
        odds = dict(H=fl(r.get('AvgH')) or fl(r.get('AvgCH')), D=fl(r.get('AvgD')) or fl(r.get('AvgCD')), A=fl(r.get('AvgA')) or fl(r.get('AvgCA')),
                    O=fl(r.get('Avg>2.5')) or fl(r.get('AvgC>2.5')), U=fl(r.get('Avg<2.5')) or fl(r.get('AvgC<2.5')),
                    closing=not fl(r.get('AvgH')))
        if odds['H'] and odds['D'] and odds['A']: out[k][cand[0]] = odds
(pathlib.Path(__file__).parent / 'history.json').write_text(json.dumps(out, indent=0))
print({k: len(v) for k, v in out.items()}, 'matched;', len(miss), 'unmatched')
for m in sorted(set(miss))[:60]: print('  ', m)
