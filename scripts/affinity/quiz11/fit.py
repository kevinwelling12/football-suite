"""Fit Kevin's values weights from round 11 (mystery pairs + direct questions).
Features (good side = +1): speaks on causes, rainbow armband, refused Pride shirt, left campaign, right campaign, funds
schools, plays fair, private life, criticises bosses, betting app. Logit on the 24 pairs, ridge-pulled toward the direct
answers (++ 2, + 1, 0, - -1, -- -2), so a trait the pairs barely test still gets his stated view.
Usage: python3 scripts/affinity/quiz11/fit.py"""
import json, pathlib, numpy as np
here = pathlib.Path(__file__).resolve().parent
A = json.load(open(here / 'raw' / 'responses' / 'kevin.json')); A = A.get('data', A)['answers']
key = json.load(open(here / 'key.json'))
F = ['causes', 'armband', 'refused_pride', 'left', 'right', 'gives', 'fair', 'private', 'speaks_up', 'betting']
def x(lv):  # levels -> features
    c, pr, pa, g, sp, li, po, ad = lv
    return np.array([c == 0, pr == 0, pr == 2, pa == 0, pa == 2, g == 0, sp == 0, li == 0, po == 0, ad == 1], float)
S = {'++': 2, '+': 1, '0': 0, '-': -1, '--': -2}
prior = np.array([S[A['s01']], S[A['s02']], -S[A['s02']] / 2, S[A['s03']], S[A['s04']], S[A['s10']], -S[A['s11']],
                  -S[A['s09']], S[A['s07']], S[A['s08']]], float)
D, y = [], []
for p in key['pairs']:
    v = A.get(p['id']); yy = {'l': 1, 'r': 0, 't': .5}.get(v)
    if yy is None: continue
    D.append(x(p['A']) - x(p['B'])); y.append(yy)
D, y = np.array(D), np.array(y)
w = prior.copy() * .5
for _ in range(4000):
    z = D @ w; pr = 1 / (1 + np.exp(-z))
    g = D.T @ (pr - y) + 0.5 * (w - prior)
    w -= .05 * g
acc = np.mean(((D @ w) > 0) == (y > .5))
out = {f: round(float(v), 2) for f, v in zip(F, w)}
json.dump(dict(w=out, prior=dict(zip(F, prior.tolist())), acc=round(float(acc), 3), n=len(y)), open(here / 'fit.json', 'w'), indent=1)
for f, v, p0 in sorted(zip(F, w, prior), key=lambda t: -abs(t[1])): print(f'{f:14s} {v:+.2f}  (stated {p0:+.0f})')
print('pairs agree', acc, 'of', len(y))
