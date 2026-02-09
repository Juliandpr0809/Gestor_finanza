# FinanceFlow Backend

Backend API para la aplicación de gestión financiera personal con IA integrada.

## Instalación

### 1. Crear y activar entorno virtual

```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env si es necesario
```

### 4. Ejecutar la aplicación

```bash
python app.py
```

La API estará disponible en `http://localhost:5000`

## Estructura del Proyecto

```
backend/
├── app.py                 # Aplicación principal
├── config.py             # Configuración de Flask
├── requirements.txt      # Dependencias
├── models/
│   └── __init__.py      # Modelos de base de datos
├── routes/
│   ├── auth.py          # Autenticación
│   ├── accounts.py      # Gestión de cuentas
│   ├── transactions.py  # Gestión de transacciones
│   ├── categories.py    # Gestión de categorías
│   └── chat.py          # Chat con IA
├── services/            # Lógica de negocio (IA, etc)
└── utils/               # Utilidades
```

## Endpoints de la API

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/me` - Obtener usuario actual

### Cuentas
- `GET /api/accounts` - Obtener todas las cuentas
- `GET /api/accounts/<id>` - Obtener detalle de cuenta
- `POST /api/accounts` - Crear cuenta
- `PUT /api/accounts/<id>` - Actualizar cuenta
- `DELETE /api/accounts/<id>` - Eliminar cuenta
- `GET /api/accounts/stats` - Obtener estadísticas

### Transacciones
- `GET /api/transactions` - Obtener transacciones
- `GET /api/transactions/<id>` - Obtener transacción
- `POST /api/transactions` - Crear transacción
- `PUT /api/transactions/<id>` - Actualizar transacción
- `DELETE /api/transactions/<id>` - Eliminar transacción
- `GET /api/transactions/stats/monthly` - Estadísticas mensuales

### Categorías
- `GET /api/categories` - Obtener categorías
- `GET /api/categories/<id>` - Obtener categoría
- `POST /api/categories` - Crear categoría
- `PUT /api/categories/<id>` - Actualizar categoría
- `DELETE /api/categories/<id>` - Eliminar categoría

### Chat
- `GET /api/chat/messages` - Obtener historial
- `POST /api/chat/send` - Enviar mensaje
- `POST /api/chat/clear` - Limpiar historial

## Base de Datos

SQLite con SQLAlchemy. Se crea automáticamente al iniciar la aplicación.

### Tablas
- `users` - Usuarios
- `accounts` - Cuentas
- `categories` - Categorías
- `transactions` - Transacciones
- `chat_messages` - Mensajes de chat

## Desarrollo

Para desarrollo, asegúrate de tener:
- Python 3.8+
- pip
- virtualenv

Cambios automáticos con `flask run` en modo debug.
