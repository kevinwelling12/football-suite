const DATA = /*__DATA__*/;
// Nations outside the Nations League (2026 World Cup), for the Affinity pages only: {wc: {name: result}, teams: [...]}.
const EXTRA = /*__EXTRA__*/;
// Club logos and national flags (files next to the page; data/logos.json, made by scripts/logos/fetch.js). Empty in the claude.ai build.
const LOGOS = /*__LOGOS__*/;
// Player Affinity lists (data/players.json, made by scripts/affinity/unified.py): {ma, mt, wa, wt: [{n, a, f, c, p, ...}]}.
const PLAYERS = /*__PLAYERS__*/;
const DEF = {sims:1000, impFloor:0.05, impRamp:0.25, drawAuto:1, drawW0:60};
const STORE = 'football-suite-2627';
// In views that mix competitions (Live), fixture ids repeat, so a click looks up ids inside its own card first.
let scopeEl = null;
const $ = s => (scopeEl && scopeEl.isConnected && s[0] === '#' && scopeEl.querySelector(s)) || document.querySelector(s);
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pct = x => (x > 0 && x * 100 < 0.5 ? '<1' : Math.round(x * 100)) + '%';
const fmtDate = (iso, o = {weekday:'short', month:'short', day:'numeric'}) => new Date(iso + 'T12:00:00').toLocaleDateString('en-US', o);
const TODAY = new Date(); const todayISO = TODAY.toISOString().slice(0, 10);

let state = {view:'home', tab:{}, mw:{}, results:{}, draws:{}, settings:{}, suite:{peOutcome:2, peExact:3, motwW:0.5}, tmode:{}, favs:{}, status:{}, live:{}, motw:{}, ko:{}, heart:{}};
const COMP = {}, R = {};
let db = null, saveMode = 'device';
for (const k of ORDER) for (const t of DATA[k].teams) {
  if (!t.abbr) t.abbr = t.name.replace(/[^A-Za-zÀ-ÿ ]/g, '').split(' ').filter(w => !['FC', 'AFC', 'City', 'Town', 'United'].includes(w)).join('').slice(0, 3).toUpperCase();
  if (!t.color) t.color = '#8E8E93';
}
for (const k of ORDER) {
  const d = DATA[k], c = COMPS_CFG[k];
  COMP[k] = {teams:d.teams, fixtures:d.fixtures, params:d.params || {}, cfg:compCfg(k, d.params)};
  state.results[k] = {}; state.settings[k] = {}; state.tab[k] = 'week'; state.favs[k] = []; state.status[k] = {}; state.live[k] = {}; state.motw[k] = {}; state.ko[k] = {}; state.heart[k] = {};
}
state.draws.cup = {};
for (const k of ORDER) Object.assign(state.status[k], DATA[k].statusDefault || {});

function Sfor(k) {
  const p = COMP[k].params, s = state.settings[k] || {};
  return Object.assign({}, DEF, {halfLife:p.halfLife || 56, k:p.k || 10, h2h:p.h2h ?? 1, h2hK:p.h2hK || 10, rhoPrior:p.rhoPrior ?? -0.13, rhoW:p.rhoW || 300,
    beta:0.3, underdog:0.05, drawW:p.drawW ?? 1.05, haPrior:p.haPrior, scPrior:p.scPrior, baseW:p.baseW || 0}, s, {peOutcome:state.suite.peOutcome, peExact:state.suite.peExact, koRes:state.ko[k] || {}});
}
// ---------------------------------------------------------------- live clock
// A live entry is {h, a, ph, t, m0}: the phase ('1H' | 'HT' | '2H'), the time t (ms) of the last tap or typed
// minute, and the match minute m0 at that moment. The clock runs on from there, so taps at kick-off,
// half-time, the second-half restart and full time keep it right through late starts and long breaks.
// Stoppage time counts up as 45+N / 90+N. If a tap is missed the clock guesses (marked ~): half-time
// after 45+12 (taken to have started at 47'), the restart 15 minutes into the break (after waiting 20
// in case it runs long), and full time is asked for ("FT?") once the second half passes 90+15.
// Older entries without t ({h, a, min, ht}) keep their fixed minute.
const HT_AT = 47, HT_LEN = 15, HT_WAIT = 20, STOP_MAX = 12, FT_ASK = 15;
function clock(L, kt, now = Date.now()) {
  if (!L.t) {
    const stale = kt && now - kt > 150 * 6e4;
    return {ph:L.ht ? 'HT' : L.min > 45 ? '2H' : '1H', min:L.ht ? 45 : L.min, ht:!!L.ht, stale, label:stale ? 'FT?' : L.ht ? 'HT' : L.min + "'"};
  }
  const el = (now - L.t) / 6e4;
  let ph = L.ph, m = ph === 'HT' ? 0 : L.m0 + el, est = false;
  if (ph === '1H' && m >= 46 + STOP_MAX) { const b = m - HT_AT; est = true; if (b < HT_LEN) return {ph:'HT', min:45, ht:true, est, label:'HT'}; ph = '2H'; m = 46 + b - HT_LEN; }
  if (ph === 'HT') { if (el < HT_WAIT) return {ph, min:45, ht:true, label:'HT'}; ph = '2H'; m = 46 + el - HT_LEN; est = true; }
  const t = est ? '~' : '';
  if (ph === '1H') { const f = Math.max(1, Math.floor(m)); return {ph, min:Math.min(f, 45), label:f <= 45 ? `${t}${f}'` : `${t}45+${f - 45}'`}; }
  const f = Math.floor(m);
  if (f > 90 + FT_ASK) return {ph, min:90, est, stale:true, label:'FT?'};
  return {ph, min:Math.min(f, 90), est, label:f <= 90 ? `${t}${f}'` : `${t}90+${f - 90}'`};
}
const liveLabel = (k, f) => { const c = clockOf(k, f.id); return c ? c.label : f.live.min + "'"; };
const kickOf = (k, id) => { const f = R[k] && R[k].fx[id]; return f ? f.kt : null; };
const clockOf = (k, id) => { const L = state.live[k][id]; return L ? clock(L, kickOf(k, id)) : null; };
// What the model needs: score, minute (capped at 90), whether it's half-time, and red cards [home, away].
function liveFor(k) {
  const out = {};
  for (const [id, L] of Object.entries(state.live[k] || {})) { const c = clock(L, kickOf(k, +id)); out[id] = {h:L.h, a:L.a, min:c.min, ht:c.ht ? 1 : 0, rc:L.rc || [0, 0]}; }
  return out;
}
// Entry for a typed minute ("67", "45+2" counts as 45, "HT").
function liveAt(h, a, raw, now = Date.now()) {
  if (raw === 'HT') return {h, a, ph:'HT', t:now};
  const mn = Math.min(parseInt(raw, 10), 120);
  return mn <= 45 ? {h, a, ph:'1H', t:now, m0:Math.max(mn, 1)} : {h, a, ph:'2H', t:now, m0:mn};
}

// ---------------------------------------------------------------- model runs
// A full run (1,000 seasons) takes up to ~0.8 s for MLS on a laptop, longer on a phone. Full runs go to a
// background worker so taps never freeze the page. update(k) first does a quick 150-season run on the page
// so a change shows at once, then swaps in the full result when the worker sends it back.
const QUICK_SIMS = 150;
// A postponed mark stops counting once the fixture has a newer date than the one it was marked on
// (new marks store that date; older marks are plain 1 and give way when the ESPN sync moved the fixture).
const baseDate = (k, id) => DATA[k].fixtures[id][COMPS_CFG[k].cup ? 2 : 1];
function statusFor(k) {
  const st = state.status[k] || {}, mv = DATA[k].moved || {}, out = {};
  for (const [id, s] of Object.entries(st)) {
    const stale = s && s.p && !s.d && (typeof s.p === 'string' ? s.p !== baseDate(k, id) : mv[id] != null);
    if (stale) { out[id] = Object.assign({}, s); delete out[id].p; } else out[id] = s;
  }
  return out;
}
const runArgs = (k, sims) => ({results:state.results[k], draws:state.draws.cup, S:Object.assign(Sfor(k), sims ? {sims} : {}), status:statusFor(k), live:liveFor(k)});
function runModel(k, a) { return COMPS_CFG[k].cup ? MODEL.runCup(COMP[k], a.results, a.draws, a.S) : MODEL.run(COMP[k], a.results, a.S, a.status, a.live); }
let worker = null; const jobs = {}; let jobSeq = 0;
function workerMain() {
  const COMP = {};
  onmessage = e => {
    const m = e.data;
    if (m.init) { for (const [k, d] of Object.entries(m.init)) COMP[k] = Object.assign(d, {cfg:compCfg(k, d.params)}); return; }
    const a = m.a, r = COMPS_CFG[m.k].cup ? MODEL.runCup(COMP[m.k], a.results, a.draws, a.S) : MODEL.run(COMP[m.k], a.results, a.S, a.status, a.live);
    postMessage({k:m.k, id:m.id, r});
  };
}
function startWorker() {
  try {
    const src = ['src-config', 'src-model'].map(id => document.getElementById(id).textContent).join('\n') + '\n(' + workerMain + ')();';
    worker = new Worker(URL.createObjectURL(new Blob([src], {type:'text/javascript'})));
    worker.onmessage = e => { const {k, id, r} = e.data; if (jobs[k] !== id) return; delete jobs[k]; finish(k, r); bgRender(k); };
    worker.onerror = () => { worker = null; for (const k of Object.keys(jobs)) { delete jobs[k]; compute(k); } render(); };
    worker.postMessage({init:Object.fromEntries(ORDER.map(k => [k, {teams:COMP[k].teams, fixtures:COMP[k].fixtures, params:COMP[k].params}]))});
  } catch (e) { worker = null; }
}
// Full run in the background (or on the page if workers are unavailable, e.g. inside claude.ai).
function queueFull(k) {
  liveSig[k] = sigOf(k);
  if (!worker) { compute(k); return false; }
  jobs[k] = ++jobSeq; worker.postMessage({k, id:jobs[k], a:runArgs(k)}); return true;
}
// Keep live clocks and "Kicked off" buttons current (every 30 s while the page is open) and re-run the
// model every 2 minutes of match time so live odds follow the clock.
const liveSig = {};
const sigOf = k => JSON.stringify(Object.entries(liveFor(k)).map(([id, x]) => [id, x.h, x.a, x.ht, x.min >> 1, x.rc]));
function tick() {
  if (document.hidden) return;
  const now = Date.now(), v = state.view;
  let redraw = false;
  for (const k of ORDER) {
    if (!R[k] || !Object.keys(state.live[k] || {}).length) continue;
    redraw = true;
    if (!jobs[k] && liveSig[k] !== sigOf(k)) { if (worker) queueFull(k); else { liveSig[k] = sigOf(k); finish(k, runModel(k, runArgs(k, QUICK_SIMS)), true); } }
  }
  if (!redraw) redraw = ORDER.some(k => R[k] && (isHub(v) || v === k) && R[k].fx.some(f => !f.played && f.kt && now >= f.kt - 10 * 6e4 && now <= f.kt + 150 * 6e4));
  if (redraw) bgRender();
}
setInterval(tick, 30000);
document.addEventListener('visibilitychange', () => { if (!document.hidden) tick(); });
// A change the user just made: quick result now, full result shortly.
function update(k) { if (worker) { finish(k, runModel(k, runArgs(k, QUICK_SIMS)), true); queueFull(k); } else { liveSig[k] = sigOf(k); compute(k); } }
function compute(k) { finish(k, runModel(k, runArgs(k))); }
function finish(k, r, quick) {
  R[k] = r;
  const km = DATA[k].kick || {}, st = statusFor(k), mv = DATA[k].moved || {}, src = DATA[k].fixtures, mine = state.results[k] || {}, si = COMPS_CFG[k].cup ? 5 : 4;
  for (const f of R[k].fx) {
    // One of Kevin's entries that disagrees with the tracker's data (nightly ESPN sync): flag it, never replace it.
    const b = src[f.id], r = mine[f.id];
    f.baseDiff = f.played && r && Number.isInteger(b[si]) && (b[si] !== r[0] || b[si + 1] !== r[1]) ? [b[si], b[si + 1]] : null;
    const s = st[f.id] || {}, x = km[f.id];
    if (s.d) { f.date = s.d; f.kt = s.t ? new Date(s.d + 'T' + s.t).getTime() : null; f.moved = true; }
    else f.kt = x && x[1] ? Date.parse(x[0]) : null;
    if (!s.d && mv[f.id] != null && !f.played) f.moved = true;
    f.postponed = !f.played && !!s.p; f.awarded = f.played && !!s.aw;
    f.sortT = f.kt || Date.parse(f.date + 'T19:00:00Z');
  }
  R[k].quick = !!quick;
  if (!quick && lockMotw(k)) saveLocal();
  if (state.mw[k] == null) state.mw[k] = defaultRound(k);
}
function defaultRound(k) {
  const r = R[k];
  if (COMPS_CFG[k].cup) { const f = r.fx.find(x => !x.played && x.h != null && x.a != null) || r.fx.find(x => !x.played); return f ? f.round : 'Final'; }
  const counts = {}; r.fx.filter(f => !f.played).forEach(f => counts[f.mw] = (counts[f.mw] || 0) + 1);
  const keys = Object.keys(counts).map(Number).sort((a, b) => a - b); if (!keys.length) return Math.max(...r.fx.map(f => f.mw));
  const full = Math.max(...Object.values(counts)); return keys.find(x => counts[x] >= 0.6 * full);
}
function computeAll() {
  if (worker) { ORDER.forEach(queueFull); return; }
  const queue = [...ORDER];
  const step = () => { const k = queue.shift(); if (!k) return; compute(k); if (isHub(state.view) || state.view === k) render(); setTimeout(step, 0); };
  step();
}
// Re-render for a background change (worker result, cloud sync, clock tick) without disturbing the reader:
// the first card on screen stays put, and an open score entry keeps its typed values and focus.
// Background changes arrive in bursts (twelve simulations finishing at start-up), so they're batched: one redraw per burst.
let bgTimer = 0;
function bgRender(k) {
  if (k && state.view !== k && !isHub(state.view)) { renderStatus(); return; }
  if (!bgTimer) bgTimer = setTimeout(() => { bgTimer = 0; bgRenderNow(); }, 250);
}
function bgRenderNow() {
  const open = [...document.querySelectorAll('#main .entry:not([hidden])')];
  const vals = open.flatMap(e => [...e.querySelectorAll('input[id],select[id]')]).map(x => [x.id, x.type === 'checkbox' ? x.checked : x.value]);
  const foc = document.activeElement && document.activeElement.id;
  const first = [...document.querySelectorAll('#main [data-fx]')].find(x => x.getBoundingClientRect().bottom > 0);
  anchor = first ? {key:first.dataset.fx, top:first.getBoundingClientRect().top} : null;
  render();
  open.forEach(e => { const x = document.getElementById(e.id); if (x) x.hidden = false; });
  vals.forEach(([id, v]) => { const x = document.getElementById(id); if (x) { if (x.type === 'checkbox') x.checked = v; else x.value = v; } });
  if (foc) { const x = document.getElementById(foc); if (x && x.closest('#main')) x.focus({preventScroll:true}); }
}

// ---------------------------------------------------------------- persistence
function loadLocal() {
  try { const j = JSON.parse(localStorage.getItem(STORE) || 'null'); if (j) { Object.assign(state.results, j.results || {}); Object.assign(state.settings, j.settings || {}); Object.assign(state.favs, j.favs || {}); Object.assign(state.status, j.status || {}); Object.assign(state.live, j.live || {}); Object.assign(state.motw, j.motw || {}); Object.assign(state.ko, j.ko || {}); Object.assign(state.heart, j.heart || {}); state.draws = j.draws || {cup:{}}; state.suite = Object.assign(state.suite, j.suite || {}); } } catch (e) {}
}
function saveLocal() { try { localStorage.setItem(STORE, JSON.stringify({results:state.results, settings:state.settings, draws:state.draws, suite:state.suite, favs:state.favs, status:state.status, live:state.live, motw:state.motw, ko:state.ko, heart:state.heart})); } catch (e) {} }
// ---------------------------------------------------------------- cloud sync
// One document per competition (plus "suite"), fields stored as JSON strings. The same layout is used
// by every backend: claude.ai artifact db, Firebase Firestore (users/{uid}/trackers/{key}) or none.
let backend = null, authState = 'none';
function docFor(k) {
  if (k === 'suite') return {suite:JSON.stringify(state.suite), updated:Date.now()};
  return {results:JSON.stringify(state.results[k] || {}), settings:JSON.stringify(state.settings[k] || {}), draws:JSON.stringify(k === 'cup' ? state.draws.cup : {}),
    favs:JSON.stringify(state.favs[k] || []), status:JSON.stringify(state.status[k] || {}), live:JSON.stringify(state.live[k] || {}),
    motw:JSON.stringify(state.motw[k] || {}), ko:JSON.stringify(state.ko[k] || {}), heart:JSON.stringify(state.heart[k] || {}), updated:Date.now()};
}
const docSig = d => JSON.stringify(Object.assign({}, d, {updated:0}));
function applyDoc(k, d) {
  try {
    if (k === 'suite') { state.suite = Object.assign(state.suite, JSON.parse(d.suite || '{}')); return true; }
    if (!ORDER.includes(k)) return false;
    state.results[k] = JSON.parse(d.results || '{}'); state.settings[k] = JSON.parse(d.settings || '{}');
    if (k === 'cup') state.draws.cup = JSON.parse(d.draws || '{}');
    if (d.favs) state.favs[k] = JSON.parse(d.favs); if (d.status) state.status[k] = JSON.parse(d.status);
    if (d.live) state.live[k] = JSON.parse(d.live); if (d.motw) state.motw[k] = JSON.parse(d.motw); if (d.ko) state.ko[k] = JSON.parse(d.ko); if (d.heart) state.heart[k] = JSON.parse(d.heart);
    return true;
  } catch (e) { return false; }
}
async function save(k) {
  saveLocal();
  if (backend) {
    try { if (k && k !== 'suite') await backend.set(k, docFor(k)); await backend.set('suite', docFor('suite')); saveMode = backend.name; }
    catch (e) { saveMode = 'device'; }
  }
  renderStatus();
}
async function claudeBackend() {
  if (!window.claude || !window.claude.use) return null;
  const d = await window.claude.use('db'); if (!d) return null;
  return { name:'claude', get: async k => { const s = await d.doc('trackers/' + k).get(); return s.exists ? s.data() : null; },
    set: (k, v) => d.doc('trackers/' + k).set(v), watch: null };
}
async function firebaseBackend() {
  if (!window.firebase || !window.FIREBASE_CONFIG) return null;
  if (!firebase.apps.length) firebase.initializeApp(window.FIREBASE_CONFIG);
  const auth = firebase.auth(), fs = firebase.firestore();
  try { await fs.enablePersistence({synchronizeTabs:true}); } catch (e) {}
  try { await auth.getRedirectResult(); } catch (e) {}
  const user = await new Promise(res => { const off = auth.onAuthStateChanged(u => { off(); res(u); }); });
  if (!user) { authState = 'signed-out'; return null; }
  authState = 'signed-in';
  const col = fs.collection('users').doc(user.uid).collection('trackers');
  return { name:'google', user,
    get: async k => { const s = await col.doc(k).get(); return s.exists ? s.data() : null; },
    set: (k, v) => col.doc(k).set(v),
    watch: cb => col.onSnapshot(snap => snap.docChanges().forEach(ch => { if (!ch.doc.metadata.hasPendingWrites) cb(ch.doc.id, ch.doc.data()); })) };
}
async function signIn() {
  const auth = firebase.auth(), p = new firebase.auth.GoogleAuthProvider();
  try { await auth.signInWithPopup(p); } catch (e) { if (/popup/.test(e.code || '')) { await auth.signInWithRedirect(p); return; } alert('Sign-in failed: ' + (e.message || e)); return; }
  connect();
}
async function signOut() { try { await firebase.auth().signOut(); } catch (e) {} backend = null; authState = 'signed-out'; saveMode = 'device'; render(); }
async function connect() {
  try {
    backend = (await claudeBackend()) || (await firebaseBackend());
    if (!backend) { renderStatus(); return; }
    const keys = [...ORDER, 'suite'], docs = await Promise.all(keys.map(k => backend.get(k)));
    const found = docs.filter(Boolean).length;
    if (!found) {
      // first sign-in: seed from the bundled export if this device has nothing yet, then upload
      if (window.SEED && !localStorage.getItem(STORE + ':seeded')) { for (const [k, d] of Object.entries(window.SEED)) applyDoc(k, d); try { localStorage.setItem(STORE + ':seeded', '1'); } catch (e) {} }
      syncFavs(); saveLocal();
      for (const k of keys) await backend.set(k, docFor(k));
    } else {
      keys.forEach((k, i) => { if (docs[i]) applyDoc(k, docs[i]); });
      syncFavs(); saveLocal();
    }
    saveMode = backend.name;
    ORDER.forEach(k => queueFull(k)); bgRender();
    if (backend.watch) backend.watch((k, d) => {
      if (docSig(d) === docSig(docFor(k))) return;
      if (applyDoc(k, d)) { saveLocal(); if (k === 'suite') ORDER.forEach(c => queueFull(c)); else update(k); bgRender(k === 'suite' ? null : k); }
    });
  } catch (e) { console.error(e); saveMode = 'device'; renderStatus(); }
}

