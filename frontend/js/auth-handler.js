/**
 * Auth Handler - Manejo de autenticación y perfil de usuario
 * v19.0 - Simplificado para evitar ejecuciones múltiples
 */

console.log('🔄 auth-handler.js v19 cargado');

// Función helper para decodificar JWT de forma segura (soporta Base64Url)
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        return JSON.parse(jsonPayload);
    } catch (e) {
        console.error('Error parsing JWT:', e);
        return {};
    }
}

// Verificar si el usuario está autenticado
function isAuthenticated() {
    const token = localStorage.getItem('token');
    console.log('isAuthenticated() verificando token:', token ? 'EXISTE' : 'NO EXISTE');
    return !!token;
}

// Verificar si estamos en una página pública
function isPublicPage() {
    const currentPath = window.location.pathname.toLowerCase();
    const isPublic = currentPath.includes('login') || currentPath.includes('register');
    console.log('isPublicPage():', currentPath, '→', isPublic);
    return isPublic;
}

// Redirigir a login si no está autenticado
function requireAuth() {
    console.log('requireAuth() llamado');
    
    // No verificar autenticación en páginas públicas
    if (isPublicPage()) {
        console.log('→ Página pública, no requiere auth');
        return true;
    }
    
    if (!isAuthenticated()) {
        console.log('→ No autenticado, redirigiendo a login');
        window.location.href = 'login.html';
        return false;
    }
    
    console.log('→ Autenticado correctamente');
    return true;
}

// Verificar validez de la sesión según "Remember Me"
function checkSessionValidity() {
    const token = localStorage.getItem('token');
    const rememberSession = localStorage.getItem('rememberSession');
    
    if (!token) return;
    
    try {
        // Decodificar token JWT para verificar expiración
        const payload = parseJwt(token);
        const expirationTime = payload.exp * 1000;
        const currentTime = Date.now();
        
        // Si NO tiene "Remember Me" activado
        if (rememberSession !== 'true') {
            // Verificar si la pestaña se cerró (usando sessionStorage como indicador)
            if (!sessionStorage.getItem('sessionActive')) {
                // Primera carga de la página, marcar sesión como activa
                sessionStorage.setItem('sessionActive', 'true');
                
                // Configurar listener para detectar cierre de ventana
                window.addEventListener('beforeunload', () => {
                    // Si no hay "Remember Me", limpia el token al cerrar
                    if (localStorage.getItem('rememberSession') !== 'true') {
                        console.log('🔒 Sesión temporal - Limpiando al cerrar ventana');
                        // No limpiamos aquí porque beforeunload es inconsistente
                    }
                });
            }
        } else {
            console.log('✅ Remember Me activo - Sesión persistente');
        }
        
        // Verificar expiración del token
        if (currentTime >= expirationTime) {
            console.warn('⚠️ Token expirado');
            handleSessionExpired();
        }
        
    } catch (error) {
        console.error('Error verificando sesión:', error);
    }
}

// Manejar sesión expirada
function handleSessionExpired() {
    const rememberSession = localStorage.getItem('rememberSession');
    const savedEmail = localStorage.getItem('rememberedEmail');
    
    // Limpiar token
    localStorage.removeItem('token');
    
    // Si tiene "Remember Me", mantener el email guardado
    if (rememberSession === 'true' && savedEmail) {
        if (typeof showToast === 'function') {
            showToast('info', 'Sesión expirada', 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.');
        } else {
            alert('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.');
        }
    } else {
        // Limpiar todo
        localStorage.removeItem('rememberedEmail');
        localStorage.removeItem('rememberSession');
    }
    
    // Redirigir al login
    window.location.href = 'login.html';
}

// Función para inicializar verificación de autenticación
function initAuthCheck() {
    // Solo verificar en páginas que no son públicas
    const currentPath = window.location.pathname.toLowerCase();
    const isPublicPage = currentPath.includes('login') || currentPath.includes('register');
    
    if (isPublicPage) {
        console.log('📄 Página pública, no requiere autenticación');
        return;
    }
    
    console.log('🔍 Verificando autenticación...');
    
    // Verificar si tiene token
    const token = localStorage.getItem('token');
    
    if (!token) {
        console.log('❌ SIN TOKEN - Redirigiendo a login');
        window.location.href = 'login.html';
        return;
    }
    
    console.log('✅ Token encontrado - Acceso permitido');
    
    // Limpiar parámetro fromLogin de la URL si existe
    if (window.location.search.includes('fromLogin')) {
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    // Cargar info del usuario
    loadUserInfo();
}

// Flag para evitar múltiples ejecuciones
let authCheckInitialized = false;

// Función unificada para inicializar todo
function initializeAuth() {
    if (authCheckInitialized) {
        console.log('⚠️ Auth ya inicializado, evitando duplicación');
        return;
    }
    authCheckInitialized = true;
    
    console.log('🔍 Inicializando autenticación...');
    
    // Configurar menú de usuario
    setupUserMenu();
    
    // Ejecutar verificación de autenticación
    initAuthCheck();
}

// Ejecutar verificación cuando el DOM esté listo
console.log('Auth-handler.js: Configurando inicialización única');
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAuth, { once: true });
} else {
    // DOM ya está listo, ejecutar de inmediato
    console.log('Auth-handler.js: DOM ya cargado, ejecutando initializeAuth()');
    initializeAuth();
}

