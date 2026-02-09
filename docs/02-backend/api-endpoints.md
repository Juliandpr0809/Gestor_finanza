# 🔌 API Endpoints Reference

Documentación completa de todos los endpoints del API.

**Base URL**: `http://localhost:5000/api`

---

## 🔐 Autenticación

Todos los endpoints (excepto login/register) requieren token JWT:

```http
Authorization: Bearer <your-jwt-token>
```

### POST `/auth/register`

Registrar nuevo usuario.

**Request:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

**Response:** `201 Created`
```json
{
  "message": "Usuario registrado exitosamente",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

### POST `/auth/login`

Iniciar sesión.

**Request:**
```json
{
  "identifier": "john@example.com",
  "password": "securepass123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Sesión iniciada",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

### GET `/auth/me`

Obtener usuario actual.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com"
}
```

---

## 💳 Cuentas

### GET `/accounts`

Listar todas las cuentas del usuario.

**Response:** `200 OK`
```json
{
  "accounts": [
    {
      "id": 1,
      "name": "Main Checking",
      "account_type": "checking",
      "currency": "USD",
      "current_balance": 5000.0,
      "is_active": true
    }
  ]
}
```

### POST `/accounts`

Crear nueva cuenta.

**Request:**
```json
{
  "name": "Savings Account",
  "account_type": "savings",
  "currency": "USD",
  "initial_balance": 10000.0
}
```

**Tipos permitidos:** `checking`, `savings`, `cash`, `credit_card`, `investment`

**Monedas soportadas:** `USD`, `EUR`, `GBP`, `COP`, `MXN`, `ARS`, `BRL`

### PUT `/accounts/{id}`

Actualizar cuenta.

### DELETE `/accounts/{id}`

Eliminar cuenta.

---

## 💸 Transacciones

### GET `/transactions`

Listar transacciones con filtros.

**Query params:**
- `account_id` (int): Filtrar por cuenta
- `category_id` (int): Filtrar por categoría
- `type` (string): `income` o `expense`
- `start_date` (ISO date): Desde fecha
- `end_date` (ISO date): Hasta fecha
- `page` (int): Página (default: 1)
- `per_page` (int): Items por página (default: 20)

**Response:**
```json
{
  "transactions": [
    {
      "id": 1,
      "account_id": 1,
      "account_name": "Main Checking",
      "category_id": 2,
      "category_name": "Alimentación",
      "category_icon": "fa-utensils",
      "type": "expense",
      "amount": 50.0,
      "description": "Supermercado",
      "date": "2024-01-15T10:30:00",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "pages": 3
  }
}
```

### POST `/transactions`

Crear transacción.

**Request:**
```json
{
  "account_id": 1,
  "category_id": 2,
  "type": "expense",
  "amount": 50.0,
  "description": "Supermercado",
  "notes": "Compra semanal",
  "date": "2024-01-15T10:30:00"
}
```

### GET `/transactions/stats/monthly`

Estadísticas mensuales.

**Query params:**
- `month` (string): Formato `YYYY-MM` (default: mes actual)

**Response:**
```json
{
  "month": "2024-01",
  "income": 5000.0,
  "expenses": 2300.0,
  "net": 2700.0
}
```

---

## 🏷️ Categorías

### GET `/categories`

Listar categorías del usuario.

### POST `/categories`

Crear categoría personalizada.

**Request:**
```json
{
  "name": "Gimnasio",
  "category_type": "expense",
  "icon": "fa-dumbbell",
  "color": "#FF5733"
}
```

---

## 🤖 Chat IA

### POST `/chat/send`

Enviar mensaje al asistente IA.

**Request:**
```json
{
  "content": "¿Cuánto gasté este mes?"
}
```

### GET `/chat/messages`

Obtener historial de chat.

### GET `/chat/analyze`

Análisis automático de gastos.

---

## ❌ Códigos de Error

- `400` - Bad Request (datos inválidos)
- `401` - Unauthorized (no autenticado)
- `403` - Forbidden (sin permisos)
- `404` - Not Found (recurso no existe)
- `409` - Conflict (datos duplicados)
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error

**Formato de error:**
```json
{
  "error": "Descripción del error",
  "details": {}  // Opcional, detalles adicionales
}
```