// ---------------------------------------------------------------- chrome
// Views that aren't a competition: Home, Live and the overall Affinity ranking.
const isHub = v => v === 'home' || v === 'rank' || v === 'live';
function setBrand(k) {
  if (isHub(k)) k = 'home';
  const b = k === 'home' ? {head:'#1A1033', accent:'#7C5CFF', glow:'rgba(124,92,255,.5)', tag:'#B9A6FF'}
    : COMPS_CFG[k].brand;
  // The page is washed in the competition's colour (Home, Live and Affinity stay neutral graphite).
  const r = document.documentElement.style; r.setProperty('--tint', k === 'home' ? '#3A3A3C' : b.accent); r.setProperty('--brand', k === 'home' ? 'rgba(235,235,245,.6)' : b.accent);
  const top = '#' + [0, 2, 4].map(j => Math.round(parseInt((k === 'home' ? '#3A3A3C' : b.accent).slice(1 + j, 3 + j), 16) * (k === 'home' ? 0.7 : 0.42)).toString(16).padStart(2, '0')).join('');
  r.setProperty('--top', top); const m = document.querySelector('meta[name="theme-color"]'); if (m) m.content = top;
}
function tabShort(k, t, l) {
  const S = {'Matchweek':'Matches', 'Matchday':'Matches', 'Round':'Matches', 'Week':'Matches', 'Rounds':'Matches', 'Conferences':'Table', 'Groups':'Table', 'Clubs left':'Left', 'Trophy race':'Race', 'Your Affinity':'Affinity', "Pick 'em":'Picks'};
  return S[l] || l;
}
function renderChrome() {
  const k = state.view, hub = isHub(k), cup = !hub && COMPS_CFG[k].cup;
  setBrand(k);
  $('#title').innerHTML = k === 'live' ? 'Live<span class="season">Now</span>' : k === 'rank' ? 'Affinity<span class="season">Ranking</span>' : hub ? 'Football Tracker<span class="season">Suite</span>' : `${esc(COMPS_CFG[k].name)}<span class="season">${esc(COMPS_CFG[k].season)}</span>`;
  const reg = regionOf(k); if (reg) lastIn[reg.key] = k;
  $('#regions').innerHTML = `<button data-view="home" aria-pressed="${k === 'home'}">Home</button><button data-view="live" aria-pressed="${k === 'live'}" class="nav-live">${liveNow().length ? '<span class="live-dot"></span>' : ''}Live</button>` +
    REGIONS.map(r => `<button data-region="${r.key}" aria-pressed="${reg === r}">${esc(r.name)}</button>`).join('') +
    `<button data-view="rank" aria-pressed="${k === 'rank'}">Affinity</button>`;
  const chip = c => { const [f, s] = CHIP[c] || [COMPS_CFG[c].name]; return s ? `<span class="nm-full">${esc(f)}</span><span class="nm-short">${esc(s)}</span>` : esc(f); };
  $('#comps').innerHTML = reg ? reg.comps.map(c => `<button data-view="${c}" aria-pressed="${k === c}" aria-label="${esc(COMPS_CFG[c].name)}"><i style="--c:${DOT[c]}"></i>${chip(c)}</button>`).join('') : '';
  $('#comps').hidden = !reg;
  { const sel = $('#comps').querySelector('[aria-pressed="true"]'); if (sel) $('#comps').scrollLeft = Math.max(0, sel.offsetLeft + sel.offsetWidth - $('#comps').clientWidth + 4); }
  $('#regions').style.setProperty('--dot', reg ? DOT[k] : '#fff');
  const tabs = hub ? [] : cup ? [['week', 'Rounds'], ['table', 'Clubs left'], ['races', 'Trophy race'], ['clubs', 'Your Affinity'], ['picks', "Pick 'em"], ['settings', 'Settings']]
    : [['week', COMPS_CFG[k].round], ['table', COMPS_CFG[k].grouped ? (['mls', 'usl'].includes(k) ? 'Conferences' : 'Groups') : 'Table'], ['races', 'Races'],
       ...(['nwsl', 'mls', 'usl'].includes(k) ? [['bracket', 'Playoffs']] : []), ['clubs', 'Clubs'], ['picks', "Pick 'em"], ['settings', 'Settings']];
  $('#tabs').innerHTML = tabs.map(([t, l]) => t === 'settings'
    ? `<button role="tab" data-tab="${t}" aria-selected="${state.tab[k] === t}" aria-label="Settings" title="Settings" class="gear"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M19.4 13a7.6 7.6 0 0 0 0-2l2-1.6-2-3.4-2.4 1a7.3 7.3 0 0 0-1.7-1l-.4-2.6h-4l-.4 2.6a7.3 7.3 0 0 0-1.7 1l-2.4-1-2 3.4 2 1.6a7.6 7.6 0 0 0 0 2l-2 1.6 2 3.4 2.4-1c.5.4 1.1.7 1.7 1l.4 2.6h4l.4-2.6c.6-.3 1.2-.6 1.7-1l2.4 1 2-3.4-2-1.6ZM12 15.5A3.5 3.5 0 1 1 12 8.5a3.5 3.5 0 0 1 0 7Z"/></svg></button>`
    : `<button role="tab" data-tab="${t}" aria-selected="${state.tab[k] === t}" aria-label="${esc(l)}">${tabShort(k, t, l) === l ? esc(l) : `<span class="nm-full">${esc(l)}</span><span class="nm-short">${esc(tabShort(k, t, l))}</span>`}</button>`).join('');
  // The tab bar scrolls sideways on a phone when a league has many tabs: keep the selected one in view.
  { const nav = $('#tabs'), sel = nav.querySelector('[aria-selected="true"]');
    if (sel && sel.offsetLeft + sel.offsetWidth > nav.scrollLeft + nav.clientWidth) nav.scrollLeft = sel.offsetLeft + sel.offsetWidth - nav.clientWidth + 4;
    else if (sel && sel.offsetLeft < nav.scrollLeft) nav.scrollLeft = Math.max(0, sel.offsetLeft - 4); }
  $('#tabs').hidden = hub;
  // Slim bar that slides in once the header's nav scrolls away: regions on Home, else competition + sections.
  $('#topbar').innerHTML = hub ? `<nav class="regions topbar-regions">${$('#regions').innerHTML}</nav>`
    : `<button class="topbar-comp" data-top="1" aria-label="${esc(COMPS_CFG[k].name)}: back to top"><i style="--c:${DOT[k]}"></i>${esc(ABBR[k])}</button><nav class="tabs topbar-tabs" role="tablist" aria-label="Sections">${[...$('#tabs').children].filter(b => !b.classList.contains('gear')).map(b => b.outerHTML).join('')}</nav>`;
  miniCheck();
}
function miniCheck() {
  const nav = isHub(state.view) ? $('#regions') : $('#tabs'), on = nav.getBoundingClientRect().bottom < 0, m = $('#topbar');
  if (m.classList.contains('on') !== on) { m.classList.toggle('on', on); m.inert = !on; }
}
let miniRaf = 0;
addEventListener('scroll', () => { if (!miniRaf) miniRaf = requestAnimationFrame(() => { miniRaf = 0; miniCheck(); }); }, {passive:true});
const regionOf = k => REGIONS.find(r => r.comps.includes(k));
const lastIn = {};
function renderStatus() {
  const k = state.view;
  let s;
  if (k === 'rank') s = rankMode === 'players' && PLAYERS.ma ? `Players ranked by your Affinity` : `<b>${rankList().length}</b> clubs and nations, ranked by Affinity`;
  else if (k === 'live') { const a = liveNow().length, b = kickedOff().length; s = a || b ? `<b>${a}</b> live${b ? `, <b>${b}</b> kicked off without a live score` : ''}` : 'Nothing live right now'; }
  else if (k === 'home') {
    const done = ORDER.filter(c => R[c]).length;
    s = done < ORDER.length ? `Crunching ${done} of ${ORDER.length} competitions…` : `${ORDER.length} competitions, live`;
  } else if (!R[k]) s = 'Crunching the numbers…';
  else {
    const r = R[k], last = r.fx.filter(f => f.played).reduce((m, f) => f.date > m ? f.date : m, '');
    s = COMPS_CFG[k].cup ? `<b>${r.alive.length}</b> clubs left of 92` : `<b>${r.nPlayed}</b> of ${r.fx.length} matches played${last ? `, results through <b>${fmtDate(last, {month:'long', day:'numeric'})}</b>` : ''}`;
    if (r.quick) s += ' · <span class="updating">updating odds…</span>';
  }
  const sv = saveMode === 'google' ? `Synced to ${esc(backend && backend.user && backend.user.email || 'your Google account')}` : saveMode === 'claude' ? 'Scores save to your Claude account'
    : authState === 'signed-out' ? 'Saved on this device · <button class="linkish" data-signin="1">Sign in to sync</button>' : 'Scores save on this device';
  $('#status').innerHTML = `${s} <span class="save-state">${sv}</span>`;
}
function render() {
  renderChrome(); renderStatus();
  const k = state.view;
  let html;
  if (k === 'home') html = viewHome();
  else if (k === 'rank') html = viewRank();
  else if (k === 'live') html = viewLive();
  else if (!R[k]) html = '<div class="loading">Crunching the numbers…</div>';
  else if (COMPS_CFG[k].cup) html = {week:cupRounds, table:cupLeft, races:cupRaces, clubs:viewClubs, picks:viewPicks, settings:viewSettings}[state.tab[k]](k);
  else html = {week:viewWeek, table:viewTable, races:viewRaces, clubs:viewClubs, picks:viewPicks, settings:viewSettings, bracket:viewBracket}[state.tab[k]](k);
  if (html !== lastHtml) { morph($('#main'), html); lastHtml = html; }
  if (anchor) { holdAnchor(anchor); const a = anchor; anchor = null; requestAnimationFrame(() => holdAnchor(a)); }
}
// Patch the page in place rather than replacing it: unchanged rows, logos and images keep their DOM nodes,
// so a background update (a simulation finishing, a sync, the live clock) doesn't redraw or reload them.
let lastHtml = null;
function morph(el, html) { const t = document.createElement('template'); t.innerHTML = html; morphKids(el, t.content); }
// Children are paired by position, except match rows, which pair by their match (data-fx) so a list that gains or
// loses a row in the middle moves the existing rows instead of rewriting every row below.
function morphKids(a, b) {
  const keyOf = n => n.nodeType === 1 ? n.getAttribute('data-fx') : null;
  const pool = new Map(); for (const x of a.childNodes) { const k = keyOf(x); if (k) pool.set(k, x); }
  let cur = a.firstChild;
  for (const y of [...b.childNodes]) {
    const k = keyOf(y), x = k ? pool.get(k) : cur && !keyOf(cur) ? cur : null;
    if (!x) { a.insertBefore(y, cur); continue; }
    if (k) pool.delete(k);
    if (x === cur) cur = cur.nextSibling; else a.insertBefore(x, cur);
    morphNode(a, x, y);
  }
  while (cur) { const n = cur.nextSibling; cur.remove(); cur = n; }
}
function morphNode(parent, x, y) {
  // A different kind of node, or a changed form field (its typed value lives outside the markup): swap it whole.
  if (x.nodeType !== y.nodeType || x.nodeName !== y.nodeName || (/^(INPUT|SELECT|TEXTAREA)$/.test(x.nodeName) && !x.isEqualNode(y))) { parent.replaceChild(y, x); return; }
  if (x.nodeType !== 1) { if (x.nodeValue !== y.nodeValue) x.nodeValue = y.nodeValue; return; }
  if (x.isEqualNode(y)) return;
  for (const {name} of [...x.attributes]) if (!y.hasAttribute(name) && !(name === 'open' && x.nodeName === 'DETAILS')) x.removeAttribute(name);
  for (const {name, value} of [...y.attributes]) if (x.getAttribute(name) !== value) x.setAttribute(name, value);
  morphKids(x, y);
}
// Keep the match card you just tapped at the same spot on screen after a re-render,
// so saving or updating a score doesn't make the page jump.
let anchor = null;
function holdAnchor(a) {
  const els = [...document.querySelectorAll(`#main [data-fx="${a.key}"]`)]; if (!els.length) return;
  const el = els.reduce((b, x) => Math.abs(x.getBoundingClientRect().top - a.top) < Math.abs(b.getBoundingClientRect().top - a.top) ? x : b);
  const dy = el.getBoundingClientRect().top - a.top; if (Math.abs(dy) > 1) window.scrollBy(0, dy);
}

// ---------------------------------------------------------------- shared bits
const T = k => COMP[k].teams;
const nm = (k, i) => i == null ? 'TBD' : T(k)[i].short || T(k)[i].name;
const full = (k, i) => i == null ? 'To be drawn' : T(k)[i].name;
const dual = (k, i) => `<span class="nm-full">${esc(T(k)[i].name)}</span><span class="nm-short">${esc(nm(k, i))}</span>`;
const fmtTime = ms => new Date(ms).toLocaleTimeString('en-US', {hour:'numeric', minute:'2-digit'});
const fmtDateK = (f, o) => f.kt ? new Date(f.kt).toLocaleDateString('en-US', o || {weekday:'short', month:'short', day:'numeric'}) : fmtDate(f.date, o);
const whenLabel = f => f.postponed ? 'Postponed · new date TBA' : `${fmtDateK(f)} · ${f.kt ? fmtTime(f.kt) : 'time TBC'}`;
const isPast = f => f.kt ? f.kt < Date.now() : f.date < todayISO;
const tvLabel = k => DATA[k].tv + (k === 'epl' ? ' (channel announced weekly)' : '');
// A club "crest": a disc in the club colour with its short code (the app has no logos). Text flips dark on light colours.
const inkOn = hex => { const n = parseInt((hex || '#48484A').slice(1), 16), [r, g, b] = [n >> 16, n >> 8 & 255, n & 255].map(v => (v /= 255) <= 0.04 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4); return 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.36 ? '#000' : '#fff'; };
const logoFor = (name, k) => (LOGOS[k] || {})[name] || LOGOS.flags[name] || Object.values(LOGOS).map(m => m[name]).find(Boolean);
// A logo that fails to load falls back to the colour disc with the short code.
const logoImg = (src, cls) => `<img class="${cls}" src="${src}" alt="" decoding="async" onerror="this.parentNode.classList.add('nologo');this.remove()">`;
const crest = (k, i, size) => { if (i == null) return `<i class="crest tbd" style="--cs:${size || 40}px">?</i>`; const t = T(k)[i], c = t.color || '#48484A', a = t.abbr || (t.short || t.name).replace(/[^A-Za-z]/g, '').slice(0, 3).toUpperCase(), lg = logoFor(t.name, k);
  return `<i class="crest${lg ? ' has-logo' + (LOGOS.flags[t.name] ? ' flag' : '') : ''}${isFav(k, i) ? ' fav' : ''}" style="--cs:${size || 40}px;--tc:${c};--ti:${inkOn(c)}" aria-hidden="true"><span>${esc(a)}</span>${lg ? logoImg(lg, 'cl') : ''}</i>`; };
// Small logo (or colour dot) before a name in tables and lists.
// A followed club gets a small gold star on its logo instead of one beside the name, so names keep their width.
const nchip = (name, color, k, fav) => { const lg = logoFor(name, k), f = fav ? ' fav' : ''; return lg ? `<i class="tchip has-logo${LOGOS.flags[name] ? ' flag' : ''}${f}" style="--tc:${color || '#48484A'}">${logoImg(lg, 'tl')}</i>` : color ? `<i class="tchip${f}" style="--tc:${color}"></i>` : ''; };
const tchip = (k, i) => i != null ? nchip(T(k)[i].name, T(k)[i].color, k, isFav(k, i)) : '';
const isFav = (k, i) => i != null && (state.favs[k] || []).includes(i);
const star = (k, i) => isFav(k, i) ? '<span class="star" aria-label="Your club">★</span>' : '';
const hasFav = (k, f) => isFav(k, f.h) || isFav(k, f.a);
const roundKey = (k, f) => COMPS_CFG[k].cup ? (f.round.startsWith('Semi') ? 'Semi-finals' : f.round) : String(f.mw);
const roundList = (k, key) => R[k].fx.filter(x => roundKey(k, x) === key && !(COMPS_CFG[k].cup && x.round.endsWith('leg 1')));
// Match of the week is fixed as of the start of the round: it locks the first time a match in the round
// kicks off, goes live or gets a result, using the importance at that moment.
function lockMotw(k, onlyKey) {
  if (!R[k]) return false; const locks = state.motw[k] = state.motw[k] || {}; let changed = false;
  const keys = onlyKey ? [onlyKey] : [...new Set(R[k].fx.map(f => roundKey(k, f)))];
  for (const key of keys) {
    if (locks[key] !== undefined) continue;
    const list = roundList(k, key);
    const started = onlyKey || list.some(f => f.played || f.live || (f.kt && f.kt < Date.now()));
    if (!started) continue;
    const m = motwOf(list); locks[key] = m ? m.id : null; changed = true;
  }
  return changed;
}
function motwFor(k, list) {
  if (!list.length) return null; const key = roundKey(k, list[0]), lk = (state.motw[k] || {})[key];
  if (lk !== undefined) return lk === null ? null : R[k].fx[lk];
  return motwOf(list);
}
// Headline score: blend of importance (what's at stake) and competitiveness (how evenly matched, 1 - |home win - away win|)
const compet = f => f.pH != null ? 1 - Math.abs((f.live || f).pH - (f.live || f).pA) : 0;
const headline = f => { const w = state.suite.motwW ?? 0.5; return w * (f.importance || 0) + (1 - w) * compet(f); };
function motwOf(list) { let best = null; for (const f of list) if (!f.played && !f.postponed && f.importance !== undefined && (!best || headline(f) > headline(best))) best = f; return best; }
const favLabel = (k, f) => f.favored === 'D' ? 'Draw' : nm(k, f.favored === 'H' ? f.h : f.a);
function impMeter(v) { return `<span class="imp" title="Match importance">Importance <span class="imp-track"><span class="imp-fill" style="width:${Math.round(v * 100)}%"></span></span> <b class="num">${v.toFixed(2)}</b></span>`; }

