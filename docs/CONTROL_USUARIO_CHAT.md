# Control Total del Usuario via Chat

## 📋 Descripción

Ahora puedes controlar completamente tus cuentas y transacciones directamente desde el chat usando instrucciones en lenguaje natural. El sistema detecta tus comandos y solicita confirmación antes de ejecutar cambios importantes.

## 🎯 Comandos Disponibles

### 1. **Cambiar Balance de Cuenta**

**Palabras clave detectadas:**
- "cambiar balance"
- "set balance"
- "establecer balance"
- "balance a"
- "ajustar balance"

**Ejemplos de uso:**
```
"Cambiar mi balance a 200000"
"Establecer balance a COP 150,000"
"Ajustar balance a 50000"
```

**Flujo:**
1. El sistema detecta tu intención de cambiar el balance
2. Te muestra tu balance actual vs el nuevo balance
3. Solicita confirmación explícita
4. Escribe "CONFIRMAR" para aplicar el cambio

**Respuesta del sistema:**
```
⚠️ CONFIRMACIÓN REQUERIDA

Estás a punto de cambiar el balance de Nequi:
- Balance actual: COP 100,000.00
- Nuevo balance: COP 200,000.00
- Diferencia: COP 100,000.00

¿Estás seguro? Escribe "CONFIRMAR" para aplicar este cambio.
```

---

### 2. **Borrar/Eliminar Transacción**

**Palabras clave detectadas:**
- "borrar"
- "eliminar"
- "delete transaction"
- "borrar transacción"
- "quitar transacción"

**Ejemplos de uso:**
```
"Borrar la transacción de 25 pesos"
"Eliminar transacción 45"
"Quitar la transacción del supermercado"
```

**Flujo:**
1. El sistema detecta tu intención de borrar una transacción
2. Te muestra tus últimas transacciones con sus IDs
3. Te pide que proporciones el ID exacto de la transacción a eliminar
4. Una vez confirmado, la transacción se elimina y el balance se ajusta automáticamente

**Respuesta del sistema:**
```
⚠️ ELIMINAR TRANSACCIÓN

Tus últimas transacciones:
- ID 41: COP -50.00 - Gasolina
- ID 42: COP -25.00 - Comida
- ID 43: COP -100.00 - Supermercado
- ID 44: COP 500.00 - Ingreso
- ID 45: COP -75.00 - Transporte

¿Cuál transacción deseas eliminar? Proporciona el ID (número).

Ejemplo: "Eliminar transacción 45"

⚠️ Esto no se puede deshacer fácilmente.
```

---

### 3. **Editar Transacción**

**Palabras clave detectadas:**
- "editar"
- "edit"
- "cambiar descripción"
- "change description"
- "modificar"

**Ejemplos de uso:**
```
"Editar transacción 45 - cambiar descripción a 'Compra en supermercado'"
"Editar transacción 42 - monto 150"
"Modificar la descripción de la transacción 43"
```

**Flujo:**
1. El sistema detecta tu intención de editar
2. Te muestra tus últimas transacciones con IDs
3. Te pide especificar qué cambios deseas hacer (descripción, monto, etc.)
4. Aplica los cambios y ajusta el balance si es necesario

**Respuesta del sistema:**
```
📝 EDITAR TRANSACCIÓN

Tus últimas transacciones:
- ID 41: COP -50.00 - Gasolina
- ID 42: COP -25.00 - Comida
- ID 43: COP -100.00 - Supermercado

¿Cuál transacción deseas editar? Proporciona el ID y los cambios.

Ejemplo: "Editar transacción 45 - cambiar descripción a 'Compra en supermercado'"
Ejemplo: "Editar transacción 45 - monto 150"

¿Qué cambios deseas hacer?
```

---

### 4. **Resetear Balance a Valor Inicial**

**Palabras clave detectadas:**
- "reset balance"
- "resetear balance"
- "balance inicial"
- "inicial"

**Ejemplos de uso:**
```
"Resetear balance"
"Volver al balance inicial"
"Reset de todas las cuentas"
```

**Flujo:**
1. El sistema detecta tu intención de resetear
2. Te muestra todas las cuentas con balance actual → balance inicial
3. Solicita confirmación explícita
4. Escribe "CONFIRMAR" para resetear TODAS las cuentas

**Respuesta del sistema:**
```
⚠️ CONFIRMACIÓN REQUERIDA - RESETEAR BALANCES

Se resetearán los siguientes balances a sus valores iniciales:
- Nequi: Balance actual COP 150,000.00 → Inicial COP 100,000.00
- Banco: Balance actual COP 250,000.00 → Inicial COP 200,000.00

¿Estás seguro? Escribe "CONFIRMAR" para aplicar este cambio.

⚠️ Esta acción afectará TODAS tus cuentas.
```

