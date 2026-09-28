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
  esp: { drawPrior: 0.26, name: 'LaLiga', season: '26/27', round: 'Matchday', abbr: 'MD', brand: { head: '#1B1B2F', accent: '#FF4B44', glow: 'rgba(255,75,68,.5)', tag: '#FF8A84' }, source: 'openfootball', build: zw => euro20(zw) },
  ita: { drawPrior: 0.26, name: 'Serie A', season: '26/27', round: 'Matchday', abbr: 'MD', brand: { head: '#0B1E3D', accent: '#1F7AE0', glow: 'rgba(31,122,224,.55)', tag: '#7DB5FF' }, source: 'openfootball', build: zw => euro20(zw) },
  bl: { drawPrior: 0.24, name: 'Bundesliga', season: '26/27', round: 'Matchday', abbr: 'MD', brand: { head: '#1A1A1A', accent: '#D20515', glow: 'rgba(210,5,21,.55)', tag: '#FF6B74' }, source: 'openfootball', build: zw => euro18(zw, 4, 'top4') },
  fra: { drawPrior: 0.27, name: 'Ligue 1', season: '26/27', round: 'Matchday', abbr: 'MD', brand: { head: '#101010', accent: '#C8DC00', glow: 'rgba(200,220,0,.45)', tag: '#DAED3A' }, source: 'openfootball', build: zw => euro18(zw, 3, 'top3') },
  ch: { drawPrior: 0.27, name: 'Championship', season: '26/27', round: 'Matchweek', abbr: 'MW', brand: { head: '#0B1F3A', accent: '#C9A227', glow: 'rgba(201,162,39,.5)', tag: '#E7C65A' }, source: 'openfootball',
    build: zw => ({
      zones: [Z('title', 'Title', r => r === 1, zw['Title']), Z('auto', 'Promoted', r => r <= 2, zw['Automatic promotion']), Z('po', 'Play-offs', r => r <= 6, zw['Play-offs (top 6)']), Z('rel', 'Relegated', r => r >= 22, zw['Relegation'], { bad: true })],
      status: [{ type: 'doom', k: 21, label: 'Relegated' }, { type: 'clinch', k: 2, label: 'Promoted' }, { type: 'clinch', k: 6, label: 'Play-offs clinched' }, { type: 'clinch', k: 21, label: 'Safe' }],
      lines: [[2.5, 1], [6.5, 0.85], [21.5, 1], [1.5, 0.3]], cols: ['auto', 'po', 'rel'], colors: [[1, 1, GOLD], [2, 2, GREEN], [3, 6, CYAN], [22, 24, RED]], cuts: [2, 6, 21],
      legend: [['Champion', GOLD], ['Promoted', GREEN], ['Play-offs', CYAN], ['Relegation', RED]],
      headline: ['Promotion race', 'auto', 'to go up automatically'], line: ['Play-off line', 6, 'Projected 6th place'] }) },
  nwsl: { drawPrior: 0.24, name: 'NWSL', season: '2026', round: 'Week', abbr: 'Wk', brand: { head: '#0A1F44', accent: '#E03A3E', glow: 'rgba(224,58,62,.5)', tag: '#FF8A8D' }, source: 'FBref',
    build: zw => ({
      zones: [Z('shield', 'Shield', r => r === 1, zw['NWSL Shield']), Z('top4', 'Top 4', r => r <= 4, zw['Top 4 (home quarterfinal)']), Z('po', 'Playoffs', r => r <= 8, zw['Playoffs (top 8)'])],
      status: [{ type: 'doom', k: 8, label: 'Eliminated' }, { type: 'clinch', k: 1, label: 'Shield clinched' }, { type: 'clinch', k: 4, label: 'Home QF clinched' }, { type: 'clinch', k: 8, label: 'Playoffs clinched' }],
      knockout: 'nwslpo', lines: [[8.5, 1], [1.5, 0.6], [4.5, 0.5]], cols: ['shield', 'top4', 'po'], colLabels: { champ: 'Champion', final: 'Final', sf: 'Semifinal' }, colors: [[1, 1, GOLD], [2, 4, GREEN], [5, 8, CYAN]], cuts: [8],
      legend: [['Shield', GOLD], ['Home quarterfinal', GREEN], ['Playoffs', CYAN]],
      headline: ['Shield race', 'shield', 'to win the Shield'], line: ['Playoff line', 8, 'Projected 8th place'] }) },
  mls: { drawPrior: 0.24, name: 'MLS', season: '2026', round: 'Round', abbr: 'Rd', brand: { head: '#001F5B', accent: '#D6001C', glow: 'rgba(214,0,28,.5)', tag: '#FF6B7E' }, source: 'your MLS file', grouped: true,
    build: zw => ({
      zones: [Z('po', 'Playoffs', r => r <= 9, zw['Playoffs (top 9 in conference)'], { scope: 'group' }), Z('bye', 'Bye', r => r <= 7, zw['Round-one bye (top 7)'], { scope: 'group' }),
        Z('conf', 'Conf 1st', r => r === 1, zw['Conference 1st'], { scope: 'group' }), Z('shield', 'Shield', r => r === 1, zw["Supporters' Shield"])],
      status: [{ type: 'doom', k: 9, label: 'Eliminated' }, { type: 'clinch', k: 9, label: 'Playoffs clinched' }],
      knockout: 'mlspo', lines: [[9.5, 1], [7.5, 0.6], [1.5, 0.4]], cols: ['shield', 'bye', 'po'], colLabels: { champ: 'MLS Cup', final: 'Cup final', cf: 'Conf final', csf: 'Conf semis' }, colors: [[1, 7, GREEN], [8, 9, CYAN]], cuts: [9],
      legend: [['Round-one bye', GREEN], ['Wild card', CYAN]],
      headline: ["Supporters' Shield", 'shield', "to win the Supporters' Shield"], line: ['Playoff line', 9, '9th in each conference'] }) },
  usl: { drawPrior: 0.26, name: 'USL Championship', season: '2026', round: 'Week', abbr: 'Wk', brand: { head: '#0F1B2D', accent: '#F26B21', glow: 'rgba(242,107,33,.5)', tag: '#FF9A5C' }, source: 'FBref', grouped: true,
    build: zw => ({
      zones: [Z('po', 'Playoffs', r => r <= 8, 1, { scope: 'group' }), Z('top4', 'Top 4', r => r <= 4, 0.5, { scope: 'group' }),
        Z('conf', 'Conf 1st', r => r === 1, 0.3, { scope: 'group' }), Z('shield', "Players' Shield", r => r === 1, 0.5)],
      knockout: 'uslpo', status: [{ type: 'doom', k: 8, label: 'Eliminated' }, { type: 'clinch', k: 8, label: 'Playoffs clinched' }],
      lines: [[8.5, 1], [4.5, 0.5], [1.5, 0.4]], cols: ['shield', 'top4', 'po'], colLabels: { champ: 'Champion', final: 'Final', cf: 'Conf final', csf: 'Conf semis', top4: 'Home QF' },
      colors: [[1, 4, GREEN], [5, 8, CYAN]], cuts: [8], legend: [['Home quarterfinal', GREEN], ['Playoffs', CYAN]],
      headline: ["Players' Shield", 'shield', "to win the Players' Shield"], line: ['Playoff line', 8, '8th in each conference'] }) },
  ucl: { drawPrior: 0.2, name: 'Champions League', season: '26/27', round: 'Matchday', abbr: 'MD', brand: { head: '#0B1446', accent: '#2F6FED', glow: 'rgba(47,111,237,.55)', tag: '#8FB0FF' }, source: 'UEFA',
    build: zw => ({
      zones: [Z('top8', 'Top 8', r => r <= 8, zw['Top 8 (round of 16 bye)']), Z('top24', 'Top 24', r => r <= 24, zw['Top 24 (knockout play-off)'])],
      knockout: 'ucl', status: [{ type: 'doom', k: 24, label: 'Eliminated' }, { type: 'clinch', k: 8, label: 'Top 8 clinched' }, { type: 'clinch', k: 24, label: 'Knockouts clinched' }],
      lines: [[8.5, 1], [24.5, 1], [16.5, 0.5]], cols: ['top8', 'qf', 'win'], colLabels: { qf: 'Quarter-finals', win: 'Win it' },
      colors: [[1, 8, GREEN], [9, 24, CYAN]], cuts: [8, 24], legend: [['Round of 16', GREEN], ['Knockout play-off', CYAN]],
      headline: ['Title race', 'win', 'to lift the trophy'], line: ['Top-8 line', 8, 'Projected 8th place'] }) },
  unl: { drawPrior: 0.25, name: 'Nations League', season: '26/27', round: 'Matchday', abbr: 'MD', brand: { head: '#0D1B3E', accent: '#00A3E0', glow: 'rgba(0,163,224,.5)', tag: '#6FD2F5' }, source: 'UEFA', grouped: true, satOrder: 'groupFirst', noun: 'Nation',
    build: zw => ({
      zones: [Z('winner', 'Group winner', r => r === 1, zw['Group winner'] ?? 0.5, { scope: 'group' }), Z('top2', 'Top 2', r => r <= 2, zw['Quarter-finals (top 2)'] ?? 1, { scope: 'group' }),
        Z('safe', 'Top 3', r => r <= 3, zw['Avoid relegation (top 3)'] ?? 1, { scope: 'group' })],
      knockout: 'unl2', status: [{ type: 'clinch', k: 1, label: 'Group won' }, { type: 'clinch', k: 2, label: 'Top 2 clinched' }],
      lines: [[2.5, 1], [3.5, 0.85], [1.5, 0.4]], cols: ['top2', 'win', 'down'],
      colsByLeague: { A: ['top2', 'win', 'down'], B: ['up', 'po', 'down'], C: ['up', 'po'], D: ['winner', 'up'] },
      colLabels: { top2: 'Quarter-finals', win: 'Win it', down: 'Relegated', up: 'Promoted', po: 'Play-off', winner: 'Group winner' },
      leagueNotes: { A: 'Top 2 in each group reach the quarter-finals. The two worst 4th-placed teams go down; the two best 4th-placed and two worst 3rd-placed teams play off against League B runners-up in March.',
        B: 'Group winners are promoted to League A. Runners-up play off for promotion against League A teams; 4th-placed teams play off to stay up against League C runners-up.',
        C: 'Group winners are promoted to League B. Runners-up play off for promotion against League B\'s 4th-placed teams.',
        D: 'Every League D nation is promoted to League C for the next edition.' },
      colors: [], cuts: [], legend: [],
      headline: ['Title race', 'win', 'to win the Nations League'], line: ['Quarter-final line', 8, 'Projected 8th overall'] }) },
  cup: { name: 'Carabao Cup', season: '26/27', round: 'Round', abbr: '', brand: { head: '#004D2C', accent: '#E30613', glow: 'rgba(227,6,19,.5)', tag: '#FF7A82' }, source: 'EFL and match reports', cup: true },
};
// Top nav: region tabs, then that region's competitions as chips. ORDER follows the regions.
// dot = the competition's colour in the nav and on the overview: one clearly different hue per competition,
// tuned to read on black. brand.* still themes each competition's own pages.
const REGIONS = [
  { key: 'eng', name: 'England', comps: ['epl', 'ch', 'cup'] },
  { key: 'eur', name: 'Europe', comps: ['esp', 'ita', 'bl', 'fra'] },
  { key: 'usa', name: 'USA', comps: ['mls', 'usl', 'nwsl'] },
  { key: 'uefa', name: 'UEFA', comps: ['ucl', 'unl'] },
];
const DOT = { epl: '#FF2D87', ch: '#E9B824', cup: '#22C55E', ucl: '#3B82F6', esp: '#FF7A1A', ita: '#14B8A6', bl: '#EF4444', fra: '#C4E02A',
  mls: '#38BDF8', usl: '#FFB020', nwsl: '#A78BFA', unl: '#CBD5E1' };
// Chip labels: [full, phone]. Phone labels keep each region's chips on one row at 390px.
const CHIP = { epl: ['Premier League', 'Premier Lg'], cup: ['Carabao Cup', 'Carabao'], usl: ['USL'] };
const ORDER = REGIONS.flatMap(r => r.comps);
// Short labels for the slim bar that sticks to the top once the header scrolls away.
const ABBR = { epl: 'EPL', ch: 'EFL', cup: 'Cup', ucl: 'UCL', esp: 'LaLiga', ita: 'Serie A', bl: 'BL', fra: 'L1', mls: 'MLS', usl: 'USL', nwsl: 'NWSL', unl: 'UNL' };
// Model config for a competition (shared by the page and the background model worker).
function compCfg(k, params) {
  const c = COMPS_CFG[k];
  return Object.assign({ grouped: !!c.grouped, satOrder: c.satOrder, drawPrior: c.drawPrior }, c.build ? c.build((params || {}).zoneW || {}) : {});
}
if (typeof module !== 'undefined') module.exports = { COMPS_CFG, ORDER, REGIONS, DOT, CHIP, ABBR, compCfg };
