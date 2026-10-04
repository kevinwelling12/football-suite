// Club logos (ESPN, dark-background variant where there is one) and national flags (flagcdn), saved into the
// repo so the page never depends on someone else's server at runtime.
//
//   node scripts/logos/fetch.js            # fetch what's missing, rewrite data/logos.json
//   node scripts/logos/fetch.js --force    # fetch everything again
//
// data/logos.json maps competition -> tracker team name -> file under src/logos/ (copied next to the page by
// build.py). Clubs ESPN doesn't list stay as colour discs; the report names them.
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '../..');
const D = require(path.join(root, 'data/suite_data.json'));
const EXTRA = require(path.join(root, 'data/nations_extra.json'));
const ALIAS = Object.assign({}, require(path.join(root, 'scripts/sync/espn_aliases.json')), require('./aliases.json'));
const OUT = path.join(root, 'src/logos'), FORCE = process.argv.includes('--force');

// Where to look for each competition's clubs. The Carabao Cup draws on all four English divisions.
const SOURCES = { epl: ['eng.1'], ch: ['eng.2'], cup: ['eng.1', 'eng.2', 'eng.3', 'eng.4'], ucl: ['uefa.champions', 'eng.1', 'esp.1', 'ita.1', 'ger.1', 'fra.1', 'por.1', 'ned.1', 'bel.1', 'sco.1', 'aut.1', 'den.1', 'nor.1', 'tur.1', 'gre.1', 'cze.1', 'sui.1'],
  esp: ['esp.1'], ita: ['ita.1'], bl: ['ger.1'], fra: ['fra.1'], mls: ['usa.1'], usl: ['usa.usl.1'], nwsl: ['usa.nwsl'] };
// ISO 3166 codes for flagcdn (UK home nations use its gb-xxx codes).
const ISO = { Albania: 'al', Andorra: 'ad', Armenia: 'am', Austria: 'at', Azerbaijan: 'az', Belarus: 'by', Belgium: 'be', 'Bosnia and Herzegovina': 'ba',
  Bulgaria: 'bg', Croatia: 'hr', Cyprus: 'cy', 'Czech Republic': 'cz', Denmark: 'dk', England: 'gb-eng', Estonia: 'ee', 'Faroe Islands': 'fo', Finland: 'fi',
  France: 'fr', Georgia: 'ge', Germany: 'de', Gibraltar: 'gi', Greece: 'gr', Hungary: 'hu', Iceland: 'is', Israel: 'il', Italy: 'it', Kazakhstan: 'kz',
  Kosovo: 'xk', Latvia: 'lv', Liechtenstein: 'li', Lithuania: 'lt', Luxembourg: 'lu', Malta: 'mt', Moldova: 'md', Montenegro: 'me', Netherlands: 'nl',
  'North Macedonia': 'mk', 'Northern Ireland': 'gb-nir', Norway: 'no', Poland: 'pl', Portugal: 'pt', 'Republic of Ireland': 'ie', Romania: 'ro',
  'San Marino': 'sm', Scotland: 'gb-sct', Serbia: 'rs', Slovakia: 'sk', Slovenia: 'si', Spain: 'es', Sweden: 'se', Switzerland: 'ch', Turkey: 'tr',
  Ukraine: 'ua', Wales: 'gb-wls', Algeria: 'dz', Argentina: 'ar', Australia: 'au', Brazil: 'br', Canada: 'ca', 'Cape Verde': 'cv', Colombia: 'co',
  'Curaçao': 'cw', 'DR Congo': 'cd', Ecuador: 'ec', Egypt: 'eg', Ghana: 'gh', Haiti: 'ht', Iran: 'ir', Iraq: 'iq', 'Ivory Coast': 'ci', Japan: 'jp',
  Jordan: 'jo', Mexico: 'mx', Morocco: 'ma', 'New Zealand': 'nz', Panama: 'pa', Paraguay: 'py', Qatar: 'qa', 'Saudi Arabia': 'sa', Senegal: 'sn',
  'South Africa': 'za', 'South Korea': 'kr', Tunisia: 'tn', 'United States': 'us', Uruguay: 'uy', Uzbekistan: 'uz' };

