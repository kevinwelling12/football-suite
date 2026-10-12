const Z = (key, label, test, w, extra = {}) => Object.assign({ key, label, test, w, scope: 'overall' }, extra);
const EU_LINES = [[17.5, 1], [1.5, 0.85], [4.5, 0.55], [6.5, 0.25], [5.5, 0.2]];
const GOLD = '#E9B308', GREEN = 'var(--mint)', CYAN = 'var(--cyan)', RED = 'var(--magenta)', AMBER = '#F29D0C';
const euro20 = (zw) => ({
  zones: [Z('title', 'Title', r => r === 1, zw['Title']), Z('top4', 'Top 4', r => r <= 4, zw['Top 4']), Z('europe', 'Top 6', r => r <= 6, zw['Europe (top 6)']), Z('rel', 'Relegated', r => r >= 18, zw['Relegation'], { bad: true })],
  status: [{ type: 'doom', k: 17, label: 'Relegated' }, { type: 'clinch', k: 4, label: 'Top 4 clinched' }, { type: 'clinch', k: 17, label: 'Safe' }],
  lines: EU_LINES, cols: ['title', 'top4', 'rel'], colors: [[1, 1, GOLD], [2, 4, GREEN], [5, 6, CYAN], [18, 20, RED]], cuts: [4, 17],
  legend: [['Champion', GOLD], ['Champions League', GREEN], ['Europe', CYAN], ['Relegation', RED]],
  headline: ['Title race', 'title', 'to win the league'], line: ['Safety line', 17, 'Projected 17th place'] });
const euro18 = (zw, top, topKey) => ({
  zones: [Z('title', 'Title', r => r === 1, zw['Title']), Z(topKey, `Top ${top}`, r => r <= top, zw[`Top ${top}`]), Z('europe', 'Top 6', r => r <= 6, zw['Europe (top 6)']),
    Z('po', '16th (play-off)', r => r === 16, zw['Relegation play-off'], { bad: true }), Z('rel', 'Relegated', r => r >= 17, zw['Relegation'], { bad: true })],
  status: [{ type: 'doom', k: 16, label: 'Relegated' }, { type: 'clinch', k: top, label: `Top ${top} clinched` }, { type: 'clinch', k: 15, label: 'Safe' }],
  lines: [[16.5, 1], [15.5, 0.6], [1.5, 0.85], [top + 0.5, 0.55], [6.5, 0.25]], cols: ['title', topKey, 'rel'],
  colors: [[1, 1, GOLD], [2, top, GREEN], [top + 1, 6, CYAN], [16, 16, AMBER], [17, 18, RED]], cuts: [top, 15],
  legend: [['Champion', GOLD], ['Champions League', GREEN], ['Europe', CYAN], ['Play-off', AMBER], ['Relegation', RED]],
  headline: ['Title race', 'title', 'to win the league'], line: ['Safety line', 15, 'Projected 15th place'] });

