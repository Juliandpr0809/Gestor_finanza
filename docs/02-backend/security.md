# 🔒 Seguridad del Backend

Documentación de todas las medidas de seguridad implementadas.

## 🛡️ Capas de Seguridad

### 1. CORS Restrictivo

**Antes:**
```python
CORS(app, origins="*")  # ❌ PELIGROSO
```

**Ahora:**
```python
# config.py
CORS_ORIGINS = os.environ.get('ALLOWED_ORIGINS',
    'http://localhost:3000,...').split(',')

# app.py
CORS(app, origins=app.config['CORS_ORIGINS'])
```

**Configuración:**
```bash
# .env
ALLOWED_ORIGINS=http://localhost:3000,https://tudominio.com
```

---

### 2. Rate Limiting

Protección contra ataques de fuerza bruta y DoS.

**Global:**
```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]  # 200 en dev, 60 en prod
)
```

**Específico por endpoint:**
```python
@auth_bp.route('/login')
@limiter.limit("5 per minute")  # Solo 5 intentos
def login():
    ...
```

**Respuesta cuando se excede:**
```http
429 Too Many Requests
{
  "error": "Rate limit exceeded"
}
```

---

### 3. Validación de Datos

Todos los inputs son validados con **Marshmallow schemas**.

**Ejemplo - Registro de Usuario:**
```python
from schemas import UserRegisterSchema
from utils.validators import validate_and_sanitize

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        schema = UserRegisterSchema()
        validated_data = validate_and_sanitize(schema, request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
    
    # validated_data ya está limpio y validado
```

**Schemas disponibles:**
- `UserRegisterSchema`: Username, email, password
- `UserLoginSchema`: Identifier, password
- `AccountSchema`: Nombre, tipo, moneda
- `TransactionSchema`: Cuenta, categoría, monto, tipo
- `CategorySchema`: Nombre, tipo, color hex

Ver [schemas/__init__.py](file:///c:/Users/USER/Desktop/Gestor_finansas/backend/schemas/__init__.py)

---

### 4. Sanitización de Inputs

Prevención de ataques XSS (Cross-Site Scripting).

```python
from utils.validators import sanitize_html, sanitize_input

# Remover HTML peligroso
clean = sanitize_html('<script>alert("XSS")</script>Hello')
# Resultado: 'Hello'

# Sanitizar diccionarios completos
data = {
    'name': '<b>John</b>',
    'bio': '<script>evil</script>Safe text'
}
clean_data = sanitize_input(data)
# Resultado: {'name': 'John', 'bio': 'Safe text'}
```

**Función combinada:**
```python
# Valida Y sanitiza en un paso
validated_data = validate_and_sanitize(schema, raw_data)
```

---

### 5. Headers de Seguridad

Todos los responses incluyen headers protectores.

```python
@app.after_request
def security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
```

| Header | Protección |
|--------|------------|
| `X-Frame-Options: DENY` | Clickjacking |
| `X-Content-Type-Options: nosniff` | MIME sniffing |
| `X-XSS-Protection: 1; mode=block` | XSS (legacy) |
| `Content-Security-Policy` | Inyección de scripts |
| `Referrer-Policy` | Info leakage |

---

### 6. Secret Key Seguro

```python
# config.py
import secrets

SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
```

**Generar secret key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiar en `.env`:
```bash
SECRET_KEY=tu-key-generado-aqui
```

---

### 7. Cookies Seguras

```python
# config.py
class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True      # Solo HTTPS
    SESSION_COOKIE_HTTPONLY = True    # No accesible desde JS
    SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection
```

---

### 8. Protección de Contraseñas

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Al registrar
user.password_hash = generate_password_hash(password)

# Al hacer login
if check_password_hash(user.password_hash, password):
    # OK
```

**Características:**
- ✅ Hashing con bcrypt
- ✅ Salt automático único por password
- ✅ Nunca se almacena texto plano
- ✅ Nunca se retorna en API

---

### 9. Validación de Archivos

```python
from utils.validators import validate_file_extension, sanitize_filename

# Solo permitir imágenes
if not validate_file_extension(filename, ['jpg', 'png', 'gif']):
    return error('Tipo de archivo no permitido')

# Limpiar nombre de archivo
safe_name = sanitize_filename('../../../etc/passwd')
# Resultado: 'etcpasswd'
```

---

### 10. Prevención de Open Redirect

```python
from utils.validators import is_safe_redirect_url

redirect_url = request.args.get('next')
if not is_safe_redirect_url(redirect_url):
    redirect_url = '/dashboard'

return redirect(redirect_url)
```

**Bloqueados:**
- `javascript:alert(1)`
- `data:text/html,<script>...`
- URLs externas

**Permitidos:**
- `/dashboard`
- `/accounts/123`

---

## 🧪 Tests de Seguridad

Suite completa en `tests/test_security.py`:

```python
def test_sanitize_html_removes_tags():
    dirty = '<script>alert("XSS")</script>Hello'
    clean = sanitize_html(dirty)
    assert '<script>' not in clean

def test_security_headers_present(client):
    response = client.get('/api/health')
    assert 'X-Frame-Options' in response.headers
    assert response.headers['X-Frame-Options'] == 'DENY'
```

**Ejecutar:**
```bash
pytest tests/test_security.py -v
```

---

## ⚙️ Configuración por Entorno

### Desarrollo
```python
RATELIMIT_DEFAULT = "200 per minute"  # Más permisivo
SESSION_COOKIE_SECURE = False         # HTTP OK
CORS_ORIGINS = ['http://localhost:3000', ...]
```

### Producción
```python
RATELIMIT_DEFAULT = "60 per minute"   # Más estricto
SESSION_COOKIE_SECURE = True          # Solo HTTPS
CORS_ORIGINS = ['https://tudominio.com']
```

---

## 📊 Checklist de Seguridad

- [x] CORS restrictivo (no `*`)
- [x] Rate limiting global y por endpoint
- [x] Validación con schemas Marshmallow
- [x] Sanitización de todos los inputs
- [x] Headers de seguridad en responses
- [x] Secret key seguro (32+ bytes)
- [x] Passwords hasheados con bcrypt
- [x] Cookies seguras (httpOnly, secure, sameSite)
- [x] Validación de tipos de archivo
- [x] Prevención de open redirect
- [ ] Refresh tokens (pendiente)
- [ ] 2FA - Two Factor Auth (futuro)
- [ ] Rate limiting por usuario (futuro)
- [ ] CSRF tokens (futuro)

---

## 🚨 Reporte de Vulnerabilidades

Si encuentras una vulnerabilidad, repórtala de forma responsable:

1. No la publiques públicamente
2. Envía email a: [security@tudominio.com]
3. Incluye pasos para reproducir
4. Espera confirmación antes de divulgar

---

## 📚 Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
