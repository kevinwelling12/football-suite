# Data sources & sync

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
Kevin's routine: he says "sync" and a full pass runs across all competitions.
