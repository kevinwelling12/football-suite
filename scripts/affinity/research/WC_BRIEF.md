# 2026 World Cup nations brief (September 2026)

Kevin wants every nation that played at the 2026 FIFA World Cup (48 teams, USA/Canada/Mexico, June-July 2026)
on his Affinity page. The 54 UEFA nations are already rated (scripts/affinity/research/wc/uefa_reference.txt:
factor scores, adjustments, resulting Affinity). You rate the non-UEFA ones on exactly the same scale.

Read first: scripts/affinity/research/BRIEF.md (sections "National teams" and the factor anchors), docs/affinity.md,
docs/supporter-profile.md. Calibrate against uefa_reference.txt: a nation you rate should sit where it belongs
next to comparable European nations (e.g. Brazil's History next to Germany/Italy's 10; a small federation next
to Iceland or Wales).

## Factors (integers 0-10), as for UEFA nations
- C: fan culture of the national team's supporters (atmosphere, away following, loyalty).
- V: federation and fan conduct (discrimination sanctions, violence, abuse scandals), plus regional identity etc.
- H: significance of the national team (World Cups, famous moments, influence).
- O: federation governance (corruption, transparency, independence from government).
- T (stored as S): the team, last 3 years: how they play (intensity), the squad's bond with fans, stable squad,
  current icons and a defining long-serving coach.
Adjustments (points on the 0-100 Affinity), with evidence:
- government: the country's regime record, -5 to -25 (Freedom House status/score and RSF press-freedom rank;
  compare with the UEFA nations: Hungary -10, Georgia -15, Turkey -20, Israel -20, Belarus/Azerbaijan -25).
  Free countries with a good record: none.
- racism / violence: FIFA or confederation discrimination sanctions, fan violence (up to -15 for nations).
- other: explain.

## Output
First confirm the full list of 48 qualified teams (including intercontinental and UEFA play-off winners) from
Wikipedia's "2026 FIFA World Cup" page, and write it to scripts/affinity/research/wc/teams48.json (only the agent
told to do so) as [{"name", "confed", "result": "group stage | round of 32 | ... | champion"}].
Then write scripts/affinity/research/wc/<batch>.json, one object per nation in your batch:
{"name": "common English name (e.g. 'United States', 'South Korea', 'Ivory Coast', 'DR Congo')", "confed": "CONMEBOL",
 "abbr": "FIFA trigram", "color": "#hex primary shirt colour that reads on black",
 "C": {"score": 8, "evidence": "..."}, "V": {...}, "H": {...}, "O": {...}, "S": {...},
 "adjustments": [{"type": "government", "points": -10, "evidence": "..."}],
 "wc2026": "how far they got", "confidence": "high | medium | low", "sources": ["https://..."]}
Neutral wording, facts as of September 2026. Do not edit any other file, do not commit, do not run git.
