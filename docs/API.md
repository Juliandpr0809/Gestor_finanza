# Documentación de API

## 🔐 Autenticación

### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "identifier": "juliandpr0809@gmai.com",
  "password": "tu_contraseña"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "message": "Sesión iniciada",
  "user": {
    "id": 3,
    "username": "juliandpr0809",
    "email": "juliandpr0809@gmai.com"
  }
}
```

### Register
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "nuevo_usuario",
  "email": "email@ejemplo.com",
  "password": "contraseña"
}
```

## 💬 Chat IA

### Enviar mensaje
```
POST /api/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "¿Cuál es mi balance total?"
}

Response 200:
{
  "response": "Respuesta de la IA...",
  "context": {
    "accounts": [...],
    "transactions": [...]
  }
}
```

## 💰 Transacciones

### Obtener transacciones
```
GET /api/transactions
Authorization: Bearer {token}

Response 200:
[
  {
    "id": 1,
    "amount": 500,
    "category": "Alimentación",
    "description": "Compra en supermercado",
    "date": "2026-01-01"
  }
]
```

### Crear transacción
```
POST /api/transactions
Authorization: Bearer {token}
Content-Type: application/json

{
  "amount": 100,
  "category": "Transporte",
  "description": "Uber a casa",
  "account_id": 1
}
```

## 👤 Cuentas

### Obtener cuentas
```
GET /api/accounts
Authorization: Bearer {token}

Response 200:
[
  {
    "id": 1,
    "name": "Tarjeta Nequi",
    "current_balance": 1110.00
  },
  {
    "id": 2,
    "name": "Efectivo",
    "current_balance": 122566.00
  }
]
```

## 🔑 Headers Requeridos

```
Authorization: Bearer {token}
```

Donde `{token}` es el `access_token` obtenido en login.

