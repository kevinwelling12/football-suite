# Top-3 audit (October 2026)

Kevin (Sacramento) asked to audit the top 3 clubs or nations in each competition of his tracker: "make sure we aren't
missing anything and to solidify the ratings". You audit a batch of them. Today is 12 October 2026.

## What you are checking
Each entity's current numbers are in scripts/affinity/research/audit_top3/current.json: factors C (Culture), V (Values),
H (History), O (Ownership), S (Team, before squad bumps), P (record 0-10, computed elsewhere: do not audit), hard lines
(already scaled by 1.98: "hard"), connection items ("conn"), roots. The raw inputs live in scripts/affinity/scores.py
(tuple: C, V, H, O, S, adjustment points before scaling, note) and scripts/importers/build_usl.py for USL clubs.

For every entity in your batch:
1. Re-research it independently (web search, as of October 2026; about 3-6 searches each). Look hardest for what could be
   MISSING or OUT OF DATE:
   - hard-line items: racism or discrimination by the club or its fans (sanctions, fines, closures), fan violence,
     state ownership or state-owned sponsors, private equity, leveraged buyouts, multi-club ownership, Super League,
     betting/casino or arms sponsors, owner scandals, relocation;
   - 2025-26 and summer 2026 changes: owner, sponsors (shirt, sleeve, stadium, betting partners), stadium plans, ticket
     pricing rows, coach churn, fan protests, women's team status;
   - positives that may be under-counted: community work, fan ownership or voice, academy, causes.
2. Judge each factor against the rubric in scripts/affinity/research/BRIEF.md (C, V, H, O, S anchors and the
   adjustments table; "Round 5 sub-weights"; women's clubs judged in the women's game; nations: V = federation and fan
   conduct, plus the government's record as a hard line) and the one-decimal scale in
   scripts/affinity/research/DECIMAL_BRIEF.md. Calibrate against other clubs in scripts/affinity/research/decimal_bands.json.
3. Read docs/preferences.md for Kevin's own rules before proposing anything (search it for the entity's name too).
   Kevin settled some orderings himself in blind deciders: Portland Timbers over Seattle (Cascadia), Dortmund over Union
   Berlin (German), Atalanta > Napoli > Fiorentina on his weights before ultras hard lines (Italian). Do not propose
   factor changes whose only effect is to reverse a decider; if new facts genuinely bear on one, flag it instead.
4. Reuse existing research where it is sound (scripts/affinity/research/out/*.json, final/, final3/, out7/,
   research/cascadia, berlin_dortmund, italian, leeds_values, heritage/). Don't redo what is already sourced and current.

## Output
scripts/affinity/research/audit_top3/<batch>.json: an array, one object per entity in batch order:
{"name": "exact name",
 "verdict": "confirmed" | "adjust",
 "changes": [{"field": "V" | "C" | "H" | "O" | "S" | "hard" | "conn", "from": 8.2, "to": 7.9,
              "why": "one sentence, neutral", "sources": ["url"]}],
 "missing_checked": ["short list of what you checked and found nothing on, e.g. 'no FA/UEFA discrimination sanctions 2021-26'"],
 "notes": "anything Kevin should decide (e.g. a fact that bears on a decider)",
 "confidence": "high|medium|low"}
For "hard" give the label and points BEFORE the 1.98 scale, like scores.py ("Racism -2"). For "conn" describe the item.
Propose a change only when the evidence clearly supports it; moves of 0.1-0.4 are fine when justified. "confirmed" with
an empty changes list is a good outcome. Neutral wording, never invent sources, mark anything unverified.
Do not edit any other file, do not commit, do not run git.
