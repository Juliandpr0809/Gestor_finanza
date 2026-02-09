// ==========================================
// AUTH PAGES - LOGIN & REGISTER
// ==========================================

// Función helper para mostrar mensajes si showToast no está disponible
function showAuthMessage(type, title, message) {
    if (typeof showToast === 'function') {
        showToast(type, title, message);
    } else {
        // Fallback simple
        const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
        console.log(`${icon} ${title}: ${message}`);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded fired');
    console.log('api available:', typeof api !== 'undefined' ? 'YES' : 'NO');

    // Forms
    const loginForm = document.getElementById('loginForm');
    console.log('loginForm found:', !!loginForm);

    const registerForm = document.getElementById('registerForm');
    const loginFeedback = document.getElementById('loginFeedback');

    // Password toggles
    const togglePassword = document.getElementById('togglePassword');
    const togglePasswordRegister = document.getElementById('togglePasswordRegister');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');

    // Password strength (register only)
    const passwordRegister = document.getElementById('passwordRegister');
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');

    // ==========================================
    // PASSWORD VISIBILITY TOGGLE
    // ==========================================

    function setupPasswordToggle(button, inputId) {
        if (!button) return;

        button.addEventListener('click', () => {
            const input = document.getElementById(inputId);
            const icon = button.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }

    setupPasswordToggle(togglePassword, 'password');
    setupPasswordToggle(togglePasswordRegister, 'passwordRegister');
    setupPasswordToggle(toggleConfirmPassword, 'confirmPassword');

    // ==========================================
    // PASSWORD STRENGTH METER
    // ==========================================

    if (passwordRegister) {
        passwordRegister.addEventListener('input', (e) => {
            const password = e.target.value;
            const strength = calculatePasswordStrength(password);

            strengthFill.className = 'strength-fill';

            if (password.length === 0) {
                strengthFill.style.width = '0%';
                strengthText.textContent = 'Enter password';
                strengthText.style.color = 'rgba(255, 255, 255, 0.4)';
            } else if (strength.score < 3) {
                strengthFill.classList.add('weak');
                strengthText.textContent = 'Weak password';
                strengthText.style.color = '#FF3B30';
            } else if (strength.score < 4) {
                strengthFill.classList.add('medium');
                strengthText.textContent = 'Medium password';
                strengthText.style.color = '#FF9500';
            } else {
                strengthFill.classList.add('strong');
                strengthText.textContent = 'Strong password';
                strengthText.style.color = '#00D46A';
            }
        });
    }

    function calculatePasswordStrength(password) {
        let score = 0;

        if (password.length >= 8) score++;
        if (password.length >= 12) score++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
        if (/\d/.test(password)) score++;
        if (/[^a-zA-Z0-9]/.test(password)) score++;

        return { score };
    }

    function setButtonLoading(button, text) {
        if (!button) return () => { };
        const original = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `<i class="fas fa-spinner fa-spin"></i><span>${text}</span>`;
        return () => {
            button.disabled = false;
            button.innerHTML = original;
        };
    }

    // ==========================================
    // LOGIN FORM SUBMISSION
    // ==========================================

    if (loginForm) {
        // Cargar datos guardados si existe "Remember Me"
        const savedEmail = localStorage.getItem('rememberedEmail');
        const rememberCheckbox = document.getElementById('remember');
        const loginTermsCheckbox = document.getElementById('loginTerms');
        const emailInput = document.getElementById('email');
        const savedIndicator = document.getElementById('savedEmailIndicator');
        const setLoginFeedback = (type, message) => {
            if (!loginFeedback) return;
            loginFeedback.textContent = message || '';
            loginFeedback.className = 'auth-feedback';

            if (type && message) {
                loginFeedback.classList.add(type, 'show');
            }
        };

        if (savedEmail) {
            emailInput.value = savedEmail;
            if (rememberCheckbox) {
                rememberCheckbox.checked = true;
            }

            // Pre-chequear términos si el usuario ya los aceptó
            try {
                const accepted = localStorage.getItem('accepted_login_terms') === 'true';
                if (loginTermsCheckbox) loginTermsCheckbox.checked = !!accepted;
            } catch (_) {}

            // Mostrar indicador de email guardado
            if (savedIndicator) {
                savedIndicator.style.display = 'block';
            }

            // Agregar indicador visual de que el email está guardado
            emailInput.style.borderColor = 'rgba(0, 212, 106, 0.3)';
            emailInput.style.paddingRight = '40px'; // Espacio para el ícono

            // Mostrar mensaje de bienvenida si existe showToast
            setTimeout(() => {
                showAuthMessage('info', '¡Bienvenido de nuevo!', `Hemos recordado tu email: ${savedEmail}`);
            }, 500);
        }

        // Actualizar borde del email cuando cambie el checkbox
        if (rememberCheckbox) {
            rememberCheckbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    emailInput.style.borderColor = 'rgba(107, 159, 255, 0.3)';
                } else {
                    emailInput.style.borderColor = '';
                }
            });
        }

        // Ocultar indicador cuando el usuario edite el email
        emailInput.addEventListener('input', () => {
            if (savedIndicator && emailInput.value !== savedEmail) {
                savedIndicator.style.display = 'none';
                emailInput.style.paddingRight = '16px';
            } else if (savedIndicator && emailInput.value === savedEmail) {
                savedIndicator.style.display = 'block';
                emailInput.style.paddingRight = '40px';
            }
        });

        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('Login form submitted');

            const identifier = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const rememberMe = document.getElementById('remember').checked;
            const termsAccepted = document.getElementById('loginTerms') ? document.getElementById('loginTerms').checked : false;

            // Validar que se acepten los términos
            if (!termsAccepted) {
                showAuthMessage('warning', 'Términos requeridos', 'Debes aceptar los términos de servicio para continuar');
                setLoginFeedback('error', 'Por favor acepta los términos y condiciones');
                return;
            }
            const acceptedTerms = loginTermsCheckbox ? loginTermsCheckbox.checked : false;

            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const resetLoading = setButtonLoading(submitBtn, 'Signing in...');
            setLoginFeedback(null, '');

            if (!acceptedTerms) {
                resetLoading();
                setLoginFeedback('error', 'Debes aceptar los Términos y la Política de Privacidad.');
                showAuthMessage('error', 'Términos requeridos', 'Por favor acepta los Términos y la Política para continuar.');
                return;
            }

            api.login(identifier, password)
                .then((data) => {
                    console.log('Login successful:', data);
                    console.log('Token recibido:', data.access_token);
                    console.log('Token guardado en localStorage:', localStorage.getItem('token'));

                    // Manejar "Remember Me"
                    if (rememberMe) {
                        // Guardar email para la próxima vez
                        localStorage.setItem('rememberedEmail', identifier);
                        // Marcar que debe recordar la sesión
                        localStorage.setItem('rememberSession', 'true');
                        console.log('✅ Sesión guardada - Remember Me activado');
                    } else {
                        // Limpiar email guardado
                        localStorage.removeItem('rememberedEmail');
                        // Marcar que NO debe recordar (usar sessionStorage para el token)
                        localStorage.removeItem('rememberSession');
                        console.log('✅ Sesión temporal - Remember Me desactivado');
                    }

                    // Mostrar notificación de bienvenida
                    showAuthMessage('success', '¡Bienvenido!', 'Has iniciado sesión correctamente');
                    setLoginFeedback('success', '¡Inicio de sesión exitoso! Redirigiendo...');

                    // Guardar aceptación de términos para futuras sesiones
                    try { localStorage.setItem('accepted_login_terms', 'true'); } catch (_) {}

                    // Verificar que el token esté guardado antes de redirigir
                    const savedToken = localStorage.getItem('token');
                    console.log('Verificando token antes de redirigir:', savedToken ? 'EXISTE' : 'NO EXISTE');

                    // Redirigir inmediatamente con parámetro especial para evitar verificación
                    console.log('🚀 Redirigiendo a index.html?fromLogin=1');
                    window.location.replace('index.html?fromLogin=1');
                })
                .catch((err) => {
                    console.error('Login error:', err);

                    // Determinar mensaje de error específico
                    let errorTitle = 'Error de autenticación';
                    let errorMessage = 'Credenciales incorrectas';

                    if (err.message && err.message.includes('Failed to fetch')) {
                        errorTitle = 'Error de conexión';
                        errorMessage = 'No se puede conectar al servidor. Verifica que el backend esté corriendo.';
                    } else if (err.message && err.message.includes('CORS')) {
                        errorTitle = 'Error CORS';
                        errorMessage = 'Problema de configuración del servidor. Contacta al administrador.';
                    } else if (err.message) {
                        errorMessage = err.message;
                    }

                    // Mostrar notificación de error con más detalles
                    showAuthMessage('error', errorTitle, errorMessage);
                    setLoginFeedback('error', errorMessage);

                    resetLoading();
                });
        });
    } else {
        console.warn('loginForm not found!');
    }

    // ==========================================
    // REGISTER FORM SUBMISSION
    // ==========================================

    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('Register form submitted');

            const firstName = document.getElementById('firstName').value.trim();
            const lastName = document.getElementById('lastName').value.trim();
            const email = document.getElementById('emailRegister').value.trim();
            const password = document.getElementById('passwordRegister').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const terms = document.getElementById('terms').checked;

            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }

            if (!terms) {
                alert('Please accept the Terms of Service and Privacy Policy');
                return;
            }

            const strength = calculatePasswordStrength(password);
            if (strength.score < 3) {
                alert('Please use a stronger password');
                return;
            }

            const username = (email.split('@')[0] || 'user').replace(/[^a-zA-Z0-9._-]/g, '') || 'user';
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            const resetLoading = setButtonLoading(submitBtn, 'Creating account...');

            api.register(email, password, username)
                .then((data) => {
                    console.log('Register successful:', data);
                    window.location.href = '/frontend/html/index.html';
                })
                .catch((err) => {
                    console.error('Register error:', err);
                    alert(`⚠️ ${err.message}`);
                    resetLoading();
                });
        });
    } else {
        console.warn('registerForm not found!');
    }

    // ==========================================
    // SOCIAL LOGIN (SIMULATION)
    // ==========================================

    const socialButtons = document.querySelectorAll('.btn-social');
    socialButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const platform = btn.querySelector('span').textContent;
            alert(`🔐 ${platform} authentication coming soon!\n\nThis will allow you to sign in with your ${platform} account.`);
        });
    });

    // ==========================================
    // FORGOT PASSWORD LINK
    // ==========================================

    const forgotLink = document.querySelector('.link-forgot');
    if (forgotLink) {
        forgotLink.addEventListener('click', (e) => {
            e.preventDefault();
            alert('Password recovery feature coming soon! Contact support@ordenc.app');
        });
    }

    // ==========================================
    // LOGOUT HANDLER
    // ==========================================

    window.handleLogout = function () {
        api.logout().finally(() => {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('user');
            window.location.href = '/frontend/html/login.html';
        });
    };

    // ==========================================
    // LOGOUT (GLOBAL)
    // ==========================================

    window.performLogout = async () => {
        const token = localStorage.getItem('accessToken');
        try {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: token ? { 'Authorization': `Bearer ${token}` } : {}
            });
        } catch (err) {
            console.warn('Logout request failed (continuing):', err);
        }

        localStorage.removeItem('accessToken');
        localStorage.removeItem('user');
        window.location.href = '/frontend/html/login.html';
    };

    // ==========================================
    // AUTO-FILL DEMO (FOR TESTING)
    // ==========================================

    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'D') {
            if (loginForm) {
                document.getElementById('email').value = 'demo@demo.com';
                document.getElementById('password').value = 'demo1234';
            }
            if (registerForm) {
                document.getElementById('firstName').value = 'John';
                document.getElementById('lastName').value = 'Doe';
                document.getElementById('emailRegister').value = 'john.doe@example.com';
                document.getElementById('passwordRegister').value = 'SecurePass123!';
                document.getElementById('confirmPassword').value = 'SecurePass123!';
                document.getElementById('terms').checked = true;

                if (passwordRegister) {
                    passwordRegister.dispatchEvent(new Event('input'));
                }
            }
            console.log('Demo credentials filled!');
        }
    });
});
