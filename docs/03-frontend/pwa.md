# 📱 Progressive Web App (PWA)

Documentación de la funcionalidad PWA.

## ✨ Características PWA

- ✅ Instalable en dispositivos
- ✅ Funciona offline (próximamente)
- ✅ App-like experience
- ✅ Splash screen personalizada
- ✅ Íconos adaptables
- ✅ Accesos directos desde home screen

## 📁 Archivos PWA

```
frontend/
├── manifest.json         # Manifiesto de la app
├── service-worker.js     # Service worker (cache)
└── html/
    └── *.html           # Incluyen link al manifest
```

## 📋 Manifest.json

Define cómo se ve y comporta la app cuando se instala:

```json
{
  "name": "OrdenC - Financial Manager",
  "short_name": "OrdenC",
  "description": "Gestor financiero inteligente con IA",
  "start_url": "/html/index.html",
  "display": "standalone",
  "theme_color": "#06070c",
  "background_color": "#06070c",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "...",
      "sizes": "192x192",
      "type": "image/svg+xml",
      "purpose": "any"
    }
  ]
}
```

### Propiedades Clave

| Propiedad | Valor | Descripción |
|-----------|-------|-------------|
| `name` | "OrdenC - Financial Manager" | Nombre completo |
| `short_name` | "OrdenC" | Nombre corto (home screen) |
| `start_url` | "/html/index.html" | URL de inicio |
| `display` | "standalone" | Modo app (sin barra navegador) |
| `theme_color` | "#06070c" | Color de tema |
| `orientation` | "portrait-primary" | Orientación |

## 🔧 Service Worker

Permite funcionalidad offline y cache de recursos.

### Registro

En cada HTML:

```html
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('../service-worker.js')
        .then(reg => console.log('SW registered:', reg))
        .catch(err => console.log('SW error:', err));
}
</script>
```

### Estrategia de Cache

```javascript
// service-worker.js
const CACHE_NAME = 'ordenc-v1';
const urlsToCache = [
  '/html/index.html',
  '/css/modern-theme.css',
  '/js/main.js',
  '/js/i18n.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
```

## 📱 Instalación

### Android (Chrome)

1. Abrir la app en Chrome
2. Menú (⋮) > "Agregar a pantalla de inicio"
3. Confirmar instalación

### iOS (Safari)

1. Abrir en Safari
2. Botón compartir (□↑)
3. "Agregar a pantalla de inicio"
4. Confirmar

### Desktop (Chrome/Edge)

1. Ícono de instalación en barra de direcciones
2. Click en "Instalar"

## 🔍 Meta Tags PWA

En cada HTML:

```html
<!-- PWA Config -->
<meta name="theme-color" content="#06070c">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="OrdenC">
<link rel="apple-touch-icon" href="...">
<link rel="manifest" href="../manifest.json">
```

## 🎯 Accesos Directos (Shortcuts)

En `manifest.json`:

```json
{
  "shortcuts": [
    {
      "name": "Nueva Transacción",
      "short_name": "Transacción",
      "url": "/html/new-transaction.html",
      "icons": [...]
    },
    {
      "name": "Chat con IA",
      "short_name": "Chat IA",
      "url": "/html/ai-chat.html",
      "icons": [...]
    }
  ]
}
```

Long-press en el ícono de la app muestra estas opciones.

## 🧪 Testing PWA

### Lighthouse (Chrome DevTools)

1. Abrir DevTools (F12)
2. Tab "Lighthouse"
3. Seleccionar "Progressive Web App"
4. Click "Generate report"

### PWA Checklist

- [ ] Responde con 200 cuando offline
- [ ] Metadata de manifest válido
- [ ] Service worker registrado
- [ ] Íconos de múltiples tamaños
- [ ] HTTPS en producción (requerido)
- [ ] Viewport meta tag
- [ ] Orientación configurada

### Herramientas

- [PWA Builder](https://www.pwabuilder.com/) - Validar y mejorar PWA
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Auditoría
- [WebPageTest](https://www.webpagetest.org/) - Performance

## 🚀 Mejoras Futuras

### Offline Functionality

```javascript
// Cache dinámico de API calls
self.addEventListener('fetch', event => {
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      caches.open('api-cache').then(cache => {
        return fetch(event.request)
          .then(response => {
            cache.put(event.request, response.clone());
            return response;
          })
          .catch(() => cache.match(event.request))
      })
    );
  }
});
```

### Background Sync

```javascript
// Sincronizar cuando vuelva conexión
self.addEventListener('sync', event => {
  if (event.tag === 'sync-transactions') {
    event.waitUntil(syncTransactions());
  }
});
```

### Push Notifications

```javascript
// Notificaciones push
self.addEventListener('push', event => {
  const data = event.data.json();
  self.registration.showNotification(data.title, {
    body: data.message,
    icon: '/icon-192.png'
  });
});
```

## 📚 Recursos

- [MDN PWA Guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [web.dev PWA](https://web.dev/progressive-web-apps/)
- [PWA Checklist](https://web.dev/pwa-checklist/)
