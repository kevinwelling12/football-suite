# Rules re-rate (September 2026)

Kevin settled four rules in the Cascadia decider (docs/affinity.md, "Cascadia decider"). Check every club in your
batch against them and propose small, evidence-backed changes. Most clubs will have NO change: only report a hit
when a rule clearly applies. Current scores are in scripts/affinity/scores.py (USL clubs: scripts/importers/build_usl.py),
as (Culture, Values, History, Ownership, Team, adjustment, note). Earlier evidence: research/out/<batch>.json
(Culture, Values, Ownership, adjustments) and research/out3/<batch>.json (Team, coaches, player conduct). Reuse it;
search to check current facts (September 2026). About 1-2 searches per club.

Rules (a rule hit changes one factor by exactly +1 or -1; never more; factors stay 0-10)
R1 owner-past: the CURRENT owner has past misconduct that lowers Ownership or Values now (check the evidence), the
   owner faced real consequences (sanction, stepping down, forced sale, fine) and nothing similar in the last 3 years
   -> +1 to that factor (it now counts half). Ongoing or repeated misconduct -> no change. A previous owner's conduct
   is already dropped by an earlier rule: no change.
R2 plans: announced or likely-and-reported plans count now.
   - Stadium: a planned move fans largely oppose, or to a worse/remote/shared ground -> Culture -1. A planned move
     fans welcome to a better soccer ground in the same city -> Culture +1 (only if not yet counted).
   - Ownership: a pending or reported sale/investment to private equity, a state fund, a multi-club group or an owner
     fans oppose -> Ownership -1. A pending sale to fans/members or a respected local owner -> Ownership +1.
   Rumours alone do not count: needs an announcement, a signed deal, an official process (bank hired) or credible
   reporting of advanced talks.
R3 coach: a head coach in charge for 5 or more full seasons who defines the club -> Team +1, unless the Team evidence
   in out3 already credits him ("defining coach" / "long-serving coach" named). Three or more permanent head coaches in
   the last 3 seasons (churn) -> Team -1, unless out3 already counted the churn. (Kevin: a long-serving coach matters
   more than the style of play.)
R4 casino: a current shirt/sleeve/stadium/pitch sponsor that is a casino brand with a sportsbook inside, or a betting
   brand under a casino name, not already counted in Values -> Values -1.

Output: scripts/affinity/research/out6/<batch>.json, an array with ONE entry per club in batch order:
{"name": "exact name", "hits": [{"rule": "R3", "factor": "S", "delta": 1, "evidence": "one or two sentences", "source": "https://..."}]}
Factor letters: C Culture, V Values, H History, O Ownership, S Team. Empty "hits" for clubs with no change.
Neutral wording. Do not edit any other file, do not commit, do not run git.
