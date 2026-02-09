# 🧪 Testing del Backend

Guía completa de testing con pytest.

## 📁 Estructura de Tests

```
backend/tests/
├── __init__.py
├── conftest.py              # Fixtures compartidos
├── test_auth.py            # Tests de autenticación (19 tests)
├── test_validation.py      # Tests de validación (13 tests)
└── test_security.py        # Tests de seguridad (15 tests)

Total: 47 tests
```

---

## ⚙️ Configuración

### Instalar Dependencias

```bash
cd backend
pip install -r requirements-test.txt
```

Incluye:
- `pytest==7.4.3`
- `pytest-cov==4.1.0` (cobertura)
- `pytest-flask==1.3.0`
- `coverage==7.3.2`

### Archivo pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = 
    -v                    # Verbose
    --cov=.              # Cobertura
    --cov-report=html    # Reporte HTML
    --tb=short           # Traceback corto
```

---

## 🚀 Ejecutar Tests

### Todos los tests

```bash
pytest
```

### Con cobertura detallada

```bash
pytest --cov=. --cov-report=html
```

Luego abre `htmlcov/index.html` en el navegador.

### Solo un archivo

```bash
pytest tests/test_auth.py
```

### Solo una clase

```bash
pytest tests/test_auth.py::TestRegister
```

### Solo un test específico

```bash
pytest tests/test_auth.py::TestRegister::test_register_success
```

### Con markers

```bash
# Solo tests de seguridad
pytest -m security

# Solo tests unitarios
pytest -m unit

# Excluir tests lentos
pytest -m "not slow"
```

### Modo verbose con traceback completo

```bash
pytest -vv --tb=long
```

### Parar en primer fallo

```bash
pytest -x
```

---

## 🎯 Fixtures Disponibles

Definidos en `conftest.py`:

### `app`
Aplicación Flask configurada para testing.

```python
def test_something(app):
    with app.app_context():
        # Tu código aquí
```

### `client`
Cliente HTTP para hacer requests.

```python
def test_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
```

### `db_session`
Base de datos limpia para cada test.

```python
def test_user_creation(db_session):
    user = User(username='test', email='test@test.com')
    db_session.session.add(user)
    db_session.session.commit()
    
    assert user.id is not None
```

### `test_user`
Usuario de prueba ya creado.

```python
def test_with_user(test_user):
    assert test_user.email == 'test@example.com'
```

### `test_user_token`
Token JWT válido del usuario de prueba.

```python
def test_protected_endpoint(client, test_user_token):
    headers = {'Authorization': f'Bearer {test_user_token}'}
    response = client.get('/api/auth/me', headers=headers)
    assert response.status_code == 200
```

### `auth_headers`
Headers completos con autenticación.

```python
def test_api_call(client, auth_headers):
    response = client.get('/api/accounts', headers=auth_headers)
    assert response.status_code == 200
```

### `test_account`, `test_category`, `test_transaction`
Datos de prueba precargados.

```python
def test_account(client, auth_headers, test_account):
    assert test_account.name == 'Test Account'
    assert test_account.current_balance == 1000.0
```

---

## 📝 Escribir Nuevos Tests

### Estructura Básica

```python
class TestMyFeature:
    """Tests para mi funcionalidad"""
    
    def test_success_case(self, client, auth_headers):
        """Test: Caso exitoso"""
        response = client.post('/api/endpoint', 
                              headers=auth_headers,
                              json={'data': 'value'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'expected_field' in data
    
    def test_error_case(self, client):
        """Test: Manejo de error"""
        response = client.post('/api/endpoint', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
```

### Tests de Validación

```python
from marshmallow import ValidationError
from schemas import MySchema

def test_valid_data():
    """Test: Datos válidos"""
    schema = MySchema()
    data = {'field': 'valid_value'}
    result = schema.load(data)
    assert result['field'] == 'valid_value'

def test_invalid_data():
    """Test: Datos inválidos son rechazados"""
    schema = MySchema()
    data = {'field': 'invalid'}
    
    with pytest.raises(ValidationError) as exc_info:
        schema.load(data)
    
    assert 'field' in exc_info.value.messages
```

---

## 📊 Ejemplos de Tests

### Test de Autenticación

```python
def test_login_success(client, test_user):
    """Test: Login exitoso con credenciales válidas"""
    response = client.post('/api/auth/login', json={
        'identifier': 'test@example.com',
        'password': 'testpassword123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['user']['email'] == 'test@example.com'
```

### Test de Seguridad

```python
def test_xss_protection(client):
    """Test: Protección contra XSS"""
    from utils.validators import sanitize_html
    
    dirty = '<script>alert("XSS")</script>Hello'
    clean = sanitize_html(dirty)
    
    assert '<script>' not in clean
    assert 'Hello' in clean
```

### Test de Rate Limiting

```python
def test_rate_limiting(client):
    """Test: Rate limiting funciona"""
    # Hacer 6 requests rápidos (límite es 5/min en login)
    for i in range(6):
        response = client.post('/api/auth/login', json={
            'identifier': 'test',
            'password': 'wrong'
        })
    
    # El 6to debe ser bloqueado
    assert response.status_code == 429
```

---

## 🎨 Markers Personalizados

Agregar en `pytest.ini`:

```ini
markers =
    slow: tests que tardan mucho
    security: tests de seguridad
    integration: tests de integración
    unit: tests unitarios
```

Usar en tests:

```python
import pytest

@pytest.mark.security
def test_xss_protection():
    ...

@pytest.mark.slow
def test_complex_calculation():
    ...
```

---

## 📈 Cobertura de Código

### Ver cobertura actual

```bash
pytest --cov=. --cov-report=term-missing
```

Output:
```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
app.py                          45      2    96%   127-128
routes/auth.py                  67      3    95%   45, 89
schemas/__init__.py             89      0   100%
utils/validators.py             42      1    98%   67
-----------------------------------------------------------
TOTAL                          243      6    98%
```

### Meta de Cobertura

Objetivo: **>80%** en todos los módulos principales.

### Generar reporte HTML

```bash
pytest --cov=. --cov-report=html
```

Abre `htmlcov/index.html` para:
- Ver líneas cubiertas/no cubiertas
- Identificar código sin testear
- Drill-down por archivo

---

## ⚠️ Troubleshooting

### ImportError: No module named X

```bash
# Asegúrate de estar en el entorno virtual
.venv\Scripts\activate

# Reinstalar dependencias
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Tests fallan con "database locked"

SQLite no soporta concurrencia. Usar fixture `db_session` que limpia la BD:

```python
def test_my_feature(db_session):  # No 'app'
    # Tu test aquí
```

### ModuleNotFoundError: No module named 'app'

Verificar que `conftest.py` tiene:

```python
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

---

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-flask](https://pytest-flask.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Testing Flask Applications](https://flask.palletsprojects.com/en/2.3.x/testing/)
