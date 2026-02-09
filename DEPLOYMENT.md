# Guía de Despliegue - FinanceFlow

Esta guía cubre el despliegue de FinanceFlow en diferentes plataformas.

## 📋 Pre-requisitos

- Cuenta en la plataforma de hosting elegida
- Base de datos configurada (PostgreSQL recomendado para producción)
- API Key de Groq (para funcionalidades de IA)
- Dominio (opcional)

## 🚀 Despliegue Rápido

### Render.com (Recomendado)

1. **Crear cuenta en Render.com**

2. **Crear Web Service**
   - New > Web Service
   - Conecta tu repositorio de GitHub
   - Configuración:
     - Name: `financeflow`
     - Environment: `Python 3`
     - Build Command: `pip install -r backend/requirements.txt`
     - Start Command: `cd backend && gunicorn app:app`

3. **Variables de Entorno**
   ```
   FLASK_ENV=production
   SECRET_KEY=<genera-clave-segura>
   JWT_SECRET_KEY=<genera-clave-segura>
   GROQ_API_KEY=<tu-api-key>
   DATABASE_URL=<url-postgresql>
   ```

4. **Crear Base de Datos PostgreSQL**
   - New > PostgreSQL
   - Conecta con tu Web Service
   - Añade `DATABASE_URL` a las variables de entorno

5. **Deploy**
   - Render detectará cambios automáticamente
   - Ejecuta migraciones después del primer deploy

### Heroku

1. **Instalar Heroku CLI**
```bash
# Windows
choco install heroku-cli
# Mac
brew tap heroku/brew && brew install heroku
```

2. **Login y crear app**
```bash
heroku login
heroku create financeflow-app
```

3. **Añadir PostgreSQL**
```bash
heroku addons:create heroku-postgresql:mini
```

4. **Configurar variables**
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=<clave-segura>
heroku config:set JWT_SECRET_KEY=<clave-segura>
heroku config:set GROQ_API_KEY=<tu-api-key>
```

5. **Crear Procfile**
```
web: cd backend && gunicorn app:app
```

6. **Deploy**
```bash
git push heroku main
heroku run "cd backend && flask db upgrade"
heroku run "cd backend && flask init-db"
```

### Railway

1. **Crear proyecto en Railway**

2. **Conectar repositorio de GitHub**

3. **Añadir PostgreSQL**
   - New > Database > PostgreSQL

4. **Variables de entorno**
   - Settings > Variables
   - Añade todas las variables necesarias

5. **Deploy automático**
   - Railway detecta Flask automáticamente

### DigitalOcean App Platform

1. **Crear app en DigitalOcean**

2. **Configurar componentes**
   - Web Service (Python)
   - Database (PostgreSQL)

3. **Variables de entorno**
   ```
   FLASK_ENV=production
   SECRET_KEY=<clave-segura>
   JWT_SECRET_KEY=<clave-segura>
   GROQ_API_KEY=<tu-api-key>
   DATABASE_URL=${db.DATABASE_URL}
   ```

4. **Build y Run**
   - Build: `pip install -r backend/requirements.txt`
   - Run: `cd backend && gunicorn app:app`

## 🐳 Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY frontend/ ../frontend/

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/financeflow
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=financeflow
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Comandos Docker

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Logs
docker-compose logs -f

# Ejecutar migraciones
docker-compose exec web flask db upgrade

# Stop
docker-compose down
```

## 🔒 Seguridad en Producción

### 1. Generar Claves Secretas

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Variables de Entorno Críticas

```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<clave-64-caracteres-minimo>
JWT_SECRET_KEY=<clave-64-caracteres-minimo>
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
CORS_ORIGINS=https://tu-dominio.com
```

### 3. Configurar HTTPS

- Usa certificados SSL (Let's Encrypt)
- Fuerza HTTPS en todas las rutas
- Configura HSTS headers

### 4. Base de Datos

- Usa PostgreSQL en producción
- Backups automáticos
- Conexiones SSL
- Usuarios con permisos limitados

### 5. Rate Limiting

```python
# En config.py
RATELIMIT_STORAGE_URL = 'redis://localhost:6379'
```

## 📊 Monitoreo

### Logs

```python
# Configurar logging en producción
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

### Health Check Endpoint

```python
@app.route('/health')
def health():
    return {'status': 'healthy', 'version': '1.0.0'}, 200
```

### Monitoring Services

- **Sentry** - Error tracking
- **New Relic** - Performance monitoring
- **Datadog** - Infrastructure monitoring
- **Uptime Robot** - Uptime monitoring

## 🔄 CI/CD con GitHub Actions

`.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements-test.txt
      - name: Run tests
        run: |
          cd backend && pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

## 📝 Checklist Pre-Despliegue

- [ ] Tests pasando al 100%
- [ ] Variables de entorno configuradas
- [ ] Claves secretas generadas
- [ ] Base de datos de producción creada
- [ ] Migraciones ejecutadas
- [ ] HTTPS configurado
- [ ] CORS configurado correctamente
- [ ] Rate limiting activo
- [ ] Logs configurados
- [ ] Backups automáticos configurados
- [ ] Monitoring configurado
- [ ] Dominio apuntando al servidor
- [ ] Documentación actualizada

## 🆘 Troubleshooting

### Error: "Application failed to start"
- Verifica que todas las variables de entorno estén configuradas
- Revisa los logs de la plataforma
- Asegúrate de que `gunicorn` esté en requirements.txt

### Error: "Database connection failed"
- Verifica DATABASE_URL
- Confirma que la base de datos esté accesible
- Revisa configuración de SSL si es requerido

### Error: "Static files not loading"
- Configura correctamente STATIC_FOLDER
- Usa CDN para assets (opcional)
- Verifica CORS headers

## 📚 Recursos

- [Flask Deployment Options](https://flask.palletsprojects.com/en/latest/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [PostgreSQL Best Practices](https://www.postgresql.org/docs/current/index.html)
- [Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)

## 💡 Optimizaciones

### Caching con Redis

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL')
})
```

### CDN para Assets

- Cloudflare
- AWS CloudFront
- Azure CDN

### Database Connection Pooling

```python
from sqlalchemy.pool import QueuePool

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': QueuePool,
    'pool_size': 10,
    'max_overflow': 20
}
```

---

**¿Necesitas ayuda?** Abre un issue en GitHub o consulta la documentación.
