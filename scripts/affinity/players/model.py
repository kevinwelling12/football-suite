"""Player research loader for the Affinity model (scripts/affinity/affinity.py rates every player).

Loads the researched facts (research/out/*.json) and factor scores (scores/*.json, SCORING_BRIEF.md) and applies, in order:
- the independent audit (audit/merged.json) and the loyalty re-scores (audit/lo_out*.json: judged from when a player
  settles, around 23; Kevin, 2026-10-06);
- Kevin's values (quiz rounds 11 and 12): Character shifts by VALUES_X x sum(weight x tag) from values/ and values2/;
- incident corrections (audit/incidents.json: dropped, retyped, new outcomes, missing incidents added).
The rating itself (character, hard lines, record, connection) lives in affinity.py; hard-line severities in inputs.py.
"""
import json, glob, pathlib, re, unicodedata
root = pathlib.Path(__file__).resolve().parents[3]
here = pathlib.Path(__file__).resolve().parent
K = ['CH', 'WK', 'LO', 'AB', 'ST', 'LE']
VALUES_X = 0.6  # how far Kevin's values tags move Character (0.3 -> 0.6 when he asked to strengthen it, 2026-10-07)
FIXES = {}      # Kevin's own factor corrections (none recorded; he asked for independent research instead, 2026-10-06)
NOW = 2026

def norm(s):
    s = unicodedata.normalize('NFD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\b(fc|cf|sc|afc|ac|the)\b', '', re.sub(r'[^a-z0-9 ]', ' ', s)).split()

ALIAS = {'man city': 'manchester city', 'man utd': 'manchester united', 'man united': 'manchester united', 'psg': 'paris saint germain',
         'inter miami': 'inter miami', 'nycfc': 'new york city football club', 'new york city': 'new york city football club',
         'leipzig': 'rb leipzig', 'bayern': 'bayern munich', 'bayern munchen': 'bayern munich', 'spurs': 'tottenham hotspur'}

def seasons(c):
    a, b = c.get('from'), c.get('to') or NOW
    return max(0.5, (b - a)) if a else 0

# Money leagues (Kevin, 2026-10-06): Saudi, Qatari, Emirati and Chinese Super League clubs; inputs.py prices the move.
MONEY = re.compile(r"\bal[- ](nassr|hilal|ittihad|ahli|ettifaq|diriyah|qadsiah|shabab|sadd|duhail|arabi|gharafa|rayyan|wasl|ain|jazira|wahda)\b|"
                   r"shanghai (shenhua|sipg|port)|guangzhou (evergrande|fc)|jiangsu suning|hebei|beijing guoan|tianjin|dalian (yifang|pro)|shandong")

def load(raw=False):
    """Facts and scores. Unless raw, the independent audit is applied: merged scores (audit/merged.json) and incident
    corrections (audit/incidents.json: dropped, retyped, new outcomes, missing incidents added)."""
    facts = {}
    for f in sorted(glob.glob(str(here / 'research' / 'out' / '*.json'))):
        for p in json.load(open(f)):
            if p['name'] in facts and len(json.dumps(facts[p['name']])) >= len(json.dumps(p)): continue
            facts[p['name']] = p
    scores = {}
    for f in sorted(glob.glob(str(here / 'scores' / '*.json'))):
        for s in json.load(open(f)): scores.setdefault(s['name'], s)
    if raw: return facts, scores
    a = here / 'audit'
    if (a / 'merged.json').exists():
        for n, m in json.loads((a / 'merged.json').read_text()).items():
            if n in scores: scores[n] = {**scores[n], **{k: m[k] for k in K if k in m}}
    for f in sorted(a.glob('lo_out*.json')):  # Loyalty re-scored from when a player settles (Kevin, 2026-10-06; LO_BRIEF.md)
        for n, v in json.loads(f.read_text()).items():
            if n in scores: scores[n] = {**scores[n], 'LO': v['LO']}
    # Character = research score shifted by Kevin's values (quiz round 11 weights x the values tags in values/out*.json):
    # + VALUES_X * sum(weight * tag), clipped 0-10 (Kevin, 2026-10-07; VALUES_X 0.3 -> 0.6 when he asked to strengthen it). A shift, not an average: an untagged player keeps his
    # research score (averaging with a neutral 6 dragged good characters down and lifted bad ones).
    # Rounds 11 and 12 (values/, values2/) add up.
    shift = {}
    for quiz, folder in (('quiz11', 'values'), ('quiz12', 'values2')):
        vw = here.parent / quiz / 'fit.json'
        if not vw.exists(): continue
        VW = json.loads(vw.read_text())['w']
        for f in sorted((here / folder).glob('out*.json')):
            for n, tg in json.loads(f.read_text()).items():
                if n in scores: shift[n] = shift.get(n, 0) + sum(VW[k] * float(tg.get(k) or 0) for k in VW)
    for n, v in shift.items():
        ch = max(0.0, min(10.0, scores[n]['CH'] + VALUES_X * v))
        scores[n] = {**scores[n], 'CH_research': scores[n]['CH'], 'CH_values': round(VALUES_X * v, 2), 'CH': round(ch, 2)}
    if (a / 'incidents.json').exists():
        for n, fx in json.loads((a / 'incidents.json').read_text()).items():
            if n not in facts: continue
            p = dict(facts[n]); inc, mon = list(p.get('incidents') or []), list(p.get('money_moves') or [])
            allv = inc + mon; drop = set()
            for v in fx.get('verdicts', []):
                i = v.get('i')
                if not isinstance(i, int) or i >= len(allv): continue
                e = allv[i] = dict(allv[i])
                if v['verdict'] == 'wrong': drop.add(i)
                elif v['verdict'] == 'retype' and v.get('type'): e['type'] = v['type']
                elif v['verdict'] == 'outcome' and v.get('outcome'): e['outcome'] = v['outcome']
            p['incidents'] = [e for i, e in enumerate(allv[:len(inc)]) if i not in drop] + list(fx.get('missing', []))
            p['money_moves'] = [e for i, e in enumerate(allv[len(inc):], len(inc)) if i not in drop]
            facts[n] = p
    return facts, scores

