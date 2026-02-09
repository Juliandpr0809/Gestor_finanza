# Setup y Configuración

## 🔧 Variables de Entorno

### Backend (.env)

```env
# Base de datos
DATABASE_URL=mysql+pymysql://user:password@localhost/gestor_finansas

# JWT
JWT_SECRET_KEY=tu_clave_secreta_aqui
JWT_ACCESS_TOKEN_EXPIRES=86400

# Groq API (para IA)
GROK_API_KEY=tu_clave_api_aqui

# Flask
FLASK_ENV=development
FLASK_APP=app.py
```

### Frontend

Las variables se configuran en `frontend/js/api.js`:
```javascript
const API_BASE_URL = 'http://127.0.0.1:5000/api';
```

## 🚀 Instalación Paso a Paso

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python app.py
```

### 2. Frontend
```bash
cd frontend
# Opción A: Abrir directamente
open html/index.html

# Opción B: Con servidor local
python -m http.server 8000
# Accede a: http://localhost:8000/html/index.html
```

## 🗄️ Base de Datos

```bash
# Desde backend/
flask db upgrade  # Aplicar migraciones
```

## 🧪 Testing

```bash
# Verificar autenticación
python backend/verify_token.py

# Verificar cuentas del usuario
python backend/debug_accounts.py
```

