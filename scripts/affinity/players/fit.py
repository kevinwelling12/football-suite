"""Fit the player Affinity weights to Kevin's choices (quiz round 8) and gut ratings (round 7). No budget.

Score S = 10 * sum(w_k * F_k) / sum(w) + c * connection + p * penalty   (factors F_k 0-10, w on the simplex)
- Head-to-heads (round 8, h01-h30): P(a over b) = sigmoid(beta * (S_a - S_b)), using each player's researched factors.
- Mystery pairs (round 8, c01-c20): the same, with the profile's hidden level values (key.json) as factors.
- Gut ratings (round 7, 18 players): S ~ a + b * rating (least squares, standardized).
Ridge pull toward equal weights keeps the fit stable with ~70 data points. Leave-one-out accuracy is reported.

Usage: python3 scripts/affinity/players/fit.py
"""
import json, pathlib, sys, numpy as np
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here)); import model as M
q8 = here.parent / 'quiz8'
K = ['CH', 'WK', 'LO', 'AB', 'ST', 'LE']
facts, scores = M.load()
A = json.load(open(q8 / 'raw' / 'responses' / 'kevin.json')); A = A.get('data', A)['answers']
key = json.load(open(q8 / 'key.json')); Q = {q['id']: q for q in json.load(open(q8 / 'questions.json'))['items']}

def feats(n):  # factors + connection + penalty for a real player
    return np.array([scores[n][k] for k in K] + [M.connection(facts[n]), M.penalties(facts[n])], float)
ATT = key['att']  # [(k, label, [(text, value)])]
def prof(levels):  # mystery profile -> same feature layout (CO is connection; no penalty)
    v = {a[0]: a[2][x][1] for a, x in zip(ATT, levels)}
    return np.array([v[k] for k in K] + [v['CO'], 0.0], float)

pairs = []  # (xa, xb, 1 if a chosen)
for i, (a, b) in enumerate(key['pairs']):
    v = A.get(f'h{i+1:02d}')
    if v in ('l', 'r'): pairs.append((feats(a), feats(b), 1.0 if v == 'l' else 0.0, f'h{i+1:02d} {a} v {b}'))
for i, (la, lb) in enumerate(key['conj']):
    v = A.get(f'c{i+1:02d}')
    if v in ('l', 'r'): pairs.append((prof(la), prof(lb), 1.0 if v == 'l' else 0.0, f'c{i+1:02d}'))
gut = [(feats(n), M.GUT[n]) for n in M.GUT if n in scores]

def score(X, w, c, p): return 10 * X[..., :6] @ w + c * X[..., 6] + p * X[..., 7]
def unpack(t):
    w = np.exp(t[:6]); w /= w.sum(); return w, np.exp(t[6]), np.exp(t[7]), np.exp(t[8])
def loss(t, P, G, lam):
    w, c, p, beta = unpack(t)
    L = 0.0
    for xa, xb, y, _ in P:
        z = beta * (score(xa, w, c, p) - score(xb, w, c, p)); L += np.logaddexp(0, -z) if y else np.logaddexp(0, z)
    if G:
        s = np.array([score(x, w, c, p) for x, _ in G]); g = np.array([r for _, r in G], float)
        s = (s - s.mean()) / (s.std() + 1e-9); g = (g - g.mean()) / g.std()
        L += 0.5 * len(G) * (1 - np.corrcoef(s, g)[0, 1])  # rank agreement with the gut ratings
    return L + lam * ((t[:6] - t[:6].mean()) ** 2).sum()
def fit(P, G, lam=0.5, iters=1500):
    t = np.zeros(9); t[8] = np.log(0.2); m = np.zeros(9); v = np.zeros(9)
    for i in range(1, iters + 1):  # Adam with numerical gradients (9 parameters)
        g = np.array([(loss(t + e, P, G, lam) - loss(t - e, P, G, lam)) / 2e-4 for e in np.eye(9) * 1e-4])
        m = .9 * m + .1 * g; v = .999 * v + .001 * g * g; t -= .05 * (m / (1 - .9 ** i)) / (np.sqrt(v / (1 - .999 ** i)) + 1e-8)
    return t

if __name__ == '__main__':
    t = fit(pairs, gut); w, c, p, beta = unpack(t)
    print('weights', {k: round(float(x) * 100, 1) for k, x in zip(K, w)}, 'connection x%.2f' % c, 'penalty x%.2f' % p)
    acc = np.mean([(score(xa, w, c, p) > score(xb, w, c, p)) == bool(y) for xa, xb, y, _ in pairs])
    s = [score(x, w, c, p) for x, _ in gut]; r = np.corrcoef(s, [g for _, g in gut])[0, 1]
    print('in-sample: choices %.0f%% of %d, gut r %.3f' % (acc * 100, len(pairs), r))
    # leave-one-out over the choices (refit without each one)
    hits = 0
    for j in range(len(pairs)):
        tj = fit(pairs[:j] + pairs[j + 1:], gut, iters=400); wj, cj, pj, _ = unpack(tj)
        xa, xb, y, _ = pairs[j]; hits += (score(xa, wj, cj, pj) > score(xb, wj, cj, pj)) == bool(y)
    print('leave-one-out choices: %d of %d (%.0f%%)' % (hits, len(pairs), hits / len(pairs) * 100))
    json.dump(dict(W={k: round(float(x) * 100, 1) for k, x in zip(K, w)}, conn=round(float(c), 2), pen=round(float(p), 2),
                   choices=len(pairs), acc=round(float(acc), 3), loo=round(hits / len(pairs), 3), gut_r=round(float(r), 3)),
              open(here / 'fit.json', 'w'), indent=1)
