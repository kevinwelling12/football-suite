"""Association: linked clubs pull each other's Affinity part of the way together (two-way).

python3 scripts/affinity/association.py   # preview the pulls from scripts/affinity/links.json

Links (scripts/affinity/links.json, reviewed by Kevin; research in research/assoc, brief ASSOC_BRIEF.md):
- strong 15%: one supporter base and identity (Portland Timbers / Thorns).
- medium 8%: formal fan friendship or shared ritual (You'll Never Walk Alone).
- light 4%: looser ties.
Each club moves that share of the gap toward its partner: pull = w * (partner - club), summed over its links.
A club's link weights add up to at most 15% (more links are scaled down, so they average instead of stacking),
and the total is capped at +/-5.
Direction (Kevin, 2026-09-28): a club always gains from a partner rated above it, but only loses to a partner
rated below 50 (a club he dislikes). So Liverpool isn't dragged down by Mainz or Gladbach, while a friendship
with Lazio or PSG still costs. It runs once, on the Affinity before any pull, so links don't feed back. A tie between two
clubs that both carry a rival penalty is skipped (the rival penalty already covers them).
Ownership ties are not links: multi-club networks have their own penalty.
"""
import json, pathlib

root = pathlib.Path(__file__).resolve().parents[2]
LINKS = root / 'scripts' / 'affinity' / 'links.json'
W = {'strong': 0.15, 'medium': 0.08, 'light': 0.04}
CAP = 5.0
MAX_W = 0.15
DISLIKE = 50


def load():
    return json.loads(LINKS.read_text()) if LINKS.exists() else []


def pulls(score, rivals, links=None):
    """score: name -> Affinity before association; rivals: names with a rival penalty.
    -> name -> (total pull, [(partner, pull), ...])"""
    out = {}
    for l in (links if links is not None else load()):
        a, b, w = l['a'], l['b'], W[l['strength']]
        if a not in score or b not in score or (a in rivals and b in rivals):
            continue
        for x, y in ((a, b), (b, a)):
            out.setdefault(x, []).append((y, w))
    res = {}
    for n, ps in out.items():
        f = min(1.0, MAX_W / sum(w for _, w in ps))
        ps = [(y, f * w * (score[y] - score[n])) for y, w in ps if score[y] > score[n] or score[y] < DISLIKE]
        ps = [(y, p) for y, p in ps if round(p, 1)]
        if not ps:
            continue
        tot = sum(p for _, p in ps)
        res[n] = (round(max(-CAP, min(CAP, tot)), 1), [(y, round(p, 1)) for y, p in ps])
    return res


if __name__ == '__main__':
    D = json.loads((root / 'data' / 'suite_data.json').read_text())
    score, rivals = {}, set()
    for k, c in D.items():
        for t in c['teams']:
            h = t.get('hai') or {}
            base = t['base'] - h.get('assoc', 0)
            score.setdefault(t['name'], base + t['bonus'])
            if 'Rival' in h.get('note', ''): rivals.add(t['name'])
    for n, (tot, ps) in sorted(pulls(score, rivals).items(), key=lambda x: -abs(x[1][0])):
        print(f'{tot:+5.1f}  {n:30} {score[n]:5.1f}  ' + ', '.join(f'{y} {p:+.1f}' for y, p in ps))
