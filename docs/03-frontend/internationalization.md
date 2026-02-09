# 🌍 Sistema de Internacionalización (i18n)

Documentación del sistema multiidioma.

## 🎯 Idiomas Soportados

- 🇪🇸 **Español** (es)
- 🇬🇧 **English** (en)

## 📁 Arquitectura

```
frontend/
├── js/
│   ├── i18n.js           # Motor de traducciones
│   └── lang-helper.js    # Helpers de idioma
└── html/
    └── *.html           # Archivos con atributos data-i18n
```

## 🔧 Cómo Funciona

### 1. Definir Traducciones

En `js/i18n.js`:

```javascript
const translations = {
  es: {
    "Dashboard": "Panel",
    "Accounts": "Cuentas",
    "Transactions": "Transacciones",
    "login.title": "Iniciar Sesión",
    "login.subtitle": "Ingresa tus credenciales"
  },
  en: {
    "Dashboard": "Dashboard",
    "Accounts": "Accounts",
    "Transactions": "Transactions",
    "login.title": "Sign In",
    "login.subtitle": "Enter your credentials"
  }
};
```

### 2. Marcar Elementos HTML

```html
<!-- Texto simple -->
<h1 data-i18n="Dashboard">Panel</h1>

<!-- Placeholder -->
<input 
  type="text" 
  data-i18n-placeholder="Enter your email"
  placeholder="Ingresa tu email">

<!-- Title attribute -->
<button 
  data-i18n-title="Click to logout"
  title="Click para cerrar sesión">
  <i class="fas fa-sign-out"></i>
</button>
```

### 3. Cargar Sistema i18n

```html
<script src="../js/i18n.js"></script>
<script>
  // El idioma se aplica automáticamente al cargar
</script>
```

## 🎛️ Selector de Idioma

```html
<div class="lang-selector">
  <button class="lang-btn" data-lang-btn="es">ES</button>
  <button class="lang-btn" data-lang-btn="en">EN</button>
</div>
```

Estilado en `css/lang-selector.css`.

## 💾 Persistencia

El idioma seleccionado se guarda en `localStorage`:

```javascript
// Cambiar idioma
function setLanguage(lang) {
  localStorage.setItem('preferred_language', lang);
  applyTranslations(lang);
}

// Al cargar página
const saved = localStorage.getItem('preferred_language') || 'es';
setLanguage(saved);
```

## 🔄 API de i18n

```javascript
// Cambiar idioma manual
window.i18n.setLanguage('en');

// Obtener traducción
const text = window.i18n.t('dashboard.title');

// Traducir elemento dinámicamente
window.i18n.translateElement(element);
```

## ➕ Agregar Nuevo Idioma

1. Agregar traducciones en `i18n.js`:

```javascript
const translations = {
  es: { ... },
  en: { ... },
  fr: {  // Nuevo idioma
    "Dashboard": "Tableau de bord",
    "Accounts": "Comptes",
    ...
  }
};
```

2. Agregar botón en selector:

```html
<button class="lang-btn" data-lang-btn="fr">FR</button>
```

3. Agregar bandera si es necesario.

## 📝 Mejores Prácticas

### Usar Keys Descriptivas

```javascript
// ✅ Bien
"dashboard.welcome": "Bienvenido",
"auth.login.title": "Iniciar Sesión",
"error.network": "Error de conexión"

// ❌ Evitar
"text1": "Bienvenido",
"btn2": "Login"
```

### Agrupar por Contexto

```javascript
const translations = {
  es: {
    // Autenticación
    "auth.login": "Iniciar Sesión",
    "auth.register": "Registrarse",
    "auth.logout": "Cerrar Sesión",
    
    // Dashboard
    "dashboard.title": "Panel Principal",
    "dashboard.stats": "Estadísticas",
  }
};
```

### Valores por Defecto

El texto en el HTML sirve como fallback:

```html
<!-- Si falta traducción, muestra "Panel" -->
<h1 data-i18n="Dashboard">Panel</h1>
```

## 🌐 Traducciones Dinámicas

Para contenido generado con JavaScript:

```javascript
// Crear elemento
const btn = document.createElement('button');
btn.textContent = window.i18n.t('Save');
btn.dataset.i18n = 'Save';

// O usar plantillas
const html = `
  <div>
    <h2 data-i18n="welcome">${window.i18n.t('welcome')}</h2>
  </div>
`;
```

## 📊 Cobertura de Traducciones

Verificar que todas las keys existen en todos los idiomas:

```javascript
// Script helper
function checkTranslationCoverage() {
  const langs = Object.keys(translations);
  const allKeys = new Set();
  
  langs.forEach(lang => {
    Object.keys(translations[lang]).forEach(key => allKeys.add(key));
  });
  
  langs.forEach(lang => {
    const missing = [];
    allKeys.forEach(key => {
      if (!translations[lang][key]) {
        missing.push(key);
      }
    });
    if (missing.length > 0) {
      console.warn(`Lang '${lang}' missing:`, missing);
    }
  });
}
```
