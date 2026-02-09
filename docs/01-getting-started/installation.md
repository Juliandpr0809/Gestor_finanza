# ⚙️ Instalación Completa

Guía detallada de instalación para desarrollo y producción.

## 📋 Requisitos

### Backend
- Python 3.8 o superior
- pip (gestor de paquetes Python)
- SQLite 3 (incluido con Python)
- PostgreSQL (opcional, para producción)

### Frontend
- Navegador moderno (Chrome, Firefox, Safari, Edge)
- Servidor HTTP para desarrollo (Live Server, http-server, etc.)

---

## 🔧 Instalación de Desarrollo

### 1. Preparar el Entorno

```bash
# Clonar repositorio
git clone [tu-repo]
cd Gestor_finansas

# Verificar versiones
python --version  # Debe ser 3.8+
pip --version
```

### 2. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias de producción
pip install -r requirements.txt

# Instalar dependencias de desarrollo (testing)
pip install -r requirements-test.txt
```

### 3. Configuración de Variables de Entorno

```bash
# Copiar ejemplo
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Editar .env
notepad .env  # Windows
# nano .env   # Linux
```

Configurar al menos:
```bash
SECRET_KEY=<genera-con-python-c-import-secrets-print-secrets-token-urlsafe-32>
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 4. Base de Datos

```bash
# Inicializar migraciones (solo primera vez)
flask db init

# Aplicar migraciones
flask db upgrade

# Cargar datos de prueba
flask seed
```

### 5. Frontend

```bash
cd ../frontend

# Opción 1: VS Code Live Server
# Instalar extensión "Live Server"
# Click derecho en html/index.html > "Open with Live Server"

# Opción 2: Servidor Python
python -m http.server 3000

# Opción 3: Node http-server
npm install -g http-server
http-server -p 3000
```

---

## 🚀 Instalación de Producción

### 1. Backend con Gunicorn

```bash
cd backend

# Instalar Gunicorn
pip install gunicorn

# Crear archivo wsgi.py
cat > wsgi.py << EOF
from app import create_app

app = create_app('production')

if __name__ == '__main__':
    app.run()
EOF

# Ejecutar con Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
```

### 2. Base de Datos PostgreSQL

```bash
# Instalar PostgreSQL
# En .env:
DATABASE_URL=postgresql://user:password@localhost:5432/financeflow

# Aplicar migraciones
flask db upgrade
```

### 3. Nginx como Reverse Proxy

```nginx
# /etc/nginx/sites-available/financeflow
server {
    listen 80;
    server_name tudominio.com;

    # Frontend
    location / {
        root /ruta/a/Gestor_finansas/frontend;
        try_files $uri $uri/ /html/index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🐳 Instalación con Docker (Próximamente)

```bash
# Construir y levantar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

---

## ✅ Verificación

### Backend

```bash
# Salud del API
curl http://localhost:5000/api/health

# Info del API
curl http://localhost:5000/api
```

Deberías ver:
```json
{
  "status": "ok",
  "message": "FinanceFlow API running"
}
```

### Frontend

Abre http://localhost:3000/html/login.html

Deberías ver la página de login.

---

## 🔥 Desinstalar

```bash
# Desactivar entorno virtual
deactivate

# Eliminar entorno virtual
rm -rf .venv  # Linux/Mac
# rmdir /s .venv  # Windows

# Eliminar base de datos
rm instance/financeflow.db
```
