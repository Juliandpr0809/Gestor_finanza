// Service Worker para OrdenC - PWA
// Versión 4.2 - Mejoras UI: iconos FontAwesome y scroll horizontal en filtros
const CACHE_NAME = 'ordenc-v4.2';
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
  '/frontend/css/mobile-native.css',
  '/frontend/css/lang-selector.css',
  '/frontend/css/ux-improvements.css',
  '/frontend/css/header-minimal.css',
  '/frontend/css/bottom-navigation.css',
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
  console.log('Service Worker: Instalando nueva versión...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Cacheando archivos...');
        return cache.addAll(urlsToCache).catch((err) => {
          console.log('Service Worker: Algunos recursos no pudieron ser cacheados', err);
        });
      })
  );
  // Forzar activación inmediata de la nueva versión
  self.skipWaiting();
});

// Activar Service Worker
self.addEventListener('activate', event => {
  console.log('Service Worker: Activando nueva versión...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Eliminando caché antiguo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker: Nueva versión activa');
      // Notificar a todos los clientes que hay una actualización
      return self.clients.matchAll().then(clients => {
        clients.forEach(client => {
          client.postMessage({
            type: 'SW_UPDATED',
            version: CACHE_NAME
          });
        });
      });
    })
  );
  // Tomar control inmediato de todas las páginas
  return self.clients.claim();
});

// Estrategia Network First (para HTML/CSS/JS y API) / Cache Fallback
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Para peticiones a API, siempre red primero
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // No cachear respuestas de API para evitar datos obsoletos
          return response;
        })
        .catch(() => {
          return new Response(JSON.stringify({ error: 'Sin conexión' }), { 
            status: 503,
            headers: { 'Content-Type': 'application/json' }
          });
        })
    );
  }
  // Para HTML, CSS, JS: Network First (siempre intentar red primero)
  else if (
    url.pathname.endsWith('.html') || 
    url.pathname.endsWith('.css') || 
    url.pathname.endsWith('.js') ||
    url.pathname.includes('/frontend/')
  ) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Si la red responde, actualizar caché
          if (response && response.status === 200) {
            const clonedResponse = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(request, clonedResponse);
            });
          }
          return response;
        })
        .catch(() => {
          // Si falla la red, usar caché como fallback
          return caches.match(request)
            .then(response => response || new Response('Offline', { status: 503 }));
        })
    );
  }
  // Para otros recursos (imágenes, fuentes, etc): Cache First
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