const reds = n => n ? `<span class="rcs" aria-label="${n} red card${n > 1 ? 's' : ''}">${'<i class="rc"></i>'.repeat(n)}</span>` : '';
// One-tap live buttons: goal, red card, the next match event, red card, goal.
function liveBtns(k, f) {
  const c = clockOf(k, f.id) || {ph:f.live.ht ? 'HT' : '2H'};
  // while the clock is guessing past a missed tap, keep offering the restart until the 70th minute
  const [ev, lab] = c.stale ? ['ft', `FT ${f.live.h}–${f.live.a}?`] : c.ph === '1H' ? ['ht', 'Half-time']
    : c.ph === 'HT' || (c.est && c.min < 70) ? ['sh', '2nd half'] : ['ft', 'Full time'];
  const ab = i => esc(T(k)[i].abbr || nm(k, i));
  return `<div class="live-ctl"><button class="btn ghost" data-ev="gh" data-id="${f.id}" aria-label="Goal ${esc(full(k, f.h))}">+1 ${ab(f.h)}</button>
    <button class="btn ghost rc-btn" data-ev="rh" data-id="${f.id}" aria-label="Red card ${esc(full(k, f.h))}"><i class="rc"></i></button>
    <button class="btn ${c.stale || ev === 'ft' ? 'primary' : 'live-btn'}" data-ev="${ev}" data-id="${f.id}">${lab}</button>
    <button class="btn ghost rc-btn" data-ev="ra" data-id="${f.id}" aria-label="Red card ${esc(full(k, f.a))}"><i class="rc"></i></button>
    <button class="btn ghost" data-ev="ga" data-id="${f.id}" aria-label="Goal ${esc(full(k, f.a))}">+1 ${ab(f.a)}</button></div>`;
}
// Compact card for the Live tab (about 150px, so 4-5 fit on a phone): competition, the score bug with red cards,
// live odds in one bar, one-tap events. Tap the bug for the full card. No Affinity or pick 'em here (their own tabs).
function liveCard(k, f) {
  const L = f.live, P = L || f, t = i => T(k)[i], ab = i => esc(t(i).abbr || nm(k, i));
  const seg = (p, cls) => `<span class="${cls}" style="flex:${p}">${p >= 0.14 ? pct(p) : ''}</span>`;
  const bar = f.pH != null ? `<div class="lc-bar num" aria-label="Win chances ${pct(P.pH)} home, ${pct(P.pD)} draw, ${pct(P.pA)} away${L ? ', live' : ''}">${seg(P.pH, 'h')}${seg(P.pD, 'd')}${seg(P.pA, 'a')}</div>` : '';
  let ctl = '';
  if (L) ctl = liveBtns(k, f);
  else if (COMPS_CFG[k].cup) ctl = `<div class="live-ctl one"><button class="btn ghost" data-go="${k}:${f.id}">Enter the result</button></div>`;
  else if (!f.played && !f.postponed) ctl = `<div class="live-ctl one"><button class="btn live-btn" data-ev="ko" data-id="${f.id}">${Date.now() - f.kt > 5 * 6e4 ? `Live now (clock from ${fmtTime(f.kt)})` : 'Kicked off'}</button></div>`;
  const team = (sd, i) => `<span class="mr-t ${sd}">${crest(k, i)}<span class="mr-n">${esc(nm(k, i))}${L ? reds(L.rc[sd === 'h' ? 0 : 1]) : ''}</span></span>`;
  return `<article data-fx="${k}:${f.id}" class="match mrow lc ${L ? 'is-live' : ''} ${hasFav(k, f) ? 'is-fav' : ''}" style="--hc:${t(f.h).color};--ac:${t(f.a).color}">
    <div class="mr-cap"><button class="live-comp" data-go="${k}:${f.id}" style="--c:${DOT[k]}"><i></i>${esc(COMPS_CFG[k].name)}</button></div>
    <div class="mr" role="button" tabindex="0" data-go="${k}:${f.id}" aria-label="Open ${esc(full(k, f.h))} v ${esc(full(k, f.a))}">
      ${team('h', f.h)}<span class="mr-v sc num">${L ? L.h : ''}</span><span class="mr-c">${L ? `<b class="mr-live num"><span class="live-dot"></span>${liveLabel(k, f)}</b>${(c => c.ht || c.stale ? '' : `<span class="mr-adj"><button data-ev="mm" data-id="${f.id}" aria-label="Clock back a minute">‹</button><button data-ev="mp" data-id="${f.id}" aria-label="Clock forward a minute">›</button></span>`)(clockOf(k, f.id) || {})}` : `<b class="num">${fmtTime(f.kt)}</b><small>Kicked off</small>`}</span><span class="mr-v sc num">${L ? L.a : ''}</span>${team('a', f.a)}</div>
    ${bar}${ctl}${heartRow(k, f)}</article>`;
}
// Heart over head: on a neutral match (none of the followed clubs), once it's under way, who you found yourself
// pulling for and a note on players or coaches you enjoyed or didn't. Saved per competition, synced like results.
const isNeutral = (k, f) => f.h != null && f.a != null && !hasFav(k, f) && (f.played || f.live || (f.kt && Date.now() >= f.kt));
function heartRow(k, f) {
  if (!isNeutral(k, f)) return '';
  const e = (state.heart[k] || {})[f.id] || {}, ab = i => esc(T(k)[i].abbr || nm(k, i));
  const b = (v, l) => `<button class="hp" data-heart="${f.id}:${v}" aria-pressed="${e.s === v}">${l}</button>`;
  return `<div class="heart"><span class="hl">Pulled for</span>${b('H', ab(f.h))}${b('A', ab(f.a))}${b('N', 'Neither')}
    ${e.s ? `<div class="hn"><input id="hn-${f.id}" value="${esc(e.note || '')}" placeholder="Players or coaches you enjoyed (or didn't)" aria-label="Note on players or coaches"><button class="btn ghost" data-heartnote="${f.id}">${e.note ? 'Update' : 'Save'}</button></div>` : ''}</div>`;
}
function matchCard(k, f, motw) {
  const fin = f.played, cup = COMPS_CFG[k].cup, known = f.h != null && f.a != null, rated = f.pH != null;
  let foot = '';
  if (fin) {
    const bits = [];
    if (f.baseDiff) bits.push(`<span class="res-row"><span>Tracker data <b>${f.baseDiff[0]}–${f.baseDiff[1]}</b></span><span class="chip fav">Differs from yours</span></span>`);
    foot = bits.length ? `<div class="res-stack">${bits.join('')}</div>` : '';
  }
  // Live controls: goals, red cards and the next match event, one tap each. Before a match, "Kicked off" appears from
  // 10 minutes before the listed kickoff; tapped more than 5 minutes after it, the clock starts at kickoff.
  let liveCtl = '';
  if (!cup && known && !fin && !f.postponed) {
    const now = Date.now();
    if (f.live) liveCtl = liveBtns(k, f);
    else if (f.kt && now >= f.kt - 10 * 6e4 && now <= f.kt + 150 * 6e4) {
      const late = now - f.kt > 5 * 6e4;
      liveCtl = `<div class="live-ctl one"><button class="btn live-btn" data-ev="ko" data-id="${f.id}">${late ? `Live now (clock from ${fmtTime(f.kt)})` : 'Kicked off'}</button></div>`;
    }
  }
  const canDraw = cup && !known && ['Quarter-final', 'Semi-final leg 1', 'Final'].includes(f.round) && f.round !== 'Final';
  const drawUI = canDraw ? drawPicker(k, f) : '';
  const canEnter = known && !(cup && f.round.startsWith('Semi-final') && false);
  const needPens = cup && !['Semi-final leg 1'].includes(f.round);
  const fcol = isFav(k, f.h) ? T(k)[f.h].color : isFav(k, f.a) ? T(k)[f.a].color : null;
  const tc = f.h != null && f.a != null && T(k)[f.h].color ? `style="--hc:${T(k)[f.h].color};--ac:${T(k)[f.a].color}${fcol ? ';--fc:' + fcol : ''}"` : '';
  // Apple Sports-style row: crest and name either side, win chances (or the score) inside them, kickoff or status in the middle.
  const side = s => {
    const team = s === 'h' ? f.h : f.a;
    if (f.live) return `<span class="mr-v sc num">${s === 'h' ? f.live.h : f.live.a}</span>`;
    if (fin) { const me = s === 'h' ? f.hs : f.as, op = s === 'h' ? f.as : f.hs, lose = me < op || (me === op && f.pens != null && f.pens !== team); return `<span class="mr-v sc num ${lose ? 'lose' : ''}">${me}</span>`; }
    const v = cup && f.advH != null ? (s === 'h' ? f.advH : 1 - f.advH) : rated ? (s === 'h' ? f.pH : f.pA) : null;
    return `<span class="mr-v num">${v == null ? '' : pct(v)}</span>`;
  };
  const mid = f.live ? `<b class="mr-live num"><span class="live-dot"></span>${liveLabel(k, f)}</b><small>Draw ${pct(f.live.pD)}</small>`
    : fin ? `<b>Final</b><small>${f.awarded ? 'Awarded' : f.pens != null && f.hs === f.as && !(f.round || '').endsWith('leg 1') ? esc(nm(k, f.pens)) + ' on pens' : ''}</small>`
    : f.postponed ? '<b>Postponed</b><small>New date TBA</small>'
    : `<b class="num">${f.kt ? fmtTime(f.kt) : 'TBC'}</b><small>${cup && f.advH != null ? 'to go through' : rated ? 'Draw ' + pct(f.pD) : known ? '' : 'Awaiting draw'}</small>`;
  const team = (s, i) => `<span class="mr-t ${s}">${crest(k, i)}<span class="mr-n">${i == null ? 'TBD' : esc(nm(k, i))}${f.live ? reds(f.live.rc[s === 'h' ? 0 : 1]) : ''}</span></span>`;
  const cap = [motw ? `<span class="cap-motw">${motw}</span>` : '', hasFav(k, f) ? '<span class="cap-fav">★ Your club</span>' : '',
    cup ? esc(f.round) + (f.round.startsWith('Semi') ? '' : ` ${f.tie}`) : '', f.moved && !f.played ? 'Rescheduled' : ''].filter(Boolean).join('<i>·</i>');
  return `<article ${tc} data-fx="${k}:${f.id}" class="match mrow ${f.live ? 'is-live' : ''} ${hasFav(k, f) ? 'is-fav' : ''} ${motw ? 'is-motw' : ''} ${f.postponed ? 'is-pp' : ''} ${fin ? 'is-fin' : ''}">
    ${cap ? `<div class="mr-cap">${cap}</div>` : ''}
    <div class="mr" ${rated || fin ? `role="button" tabindex="0" data-open="${f.id}" aria-label="Open ${esc(full(k, f.h))} v ${esc(full(k, f.a))}"` : ''}>
      ${team('h', f.h)}${side('h')}<span class="mr-c">${mid}${canEnter ? `<button class="enter" data-enter="${f.id}">${fin ? 'Edit' : f.live ? 'Update' : 'Enter score'}</button>` : ''}</span>${side('a')}${team('a', f.a)}</div>
    ${liveCtl}${foot ? `<div class="m-foot">${foot}</div>` : ''}${heartRow(k, f)}${drawUI}
    ${canEnter ? `
    <div class="entry" id="entry-${f.id}" hidden>
      <input inputmode="numeric" aria-label="${esc(full(k, f.h))} goals" value="${fin ? f.hs : f.live ? f.live.h : ''}" id="hs-${f.id}"><span>–</span>
      <input inputmode="numeric" aria-label="${esc(full(k, f.a))} goals" value="${fin ? f.as : f.live ? f.live.a : ''}" id="as-${f.id}">
      ${needPens ? `<select id="pw-${f.id}" aria-label="Penalty winner if level"><option value="">Pens (if level)</option><option value="${f.h}" ${f.pens === f.h ? 'selected' : ''}>${esc(nm(k, f.h))}</option><option value="${f.a}" ${f.pens === f.a ? 'selected' : ''}>${esc(nm(k, f.a))}</option></select>` : ''}
      <button class="btn primary" data-save="${f.id}">Save</button>${fin ? `<button class="btn ghost" data-clear="${f.id}">Clear</button>` : ''}
      ${!cup && !fin ? `<div class="st-row live-row"><span>Red cards</span><input id="rch-${f.id}" inputmode="numeric" value="${f.live ? f.live.rc[0] : 0}" aria-label="${esc(full(k, f.h))} red cards"><span>–</span><input id="rca-${f.id}" inputmode="numeric" value="${f.live ? f.live.rc[1] : 0}" aria-label="${esc(full(k, f.a))} red cards"></div>
      <div class="st-row live-row"><span>In progress? Minute or HT</span><input id="mn-${f.id}" value="${f.live ? (c => c.ht ? 'HT' : c.min)(clockOf(k, f.id) || f.live) : ''}" placeholder="67" aria-label="Minute, or HT">
        <button class="btn live-btn" data-live="${f.id}">Update live</button>${f.live ? `<button class="btn ghost" data-unlive="${f.id}">Not live</button>` : ''}</div>
      <p class="hint">Save = full time. Update live = the score and red cards so far at that minute; odds, tables and importance update to match.</p>` : ''}
      ${!cup ? `<div class="st-row"><label class="aw"><input type="checkbox" id="aw-${f.id}" ${f.awarded ? 'checked' : ''}> Awarded result (counts in the table, not in ratings or pick 'em)</label></div>
      ${fin ? '' : `<div class="st-row">${f.postponed ? `<button class="btn ghost" data-unpp="${f.id}">Not postponed</button>` : `<button class="btn ghost" data-pp="${f.id}">Mark postponed</button>`}
        <span class="mv">New date <input type="date" id="nd-${f.id}" value="${f.moved ? f.date : ''}"> <input type="time" id="nt-${f.id}" value="${f.moved && f.kt ? new Date(f.kt).toTimeString().slice(0, 5) : ''}"> <button class="btn ghost" data-move="${f.id}">Reschedule</button></span></div>`}` : ''}</div>` : ''}
  </article>`;
}
// A round's matches in one grouped panel, with a date line each time the day changes.
function matchList(k, list, m, label) {
  let last = '', out = '';
  for (const f of list) { const d = f.postponed ? 'Postponed' : fmtDateK(f, {weekday:'long', month:'short', day:'numeric'}); if (d !== last) { out += `${last ? '</div>' : ''}<div class="mdate">${esc(d)}</div><div class="mday">`; last = d; } out += matchCard(k, f, m && m.id === f.id ? label : ''); }
  return `<div class="mlist">${out}${last ? '</div>' : ''}</div>`;
}
// Read-only row for lists that span competitions (Home): the competition as the caption, tap to open the match in its competition.
function feedRow(k, f, extra) {
  const L = f.live, rated = f.pH != null, P = L || f;
  const team = (sd, i) => `<span class="mr-t ${sd}">${crest(k, i, 34)}<span class="mr-n">${esc(nm(k, i))}${L ? reds(L.rc[sd === 'h' ? 0 : 1]) : ''}</span></span>`;
  const v = sd => L ? `<span class="mr-v sc num">${sd === 'h' ? L.h : L.a}</span>` : `<span class="mr-v num">${rated ? pct(sd === 'h' ? P.pH : P.pA) : ''}</span>`;
  const mid = L ? `<b class="mr-live num"><span class="live-dot"></span>${liveLabel(k, f)}</b><small>Draw ${pct(L.pD)}</small>`
    : `<b class="num ${isPast(f) ? 'past' : ''}">${f.kt ? fmtTime(f.kt) : 'TBC'}</b><small>${rated ? 'Draw ' + pct(f.pD) : ''}</small>`;
  return `<article class="match mrow feed ${hasFav(k, f) ? 'is-fav' : ''} ${L ? 'is-live' : ''} ${extra && extra.motd ? 'is-motw' : ''}" data-fx="${k}:${f.id}">
    <div class="mr-cap"><span style="color:${DOT[k]}">${esc(COMPS_CFG[k].name)}</span>${extra && extra.cap ? `<i>·</i>${extra.cap}` : ''}</div>
    <div class="mr" role="button" tabindex="0" data-go="${k}:${f.id}" aria-label="Open ${esc(full(k, f.h))} v ${esc(full(k, f.a))}">${team('h', f.h)}${v('h')}<span class="mr-c">${mid}</span>${v('a')}${team('a', f.a)}</div></article>`;
}
function feedList(items, capFn, byDate) {
  let last = '', out = '';
  for (const x of items) { const d = byDate ? fmtDateK(x.f, {weekday:'long', month:'short', day:'numeric'}) : '-'; if (d !== last) { out += `${last ? '</div>' : ''}${byDate ? `<div class="mdate">${esc(d)}</div>` : ''}<div class="mday">`; last = d; } out += feedRow(x.k, x.f, capFn ? capFn(x) : null); }
  return `<div class="mlist">${out}${last ? '</div>' : ''}</div>`;
}
function drawPicker(k, f) {
  const r = R[k], taken = new Set(r.fx.filter(x => x.round === f.round && x.id !== f.id).flatMap(x => [x.h, x.a]).filter(x => x != null));
  const opts = r.alive.filter(i => !taken.has(i)).map(i => `<option value="${i}">${esc(nm(k, i))}</option>`).join('');
  return `<div class="draw-sel"><select id="dh-${f.id}" aria-label="Home club"><option value="">Home club</option>${opts}</select><span>v</span>
    <select id="da-${f.id}" aria-label="Away club"><option value="">Away club</option>${opts}</select><button class="btn primary" data-draw="${f.id}">Set draw</button></div>`;
}

// ---------------------------------------------------------------- league views
function viewWeek(k) {
  const r = R[k], mw = state.mw[k], rounds = [...new Set(r.fx.map(f => f.mw))].sort((a, b) => a - b);
  const lgw = k === 'unl' ? (state.unlLeague || 'A') : null;
  const list = r.fx.filter(f => f.mw === mw && (!lgw || (T(k)[f.h].group || '')[0] === lgw)).sort((a, b) => a.sortT - b.sortT || a.id - b.id), dates = list.map(f => f.date).sort();
  const up = list.filter(f => !f.played), done = list.filter(f => f.played);
  const i = rounds.indexOf(mw);
  return `<section class="section"><div class="mw-head">
      <div><div class="mw-title">${esc(COMPS_CFG[k].round)} ${mw}</div><div class="mw-dates">${dates.length ? fmtDate(dates[0], {month:'long', day:'numeric'}) + (dates[0] !== dates[dates.length - 1] ? ' to ' + fmtDate(dates[dates.length - 1], {month:'long', day:'numeric'}) : '') : ''}</div></div>
      <div class="mw-nav"><button data-step="-1" aria-label="Previous" ${i <= 0 ? 'disabled' : ''}>‹</button><button data-step="1" aria-label="Next" ${i >= rounds.length - 1 ? 'disabled' : ''}>›</button></div></div>
    ${k === 'unl' ? leagueSeg() : ''}
    ${matchList(k, list, motwFor(k, list), 'Match of the week')}
    <p class="note">Match of the week blends importance with how evenly matched the sides are; it's fixed once the round's first match kicks off. Tap a match for the full scoreline grid.</p></section>`;
}
function zoneColor(k, pos) { const c = COMP[k].cfg.colors.find(([a, b]) => pos >= a && pos <= b); return c ? c[2] : 'transparent'; }
const COL_SHORT = {'Promoted':'Up', 'Play-offs':'PO', 'Relegated':'Rel', 'Quarter-finals':'QF', 'Win it':'Win', 'Top 8':'Top 8', 'Title':'Title', 'Top 4':'Top 4', 'Top 3':'Top 3', 'Shield':'Shield', 'Bye':'Bye', 'Playoffs':'PO',
  "Players' Shield":'Shield', "Supporters' Shield":'Shield', 'Home QF':'Home', 'Group winner':'1st', 'Play-off':'PO'};
