# FinanceFlow Development Setup

Este documento explica cómo configurar el entorno de desarrollo.

## Requisitos Previos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Git
- Navegador web moderno

## Instalación Paso a Paso

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd Gestor_finansas
```

### 2. Crear Entorno Virtual

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r backend/requirements.txt
```

Para desarrollo (incluye herramientas de testing):
```bash
pip install -r backend/requirements-test.txt
```

### 4. Configurar Variables de Entorno

```bash
cp backend/.env.example backend/.env
```

Edita `backend/.env` con tus configuraciones:
- Genera claves secretas seguras para `SECRET_KEY` y `JWT_SECRET_KEY`
- Añade tu `GROQ_API_KEY` si vas a usar funcionalidades de IA

### 5. Inicializar Base de Datos

```bash
cd backend
flask db upgrade
flask init-db
```

El comando `init-db` creará:
- Usuario administrador por defecto
- Categorías predeterminadas
- Datos de ejemplo (opcional)

### 6. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## Comandos Útiles

### Base de Datos

```bash
# Crear nueva migración
flask db migrate -m "Descripción del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir última migración
flask db downgrade

# Ver historial de migraciones
flask db history

# Reiniciar base de datos
flask reset-db
```

### Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=. --cov-report=html

# Tests específicos
pytest tests/test_auth.py

# Tests con output verbose
pytest -v

# Tests con pdb en fallos
pytest --pdb
```

### Linting y Formateo

```bash
# Formatear código con black
black .

# Verificar con flake8
flake8 .

# Ordenar imports
isort .
```

## Estructura de Desarrollo

```
backend/
├── app.py              # Punto de entrada
├── config.py           # Configuraciones
├── models/             # Modelos SQLAlchemy
├── routes/             # Endpoints API
├── services/           # Lógica de negocio
├── schemas/            # Validación Marshmallow
├── utils/              # Utilidades
├── scripts/            # Scripts de administración
└── tests/              # Tests unitarios
```

## Variables de Entorno Importantes

### Desarrollo
```env
FLASK_ENV=development
DEBUG=True
TESTING=False
```

### Producción
```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<clave-segura-generada>
JWT_SECRET_KEY=<clave-segura-generada>
SESSION_COOKIE_SECURE=True
```

## Generar Claves Secretas

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

## Solución de Problemas

### Error: "No module named 'flask'"
```bash
# Asegúrate de tener el entorno virtual activado
pip install -r backend/requirements.txt
```

### Error: "Database not found"
```bash
# Inicializa la base de datos
cd backend
flask db upgrade
flask init-db
```

### Error: "GROQ_API_KEY not found"
```bash
# Añade tu API key en backend/.env
GROQ_API_KEY=tu-api-key-aqui
```

### Puerto 5000 ya en uso
```bash
# Cambia el puerto en app.py o usa variable de entorno
PORT=5001 python app.py
```

## Herramientas Recomendadas

### VS Code Extensions
- Python (Microsoft)
- Pylance
- Python Test Explorer
- GitLens
- Thunder Client (para testing API)
- Better Comments

### Configuración VS Code

Crea `.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

## Flujo de Trabajo Git

1. Crea una rama para tu feature
```bash
git checkout -b feature/mi-nueva-feature
```

2. Haz commits siguiendo las convenciones
```bash
git commit -m "Add: nueva funcionalidad X"
```

3. Push y crea Pull Request
```bash
git push origin feature/mi-nueva-feature
```

## Recursos Adicionales

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [API Documentation](docs/API.md)

## Soporte

Si encuentras problemas:
1. Revisa este documento
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema
