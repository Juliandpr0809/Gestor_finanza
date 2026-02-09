# Estructura Organizada del Proyecto

## 📁 Nueva Estructura

```
Gestor_finansas/
│
├── 📂 backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── routes/
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── migrations/
│
├── 📂 frontend/
│   ├── html/
│   ├── js/
│   ├── css/
│   └── img/ (si existe)
│
├── 📂 docs/
│   ├── DEPENDENCIAS.md
│   ├── ESTRUCTURA.md (este archivo)
│   ├── API.md
│   └── SETUP.md
│
├── 📂 config/
│   ├── .env.example
│   └── variables.env
│
├── 📂 .venv/          (entorno virtual)
├── 📂 .vscode/        (configuración del editor)
├── 📂 instance/       (base de datos)
│
└── 📄 README.md       (información principal)
```

## 🗂️ Descripción por Carpeta

### `backend/`
- **app.py**: Aplicación principal Flask
- **config.py**: Configuración (BD, JWT, etc)
- **routes/**: Endpoints (auth, chat, transactions, accounts, categories)
- **models/**: Modelos SQLAlchemy
- **services/**: Lógica de negocios (AI con Groq, etc)
- **utils/**: Funciones auxiliares (JWT, etc)
- **requirements.txt**: Dependencias Python

### `frontend/`
- **html/**: Páginas (login, register, index, chat, transactions, etc)
- **js/**: Scripts (auth.js, api.js, dashboard.js, etc)
- **css/**: Estilos (auth.css, minimalist-clean.css, etc)

### `docs/`
- Documentación técnica
- Guías de configuración
- Documentación de API

### `config/`
- Archivos de configuración
- Variables de entorno

## 📋 Archivos Organizados

| Archivo | Ubicación Original | Ubicación Nueva | Tipo |
|---------|-------------------|-----------------|------|
| lista.txt | Raíz | docs/ (opcional) | Referencia |
| README.md | Raíz | Raíz | Documentación |
| .env | Backend | config/.env | Config |