const colHead = (k, key) => { const l = colLabel(k, key), s = COL_SHORT[l] || l; return s === l ? esc(l) : `<span class="nm-full">${esc(l)}</span><span class="nm-short">${esc(s)}</span>`; };
function colLabel(k, key) { const cfg = COMP[k].cfg; return (cfg.colLabels && cfg.colLabels[key]) || (cfg.zones.find(z => z.key === key) || {}).label || key; }
// Playoff leagues mark clinched and eliminated clubs beside the name (x, y, z, e) instead of a status column.
const hasMarks = k => (COMP[k].cfg.status || []).some(s => s.mark);
function markLegend(k, rows) {
  const seen = new Set(rows.map(r => r.mark).filter(Boolean));
  return COMP[k].cfg.status.filter(s => s.mark && seen.has(s.mark)).sort((a, b) => (a.type === 'doom') - (b.type === 'doom')).map(s => `<span class="mk"><sup class="smark ${s.type === 'doom' ? 'bad' : ''}">${s.mark}</sup>${esc(s.label)}</span>`).join('');
}
function tableRows(k, rows, proj, colsOverride) {
  const cfg = colsOverride ? Object.assign({}, COMP[k].cfg, {cols: colsOverride}) : COMP[k].cfg, bad = key => (cfg.zones.find(z => z.key === key) || {}).bad;
  const mini = (r, key) => { const v = r.odds[key] || 0; return `<span class="mini ${bad(key) || key === 'down' ? 'bad' : ''}"><i style="width:${Math.max(2, v * 48)}px"></i><span class="num">${pct(v)}</span></span>`; };
  const marked = hasMarks(k);
  return rows.map(r => {
    const mk = marked && r.mark ? `<sup class="smark ${r.statusBad ? 'bad' : ''}" title="${esc(r.status)}">${r.mark}</sup>` : '';
    const pos = proj ? r.projPos : r.pos, mv = r.moved ? `<span class="mv-arrow ${r.moved > 0 ? 'up' : 'down'}">${r.moved > 0 ? '▲' : '▼'}${Math.abs(r.moved)}</span>` : '', club = `<button class="club-link" data-club="${r.i}">${tchip(k, r.i)}${dual(k, r.i)}${mk}</button>${mv}`;
    const st = r.status ? `<span class="status-tag ${r.statusBad ? 'rel' : ''}">${esc(r.status)}</span>` : '';
    const mid = proj
      ? `<td class="num sm-hide">${wdl(r).join('-')}</td><td class="num sm-hide">${r.projGD > 0.5 ? '+' : ''}${r.projGD.toFixed(0)}</td>
         <td class="num"><b>${r.projPts.toFixed(0)}</b><span class="sm-hide" style="color:var(--faint)"> (${r.projLow}–${r.projHigh})</span></td><td class="num">${r.pos}${ord(r.pos)}<span class="sm-hide" style="color:var(--faint)"> · ${r.Pts} pts</span></td>`
      : `<td class="num sm-hide">${r.P}</td><td class="num sm-hide">${r.W}-${r.D}-${r.L}</td><td class="num">${r.GF - r.GA > 0 ? '+' : ''}${r.GF - r.GA}</td><td class="num"><b>${r.Pts}</b>${r.adj ? `<span class="adj-chip" title="${esc(r.adjNote || 'Points adjustment')}">${r.adj > 0 ? '+' : ''}${r.adj}</span>` : ''}</td>
         <td class="num sm-hide">${r.projPts.toFixed(0)} <span style="color:var(--faint)">(${r.projLow}–${r.projHigh})</span></td>`;
 return `<tr class="${cfg.cuts.includes(pos) ? 'cut' : ''} ${isFav(k, r.i) ? 'fav-row' : ''} ${marked && r.statusBad ? 'out' : ''}" ${T(k)[r.i].color ? `style="--fc:${T(k)[r.i].color}"` : ''}><td class="pos num" style="--zone:${zoneColor(k, pos)}">${pos}</td><td class="club">${club}</td>${mid}
      ${cfg.cols.map(c => `<td>${mini(r, c)}</td>`).join('')}${marked ? '' : `<td class="sm-hide">${proj ? '' : st}</td>`}</tr>`;
  }).join('');
}
function wdl(r) {
  // round expected W/D/L so they add up to the games played + left (largest remainder)
  const v = [r.projW, r.projD, r.projL], n = Math.round(v[0] + v[1] + v[2]), base = v.map(Math.floor);
  let left = n - base.reduce((s, x) => s + x, 0);
  v.map((x, i) => [x - Math.floor(x), i]).sort((p, q) => q[0] - p[0]).forEach(([, i]) => { if (left > 0) { base[i]++; left--; } });
  return base;
}
const ord = n => (n % 100 >= 11 && n % 100 <= 13) ? 'th' : ({1:'st', 2:'nd', 3:'rd'}[n % 10] || 'th');
function tableHTML(k, rows, proj, grp) {
  const cfg0 = COMP[k].cfg, cfg = cfg0.colsByLeague && grp ? Object.assign({}, cfg0, {cols: cfg0.colsByLeague[grp[0]]}) : cfg0;
  const head = proj ? '<th class="sm-hide">Proj W-D-L</th><th class="sm-hide">GD</th><th>Proj</th><th>Now</th>' : '<th class="sm-hide">P</th><th class="sm-hide">W-D-L</th><th>GD</th><th>Pts</th><th class="sm-hide">Projected</th>';
  const sorted = proj ? [...rows].sort((a, b) => a.projPos - b.projPos) : rows;
  return `<div class="card scroll" style="margin-top:10px"><table><thead><tr><th>#</th><th class="club">${esc(COMPS_CFG[k].noun || 'Club')}</th>${head}${cfg.cols.map(c => `<th>${colHead(k, c)}</th>`).join('')}${hasMarks(k) ? '' : '<th class="sm-hide"></th>'}</tr></thead><tbody>${tableRows(k, sorted, proj, cfg.cols)}</tbody></table></div>`;
}

