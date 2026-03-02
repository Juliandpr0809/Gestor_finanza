"""
Guía de Mensajes de Error Mejorados - Chat IA
==============================================

Esta guía documenta los mensajes de error que el sistema muestra cuando NO se puede crear una transacción.

## 1. NO SE DETECTÓ INTENCIÓN DE TRANSACCIÓN

**Cuándo:** El mensaje no contiene palabras clave de transacción (gasté, compré, recibí, etc.) ni números.

**Mensaje al usuario:**
```
⚠️ **No entendí qué transacción querrías crear**

👉 **¿Qué quisiste decir?**

Si querías registrar un gasto o ingreso, intenta con frases claras:

💸 **Gastos:**
• "Gasté [monto] en [descripción]"
• "Compré [cosa] por [monto]"
• "Le pasé [monto] para [motivo]"

💰 **Ingresos:**
• "Me llegaron [monto] de [motivo]"
• "Recibí [monto] por [descripción]"
• "Ingresó mi salario de [monto]"
```

**Log en consola:**
```
DEBUG CHAT: ❌ NO transaction intent detected for message: 'cuanto tengo'
DEBUG CHAT: Reason: Missing transaction keywords or numbers
```

---

## 2. FALTA INFORMACIÓN (Monto, Tipo o Descripción)

**Cuándo:** Se detectó intención pero falta algún dato crítico.

**Mensaje al usuario:**
```
❌ **No se pudo crear la transacción**

🔍 **Razones:**

Falta información:
💵 **Monto** (ej: 200000, 50k, 1500)
🎯 **Tipo de transacción** (usa palabras como: "gasté", "compré", "me llegaron", "ingresó")
📝 **Descripción** (para qué fue: arriendo, mercado, salario, etc.)
```

**Log en consola:**
```
DEBUG CHAT: ❌ Skipping incomplete transaction: amount=None, type='expense', desc='mercado'
```

---

## 3. NO HAY CUENTAS CONFIGURADAS

**Cuándo:** El usuario intenta crear una transacción pero no tiene cuentas creadas.

**Mensaje al usuario:**
```
⚠️ **No tienes cuentas configuradas**

👉 Ve a la página de "Cuentas" y crea una primero.
Ejemplo: "Nequi", "Efectivo", "Banco", etc.
```

**Log en consola:**
```
DEBUG CHAT: ❌ No account found for user 123
```

---

## 4. NO HAY CATEGORÍAS CONFIGURADAS

**Cuándo:** El usuario intenta crear una transacción pero no tiene categorías del tipo necesario.

**Mensaje al usuario:**
```
⚠️ **No tienes categorías de gastos**

👉 Ve a la página de "Transacciones" y crea una categoría primero.
```

**Log en consola:**
```
DEBUG CHAT: ❌ No category found for user 123, type expense
```

---

## 5. CUENTA NO ENCONTRADA

**Cuándo:** El sistema detectó un nombre de cuenta pero no existe.

**Mensaje al usuario:**
```
❌ **Cuenta 'Daviplata' no encontrada**

💳 Tus cuentas disponibles: Nequi, Efectivo, Banco
```

**Log en consola:**
```
DEBUG CHAT: ❌ Account 'Daviplata' not found
```

---

## 6. CATEGORÍA NO ENCONTRADA

**Cuándo:** El sistema detectó una categoría pero no existe.

**Mensaje al usuario:**
```
❌ **Categoría 'Entretenimiento' no encontrada**

📊 Categorías disponibles: Comida, Transporte, Servicios
```

**Log en consola:**
```
DEBUG CHAT: ❌ Category 'Entretenimiento' not found
```

---

## 7. ERROR TÉCNICO AL CREAR

**Cuándo:** Hubo una excepción durante la creación de la transacción.

**Mensaje al usuario:**
```
❌ **Error técnico al crear transacción:**
[Mensaje del error truncado a 100 caracteres]
```

**Log en consola:**
```
Error creating transaction: [stack trace completo]
DEBUG CHAT: ❌ 1 transactions failed
```

---

## 8. LA IA SIMULÓ SIN CREAR (Falso Positivo)

**Cuándo:** La IA respondió como si creó una transacción pero NO la creó realmente.

**Mensaje agregado al usuario:**
```
⚠️ **Nota:** Esta es solo una simulación. Para crear transacciones reales, usa frases como:
• 'Gasté 25000 en mercado'
• 'Le pasé 200k para arriendo'
```

**Log en consola:**
```
DEBUG CHAT: ⚠️️ AI simulated transaction without creating it!
```

---

## EJEMPLOS DE FRASES QUE FUNCIONAN

✅ **Gastos:**
- "Gasté 25000 en mercado"
- "Le pasé 200k a mi mamá para el arriendo"
- "Compré una pizza por 35000"
- "Pagué 50000 del agua"
- "Saqué 100k del cajero"

✅ **Ingresos:**
- "Me llegaron 50000 de salario"
- "Recibí 25000 por un trabajo"
- "Me depositaron 100k"
- "Ingresó mi pago de 1200000"

❌ **Frases que NO funcionan:**
- "cuanto tengo" (consulta, no transacción)
- "pasé dinero" (falta monto)
- "gasté en mercado" (falta monto)
- "le di plata a mi mamá" (falta monto)

---

## FLUJO DE VALIDACIÓN

```
1. ¿Tiene palabras clave de transacción? (gasté, compré, recibí, etc.)
   ❌ → "No entendí qué transacción querrías crear"
   
2. ¿Tiene números?
   ❌ → "Falta información: Monto"
   
3. ¿Se pudo extraer tipo de transacción?
   ❌ → "Falta información: Tipo de transacción"
   
4. ¿Se pudo extraer descripción?
   ❌ → "Falta información: Descripción"
   
5. ¿El usuario tiene cuentas?
   ❌ → "No tienes cuentas configuradas"
   
6. ¿El usuario tiene categorías del tipo correcto?
   ❌ → "No tienes categorías de [gastos/ingresos]"
   
7. ¿La cuenta especificada existe?
   ❌ → "Cuenta '[nombre]' no encontrada"
   
8. ¿La categoría especificada existe?
   ❌ → "Categoría '[nombre]' no encontrada"
   
9. ¿Se creó sin errores?
   ❌ → "Error técnico al crear transacción"
   
✅ → "Transacción registrada" + detalles
```

---

## DEBUGGING EN CONSOLA

Todos los fallos ahora imprimen:
- Emoji ❌ para errores
- Mensaje específico del problema
- Datos relevantes (mensaje original, valores extraídos, etc.)

Ejemplo completo:
```
DEBUG CHAT: Processing part: le pasé dinero a mi mamá
DEBUG CHAT: Extracted data: {'amount': None, 'transaction_type': 'expense', 'description': 'mamá'}
DEBUG CHAT: ❌ Skipping incomplete transaction: amount=None, type=expense, desc=mamá
DEBUG CHAT: ❌ 1 transactions failed
```

---

## CONFIGURACIÓN

Para habilitar logging detallado en desarrollo:
- Los mensajes DEBUG se imprimen automáticamente en consola
- Para deshabilitarlos, cambiar nivel de logging en app.py

Para producción:
- Los mensajes de error al usuario son siempre amigables
- Los logs técnicos van solo a la consola del servidor