// Cargar información del usuario desde el token JWT
async function loadUserInfo() {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('No token found');
        }

        // Decodificar token JWT
        const payload = parseJwt(token);
        
        const userName = payload.email ? payload.email.split('@')[0] : 'Usuario';
        const userEmail = payload.email || 'user@example.com';
        
        // Actualizar elementos del perfil
        updateProfileElements(userName, userEmail);
        
        return { username: userName, email: userEmail };
    } catch (error) {
        console.error('Error loading user:', error);
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    }
}

// Actualizar elementos del DOM con información del usuario
function updateProfileElements(userName, userEmail) {
    const displayName = userName.charAt(0).toUpperCase() + userName.slice(1);
    
    // Actualizar avatar
    const avatarElements = document.querySelectorAll('#profileAvatar');
    avatarElements.forEach(el => {
        el.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=667eea&color=fff&bold=true`;
        el.alt = displayName;
    });
    
    // Actualizar nombre en header
    const nameElements = document.querySelectorAll('#profileName');
    nameElements.forEach(el => {
        const verifiedIcon = el.querySelector('.verified-badge');
        el.innerHTML = `${displayName}${verifiedIcon ? verifiedIcon.outerHTML : '<i class="fas fa-check-circle verified-badge"></i>'}`;
    });
    
    // Actualizar email
    const emailElements = document.querySelectorAll('#profileEmail, #dropdownUserEmail');
    emailElements.forEach(el => {
        el.textContent = userEmail;
    });
    
    // Actualizar nombre en dropdown
    const dropdownNameElements = document.querySelectorAll('#dropdownUserName');
    dropdownNameElements.forEach(el => {
        el.textContent = displayName;
    });
}

// Flag para evitar configurar el menú múltiples veces
let userMenuSetup = false;

// Configurar menú desplegable de usuario
function setupUserMenu() {
    if (userMenuSetup) {
        console.log('⚠️ Menú de usuario ya configurado');
        return;
    }
    
    const menuToggle = document.getElementById('userMenuToggle');
    const dropdown = document.getElementById('userDropdown');
    
    if (!menuToggle || !dropdown) {
        console.log('⚠️ Elementos de menú no encontrados');
        return;
    }
    
    userMenuSetup = true;
    console.log('✅ Configurando menú de usuario');
    
    // Toggle del menú
    menuToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('show');
        menuToggle.classList.toggle('active');
    });
    
    // Cerrar menú al hacer click fuera
    document.addEventListener('click', (e) => {
        if (!menuToggle.contains(e.target)) {
            dropdown.classList.remove('show');
            menuToggle.classList.remove('active');
        }
    });
    
    // Cerrar menú al hacer click en un item (excepto logout)
    const dropdownItems = dropdown.querySelectorAll('.dropdown-item:not(.logout)');
    dropdownItems.forEach(item => {
        item.addEventListener('click', () => {
            dropdown.classList.remove('show');
            menuToggle.classList.remove('active');
        });
    });
    
    // Registrar evento de logout usando data-action
    const logoutBtn = dropdown.querySelector('[data-action="logout"]');
    if (logoutBtn) {
        console.log('✅ Registrando evento de logout');
        logoutBtn.addEventListener('click', handleLogout);
    } else {
        console.warn('⚠️ Botón de logout no encontrado');
    }
}

// Logout mejorado con modal de confirmación
function handleLogout(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Mostrar modal de confirmación personalizado
    showConfirmationModal({
        title: '¿Cerrar Sesión?',
        message: '¿Estás seguro de que deseas cerrar tu sesión? Tendrás que volver a iniciar sesión para acceder.',
        confirmText: 'Cerrar Sesión',
        cancelText: 'Cancelar',
        onConfirm: () => {
            // Verificar si tiene "Remember Me" activado
            const rememberSession = localStorage.getItem('rememberSession');
            const savedEmail = localStorage.getItem('rememberedEmail');
            
            // Limpiar datos de autenticación
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            localStorage.removeItem('selectedAccount');
            
            // Si NO tiene "Remember Me", limpiar también el email guardado
            if (rememberSession !== 'true') {
                localStorage.removeItem('rememberedEmail');
                localStorage.removeItem('rememberSession');
                console.log('🔒 Sesión limpiada completamente');
            } else {
                console.log('✅ Email guardado para próximo login:', savedEmail);
            }
            
            // Limpiar sessionStorage
            sessionStorage.clear();
            
            // Mostrar notificación
            showToast('success', '¡Hasta pronto!', 'Has cerrado sesión correctamente');
            
            // Redirigir al login después de un pequeño delay
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 800);
        }
    });
}

// Mostrar modal de confirmación personalizado
function showConfirmationModal({ title, message, confirmText, cancelText, onConfirm, onCancel }) {
    // Evitar múltiples modales - si ya existe uno, no crear otro
    if (document.querySelector('.confirmation-modal-overlay')) {
        console.warn('⚠️ Modal de confirmación ya existe, evitando duplicación');
        return;
    }
    
    // Crear overlay
    const overlay = document.createElement('div');
    overlay.className = 'confirmation-modal-overlay';
    
    // Crear modal
    overlay.innerHTML = `
        <div class="confirmation-modal">
            <div class="modal-icon warning">
                <i class="fas fa-sign-out-alt"></i>
            </div>
            <h3 class="modal-title">${title}</h3>
            <p class="modal-message">${message}</p>
            <div class="modal-actions">
                <button class="modal-btn cancel">${cancelText}</button>
                <button class="modal-btn confirm">${confirmText}</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Event listeners
    const cancelBtn = overlay.querySelector('.modal-btn.cancel');
    const confirmBtn = overlay.querySelector('.modal-btn.confirm');
    
    const closeModal = () => {
        overlay.style.animation = 'fadeOut 0.2s ease';
        setTimeout(() => overlay.remove(), 200);
    };
    
    cancelBtn.addEventListener('click', () => {
        closeModal();
        if (onCancel) onCancel();
    });
    
    confirmBtn.addEventListener('click', () => {
        closeModal();
        if (onConfirm) onConfirm();
    });
    
    // Cerrar con click fuera
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            closeModal();
            if (onCancel) onCancel();
        }
    });
    
    // Cerrar con ESC
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeModal();
            if (onCancel) onCancel();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

// Mostrar notificaciones toast
function showToast(type, title, message, duration = 3000) {
    // Crear contenedor de toasts si no existe
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    // Crear toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type]} toast-icon"></i>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Cerrar toast
    const closeBtn = toast.querySelector('.toast-close');
    const removeToast = () => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    };
    
    closeBtn.addEventListener('click', removeToast);
    
    // Auto cerrar
    if (duration > 0) {
        setTimeout(removeToast, duration);
    }
}

// Agregar animación slideOutRight al CSS (se puede hacer dinámicamente)
if (!document.getElementById('toast-animations')) {
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.textContent = `
        @keyframes slideOutRight {
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
        @keyframes fadeOut {
            to { opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}

// Nota: La inicialización ya se maneja arriba con initializeAuth()
// que incluye setupUserMenu() y initAuthCheck()