function liveTable(k) {
  const r = R[k], cfg = COMP[k].cfg;
  const t = r.tab.map(x => Object.assign({}, x));
  for (const f of r.fx) if (f.live) {
    const H = t[f.h], A = t[f.a], L = f.live; H.P++; A.P++; H.GF += L.h; H.GA += L.a; A.GF += L.a; A.GA += L.h;
    if (L.h > L.a) { H.W++; A.L++; H.Pts += 3; } else if (L.h < L.a) { A.W++; H.L++; A.Pts += 3; } else { H.D++; A.D++; H.Pts++; A.Pts++; }
  }
  const key = x => x.Pts * 1e6 + (x.GF - x.GA + 300) * 1e3 + x.GF;
  for (const x of t) { const peers = cfg.grouped ? t.filter(o => o.group === x.group) : t; x.moved = x.pos; x.pos = 1 + peers.filter(o => key(o) > key(x)).length; x.moved = x.moved - x.pos; x.status = ''; }
  return t;
}
// Nations League A: 3rd- and 4th-placed nations ranked across the groups (points, goal difference,
// goals scored: the order the model uses for relegation and play-off places), each tagged with where that spot leads.
const UNL_RACES = {
  A: [{p: 4, title: '4th-placed nations', sub: 'The best two play off to stay up; the worst two go down to League B.', fate: n => n < 2 ? 'po' : 'down', cols: ['po', 'down']},
      {p: 3, title: '3rd-placed nations', sub: 'The worst two play off to stay up against League B runners-up.', fate: n => n < 2 ? 'safe' : 'po', cols: ['po', 'down']}],
};
const UNL_FATE = {safe: ['Safe', 'var(--mint)'], po: ['Play-off', '#F29D0C'], down: ['Relegated', 'var(--magenta)']};
function unlRaces(k, base, proj, lg) {
  const specs = UNL_RACES[lg]; if (!specs) return '';
  const pts = r => proj ? r.projPts : r.Pts, gd = r => proj ? r.projGD : r.GF - r.GA, gf = r => proj ? 0 : r.GF;
  const mini = (r, key) => { const v = r.odds[key] || 0; return `<span class="mini ${key === 'down' ? 'bad' : ''}"><i style="width:${Math.max(2, v * 48)}px"></i><span class="num">${pct(v)}</span></span>`; };
  const table = sp => {
    const order = (a, b) => pts(b) - pts(a) || gd(b) - gd(a) || gf(b) - gf(a);
    // Exactly one nation per group for each place, even when two are level on the group's own tiebreakers.
    const groups = [...new Set(base.filter(r => (r.group || '')[0] === lg).map(r => r.group))];
    const rows = groups.map(g => base.filter(r => r.group === g).sort((a, b) => (proj ? a.projPos - b.projPos : a.pos - b.pos) || order(a, b) || a.i - b.i)[sp.p - 1]).filter(Boolean).sort(order);
    return `<div class="grp">${esc(sp.title)}</div><p class="sub" style="margin:0">${esc(sp.sub)}</p>
    <div class="card scroll" style="margin-top:10px"><table><thead><tr><th>#</th><th class="club">Nation</th><th class="sm-hide">Group</th><th class="sm-hide">P</th><th>GD</th><th>Pts</th>${sp.cols.map(c => `<th>${colHead(k, c)}</th>`).join('')}<th></th></tr></thead><tbody>
    ${rows.map((r, n) => { const [lab, col] = UNL_FATE[sp.fate(n)], g = gd(r);
      return `<tr class="${isFav(k, r.i) ? 'fav-row' : ''}" ${T(k)[r.i].color ? `style="--fc:${T(k)[r.i].color}"` : ''}><td class="pos num" style="--zone:${col}">${n + 1}</td>
      <td class="club"><button class="club-link" data-club="${r.i}">${tchip(k, r.i)}${dual(k, r.i)}</button></td><td class="num sm-hide">${esc(r.group)}</td><td class="num sm-hide">${r.P}</td>
      <td class="num">${g > 0.5 ? '+' : ''}${proj ? g.toFixed(0) : g}</td><td class="num"><b>${proj ? pts(r).toFixed(0) : pts(r)}</b></td>${sp.cols.map(c => `<td>${mini(r, c)}</td>`).join('')}
      <td><span class="status-tag ${({down: "rel", po: "po"})[sp.fate(n)] || ""}">${lab}</span></td></tr>`; }).join('')}</tbody></table></div>`;
  };
  return `<h3 style="margin-top:26px">League ${lg}: relegation race</h3>${specs.map(table).join('')}`;
}
function leagueSeg() { const lg = state.unlLeague || 'A'; return `<div class="seg" role="group" aria-label="League" style="margin-top:12px">${['A', 'B', 'C', 'D'].map(x => `<button data-unllg="${x}" aria-pressed="${lg === x}">League ${x}</button>`).join('')}</div>`; }
function viewTable(k) {
  const r = R[k], cfg = COMP[k].cfg, proj = state.tmode[k] === 'proj';
  const anyLive = r.fx.some(f => f.live), live = anyLive && state.tmode[k] === 'live';
  const src = live ? liveTable(k) : null;
  const rowsFor = g => { const base = src || r.tab; const rs = base.filter(x => !cfg.grouped || x.group === g); return rs.sort((a, b) => a.pos - b.pos); };
  const lg = k === 'unl' ? (state.unlLeague || 'A') : null;
  const body = cfg.grouped ? Object.keys(r.byGroup).sort().filter(g => !lg || g[0] === lg).map(g => `<div class="grp">${['mls', 'usl'].includes(k) ? esc(g) + 'ern Conference' : 'Group ' + esc(g)}</div>${tableHTML(k, rowsFor(g), proj, g)}`).join('')
    + (lg && cfg.leagueNotes ? `<p class="note">${esc(cfg.leagueNotes[lg])}</p>` : '') + (lg ? unlRaces(k, src || r.tab, proj, lg) : '') : tableHTML(k, rowsFor(''), proj);
  const toggle = `<div class="seg" role="group" aria-label="Table view"><button data-tmode="now" aria-pressed="${!proj && !live}">Current</button>${anyLive ? `<button data-tmode="live" aria-pressed="${live}"><span class="live-dot"></span>As it stands</button>` : ''}<button data-tmode="proj" aria-pressed="${proj}">Projected</button></div>`;
  return `<section class="section"><div class="mw-head"><h2>${cfg.grouped ? (['mls', 'usl'].includes(k) ? 'Conferences' : 'Groups') : 'Table'}</h2>${toggle}</div>${k === 'unl' ? leagueSeg() : ''}
    <p class="sub">${live ? 'The table if every live match finished at its current score. Odds already account for the live scores. ' : ''}${proj ? 'Final table if every remaining match plays out at its expected value: projected points, the middle-80% range from 1,000 simulated seasons, and where each club sits now.' : 'Live from your results. Projected points and odds come from 1,000 simulated seasons; the range covers the middle 80%.'} Tap a club for its fixtures.</p>
    ${body}<div class="legend">${cfg.legend.map(([l, c]) => `<span style="--c:${c}">${esc(l)}</span>`).join('')}</div>${hasMarks(k) && !live && markLegend(k, r.tab) ? `<div class="legend marks">${markLegend(k, r.tab)}</div>` : ''}
    <div class="race" style="margin-top:18px;display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap">
      <div><h3 style="margin:0">Affinity satisfaction</h3><p class="sub" style="margin:4px 0 0">How closely the standings follow your Affinity order. 0 is the worst possible order, 100 the best.</p></div>
      <div class="mw-title num">${Math.round(r.satisfaction)}</div></div></section>`;
}
function raceList(k, key, title, bad, group) {
  const r = R[k], rows = r.tab.filter(t => !group || t.group === group || (group.length === 1 && (t.group || '')[0] === group)).map(t => ({i:t.i, v:t.odds[key] || 0})).sort((a, b) => b.v - a.v);
  const inn = rows.filter(x => x.v >= 0.995), out = rows.filter(x => x.v < 0.005), live = rows.filter(x => x.v >= 0.005 && x.v < 0.995);
  const names = xs => xs.map(x => esc(nm(k, x.i))).join(', ');
  const lockPills = xs => xs.map(x => `<span class="lock-pill ${bad ? 'bad' : ''}" style="--fc:${T(k)[x.i].color || '#8E8E93'}">${bad ? '✕' : '✓'} ${esc(nm(k, x.i))}</span>`).join('');
  const lockLabel = bad ? 'Already down' : 'Locked in', outLabel = bad ? 'Safe' : 'Out of it';
  const summary = [inn.length ? `<div class="race-note"><b>${lockLabel}:</b></div><div class="lock-pills">${lockPills(inn)}</div>` : '',
                   out.length ? `<div class="race-note"><b>${outLabel}:</b> ${out.length > 6 ? out.length + ' clubs' : names(out)}</div>` : ''].join('');
  const clinched = !bad && !live.length && inn.length === 1 ? inn[0] : null;
  if (clinched) {
    const c = T(k)[clinched.i];
    return `<div class="race done" style="--fc:${c.color || '#30D158'}"><h3>${esc(title)}</h3>
      <div class="clinched"><span class="cl-tag">✓ Wrapped up</span><button class="club-link cl-name" data-club="${clinched.i}">${tchip(k, clinched.i)}${esc(c.name)}</button>
      <span class="cl-sub">No one else finishes there in any of the 1,000 simulated seasons.</span></div></div>`;
  }
  const body = live.length ? live.slice(0, 10).map(x => `<div class="bar-row"><button class="t club-link ${isFav(k, x.i) ? 'fav-name' : ''}" data-club="${x.i}">${tchip(k, x.i)}<span class="tt">${esc(nm(k, x.i))}</span></button><span class="bar"><i style="width:${x.v * 100}%"></i></span><span class="v num">${pct(x.v)}</span></div>`).join('')
    : `<div class="race-done">${inn.length && !bad && inn.length === 1 ? esc(nm(k, inn[0].i)) + ' has it wrapped up.' : 'Settled: no club is between 1% and 99%.'}</div>`;
  return `<div class="race ${bad ? 'bad' : ''} ${group ? '' : 'solo'}"><h3>${esc(title)}</h3>${body}${summary}</div>`;
}
function raceSpecs(k) {
  const cfg = COMP[k].cfg;
  if (k === 'nwsl') return [['champ', 'NWSL Championship'], ...cfg.cols.map(c => [c, colLabel(k, c)])];
  if (k === 'usl') return [['champ', 'USL Championship title'], ['shield', "Players' Shield"], ['po', 'East: playoff race', 'East'], ['po', 'West: playoff race', 'West'],
    ['top4', 'East: home quarterfinal (top 4)', 'East'], ['top4', 'West: home quarterfinal (top 4)', 'West'], ['conf', 'East: conference winner', 'East'], ['conf', 'West: conference winner', 'West']];
  if (k === 'mls') return [['champ', 'MLS Cup'], ['shield', "Supporters' Shield"], ['po', 'East: playoff race', 'East'], ['po', 'West: playoff race', 'West'],
    ['bye', 'East: round-one bye (top 7)', 'East'], ['bye', 'West: round-one bye (top 7)', 'West'], ['conf', 'East: conference winner', 'East'], ['conf', 'West: conference winner', 'West']];
  if (k === 'unl') return [['win', 'Win the Nations League', 'A'], ['down', 'Relegated from League A', 'A'], ['up', 'Promoted from League B', 'B'], ['down', 'Relegated from League B', 'B'], ['up', 'Promoted from League C', 'C'], ['po', 'Play-off: League C runners-up', 'C']];
  return cfg.cols.map(c => [c, colLabel(k, c)]);
}
function bigList(k, list, cup) {
  return `<div class="card big">${list.map(f => `<div class="big-row" data-open="${f.id}" role="button" tabindex="0">
      <span class="wk">${cup ? esc(f.round.replace('Semi-final', 'SF')) : esc(COMPS_CFG[k].abbr) + ' ' + f.mw}<br>${fmtDate(f.date, {month:'short', day:'numeric'})}</span>
      <span class="mt">${esc(full(k, f.h))} v ${esc(full(k, f.a))}<small>Matters most to ${f.mattersTo == null ? 'nobody' : esc(full(k, f.mattersTo))}</small></span>
      ${impMeter(f.importance).replace('Importance ', '')}</div>`).join('') || '<div class="empty">No matches left.</div>'}</div>`;
}
function viewRaces(k) {
  const cfg = COMP[k].cfg, r = R[k];
  const specs = raceSpecs(k);
  const big = r.fx.filter(f => !f.played && f.importance !== undefined).sort((a, b) => b.importance - a.importance).slice(0, 10);
  return `<section class="section"><h2>The races</h2><p class="sub">Chances from 1,000 simulated seasons${cfg.knockout ? ', knockout rounds included' : ''}. Each race lists the clubs still in doubt; clubs already locked in or out are listed underneath.</p>
    <div class="races ${COMP[k].cfg.grouped ? 'pairs' : ''}">${specs.map(([key, title, g]) => raceList(k, key, title, (cfg.zones.find(z => z.key === key) || {}).bad || key === 'down', g)).join('')}</div></section>
    <section class="section"><h2>Biggest matches left</h2><p class="sub">How far each result swings the odds that matter, scaled so the biggest is 1.00.</p>${bigList(k, big)}</section>`;
}
// ---------------------------------------------------------------- Affinity
const affOf = t => t.base + t.bonus;
const signed = v => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v);
// One-line summary under a club's name: track record and adjustments (the factors are on the club card).
const AFF_HOW = `<details class="how"><summary>How it's scored</summary><p>Five ratings out of 10: Values 26%, Culture 23%, History 16%, Team 15%, Ownership 10%. Recent results scale that by 0.95 to 1.05 (top-flight clubs). Then hard lines (racism, state ownership, fan violence, private equity, Super League) and connection (distance, local teams, linked clubs, hometown or heritage).</p></details>`;
let natF = 'all';
const wcOf = name => EXTRA.wc[name];
function viewClubs(k) {
  if (k === 'unl') return viewNations();
  const t = T(k), order = [...t.keys()].sort((a, b) => affOf(t[b]) - affOf(t[a])), mx = Math.max(...order.map(i => affOf(t[i])));
  const cup = COMPS_CFG[k].cup, r = R[k], anyBonus = order.some(i => t[i].bonus);
  const ratings = cup ? '' : `<section class="section"><h2>Ratings</h2><p class="sub">Opponent-adjusted attack and defense (1.00 = average; lower defense is better).</p>
    <div class="card scroll" style="margin-top:14px"><table><thead><tr><th class="club">${esc(COMPS_CFG[k].noun || 'Club')}</th><th>Attack</th><th>Defense</th><th>Avg finish</th></tr></thead>
    <tbody>${[...t.keys()].sort((a, b) => (r.att[b] / r.def[b]) - (r.att[a] / r.def[a])).map(i => `<tr><td class="club"><button class="club-link" data-club="${i}">${dual(k, i)}</button></td><td class="num">${r.att[i].toFixed(2)}</td><td class="num">${r.def[i].toFixed(2)}</td><td class="num">${r.tab[i].avgSimPos.toFixed(1)}</td></tr>`).join('')}</tbody></table></div></section>`;
  return `<section class="section"><div class="sec-head"><h2>Your Affinity</h2><button class="linkish" data-view="rank">All ${rankList().length} ranked →</button></div>
    ${AFF_HOW}
    ${anyBonus ? '<div class="legend"><span style="--c:var(--accent)">Affinity</span><span style="--c:var(--magenta)">Heritage bonus</span></div>' : ''}
    <div class="card" style="margin-top:10px">${order.map((i, n) => `<div class="hai-row"><span class="num rk">${n + 1}</span>
      <span class="who"><button class="club-link" data-club="${i}">${tchip(k, i)}${esc(t[i].name)}</button><small>${esc((cup ? t[i].tier : t[i].region) || '')}</small></span>
      <span class="stack"><span class="b" style="width:${t[i].base / mx * 100}%"></span><span class="x" style="width:${t[i].bonus / mx * 100}%"></span></span>
      <span class="num sc">${fmtA(affOf(t[i]))}</span></div>`).join('')}</div></section>${ratings}`;
}
// Nations: the Nations League's 54 plus the rest of the 2026 World Cup field, filterable.
function viewNations() {
  const k = 'unl', r = R[k], t = T(k);
  const all = t.map((x, i) => ({t: x, attr: `data-club="${i}"`, chip: tchip(k, i)}))
    .concat(EXTRA.teams.map((x, j) => ({t: x, attr: `data-xnat="${j}"`, chip: nchip(x.name, x.color)})))
    .sort((a, b) => affOf(b.t) - affOf(a.t) || a.t.name.localeCompare(b.t.name));
  const nWc = all.filter(e => wcOf(e.t.name)).length;
  const list = all.map((e, n) => Object.assign({n: n + 1}, e)).filter(e => natF === 'all' || (natF === 'wc' ? wcOf(e.t.name) : !e.t.confed));
  const mx = affOf(all[0].t), sub = e => [e.t.confed || 'UEFA', wcOf(e.t.name) ? `World Cup: ${wcOf(e.t.name)}` : ''].filter(Boolean).join(' · ');
  const chips = [['all', `All ${all.length}`], ['wc', `World Cup 2026 ${nWc}`], ['uefa', `Nations League ${t.length}`]];
  const ratings = `<section class="section"><h2>Ratings</h2><p class="sub">Opponent-adjusted attack and defense (1.00 = average; lower defense is better). Nations League sides only.</p>
    <div class="card scroll" style="margin-top:14px"><table><thead><tr><th class="club">Nation</th><th>Attack</th><th>Defense</th><th>Avg finish</th></tr></thead>
    <tbody>${[...t.keys()].sort((a, b) => (r.att[b] / r.def[b]) - (r.att[a] / r.def[a])).map(i => `<tr><td class="club"><button class="club-link" data-club="${i}">${dual(k, i)}</button></td><td class="num">${r.att[i].toFixed(2)}</td><td class="num">${r.def[i].toFixed(2)}</td><td class="num">${r.tab[i].avgSimPos.toFixed(1)}</td></tr>`).join('')}</tbody></table></div></section>`;
  return `<section class="section"><div class="sec-head"><h2>Your Affinity</h2><button class="linkish" data-view="rank">All ${rankList().length} ranked →</button></div>
    ${AFF_HOW}
    <div class="rank-chips">${chips.map(([f, l]) => `<button class="rchip" data-natf="${f}" aria-pressed="${natF === f}">${esc(l)}</button>`).join('')}</div>
    <div class="legend"><span style="--c:var(--accent)">Affinity</span><span style="--c:var(--magenta)">Heritage bonus</span></div>
    <div class="card" style="margin-top:10px">${list.map(e => `<div class="hai-row"><span class="num rk">${e.n}</span>
      <span class="who"><button class="club-link" ${e.attr}>${e.chip}${esc(e.t.name)}</button><small>${esc(sub(e))}</small></span>
      <span class="stack"><span class="b" style="width:${Math.max(0, e.t.base) / mx * 100}%"></span><span class="x" style="width:${e.t.bonus / mx * 100}%"></span></span>
      <span class="num sc">${fmtA(affOf(e.t))}</span></div>`).join('')}</div></section>${ratings}`;
}
// A World Cup nation outside the Nations League: Affinity breakdown only.
function openNation(j) {
  const t = EXTRA.teams[j];
  $('#sheet').style.cssText = '';
  $('#sheet').innerHTML = `<div class="sheet-head"><div><div class="sub">${esc(t.confed)}${wcOf(t.name) ? ` · World Cup 2026: ${esc(wcOf(t.name))}` : ''}</div>
      <h2 style="margin-top:4px"><i class="tchip" style="--tc:${t.color}"></i>${esc(t.name)}</h2></div><button class="close" aria-label="Close" id="close">✕</button></div>
    ${affBreakdown('unl', t)}<p class="note">Not in the Nations League, so there are no matches or ratings to show.</p>`;
  if (!$('#detail').open) $('#detail').showModal(); $('#close').onclick = () => $('#detail').close();
}
// A heritage club (Kevin's ancestry regions, outside the tracked leagues): Affinity breakdown only.
function openXClub(j) {
  const t = EXTRA.clubs[j];
  $('#sheet').style.cssText = '';
  $('#sheet').innerHTML = `<div class="sheet-head"><div><div class="sub">${esc(t.league)} · ${esc(t.region)}</div>
      <h2 style="margin-top:4px">${nchip(t.name, t.color, 'xc')}${esc(t.name)}</h2></div><button class="close" aria-label="Close" id="close">✕</button></div>
    ${affBreakdown('xc', t)}<p class="note">Rated for your heritage region. Not in a league the app tracks, so there are no matches to show.</p>`;
  if (!$('#detail').open) $('#detail').showModal(); $('#close').onclick = () => $('#detail').close();
}
// Overall ranking: every club and nation once, under its primary league.
const RANK_PRIMARY = ['epl', 'esp', 'ita', 'bl', 'fra', 'mls', 'nwsl', 'ch', 'usl', 'ucl', 'cup', 'unl'];
const RANK_LABEL = { cup: 'League One / Two', ucl: 'Other European leagues', unl: 'Nations', xc: 'Heritage clubs' };
const rankLabel = k => RANK_LABEL[k] || COMPS_CFG[k].name;
let rankF = 'all', rankCache = null, rankMode = 'clubs', plF = 'ma', plOpen = null;
// What Kevin can realistically follow (bandwidth): the leagues he follows, and the competitions where his clubs meet
// others (Champions League, Carabao Cup). Shown next to Affinity, never added to it.
const YOUR_LEAGUES = ['epl', 'bl', 'mls', 'nwsl', 'usl'];
let compsOfCache = null;
function fitOf(name) {
  if (!compsOfCache) { compsOfCache = {}; for (const k of ORDER) for (const t of T(k)) (compsOfCache[t.name] = compsOfCache[t.name] || new Set()).add(k); }
  const cs = compsOfCache[name]; if (!cs) return '';
  if (YOUR_LEAGUES.some(k => cs.has(k))) return 'league';
  if (cs.has('ucl')) return 'meets';
  // Carabao Cup: only clubs still in it can meet Liverpool
  if (cs.has('cup') && R.cup && R.cup.alive.some(i => T('cup')[i].name === name)) return 'meets';
  return '';
}
function rankList() {
  if (rankCache) return rankCache;
  const by = {};
  for (const k of RANK_PRIMARY) T(k).forEach((t, i) => { if (!by[t.name]) by[t.name] = {k, i, t}; });
  EXTRA.teams.forEach((t, j) => { if (!by[t.name]) by[t.name] = {k: 'unl', x: j, t}; });
  (EXTRA.clubs || []).forEach((t, j) => { if (!by[t.name]) by[t.name] = {k: 'xc', xc: j, t}; });
  return rankCache = Object.values(by).sort((a, b) => affOf(b.t) - affOf(a.t) || a.t.name.localeCompare(b.t.name));
}
const PL_TABS = [['ma', 'Men · Active'], ['mt', 'Men · All-time'], ['wa', 'Women · Active'], ['wt', 'Women · All-time']];
const PL_F = ['Character', 'Team player', 'Loyalty & bond', 'Greatness', 'Joy to watch', 'Legacy'];
const rankModes = () => PLAYERS.ma ? `<div class="rank-chips">${[['clubs', 'Clubs & nations'], ['players', 'Players']].map(([m, l]) => `<button class="rchip" data-rankmode="${m}" aria-pressed="${rankMode === m}" style="--c:#fff">${l}</button>`).join('')}</div>` : '';
const PL_HOW = `<details class="how"><summary>How it's scored</summary><p>Two halves, and a player needs both. Role model: Character, Team player and Loyalty (weighted by your quiz choices), your values, hard lines (abuse, racism, match-fixing, violence, money-league moves and the like) and connection to the clubs they played for. Performance: Greatness 40%, Legacy 35%, Joy to watch 25%. Affinity combines them 60/40 so a weak half pulls the total down. A club's best players and icons also lift its own Affinity.</p></details>`;
function viewPlayers() {
  const L = PLAYERS[plF] || [], mx = L.length ? L[0].a : 100;
  return `<section class="section">${rankModes()}${PL_HOW}
    <div class="rank-chips">${PL_TABS.map(([k, l]) => `<button class="rchip" data-plf="${k}" aria-pressed="${plF === k}" style="--c:#fff">${l}</button>`).join('')}</div>
    <div class="card rank" style="margin-top:12px">${L.map((p, n) => `<div class="rank-row pl-row" data-plopen="${n}" role="button" tabindex="0" aria-expanded="${plOpen === n}"><span class="num rk">${n + 1}</span>
      <span class="who">${esc(p.n)}${p.nw ? ' <span class="pl-tag">NWSL</span>' : ''}<small><span>${esc([p.pos, p.nat, (p.clubs || []).slice(-1)[0]].filter(Boolean).join(' · '))}</span></small></span>
      <span class="stack"><span class="b" style="width:${Math.max(0, p.a) / mx * 100}%"></span></span>
      <span class="num sc">${p.a.toFixed(1)}</span></div>${plOpen === n ? `<div class="pl-det">${p.f.map((v, j) => `<div class="hb"><span>${PL_F[j]}</span><span class="bar"><i style="width:${v * 10}%"></i></span><b class="num">${v.toFixed(1)}</b></div>`).join('')}
        <div class="hb-items">${p.rm != null ? `<div class="hb-item"><span>Role model</span><b class="num">${p.rm.toFixed(1)}</b></div><div class="hb-item"><span>Performance</span><b class="num">${p.pf.toFixed(1)}</b></div>` : ''}${p.c ? `<div class="hb-item"><span>Connection</span><b class="num ${p.c < 0 ? 'neg' : ''}">${signed(p.c)}</b></div>` : ''}${p.p ? `<div class="hb-item"><span>Hard lines</span><b class="num neg">${signed(p.p)}</b></div>${(p.pen || []).map(x => `<div class="hb-item"><span>${esc(x)}</span></div>`).join('')}` : ''}</div>
        ${p.why ? `<p class="note">${esc(p.why)}</p>` : ''}</div>` : ''}`).join('')}</div></section>`;
}
function viewRank() {
  if (rankMode === 'players' && PLAYERS.ma) return viewPlayers();
  const all = rankList(), mx = affOf(all[0].t);
  const counts = {}; all.forEach(e => counts[e.k] = (counts[e.k] || 0) + 1);
  const nFit = all.filter(e => fitOf(e.t.name)).length;
  const chips = [['all', `All ${all.length}`], ['fit', `In your competitions ${nFit}`]].concat(RANK_PRIMARY.concat('xc').filter(k => counts[k]).map(k => [k, `${rankLabel(k)} ${counts[k]}`]));
  const list = all.map((e, n) => Object.assign({n: n + 1}, e)).filter(e => rankF === 'all' || (rankF === 'fit' ? fitOf(e.t.name) : e.k === rankF));
  // Filtered to one league: rank within the league, overall rank in parentheses.
  const byLeague = rankF !== 'all' && rankF !== 'fit';
  return `<section class="section">${rankModes()}${AFF_HOW}
    <div class="rank-chips">${chips.map(([k, l]) => `<button class="rchip" data-rankf="${k}" aria-pressed="${rankF === k}" style="--c:${k === 'all' || k === 'fit' ? '#fff' : DOT[k]}">${k === 'all' || k === 'fit' ? '' : '<i></i>'}${esc(l)}</button>`).join('')}</div>
    <div class="card rank ${byLeague ? 'by-league' : ''}" style="margin-top:12px">${list.map((e, j) => `<div class="rank-row" style="--c:${DOT[e.k]}"><span class="num rk">${byLeague ? `${j + 1} <small>(${e.n})</small>` : e.n}</span>
      <span class="who"><button class="club-link" ${e.x != null ? `data-xnat="${e.x}"` : e.xc != null ? `data-xclub="${e.xc}"` : `data-club="${e.k}:${e.i}"`}>${nchip(e.t.name, e.t.color, e.k)}${esc(e.t.name)}</button><small><i></i><span>${esc(rankLabel(e.k))}</span></small></span>
      <span class="stack"><span class="b" style="width:${Math.max(0, affOf(e.t)) / mx * 100}%"></span></span>
      <span class="num sc">${fmtA(affOf(e.t))}</span></div>`).join('')}</div></section>`;
}
function field(k, key, label, help, step, global) { const v = global ? state.suite[key] : Sfor(k)[key]; return `<div class="field"><label for="f-${key}">${label}</label><p>${help}</p><input id="f-${key}" data-set="${key}" data-global="${global ? 1 : 0}" type="number" step="${step}" value="${v}"></div>`; }
function viewSettings(k) {
  const n = Object.keys(state.results[k]).length, cup = COMPS_CFG[k].cup, nd = R[k] ? R[k].fx.filter(f => f.baseDiff).length : 0;
  return `<section class="section"><h2>Settings</h2><p class="sub">Changes apply straight away and save with your scores. Pick 'em scoring is shared by every competition.</p>
    <div class="set-grid">${field(k, 'peOutcome', "Pick 'em: correct result", 'Points for the right winner or draw.', 1, true)}${field(k, 'motwW', 'Match of the week: importance share', 'Blend of what\'s at stake (importance) and how evenly matched the sides are. 1 = importance only, 0 = competitiveness only. Default 0.5. Also used for Match of the day.', 0.1, true)}${field(k, 'peExact', "Pick 'em: correct score (total)", 'Total points when the exact score is right too.', 1, true)}
    ${cup ? field(k, 'underdog', 'Affinity pick: underdog lean', 'Extra weight for the side less likely to go through. At 0.05 (5%) it only decides close calls. 0 = off.', 0.01) : field(k, 'beta', 'Affinity pick: stakes weight (β)', "How much a club's stakes can outweigh Affinity in the pick. 0 = Affinity only. Default 0.3.", 0.05) +
      field(k, 'underdog', 'Affinity pick: underdog lean', "Extra weight for the side less likely to win. At 0.05 (5%) it only decides close calls. 0 = off.", 0.01) + field(k, 'drawW', 'Favor: draw weight (used when auto draw rate is off)', `How strongly an even match is favored as a draw. With auto draw rate on, it's set so Affinity picks call draws at the same rate as the league: now ${R[k] && R[k].favDrawW ? R[k].favDrawW.toFixed(3) : '—'}.`, 0.05) +
      field(k, 'drawAuto', 'Model: auto draw rate (1 = on, 0 = off)', `Keeps predicted draws in line with how often this league actually draws. Now: ${R[k] && R[k].drawTarget != null ? (R[k].drawTarget * 100).toFixed(1) + '% target (' + (R[k].fx.filter(f => f.played && f.hs === f.as).length) + ' draws in ' + R[k].fx.filter(f => f.played).length + ' matches, blended with a ' + Math.round(COMP[k].cfg.drawPrior * 100) + '% long-run norm)' : 'off'}.`, 1) +
      field(k, 'drawW0', 'Model: draw-rate prior (matches)', 'How many matches of the long-run norm the observed rate is blended with. Lower = follow this season faster.', 5) +
      field(k, 'halfLife', 'Model: recency half-life (days)', 'A result this many days older counts half as much.', 1) + field(k, 'k', 'Model: regression to the mean', "Phantom games at each club's preseason rating.", 1)}</div></section>
    ${cup ? '' : `<section class="section"><h2>Points adjustments</h2><p class="sub">For points deductions or awards handed down by the league. They apply to the table, clinch statuses and every simulation.</p>
      <div class="card" style="margin-top:12px">${(state.settings[k].adj || []).map((x, n) => `<div class="adj-row"><span>${tchip(k, x.i)}<b>${esc(T(k)[x.i].name)}</b> ${x.n ? `<small>${esc(x.n)}</small>` : ''}</span><b class="num ${x.p < 0 ? 'neg' : ''}">${x.p > 0 ? '+' : ''}${x.p} pts</b><button class="btn ghost" data-adjdel="${n}">Remove</button></div>`).join('') || '<div class="adj-row"><span style="color:var(--muted)">None</span></div>'}
      <div class="adj-add"><select id="adj-club" aria-label="Club">${[...T(k).keys()].sort((x, y) => T(k)[x].name.localeCompare(T(k)[y].name)).map(i => `<option value="${i}">${esc(T(k)[i].name)}</option>`).join('')}</select>
        <select id="adj-sign" aria-label="Deduction or award"><option value="-1">Deduct</option><option value="1">Award</option></select>
        <input id="adj-pts" inputmode="numeric" pattern="[0-9]*" placeholder="6" aria-label="Points"><input id="adj-note" placeholder="Reason (optional)" aria-label="Reason">
        <button class="btn primary" data-adjadd="1">Add</button></div></div></section>`}
    <section class="section"><h2>Your clubs</h2><p class="sub">Followed clubs get a star, a highlighted match card and table row, and their own section on the overview. You can also follow from any club card.</p>
    <div class="fav-chips">${[...T(k).keys()].sort((x, y) => T(k)[x].name.localeCompare(T(k)[y].name)).filter(i => !cup || R[k].alive.includes(i) || isFav(k, i)).map(i => `<button class="fchip ${isFav(k, i) ? 'on' : ''}" data-follow="${i}">${isFav(k, i) ? '★' : '☆'} ${esc(T(k)[i].name)}</button>`).join('')}</div>
    ${cup ? '<p class="note">Showing the 16 clubs still in the cup.</p>' : ''}</section>
    <section class="section"><h2>Your data</h2><p class="sub">${n} result${n === 1 ? '' : 's'} entered or edited here, on top of the results that came with the tracker.${nd ? ` <b>${nd}</b> of them ${nd === 1 ? 'differs' : 'differ'} from the tracker's data; the match cards show both.` : ''} ${saveMode === 'google' ? `They sync to your Google account (${esc(backend.user.email || '')}), so they follow you between devices. <button class="linkish" data-signout="1">Sign out</button>` : saveMode === 'claude' ? 'They save to your Claude account, so they follow you between devices.' : authState === 'signed-out' ? 'They save on this device only. <button class="linkish" data-signin="1">Sign in with Google</button> to sync between devices.' : 'They save on this device.'}</p>
    <button class="danger" data-reset="${k}" style="margin-top:12px">Remove my entered results for ${esc(COMPS_CFG[k].name)}</button>
    <p class="note">US broadcaster: ${esc(DATA[k].tv)}. Kickoff times show in your device's time zone; "time TBC" means the league hasn't confirmed the slot yet. Fixtures and results through September 20 from ${esc(COMPS_CFG[k].source)}${DATA[k].synced ? `, then from ESPN (last update ${fmtDate(DATA[k].synced, {month:'long', day:'numeric'})})` : ''}. ${cup ? 'Model: Poisson ratings on the Premier League scale with tier offsets, 1,000 simulated cups with random draws for undrawn rounds.' : 'Model: Dixon-Coles Poisson ratings with preseason priors and a 1,000-season simulation, the same method as your Excel trackers.'}</p></section>`;
}


// ---------------------------------------------------------------- playoffs bracket (NWSL, MLS)
function bracketState(k) {
  const r = R[k], done = r.rem.length === 0, kind = COMP[k].cfg.knockout, ko = state.ko[k] || {};
  const seedNum = {}, pts = {}; let seedOf;
  r.tab.forEach(t => { pts[t.i] = t.Pts; });
  const rank = t => done ? t.pos : t.projPos;
  if (kind === 'nwslpo') { const ov = [...r.tab].sort((a, b) => rank(a) - rank(b) || a.pos - b.pos).map(t => t.i); ov.forEach((t, i) => { seedNum[t] = i + 1; }); seedOf = s => ov[s.seed - 1]; }
  else { const byC = {}; for (const c of ['East', 'West']) { byC[c] = r.tab.filter(t => t.group === c).sort((a, b) => rank(a) - rank(b) || a.pos - b.pos).map(t => t.i); byC[c].forEach((t, i) => { seedNum[t] = i + 1; }); } seedOf = s => byC[s.conf][s.seed - 1]; }
  const P = MODEL.poProbs(r.att, r.def, r.homeRate, r.awayRate);
  const decide = (t, h, v) => {
    if (!done) return null;
    if (t.kind === 'bo3') { let wh = 0, wv = 0; for (let g = 1; g <= 3; g++) { const res = ko[`${t.id}-G${g}`]; if (!res) continue; let hw = MODEL.realWin(res); if (hw == null) continue; if (g === 2) hw = 1 - hw; if (hw) wh++; else wv++; } return wh >= 2 ? h : wv >= 2 ? v : null; }
    const res = ko[t.id]; if (!res) return null; const hw = MODEL.realWin(res); return hw == null ? null : hw ? h : v;
  };
  const ties = MODEL.poResolve(kind, seedOf, seedNum, pts, decide);
  for (const t of ties) {
    if (t.h == null || t.v == null || t.winner != null) continue;
    if (t.kind === 'bo3') {
      // exact series odds from the games still to play
      const gp = g => g === 2 ? 1 - P.pens(t.v, t.h) : P.pens(t.h, t.v);
      const rec = (g, wh, wv) => { if (wh >= 2) return 1; if (wv >= 2) return 0; const res = done ? ko[`${t.id}-G${g}`] : null;
        let hw = res ? MODEL.realWin(res) : null; if (hw != null && g === 2) hw = 1 - hw;
        if (hw != null) return rec(g + 1, wh + hw, wv + 1 - hw); const p = gp(g); return p * rec(g + 1, wh + 1, wv) + (1 - p) * rec(g + 1, wh, wv + 1); };
      t.pH = rec(1, 0, 0);
    } else t.pH = t.kind === 'pens' ? P.pens(t.h, t.v) : P.single(t.h, t.v, t.neutral);
  }
  return { done, ties, seedNum, ko };
}
function tieCard(k, t, B) {
  const team = (i, isH) => {
    if (i == null) return `<div class="tie-team tbd"><span class="seed"></span><span class="tn">To be decided</span><span></span></div>`;
    const tm = T(k)[i], won = t.winner === i, lost = t.winner != null && !won, p = t.pH == null ? null : isH ? t.pH : 1 - t.pH;
    return `<div class="tie-team ${won ? 'won' : ''} ${lost ? 'lost' : ''}"><span class="seed">${B.seedNum[i]}</span><button class="club-link tn" data-club="${i}">${tchip(k, i)}${esc(nm(k, i))}</button>
      <span class="tp num">${won ? '✓' : lost ? '' : p == null ? '' : pct(p)}</span></div>`;
  };
  const games = t.kind === 'bo3' ? [1, 2, 3] : [0];
  const known = t.h != null && t.v != null;
  const rows = games.map(g => {
    const id = g ? `${t.id}-G${g}` : t.id, res = B.ko[id], host = g === 2 ? t.v : t.h, vis = g === 2 ? t.h : t.v;
    const label = g ? `Game ${g}` : t.neutral ? 'Neutral site' : '';
    const seriesOver = t.kind === 'bo3' && t.winner != null && !res;
    if (!known || seriesOver) return '';
    const txt = res ? `${esc(T(k)[host].abbr)} ${res.hs}–${res.as} ${esc(T(k)[vis].abbr)}${res.hs === res.as ? ` · ${esc(T(k)[res.adv === 'H' ? host : vis].abbr)} on ${t.kind === 'single' ? 'ET/pens' : 'pens'}` : ''}` : `${label ? label + ' · ' : ''}at ${esc(nm(k, host))}`;
    const entry = B.done ? `<button class="enter tiny" data-koenter="${id}">${res ? 'Edit' : 'Enter'}</button>
      <div class="entry" id="koe-${id}" hidden><input inputmode="numeric" id="kh-${id}" value="${res ? res.hs : ''}" aria-label="${esc(nm(k, host))} goals"><span>–</span><input inputmode="numeric" id="ka-${id}" value="${res ? res.as : ''}" aria-label="${esc(nm(k, vis))} goals">
        <select id="kw-${id}" aria-label="Winner if level"><option value="">If level: winner</option><option value="H" ${res && res.adv === 'H' ? 'selected' : ''}>${esc(nm(k, host))}</option><option value="A" ${res && res.adv === 'A' ? 'selected' : ''}>${esc(nm(k, vis))}</option></select>
        <button class="btn primary" data-kosave="${id}">Save</button>${res ? `<button class="btn ghost" data-koclear="${id}">Clear</button>` : ''}</div>` : '';
    return `<div class="tie-game"><span>${txt}</span>${entry}</div>`;
  }).join('');
  const fmt = t.kind === 'bo3' ? 'Best of three · level games go to penalties' : t.kind === 'pens' ? 'Single match · level after 90 goes to penalties' : 'Single match · extra time and penalties';
  return `<article class="tie"><div class="m-top"><span>${esc(t.round)}${t.conf ? ' · ' + esc(t.conf) : ''}</span><span>${fmt}</span></div>${team(t.h, true)}${team(t.v, false)}${rows}</article>`;
}
function viewBracket(k) {
  const B = bracketState(k), r = R[k], rounds = [...new Set(B.ties.map(t => t.round))];
  const champKey = 'champ', top = [...r.tab].sort((a, b) => (b.odds[champKey] || 0) - (a.odds[champKey] || 0)).slice(0, 6);
  const intro = B.done ? 'The regular season is over. Enter each playoff result as it happens; the bracket and title odds update automatically.'
    : `Projected bracket. Seeds come from the projected final ${k === 'nwsl' ? 'table' : 'conference tables'} and update with every result; the bracket locks in once every regular-season result is entered. Percentages are each side's chance of winning the tie if these pairings hold.`;
  return `<section class="section"><h2>${k === 'mls' ? 'MLS Cup Playoffs' : k === 'usl' ? 'USL Championship Playoffs' : 'NWSL Playoffs'}</h2><p class="sub">${intro}</p>
    <div class="race" style="margin-top:14px"><h3>${k === 'mls' ? 'Win MLS Cup' : k === 'usl' ? 'Win the USL Championship' : 'Win the championship'}</h3>${top.map(t => `<div class="bar-row"><button class="t club-link" data-club="${t.i}">${tchip(k, t.i)}<span class="tt">${esc(nm(k, t.i))}</span></button><span class="bar"><i style="width:${(t.odds[champKey] || 0) * 100 / Math.max(top[0].odds[champKey] || 0.01, 0.01)}%"></i></span><span class="v num">${pct(t.odds[champKey] || 0)}</span></div>`).join('')}
      <p class="note" style="margin-top:8px">From 1,000 simulated seasons, playoffs included.</p></div>
    ${rounds.map(rd => `<h3 class="grp">${esc(rd)}</h3><div class="ties">${B.ties.filter(t => t.round === rd).map(t => tieCard(k, t, B)).join('')}</div>`).join('')}</section>`;
}

