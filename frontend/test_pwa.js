// test_pwa.js - Verificar que PWA está configurada correctamente

const pwaTests = {
  results: [],

  async runAllTests() {
    console.log('🚀 Iniciando tests de PWA...\n');
    
    await this.testManifest();
    await this.testServiceWorker();
    await this.testMetaTags();
    await this.testCache();
    
    this.printResults();
  },

  async testManifest() {
    console.log('📋 Test 1: Verificar manifest.json...');
    try {
      const link = document.querySelector('link[rel="manifest"]');
      
      if (!link) {
        this.results.push({ test: 'Manifest linkeado', status: '❌', message: 'No se encontró <link rel="manifest">' });
        return;
      }

      const manifestUrl = link.getAttribute('href');
      const response = await fetch(manifestUrl);
      const manifest = await response.json();

      if (!manifest.name || !manifest.short_name) {
        this.results.push({ test: 'Manifest datos básicos', status: '❌', message: 'Faltan name o short_name' });
        return;
      }

      if (!manifest.icons || manifest.icons.length === 0) {
        this.results.push({ test: 'Manifest iconos', status: '⚠️', message: 'Sin iconos definidos' });
      } else {
        this.results.push({ test: 'Manifest iconos', status: '✅', message: `${manifest.icons.length} iconos` });
      }

      if (!manifest.display || manifest.display !== 'standalone') {
        this.results.push({ test: 'Manifest display', status: '⚠️', message: 'Display no es standalone' });
      } else {
        this.results.push({ test: 'Manifest display', status: '✅', message: 'standalone' });
      }

      this.results.push({ test: 'Manifest linkeado', status: '✅', message: manifestUrl });
      this.results.push({ test: 'Manifest válido', status: '✅', message: `${manifest.short_name}` });

    } catch (error) {
      this.results.push({ test: 'Manifest', status: '❌', message: error.message });
    }
  },

  async testServiceWorker() {
    console.log('🔧 Test 2: Verificar Service Worker...');
    try {
      if (!navigator.serviceWorker) {
        this.results.push({ test: 'Service Worker disponible', status: '❌', message: 'No soportado en este navegador' });
        return;
      }

      const registration = await navigator.serviceWorker.ready;
      
      if (registration.active) {
        this.results.push({ test: 'Service Worker registrado', status: '✅', message: 'Activo' });
      } else if (registration.installing) {
        this.results.push({ test: 'Service Worker registrado', status: '⏳', message: 'Instalando...' });
      } else if (registration.waiting) {
        this.results.push({ test: 'Service Worker registrado', status: '⚠️', message: 'En espera de activación' });
      }

      this.results.push({ test: 'Service Worker scope', status: '✅', message: registration.scope });

    } catch (error) {
      this.results.push({ test: 'Service Worker', status: '⚠️', message: error.message });
    }
  },

  async testMetaTags() {
    console.log('📱 Test 3: Verificar meta tags...');
    const metaTags = [
      { name: 'viewport', content: 'width=device-width' },
      { name: 'theme-color', content: '#06070c' },
      { name: 'apple-mobile-web-app-capable', content: 'yes' },
      { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' }
    ];

    metaTags.forEach(tag => {
      const element = document.querySelector(`meta[name="${tag.name}"]`);
      if (element) {
        this.results.push({ test: `Meta ${tag.name}`, status: '✅', message: element.getAttribute('content') });
      } else {
        this.results.push({ test: `Meta ${tag.name}`, status: '⚠️', message: 'No encontrado' });
      }
    });
  },

  async testCache() {
    console.log('💾 Test 4: Verificar caché...');
    try {
      if (!caches) {
        this.results.push({ test: 'Cache API', status: '❌', message: 'No soportado' });
        return;
      }

      const cacheNames = await caches.keys();
      
      if (cacheNames.length === 0) {
        this.results.push({ test: 'Cache almacenado', status: '⚠️', message: 'Sin cachés aún (primera visita)' });
        return;
      }

      this.results.push({ test: 'Cache almacenado', status: '✅', message: `${cacheNames.length} cachés: ${cacheNames.join(', ')}` });

      // Verificar tamaño aproximado
      let totalSize = 0;
      for (const cacheName of cacheNames) {
        const cache = await caches.open(cacheName);
        const keys = await cache.keys();
        this.results.push({ test: `Items en ${cacheName}`, status: '✅', message: `${keys.length} archivos` });
      }

    } catch (error) {
      this.results.push({ test: 'Cache', status: '⚠️', message: error.message });
    }
  },

  printResults() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 RESULTADOS DE TESTS PWA');
    console.log('='.repeat(60));
    
    this.results.forEach(result => {
      console.log(`${result.status} ${result.test.padEnd(30)} → ${result.message}`);
    });

    console.log('='.repeat(60));
    
    const passed = this.results.filter(r => r.status === '✅').length;
    const warnings = this.results.filter(r => r.status === '⚠️').length;
    const failed = this.results.filter(r => r.status === '❌').length;

    console.log(`\n✅ Pasados: ${passed} | ⚠️ Advertencias: ${warnings} | ❌ Fallidos: ${failed}`);
    
    if (failed === 0 && warnings <= 1) {
      console.log('\n🎉 ¡PWA correctamente configurada!');
    } else if (warnings > 0) {
      console.log('\n⚠️ PWA funciona pero tiene algunas advertencias');
    } else {
      console.log('\n❌ PWA tiene problemas');
    }
  }
};

// Ejecutar tests cuando el DOM está listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => pwaTests.runAllTests());
} else {
  pwaTests.runAllTests();
}

// Exportar para uso en consola
window.pwaTests = pwaTests;
