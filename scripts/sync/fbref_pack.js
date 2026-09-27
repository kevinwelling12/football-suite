// Paste into the browser console (or run via Claude in Chrome javascript_tool) on an FBref
// "Scores & Fixtures" page. Produces the compact text format read by apply_fbref.py:
//   line 1: team names joined by "|"
//   line 2: rows joined by ";"  ->  when,homeIdx36,awayIdx36[,hs:as]
//   when = minutes since 2026-01-01T00:00Z in base 36 (from data-venue-epoch), or "d" if no time
// Played rows and timed unplayed rows are included; date-only (provisional) rows are skipped.
(() => {
  const t = document.querySelector('table[id^="sched_"]');
  const g = (tr, s) => { const c = tr.querySelector(`[data-stat="${s}"]`); return c ? c.innerText.trim() : ''; };
  const cl = s => s.replace(/^[a-z]{2,3}\s+/, '').replace(/\s+[a-z]{2,3}$/, ''); // strip UEFA country codes
  const rows = [...t.querySelectorAll('tbody tr')].filter(tr => { const h = g(tr, 'home_team'); return h && h !== 'Home'; });
  const names = [...new Set(rows.flatMap(tr => [cl(g(tr, 'home_team')), cl(g(tr, 'away_team'))]))].sort();
  const B = 1767225600;
  const out = rows.map(tr => {
    const vt = tr.querySelector('.venuetime'), ep = vt && vt.getAttribute('data-venue-epoch');
    const sc = g(tr, 'score').replace(/\(.*?\)/g, '').replace(/[^0-9–]/g, '');
    if (!sc.includes('–') && !ep) return null;
    const when = ep ? Math.round((+ep - B) / 60).toString(36) : 'd';
    return when + ',' + names.indexOf(cl(g(tr, 'home_team'))).toString(36) + ',' + names.indexOf(cl(g(tr, 'away_team'))).toString(36)
      + (sc.includes('–') ? ',' + sc.split('–').join(':') : '');
  }).filter(Boolean);
  return names.join('|') + '\n' + out.join(';');
})();
