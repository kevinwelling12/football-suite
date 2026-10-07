"""Fit Kevin's values weights from round 12 (mystery pairs + direct questions), as quiz11/fit.py.
Pair traits (good side +1 unless named for the bad side): wgame, climate, private_jet, mental_health, fans_close,
fans_rows, taunts, feuds, indiscipline, common_goal. Priors for the pair traits come from related direct answers
(mental health from round 11), else +-1. Direct-only traits keep the stated value (++ 2 ... -- -2).
Usage: python3 scripts/affinity/quiz12/fit.py"""
import json, pathlib, numpy as np
here = pathlib.Path(__file__).resolve().parent
A = json.load(open(here / 'raw' / 'responses' / 'kevin.json')); A = A.get('data', A)['answers']
A11 = json.load(open(here.parent / 'quiz11' / 'raw' / 'responses' / 'kevin.json')); A11 = A11.get('data', A11)['answers']
key = json.load(open(here / 'key.json'))
S = {'++': 2, '+': 1, '0': 0, '-': -1, '--': -2}
F = ['wgame', 'climate', 'private_jet', 'mental_health', 'fans_close', 'fans_rows', 'taunts', 'feuds', 'indiscipline', 'common_goal']
def x(lv):
    wg, cl, mh, fa, re_, tm, di, cg = lv
    return np.array([wg == 0, cl == 0, cl == 2, mh == 0, fa == 0, fa == 2, re_ == 1, tm == 1, di == 1, cg == 0], float)
prior = np.array([1, S[A['s06']], -1, S[A11['s06']], 1, -1, -1, -1, -1, 1], float)
D, y = [], []
for p in key['pairs']:
    yy = {'l': 1, 'r': 0, 't': .5}.get(A.get(p['id']))
    if yy is None: continue
    D.append(x(p['A']) - x(p['B'])); y.append(yy)
D, y = np.array(D), np.array(y)
w = prior * .5
for _ in range(4000):
    pr = 1 / (1 + np.exp(-(D @ w))); w -= .05 * (D.T @ (pr - y) + 0.5 * (w - prior))
acc = np.mean(((D @ w) > 0) == (y > .5))
DIRECT = {'refugees': 's01', 'union': 's02', 'badge_kiss_exit': 's03', 'contract_media': 's04', 'honest': 's05',
          'fan_owned_club': 's08', 'outside_interests': 's09', 'ref_disputes': 's11', 'youth_mentor': 's12'}
out = {f: round(float(v), 2) for f, v in zip(F, w)}
out.update({k: float(S[A[q]]) for k, q in DIRECT.items()})
json.dump(dict(w=out, acc=round(float(acc), 3), n=len(y)), open(here / 'fit.json', 'w'), indent=1)
for f, v in sorted(out.items(), key=lambda t: -abs(t[1])): print(f'{f:18s} {v:+.2f}{"  (pairs)" if f in F else "  (stated)"}')
print('pairs agree', acc, 'of', len(y))
