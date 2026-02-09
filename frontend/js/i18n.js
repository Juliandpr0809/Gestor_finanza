/**
 * Sistema de Internacionalización (i18n)
 * Gestor Financiero OrdenC
 * Idiomas soportados: Español (es), Inglés (en)
 */

const translations = {
    es: {
        // Navigation
        'Dashboard': 'Panel',
        'Transactions': 'Transacciones',
        'Accounts': 'Cuentas',
        'Reports': 'Reportes',
        'AI Chat': 'Chat IA',
        'AI Assistant': 'Asistente IA',
        'Logout': 'Cerrar Sesión',
        'User Guide': 'Guía de Uso',

        // Common
        'Save': 'Guardar',
        'Cancel': 'Cancelar',
        'Edit': 'Editar',
        'Delete': 'Eliminar',
        'Close': 'Cerrar',
        'Search': 'Buscar',
        'Filter': 'Filtrar',
        'Loading': 'Cargando',
        'Error': 'Error',
        'Success': 'Éxito',
        'Confirm': 'Confirmar',
        'Back': 'Volver',
        'Next': 'Siguiente',
        'Previous': 'Anterior',
        'Select': 'Seleccionar',
        'All': 'Todos',
        'None': 'Ninguno',
        'Loading': 'Cargando',

        // Dashboard
        'Total Balance': 'Balance Total',
        'Quick Actions': 'Acciones Rápidas',
        'Recent Transactions': 'Transacciones Recientes',
        'Add Income': 'Agregar Ingreso',
        'Add Expense': 'Agregar Gasto',
        'Transfer': 'Transferir',
        'View All': 'Ver Todo',
        'No transactions yet': 'Sin transacciones aún',
        'Start by adding your first transaction': 'Comienza agregando tu primera transacción',
        'dashboard.cards.title': 'Mis Tarjetas Virtuales',
        'dashboard.add.card': 'Agregar Nueva Tarjeta',
        'dashboard.add.transaction': 'Agregar Transacción',
        'dashboard.upload.files': 'Subir Archivos',
        'dashboard.voice.input': 'Entrada de Voz',
        'dashboard.scan.receipt': 'Escanear Recibo',

        // Transactions
        'New Transaction': 'Nueva Transacción',
        'All Transactions': 'Todas las Transacciones',
        'transactions.subtitle': 'Rastrea tus ingresos y gastos.',
        'Income': 'Ingreso',
        'Expense': 'Gasto',
        'Balance': 'Balance',
        'Date': 'Fecha',
        'Amount': 'Monto',
        'Category': 'Categoría',
        'Account': 'Cuenta',
        'Description': 'Descripción',
        'Type': 'Tipo',
        'Notes': 'Notas',
        'Search transactions...': 'Buscar transacciones...',
        'All Types': 'Todos los Tipos',
        'All Categories': 'Todas las Categorías',
        'All Accounts': 'Todas las Cuentas',
        'Food & Dining': 'Comida',
        'Transportation': 'Transporte',
        'Entertainment': 'Entretenimiento',
        'Shopping': 'Compras',
        'Bills & Utilities': 'Facturas',
        'Healthcare': 'Salud',
        'Salary': 'Salario',
        'Freelance': 'Freelance',
        'Other': 'Otro',
        'NAME': 'NOMBRE',
        'DATE': 'FECHA',
        'CATEGORY': 'CATEGORÍA',
        'AMOUNT': 'MONTO',
        'ACTIONS': 'ACCIONES',

        // Filtros Rápidos
        'filter.all': 'Todos',
        'filter.today': 'Hoy',
        'filter.week': 'Esta Semana',
        'filter.month': 'Este Mes',
        'filter.high': 'Montos Altos',
        'filter.income': 'Ingresos',
        'filter.expense': 'Gastos',
        'Today': 'Hoy',
        'This Week': 'Esta Semana',
        'This Month': 'Este Mes',
        'High Amounts': 'Montos Altos',
        'Expenses': 'Gastos',

        // Accounts
        'My Accounts': 'Mis Cuentas',
        'Add Account': 'Agregar Cuenta',
        'accounts.subtitle': 'Gestiona tus cuentas bancarias y balances',
        'Account Name': 'Nombre de Cuenta',
        'Account Type': 'Tipo de Cuenta',
        'Initial Balance': 'Balance Inicial',
        'Current Balance': 'Balance Actual',
        'Total Balance': 'Balance Total',
        'Bank Accounts': 'Cuentas Bancarias',
        'Credit Cards': 'Tarjetas de Crédito',
        'Savings Goals': 'Metas de Ahorro',
        'accounts.change.lastmonth': '+12.5% desde el mes pasado',
        'accounts.checking.savings': '2 corriente, 1 ahorros',
        'accounts.available.credit': '$2,340 crédito disponible',
        'Checking': 'Corriente',
        'Savings': 'Ahorros',
        'Credit': 'Crédito',
        'Cash': 'Efectivo',
        'Bank': 'Banco',
        'Credit Card': 'Tarjeta de Crédito',
        'Investment': 'Inversión',

        // Account Modal
        'Add New Account': 'Agregar Nueva Cuenta',
        'Edit Account': 'Editar Cuenta',
        'Save Account': 'Guardar Cuenta',
        'Bank/Institution': 'Banco / Institución',
        'Account Number (Last 4 digits)': 'Número de Cuenta (4 dígitos)',
        'Credit Limit': 'Cupo de Crédito',
        'Savings Goal (Optional)': 'Meta de Ahorro (Opcional)',
        'Select type': 'Seleccionar tipo',
        'Checking Account': 'Cuenta Corriente',
        'Savings Account': 'Cuenta de Ahorros',
        'Cash / Wallet': 'Efectivo / Billetera',
        'COP - Colombian Peso': 'COP - Peso Colombiano',
        'USD - US Dollar': 'USD - Dólar Estadounidense',
        'EUR - Euro': 'EUR - Euro',
        'MXN - Mexican Peso': 'MXN - Peso Mexicano',
        'e.g., Main Checking': 'ej. Cuenta Principal',
        'e.g., Chase Bank': 'ej. Bancolombia',

        // Reports
        'Financial Reports': 'Reportes Financieros',
        'Analytics': 'Análisis',
        'Charts': 'Gráficos',
        'Export': 'Exportar',
        'Reports & Analytics': 'Reportes y Análisis',
        'reports.subtitle': 'Panel de reportes financieros y análisis próximamente. ¡Rastrea tus patrones de gasto e insights!',
        'Ask AI Assistant': 'Preguntar a IA',
        'Back to Dashboard': 'Volver al Panel',

        // AI Chat
        'Type your message': 'Escribe tu mensaje',
        'Send': 'Enviar',
        'Clear Chat': 'Limpiar Chat',
        'Help': 'Ayuda',

        // Auth
        'Login': 'Iniciar Sesión',
        'Register': 'Registrarse',
        'Email': 'Correo',
        'Password': 'Contraseña',
        'Forgot Password?': '¿Olvidaste tu Contraseña?',
        'Remember Me': 'Recordarme',
        'Active': 'Activa',
        'Inactive': 'Inactiva',
        'checking': 'corriente',
        'savings': 'ahorros',
        'credit': 'crédito',
        'investment': 'inversión',
        'cash': 'efectivo',
        'of target': 'de la meta',

        // Login specific
        'login.tagline': 'Tu asistente financiero personal',
        'Bank-level Security': 'Seguridad Bancaria',
        'login.security.desc': 'Encriptación de extremo a extremo',
        'Smart Insights': 'Análisis Inteligentes',
        'login.insights.desc': 'Analítica financiera con IA',
        'Multi-Platform': 'Multi-Plataforma',
        'login.platform.desc': 'Accede desde cualquier lugar',
        'Active Users': 'Usuarios Activos',
        'Managed': 'Gestionado',
        'Rating': 'Calificación',
        'Welcome Back': 'Bienvenido de Vuelta',
        'login.subtitle': 'Inicia sesión para continuar',
        'Email Address': 'Correo Electrónico',
        'Enter your password': 'Ingresa tu contraseña',
        'Remember me for 30 days': 'Recuérdame 30 días',
        'Forgot password?': '¿Olvidaste tu contraseña?',
        'Sign In': 'Iniciar Sesión',
        'or continue with': 'o continúa con',
        'Don\'t have an account?': '¿No tienes cuenta?',
        'Sign up': 'Regístrate',

        // Register specific
        'register.tagline': 'Comienza tu viaje financiero hoy',
        'Quick Setup': 'Configuración Rápida',
        'register.quicksetup.desc': 'Comienza en menos de 2 minutos',
        'Free Forever': 'Gratis Siempre',
        'register.free.desc': 'Sin cargos ocultos ni suscripciones',
        '24/7 Support': 'Soporte 24/7',
        'register.support.desc': 'Estamos aquí cuando nos necesites',
        'Create Account': 'Crear Cuenta',
        'register.subtitle': 'Únete a miles de usuarios gestionando mejor sus finanzas',
        'First Name': 'Nombre',
        'Last Name': 'Apellido',
        'Confirm Password': 'Confirmar Contraseña',
        'Create a strong password': 'Crea una contraseña fuerte',
        'Confirm your password': 'Confirma tu contraseña',
        'register.terms': 'Acepto los ',
        'Terms of Service': 'Términos de Servicio',
        'register.and': ' y la ',
        'Privacy Policy': 'Política de Privacidad',
        'or sign up with': 'o regístrate con',
        'Already have an account?': '¿Ya tienes cuenta?',
        'Sign in': 'Inicia sesión',

        // Settings
        'Settings': 'Configuración',
        'Language': 'Idioma',
        'Spanish': 'Español',
        'English': 'Inglés',
        'Theme': 'Tema',
        'Currency': 'Moneda',
        'Notifications': 'Notificaciones',
        'Privacy': 'Privacidad',
        'About': 'Acerca de',

        // Messages
        'Are you sure?': '¿Estás seguro?',
        'This action cannot be undone': 'Esta acción no se puede deshacer',
        'Transaction added successfully': 'Transacción agregada exitosamente',
        'Transaction updated successfully': 'Transacción actualizada exitosamente',
        'Transaction deleted successfully': 'Transacción eliminada exitosamente',
        'Account created successfully': 'Cuenta creada exitosamente',
        'Account updated successfully': 'Cuenta actualizada exitosamente',
        'Account deleted successfully': 'Cuenta eliminada exitosamente',
    },

    en: {
        // Navigation (ya están en inglés, pero las incluyo para consistencia)
        'Dashboard': 'Dashboard',
        'Transactions': 'Transactions',
        'Accounts': 'Accounts',
        'Reports': 'Reports',
        'AI Chat': 'AI Chat',
        'AI Assistant': 'AI Assistant',
        'Logout': 'Logout',
        'User Guide': 'User Guide',

        // Common
        'Save': 'Save',
        'Cancel': 'Cancel',
        'Edit': 'Edit',
        'Delete': 'Delete',
        'Close': 'Close',
        'Search': 'Search',
        'Filter': 'Filter',
        'Loading': 'Loading',
        'Error': 'Error',
        'Success': 'Success',
        'Confirm': 'Confirm',
        'Back': 'Back',
        'Next': 'Next',
        'Previous': 'Previous',
        'Select': 'Select',
        'All': 'All',
        'None': 'None',

        // Dashboard
        'Total Balance': 'Total Balance',
        'Quick Actions': 'Quick Actions',
        'Recent Transactions': 'Recent Transactions',
        'Add Income': 'Add Income',
        'Add Expense': 'Add Expense',
        'Transfer': 'Transfer',
        'View All': 'View All',
        'No transactions yet': 'No transactions yet',
        'Start by adding your first transaction': 'Start by adding your first transaction',
        'dashboard.cards.title': 'My Virtual Cards',
        'dashboard.add.card': 'Add New Card',
        'dashboard.add.transaction': 'Add Transaction',
        'dashboard.upload.files': 'Upload Files',
        'dashboard.voice.input': 'Voice Input',
        'dashboard.scan.receipt': 'Scan Receipt',
        'No transactions yet': 'No transactions yet',
        'Start by adding your first transaction': 'Start by adding your first transaction',

        // Reports
        'Reports & Analytics': 'Reports & Analytics',
        'reports.subtitle': 'Financial reports and analytics dashboard coming soon. Track your spending patterns and insights!',
        'Ask AI Assistant': 'Ask AI Assistant',
        'Back to Dashboard': 'Back to Dashboard',

        // Transactions
        'New Transaction': 'New Transaction',
        'All Transactions': 'All Transactions',
        'transactions.subtitle': 'Track your income and expenses.',
        'Income': 'Income',
        'Expense': 'Expense',
        'Balance': 'Balance',
        'Date': 'Date',
        'Amount': 'Amount',
        'Category': 'Category',
        'Account': 'Account',
        'Description': 'Description',
        'Type': 'Type',
        'Notes': 'Notes',
        'Search transactions...': 'Search transactions...',
        'All Types': 'All Types',
        'All Categories': 'All Categories',
        'All Accounts': 'All Accounts',
        'Food & Dining': 'Food & Dining',
        'Transportation': 'Transportation',
        'Entertainment': 'Entertainment',
        'Shopping': 'Shopping',
        'Bills & Utilities': 'Bills & Utilities',
        'Healthcare': 'Healthcare',
        'Salary': 'Salary',
        'Freelance': 'Freelance',
        'Other': 'Other',
        'NAME': 'NAME',
        'DATE': 'DATE',
        'CATEGORY': 'CATEGORY',
        'AMOUNT': 'AMOUNT',
        'ACTIONS': 'ACTIONS',

        // Quick Filters
        'filter.all': 'All',
        'filter.today': 'Today',
        'filter.week': 'This Week',
        'filter.month': 'This Month',
        'filter.high': 'High Amounts',
        'filter.income': 'Income',
        'filter.expense': 'Expenses',
        'Today': 'Today',
        'This Week': 'This Week',
        'This Month': 'This Month',
        'High Amounts': 'High Amounts',
        'Expenses': 'Expenses',
        'CATEGORY': 'CATEGORY',
        'AMOUNT': 'AMOUNT',
        'ACTIONS': 'ACTIONS',

        // Accounts
        'My Accounts': 'My Accounts',
        'Add Account': 'Add Account',
        'accounts.subtitle': 'Manage your bank accounts and balances',
        'Account Name': 'Account Name',
        'Account Type': 'Account Type',
        'Initial Balance': 'Initial Balance',
        'Current Balance': 'Current Balance',
        'Total Balance': 'Total Balance',
        'Bank Accounts': 'Bank Accounts',
        'Credit Cards': 'Credit Cards',
        'Savings Goals': 'Savings Goals',
        'accounts.change.lastmonth': '+12.5% from last month',
        'accounts.checking.savings': '2 checking, 1 savings',
        'accounts.available.credit': '$2,340 available credit',
        'Checking': 'Checking',
        'Savings': 'Savings',
        'Credit': 'Credit',
        'Cash': 'Cash',
        'Bank': 'Bank',
        'Credit Card': 'Credit Card',
        'Investment': 'Investment',
        'Initial Balance': 'Initial Balance',
        'Current Balance': 'Current Balance',
        'Cash': 'Cash',
        'Bank': 'Bank',
        'Credit Card': 'Credit Card',
        'Savings': 'Savings',
        'Investment': 'Investment',

        // Reports
        'Financial Reports': 'Financial Reports',
        'Analytics': 'Analytics',
        'Charts': 'Charts',
        'Export': 'Export',

        // AI Chat
        'Type your message': 'Type your message',
        'Send': 'Send',
        'Clear Chat': 'Clear Chat',
        'Help': 'Help',

        // Auth
        'Login': 'Login',
        'Register': 'Register',
        'Email': 'Email',
        'Password': 'Password',
        'Forgot Password?': 'Forgot Password?',
        'Remember Me': 'Remember Me',

        // Login specific
        'login.tagline': 'Your personal financial assistant',
        'Bank-level Security': 'Bank-level Security',
        'login.security.desc': 'End-to-end encryption for your data',
        'Smart Insights': 'Smart Insights',
        'login.insights.desc': 'AI-powered financial analytics',
        'Multi-Platform': 'Multi-Platform',
        'login.platform.desc': 'Access from anywhere, anytime',
        'Active Users': 'Active Users',
        'Managed': 'Managed',
        'Rating': 'Rating',
        'Welcome Back': 'Welcome Back',
        'login.subtitle': 'Sign in to your account to continue',
        'Email Address': 'Email Address',
        'Enter your password': 'Enter your password',
        'Remember me for 30 days': 'Remember me for 30 days',
        'Forgot password?': 'Forgot password?',
        'Sign In': 'Sign In',
        'or continue with': 'or continue with',
        'Don\'t have an account?': 'Don\'t have an account?',
        'Sign up': 'Sign up',

        // Register specific
        'register.tagline': 'Start your financial journey today',
        'Quick Setup': 'Quick Setup',
        'register.quicksetup.desc': 'Get started in less than 2 minutes',
        'Free Forever': 'Free Forever',
        'register.free.desc': 'No hidden fees or subscriptions',
        '24/7 Support': '24/7 Support',
        'register.support.desc': 'We\'re here whenever you need us',
        'Create Account': 'Create Account',
        'register.subtitle': 'Join thousands of users managing their finances smarter',
        'First Name': 'First Name',
        'Last Name': 'Last Name',
        'Confirm Password': 'Confirm Password',
        'Create a strong password': 'Create a strong password',
        'Confirm your password': 'Confirm your password',
        'register.terms': 'I agree to the ',
        'Terms of Service': 'Terms of Service',
        'register.and': ' and ',
        'Privacy Policy': 'Privacy Policy',
        'or sign up with': 'or sign up with',
        'Already have an account?': 'Already have an account?',
        'Sign in': 'Sign in',

        // Settings
        'Settings': 'Settings',
        'Language': 'Language',
        'Spanish': 'Spanish',
        'English': 'English',
        'Theme': 'Theme',
        'Currency': 'Currency',
        'Notifications': 'Notifications',
        'Privacy': 'Privacy',
        'About': 'About',

        // Messages
        'Are you sure?': 'Are you sure?',
        'This action cannot be undone': 'This action cannot be undone',
        'Transaction added successfully': 'Transaction added successfully',
        'Transaction updated successfully': 'Transaction updated successfully',
        'Transaction deleted successfully': 'Transaction deleted successfully',
        'Account created successfully': 'Account created successfully',
        'Account updated successfully': 'Account updated successfully',
        'Account deleted successfully': 'Account deleted successfully',
    }
};