// ESPN ids whose dark variant has a solid white square; the standard logo is transparent.
const LIGHT = new Set(['345']);
// Files whose white square was cleared by clear_bg.js (no transparent version at ESPN): never re-downloaded.
const CLEARED = new Set(['17828-d.png', '17850-d.png', '18265-d.png', '303-d.png']);
const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ø/gi, 'o').replace(/ß/g, 'ss').toLowerCase()
  .replace(/\b(fc|afc|cf|sc|ac|club|de|the|cd|ud|sd|rc|ca|ssc|as|us|sv|vfb|vfl|tsg|1)\b/g, '').replace(/[^a-z0-9]/g, '');
async function get(url, json = true, tries = 4) {
  for (let i = 0; ; i++) {
    try { const r = await fetch(url); if (r.ok) return json ? await r.json() : Buffer.from(await r.arrayBuffer()); if (r.status < 500) return null; } catch (e) { if (i >= tries) throw e; }
    if (i >= tries) return null;
    await new Promise(res => setTimeout(res, 800 * 2 ** i));
  }
}
const espnTeams = {};
async function league(slug) {
  if (!espnTeams[slug]) {
    const j = await get(`https://site.api.espn.com/apis/site/v2/sports/soccer/${slug}/teams`);
    espnTeams[slug] = ((j && j.sports && j.sports[0].leagues[0].teams) || []).map(x => x.team);
  }
  return espnTeams[slug];
}
function pick(teams, t) {
  const want = [t.name, t.short].filter(Boolean), keys = want.map(norm);
  const names = x => [x.displayName, x.shortDisplayName, x.location, x.name].filter(Boolean);
  for (const x of teams) if (names(x).some(n => want.includes(ALIAS[n]))) return x;
  for (const x of teams) if (names(x).some(n => want.includes(n))) return x;
  const hits = teams.filter(x => names(x).map(norm).some(n => keys.includes(n)));
  if (hits.length === 1) return hits[0];
  const loose = teams.filter(x => names(x).map(norm).some(n => n.length > 3 && keys.some(kk => kk.length > 3 && (kk.includes(n) || n.includes(kk)))));
  return loose.length === 1 ? loose[0] : null;
}
async function save(file, url) {
  const dest = path.join(OUT, file);
  if ((!FORCE || CLEARED.has(file)) && fs.existsSync(dest)) return true;
  const buf = await get(url, false); if (!buf) return false;
  fs.mkdirSync(path.dirname(dest), { recursive: true }); fs.writeFileSync(dest, buf); return true;
}

(async () => {
  const map = {}, missing = [];
  for (const [k, slugs] of Object.entries(SOURCES)) {
    map[k] = {};
    const seen = new Set(), pool = []; for (const s of slugs) for (const x of await league(s)) if (!seen.has(x.id)) { seen.add(x.id); pool.push(x); }
    for (const t of D[k].teams) {
      const x = pick(pool, t);
      if (x && process.argv.includes('--check') && norm(x.displayName) !== norm(t.name)) console.log(`  ${k}: ${t.name} <- ${x.displayName}`);
      const logo = x && x.logos && ((!LIGHT.has(x.id) && x.logos.find(l => (l.rel || []).includes('dark'))) || x.logos.find(l => !(l.rel || []).includes('dark')) || x.logos[0]);
      if (!logo) { missing.push(`${k}: ${t.name}`); continue; }
      const dark = (logo.rel || []).includes('dark'), file = `${x.id}${dark ? '-d' : ''}.png`;
      // ESPN's image combiner serves a 128px copy (about a tenth of the 500px original).
      const src = logo.href.replace(/^https:\/\/a\.espncdn\.com/, '');
      if (await save(file, `https://a.espncdn.com/combiner/i?img=${encodeURIComponent(src)}&w=128&h=128`) || await save(file, logo.href)) map[k][t.name] = 'logos/' + file;
      else missing.push(`${k}: ${t.name} (download failed)`);
    }
  }
  const nations = [...D.unl.teams, ...EXTRA.teams];
  map.flags = {};
  for (const t of nations) {
    const c = ISO[t.name]; if (!c) { missing.push(`flag: ${t.name}`); continue; }
    if (await save(`flags/${c}.png`, `https://flagcdn.com/w160/${c}.png`)) map.flags[t.name] = `logos/flags/${c}.png`; else missing.push(`flag: ${t.name} (download failed)`);
  }
  fs.writeFileSync(path.join(root, 'data/logos.json'), JSON.stringify(map, null, 1) + '\n');
  const n = Object.values(map).reduce((s, m) => s + Object.keys(m).length, 0);
  console.log(`${n} logos and flags mapped; ${missing.length} without:\n` + missing.join('\n'));
})();
