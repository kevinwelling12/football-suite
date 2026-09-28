# Data sources & sync

Automatic (default): ESPN's public scoreboard API (site.api.espn.com, free, no key, unofficial).
.github/workflows/espn-sync.yml runs scripts/sync/espn.js twice a day (10:17 and 23:17 UTC) and on demand
(Actions tab > Sync results from ESPN > Run workflow; "back" = days of results to re-check).
- Fills results for fixtures with no base result, with the pick 'em score and Affinity pick the model
  gave before the match (default settings) in slots 6-8. Sets confirmed kickoff times and moves dates
  (local date: US leagues Eastern, the rest UK) for unplayed fixtures. Stamps `synced` on the competition.
- Never replaces a base result. Disagreements, extra time, penalties outside the cup, postponements,
  unknown team names and API errors go to one open GitHub issue, "ESPN sync needs a look".
- Kevin's own entries override base results in the app as before. If one disagrees with the base
  result, the match card shows "Tracker data x–y · Differs from yours" and Settings > Your data counts them.
- Commits data/suite_data.json to main, then starts pages.yml (bot pushes don't trigger it).
- ESPN names the matcher can't pair go in scripts/sync/espn_aliases.json (ESPN name -> tracker name).
- Local run: `node scripts/sync/espn.js --dry` (options: --comp epl,mls --back N --ahead N --report FILE).
  Behind a proxy add NODE_USE_ENV_PROXY=1 (and NODE_EXTRA_CA_CERTS if needed).
- ESPN answers one day per request (date ranges return 400); the script asks only listed match days.

Manual fallback: FBref.
Primary source: FBref "Scores & Fixtures" pages (results, dates, kickoffs as epoch).
- Leagues/UCL/UNL/EFL Cup pages: /en/comps/{id}/schedule/... ids: EPL 9, Championship 10, Serie A 11,
  LaLiga 12, Ligue 1 13, Bundesliga 20, MLS 22, USL Championship 73, NWSL 182, UCL 8, Nations League 677,
  EFL Cup 690.
Two proven routes:
1. Browser (Claude in Chrome): run scripts/sync/fbref_pack.js on the page, save output to a text file,
   then `python3 scripts/sync/apply_fbref.py <compKey> <file> '<alias JSON>'` (FBref->app team-name
   aliases, e.g. {"Paris SG":"Paris Saint-Germain"}). It reports result mismatches, date moves, time
   changes and newly timed matches, and updates data/suite_data.json (unplayed fixtures only).
   Output of the browser tool truncates around 1.2-1.8 KB, so fetch the packed string in slices.
2. PDF: Kevin saves the FBref page as PDF; parsers in scripts/importers/fbref_pdf_*.py (text rows
   grouped by y-position; team names matched against a known list; parenthetical time = Pacific).
Rules: never overwrite Kevin's entered results; compare them (user-data) and report. Base results are
only replaced if FBref disagrees and Kevin confirms.
Broadcasters (US, 2026-27) are in data (tv field); USL = "ESPN Select (ESPN+)".
Kevin's routine: he says "sync" and a full pass runs across all competitions (now mostly covered by the
ESPN workflow; use FBref to cross-check or when ESPN is down).
