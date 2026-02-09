# 🚀 Inicio Rápido - OrdenC

Guía rápida para levantar el proyecto en minutos.

## ⚡ Quick Start (5 minutos)

### 1. Clonar el Repositorio

```bash
git clone [tu-repo]
cd Gestor_finansas
```

### 2. Backend (API Flask)

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
flask db upgrade

# (Opcional) Cargar datos de prueba
flask seed

# Ejecutar servidor
python app.py
```

✅ **Backend corriendo en:** http://localhost:5000

### 3. Frontend (Web App)

```bash
cd frontend

# Abrir con Live Server (VS Code)
# O usar servidor Python simple:
python -m http.server 3000
```

✅ **Frontend corriendo en:** http://localhost:3000/html/index.html

### 4. Credenciales de Prueba

Si ejecutaste `flask seed`:

- **Email**: demo@demo.com
- **Password**: demo1234

---

## 🎯 Próximos Pasos

1. 📖 [Instalación Completa](./installation.md) - Setup detallado
2. 🔌 [API Endpoints](../02-backend/api-endpoints.md) - Documentación del API
3. 🔐 [Autenticación](../02-backend/authentication.md) - Sistema de auth

---

## ⚠️ Troubleshooting

### El backend no arranca

```bash
# Verificar que el entorno virtual esté activado
which python  # Debe mostrar .venv/bin/python

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### CORS Error en el frontend

Verifica que en `backend/.env`:
```
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Base de datos no existe

```bash
cd backend
flask db upgrade  # Crea las tablas
flask seed       # Datos de prueba
```
