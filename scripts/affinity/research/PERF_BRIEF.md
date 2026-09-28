# Track record research brief (September 2026)

Kevin wants Affinity to credit clubs with consistent success over recent years: staying in or near the
top of their tier, season after season. A trophy from 1965 counts for nothing here (History already covers
heritage). You collect facts only. The score is computed later by scripts/affinity/performance.py.

## What to collect, per club
The last 10 COMPLETED league seasons, most recent first:
- European and Turkish leagues: 2025-26 back to 2016-17.
- Calendar-year leagues (MLS, NWSL, USL, Norway, Sweden, ...): 2025 back to 2016.
  The 2026 MLS/NWSL/USL season is still in progress: do not include it.

For each season: the national tier the club played in (1 = top flight; England: Premier League 1,
Championship 2, League One 3, League Two 4, National League 5; USA: MLS/NWSL 1, USL Championship 2,
USL League One 3; NASL counts as tier 2), the final regular-season league position, and the number of
teams in that table.
- MLS: use the overall (Supporters' Shield) table if you can find it; otherwise the conference table
  and say so with "table": "conf".
- USL Championship: conference table is fine ("table": "conf").
- Split-phase leagues (Belgium, Scotland, Austria, Azerbaijan, ...): final position after the split.
- A season the club did not exist, was dormant or played below tier 6: "tier": null.

Trophies won in those same seasons (only these types):
- "league": national league title (a playoff final that decides the champion counts, e.g. MLS Cup, NWSL
  Championship, USL Championship final). Winning a lower tier's title also counts (e.g. Championship winners).
- "cup": the main national cup (FA Cup, DFB-Pokal, Copa del Rey, Coppa Italia, Coupe de France,
  US Open Cup, KNVB Cup, Turkish Cup, Taça de Portugal, ...).
- "league_cup": secondary national cups (EFL Cup, Coupe de la Ligue, NWSL Challenge Cup, Leagues Cup).
  Skip super cups, community shields and the EFL Trophy.
- "continental": UEFA Champions League, CONCACAF Champions Cup/League.
- "continental2": UEFA Europa League, UEFA Conference League.

Also: "current_tier" (the tier the club plays in for 2026-27, or the 2026 season for calendar leagues).

## Method
Recall first, then verify against Wikipedia: the club's "List of <club> seasons" page or the season
tables on the club article (e.g. `curl -sL https://en.wikipedia.org/wiki/List_of_Barnsley_F.C._seasons`,
then grep/python to pull the rows). Wikipedia rate-limits: space requests out, retry with backoff on 429,
prefer the normal article URLs over the API. WebSearch/WebFetch are fine too. Aim for accuracy on tier and
position; a position off by one matters little, a wrong tier matters a lot.

## Output
Write ONE JSON file: scripts/affinity/research/perf/<batch>.json, an array in the batch order:
```json
{"name": "exact name from the batch file",
 "seasons": [{"s": "2025-26", "tier": 1, "pos": 3, "of": 20}, {"s": "2024-25", "tier": 2, "pos": 1, "of": 24}, ...],
 "trophies": [{"s": "2024-25", "type": "league", "what": "EFL Championship"}],
 "current_tier": 1,
 "confidence": "high | medium | low",
 "notes": "anything odd (points deductions, expulsions, re-foundings, conference tables)"}
```
Exactly 10 season entries per club (use "tier": null for seasons that did not exist).
Skip national teams. Do not edit any other file, do not commit, do not run git.
