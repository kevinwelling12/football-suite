# Football Tracker Suite

A single-page web app that tracks 13 competitions for one supporter (Kevin): live tables, a Dixon-Coles
prediction model with 1,000-season simulations, pick 'em, match importance, playoff/knockout brackets,
and a personal **Affinity** score for every club that drives "Affinity picks".

Competitions: Premier League, Champions League, Carabao Cup, MLS, USL Championship, Bundesliga, NWSL,
LaLiga, Serie A, Ligue 1, Championship, Nations League (A–D, 54 nations).

## Quick start
    python3 scripts/build.py            # -> dist/web/index.html (GitHub Pages; Firebase sync if configured)
    python3 scripts/build.py --claude   # -> dist/football_suite.html (claude.ai artifact version)
    open dist/web/index.html            # works from file:// ; state falls back to localStorage

Cloud sync + hosting setup: docs/firebase-setup.md

Pure vanilla JS/CSS/HTML: no bundler, no npm dependencies. Python 3 only for build/data scripts
(`pdfplumber` for the FBref PDF importers).

## Layout
    src/index.template.html   page shell (placeholders: /*__CSS__*/ /*__CONFIG__*/ /*__MODEL__*/ /*__APP__*/)
    src/styles.css            all styles; the "broadcast" (Apple TV-style) theme is the :root.bc block
    src/config.js             per-competition config: zones, statuses, race lines, brand colours, knockout kind
    src/model.js              the engine (MODEL.run for leagues, MODEL.runCup, playoffs/knockouts)
    src/app.js                UI, state, persistence, views, events (/*__DATA__*/ is replaced by data JSON)
    data/suite_data.json      all competition data (teams, fixtures, results, kickoffs, TV, Affinity)
    dist/web/index.html       built web app;  dist/football_suite.html = claude.ai build (not committed)
    firestore.rules           Firestore security rules;  .github/workflows/pages.yml = deploy
    user-data/                export of Kevin's saved state (entered results, follows, statuses...) - see docs/state.md
    scripts/build.py          build
    scripts/affinity/         Affinity rubric scores + rescore script
    scripts/sync/             FBref sync: browser pack snippet + apply script
    scripts/importers/        one-off importers used to build the data (kept for reference/reuse)
    docs/                     architecture, data model, Affinity rules, sync procedure, backlog

Start with CLAUDE.md.
