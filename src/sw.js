// Service worker (web build only): logos, flags and icons come from the phone's cache after the first visit,
// so scrolling never waits on the network; the page itself is network-first with the cached copy as the
// offline fallback. VERSION is a hash of the image files (build.py), so changed logos replace the old cache.
const VERSION = '__VERSION__', CACHE = 'fts-' + VERSION;
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(caches.keys()
  .then(ks => Promise.all(ks.filter(k => k.startsWith('fts-') && k !== CACHE).map(k => caches.delete(k))))
  .then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const req = e.request, u = new URL(req.url);
  if (req.method !== 'GET' || u.origin !== location.origin) return;
  if (/\.(png|svg)$/.test(u.pathname)) {
    e.respondWith(caches.open(CACHE).then(async c => (await c.match(req)) || fetch(req).then(r => { if (r.ok) c.put(req, r.clone()); return r; })));
  } else if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return r; })
      .catch(() => caches.match(req)));
  }
});
