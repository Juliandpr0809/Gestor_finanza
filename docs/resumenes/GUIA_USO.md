# Guía de Uso - Chat Financiero con Transacciones Reales

## 🎯 Objetivo
El chat ahora pregunta tu moneda preferida la primera vez y **crea transacciones REALES** en la base de datos automáticamente.

---

## 📋 Flujo de Uso

### 1️⃣ Primera vez que abres el chat

```
Tu: [Abres el chat]

Bot: 👋 ¡Bienvenido a tu Gestor Financiero!
     ¿Cuál es tu moneda preferida?
     • USD - Dólar Estadounidense
     • EUR - Euro
     • COP - Peso Colombiano
     • MXN - Peso Mexicano
     • ARS - Peso Argentino
```

---

### 2️⃣ Respondes con tu moneda

```
Tu: USD

Bot: ✅ Moneda establecida: USD
     Perfecto, ahora todas tus transacciones estarán en USD.
     💡 Puedes:
     • Registrar transacciones: "Gasté 50 en comida"
     • Ver tus cuentas: "¿Cuál es mi balance?"
     • Obtener consejos: "Dame recomendaciones"
```

---

### 3️⃣ Registras una transacción

```
Tu: Compré 25 dólares de aceite de motor con mi tarjeta nequi

Bot: ✅ Transacción registrada
     - Monto: USD 25.00
     - Cuenta: tarjeta nequi (credit)
     - Descripción: aceite de motor
     
     🔄 Balances actualizados
     - tarjeta nequi (credit): USD 5.00
     - efectivo (savings): USD 40.00
     
     Balance Total: USD 45.00
     
     💡 Consejo: El gasto en mantenimiento del vehículo es importante,
        pero puedes intentar buscar ofertas o comprar en mayor cantidad
        para reducir el costo por unidad. Mantener un registro de estos
        gastos te ayudará a planificar mejor tu presupuesto mensual.
     
     Si necesitas revisar transacciones o más recomendaciones, ¡avísame! 💬✅
```

---

## ✨ Características Clave

### 🔒 Transacciones REALES
- ✅ Se guardan en la base de datos
- ✅ El balance se actualiza automáticamente
- ✅ Quedan registradas para análisis futuro
- ❌ NO son simuladas

### 💡 Inteligencia Artificial
- Lee tu mensaje de forma natural
- Extrae automáticamente: monto, descripción, cuenta
- Proporciona consejos personalizados
- Detecta cuando quieres simular (no crea transacción)

### 🎨 Autocompletado Inteligente
Si no especificas cuenta o categoría:
- **Cuenta**: Usa tu primera cuenta activa
- **Categoría**: Intenta inferir de la descripción

### 🚫 Control de Simulaciones
```
Tu: Simula que gasté 100 en comida

Bot: [Solo responde con análisis, NO crea transacción]
     Si gastaras $100 en comida...
```

---

## 📝 Ejemplos de Comandos

### Registrar Gasto
```
"Gasté 50 en gasolina"
"Compré un café por 3.50"
"Pague 100 de arriendo"
```

### Registrar Ingreso
```
"Recibí mi salario de 2000"
"Cobré 150 por freelance"
"Gané 50 en apuestas" 😄
```

### Consultas
```
"¿Cuál es mi balance?"
"¿Cuánto tengo en total?"
"Muéstrame mis últimas transacciones"
"Dame consejos de ahorro"
```

### Simulaciones (NO crea transacción)
```
"¿Qué pasaría si gastara 500?"
"Simula que compré un carro"
"Como sería mi balance si..."
```

---

## 🔄 Flujo Técnico

```
Usuario escribe mensaje
         ↓
API detecta chat_initialized
         ├─ FALSE: Procesar moneda
         │   ├─ Extrae moneda del texto
         │   ├─ Actualiza user.preferred_currency
         │   └─ Responde confirmación
         │
         └─ TRUE: Procesar mensaje normal
             ├─ Detecta intención de transacción
             │   ├─ Extrae datos (monto, descripción, etc)
             │   ├─ Busca cuenta y categoría
             │   ├─ CREA TRANSACCIÓN en BD
             │   ├─ Actualiza balance
             │   ├─ Genera consejo de IA
             │   └─ Responde con confirmación
             │
             └─ Sin intención: Chat general
                 └─ Responde con IA normalmente
```

---

## 📊 Base de Datos

### Tabla de Usuarios (users)
```
id              INTEGER PRIMARY KEY
username        VARCHAR(80) UNIQUE
email           VARCHAR(120) UNIQUE
password_hash   VARCHAR(255)
preferred_currency VARCHAR(3) ← NUEVO (ej: "USD")
chat_initialized BOOLEAN      ← NUEVO (ej: True/False)
created_at      DATETIME
updated_at      DATETIME
```

### Transacciones Creadas (transactions)
```
id              INTEGER PRIMARY KEY
user_id         INTEGER FK
account_id      INTEGER FK
category_id     INTEGER FK
amount          FLOAT (negativo para gastos)
description     VARCHAR(255)
transaction_type VARCHAR(50) (expense/income)
transaction_date DATETIME
created_at      DATETIME
```

---

## 🎓 Notas Técnicas

### ✅ Lo que funciona
- Crear transacciones reales automáticamente
- Actualizar balances en tiempo real
- Detectar intenciones naturales
- Generar consejos con IA
- Persistencia en BD (MySQL)
- Multi-cuenta y multi-categoría

### ⏳ En desarrollo
- Conversión entre monedas
- Presupuestos y límites
- Análisis predictivo
- Exportar reportes
- Integraciones bancarias

---

## 🆘 Preguntas Frecuentes

### ¿Cómo cambio de moneda?
Por ahora, se establece la primera vez. Para cambiar, contacta soporte.

### ¿Puedo usar múltiples monedas?
Actualmente no. Todas tus cuentas están en la misma moneda.

### ¿Se pierden las transacciones si cierro la sesión?
No, quedan guardadas en la BD. El chat es histórico.

### ¿Cómo borro una transacción?
Por ahora no está implementado. Se debe hacer manualmente en BD.

### ¿Funciona sin conexión a IA?
Las transacciones se crean igual. Sin IA, no hay consejos personalizados.

---

## 🚀 Próximos Pasos

1. **Frontend**: Integrar endpoint `/api/chat/init`
2. **UI**: Pantalla bonita para elegir moneda
3. **Testing**: Pruebas E2E del flujo completo
4. **Documentación**: API docs en Swagger

---

**Última actualización:** 2 de enero de 2026
**Estado:** ✅ Implementado y Testeado
