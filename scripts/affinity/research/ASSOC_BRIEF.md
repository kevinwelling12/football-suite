# Association research brief (September 2026)

Kevin wants Affinity to reflect ties between clubs, the mirror of the multi-club ownership demerit. Two linked
clubs pull each other's Affinity part of the way together (scored later by scripts/affinity/association.py).
You find and document the ties. You do not score anything.

## Scope
Only ties between two clubs that are BOTH in scripts/affinity/research/assoc/clubs.txt (exact names from that
file). Your batch lists the clubs you are responsible for; report every tie where at least one side is in your
batch (the other side can be any club in clubs.txt). No national teams.

## What counts (and its strength)
- strong: one supporter base and identity shared by two sides. Men's and women's teams of the same club or
  the same supporters' group (Portland Timbers / Thorns: Timbers Army and Rose City Riveters, same stadium).
  A women's team that is a separate company but shares the name, stadium and supporters' group counts.
- medium: a documented, long-standing FORMAL fan friendship (ultras twinning, supporters' groups that visit
  each other and display each other's banners), or a shared defining ritual with documented mutual
  recognition (You'll Never Walk Alone: Liverpool, Borussia Dortmund, Feyenoord, Mainz 05 ...).
  Friendships between far-right or violent groups count too: they are the reason this runs both ways.
- light: real but looser: one-off or fading friendships, shared-heritage ties (same founders, kit borrowed
  from the other club), partnerships between supporters' trusts.

## What does NOT count
- Ownership links (multi-club groups, shared investors, loan partnerships): already handled elsewhere.
- Rivalries or derbies. Player transfers. Commercial or academy partnerships. Shared city alone.
- Anything you cannot source. Wikipedia "friendships" sections, supporters' group sites and reputable press
  are fine; fan forums alone are not.

## Output
Write ONE JSON file to scripts/affinity/research/assoc/<batch>.json: an array of ties
```json
{"a": "Portland Timbers", "b": "Portland Thorns", "strength": "strong",
 "type": "shared supporters | fan friendship | ritual | heritage | other",
 "evidence": "one or two neutral sentences", "sources": ["https://..."], "confidence": "high | medium | low"}
```
Put each tie in once. It is fine to return few ties: most clubs have none that meet the bar.
Do not edit any other file, do not commit, do not run git.
