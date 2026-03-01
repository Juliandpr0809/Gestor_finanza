/**
 * Logo Dropdown Menu Handler
 * Maneja el menú desplegable del logo con idioma, moneda y cerrar sesión
 */

document.addEventListener('DOMContentLoaded', () => {
    const logoMenuToggle = document.getElementById('logoMenuToggle');
    const logoDropdown = document.getElementById('logoDropdown');

    if (!logoMenuToggle || !logoDropdown) return;

    // Toggle menú al hacer clic en el logo
    logoMenuToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        logoMenuToggle.classList.toggle('active');
    });

    // Cerrar menú al hacer clic fuera
    document.addEventListener('click', (e) => {
        if (!logoMenuToggle.contains(e.target)) {
            logoMenuToggle.classList.remove('active');
        }
    });

    // Prevenir que clics dentro del dropdown lo cierren
    logoDropdown.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    // IDIOMA - Los botones ya están configurados en i18n.js con data-lang-btn
    // Solo necesitamos actualizar el estado activo     updateLanguageButtonsState();

    // MONEDA - Manejar cambio de moneda
    const currencyOptions = document.querySelectorAll('.logo-currency-option');
    const savedCurrency = localStorage.getItem('preferredCurrency') || 'COP';

    // Marcar moneda activa
    currencyOptions.forEach(opt => {
        if (opt.dataset.currency === savedCurrency) {
            opt.classList.add('active');
        }

        // Click en opción de moneda
        opt.addEventListener('click', () => {
            const newCurrency = opt.dataset.currency;

            // Actualizar UI
            currencyOptions.forEach(o => o.classList.remove('active'));
            opt.classList.add('active');

            // Guardar en localStorage
            localStorage.setItem('preferredCurrency', newCurrency);

            // Actualizar también el currencyValue si existe
            const currencyValue = document.getElementById('currencyValue');
            if (currencyValue) {
                currencyValue.textContent = newCurrency;
            }

            // Cerrar menú
            logoMenuToggle.classList.remove('active');

            // Recargar datos con nueva moneda
            if (typeof loadDashboardData === 'function') {
                loadDashboardData();
            }

            console.log(`💱 Moneda cambiada a: ${newCurrency}`);
        });
    });

    // CERRAR SESIÓN
    const logoutItem = logoDropdown.querySelector('[data-action="logout"]');
    if (logoutItem) {
        logoutItem.addEventListener('click', () => {
            console.log('🚪 Cerrando sesión...');
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = 'login.html';
        });
    }

    // Actualizar estado de botones de idioma cuando se cambie
    function updateLanguageButtonsState() {
        const currentLang = localStorage.getItem('preferredLanguage') || 'es';
        document.querySelectorAll('.logo-lang-btn').forEach(btn => {
            const btnLang = btn.getAttribute('data-lang-btn');
            if (btnLang === currentLang) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // Escuchar cambios de idioma para actualizar el estado
    window.addEventListener('languageChanged', updateLanguageButtonsState);
});
