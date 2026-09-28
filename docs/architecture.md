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
6. Predicted score (draw-zone calibrated) and **pick 'em** pick = argmax of
   peOutcome*P(outcome) + (peExact-peOutcome)*P(exact). Locked at result entry (results[id][2..4]).
7. Table (+ points adjustments S.adj), clinch/elimination statuses (cfg.status), groups/conferences.
8. Monte Carlo: S.sims seasons (1000); live matches sample remaining goals (xG scaled by time left).
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
  (Kicked off, Half-time, 2nd half, Full time, +1 goal); the clock runs from the last tap. 45+N/90+N for
  stoppage; missed taps are guessed (~) and "FT?" asks for full time after 90+15. A 30 s timer keeps clocks
  current and re-runs the model every 2 match minutes. Old {h, a, min, ht} entries keep a fixed minute.
- Sticky bar (#mini): slides in once the header nav scrolls away; competition (tap = back to top) + sections.
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