const COMPS_CFG = {
  epl: { drawPrior: 0.24, name: 'Premier League', season: '26/27', round: 'Matchweek', abbr: 'MW', brand: { head: '#37003C', accent: '#E90052', glow: 'rgba(233,0,82,.55)', tag: '#FF6FA6' }, source: 'openfootball', build: zw => euro20(zw) },
  bl: { drawPrior: 0.24, name: 'Bundesliga', season: '26/27', round: 'Matchday', abbr: 'MD', brand: { head: '#1A1A1A', accent: '#D20515', glow: 'rgba(210,5,21,.55)', tag: '#FF6B74' }, source: 'openfootball', build: zw => euro18(zw, 4, 'top4') },
  nwsl: { drawPrior: 0.24, name: 'NWSL', season: '2026', round: 'Week', abbr: 'Wk', brand: { head: '#0A1F44', accent: '#E03A3E', glow: 'rgba(224,58,62,.5)', tag: '#FF8A8D' }, source: 'FBref',
    build: zw => ({
      zones: [Z('shield', 'Shield', r => r === 1, zw['NWSL Shield']), Z('top4', 'Top 4', r => r <= 4, zw['Top 4 (home quarterfinal)']), Z('po', 'Playoffs', r => r <= 8, zw['Playoffs (top 8)'])],
      status: [{ type: 'doom', k: 8, label: 'Eliminated', mark: 'e' }, { type: 'clinch', k: 1, label: 'Shield clinched', mark: 'z' }, { type: 'clinch', k: 4, label: 'Home QF clinched', mark: 'y' }, { type: 'clinch', k: 8, label: 'Playoffs clinched', mark: 'x' }],
      knockout: 'nwslpo', lines: [[8.5, 1], [1.5, 0.6], [4.5, 0.5]], cols: ['shield', 'top4', 'po'], colLabels: { champ: 'Champion', final: 'Final', sf: 'Semifinal' }, colors: [[1, 1, GOLD], [2, 4, GREEN], [5, 8, CYAN]], cuts: [8],
      legend: [['Shield', GOLD], ['Home quarterfinal', GREEN], ['Playoffs', CYAN]],
      headline: ['Shield race', 'shield', 'to win the Shield'], line: ['Playoff line', 8, 'Projected 8th place'] }) },
  mls: { drawPrior: 0.24, name: 'MLS', season: '2026', round: 'Round', abbr: 'Rd', brand: { head: '#001F5B', accent: '#D6001C', glow: 'rgba(214,0,28,.5)', tag: '#FF6B7E' }, source: 'your MLS file', grouped: true,
    build: zw => ({
      zones: [Z('po', 'Playoffs', r => r <= 9, zw['Playoffs (top 9 in conference)'], { scope: 'group' }), Z('bye', 'Bye', r => r <= 7, zw['Round-one bye (top 7)'], { scope: 'group' }),
        Z('conf', 'Conf 1st', r => r === 1, zw['Conference 1st'], { scope: 'group' }), Z('shield', 'Shield', r => r === 1, zw["Supporters' Shield"])],
      status: [{ type: 'doom', k: 9, label: 'Eliminated', mark: 'e' }, { type: 'clinch', k: 7, label: 'Bye clinched', mark: 'y' }, { type: 'clinch', k: 9, label: 'Playoffs clinched', mark: 'x' }],
      knockout: 'mlspo', lines: [[9.5, 1], [7.5, 0.6], [1.5, 0.4]], cols: ['shield', 'bye', 'po'], colLabels: { champ: 'MLS Cup', final: 'Cup final', cf: 'Conf final', csf: 'Conf semis' }, colors: [[1, 7, GREEN], [8, 9, CYAN]], cuts: [9],
      legend: [['Round-one bye', GREEN], ['Wild card', CYAN]],
      headline: ["Supporters' Shield", 'shield', "to win the Supporters' Shield"], line: ['Playoff line', 9, '9th in each conference'] }) },
  usl: { drawPrior: 0.26, name: 'USL Championship', season: '2026', round: 'Week', abbr: 'Wk', brand: { head: '#0F1B2D', accent: '#F26B21', glow: 'rgba(242,107,33,.5)', tag: '#FF9A5C' }, source: 'FBref', grouped: true,
    build: zw => ({
      zones: [Z('po', 'Playoffs', r => r <= 8, 1, { scope: 'group' }), Z('top4', 'Top 4', r => r <= 4, 0.5, { scope: 'group' }),
        Z('conf', 'Conf 1st', r => r === 1, 0.3, { scope: 'group' }), Z('shield', "Players' Shield", r => r === 1, 0.5)],
      knockout: 'uslpo', status: [{ type: 'doom', k: 8, label: 'Eliminated', mark: 'e' }, { type: 'clinch', k: 4, label: 'Home QF clinched', mark: 'y' }, { type: 'clinch', k: 8, label: 'Playoffs clinched', mark: 'x' }],
      lines: [[8.5, 1], [4.5, 0.5], [1.5, 0.4]], cols: ['shield', 'top4', 'po'], colLabels: { champ: 'Champion', final: 'Final', cf: 'Conf final', csf: 'Conf semis', top4: 'Home QF' },
      colors: [[1, 4, GREEN], [5, 8, CYAN]], cuts: [8], legend: [['Home quarterfinal', GREEN], ['Playoffs', CYAN]],
      headline: ["Players' Shield", 'shield', "to win the Players' Shield"], line: ['Playoff line', 8, '8th in each conference'] }) },
  ucl: { drawPrior: 0.2, name: 'Champions League', season: '26/27', round: 'Matchday', abbr: 'MD', brand: { head: '#0B1446', accent: '#2F6FED', glow: 'rgba(47,111,237,.55)', tag: '#8FB0FF' }, source: 'UEFA',
    build: zw => ({
      zones: [Z('top8', 'Top 8', r => r <= 8, zw['Top 8 (round of 16 bye)']), Z('top24', 'Top 24', r => r <= 24, zw['Top 24 (knockout play-off)'])],
      knockout: 'ucl', status: [{ type: 'doom', k: 24, label: 'Eliminated', mark: 'e' }, { type: 'clinch', k: 8, label: 'Top 8 clinched', mark: 'y' }, { type: 'clinch', k: 24, label: 'Knockouts clinched', mark: 'x' }],
      lines: [[8.5, 1], [24.5, 1], [16.5, 0.5]], cols: ['top8', 'qf', 'win'], colLabels: { qf: 'Quarter-finals', win: 'Win it' },
      colors: [[1, 8, GREEN], [9, 24, CYAN]], cuts: [8, 24], legend: [['Round of 16', GREEN], ['Knockout play-off', CYAN]],
      headline: ['Title race', 'win', 'to lift the trophy'], line: ['Top-8 line', 8, 'Projected 8th place'] }) },
};
// Top nav: region tabs, then that region's competitions as chips. ORDER follows the regions.
// dot = the competition's colour in the nav and on the overview: one clearly different hue per competition,
// tuned to read on black. brand.* still themes each competition's own pages.
const REGIONS = [
  { key: 'eur', name: 'Europe', comps: ['epl', 'bl', 'ucl'] },
  { key: 'usa', name: 'USA', comps: ['mls', 'usl', 'nwsl'] },
];
const DOT = { epl: '#FF2D87', ucl: '#3B82F6', bl: '#EF4444', mls: '#38BDF8', usl: '#FFB020', nwsl: '#A78BFA' };
// Chip labels: [full, phone]. Phone labels keep each region's chips on one row at 390px.
const CHIP = { epl: ['Premier League', 'Premier Lg'], usl: ['USL'] };
const ORDER = REGIONS.flatMap(r => r.comps);
// US TV, short form for match cards (the full line, from data tv, shows on the match sheet).
const TV_SHORT = { epl: 'Peacock / NBC', ucl: 'Paramount+ / CBS', bl: 'Fandango', mls: 'Apple TV', usl: 'ESPN+', nwsl: 'Paramount+, ESPN, Prime' };
// Short labels for the slim bar that sticks to the top once the header scrolls away.
const ABBR = { epl: 'EPL', ucl: 'UCL', bl: 'BL', mls: 'MLS', usl: 'USL', nwsl: 'NWSL' };
// Model config for a competition (shared by the page and the background model worker).
function compCfg(k, params) {
  const c = COMPS_CFG[k];
  return Object.assign({ grouped: !!c.grouped, satOrder: c.satOrder, drawPrior: c.drawPrior }, c.build ? c.build((params || {}).zoneW || {}) : {});
}
if (typeof module !== 'undefined') module.exports = { COMPS_CFG, ORDER, REGIONS, DOT, CHIP, ABBR, TV_SHORT, compCfg };
