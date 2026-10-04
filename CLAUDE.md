# CLAUDE.md: Football Tracker Suite

Read this first. Then docs/architecture.md, docs/data-model.md, docs/affinity.md as needed.

## What this is
A personal football tracker for Kevin (Sacramento). One self-contained HTML page built from src/ + data/.
Used mostly on iPhone/iPad (Safari), dark mode. It was built in claude.ai chat and published as a
claude.ai artifact; this repo is the transfer to Claude Code.

## Build / run
- `python3 scripts/build.py` -> `dist/web/index.html` (web). `--claude` -> `dist/football_suite.html`. Rebuild after editing src/ or data/.
  dist/ is git-ignored: the Pages workflow builds it on every push to main, so commit only src/, data/ and scripts/.
- App icon: src/icons/icon.svg (football in a ring of the 12 competition colours). PNGs are rendered from it with
  `node scripts/icons/render.js` and committed; build.py copies them next to the page.
- Verify in a headless browser (Playwright was used) at 390px and 1100px widths, dark colour scheme;
  check for page errors and horizontal overflow. Mobile is the primary target.

## Hosting & persistence
- Web target (default build): `dist/web/index.html`, deployed to GitHub Pages by
  .github/workflows/pages.yml on every push to main.
- Cloud sync: Firebase Firestore + Google sign-in (compat SDK from gstatic, version in scripts/build.py).
  Data path `users/{uid}/trackers/{key}`: one doc per competition + `suite`, fields are JSON strings
  (same layout as the old claude.ai artifact db). Rules in firestore.rules. Config in
  src/firebase-config.js (null = no sync). Real-time via onSnapshot; offline via enablePersistence.
- First sign-in with an empty cloud seeds from user-data/*.json (bundled as window.SEED) and uploads.
- `python3 scripts/build.py --claude` builds the claude.ai artifact version (no external scripts;
  uses window.claude.use('db')). Both backends share docFor()/applyDoc() in app.js.
- localStorage (`football-suite-2627`) is always kept as a local cache/fallback.
- One-time account setup steps: docs/firebase-setup.md.

## Working agreements (Kevin's preferences, learned over many sessions)
- Plain, short replies. Show what changed and the concrete effect (numbers, examples). No hype.
- Never overwrite results Kevin entered; when syncing, compare and report disagreements instead.
- If you renumber fixtures (fixture ids = array index in data), migrate saved state by teams+date,
  never by index (a past renumbering corrupted Nations League entries).
- Pick 'em is scored on the 90-minute score only (2 pts result, 3 exact).
- Terminology: "Affinity" (not HAI), "Matches" (not "Games"), "Affinity pick", "Match of the week".
- The visual theme (Apple Sports-inspired: page tinted in the competition's colour, dark translucent panels, club colour discs as crests, big plain numbers) applies to every competition; keep it consistent. One dark stylesheet, src/styles.css.
- Excel trackers are deprecated. Don't recreate them.
- "Ship it" = take it live without asking: commit, push, open the PR and merge it to main (Pages deploys main).

## Where the logic lives
- Affinity rubric & rules: docs/affinity.md and scripts/affinity/scores.py (+ USL in build_usl.py).
  Track record coefficient: scripts/affinity/performance.py. Overall ranking of every club: the Affinity view (view 'rank').
- Model details: docs/architecture.md (Dixon-Coles, draw calibration, importance, favour/Affinity picks).
- Data sources and sync: docs/sync.md (nightly ESPN sync: .github/workflows/espn-sync.yml, scripts/sync/espn.js).
- Open ideas: docs/backlog.md.
