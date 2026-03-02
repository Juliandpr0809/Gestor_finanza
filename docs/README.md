# 📚 Documentación del Proyecto - OrdenC/FinanceFlow

Bienvenido a la documentación del proyecto. Aquí encontrarás toda la información organizada por categorías.

## 📁 Estructura de Documentación

```
docs/
├── 01-getting-started/         # Primeros pasos
│   ├── README.md              # Inicio rápido
│   └── installation.md        # Instalación completa
│
├── 02-backend/                 # Documentación del backend
│   ├── api-endpoints.md       # Referencia de API
│   ├── authentication.md      # Sistema de autenticación
│   ├── database-models.md     # Modelos de base de datos
│   ├── security.md           # Seguridad implementada
│   └── testing.md            # Guía de tests
│
├── 03-frontend/                # Documentación del frontend
│   ├── components.md          # Componentes UI
│   ├── internationalization.md # Sistema i18n
│   ├── pwa.md                # Progressive Web App
│   └── theming.md            # Sistema de temas
│
├── 04-deployment/              # Despliegue
│   ├── production.md          # Configuración de producción
│   └── environment.md         # Variables de entorno
│
└── 05-development/             # Desarrollo
    ├── contributing.md        # Guía de contribución
    └── architecture.md        # Arquitectura del sistema
```

## 🚀 Enlaces Rápidos

### Para Empezar
- [📖 Guía de Inicio Rápido](./01-getting-started/README.md)
- [⚙️ Instalación Completa](./01-getting-started/installation.md)

### Backend
- [🔌 API Endpoints](./02-backend/api-endpoints.md)
- [🔐 Autenticación](./02-backend/authentication.md)
- [🗄️ Modelos de BD](./02-backend/database-models.md)
- [🔒 Seguridad](./02-backend/security.md)
- [🧪 Testing](./02-backend/testing.md)

### Frontend
- [🎨 Componentes UI](./03-frontend/components.md)
- [🌍 Internacionalización](./03-frontend/internationalization.md)
- [📱 PWA](./03-frontend/pwa.md)
- [🎭 Temas](./03-frontend/theming.md)

### Despliegue
- [🚀 Producción](./04-deployment/production.md)
- [🔧 Variables de Entorno](./04-deployment/environment.md)

### Desarrollo
- [🤝 Contribuir](./05-development/contributing.md)
- [🏗️ Arquitectura](./05-development/architecture.md)

---

## 🎙️ Documentación de Chat de Voz

### Nueva Funcionalidad: Chat de Voz Bidireccional

| Documento | Descripción | Audiencia | Tiempo Lectura |
|-----------|-------------|-----------|----------------|
| [📋 Resumen Ejecutivo](VOICE_CHAT_EXECUTIVE_SUMMARY.md) | Decisión de negocio, costos, ROI, timeline | Gerencia, Product Managers | 5 min |
| [📖 Especificación Técnica Completa](VOICE_CHAT_REDESIGN_SPEC.md) | Arquitectura detallada, stack, implementación | Desarrolladores, Arquitectos | 30 min |
| [🚀 Guía de Inicio Rápido](VOICE_CHAT_QUICK_START.md) | Implementación en 30 minutos, código listo | Desarrolladores | 10 min |

**Estado**: Propuesta técnica completa ✅  
**Próximo paso**: Revisión y aprobación para implementación

#### Resumen Rápido

El rediseño del chat de voz propone:
- ✅ **Voz bidireccional** (usuario habla → sistema responde en voz)
- ✅ **100% funcionalidades accesibles** por comandos de voz naturales
- ✅ **Costo mínimo**: $0-10/mes (soluciones gratuitas/open source)
- ✅ **Stack**: Whisper (STT) + Groq Llama 3.3 (NLU) + gTTS/pyttsx3 (TTS)
- ✅ **Timeline**: 4-8 semanas hasta producción

**Leer primero**: [Resumen Ejecutivo](VOICE_CHAT_EXECUTIVE_SUMMARY.md) (5 min)

---

## 📊 Stack Tecnológico

### Backend
- **Framework**: Flask 3.0.0
- **ORM**: SQLAlchemy 2.0+
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Autenticación**: JWT
- **Testing**: pytest

### Frontend
- **HTML5** + **CSS3** + **JavaScript ES6+**
- **PWA**: Service Workers + Manifest
- **i18n**: Sistema multiidioma (ES/EN)
- **Iconos**: Font Awesome 6.5

---

## 🆘 Soporte

¿Problemas? Revisa la documentación específica de cada sección.
