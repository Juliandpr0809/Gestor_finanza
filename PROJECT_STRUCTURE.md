# 📁 Estructura del Proyecto FinanceFlow

Estructura completa y organizada del proyecto.

## 🏗️ Estructura General

```
Gestor_finansas/
│
├── 📄 README.md                 # Documentación principal
├── 📄 LICENSE                   # Licencia MIT
├── 📄 CHANGELOG.md              # Historia de cambios
├── 📄 CONTRIBUTING.md           # Guía para contribuir
├── 📄 DEVELOPMENT.md            # Guía de desarrollo
├── 📄 DEPLOYMENT.md             # Guía de despliegue
├── 📄 .gitignore                # Archivos ignorados por Git
│
├── 📁 backend/                  # Backend Flask
│   ├── 📄 app.py                # Aplicación principal
│   ├── 📄 config.py             # Configuraciones
│   ├── 📄 requirements.txt      # Dependencias producción
│   ├── 📄 requirements-test.txt # Dependencias desarrollo
│   ├── 📄 pytest.ini            # Configuración pytest
│   ├── 📄 README.md             # Documentación backend
│   ├── 📄 .env.example          # Ejemplo variables entorno
│   │
│   ├── 📁 models/               # Modelos de datos
│   │   ├── __init__.py
│   │   └── ... (User, Account, Transaction, etc.)
│   │
│   ├── 📁 routes/               # Endpoints API REST
│   │   ├── __init__.py
│   │   ├── auth.py              # Autenticación
│   │   ├── accounts.py          # Gestión de cuentas
│   │   ├── categories.py        # Categorías
│   │   ├── transactions.py      # Transacciones
│   │   └── chat.py              # Chat con IA
│   │
│   ├── 📁 services/             # Lógica de negocio
│   │   ├── ai_service.py        # Servicio IA
│   │   ├── groq_service.py      # Integración Groq
│   │   └── ...
│   │
│   ├── 📁 schemas/              # Validación y serialización
│   │   ├── __init__.py
│   │   └── ... (Marshmallow schemas)
│   │
│   ├── 📁 utils/                # Utilidades
│   │   ├── jwt_utils.py         # JWT helpers
│   │   ├── validators.py        # Validadores
│   │   └── ...
│   │
│   ├── 📁 scripts/              # Scripts de administración
│   │   ├── check_transactions.py
│   │   ├── apply_migrations.py
│   │   ├── add_i18n.sh
│   │   └── ...
│   │
│   ├── 📁 tests/                # Tests unitarios backend
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_security.py
│   │   ├── test_validation.py
│   │   ├── test_categorization_efficiency.py
│   │   └── ...
│   │
│   ├── 📁 migrations/           # Migraciones Alembic
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   └── versions/
│   │
│   └── 📁 config_files/         # Archivos de configuración
│       ├── .env.example
│       └── .gitignore
│
├── 📁 frontend/                 # Frontend (PWA)
│   ├── 📄 manifest.json         # PWA Manifest
│   ├── 📄 service-worker.js     # Service Worker
│   ├── 📄 THEME_DOCUMENTATION.md
│   │
│   ├── 📁 html/                 # Páginas HTML
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   └── ...
│   │
│   ├── 📁 css/                  # Estilos
│   │   ├── main.css
│   │   ├── theme.css
│   │   └── ...
│   │
│   └── 📁 js/                   # JavaScript
│       ├── app.js
│       ├── api.js
│       ├── auth.js
│       └── ...
│
├── 📁 tests/                    # Tests de integración
│   ├── test_ai_variety.py
│   ├── test_chat_flow.py
│   ├── test_control_commands.py
│   ├── test_currencies.py
│   ├── test_datetime.py
│   ├── test_login.py
│   ├── test_all_endpoints.py
│   ├── test_command_detection.py
│   ├── test_edit.py
│   ├── stress_test_ai.py
│   └── run_complete_tests.py
│
├── 📁 docs/                     # Documentación completa
│   ├── 📄 README.md
│   ├── 📄 API.md                # Documentación API
│   ├── 📄 BACKEND_STRUCTURE.md # Estructura backend
│   ├── 📄 CONTROL_USUARIO_CHAT.md
│   ├── 📄 DEPENDENCIAS.md
│   ├── 📄 ESTRUCTURA.md
│   ├── 📄 SETUP.md
│   ├── 📄 RESUMEN_CONTROL_USUARIO.md
│   ├── 📄 EJEMPLOS_API.json     # Ejemplos de API
│   │
│   ├── 📁 01-getting-started/   # Guías de inicio
│   ├── 📁 02-backend/           # Docs backend
│   ├── 📁 03-frontend/          # Docs frontend
│   ├── 📁 pwa/                  # Documentación PWA
│   └── 📁 resumenes/            # Resúmenes
│
├── 📁 config/                   # Configuraciones globales
│
├── 📁 instance/                 # Datos de instancia (ignorado por Git)
│   └── financeflow.db           # Base de datos SQLite
│
├── 📁 .venv/                    # Entorno virtual Python (ignorado)
│
└── 📁 .vscode/                  # Configuración VS Code (ignorado)
```

## 📋 Descripción de Carpetas Principales

### 🔹 Backend (`/backend`)

Contiene toda la lógica del servidor Flask:

