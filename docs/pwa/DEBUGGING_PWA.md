# 🔍 Debugging de OrdenC PWA

## Verificar que PWA está funcionando

### Opción 1: Tests Automáticos (Recomendado)
Agregar esto a la consola del navegador:
```javascript
// Copiar en DevTools Console (F12)
fetch('../test_pwa.js')
  .then(r => r.text())
  .then(code => eval(code));
```

O agregar el script directamente al HTML:
```html
<script src="../test_pwa.js"></script>
```

### Opción 2: Verificación Manual

#### 1. **Verificar Manifest**
```javascript
// En DevTools Console:
const link = document.querySelector('link[rel="manifest"]');
fetch(link.href).then(r => r.json()).then(m => console.log(m));
```

Debería mostrar:
```json
{
  "name": "OrdenC - Financial Manager",
  "short_name": "OrdenC",
  "display": "standalone",
  ...
}
```

#### 2. **Verificar Service Worker**
```javascript
// En DevTools Console:
navigator.serviceWorker.ready.then(reg => {
  console.log('Estado:', reg.active ? '✅ Activo' : '⚠️ Inactivo');
  console.log('Scope:', reg.scope);
});
```

Debería mostrar:
```
✅ Activo
https://localhost:5000/
```

#### 3. **Verificar Caché**
```javascript
// En DevTools Console:
caches.keys().then(names => {
  console.log('Cachés:', names);
  names.forEach(async name => {
    const cache = await caches.open(name);
    const keys = await cache.keys();
    console.log(`${name}: ${keys.length} archivos`);
  });
});
```

#### 4. **Verificar Meta Tags**
```javascript
// En DevTools Console:
document.querySelectorAll('meta').forEach(m => {
  const name = m.getAttribute('name') || m.getAttribute('property');
  const content = m.getAttribute('content');
  if (name?.includes('app') || name?.includes('theme')) {
    console.log(`${name}: ${content}`);
  }
});
```

## DevTools Navigation

### Chrome / Edge

#### Application Tab
1. **Manifest**: 
   - Abre: F12 → Application → Manifest
   - Deberías ver "Manifest status: ✓ Installed"

2. **Service Workers**:
   - Abre: F12 → Application → Service Workers
   - Deberías ver "service-worker.js" con estado "activated and running"

3. **Cache Storage**:
   - Abre: F12 → Application → Cache Storage
   - Deberías ver "ordenc-v1" con muchos archivos

4. **Storage**:
   - LocalStorage: Datos de usuario (tokens, preferencias)
   - IndexedDB: Posibles datos offline (no implementados aún)

### Firefox

#### Storage Tab
1. Abre: F12 → Storage → Manifest
2. Abre: F12 → Storage → Service Workers
3. Abre: F12 → Storage → Cache

### Safari (iOS)

1. Settings → Developer → AdvancedPage
2. Conectar a Xcode o usar Safari Remote Debugger

## Simular Offline

### En Chrome DevTools
1. F12 → Network Tab
2. Selecciona "Offline" en el dropdown de throttle
3. Recarga la página
4. Debería funcionar con datos cacheados

### En Firefox DevTools
1. F12 → Network → Engranaje ⚙️
2. Marca "Throttling"
3. Selecciona "Offline"

## Limpiar Caché

### Para desarrollo (cuando haces cambios)
```javascript
// En DevTools Console:
caches.delete('ordenc-v1').then(() => {
  console.log('Caché limpiado');
  location.reload();
});
```

### Opción manual
1. DevTools → Application → Cache Storage
2. Click derecho en "ordenc-v1"
3. "Delete"

## Problemas Comunes

### ❌ "Service Worker no se registra"

**Causas:**
- No está en HTTPS (devtunnels sí lo es)
- El archivo service-worker.js no existe
- Path del archivo es incorrecto

**Solución:**
```javascript
// En DevTools Console:
navigator.serviceWorker.register('../service-worker.js')
  .then(r => console.log('✅ Registrado'))
  .catch(e => console.log('❌', e.message));
```

### ❌ "Manifest no se detecta"