// ---------------------------------------------------------------- pick 'em (its own tab, kept off the match cards)
function viewPicks(k) {
  const r = R[k], cup = COMPS_CFG[k].cup, known = f => f.h != null && f.a != null;
  const up = r.fx.filter(f => !f.played && !f.postponed && known(f) && f.pick).sort((a, b) => a.sortT - b.sortT).slice(0, 30);
  const done = r.fx.filter(f => f.played && f.pickPts !== undefined).sort((a, b) => b.sortT - a.sortT).slice(0, 30);
  const ev = up.reduce((s, f) => s + (f.pickEV || 0), 0), hits = done.filter(f => f.favorHit).length, favN = done.filter(f => f.favorHit !== undefined).length;
  const when = f => `${fmtDateK(f, {month:'short', day:'numeric'})}${cup ? ' · ' + esc(f.round) : ''}`;
  const aff = f => f.favored ? esc(favLabel(k, f)) : '';
  return `<section class="section"><h2>Pick 'em</h2>
    <div class="slate"><span class="pill">Season <b class="num">${r.pickemPts}</b> pts in ${r.nPlayed} matches</span>${up.length ? `<span class="pill">Next ${up.length}: <b class="num">${ev.toFixed(1)}</b> expected pts</span>` : ''}${favN ? `<span class="pill">Affinity picks <b class="num">${hits}</b> of ${favN}</span>` : ''}</div>
    ${up.length ? `<h3 style="margin-top:16px">Upcoming</h3><div class="card scroll" style="margin-top:8px"><table class="picks"><thead><tr><th>Date</th><th class="club">Match</th><th>Pick</th><th>Exp.</th><th class="sm-hide">Affinity pick</th></tr></thead>
      <tbody>${up.map(f => `<tr data-open="${f.id}"><td>${when(f)}</td><td class="club">${esc(nm(k, f.h))} v ${esc(nm(k, f.a))}</td><td class="num"><b>${f.pick[0]}–${f.pick[1]}</b></td><td class="num">${f.pickEV.toFixed(2)}</td><td class="sm-hide">${aff(f)}</td></tr>`).join('')}</tbody></table></div>` : ''}
    ${done.length ? `<h3 style="margin-top:16px">Scored</h3><div class="card scroll" style="margin-top:8px"><table class="picks"><thead><tr><th>Date</th><th class="club">Match</th><th>Score</th><th>Pick</th><th>Pts</th><th class="sm-hide">Affinity pick</th></tr></thead>
      <tbody>${done.map(f => `<tr><td>${when(f)}</td><td class="club">${esc(nm(k, f.h))} v ${esc(nm(k, f.a))}</td><td class="num">${f.hs}–${f.as}</td><td class="num">${f.pick[0]}–${f.pick[1]}</td><td class="num"><b>${f.pickPts}</b></td><td class="sm-hide">${f.favorHit === undefined ? '' : `${aff(f)} ${f.favorHit ? '✓' : '✗'}`}</td></tr>`).join('')}</tbody></table></div>` : ''}
    <p class="note">Scored on the 90-minute score: ${state.suite.peOutcome} for the right result, ${state.suite.peExact} for the exact score. Entering a result locks in the pick and Affinity pick from before kickoff.</p></section>`;
}
// ---------------------------------------------------------------- cup views
const CUP_ROUNDS = ['Preliminary round', 'First round', 'Second round', 'Third round', 'Fourth round', 'Quarter-final', 'Semi-finals', 'Final'];
function cupRounds(k) {
  const r = R[k], rd = state.mw[k] && state.mw[k].startsWith('Semi') ? 'Semi-finals' : state.mw[k], i = CUP_ROUNDS.indexOf(rd);
  const list = r.fx.filter(f => rd === 'Semi-finals' ? f.round.startsWith('Semi') : f.round === rd).sort((a, b) => (a.sortT || 0) - (b.sortT || 0) || a.tie - b.tie || a.t - b.t);
  return `<section class="section"><div class="mw-head"><div><div class="mw-title">${esc(rd)}</div><div class="mw-dates">${list.length} tie${list.length === 1 ? '' : 's'}${list[0] ? ', ' + fmtDate(list[0].date, {month:'long', day:'numeric'}) : ''}</div></div>
    <div class="mw-nav"><button data-cstep="-1" aria-label="Previous round" ${i <= 0 ? 'disabled' : ''}>‹</button><button data-cstep="1" aria-label="Next round" ${i >= CUP_ROUNDS.length - 1 ? 'disabled' : ''}>›</button></div></div>
    ${matchList(k, list, motwFor(k, list.filter(f => !f.round.endsWith('leg 1'))), 'Tie of the round')}
    <p class="note">Ties level after 90 minutes go straight to penalties (the final has extra time first): enter the 90-minute score and pick the shootout winner. After each draw, set the pairings on the next round.</p></section>`;
}
function cupLeft(k) {
  const r = R[k], t = T(k), alive = [...r.alive].sort((a, b) => r.odds[b].win - r.odds[a].win);
  const mini = v => `<span class="mini"><i style="width:${Math.max(2, v * 48)}px"></i><span class="num">${pct(v)}</span></span>`;
  const out = t.map((x, i) => i).filter(i => !r.alive.includes(i)).sort((a, b) => (t[b].base + t[b].bonus) - (t[a].base + t[a].bonus));
  return `<section class="section"><h2>Clubs left</h2><p class="sub">Chances from 1,000 simulated cups; undrawn rounds are drawn at random each time.</p>
    <div class="card scroll" style="margin-top:14px"><table><thead><tr><th class="club">Club</th><th class="sm-hide">Tier</th><th class="sm-hide">Affinity</th><th>QF</th><th>SF</th><th>Final</th><th>Win</th></tr></thead>
    <tbody>${alive.map(i => `<tr><td class="club"><button class="club-link" data-club="${i}">${dual(k, i)}</button></td><td class="sm-hide" style="color:var(--muted)">${esc(t[i].tier)}</td><td class="num sm-hide">${fmtA(t[i].base + t[i].bonus)}</td><td>${mini(r.odds[i].qf)}</td><td>${mini(r.odds[i].sf)}</td><td>${mini(r.odds[i].final)}</td><td>${mini(r.odds[i].win)}</td></tr>`).join('')}</tbody></table></div>
    <div class="race" style="margin-top:18px;display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap"><div><h3 style="margin:0">Affinity satisfaction</h3><p class="sub" style="margin:4px 0 0">How well the likely runs of the clubs left match your Affinity order.</p></div><div class="mw-title num">${Math.round(r.satisfaction)}</div></div>
    <h3 class="grp">Knocked out (${out.length})</h3><div class="card out-list">${out.map(i => `<div>${esc(t[i].name)}</div>`).join('')}</div></section>`;
}
function cupRaces(k) {
  const r = R[k], alive = [...r.alive].sort((a, b) => r.odds[b].win - r.odds[a].win);
  const big = r.fx.filter(f => !f.played && f.importance !== undefined && !f.round.endsWith('leg 1')).sort((a, b) => b.importance - a.importance).slice(0, 8);
  return `<section class="section"><h2>Trophy race</h2><p class="sub">Chance of lifting the cup at Wembley.</p><div class="races"><div class="race"><h3>Win the cup</h3>
    ${alive.map(i => `<div class="bar-row"><span class="t">${esc(nm(k, i))}</span><span class="bar"><i style="width:${r.odds[i].win * 100 / Math.max(r.odds[alive[0]].win, 0.01)}%"></i></span><span class="v num">${pct(r.odds[i].win)}</span></div>`).join('')}</div></div></section>
    <section class="section"><h2>Biggest ties left</h2><p class="sub">Trophy odds riding on each tie, scaled so the biggest is 1.00.</p>${bigList(k, big, true)}</section>`;
}

// ---------------------------------------------------------------- overview
function tileData(k) {
  const r = R[k], c = COMPS_CFG[k];
  if (!r) return null;
  const upcoming = r.fx.filter(f => !f.played && !f.postponed && f.h != null && f.a != null && f.pick).sort((a, b) => a.sortT - b.sortT);
  const next = upcoming[0];
  if (c.cup) {
    const lead = [...r.alive].sort((a, b) => r.odds[b].win - r.odds[a].win)[0];
    const peN = r.fx.filter(f => f.pickPts !== undefined).length;
    return {peN, h1:['Favorite', lead != null ? nm(k, lead) : '—', lead != null ? pct(r.odds[lead].win) + ' to win the cup' : ''], h2:['Clubs left', String(r.alive.length), 'of 92 that entered'], next, pe:r.pickemPts, sat:r.satisfaction};
  }
  const cfg = COMP[k].cfg, hk = cfg.headline[1];
  const lead = [...r.tab].sort((a, b) => (b.odds[hk] || 0) - (a.odds[hk] || 0))[0];
  let line;
  if (k === 'unl') { const at = [...r.tab].filter(t => t.group[0] === 'A').sort((a, b) => (b.odds.down || 0) - (a.odds.down || 0))[0]; line = ['Relegation from A', nm(k, at.i), pct(at.odds.down || 0) + ' to drop to League B']; }
  else if (k === 'mls' || k === 'usl') { const n = k === 'mls' ? 9 : 8; const g = ['East', 'West'].map(G => r.tab.filter(t => t.group === G).map(t => t.projPts).sort((a, b) => b - a)[n - 1]); line = [cfg.line[0], `E ${g[0].toFixed(1)} · W ${g[1].toFixed(1)}`, `Projected ${n}th in each conference`]; }
  else { const pp = r.tab.map(t => t.projPts).sort((a, b) => b - a); line = [cfg.line[0], pp[cfg.line[1] - 1].toFixed(1) + ' pts', cfg.line[2]]; }
  return {peN:r.fx.filter(f => f.pickPts !== undefined).length, h1:[cfg.headline[0], nm(k, lead.i), pct(lead.odds[hk] || 0) + ' ' + cfg.headline[2]], h2:line, next, pe:r.pickemPts, sat:r.satisfaction, played:r.nPlayed};
}
// Live: every match marked in progress, plus matches that have kicked off (by the schedule) with no score yet.
const liveNow = () => ORDER.filter(k => R[k]).flatMap(k => R[k].fx.filter(f => f.live).map(f => ({k, f})));
const kickedOff = () => { const now = Date.now(); return ORDER.filter(k => R[k]).flatMap(k => R[k].fx.filter(f => !f.played && !f.live && !f.postponed && f.h != null && f.a != null && f.kt && now >= f.kt && now <= f.kt + 150 * 6e4).map(f => ({k, f}))); };
function viewLive() {
  const byTime = (a, b) => (a.f.kt || 0) - (b.f.kt || 0) || ORDER.indexOf(a.k) - ORDER.indexOf(b.k);
  const live = liveNow().sort(byTime), ko = kickedOff().sort(byTime);
  const cards = list => `<div class="mlist live-list"><div class="mday">${list.map(({k, f}) => liveCard(k, f)).join('')}</div></div>`;
  if (!ORDER.every(k => R[k])) return '<div class="loading">Crunching the numbers…</div>';
  if (!live.length && !ko.length) {
    const next = ORDER.flatMap(k => R[k].fx.filter(f => !f.played && !f.postponed && f.kt && f.kt > Date.now() && f.h != null && f.a != null).map(f => ({k, f}))).sort(byTime).slice(0, 5);
    return `<section class="section"><h2>Nothing live right now</h2><p class="sub">Matches show up here when they kick off. Mark one in progress (Update live on its card) to track the score and live win chances.</p>
      ${next.length ? `<h3 style="margin-top:18px">Next kickoffs</h3><div class="card" style="margin-top:10px">${next.map(({k, f}) => `<div class="feed-row" data-go="${k}:${f.id}" role="button" tabindex="0" style="--c:${DOT[k]}">
        <span class="d">${whenLabel(f)}</span><span class="c">${esc(COMPS_CFG[k].name)}</span><span class="m">${star(k, f.h)}${esc(nm(k, f.h))} v ${esc(nm(k, f.a))}${star(k, f.a)}</span><span class="p num"></span><span class="imp"></span></div>`).join('')}</div>` : ''}</section>`;
  }
  return `${live.length ? `<section class="section"><h2><span class="live-dot"></span>Live now</h2><p class="sub">Tap +1 for a goal, the red card for a sending-off, and Half-time or Full time as the match goes on. Tap a scoreboard for the full card.</p>${cards(live)}</section>` : ''}
    ${ko.length ? `<section class="section"><h2>Kicked off</h2><p class="sub">Past their kickoff time with no live score yet. Enter the minute and score to follow one live, or the final score when it's over.</p>${cards(ko)}</section>` : ''}`;
}
function viewHome() {
  // Compact competition tiles (2 per row on a phone): colour, name and the headline race.
  const tiles = ORDER.map(k => {
    const d = tileData(k), c = COMPS_CFG[k];
    const head = `<div class="tile-top"><i style="--c:${DOT[k]}"></i><b>${esc(c.name)}</b></div>`;
    if (!d) return `<div class="tile">${head}<div class="tile-body"><span class="tile-sub">Crunching…</span></div></div>`;
    return `<button class="tile" data-view="${k}">${head}<div class="tile-body">
      <span class="tile-k">${esc(d.h1[0])}</span><span class="tile-v">${esc(d.h1[1])}</span><span class="tile-sub">${esc(d.h1[2])}</span>
</div></button>`;
  }).join('');
  const feed = ORDER.filter(k => R[k]).flatMap(k => R[k].fx.filter(f => !f.played && !f.postponed && f.h != null && f.a != null && f.pick).map(f => ({k, f}))).sort((a, b) => a.f.sortT - b.f.sortT || ORDER.indexOf(a.k) - ORDER.indexOf(b.k)).slice(0, 20);
  const big = ORDER.filter(k => R[k]).map(k => { const f = R[k].fx.filter(x => !x.played && x.importance !== undefined && !(x.round || '').endsWith('leg 1')).sort((a, b) => b.importance - a.importance)[0]; return f ? {k, f} : null; }).filter(Boolean)
    .sort((a, b) => a.f.sortT - b.f.sortT || ORDER.indexOf(a.k) - ORDER.indexOf(b.k));
  const motd = {}; for (const {k, f} of feed) { const d = fmtDateK(f); if (f.importance !== undefined && (!motd[d] || headline(f) > headline(motd[d].f))) motd[d] = {k, f}; }
  const isMotd = (k, f) => { const m = motd[fmtDateK(f)]; return m && m.k === k && m.f.id === f.id; };
  const byClub = {};
  for (const k of ORDER.filter(c => R[c])) for (const i of (state.favs[k] || [])) {
    const name = T(k)[i].name, e = byClub[name] = byClub[name] || {name, comps:new Set(), best:null};
    e.comps.add(k);
    const nxt = R[k].fx.filter(f => !f.played && !f.postponed && (f.h === i || f.a === i) && f.h != null && f.a != null).sort((a, b) => a.sortT - b.sortT)[0];
    if (nxt && (!e.best || nxt.sortT < e.best.f.sortT)) e.best = {k, i, f:nxt};
  }
  const mine = Object.values(byClub).filter(e => e.best).map(e => Object.assign({}, e.best, {also:[...e.comps].filter(c => c !== e.best.k)})).sort((a, b) => a.f.sortT - b.f.sortT);
  const yours = `<section class="section"><h2>Your clubs</h2><p class="sub">${mine.length ? 'The very next match for each club you follow, whichever competition it\'s in. Following a club in one competition follows it everywhere it plays.' : 'Follow clubs from any club card (tap a club name) or a competition\'s Settings tab, and their next matches show up here.'}</p>
    ${mine.length ? feedList(mine, x => x.also.length ? {cap:`also following in ${x.also.map(c => esc(COMPS_CFG[c].name)).join(', ')}`} : null, true) : ''}</section>`;
  const lives = ORDER.filter(k => R[k]).flatMap(k => R[k].fx.filter(f => f.live).map(f => ({k, f})));
  const liveSec = lives.length ? `<section class="section"><h2><span class="live-dot"></span>Live now</h2><p class="sub">Matches you've marked in progress, with live win chances.</p>
    ${feedList(lives)}</section>` : '';
  return `${liveSec}${yours}
    <section class="section"><h2>What's next</h2><p class="sub">The next 20 unplayed matches everywhere. Each day's match of the day is marked in gold: the best blend of what's at stake and how evenly matched the sides are. Dimmed kickoff times have passed: enter those results in their competition.</p>
      ${feed.length ? feedList(feed, x => isMotd(x.k, x.f) ? {motd:true, cap:'<span class="cap-motw">Match of the day</span>'} : null, true) : '<div class="loading">Crunching…</div>'}</section>
    <section class="section"><h2>Competitions</h2><p class="sub">Tap one to open it.</p><div class="tiles">${tiles}</div></section>
    <section class="section"><div class="sec-head"><h2>Affinity ranking</h2><button class="linkish" data-view="rank">All ${rankList().length} →</button></div><p class="sub">Your top 10 across every competition, coloured by league.</p>
      <div class="card rank" style="margin-top:12px">${rankList().slice(0, 10).map((e, n) => `<div class="rank-row" style="--c:${DOT[e.k]}"><span class="num rk">${n + 1}</span>
      <span class="who"><button class="club-link" ${e.x != null ? `data-xnat="${e.x}"` : e.xc != null ? `data-xclub="${e.xc}"` : `data-club="${e.k}:${e.i}"`}>${nchip(e.t.name, e.t.color, e.k)}${esc(e.t.name)}</button><small><i></i>${esc(rankLabel(e.k))}</small></span><span></span><span class="num sc">${fmtA(affOf(e.t))}</span></div>`).join('')}</div></section>
    <section class="section"><h2>Biggest match left in each competition</h2><p class="sub">The most important match left in each competition, soonest first.</p>
      ${feedList(big, x => ({cap:`${esc(fmtDateK(x.f))}${x.f.mattersTo != null ? ` · matters most to ${esc(nm(x.k, x.f.mattersTo))}` : ''}`}))}</section>`;
}


