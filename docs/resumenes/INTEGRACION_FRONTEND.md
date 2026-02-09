# 🎨 Guía de Integración Frontend

## Descripción
Este documento guía la integración del nuevo sistema de chat con moneda y transacciones reales en el frontend.

---

## 📋 Cambios en Frontend Necesarios

### 1. Script de Inicialización de Chat

**Archivo:** `frontend/js/ai-chat.js`

```javascript
// Agregar al inicio de cargar el chat
async function initializeChat() {
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch('/api/chat/init', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!data.initialized) {
            // Primera vez - mostrar mensaje de inicialización
            displayMessage({
                role: 'assistant',
                content: data.message
            });
        }
    } catch (error) {
        console.error('Error inicializando chat:', error);
    }
}

// Llamar al cargar la página
window.addEventListener('load', initializeChat);
```

---

### 2. Función para Enviar Mensajes

**Actualización en:** `frontend/js/ai-chat.js`

```javascript
async function sendMessage(messageContent) {
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch('/api/chat/send', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: messageContent
            })
        });
        
        const data = await response.json();
        
        if (response.status === 201) {
            // Mostrar mensaje del usuario
            displayMessage({
                role: 'user',
                content: data.user_message.content
            });
            
            // Mostrar respuesta del bot
            displayMessage({
                role: 'assistant',
                content: data.assistant_message.content,
                isTransactionConfirmation: 
                    data.assistant_message.content.includes('Transacción registrada')
            });
            
            // Si fue transacción, actualizar UI
            if (data.assistant_message.content.includes('Balances actualizados')) {
                updateAccountsDisplay();
            }
        } else {
            displayError(data.error || 'Error al enviar mensaje');
        }
    } catch (error) {
        console.error('Error:', error);
        displayError('Error de conexión');
    }
}
```

---

### 3. Función para Mostrar Mensajes

**Crear/Actualizar:** `frontend/js/ai-chat.js`

```javascript
function displayMessage(message) {
    const chatContainer = document.getElementById('chat-messages');
    const messageEl = document.createElement('div');
    
    messageEl.className = `message ${message.role}`;
    
    // Parsear markdown simple
    let content = message.content
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
    
    messageEl.innerHTML = `
        <div class="message-content">
            ${content}
        </div>
    `;
    
    if (message.isTransactionConfirmation) {
        messageEl.classList.add('success');
    }
    
    chatContainer.appendChild(messageEl);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function displayError(error) {
    displayMessage({
        role: 'assistant',
        content: `❌ Error: ${error}`
    });
}
```

---

### 4. Actualizar Pantalla de Cuentas

**Crear en:** `frontend/js/ai-chat.js`

```javascript
async function updateAccountsDisplay() {
    try {
        const response = await fetch('/api/accounts', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const { accounts } = await response.json();
        
        // Actualizar UI de cuentas
        const accountsContainer = document.getElementById('accounts-list');
        accountsContainer.innerHTML = accounts.map(acc => `
            <div class="account-card">
                <h3>${acc.name}</h3>
                <p class="balance">${acc.currency} ${acc.current_balance.toFixed(2)}</p>
                <small>${acc.account_type}</small>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error actualizando cuentas:', error);
    }
}
```

---

## 🎨 Estilos CSS

**Agregar a:** `frontend/css/ai-chat.css`

```css
/* Estilos para mensajes de transacción */
.message.success {
    background-color: #d4edda;
    border-left: 4px solid #28a745;
    color: #155724;
    padding: 15px;
    margin: 10px 0;
    border-radius: 4px;
}

.message.success strong {
    color: #155724;
}

/* Estilos para error */
.message.error {
    background-color: #f8d7da;
    border-left: 4px solid #dc3545;
    color: #721c24;
}

/* Contenedor de cuentas */
#accounts-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.account-card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.account-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.account-card h3 {
    margin: 0 0 10px 0;
    color: #333;
}

.account-card .balance {
    font-size: 24px;
    font-weight: bold;
    color: #28a745;
    margin: 10px 0;
}

.account-card small {
    color: #666;
    font-size: 12px;
}
```

---

## 🔄 Flujo de Interacción Completo

```
┌─────────────────────────────────────┐
│ Usuario abre ai-chat.html           │
└──────────────┬──────────────────────┘
               │
               ├─→ window.addEventListener('load', initializeChat)
               │
               ↓
┌─────────────────────────────────────┐
│ POST /api/chat/init                 │
│ Verificar si chat_initialized=false │
└──────────────┬──────────────────────┘
               │
               ├─→ SI: Mostrar pregunta de moneda
               │
               ├─→ NO: Continuar con chat normal
               │
               ↓
┌─────────────────────────────────────┐
│ Usuario escribe en input + Enter     │
└──────────────┬──────────────────────┘
               │
               ├─→ sendMessage(content)
               │
               ↓
