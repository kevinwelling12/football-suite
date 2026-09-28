# Re-rate review (runbook step 4), 2026-09-28

All 11 batches in: 308 entries, 0 validation problems, all 13 anchor checks pass.
Full numbers: out/report.txt (python3 scripts/affinity/research/compare.py).
Nothing in scores.py, build_usl.py, rescore.py or the app has changed. Waiting on Kevin.

## Calibration
- No outlier batch. Factor means by batch sit within about 1 point of the old scores on the same clubs.
- Culture fell about 0.9 in b03, b04, b09 and b10. The drops are specific clubs with attendance evidence
  (Racing Louisville ~5,500, Chicago Stars 4,517, Fleetwood, Burton, Stevenage, Andorra, Gibraltar), not a harsh batch.
- Clubs change -4.7 on average: research factors and new adjustments. The weight change adds +0.1, dropping the
  regional bonus -0.7.

## Weights
Proposal C26 V28 H16 O12 S8 (of 90). Top 12 clubs under it: Athletic Club 94.2, Union Berlin 88.0, Dortmund 83.6,
Stuttgart 82.9, Köln 82.4, Schalke 81.8, AFC Wimbledon 81.8, Liverpool 80.7, Sounders 79.8, Bayern 79.8,
Detroit City 78.9, Werder Bremen 78.2. Old weights give almost the same top 12 (Portland Thorns in, Detroit out).
Recommendation: take the proposal.

## Decisions for Kevin
A. Double counting
1. City Football Group satellites: Troyes and NYCFC have state -25 plus multiclub -8 (Troyes 36.9 -> 0.8,
   NYCFC 39.0 -> 5.9). Option: state -25 only on Man City, satellites keep multiclub -8 (old approach).
2. Stacks: Man City -39 (state, multiclub, Super League, overspend -6), PSG -33 (state, pe -4 Arctos, multiclub -4 Braga, unverified).
3. pe plus multiclub for the same owner: Chelsea -14, Strasbourg -12, Walsall -10, Southampton -10, Milan -10, Toulouse -8, Lens -8.
   Option: cap the pair at -8.
4. RB Leipzig: new franchise -10 on top of multiclub -6.
5. Southampton Spygate counted twice (Values 5 and other -3).

B. Same owner, different treatment
- Kroenke: Colorado multiclub -4, Arsenal 0.
- Nagle: Huddersfield -4, Sacramento Republic 0.
- Kang: Washington Spirit -6, Lyon -4.
- Levien/Kaplan: D.C. United -4, Swansea 0.
- Pozzo: Watford -6, Udinese -4 (Udinese sale to Guggenheim unconfirmed).

C. New or larger adjustments to confirm
- LBO: Manchester United -20 (Glazer debt), Burnley -15.
- Liverpool: pe -4 (FSG), Values 9 -> 8 (Turkish Airlines from 2027-28).
- Violence, 12 new: Galatasaray -8, Fenerbahçe -8, Inter -6, Roma -6, Frankfurt -5, Nice -5, Feyenoord -5,
  Porto -5, Slovan -5, England -5, Marseille -4, Atlético -4.
- Racism: Millwall -5 -> -8, Serbia -10 -> -12, Croatia -10 -> -12, new Albania -10, Romania -10, Atlético -10,
  Slovan -10, Feyenoord -5 -> -8, Nice -6, Valencia -5. Lazio stays -30.
- Government (16 nations): Belarus, Azerbaijan -25 (replaces old federation -10); Israel, Turkey, Kazakhstan -20;
  Georgia, Serbia -15; Albania, Armenia, Bosnia, Hungary, Kosovo, Moldova, Montenegro, North Macedonia, Ukraine -10.
  Open: Ukraine (martial law drives the score), Moldova (RSF 31st), Israel (-15 to -25 defensible), Turkey (-25?).
- Man City overspend -6 rests on the 25 Sept report (The Athletic, Reuters) of 114 of 115 charges upheld.
  Not published by the Premier League; City to appeal.

D. Sponsor rules
- Casino brands, not sportsbooks: Reading (Mr Vegas), QPR (MrQ), Leicester (BC.Game, has a sportsbook),
  Seattle (Emerald Queen Casino). Count as betting?
- Owner owns the betting sponsor: Stoke / bet365, Values 3.
- State tourism brands from Partly Free states: Cardiff (Visit Malaysia), MK Dons (Visit Kuwait), Villa (Visit Rwanda),
  Bayern (Rwanda, academy only now).

E. Big moves on clubs Kevin follows
- Sacramento Republic: Culture 10 -> 8, History 7 -> 6. Displayed 85.6 -> 77.8 (with +4 hometown).
- Louisville City Culture 10 -> 8. Racing Louisville Culture 7 -> 4, Ownership 7 -> 4 (possible move to Cincinnati).
- Portland Thorns Values 8 -> 6 (Yates report), Timbers Values 9 -> 8, History 8 -> 7.
- St. Louis CITY Values 7 -> 5 (banner ban Feb 2026, FanDuel), Culture 9 -> 8.
- NC Courage: franchise -10 for the 2017 Western New York Flash move, not applied.

F. Low confidence: Udinese, LASK, Sabah, Denver Summit, Brooklyn FC, Orange County SC, Cyprus, Kazakhstan, Malta.

Per-club flags (about 250) are in each out/<batch>.json entry and listed at the end of out/report.txt.
