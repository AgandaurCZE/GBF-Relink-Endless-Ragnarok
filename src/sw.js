/* sw.js: lets the guide open offline and installs it as an app. Published at the site root.
   - Pages and data (data/*.json): network first, so visitors always get the newest content when online;
     the last copy is kept for offline use.
   - css/, js/, assets/: served from the cache and refreshed in the background (their ?v= changes when they change).
   - Offline, an address never opened before falls back to 404.html, which draws any page of the guide.
   Change CACHE when this strategy changes; old caches are deleted on activation. */
const CACHE = 'relink-guide-v1';
const SHELL = ['./', '404.html', 'data/game.json', 'data/steam-news.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

async function networkFirst(request, fallback) {
  const cache = await caches.open(CACHE);
  try {
    const response = await fetch(request);
    if (response.ok) cache.put(request, response.clone());
    return response;
  } catch (error) {
    const cached = (await cache.match(request, { ignoreSearch: true })) || (fallback && (await cache.match(fallback)));
    if (cached) return cached;
    throw error;
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match(request);
  const refresh = fetch(request)
    .then((response) => {
      if (response.ok) cache.put(request, response.clone());
      return response;
    })
    .catch(() => cached);
  return cached || refresh;
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== location.origin) return;
  if (request.mode === 'navigate') event.respondWith(networkFirst(request, new URL('404.html', self.registration.scope).href));
  else if (url.pathname.includes('/data/')) event.respondWith(networkFirst(request));
  else event.respondWith(cacheFirst(request));
});
