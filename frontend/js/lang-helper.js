/**
 * Script auxiliar para actualizar headers con selector de idioma
 * Incluir después de i18n.js
 */

// Función para agregar selector de idioma al header si no existe
function addLanguageSelectorToHeader() {
    const headerRight = document.querySelector('.header-right');
    if (!headerRight) return;
    
    // Verificar si ya existe el selector
    if (document.querySelector('.lang-selector')) return;
    
    // Crear el selector de idioma
    const langSelector = document.createElement('div');
    langSelector.className = 'lang-selector';
    langSelector.innerHTML = `
        <button class="lang-btn" data-lang-btn="es">ES</button>
        <button class="lang-btn" data-lang-btn="en">EN</button>
    `;
    
    // Insertar antes de las acciones del header
    const headerActions = headerRight.querySelector('.header-actions') || headerRight.querySelector('.header-profile');
    if (headerActions) {
        headerRight.insertBefore(langSelector, headerActions);
    } else {
        headerRight.appendChild(langSelector);
    }
    
    // Reinicializar i18n para los nuevos botones
    if (window.i18n) {
        window.i18n.translatePage();
    }
}

// Auto-ejecutar al cargar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addLanguageSelectorToHeader);
} else {
    addLanguageSelectorToHeader();
}
