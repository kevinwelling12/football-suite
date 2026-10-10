# Architecture

## Engine (src/model.js)
MODEL.run(comp, results, S, status, live) for league-style competitions:
1. Build fixture objects; apply user results (results[id] overrides base data), status (postponed `p`,
   rescheduled `d`/`t`, awarded `aw`) and live scores.
2. League baseline rates (optionally blended with priors `haPrior`/`scPrior`, weight `baseW`).
3. Attack/defence ratings: 5-iteration EM, exponential recency weights (halfLife days), regression to
   preseason priors with k phantom games (`pa`/`pd` per team; 1.0 when no prior).
4. Head-to-head adjustment (h2hK), Dixon-Coles rho (fit vs prior, weight rhoW).
5. **Draw calibration** (drawAuto): diagonal of every scoreline grid scaled so mean P(draw) over played
   matches = target, target = (n*observed + drawW0*cfg.drawPrior)/(n+drawW0).
5b. **Betting market blend** (mktW, default 0.8; Settings): for fixtures with odds (comp.odds = data odds[fixtureId], DraftKings
   via the ESPN sync), the scoreline grid becomes mktW x market grid + (1 - mktW) x model grid (marketFit: margin removed,
   total from the over/under price, home-away split and draws matched to the market). Probabilities, picks and the season
   simulations all use the blended grid. Backtest (scripts/pickem/blend.js, 750 matches with odds, walk-forward): log loss
   1.052 model only, 1.016 at 0.75, 1.015 market only; pick 'em 1.048 -> 1.084 points a match.
6. Predicted score (draw-zone calibrated) and **pick 'em** pick = argmax of
   peOutcome*P(outcome) + (peExact-peOutcome)*P(exact). Locked at result entry (results[id][2..4]).
7. Table (+ points adjustments S.adj), clinch/elimination statuses (cfg.status), groups/conferences.
8. Monte Carlo: S.sims seasons (1000); live matches sample remaining goals (xG scaled by time left;
   per red card that side's rate x0.67, the opponent's x1.25, up to 3 each; live entry field rc:[home, away]).
   Knockouts/playoffs simulated per season via makeKO(kind): 'ucl', 'unl2' (Nations League A-D with
   promotion/relegation play-offs), 'nwslpo', 'mlspo' (wild card + best-of-3), 'uslpo'.
9. **Importance** per unplayed match: sum over zones of weight*|P(zone|win)-P(zone|loss)| (floor
   impFloor), scaled so the biggest remaining match = 1.00; blended early-season with position leverage.
10. **Affinity pick** (favor()): score(outcome) = Affinity*(1 + beta*stakes); draw = drawW*min(Affinity)*...;
    underdog lean multiplies the less-likely side by (1+underdog). With drawAuto, drawW is set per
    league so the share of draw picks among upcoming matches = draw target.
11. Affinity satisfaction: how closely the (interim) order follows Affinity order, 0-100.

MODEL.runCup: Carabao Cup (single ties, pens; two-legged semis; neutral final with ET), random draws for
undrawn rounds, draw entry supported. MODEL.poResolve/poProbs: bracket resolution for the Playoffs tab.

## App (src/app.js)
- Model runs: full runs (1,000 seasons) go to a Web Worker built from the page's own config.js + model.js
  (script tags #src-config/#src-model), so taps never block. update(k) shows a quick 150-season run at once
  and the full result replaces it (status shows "updating odds…"). No Worker (claude.ai artifact) = runs
  on the page as before. bgRender() redraws for background changes without moving the page or closing an
  open score entry.
- Live clock: live entries are {h, a, ph:'1H'|'HT'|'2H', t, m0}. Match events are one tap on the card
  (Kicked off, Half-time, 2nd half, Full time, +1 goal, red card); the clock runs from the last tap. 45+N/90+N for
  stoppage; missed taps are guessed (~) and "FT?" asks for full time after 90+15. A 30 s timer keeps clocks
  current and re-runs the model every 2 match minutes. Old {h, a, min, ht} entries keep a fixed minute.
- Live view (nav 'Live', view 'live'): every match marked live, plus matches past kickoff (up to 150 min) with no
  score, as compact cards (liveCard: comp + pick 'em outlook, score bug with red cards, odds bar, one-tap
  buttons; ~155px so 4-5 fit on a phone; tap the bug for the full card). Card clicks act on the card's own competition (k from
  data-fx) and `$('#id')` looks inside the clicked card first, because fixture ids repeat across competitions.
- Pull to refresh (#ptr): home-screen web app only (navigator.standalone). Pull down from the top past
  the line to reload; view/tab/round/table mode come back from sessionStorage. Safari keeps its own gesture.
- Sticky bar (#topbar): slides in once the header nav scrolls away; competition (tap = back to top) + sections.
- `state`: view/tab/round per comp, results, status, live, favs (followed clubs, synced across comps by
  name), settings (per comp incl. adj = points adjustments), ko (playoff results), motw (locked Match of the
  week per round), suite (pick 'em scoring, motwW), draws (cup), tmode (table view).
- compute(k) runs the model and attaches kickoffs (data.kick + reschedules); computeAll() is progressive.
- Top nav (renderChrome): region tabs (REGIONS in config.js: England, Europe, USA, UEFA) > that region's
  competition chips (DOT colours, CHIP phone labels) > section tabs. A region tab reopens the last competition
  viewed in it. ORDER follows REGIONS.
- Views: overview (tiles, Your clubs, What's next, biggest per comp, Live now), round/matchweek cards
  (score bug), table (current / as it stands / projected, per-league columns for Nations League),
  races, playoffs bracket, clubs (Affinity breakdown), settings, club sheet, match detail
  ("Why it matters" narrative, stat tiles, scoreline heatmap).
- Match of the week: blend motwW*importance + (1-motwW)*competitiveness; locked when the round starts.

## Silos (2026-10-02)
- Match cards (full, compact live, detail sheet), home feeds and club fixture lists show no Affinity and no pick 'em,
  so neither colours a neutral viewing. Pick 'em lives in each competition's Pick 'em tab (viewPicks: upcoming picks
  with expected points and the Affinity pick, scored picks, season totals); Affinity in the Clubs tab, club cards and
  the Affinity ranking.
- Heart over head: on a neutral match (no followed club) once it's under way, a "Pulled for" row (home / away /
  neither) and an optional note on players or coaches. Stored as state.heart[k][fixtureId] = {s:'H'|'A'|'N', t, note},
  synced in the competition doc's `heart` field like results, cached in localStorage. Meant as the next calibration
  set for Affinity (each pull is a head-to-head preference).