**Causas:**
- Link rel="manifest" falta en HTML
- Path es incorrecto
- JSON inválido

**Solución:**
```html
<!-- Verificar que existe en HTML -->
<link rel="manifest" href="../manifest.json">
```

Luego:
```javascript
const link = document.querySelector('link[rel="manifest"]');
if (!link) console.log('❌ Link no encontrado');
else fetch(link.href).then(r => r.json()).then(m => console.log('✅', m));
```

### ⚠️ "App no se instala"

**Checklist:**
- [ ] Abriste desde HTTPS (devtunnels es HTTPS)
- [ ] Esperaste a que cargue completamente
- [ ] Manifest tiene mínimo 192x192 icono
- [ ] Display es "standalone"
- [ ] Esperaste 5+ segundos

**Solución:**
- Prueba en Chrome (mejor soporte PWA)
- Prueba en pestaña privada
- Borra caché del navegador
- Intenta desde otro dispositivo

### ⚠️ "Los datos no se sincronizan offline"

**Nota:** OrdenC cachea solo para lectura. Las nuevas transacciones se guardan localmente y se sincronizan cuando vuelve internet.

**Verificar:**
1. Desactiva internet
2. Intenta agregar transacción
3. Debería mostrar "Pendiente de sincronización"
4. Activa internet
5. Debería sincronizar automáticamente

## Performance

### Verificar velocidad de carga

#### Chrome DevTools Performance
1. F12 → Performance
2. Click en grabar
3. Recarga la página
4. Stop
5. Analiza:
   - First Contentful Paint (FCP): < 2s ✅
   - Largest Contentful Paint (LCP): < 3s ✅
   - Time to Interactive (TTI): < 4s ✅

#### Network Tab
1. F12 → Network
2. Recarga
3. Verifica tiempos:
   - HTML: < 200ms
   - CSS: < 100ms
   - JS: < 100ms
   - Imágenes: < 300ms

### Ver tamaño de caché
```javascript
// En DevTools Console:
async function getCacheSize() {
  const names = await caches.keys();
  let total = 0;
  
  for (const name of names) {
    const cache = await caches.open(name);
    const keys = await cache.keys();
    
    for (const request of keys) {
      const response = await cache.match(request);
      const blob = await response.blob();
      total += blob.size;
    }
  }
  
  console.log('Tamaño total caché:', (total / 1024 / 1024).toFixed(2), 'MB');
}

getCacheSize();
```

## Monitoreo en Producción

### Implementar logging
```javascript
// En app.js o main.js
window.addEventListener('error', (e) => {
  console.error('Error:', e.message);
  // Aquí podrías enviar a un servicio de logging
});

// Monitorar Service Worker
navigator.serviceWorker.addEventListener('message', (e) => {
  console.log('Mensaje del SW:', e.data);
});
```

## Testing en Diferentes Dispositivos

### Usando Chrome DevTools Device Mode
1. F12 → Toggle device toolbar (Ctrl+Shift+M)
2. Selecciona dispositivo (iPhone 12, Pixel 5, etc.)
3. Prueba responsive
4. Prueba touch events

### Usando Android Emulator
1. Android Studio → Virtual Device
2. Abre Chrome
3. Navega a: `http://10.0.2.2:5000/html/index.html`
4. Instala como PWA

## Seguridad

### Verificar HTTPS
```javascript
// En DevTools Console:
console.log('URL actual:', window.location.href);
console.log('¿HTTPS?', window.location.protocol === 'https:' ? '✅' : '❌');
```

### Verificar CSP Headers
```javascript
// En DevTools → Network → index.html
// Busca header: Content-Security-Policy
```

## Documentación de Referencia

- [Web.dev PWA Checklist](https://web.dev/pwa-checklist/)
- [Chrome DevTools Guide](https://developer.chrome.com/docs/devtools/)
- [MDN Service Workers](https://developer.mozilla.org/es/docs/Web/API/Service_Worker_API)
- [Web App Manifest](https://developer.mozilla.org/es/docs/Web/Manifest)

---

**Última actualización:** 3 de enero de 2026
**Estado:** ✅ Listo para debugging
