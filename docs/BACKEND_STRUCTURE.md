# Backend - Estructura Organizada

## 📁 Estructura

```
backend/
│
├── 📄 app.py                 # Aplicación principal Flask
├── 📄 config.py              # Configuración de la app
├── 📄 requirements.txt        # Dependencias Python
├── 📄 README.md              # Documentación del backend
│
├── 📂 config_files/          # Archivos de configuración
│   ├── .env                  # Variables de entorno (local)
│   ├── .env.example          # Plantilla .env
│   └── .gitignore            # Archivos ignorados por Git
│
├── 📂 routes/                # Endpoints de la API
│   ├── __init__.py
│   ├── auth.py               # Login, Register
│   ├── chat.py               # IA Chat
│   ├── transactions.py       # Gestión de transacciones
│   ├── accounts.py           # Gestión de cuentas
│   └── categories.py         # Categorías de gastos
│
├── 📂 models/                # Modelos SQLAlchemy
│   └── __init__.py
│
├── 📂 services/              # Lógica de negocios
│   ├── __init__.py
│   └── ai_service.py         # Integración Groq API
│
├── 📂 utils/                 # Funciones auxiliares
│   ├── __init__.py
│   └── jwt_utils.py          # Utilidades JWT
│
├── 📂 scripts/               # Scripts de testing/debugging
│   ├── check_user.py         # Verificar usuarios
│   ├── verify_token.py       # Verificar tokens JWT
│   ├── debug_accounts.py     # Debug de cuentas
│   ├── list_users.py         # Listar usuarios
│   ├── fix_balances.py       # Reparar balances
│   └── test_login.py         # Testing de login
│
├── 📂 migrations/            # Migraciones de BD (Alembic)
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── 📂 instance/              # Archivos generados (BD SQLite)
│   └── app.db
│
└── 📂 __pycache__/           # Cache Python (ignorado)
```

## 🚀 Cómo Usar

### Ejecutar la aplicación
```bash
cd backend
python app.py
```

### Usar scripts de testing
```bash
python scripts/verify_token.py
python scripts/debug_accounts.py
python scripts/list_users.py
```

### Configuración
- Edita `.env` desde `config_files/.env`
- Usa `.env.example` como referencia

## 📋 Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| app.py | Punto de entrada de Flask |
| config.py | Variables de configuración |
| routes/ | Todos los endpoints API |
| models/ | Definición de tablas BD |
| services/ | Lógica de IA y servicios |
| scripts/ | Herramientas de debug/testing |

