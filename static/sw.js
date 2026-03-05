const CACHE_NAME = 'trainingos-v2';  // Change le numéro de version quand tu mets à jour

const STATIC_ASSETS = [
  '/',                          // page d'accueil
  '/index.html',                // si tu en as un explicite
  '/static/icon-192.png',
  '/static/icon-512.png',
  // Ajoute ici tes fichiers JS/CSS principaux, ex:
  // '/static/js/main.chunk.js',
  // '/static/css/main.css',
  // etc.
];

self.addEventListener('install', event => {
  console.log('Service Worker installing…');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  console.log('Service Worker activated');
  // Nettoyage des anciens caches (très recommandé)
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME)
            .map(key => caches.delete(key))
      );
    })
  );
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Ignorer les requêtes non-GET ou cross-origin non sécurisées
  if (event.request.method !== 'GET' || url.origin !== self.location.origin) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Stratégie Cache First pour les assets statiques
  if (STATIC_ASSETS.includes(url.pathname) || url.pathname.match(/\.(js|css|png|jpg|svg|woff2?)$/)) {
    event.respondWith(
      caches.match(event.request)
        .then(cached => cached || fetch(event.request).then(response => {
          // Optionnel : mettre en cache les réponses réseau réussies
          if (response && response.status === 200) {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseToCache));
          }
          return response;
        }))
    );
    return;
  }

  // Pour les pages dynamiques : Network First, fallback sur cache si offline
  event.respondWith(
    fetch(event.request)
      .catch(() => caches.match('/'))  // fallback sur la page d'accueil si offline
  );
});