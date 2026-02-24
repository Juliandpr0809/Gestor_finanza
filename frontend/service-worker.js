const CACHE_NAME = 'ordenc-v2';
const urlsToCache = [
  '/frontend/html/index.html',
  '/frontend/html/login.html',
  '/frontend/html/register.html',
  '/frontend/html/accounts.html',
  '/frontend/html/transactions.html',
  '/frontend/html/ai-chat.html',
  '/frontend/html/new-transaction.html',
  '/frontend/css/modern-theme.css',
  '/frontend/css/unified-pages.css',
  '/frontend/css/accounts.css',
  '/frontend/css/transactions.css',
  '/frontend/css/ai-chat.css',
  '/frontend/css/new-transaction.css',
  '/frontend/css/auth.css',
  '/frontend/js/api.js',
  '/frontend/js/auth.js',
  '/frontend/js/dashboard.js',
  '/frontend/js/transactions.js',
  '/frontend/js/accounts.js',
  '/frontend/js/ai-chat.js'
];

// Instalar Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache).catch(() => {
          console.log('Algunos recursos no pudieron ser cacheados');
        });
      })
  );
  self.skipWaiting();
});

// Activar Service Worker
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Estrategia Network First (para API) / Cache First (para assets)
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Para peticiones a API, intentar red primero
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          const clonedResponse = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(request, clonedResponse);
          });
          return response;
        })
        .catch(() => {
          return caches.match(request)
            .then(response => response || new Response('Offline', { status: 503 }));
        })
    );
  }
  // Para assets, usar caché primero
  else {
    event.respondWith(
      caches.match(request)
        .then(response => response || fetch(request))
        .catch(() => new Response('Offline', { status: 503 }))
    );
  }
});

// Sincronización en background
self.addEventListener('sync', event => {
  if (event.tag === 'sync-transactions') {
    event.waitUntil(
      fetch('/api/sync')
        .then(() => console.log('Transacciones sincronizadas'))
        .catch(() => console.log('Error en sincronización'))
    );
  }
});
