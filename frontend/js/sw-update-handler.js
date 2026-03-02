// ==========================================
// SERVICE WORKER UPDATE HANDLER
// Maneja actualizaciones automáticas del SW
// ==========================================

console.log('SW Update Handler cargado');

if ('serviceWorker' in navigator) {
  // Registrar Service Worker
  navigator.serviceWorker.register('../service-worker.js')
    .then(registration => {
      console.log('✅ Service Worker registrado:', registration.scope);
      
      // Verificar actualizaciones cada 60 segundos
      setInterval(() => {
        registration.update();
      }, 60000);
      
      // Escuchar cambios en el Service Worker
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        console.log('🔄 Nueva versión del Service Worker detectada');
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // Hay una nueva versión disponible
            console.log('✨ Nueva versión lista para usar');
            showUpdateNotification();
          }
        });
      });
    })
    .catch(err => {
      console.log('❌ Error registrando Service Worker:', err);
    });
  
  // Escuchar mensajes del Service Worker
  navigator.serviceWorker.addEventListener('message', event => {
    if (event.data.type === 'SW_UPDATED') {
      console.log('📢 Service Worker actualizado a:', event.data.version);
      // Auto-recargar la página después de 2 segundos
      setTimeout(() => {
        console.log('🔄 Recargando página automáticamente...');
        window.location.reload();
      }, 2000);
    }
  });
  
  // Controlar el Service Worker
  let refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (!refreshing) {
      console.log('🔄 Nuevo Service Worker tomó control - recargando...');
      refreshing = true;
      window.location.reload();
    }
  });
}

// Mostrar notificación de actualización
function showUpdateNotification() {
  // Crear elemento de notificación
  const notification = document.createElement('div');
  notification.id = 'sw-update-notification';
  notification.innerHTML = `
    <div style="
      position: fixed;
      bottom: 80px;
      left: 50%;
      transform: translateX(-50%);
      background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
      color: white;
      padding: 16px 24px;
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
      z-index: 10000;
      display: flex;
      align-items: center;
      gap: 16px;
      animation: slideUp 0.3s ease-out;
      max-width: 90%;
      font-family: system-ui, -apple-system, sans-serif;
    ">
      <i class="fas fa-sync-alt" style="font-size: 20px; animation: spin 2s linear infinite;"></i>
      <div style="flex: 1;">
        <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">
          ✨ Nueva versión disponible
        </div>
        <div style="font-size: 12px; opacity: 0.9;">
          Recargando automáticamente...
        </div>
      </div>
    </div>
    <style>
      @keyframes slideUp {
        from {
          opacity: 0;
          transform: translateX(-50%) translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateX(-50%) translateY(0);
        }
      }
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
    </style>
  `;
  
  document.body.appendChild(notification);
  
  // Auto-remover después de 3 segundos
  setTimeout(() => {
    notification.remove();
  }, 3000);
}

// Detectar si la página se cargó desde caché
window.addEventListener('load', () => {
  if (performance.navigation.type === 1) {
    console.log('🔄 Página recargada');
  }
  
  // Limpiar caché antiguo del localStorage si es necesario
  const currentVersion = 'v4.1';
  const storedVersion = localStorage.getItem('app_version');
  
  if (storedVersion !== currentVersion) {
    console.log(`📦 Actualizando versión de ${storedVersion || 'antigua'} a ${currentVersion}`);
    localStorage.setItem('app_version', currentVersion);
    
    // Limpiar datos obsoletos si es necesario
    // localStorage.removeItem('old_data_key');
  }
});

console.log('✅ SW Update Handler inicializado');
