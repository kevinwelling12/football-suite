# Running the Affinity research (re-rate, 2026)

Status: quiz done (docs/supporter-profile.md), brief written (BRIEF.md), 11 batch lists committed
(b01 ... b11, 308 unique clubs and nations). The first run stopped because the session's web-search
cap (200) ran out and the network policy blocked direct page fetches. Only a partial, low-confidence
out/b10-nations-a.json exists; redo it (its RSF 2026 ranks can be reused as a starting point).

## Environment needed
- Web-search cap raised (env var CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION, e.g. 2000).
- Network access allowing at least: wikipedia.org, rsf.org, freedomhouse.org, uefa.com, transfermarkt.com.
- Check both before launching: one WebSearch and one WebFetch of https://en.wikipedia.org/wiki/Barnsley_F.C.

## Run
1. Launch one background research agent per batch (general-purpose). Each agent: read BRIEF.md,
   docs/supporter-profile.md and docs/affinity.md; research every club in its batch file with
   WebSearch/WebFetch (facts as of the current month); score C/V/H/O/S 0-10 and adjustments per the
   brief; write scripts/affinity/research/out/<batch>.json; no other edits, no git.
   Budget about 4-5 searches per club (roughly 1,300-1,500 in total). Stagger launches if the cap is tight.
2. When all 11 are in: validate every file (all names present, scores 0-10, sources >= 2, adjustments typed).
3. Calibrate across batches: compare score distributions per factor by batch, check the anchors
   (Dortmund / Union Berlin / Timbers Culture 10, Union Berlin / Athletic Club Ownership 10, Lazio racism -30,
   MK Dons franchise -15, Liverpool / Real Madrid / Athletic Club History 10), fix outlier batches.
4. Show Kevin: flagged calls, the biggest rating changes, and final weights (proposal: Culture 26,
   Values 28, History 16, Ownership 12, Style 8 of 90).
5. After Kevin approves: write the new factors into scripts/affinity/scores.py and
   scripts/importers/build_usl.py, set the new weights in rescore.py (and the USL builder), drop the
   regional heritage bonus for clubs (keep Sacramento Republic +4 and the national-team bonus), rescore,
   rebuild, check the app, commit.
