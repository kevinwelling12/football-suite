# Tenths re-rate (September 2026)

Kevin wants Culture (C), Values (V), History (H) and Ownership (O) to one decimal place. Team (S) already has decimals
(squad interplay) and is out of scope. This is a REFINEMENT, not a re-rate: every current whole-number score stays
where it is to within 0.4.

## The rule
For each club or nation in your batch and each of C, V, H, O:
- current score k (from scripts/affinity/scores.py, USL clubs from the A dict in scripts/importers/build_usl.py)
- new score in [k - 0.4, k + 0.4], one decimal, kept inside 0.0-10.0 (a 10 can only go down, a 0 only up)
- k.0 means "a typical case of k". Move up when the case is stronger than a typical k (closer to k+1), down when
  weaker (closer to k-1). About ±0.1-0.2 for a modest difference, ±0.3-0.4 when it nearly deserved the next score.
- Compare against the other entries with the same score across the WHOLE tracker, not just your batch:
  research/decimal_bands.json lists every club and nation by factor and current score. The goal is that two 7s in
  different batches are ordered sensibly.
- Use the spread. Not everything is .0; but don't invent differences either. A factor with nothing to separate it
  stays at k.0.

## What each factor means (docs/affinity.md has the full rubric and Kevin's rules; read it first)
- C Culture: atmosphere, attendance vs capacity, supporter groups, rituals, travelling support, fan power.
- V Values: community work, inclusion, conduct, sponsors (sportsbooks/casinos count against), women's team, pricing.
- H History: trophies, eras, identity, age, iconic moments (a tier-1 global reference; lower tiers regional).
- O Ownership: fan/member ownership, stability, owner conduct and competence, private equity/multi-club/state
  (those also carry separate adjustments; don't double count what an adjustment already covers).
Kevin's rules that were rounded to a whole point before can now show their size: "counts half", "counts partly",
"counts a little" (docs/affinity.md, Cascadia decider and later sections) are natural reasons for a few tenths.

## Evidence
Earlier research: research/out/<batch>.json (C, V, H, O evidence with sources; nations b10/b11 there too),
research/wc/americas.json and research/wc/asia_africa.json for the 32 World Cup nations outside the Nations League,
notes in scores.py. Reuse it. Search only where a tenth hinges on a fact you cannot settle from it: at most about one
search per club.

## Output
scripts/affinity/research/out7/<batch>.json, one entry per club/nation in batch order:
{"name": "exact name", "C": 7.3, "V": 5.8, "H": 8.0, "O": 4.6,
 "why": "C +0.3 sells out every week, loudest end in the league; V -0.2 betting sleeve; O -0.4 owner sale talks"}
"why" lists only the factors you moved off .0, one short clause each. Neutral wording.
Do not edit any other file, do not commit, do not run git.