---

## 🔒 Seguridad

### Confirmaciones Requeridas

Para proteger tus datos, **todos los comandos de modificación requieren confirmación explícita**:

1. **Primera acción:** El sistema detecta tu intención y te muestra lo que va a cambiar
2. **Confirmación:** Debes escribir "CONFIRMAR" (exactamente así, en mayúsculas)
3. **Ejecución:** Solo después de confirmar se aplican los cambios

### Ejemplo de Flujo Completo:

**Usuario:**
```
Cambiar mi balance a 200000
```

**Sistema:**
```
⚠️ CONFIRMACIÓN REQUERIDA

Estás a punto de cambiar el balance de Nequi:
- Balance actual: COP 100,000.00
- Nuevo balance: COP 200,000.00
- Diferencia: COP 100,000.00

¿Estás seguro? Escribe "CONFIRMAR" para aplicar este cambio.
```

**Usuario:**
```
CONFIRMAR
```

**Sistema:**
```
✅ Balance actualizado correctamente

- Cuenta: Nequi
- Balance anterior: COP 100,000.00
- Balance nuevo: COP 200,000.00
- Cambio: COP 100,000.00

✨ Tu cuenta ha sido actualizada.
```

---

## 🛠️ Implementación Técnica

### Archivos Modificados

1. **`backend/services/ai_service.py`**
   - Nueva función: `detect_control_command(message)`
   - Detecta automáticamente comandos de control en los mensajes

2. **`backend/routes/chat.py`**
   - Nueva función: `process_control_command(user, user_id, control_command, original_message)`
   - Nueva función: `process_confirmation(user, user_id, last_control_action, confirmation_message)`
   - Procesamiento prioritario de comandos de control antes de crear transacciones

3. **Endpoints de backend ya existentes (ahora usados por el chat):**
   - `POST /api/accounts/<id>/set-balance` - Cambiar balance
   - `POST /api/accounts/<id>/reset-balance` - Resetear balance
   - `DELETE /api/transactions/<id>` - Eliminar transacción
   - `PUT /api/transactions/<id>` - Editar transacción
   - `POST /api/transactions/<id>/restore` - Restaurar transacción

---

## 🎨 Características Destacadas

✅ **Lenguaje Natural:** Usa tu propio lenguaje, no necesitas comandos específicos

✅ **Confirmaciones Inteligentes:** Te muestra exactamente qué va a cambiar antes de aplicarlo

✅ **Seguridad:** Requiere confirmación explícita para cambios importantes

✅ **Contexto de Moneda:** Todas las operaciones respetan tu moneda preferida (COP, USD, EUR, etc.)

✅ **Historial Completo:** Todas las acciones quedan registradas en el chat

✅ **Balance Automático:** Los cambios en transacciones ajustan automáticamente el balance

---

## 📝 Notas Importantes

1. **Comandos de eliminación son permanentes:** Eliminar una transacción no se puede deshacer fácilmente
2. **Resetear afecta TODAS las cuentas:** El comando de reset aplica a todas tus cuentas simultáneamente
3. **Cambios de balance son directos:** No crean transacciones, solo ajustan el valor del balance
4. **Las confirmaciones expiran:** Si no confirmas inmediatamente, tendrás que volver a enviar el comando

---

## 🚀 Próximas Mejoras

- [ ] Registro de auditoría de cambios manuales
- [ ] Deshacer última acción (UNDO)
- [ ] Cambiar balance específico por cuenta (si tienes múltiples cuentas)
- [ ] Confirmación con PIN o contraseña adicional
- [ ] Límites de cambio de balance diario

---

## 💬 Ejemplos de Conversación

### Escenario 1: Cambiar Balance
```
Usuario: Hola, necesito cambiar mi balance a 500000
Sistema: [detecta comando y muestra confirmación]
Usuario: CONFIRMAR
Sistema: ✅ Balance actualizado correctamente
```

### Escenario 2: Eliminar Transacción
```
Usuario: Borrar la transacción de comida de 25 pesos
Sistema: [muestra lista de transacciones con IDs]
Usuario: Eliminar transacción 42
Sistema: ✅ Transacción eliminada. Balance ajustado.
```

### Escenario 3: Resetear Todo
```
Usuario: Necesito resetear todas las cuentas al balance inicial
Sistema: [muestra balance actual → inicial de todas las cuentas]
Usuario: CONFIRMAR
Sistema: ✅ Balances reseteados a valores iniciales
```

---

## ✨ Conclusión

Con estas nuevas funcionalidades, tienes **control total** sobre tus finanzas directamente desde el chat. Simplemente dile al sistema qué necesitas hacer, y él te guiará de forma segura para aplicar los cambios.

**¡Disfruta tu nuevo control financiero! 💰**