┌─────────────────────────────────────┐
│ POST /api/chat/send                 │
│ Enviar mensaje                      │
└──────────────┬──────────────────────┘
               │
               ├─→ Procesar en backend
               │
               ├─→ Detectar transacción?
               │   ├─ SÍ → Crear en BD
               │   └─ NO → Responder con IA
               │
               ↓
┌─────────────────────────────────────┐
│ Response con user_message +          │
│ assistant_message                   │
└──────────────┬──────────────────────┘
               │
               ├─→ displayMessage(user_msg)
               │
               ├─→ displayMessage(assistant_msg)
               │
               ├─→ ¿Fue transacción? → updateAccountsDisplay()
               │
               ↓
┌─────────────────────────────────────┐
│ Mostrar en UI                       │
│ - Mensajes                          │
│ - Balances actualizados             │
│ - Consejo de IA                     │
└─────────────────────────────────────┘
```

---

## 📱 HTML Necesario

**Actualizar/Crear:** `frontend/html/ai-chat.html`

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chat Financiero</title>
    <link rel="stylesheet" href="../css/ai-chat.css">
</head>
<body>
    <div class="chat-container">
        <!-- Cuentas activas -->
        <div class="sidebar-accounts">
            <h2>Mis Cuentas</h2>
            <div id="accounts-list">
                <!-- Se llena dinámicamente -->
            </div>
        </div>
        
        <!-- Chat -->
        <div class="chat-section">
            <div id="chat-messages" class="messages-container">
                <!-- Mensajes aparecen aquí -->
            </div>
            
            <div class="input-section">
                <input 
                    type="text" 
                    id="message-input" 
                    placeholder="Escribe tu mensaje..."
                    onkeypress="if(event.key==='Enter') sendMessage(this.value); this.value=''"
                >
                <button onclick="sendMessage(document.getElementById('message-input').value)">
                    Enviar
                </button>
            </div>
        </div>
    </div>
    
    <script src="../js/ai-chat.js"></script>
    <script src="../js/api.js"></script>
</body>
</html>
```

---

## ✅ Checklist de Integración

- [ ] Copiar código de `initializeChat()` a `ai-chat.js`
- [ ] Actualizar función `sendMessage()` con nuevo endpoint
- [ ] Agregar función `displayMessage()` y `displayError()`
- [ ] Crear función `updateAccountsDisplay()`
- [ ] Agregar estilos CSS para mensajes success/error
- [ ] Actualizar HTML con contenedor de cuentas
- [ ] Probar inicialización de moneda
- [ ] Probar creación de transacción
- [ ] Probar actualización de balances
- [ ] Probar simulaciones (no crear transacción)

---

## 🧪 Pruebas Manuales

### Test 1: Inicialización
```
1. Abrir ai-chat.html
2. Verificar: Bot pregunta "¿Cuál es tu moneda?"
3. Responder: "USD"
4. Verificar: Confirma "Moneda establecida: USD"
```

### Test 2: Crear Transacción
```
1. Escribir: "Compré 25 dólares de aceite"
2. Verificar: Aparece "✅ Transacción registrada"
3. Verificar: Se muestra monto, cuenta, balance
4. Revisar BD: Debe existir registro en tabla transactions
```

### Test 3: Consulta
```
1. Escribir: "¿Cuál es mi balance?"
2. Verificar: Bot responde con saldos actualizados
```

### Test 4: Simulación
```
1. Escribir: "¿Qué pasaría si gastara 100?"
2. Verificar: Solo responde, no crea transacción
3. Revisar BD: No debe crear registro
```

---

## 🔗 APIs Frontend Necesarias

Asegurarse que `frontend/js/api.js` tenga:

```javascript
const API_BASE = 'http://localhost:5000/api';

async function apiCall(method, endpoint, body = null) {
    const token = localStorage.getItem('token');
    const options = {
        method,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };
    
    if (body) options.body = JSON.stringify(body);
    
    return fetch(`${API_BASE}${endpoint}`, options);
}
```

---

## 📊 Variables Locales a Mantener

```javascript
// Moneda del usuario
let userCurrency = 'USD';

// Estado del chat
let chatInitialized = false;

// Historial de mensajes
let messageHistory = [];

// Cuentas disponibles
let userAccounts = [];
```

---

## 🚀 Deployment

### Antes de poner en producción:

1. ✅ Verificar tokens JWT válidos
2. ✅ Probar en diferentes navegadores
3. ✅ Validar CORS en backend
4. ✅ Cambiar API_BASE según ambiente
5. ✅ Agregar loading spinners
6. ✅ Implementar manejo de errores
7. ✅ Agregar logs de debug
8. ✅ Usar HTTPS

---

## 💾 Guardar Datos Locales (Opcional)

```javascript
// Guardar último mensaje enviado
localStorage.setItem('lastMessage', messageContent);

// Guardar preferencia de moneda
localStorage.setItem('preferredCurrency', userCurrency);

// Cargar al iniciar
window.addEventListener('load', () => {
    userCurrency = localStorage.getItem('preferredCurrency') || 'USD';
});
```

---

**Documento de Integración Frontend completado**  
**Última actualización:** 2 de enero de 2026
