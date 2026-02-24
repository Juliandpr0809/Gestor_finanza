# 💰 FinanceFlow - Gestor de Finanzas Personales

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Sistema de gestión de finanzas personales con inteligencia artificial integrada para categorización automática y análisis financiero.

## ✨ Características

- 🔐 **Autenticación segura** con JWT
- 💳 **Gestión de cuentas** bancarias múltiples
- 📊 **Transacciones** con categorización automática
- 🤖 **Asistente IA** para análisis financiero
- 📱 **PWA** - Progressive Web App
- 🌍 **Multi-moneda** con conversión automática
- 📈 **Reportes** y análisis detallados

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.9+
- pip
- Navegador web moderno

### Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd Gestor_finansas
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r backend/requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp backend/.env.example backend/.env
# Editar .env con tus configuraciones
```

5. **Inicializar base de datos**
```bash
cd backend
flask db upgrade
flask init-db
```

6. **Ejecutar aplicación**
```bash
python backend/app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 📁 Estructura del Proyecto

```
Gestor_finansas/
├── backend/              # Backend Flask
│   ├── app.py           # Aplicación principal
│   ├── config.py        # Configuraciones
│   ├── models/          # Modelos de base de datos
│   ├── routes/          # Rutas/Endpoints
│   ├── services/        # Lógica de negocio
│   ├── schemas/         # Validaciones
│   ├── utils/           # Utilidades
│   ├── scripts/         # Scripts de administración
│   └── tests/           # Tests del backend
├── frontend/            # Frontend (HTML/CSS/JS)
│   ├── html/
│   ├── css/
│   └── js/
├── tests/               # Tests de integración
├── docs/                # Documentación
└── config/              # Configuraciones adicionales
```

## 📚 Documentación

- [Guía de inicio](docs/01-getting-started/README.md)
- [Documentación Backend](docs/02-backend/README.md)
- [Documentación Frontend](docs/03-frontend/README.md)
- [API Reference](docs/API.md)
- [Configuración](docs/SETUP.md)

## 🧪 Testing

```bash
# Tests del backend
cd backend
pytest

# Tests de integración
python tests/test_all_endpoints.py

# Tests con cobertura
pytest --cov=. --cov-report=html
```

## � PWA - Instalar como App Nativa

FinanceFlow es una **Progressive Web App (PWA)** - funcionará como una app nativa en tu teléfono sin necesidad de APK:

### Instalación Rápida

1. **Abre en tu teléfono**: `https://tu-dominio.com`
2. **Espera 3-5 segundos** a que aparezca el banner
3. **Toca "Instalar"** (Android) o **Compartir → Agregar a pantalla de inicio** (iPhone)
4. ¡La app estará en tu pantalla de inicio!

### Requisitos
- Dominio con **HTTPS** (obligatorio)
- Chrome, Edge o Safari
- Internet para primera instalación

### Características de PWA
- ✅ Funciona como app nativa
- ✅ Funcionamiento offline parcial
- ✅ Sin necesidad de Play Store
- ✅ Actualizaciones automáticas
- ✅ Acceso a notificaciones

### Documentación Detallada
- [Guía Rápida PWA](docs/QUICK_START_PWA.md)
- [Instalación Completa](docs/PWA_INSTALACION.md)
- [Despliegue con HTTPS](docs/HTTPS_DEPLOYMENT.md)

### Testing Local

Para probar la PWA localmente antes de desplegar:

```bash
# Usar ngrok para crear URL HTTPS temporal
ngrok http 5000
# Accede en teléfono a: https://abc123.ngrok.io
```

## �🛠️ Tecnologías

### Backend
- **Flask** - Framework web
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Autenticación
- **Groq API** - Inteligencia Artificial
- **Alembic** - Migraciones de BD

### Frontend
- **HTML5/CSS3/JavaScript**
- **PWA** - Service Workers
- **LocalStorage** - Almacenamiento local

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: amazing feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**FinanceFlow Team**

## 🙏 Agradecimientos

- Groq AI por su API de inteligencia artificial
- Comunidad de Flask
- Todos los contribuidores

---

**¿Necesitas ayuda?** Abre un [issue](../../issues) en GitHub