// "Why it matters" as one small table: each club's biggest race or two, its chance now and after a win,
// a draw or a loss does to it. Importance itself is on the match odds card just below.
function narrative(k, f) {
  const r = R[k], cfg = COMP[k].cfg;
  if (COMPS_CFG[k].cup) {
    if (f.rawH == null) return '';
    const row = (i, raw) => `<tr><td class="wt-name">${tchip(k, i)}${esc(nm(k, i))}</td><td class="num">${pct(r.odds[i].win)}</td><td class="num"><b>${pct(raw)}</b></td></tr>`;
    return `<p class="why-lead">Chance of winning the cup. Lose and they're out.</p><table class="why-t"><thead><tr><th></th><th>Now</th><th>If through</th></tr></thead><tbody>${row(f.h, f.rawH)}${row(f.a, f.rawA)}</tbody></table>`;
  }
  if (!f.imp) return '';
  const left = r.fx.filter(x => !x.played && x.importance !== undefined).sort((a, b) => b.importance - a.importance);
  const rank = left.findIndex(x => x.id === f.id) + 1, roundRank = r.fx.filter(x => x.mw === f.mw && !x.played && x.importance > f.importance).length + 1;
  const lead = `<p class="why-lead">${rank === 1 ? 'The biggest match left' : `#${rank} of ${left.length} matches left`}${roundRank === 1 && rank !== 1 ? `, the biggest ${COMPS_CFG[k].round === 'Week' ? 'this week' : 'this round'}` : ''}.</p>`;
  const anyDraw = ['h', 'a'].some(sd => Object.values(f.imp[sd].cond).some(c => c && c.pd != null));
  const rows = (side, i) => {
    const t = r.tab[i], im = f.imp[side];
    const zs = cfg.zones.filter(z => z.w && im.parts[z.key] >= 0.05).sort((a, b) => b.w * im.parts[b.key] - a.w * im.parts[a.key]).slice(0, 2);
    const head = `<tr class="wt-club"><th colspan="${anyDraw ? 5 : 4}">${tchip(k, i)}${esc(nm(k, i))}${zs.length ? '' : ' <span>· little riding on it</span>'}</th></tr>`;
    return head + zs.map(z => { const c = im.cond[z.key];
      return `<tr><td>${esc(z.label)}</td><td class="num">${pct(t.odds[z.key] || 0)}</td><td class="num"><b>${pct(c.pw)}</b></td>${anyDraw ? `<td class="num">${c.pd != null ? pct(c.pd) : ''}</td>` : ''}<td class="num">${pct(c.pl)}</td></tr>`; }).join('');
  };
  return lead + `<table class="why-t"><thead><tr><th></th><th>Now</th><th>Win</th>${anyDraw ? '<th>Draw</th>' : ''}<th>Lose</th></tr></thead><tbody>${rows('h', f.h)}${rows('a', f.a)}</tbody></table>`;
}

// ---------------------------------------------------------------- detail
function openDetail(k, id) {
  const f = R[k].fx[id]; if (!f.g) return;
  const mx = Math.max(...[0, 1, 2, 3, 4, 5].flatMap(h => [0, 1, 2, 3, 4, 5].map(a => f.g[h][a])));
  let heat = `<div class="ax"></div>${[0, 1, 2, 3, 4, 5].map(a => `<div class="ax">${a}</div>`).join('')}`;
  for (let h = 0; h <= 5; h++) { heat += `<div class="ax">${h}</div>`; for (let a = 0; a <= 5; a++) { const p = f.g[h][a], al = 0.08 + 0.85 * p / mx;
    const cls = (f.pred && f.pred[0] === h && f.pred[1] === a ? ' pred' : '');
    heat += `<div class="c${cls}" style="background:color-mix(in srgb, #0A84FF ${Math.round(al * 100)}%, transparent);color:#fff">${(p * 100).toFixed(1)}</div>`; } }
  const zones = COMP[k].cfg && COMP[k].cfg.zones ? COMP[k].cfg.zones.filter(z => z.w) : [];
  const t = i => T(k)[i], P = f.live || f, fin = f.played, cup = COMPS_CFG[k].cup;
  // Head-to-head bar, Apple Sports style: the two numbers either side of the label, one bar split in the club colours.
  const sbar = (label, a, b, fmt) => `<div class="srow"><div class="sl"><b class="num">${fmt(a)}</b><span>${label}</span><b class="num">${fmt(b)}</b></div>
    <div class="sb"><i style="flex:${a + b > 0 ? Math.round(1000 * a / (a + b)) : 1} 1 0"></i><i style="flex:${a + b > 0 ? Math.round(1000 * b / (a + b)) : 1} 1 0"></i></div></div>`;
  const sc = s => fin ? (s === 'h' ? f.hs : f.as) : f.live ? (s === 'h' ? f.live.h : f.live.a) : '';
  const lose = s => fin && (s === 'h' ? f.hs < f.as || (f.hs === f.as && f.pens != null && f.pens !== f.h) : f.as < f.hs || (f.hs === f.as && f.pens != null && f.pens !== f.a));
  const status = f.live ? `<b class="hero-live"><span class="live-dot"></span>${liveLabel(k, f)}</b>` : fin ? `<b>Final</b>${f.pens != null && f.hs === f.as ? `<small>${esc(nm(k, f.pens))} on pens</small>` : f.awarded ? '<small>Awarded</small>' : ''}`
    : `<b class="num">${f.kt ? fmtTime(f.kt) : 'TBC'}</b>`;
  const side = s => { const i = s === 'h' ? f.h : f.a, w = cup && f.advH != null ? (s === 'h' ? f.advH : 1 - f.advH) : (s === 'h' ? P.pH : P.pA);
    return `<div class="hero-team">${fin || f.live ? `<span class="hero-s num ${lose(s) ? 'lose' : ''}">${sc(s)}</span>` : ''}${crest(k, i, 64)}<b>${esc(nm(k, i))}${f.live ? reds(f.live.rc[s === 'h' ? 0 : 1]) : ''}</b>${w != null ? `<small class="num">${pct(w)} ${cup && f.advH != null ? 'to go through' : 'win'}</small>` : ''}</div>`; };
  $('#sheet').style.cssText = `--hc:${t(f.h).color || '#8E8E93'};--ac:${t(f.a).color || '#8E8E93'}`;
  $('#sheet').innerHTML = `<div class="hero">
      <div class="hero-top"><span>${esc(COMPS_CFG[k].name)}</span><button class="close" aria-label="Close" id="close">✕</button></div>
      <div class="hero-date">${fmtDateK(f, {weekday:'long', month:'long', day:'numeric'})}</div>
      <div class="hero-grid">${side('h')}<div class="hero-mid">${status}</div>${side('a')}</div>
      ${fin ? '' : `<div class="hero-tv">Watch on ${esc(tvLabel(k))}</div>`}</div>
    <div class="sheet-body">
    ${f.live ? `<div class="why live"><h4><span class="live-dot"></span>Live, ${liveLabel(k, f)}</h4>
      <p>Before kickoff it was ${pct(f.pH)} / ${pct(f.pD)} / ${pct(f.pA)}. Expected goals still to come: ${f.live.rh.toFixed(2)} and ${f.live.ra.toFixed(2)}.</p></div>` : ''}
    ${!fin && (f.imp || f.rawH != null) ? `<div class="why"><h4>Why it matters</h4>${narrative(k, f)}</div>` : ''}
    <div class="scard"><h4>${fin ? 'Before kickoff' : 'Match odds'}</h4>
      ${sbar(fin ? 'Win chance' : 'Win chance' + (f.live ? ' (live)' : ''), (fin ? f : P).pH, (fin ? f : P).pA, pct)}
      <div class="sdraw num">Draw ${pct((fin ? f : P).pD)}</div>
      ${sbar('Expected goals', f.lh, f.la, v => v.toFixed(2))}
      ${f.advH != null ? sbar('Goes through', f.advH, 1 - f.advH, pct) : ''}
      ${f.importance !== undefined ? `<div class="sdraw num">Importance ${f.importance.toFixed(2)}</div>` : ''}</div>
    ${f.imp && zones.length ? `<div class="scard"><h4>What's riding on it</h4><p class="sub" style="margin:-4px 0 6px">Change in each club's odds between winning and losing.</p>
      ${zones.map(z => sbar(esc(z.label), f.imp.h.parts[z.key] || 0, f.imp.a.parts[z.key] || 0, v => (v * 100).toFixed(0))).join('')}</div>` : ''}
    <div class="scard"><h4>Scoreline chances (%)</h4><div class="sub" style="margin:0">${esc(nm(k, f.h))} goals down, ${esc(nm(k, f.a))} across. Outlined = most likely score.</div><div class="heat num">${heat}</div></div>
    </div>`;
  if (!$('#detail').open) $('#detail').showModal(); $('#close').onclick = () => $('#detail').close();
}


// Component ratings read to the tenth (7.0, 6.4), except the ends of the scale (0, 10).
const fmtR = v => v === 0 || v === 10 ? String(v) : Number(v).toFixed(1);
// Overall Affinity reads to the tenth too, except the ends of its scale (0, 100).
const fmtA = v => { const r = Math.round(v * 10) / 10; return r === 0 || r === 100 ? String(r) : r.toFixed(1); };
const FACTORS = [['Values', 'V', 26], ['Culture', 'C', 23], ['History', 'H', 16], ['Team', 'S', 15], ['Ownership', 'O', 10]];
function affBreakdown(k, t) {
  const h = t.hai, fs = FACTORS.reduce((s, [, key, w]) => s + w * h[key], 0) / 90 * 10;
  const spark = h.ps ? (() => { const last = h.pl || '', cal = !last.includes('-'), y = parseInt(last, 10);
    const lab = j => cal ? String(y - 9 + j) : `${String(y - 9 + j).slice(2)}/${String(y - 8 + j).slice(2)}`;
    return `<span class="spark" aria-label="Season scores, oldest to newest">${h.ps.map((x, j) => `<i title="${lab(j)}: ${x == null ? 'no season' : x.toFixed(1)}" class="${x == null ? 'none' : ''}" style="height:${x == null ? 8 : Math.max(8, x * 10)}%"></i>`).join('')}</span>`; })() : '';
  // Added after the factors and track record, in two groups: hard lines (the penalties left in the note; its other
  // lines are research history and stay out) and connection (distance, local teams, linked clubs, hometown or heritage).
  const hard = [], conn = [];
  if (h.adj) {
    let left = h.adj;
    for (const part of (h.note || '').split(';')) { const m = part.trim().match(/^(.*?)\s*([+−-]\d+(?:\.\d+)?)$/); if (m && m[1] && !/^(Rules|Folded|Cascadia)/.test(m[1])) { const v = parseFloat(m[2].replace('−', '-')); hard.push([m[1], v]); left -= v; } }
    if (Math.abs(left) > 0.05) hard.push([hard.length ? 'Other' : 'Hard lines', Math.round(left * 10) / 10]);
  }
  for (const [l, v] of h.us || []) conn.push([l, v]);
  for (const [y, v] of h.links || []) conn.push([`Linked to ${y}`, v]);
  if (t.bonus) conn.push([k === 'unl' ? (t.region === 'Home nation' ? 'Home nation' : 'Heritage') : 'Hometown', t.bonus]);
  const tot = xs => Math.round(xs.reduce((x, [, v]) => x + v, 0) * 10) / 10, hardT = tot(hard), connT = tot(conn);
  const sum = [`${fs.toFixed(1)} factors`];
  if (h.k != null) sum.push(`× ${h.k.toFixed(2)} track record`);
  if (hardT) sum.push(`${hardT < 0 ? '−' : '+'} ${Math.abs(hardT)} hard lines`);
  if (connT) sum.push(`${connT < 0 ? '−' : '+'} ${Math.abs(connT)} connection`);
  if (fs * (h.k ?? 1) + h.adj > 100) sum.push('(capped at 100)');
  const group = (title, xs, total) => xs.length ? `<div class="hb-items"><div class="hb-items-head"><span>${title}</span><b class="num ${total < 0 ? 'neg' : ''}">${signed(total)}</b></div>${xs.map(([l, v]) => `<div class="hb-item"><span>${esc(l)}</span><b class="num ${v < 0 ? 'neg' : ''}">${signed(v)}</b></div>`).join('')}</div>` : '';
  const squad = h.tb ? (h.dom ? `${Math.round(h.dom[0] * 100)}% · league ${Math.round(h.dom[1] * 100)}%` : (h.clubs || []).slice(0, 2).map(([c]) => esc(c)).join(', ')) : '';
  return `<h4 style="margin-top:18px">Affinity ${fmtA(affOf(t))}</h4><p class="aff-sum">${sum.join(' ')}</p><div class="hai-break">
    ${FACTORS.map(([l, key, w]) => `<div class="hb"><span>${l} <small>${w}%</small></span><span class="bar"><i style="width:${h[key] * 10}%"></i></span><b class="num">${fmtR(h[key])}</b></div>` +
      (key === 'S' && h.tb ? `<div class="hb hb-sub"><span>${h.dom ? 'Homegrown' : 'Club links'}</span><span>${squad}</span><b class="num ${h.tb < 0 ? 'neg' : ''}">${signed(h.tb)}</b></div>` : '') +
      (key === 'S' && h.py && h.py.t ? `<div class="hb hb-sub"><span>Players</span><span>${(h.py.sq || []).map(esc).join(', ')}</span><b class="num ${h.py.t < 0 ? 'neg' : ''}">${signed(h.py.t)}</b></div>` : '') +
      (key === 'H' && h.py && h.py.h ? `<div class="hb hb-sub"><span>Icons</span><span>${(h.py.ic || []).map(esc).join(', ')}</span><b class="num ${h.py.h < 0 ? 'neg' : ''}">${signed(h.py.h)}</b></div>` : '')).join('')}
    ${h.P != null ? `<div class="hb hb-tr"><span>Track record <small>×${h.k.toFixed(2)}</small></span>${spark}<b class="num">${h.P.toFixed(1)}</b></div>` : ''}
    ${group('Hard lines', hard, hardT)}${group('Connection', conn, connT)}</div>`;
}
function openClub(k, i) {
  const r = R[k], cup = COMPS_CFG[k].cup, t = T(k)[i];
  const mine = r.fx.filter(f => f.h === i || f.a === i).sort((a, b) => a.sortT - b.sortT || a.id - b.id);
  const up = mine.filter(f => !f.played), done = mine.filter(f => f.played);
  const opp = f => f.h === i ? f.a : f.h, home = f => f.h === i;
  const res = f => { const gf = home(f) ? f.hs : f.as, ga = home(f) ? f.as : f.hs; return gf > ga ? 'W' : gf < ga ? 'L' : 'D'; };
  const form = done.slice(-5).map(f => `<span class="form f${res(f)}" title="${esc(fmtDate(f.date))} ${home(f) ? 'v' : 'at'} ${esc(nm(k, opp(f)))} ${f.hs}–${f.as}">${res(f)}</span>`).join('');
  const rowUp = f => {
    const w = f.pH == null ? null : home(f) ? f.pH : f.pA, l = f.pH == null ? null : home(f) ? f.pA : f.pH;
    return `<div class="cf-row" data-open="${f.id}" role="button" tabindex="0"><span class="d">${fmtDateK(f)}<small>${f.kt ? fmtTime(f.kt) : 'TBC'}</small></span>
      <span class="o">${home(f) ? 'v' : 'at'} <b>${esc(f.h == null || f.a == null ? 'TBD' : nm(k, opp(f)))}</b>${cup ? `<small>${esc(f.round)}</small>` : ''}</span>
      <span class="wdl num">${w == null ? '' : `<span class="w">${pct(w)}</span> <span class="dr">${pct(f.pD)}</span> <span class="l">${pct(l)}</span>`}</span>
      <span class="pk num"></span>
      <span class="imp">${f.importance !== undefined ? `<span class="imp-track"><span class="imp-fill" style="width:${f.importance * 100}%"></span></span>` : ''}</span></div>`;
  };
  const rowDone = f => `<div class="cf-row" ${f.g ? `data-open="${f.id}" role="button" tabindex="0"` : ''}><span class="d">${fmtDate(f.date)}</span>
      <span class="o">${home(f) ? 'v' : 'at'} <b>${esc(nm(k, opp(f)))}</b>${cup ? `<small>${esc(f.round)}</small>` : ''}</span>
      <span class="wdl num"><span class="form f${res(f)}">${res(f)}</span> ${home(f) ? f.hs + '–' + f.as : f.as + '–' + f.hs}</span><span class="pk num"></span><span></span></div>`;
  let stats = '';
  if (!cup) {
    const row = r.tab[i], cfg = COMP[k].cfg;
    stats = `<div class="club-stats"><div><div class="k">Now</div><div class="v">${row.pos}${ord(row.pos)} · ${row.Pts} pts</div></div>
      <div><div class="k">Projected</div><div class="v">${row.projPos}${ord(row.projPos)} · ${row.projPts.toFixed(0)} pts</div></div>
      ${cfg.cols.map(c => `<div><div class="k">${esc(colLabel(k, c))}</div><div class="v">${pct(row.odds[c] || 0)}</div></div>`).join('')}
      <div><div class="k">Affinity</div><div class="v">${fmtA(t.base + t.bonus)}</div></div></div>`;
  } else {
    const o = r.odds[i];
    stats = `<div class="club-stats"><div><div class="k">Status</div><div class="v">${r.alive.includes(i) ? 'Still in' : 'Knocked out'}</div></div>
      ${r.alive.includes(i) ? `<div><div class="k">Win the cup</div><div class="v">${pct(o.win)}</div></div><div><div class="k">Reach final</div><div class="v">${pct(o.final)}</div></div>` : ''}
      <div><div class="k">Affinity</div><div class="v">${fmtA(t.base + t.bonus)}</div></div></div>`;
  }
  $('#sheet').style.cssText = `--hc:${t.color || '#8E8E93'};--ac:${t.color || '#8E8E93'}`;
  $('#sheet').innerHTML = `<div class="hero club"><div class="hero-top"><span>${esc(COMPS_CFG[k].name)}${t.group ? ' · ' + (k === 'mls' ? esc(t.group) + 'ern Conference' : 'Group ' + esc(t.group)) : ''}</span><button class="close" aria-label="Close" id="close">✕</button></div>
      <div class="club-hero">${crest(k, i, 72)}<h2>${esc(t.name)}</h2>
      <div class="club-meta">${form ? `<div class="form-row">${form}</div>` : ''}<button class="follow ${isFav(k, i) ? 'on' : ''}" data-fk="${k}" data-follow="${i}">${isFav(k, i) ? '★ Following' : '☆ Follow'}</button></div></div></div>
    <div class="sheet-pad">${stats}
    ${t.hai ? affBreakdown(k, t) : ''}
    <h4 style="margin-top:18px">Upcoming (${up.length})</h4>
    ${up.length ? `<div class="cf-head"><span>Date</span><span>Opponent</span><span>Win · Draw · Loss</span><span></span><span>Importance</span></div><p class="note" style="margin:6px 0 0">Scores are shown with ${esc(t.short || t.name)} first.</p>${up.map(rowUp).join('')}` : '<p class="note">No fixtures left.</p>'}
    ${done.length ? `<h4 style="margin-top:18px">Results (${done.length})</h4>${done.slice().reverse().map(rowDone).join('')}` : ''}</div>`;
  if (!$('#detail').open) $('#detail').showModal(); $('#close').onclick = () => $('#detail').close();
}

