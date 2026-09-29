"""Round-5 sub-weights: rebuild Culture, Values and Team from their parts (research in research/out5).

python3 scripts/affinity/subweights.py      # writes scripts/affinity/sub5.json and prints the biggest moves

Composites (Kevin's quiz round 5, docs/supporter-profile.md):
  Culture = .35 ground + .30 loyalty through bad years + .25 loudness + .10 away following
  Values  = .20 community + .20 women's team + .20 causes/identity + .15 academy + .15 affordability + .10 fan voice
            + Vneg (sponsors, player conduct; 0 to -4)
  Team    = .40 player-fan bond + .25 stable squad + .20 icon or defining coach + .15 pressing
Each composite is mapped linearly onto the old factor's mean and spread across the same clubs, so clubs stay on
the scale nations (not re-rated) use, and the anchors keep their meaning; only the order within a factor changes.
Decay: a racism or fan-violence adjustment whose last serious incident was 5+ years ago (2021 or earlier) and is
not ongoing counts half.
"""
import ast, json, pathlib, re, statistics as st, sys

root = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'scripts' / 'affinity'))
from scores import S as S0
S = dict(S0)
for node in ast.parse((root / 'scripts' / 'importers' / 'build_usl.py').read_text()).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'A':
        S.update(ast.literal_eval(node.value))
CW = {'CG': .35, 'CY': .30, 'CL': .25, 'CA': .10}
VW = {'VC': .20, 'VW': .20, 'VI': .20, 'VA': .15, 'VP': .15, 'VF': .10}
TW = {'TB': .40, 'TS': .25, 'TI': .20, 'TP': .15}
LABEL = {'CG': 'Ground', 'CY': 'Loyal', 'CL': 'Loud', 'CA': 'Away', 'VC': 'Community', 'VW': "Women's team", 'VI': 'Causes',
         'VA': 'Academy', 'VP': 'Prices', 'VF': 'Fan voice', 'TB': 'Bond', 'TS': 'Stable', 'TI': 'Icon', 'TP': 'Pressing'}
DECAY_BEFORE = 2021
# Values deductions that repeat something an adjustment already counts (violence/racism): corrected here.
VNEG_FIX = {'Eintracht Frankfurt': (0, 'UEFA fan sanctions already in the fan-violence adjustment'),
            'Nice': (-1, 'VBET sponsor only; the ultras assault is in the fan-violence adjustment')}


def sc(r, k):
    v = r.get(k, {})
    return float(v['score'] if isinstance(v, dict) else v)


def main():
    R = {}
    for f in sorted((root / 'scripts' / 'affinity' / 'research' / 'out5').glob('*.json')):
        for r in json.loads(f.read_text()):
            R[r['name']] = r
    names = [n for n in R if n in S]
    raw = {}
    for n in names:
        r = R[n]
        vneg = float(VNEG_FIX[n][0] if n in VNEG_FIX else (r.get('Vneg') or {}).get('points', 0))
        raw[n] = (sum(w * sc(r, k) for k, w in CW.items()),
                  min(10, max(0, sum(w * sc(r, k) for k, w in VW.items()) + vneg)),
                  sum(w * sc(r, k) for k, w in TW.items()))
    out = {}
    maps = []
    for i, old_i in ((0, 0), (1, 1), (2, 4)):   # C, V, Team (slot S = index 4 in scores tuples)
        new = [raw[n][i] for n in names]; old = [S[n][old_i] for n in names]
        a = st.pstdev(old) / (st.pstdev(new) or 1); b = st.mean(old) - a * st.mean(new)
        maps.append((a, b))
    for n in names:
        r = R[n]
        C, V, T = (round(min(10, max(0, maps[j][0] * raw[n][j] + maps[j][1])), 1) for j in range(3))
        adj0, note = S[n][5], S[n][6]
        adj, newnote = adj0, note
        for inc in r.get('incidents') or []:
            y, ongoing = inc.get('last_year'), inc.get('ongoing')
            if not y or ongoing or y > DECAY_BEFORE: continue
            ty = 'Racism' if inc.get('type') == 'racism' else 'Fan violence'
            m = re.search(re.escape(ty) + r' -(\d+)', newnote)
            if not m: continue
            v = int(m.group(1)); h = round(v / 2)
            adj += v - h; newnote = newnote.replace(f'{ty} -{v}', f'{ty} -{h} (last incident {y}, halved)', 1)
        parts = {k: int(sc(r, k)) for k in list(CW) + list(VW) + list(TW)}
        parts['Vneg'] = VNEG_FIX[n][0] if n in VNEG_FIX else (r.get('Vneg') or {}).get('points', 0)
        out[n] = dict(C=C, V=V, S=T, adj=adj, note=newnote, parts=parts)
    (root / 'scripts' / 'affinity' / 'sub5.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
    moves = sorted(((out[n]['C'] - S[n][0]) * .23 + (out[n]['V'] - S[n][1]) * .26 + (out[n]['S'] - S[n][4]) * .15, n) for n in names)
    print(f'{len(out)} clubs; maps C/V/T:', [(round(a, 2), round(b, 2)) for a, b in maps])
    print('down:', [(n, round(v / .9 * 10, 1)) for v, n in moves[:10]])
    print('up:', [(n, round(v / .9 * 10, 1)) for v, n in moves[-10:]])
    print('decayed:', [(n, out[n]['note']) for n in names if out[n]['adj'] != S[n][5]])


if __name__ == '__main__':
    main()