- **models/** - Definición de modelos de base de datos con SQLAlchemy
- **routes/** - Endpoints de la API REST organizados por recurso
- **services/** - Lógica de negocio y servicios externos (IA, etc.)
- **schemas/** - Validación y serialización de datos con Marshmallow
- **utils/** - Funciones utilitarias reutilizables
- **scripts/** - Scripts de administración y mantenimiento
- **tests/** - Tests unitarios del backend
- **migrations/** - Control de versiones de la base de datos

### 🔹 Frontend (`/frontend`)

Aplicación web progresiva (PWA):

- **html/** - Páginas HTML de la aplicación
- **css/** - Hojas de estilo y temas
- **js/** - Lógica de frontend en JavaScript vanilla
- **manifest.json** - Configuración PWA
- **service-worker.js** - Caché y funcionalidad offline

### 🔹 Tests (`/tests`)

Tests de integración y end-to-end:

- Tests de flujos completos
- Tests de API
- Tests de estrés
- Tests de funcionalidades específicas

### 🔹 Docs (`/docs`)

Documentación completa del proyecto:

- Documentación de API
- Guías de uso
- Arquitectura del sistema
- Ejemplos de código

### 🔹 Config (`/config`)

Archivos de configuración globales del proyecto

### 🔹 Instance (`/instance`)

Datos específicos de la instancia (base de datos, archivos subidos)
**⚠️ Esta carpeta NO debe subirse a Git**

## 📝 Archivos Importantes

### En la raíz del proyecto:

- **README.md** - Punto de entrada, overview del proyecto
- **LICENSE** - Licencia del software (MIT)
- **CHANGELOG.md** - Registro de cambios por versión
- **CONTRIBUTING.md** - Guía para contribuidores
- **DEVELOPMENT.md** - Setup de entorno de desarrollo
- **DEPLOYMENT.md** - Guía de despliegue a producción
- **.gitignore** - Archivos/carpetas ignorados por Git

### En `/backend`:

- **app.py** - Aplicación Flask principal, factory pattern
- **config.py** - Configuraciones por entorno (dev, test, prod)
- **requirements.txt** - Dependencias de producción
- **requirements-test.txt** - Dependencias de desarrollo/testing
- **pytest.ini** - Configuración de pytest
- **.env.example** - Template de variables de entorno

## 🎯 Convenciones

### Nomenclatura de Archivos

- **Python**: `snake_case.py`
- **JavaScript**: `camelCase.js` o `kebab-case.js`
- **CSS**: `kebab-case.css`
- **HTML**: `kebab-case.html`
- **Docs**: `SCREAMING_SNAKE_CASE.md` o `Title-Case.md`

### Organización de Código

#### Backend (Python)
```python
# Orden de imports
# 1. Standard library
# 2. Third-party
# 3. Local application

from datetime import datetime
from flask import Flask, jsonify
from models import User
```

#### Frontend (JavaScript)
```javascript
// Estructura de módulos
const API = {
  // Configuración
  baseURL: 'http://localhost:5000',
  
  // Métodos públicos
  async getData() { /* ... */ }
}
```

### Tests

- **Unitarios**: `test_*.py` en `backend/tests/`
- **Integración**: `test_*.py` en `tests/`
- **E2E**: Scripts específicos en `tests/`

## 🔒 Archivos Sensibles (No subir a Git)

Asegurados por `.gitignore`:

```
.env                    # Variables de entorno
*.db                    # Bases de datos
*.sqlite               # Bases de datos SQLite
*.log                  # Logs
*.pid                  # Process IDs
__pycache__/           # Cache de Python
.venv/                 # Entorno virtual
instance/              # Datos de instancia
htmlcov/               # Reportes de cobertura
.pytest_cache/         # Cache de pytest
node_modules/          # Dependencias Node (si las hay)
```

## 📊 Flujo de Datos

```
Cliente (Browser)
    ↓
Frontend (HTML/CSS/JS)
    ↓
API REST (Flask Routes)
    ↓
Services (Business Logic)
    ↓
Models (SQLAlchemy)
    ↓
Database (SQLite/PostgreSQL)
```

## 🚀 Comandos Rápidos

```bash
# Iniciar desarrollo
python backend/app.py

# Ejecutar tests
pytest backend/tests/
python tests/run_complete_tests.py

# Aplicar migraciones
cd backend && flask db upgrade

# Crear migración
cd backend && flask db migrate -m "Descripción"

# Linting
black backend/
flake8 backend/
```

## 📚 Recursos de Documentación

- **Para desarrolladores**: Ver `DEVELOPMENT.md`
- **Para despliegue**: Ver `DEPLOYMENT.md`
- **Para contribuir**: Ver `CONTRIBUTING.md`
- **API Reference**: Ver `docs/API.md`
- **Arquitectura**: Ver `docs/BACKEND_STRUCTURE.md`

## ✅ Checklist de Organización

- [x] Estructura de carpetas clara y lógica
- [x] Archivos en ubicaciones apropiadas
- [x] .gitignore configurado correctamente
- [x] Documentación completa y actualizada
- [x] README.md informativo en raíz
- [x] LICENSE definida
- [x] Tests organizados por tipo
- [x] Scripts de utilidad en carpetas apropiadas
- [x] Configuraciones separadas por entorno
- [x] Variables de entorno documentadas

---

**Última actualización**: 12 de enero de 2026

**Mantenedores**: FinanceFlow Team
