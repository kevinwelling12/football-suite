# Big-4 ties research brief (September 2026)

Kevin (Sacramento) follows the Sacramento Kings (NBA), San Francisco Giants (MLB), San Francisco 49ers (NFL) and
San Jose Sharks (NHL). Affinity will credit football clubs tied to those teams and mark down clubs tied to their
rivals. You find and document ties between the football clubs in your batch and ANY NBA, MLB, NFL or NHL
franchise (we filter to Kevin's teams and their rivals later, so report them all). You do not score anything.

## What counts
- ownership: the franchise, its owner(s) or its holding company own or control the football club, or hold a
  significant stake (e.g. 49ers Enterprises in Leeds United; Kroenke Sports: LA Rams and Arsenal).
- minority: a smaller stake or a place in the ownership group held by a franchise's owner, part-owner or
  executive (e.g. an MLS club whose investor group includes a co-owner of an MLB team).
- operations: the franchise's company runs the club or its stadium, or they share an arena company (e.g. AEG).
- partnership: a formal, current club-to-club partnership (not a one-off friendly or a shirt sponsor).
- former: a tie that ended (say when); former owners count only if the tie is to the CURRENT club owner
  (e.g. a club's current owner formerly owned an MLB team).
Players, celebrities who are only fans, and athletes who are investors because of their playing career count
only if they are ALSO an owner/part-owner of a big-4 franchise (e.g. an NFL minority owner who invests in a
football club counts).

## Output
Write ONE JSON file to scripts/affinity/research/big4/<batch>.json: an array of ties
```json
{"club": "exact name from the batch", "franchise": "Los Angeles Rams", "league": "NFL",
 "kind": "ownership | minority | operations | partnership | former",
 "via": "Kroenke Sports & Entertainment (Stan Kroenke)", "evidence": "one or two neutral sentences, current as of Sept 2026",
 "sources": ["https://..."], "confidence": "high | medium | low"}
```
Most clubs have no tie: list only the ones that have. Verify ownership as of September 2026 (it changes).
Do not edit any other file, do not commit, do not run git.