// Full-time result (Save, or the Full time button on a live card).
function saveResult(k, id, h, a) {
  if (!(Number.isInteger(h) && Number.isInteger(a) && h >= 0 && a >= 0)) return;
  if (R[k] && R[k].fx[id]) lockMotw(k, roundKey(k, R[k].fx[id]));
  const f = R[k].fx[id], prev = state.results[k][id];
    if (COMPS_CFG[k].cup) {
      const pwEl = $('#pw-' + id), pw = pwEl && pwEl.value !== '' ? +pwEl.value : null;
      const lock = f.played ? (prev && prev.length >= 6 ? prev.slice(3) : null) : (f.pick ? [f.pick[0], f.pick[1], f.favored] : null);
      state.results[k][id] = lock ? [h, a, pw, ...lock] : [h, a, pw];
    } else {
      const lock = f.played ? (prev && prev.length >= 5 ? prev.slice(2) : null) : [f.pick[0], f.pick[1], f.favored];
      state.results[k][id] = lock ? [h, a, ...lock] : [h, a];
      delete state.live[k][id];
      const aw = $('#aw-' + id); const st = state.status[k][id] = Object.assign({}, state.status[k][id]);
      delete st.p; if (aw && aw.checked) st.aw = 1; else delete st.aw;
    }
  update(k); render(); save(k);
}
// One-tap match events on a live card.
function liveEvent(k, id, ev) {
  const now = Date.now(), f = R[k] && R[k].fx[id], L = state.live[k][id];
  if (!f) return;
  if (ev === 'ft') { if (L) saveResult(k, id, L.h, L.a); return; }
  lockMotw(k, roundKey(k, f));
  if (ev === 'ko') state.live[k][id] = {h:0, a:0, ph:'1H', t:f.kt && now - f.kt > 5 * 6e4 ? f.kt : now, m0:1};
  else if (!L) return;
  else if (ev === 'ht') state.live[k][id] = {h:L.h, a:L.a, ph:'HT', t:now, rc:L.rc};
  else if (ev === 'mm' || ev === 'mp') {
    // Nudge the clock a minute back or forward. A running clock shifts its start; a guessed or fixed one restarts
    // from the minute shown, so the nudge always moves what's on screen. Never before 1' (first half) or 46' (second).
    const c = clock(L, f.kt, now), d = ev === 'mp' ? 1 : -1;
    if (c.ht || c.stale) return;
    if (L.t && !c.est && L.ph === c.ph) {
      const m = L.m0 + (now - L.t) / 6e4, floor = c.ph === '1H' ? 1 : 46;
      if (d < 0 && Math.floor(m) <= floor) return;
      state.live[k][id] = Object.assign({}, L, {t:L.t - d * 6e4});
    } else {
      const m = Math.max(c.ph === '1H' ? 1 : 46, (c.ph === '1H' ? Math.min(c.min, 45) : c.min) + d);
      state.live[k][id] = {h:L.h, a:L.a, ph:c.ph, t:now, m0:m, rc:L.rc};
    }
  }
  else if (ev === 'sh') state.live[k][id] = {h:L.h, a:L.a, ph:'2H', t:now, m0:46, rc:L.rc};
  else if (ev === 'gh' || ev === 'ga' || ev === 'rh' || ev === 'ra') {
    // goals and red cards keep the clock; an old fixed-minute entry starts running from its minute
    const c = clock(L, f.kt), base = L.t ? L : Object.assign(liveAt(L.h, L.a, c.ht ? 'HT' : String(c.min), now), {rc:L.rc});
    const rc = L.rc || [0, 0];
    state.live[k][id] = Object.assign({}, base, ev === 'gh' ? {h:L.h + 1} : ev === 'ga' ? {a:L.a + 1} : {rc:ev === 'rh' ? [rc[0] + 1, rc[1]] : [rc[0], rc[1] + 1]});
  }
  update(k); render(); save(k);
}
// ---------------------------------------------------------------- events
document.addEventListener('click', e => {
  const t = e.target.closest('[data-heart],[data-heartnote],[data-signin],[data-signout],[data-ev],[data-top],[data-adjadd],[data-adjdel],[data-koenter],[data-kosave],[data-koclear],[data-unllg],[data-live],[data-unlive],[data-pp],[data-unpp],[data-move],[data-follow],[data-club],[data-rankf],[data-rankmode],[data-plf],[data-plopen],[data-natf],[data-xnat],[data-xclub],[data-tmode],[data-region],[data-view],[data-tab],[data-open],[data-enter],[data-save],[data-clear],[data-step],[data-cstep],[data-reset],[data-go],[data-draw]');
  if (!t) return;
  const card = t.closest('#main [data-fx]');
  // On Live, a match card's buttons act on that card's competition.
  const k = isHub(state.view) && card ? card.dataset.fx.split(':')[0] : state.view;
  scopeEl = card; queueMicrotask(() => { scopeEl = null; });
  anchor = card ? {key:card.dataset.fx, top:card.getBoundingClientRect().top} : null; queueMicrotask(() => { anchor = null; });
  if (t.dataset.top) { window.scrollTo({top:0, behavior:'smooth'}); return; }
  if (t.dataset.heart) { const [id, v] = t.dataset.heart.split(':'); const h = state.heart[k] = state.heart[k] || {}, e = h[id] || {};
    h[id] = e.s === v ? Object.assign({}, e, {s:null}) : Object.assign({}, e, {s:v, t:Date.now()}); if (!h[id].s && !h[id].note) delete h[id]; render(); save(k); return; }
  if (t.dataset.heartnote) { const id = t.dataset.heartnote, el = document.getElementById('hn-' + id), h = state.heart[k] = state.heart[k] || {};
    h[id] = Object.assign({}, h[id], {note:(el ? el.value : '').trim().slice(0, 300)}); render(); save(k); return; }
  if (t.dataset.signin) { signIn(); return; }
  if (t.dataset.signout) { signOut(); return; }
  if (t.dataset.adjadd) { const i = +$('#adj-club').value, p = +$('#adj-sign').value * Math.abs(parseInt(String($('#adj-pts').value).replace(/[^0-9]/g, ''), 10)), n = $('#adj-note').value.trim();
    if (!Number.isInteger(p) || p === 0) return; const st = state.settings[k]; st.adj = [...(st.adj || []), {i, p, n}]; update(k); render(); save(k); return; }
  if (t.dataset.adjdel) { const st = state.settings[k]; st.adj = (st.adj || []).filter((_, n) => n !== +t.dataset.adjdel); update(k); render(); save(k); return; }
  if (t.dataset.koenter) { const el = document.getElementById('koe-' + t.dataset.koenter); el.hidden = !el.hidden; return; }
  if (t.dataset.kosave) { const id = t.dataset.kosave, h = parseInt(document.getElementById('kh-' + id).value, 10), a2 = parseInt(document.getElementById('ka-' + id).value, 10), w = document.getElementById('kw-' + id).value;
    if (!(Number.isInteger(h) && Number.isInteger(a2) && h >= 0 && a2 >= 0)) return; if (h === a2 && !w) { alert('Level after 90 minutes: pick who went through.'); return; }
    state.ko[k] = state.ko[k] || {}; state.ko[k][id] = {hs:h, as:a2, adv: h === a2 ? w : null}; update(k); render(); save(k); return; }
  if (t.dataset.koclear) { delete state.ko[k][t.dataset.koclear]; update(k); render(); save(k); return; }
  if (t.dataset.unllg) { state.unlLeague = t.dataset.unllg; render(); return; }
  if (t.dataset.live) {
    if (R[k] && R[k].fx[+t.dataset.live]) lockMotw(k, roundKey(k, R[k].fx[+t.dataset.live]));
    const id = +t.dataset.live, h = parseInt($('#hs-' + id).value, 10), a2 = parseInt($('#as-' + id).value, 10), raw = $('#mn-' + id).value.trim().toUpperCase();
    const ht = raw === 'HT', mn = ht ? 45 : parseInt(raw, 10);
    if (!(Number.isInteger(h) && Number.isInteger(a2) && h >= 0 && a2 >= 0 && Number.isInteger(mn) && mn >= 0)) return;
    const rd = s => { const v = parseInt(($('#' + s + '-' + id) || {}).value, 10); return Number.isInteger(v) && v >= 0 ? Math.min(v, 5) : 0; };
    const rc = [rd('rch'), rd('rca')];
    state.live[k][id] = Object.assign(liveAt(h, a2, ht ? 'HT' : raw), rc[0] || rc[1] ? {rc} : {}); update(k); render(); save(k); return;
  }
  if (t.dataset.unlive) { delete state.live[k][+t.dataset.unlive]; update(k); render(); save(k); return; }
  if (t.dataset.pp || t.dataset.unpp || t.dataset.move) {
    const id = +(t.dataset.pp || t.dataset.unpp || t.dataset.move), st = state.status[k][id] = Object.assign({}, state.status[k][id]);
    if (t.dataset.pp) { st.p = baseDate(k, id); delete st.d; delete st.t; }
    else if (t.dataset.unpp) delete st.p;
    else { const d = $('#nd-' + id).value, tm = $('#nt-' + id).value; if (!d) return; st.d = d; if (tm) st.t = tm; else delete st.t; delete st.p; }
    update(k); render(); save(k); return;
  }
  if (t.dataset.follow) { const k = t.dataset.fk || state.view, i = +t.dataset.follow, name = T(k)[i].name, on = !isFav(k, i);
    for (const c of ORDER) { const idx = T(c).findIndex(x => x.name === name); if (idx < 0) continue;
      const arr = state.favs[c] = state.favs[c] || [], j = arr.indexOf(idx);
      if (on && j < 0) arr.push(idx); if (!on && j >= 0) arr.splice(j, 1);
      if (c !== k) save(c); }
    save(k); if ($('#detail').open) openClub(k, i); render(); return; }
  if (t.dataset.club) { const [kk, i] = t.dataset.club.includes(':') ? t.dataset.club.split(':') : [k, t.dataset.club]; if (R[kk]) openClub(kk, +i); return; }
  if (t.dataset.rankf) { rankF = t.dataset.rankf; render(); return; }
  if (t.dataset.rankmode) { rankMode = t.dataset.rankmode; plOpen = null; render(); return; }
  if (t.dataset.plf) { plF = t.dataset.plf; plOpen = null; render(); return; }
  if (t.dataset.plopen) { const n = +t.dataset.plopen; plOpen = plOpen === n ? null : n; render(); return; }
  if (t.dataset.natf) { natF = t.dataset.natf; render(); return; }
  if (t.dataset.xnat) { openNation(+t.dataset.xnat); return; }
  if (t.dataset.xclub) { openXClub(+t.dataset.xclub); return; }
  if (t.dataset.tmode) { state.tmode[k] = t.dataset.tmode; render(); return; }
  if (t.dataset.region) { const r = REGIONS.find(x => x.key === t.dataset.region); if (regionOf(k) === r) return; state.view = lastIn[r.key] || r.comps[0]; render(); window.scrollTo({top:0}); return; }
  if (t.dataset.view) { state.view = t.dataset.view; render(); window.scrollTo({top:0}); return; }
  if (t.dataset.go) { const [kk, id] = t.dataset.go.split(':'); state.view = kk; state.tab[kk] = 'week'; const f = R[kk].fx[+id]; state.mw[kk] = f.mw;
    if (kk === 'unl' && f.h != null) state.unlLeague = (T(kk)[f.h].group || 'A')[0];
    render();
    // Land on the match itself, centred, with a brief highlight so it's easy to spot.
    const card = document.querySelector(`#main [data-fx="${kk}:${id}"]`);
    if (card) { card.scrollIntoView({block:'center'}); card.classList.add('flash'); setTimeout(() => card.classList.remove('flash'), 1600); } else window.scrollTo({top:0});
    return; }
  if (t.dataset.tab) { state.tab[k] = t.dataset.tab; render(); window.scrollTo({top:0}); return; }
  if (t.dataset.open) { openDetail(k, +t.dataset.open); return; }
  if (t.dataset.enter) { const el = $('#entry-' + t.dataset.enter); el.hidden = !el.hidden; if (!el.hidden) $('#hs-' + t.dataset.enter).focus({preventScroll:true}); return; }
  if (t.dataset.save) {
    const id = +t.dataset.save, h = parseInt($('#hs-' + id).value, 10), a = parseInt($('#as-' + id).value, 10);
    saveResult(k, id, h, a); return;
  }
  if (t.dataset.ev) { liveEvent(k, +t.dataset.id, t.dataset.ev); return; }
  if (t.dataset.clear) { state.results[k][+t.dataset.clear] = null; update(k); render(); save(k); return; }
  if (t.dataset.draw) { const id = +t.dataset.draw, h = $('#dh-' + id).value, a = $('#da-' + id).value; if (h === '' || a === '' || h === a) return; state.draws.cup[id] = [+h, +a]; update('cup'); render(); save('cup'); return; }
  if (t.dataset.step) { const rounds = [...new Set(R[k].fx.map(f => f.mw))].sort((x, y) => x - y); const i = rounds.indexOf(state.mw[k]) + (+t.dataset.step); if (rounds[i] != null) { state.mw[k] = rounds[i]; render(); } return; }
  if (t.dataset.cstep) { const cur = state.mw[k] && state.mw[k].startsWith('Semi') ? 'Semi-finals' : state.mw[k]; const i = CUP_ROUNDS.indexOf(cur) + (+t.dataset.cstep); if (CUP_ROUNDS[i]) { state.mw[k] = CUP_ROUNDS[i] === 'Semi-finals' ? 'Semi-final leg 1' : CUP_ROUNDS[i]; render(); } return; }
  if (t.dataset.reset) { if (confirm('Remove every result you entered or edited here? The results that came with the tracker stay.')) { state.results[t.dataset.reset] = {}; if (t.dataset.reset === 'cup') state.draws.cup = {};
for (const k of ORDER) Object.assign(state.status[k], DATA[k].statusDefault || {}); update(t.dataset.reset); render(); save(t.dataset.reset); } }
});
document.addEventListener('keydown', e => { if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('[data-open],[data-go]')) { e.preventDefault(); e.target.click(); } });
document.addEventListener('change', e => {
  const key = e.target.dataset && e.target.dataset.set; if (!key) return;
  const v = parseFloat(e.target.value); if (isNaN(v)) return;
  if (e.target.dataset.global === '1') { state.suite[key] = v; ORDER.forEach(c => queueFull(c)); render(); save(state.view); }
  else { state.settings[state.view][key] = v; update(state.view); render(); save(state.view); }
});
function syncFavs() {
  const names = new Set(); for (const c of ORDER) for (const i of (state.favs[c] || [])) if (T(c)[i]) names.add(T(c)[i].name);
  for (const c of ORDER) { const arr = state.favs[c] = state.favs[c] || []; T(c).forEach((x, i) => { if (names.has(x.name) && !arr.includes(i)) arr.push(i); }); }
}
// ---------------------------------------------------------------- pull to refresh
// Home-screen web apps on iOS have no browser pull-to-refresh, so add one: pull down from the top of the
// page and let go past the line to reload (new deploys and fresh cloud data). The page comes back on the
// same competition and tab. In Safari itself the browser's own gesture is used instead.
const UI_KEY = STORE + ':ui';
const standalone = navigator.standalone === true || matchMedia('(display-mode: standalone)').matches;
function restoreUI() {
  try {
    const u = JSON.parse(sessionStorage.getItem(UI_KEY) || 'null'); sessionStorage.removeItem(UI_KEY);
    if (u && (isHub(u.view) || ORDER.includes(u.view))) Object.assign(state, {view:u.view, unlLeague:u.unlLeague}, {tab:Object.assign(state.tab, u.tab), mw:Object.assign(state.mw, u.mw), tmode:Object.assign(state.tmode, u.tmode)});
  } catch (e) {}
}
function pullRefresh() {
  const PULL = 70, MAX = 110, el = $('#ptr');
  let y0 = null, d = 0;
  const reset = () => { y0 = null; d = 0; el.style.transform = ''; el.classList.remove('ready'); };
  addEventListener('touchstart', e => {
    y0 = scrollY <= 0 && e.touches.length === 1 && !$('#detail').open && !e.target.closest('input,select,textarea') ? e.touches[0].clientY : null;
  }, {passive:true});
  addEventListener('touchmove', e => {
    if (y0 == null) return;
    d = Math.min(MAX, Math.max(0, (e.touches[0].clientY - y0) * 0.5));
    if (scrollY > 0) { reset(); return; }
    el.style.transform = `translate(-50%, ${d}px) rotate(${d * 3}deg)`; el.classList.toggle('ready', d >= PULL);
  }, {passive:true});
  addEventListener('touchend', () => {
    if (y0 == null) return;
    if (d < PULL) { reset(); return; }
    el.classList.add('spin'); el.style.transform = `translate(-50%, ${PULL}px)`;
    try { sessionStorage.setItem(UI_KEY, JSON.stringify({view:state.view, tab:state.tab, mw:state.mw, tmode:state.tmode, unlLeague:state.unlLeague})); } catch (e) {}
    location.reload();
  });
  addEventListener('touchcancel', reset);
}

loadLocal(); syncFavs(); restoreUI(); startWorker(); render(); computeAll(); connect();
if (standalone) { document.documentElement.classList.add('standalone'); pullRefresh(); }
