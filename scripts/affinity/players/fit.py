"""Fit the player Affinity weights to Kevin's mystery-player choices (quiz rounds 8 and 9). No budget, no names.

Round 8 showed name recognition steering the real-player head-to-heads (familiar names won; no single factor explained
more than 55% of those picks) while the anonymous profiles matched the factors (80%). So the weights come from the
anonymous profiles only; the real-player head-to-heads and the round-7 gut ratings are reported as checks, not fitted.

Score S = 10 * sum(w_k * F_k) / sum(w) + c * connection + p * penalty   (factors F_k 0-10, w on the simplex)
P(a over b) = sigmoid(beta * (S_a - S_b)); a "can't split them" answer counts half to each side. Profile values come from
each round's key.json (round 8 had no baggage trait, so its penalty is 0). A ridge pull toward equal weights keeps the fit
stable. Leave-one-out accuracy is reported.

Usage: python3 scripts/affinity/players/fit.py
"""
import json, pathlib, sys, numpy as np
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here)); import model as M
K = ['CH', 'WK', 'LO', 'AB', 'ST', 'LE']
facts, scores = M.load()
def answers(r):
    A = json.load(open(here.parent / r / 'raw' / 'responses' / 'kevin.json')); return A.get('data', A)['answers']
Y = {'l': 1.0, 'r': 0.0, 't': 0.5}

def profiles(r):
    key = json.load(open(here.parent / r / 'key.json')); A = answers(r); out = []
    def prof(lv):
        v = {a[0]: a[2][x][1] for a, x in zip(key['att'], lv)}
        return np.array([v[k] for k in K] + [v['CO'], v.get('PE', 0.0)], float)
    for i, (la, lb) in enumerate(key['conj']):
        y = Y.get(A.get(f'c{i+1:02d}'))
        if y is not None: out.append((prof(la), prof(lb), y, f'{r} c{i+1:02d}'))
    return out
def feats(n): return np.array([scores[n][k] for k in K] + [M.connection(facts[n]), M.penalties(facts[n])], float)
pairs = profiles('quiz8') + profiles('quiz9')
k8, A8 = json.load(open(here.parent / 'quiz8' / 'key.json')), answers('quiz8')
named = [(feats(a), feats(b), Y[A8[f'h{i+1:02d}']], f'{a} v {b}') for i, (a, b) in enumerate(k8['pairs']) if A8.get(f'h{i+1:02d}') in Y]
gut = [(feats(n), M.GUT[n]) for n in M.GUT if n in scores]

def unpack(t):
    w = np.exp(t[:6]); w /= w.sum(); return w, np.exp(t[6]), np.exp(t[7]), np.exp(t[8])
def score(X, w, c, p): return 10 * X[..., :6] @ w + c * X[..., 6] + p * X[..., 7]
def stack(P): return np.array([a for a, *_ in P]), np.array([b for _, b, *_ in P]), np.array([y for _, _, y, _ in P])
def loss(t, S, lam):
    w, c, p, beta = unpack(t); Xa, Xb, y = S
    z = beta * (score(Xa, w, c, p) - score(Xb, w, c, p))
    return (y * np.logaddexp(0, -z) + (1 - y) * np.logaddexp(0, z)).sum() + lam * ((t[:6] - t[:6].mean()) ** 2).sum()
def fit(P, lam=0.5, iters=3000):
    S = stack(P); t = np.zeros(9); t[8] = np.log(0.2); m = np.zeros(9); v = np.zeros(9)
    for i in range(1, iters + 1):  # Adam with numerical gradients (9 parameters)
        g = np.array([(loss(t + e, S, lam) - loss(t - e, S, lam)) / 2e-4 for e in np.eye(9) * 1e-4])
        m = .9 * m + .1 * g; v = .999 * v + .001 * g * g; t -= .03 * (m / (1 - .9 ** i)) / (np.sqrt(v / (1 - .999 ** i)) + 1e-8)
    return t
def acc(P, w, c, p):  # toss-ups left out of accuracy
    h = [(score(a, w, c, p) > score(b, w, c, p)) == (y > .5) for a, b, y, _ in P if y != .5]; return sum(h), len(h)

if __name__ == '__main__':
    w, c, p, beta = unpack(fit(pairs))
    W = {k: round(float(x) * 100, 1) for k, x in zip(K, w)}
    print('weights', W, 'connection x%.2f' % c, 'penalty x%.2f' % p)
    a = acc(pairs, w, c, p); n = acc(named, w, c, p)
    r = np.corrcoef([score(x, w, c, p) for x, _ in gut], [g for _, g in gut])[0, 1]
    print('profiles in-sample %d of %d; named head-to-heads %d of %d; gut r %.2f' % (*a, *n, r))
    hits = tot = 0
    for j in range(len(pairs)):
        if pairs[j][2] == .5: continue
        wj, cj, pj, _ = unpack(fit(pairs[:j] + pairs[j + 1:], iters=1500)); xa, xb, y, _ = pairs[j]
        hits += (score(xa, wj, cj, pj) > score(xb, wj, cj, pj)) == (y > .5); tot += 1
    print('leave-one-out profiles: %d of %d (%.0f%%)' % (hits, tot, hits / tot * 100))
    json.dump(dict(W=W, conn=round(float(c), 2), pen=round(float(p), 2), source='mystery profiles, quiz rounds 8-9',
                   choices=len(pairs), acc=round(a[0] / a[1], 3), loo=round(hits / tot, 3), named_acc=round(n[0] / n[1], 3),
                   gut_r=round(float(r), 3)), open(here / 'fit.json', 'w'), indent=1)
