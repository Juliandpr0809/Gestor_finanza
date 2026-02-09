const CACHE_NAME = 'ordenc-v1';
const urlsToCache = [
  '/html/index.html',
  '/html/login.html',
  '/html/register.html',
  '/html/accounts.html',
  '/html/transactions.html',
  '/html/ai-chat.html',
  '/html/new-transaction.html',
  '/css/modern-theme.css',
  '/css/unified-pages.css',
  '/css/accounts.css',
  '/css/transactions.css',
  '/css/ai-chat.css',
  '/css/new-transaction.css',
  '/css/auth.css',
  '/js/api.js',
  '/js/auth.js',
  '/js/dashboard.js',
  '/js/transactions.js',
  '/js/accounts.js',
  '/js/ai-chat.js'
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
