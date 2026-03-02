/**
 * Utilidad para guardar credenciales de forma segura (encriptación básica)
 * NOTA: No es 100% seguro, pero mejor que texto plano
 */

const CredentialStore = {
    // Clave de encriptación simple (en producción debería ser más robusta)
    SECRET_KEY: 'OrdenC_2026_SecureKey_!@#',

    /**
     * Encripta un texto usando XOR + Base64
     */
    encrypt(text) {
        if (!text) return '';
        
        let encrypted = '';
        const key = this.SECRET_KEY;
        
        for (let i = 0; i < text.length; i++) {
            encrypted += String.fromCharCode(
                text.charCodeAt(i) ^ key.charCodeAt(i % key.length)
            );
        }
        
        // Convertir a Base64 para que sea almacenable
        return btoa(encrypted);
    },

    /**
     * Desencripta un texto
     */
    decrypt(encrypted) {
        if (!encrypted) return '';
        
        try {
            const decoded = atob(encrypted);
            let decrypted = '';
            const key = this.SECRET_KEY;
            
            for (let i = 0; i < decoded.length; i++) {
                decrypted += String.fromCharCode(
                    decoded.charCodeAt(i) ^ key.charCodeAt(i % key.length)
                );
            }
            
            return decrypted;
        } catch (e) {
            console.error('Error al desencriptar:', e);
            return '';
        }
    },

    /**
     * Guarda credenciales encriptadas
     */
    saveCredentials(email, password) {
        try {
            localStorage.setItem('saved_email', email); // Email en claro (no es sensible)
            localStorage.setItem('saved_pwd', this.encrypt(password)); // Contraseña encriptada
            localStorage.setItem('credentials_saved', 'true');
            console.log('✅ Credenciales guardadas de forma segura');
        } catch (e) {
            console.error('Error guardando credenciales:', e);
        }
    },

    /**
     * Recupera credenciales
     */
    loadCredentials() {
        try {
            const saved = localStorage.getItem('credentials_saved');
            if (saved !== 'true') return null;

            const email = localStorage.getItem('saved_email');
            const encryptedPwd = localStorage.getItem('saved_pwd');
            
            if (!email || !encryptedPwd) return null;

            return {
                email: email,
                password: this.decrypt(encryptedPwd)
            };
        } catch (e) {
            console.error('Error recuperando credenciales:', e);
            return null;
        }
    },

    /**
     * Elimina credenciales guardadas
     */
    clearCredentials() {
        try {
            localStorage.removeItem('saved_email');
            localStorage.removeItem('saved_pwd');
            localStorage.removeItem('credentials_saved');
            localStorage.removeItem('rememberedEmail'); // Legacy
            console.log('🗑️ Credenciales eliminadas');
        } catch (e) {
            console.error('Error eliminando credenciales:', e);
        }
    },

    /**
     * Verifica si hay credenciales guardadas
     */
    hasCredentials() {
        return localStorage.getItem('credentials_saved') === 'true';
    }
};

// Exportar para uso global
window.CredentialStore = CredentialStore;