// Estado global del idioma
let currentLang = localStorage.getItem('appLanguage') || 'es'; // Español por defecto

/**
 * Obtiene la traducción de una clave en el idioma actual
 */
function t(key) {
    return translations[currentLang][key] || key;
}

/**
 * Cambia el idioma de la aplicación
 */
function setLanguage(lang) {
    if (!translations[lang]) {
        console.error(`Idioma no soportado: ${lang}`);
        return;
    }

    currentLang = lang;
    localStorage.setItem('appLanguage', lang);

    // Actualizar la página
    translatePage();

    // Actualizar el selector de idioma si existe
    updateLanguageSelector();

    // Dispatch evento para que otros scripts sepan del cambio
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
}

/**
 * Traduce todos los elementos con data-i18n
 */
function translatePage() {
    // Traducir elementos con data-i18n
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);

        // Si es un input o textarea, traducir el placeholder
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            if (element.hasAttribute('placeholder')) {
                element.setAttribute('placeholder', translation);
            }
        } else if (element.tagName === 'BUTTON' || element.tagName === 'A') {
            // Para botones y links, mantener solo el texto
            element.textContent = translation;
        } else {
            element.textContent = translation;
        }
    });

    // Traducir placeholders con data-i18n-placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        element.setAttribute('placeholder', t(key));
    });

    // Traducir títulos (title attribute)
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        element.setAttribute('title', t(key));
    });

    // Traducir el título de la página si tiene data-i18n
    if (document.title.includes('-')) {
        const titleParts = document.title.split('-');
        const titleKey = titleParts[0].trim();
        if (translations[currentLang][titleKey]) {
            document.title = `${t(titleKey)} - OrdenC`;
        }
    }
}

/**
 * Actualiza el selector de idioma activo
 */
function updateLanguageSelector() {
    document.querySelectorAll('[data-lang-btn]').forEach(btn => {
        const btnLang = btn.getAttribute('data-lang-btn');
        if (btnLang === currentLang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

/**
 * Inicializa el sistema de idiomas
 */
function initI18n() {
    // Traducir la página al cargar
    translatePage();

    // Configurar botones de idioma
    document.querySelectorAll('[data-lang-btn]').forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.getAttribute('data-lang-btn');
            setLanguage(lang);
        });
    });

    // Actualizar selector inicial
    updateLanguageSelector();
}

// Auto-inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initI18n);
} else {
    initI18n();
}

// Exportar funciones para uso global
window.i18n = {
    t,
    setLanguage,
    getCurrentLanguage: () => currentLang,
    translatePage
};
