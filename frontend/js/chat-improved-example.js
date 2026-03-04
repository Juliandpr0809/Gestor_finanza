/**
 * EJEMPLO DE INTEGRACIÓN EN CHAT.JS
 * Muestra cómo modificar el JavaScript del chat para usar
 * el nuevo componente de confirmación visual
 */

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

let confirmComponent;
let currentPendingTransaction = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('Inicializando chat mejorado...');
    
    // Inicializar componente de confirmación
    confirmComponent = new TransactionConfirmationComponent(
        document.querySelector('.chat-messages')
    );
    
    // Event listeners
    initializeChatListeners();
});

function initializeChatListeners() {
    const sendButton = document.getElementById('send-message-btn');
    const messageInput = document.getElementById('message-input');
    
    // Enviar con botón
    sendButton?.addEventListener('click', () => {
        const message = messageInput.value.trim();
        if (message) {
            sendMessage(message);
            messageInput.value = '';
        }
    });
    
    // Enviar con Enter
    messageInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const message = messageInput.value.trim();
            if (message) {
                sendMessage(message);
                messageInput.value = '';
            }
        }
    });
}


// ============================================================================
// FUNCIONES PRINCIPALES
// ============================================================================

/**
 * Envía mensaje al chat con IA mejorada
 */
async function sendMessage(message) {
    try {
        // Mostrar mensaje del usuario
        appendMessage('user', message);
        
        // Deshabilitar input mientras procesa
        setInputEnabled(false);
        showTypingIndicator();
        
        // Enviar a backend
        const response = await fetch('/api/chat/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Ocultar typing indicator
        hideTypingIndicator();
        
        // Procesar respuesta según tipo
        await handleAIResponse(data);
        
    } catch (error) {
        console.error('Error enviando mensaje:', error);
        hideTypingIndicator();
        appendMessage('ai', '❌ Lo siento, ocurrió un error. Intenta de nuevo.');
        
    } finally {
        setInputEnabled(true);
    }
}

/**
 * Maneja diferentes tipos de respuesta de la IA
 */
async function handleAIResponse(data) {
    const { type, response, requires_confirmation, transaction_data, account_data, function: functionName } = data;
    
    // Mostrar respuesta textual
    if (response) {
        appendMessage('ai', response);
    }
    
    // Manejar según tipo
    switch (type) {
        case 'confirmation_required':
            if (functionName === 'create_transaction') {
                showTransactionConfirmation(transaction_data);
            } else if (functionName === 'create_account') {
                showAccountConfirmation(account_data);
            }
            break;
            
        case 'success':
            // Transacción/acción completada exitosamente
            if (data.transaction_id) {
                await refreshTransactions();
                await updateBalance();
            }
            break;
            
        case 'summary':
            // Resumen financiero
            if (data.data) {
                displayFinancialSummary(data.data);
            }
            break;
            
        case 'text':
        default:
            // Solo respuesta conversacional, ya mostrada arriba
            break;
    }
}

/**
 * Muestra componente de confirmación para transacción
 */
function showTransactionConfirmation(txData) {
    // Guardar datos pendientes
    currentPendingTransaction = txData;
    
    // Mostrar componente visual
    confirmComponent.show(
        txData,
        // Callback: Al confirmar
        async () => {
            await confirmAndSaveTransaction(txData);
        },
        // Callback: Al cancelar
        () => {
            appendMessage('ai', 'Entendido, transacción cancelada.');
            currentPendingTransaction = null;
        }
    );
}

/**
 * Confirma y guarda la transacción
 */
async function confirmAndSaveTransaction(txData) {
    try {
        const response = await fetch('/api/chat/confirm-transaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify(txData)
        });
        
        if (!response.ok) {
            throw new Error('Error al guardar transacción');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Actualizar UI
            await refreshTransactions();
            await updateBalance();
            
            // El componente ya muestra "¡Guardado!"
            currentPendingTransaction = null;
            
        } else {
            throw new Error(result.error || 'Error desconocido');
        }
        
    } catch (error) {
        console.error('Error confirmando transacción:', error);
        appendMessage('ai', `❌ Error: ${error.message}`);
        throw error; // Para que el componente muestre error
    }
}

/**
 * Muestra confirmación para crear cuenta
 */
function showAccountConfirmation(accountData) {
    // Crear HTML personalizado para confirmación de cuenta
    const confirmHTML = `
        <div class="account-confirmation">
            <p><strong>Crear nueva cuenta:</strong></p>
            <p>📛 Nombre: ${accountData.name}</p>
            <p>🏦 Tipo: ${accountData.type || 'Estándar'}</p>
            <p>💰 Saldo inicial: $${accountData.initial_balance || 0}</p>
            <button onclick="confirmCreateAccount()">✅ Confirmar</button>
            <button onclick="cancelCreateAccount()">❌ Cancelar</button>
        </div>
    `;
    
    const messagesContainer = document.querySelector('.chat-messages');
    messagesContainer.insertAdjacentHTML('beforeend', confirmHTML);
    scrollToBottom();
    
    // Guardar datos temporalmente
    window.pendingAccountData = accountData;
}

async function confirmCreateAccount() {
    try {
        const response = await fetch('/api/chat/confirm-account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify(window.pendingAccountData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            appendMessage('ai', `✅ Cuenta "${window.pendingAccountData.name}" creada exitosamente.`);
            await refreshAccounts();
        } else {
            throw new Error(result.error);
        }
        
    } catch (error) {
        appendMessage('ai', `❌ Error: ${error.message}`);
    } finally {
        // Limpiar confirmación
        document.querySelector('.account-confirmation')?.remove();
        window.pendingAccountData = null;
    }
}

function cancelCreateAccount() {
    appendMessage('ai', 'Entendido, cuenta no creada.');
    document.querySelector('.account-confirmation')?.remove();
    window.pendingAccountData = null;
}


// ============================================================================
// FUNCIONES DE UI
// ============================================================================

/**
 * Agrega mensaje al chat
 */
function appendMessage(sender, text) {
    const messagesContainer = document.querySelector('.chat-messages');
    if (!messagesContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Formatear texto con markdown básico
    const formattedText = formatMessageText(text);
    
    messageDiv.innerHTML = `
        <div class="message-content">
            ${formattedText}
        </div>
        <div class="message-time">
            ${getCurrentTime()}
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Formatea texto del mensaje (markdown básico)
 */
function formatMessageText(text) {
    return text
        // Negrita
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Cursiva
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Código inline
        .replace(/`(.*?)`/g, '<code>$1</code>')
        // Saltos de línea
        .replace(/\n/g, '<br>')
        // Emojis de estado (ya incluidos en el texto)
        .replace(/✅/g, '<span class="emoji-success">✅</span>')
        .replace(/❌/g, '<span class="emoji-error">❌</span>')
        .replace(/⏳/g, '<span class="emoji-pending">⏳</span>');
}

/**
 * Muestra/oculta indicador de "escribiendo..."
 */
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
        <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    
    document.querySelector('.chat-messages')?.appendChild(indicator);
    scrollToBottom();
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator')?.remove();
}

/**
 * Habilita/deshabilita input
 */
function setInputEnabled(enabled) {
    const input = document.getElementById('message-input');
    const button = document.getElementById('send-message-btn');
    
    if (input) input.disabled = !enabled;
    if (button) button.disabled = !enabled;
}

/**
 * Scroll automático al final del chat
 */
function scrollToBottom() {
    const messagesContainer = document.querySelector('.chat-messages');
    if (messagesContainer) {
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }
}

/**
 * Obtiene hora actual formateada
 */
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

/**
 * Muestra resumen financiero en el chat
 */
function displayFinancialSummary(data) {
    const { period, total_income, total_expense, balance, transaction_count } = data;
    
    const summaryHTML = `
        <div class="financial-summary">
            <div class="summary-header">
                📊 Resumen ${period === 'month' ? 'del mes' : 'semanal'}
            </div>
            <div class="summary-stats">
                <div class="stat income">
                    <span class="label">Ingresos</span>
                    <span class="value">+$${total_income.toFixed(2)}</span>
                </div>
                <div class="stat expense">
                    <span class="label">Gastos</span>
                    <span class="value">-$${total_expense.toFixed(2)}</span>
                </div>
                <div class="stat balance">
                    <span class="label">Balance</span>
                    <span class="value">${balance >= 0 ? '+' : ''}$${balance.toFixed(2)}</span>
                </div>
                <div class="stat count">
                    <span class="label">Transacciones</span>
                    <span class="value">${transaction_count}</span>
                </div>
            </div>
        </div>
    `;
    
    const messagesContainer = document.querySelector('.chat-messages');
    messagesContainer?.insertAdjacentHTML('beforeend', summaryHTML);
    scrollToBottom();
}


// ============================================================================
// FUNCIONES DE DATOS
// ============================================================================

/**
 * Actualiza lista de transacciones
 */
async function refreshTransactions() {
    try {
        const response = await fetch('/api/transactions', {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (response.ok) {
            const transactions = await response.json();
            // Actualizar UI de transacciones si existe
            if (typeof updateTransactionsList === 'function') {
                updateTransactionsList(transactions);
            }
        }
    } catch (error) {
        console.error('Error actualizando transacciones:', error);
    }
}

/**
 * Actualiza balance de cuentas
 */
async function updateBalance() {
    try {
        const response = await fetch('/api/accounts/summary', {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (response.ok) {
            const summary = await response.json();
            // Actualizar UI de balance si existe
            if (typeof updateBalanceDisplay === 'function') {
                updateBalanceDisplay(summary);
            }
        }
    } catch (error) {
        console.error('Error actualizando balance:', error);
    }
}

/**
 * Actualiza lista de cuentas
 */
async function refreshAccounts() {
    try {
        const response = await fetch('/api/accounts', {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (response.ok) {
            const accounts = await response.json();
            // Actualizar UI de cuentas si existe
            if (typeof updateAccountsList === 'function') {
                updateAccountsList(accounts);
            }
        }
    } catch (error) {
        console.error('Error actualizando cuentas:', error);
    }
}

/**
 * Obtiene token de autenticación
 */
function getAuthToken() {
    return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
}


// ============================================================================
// CSS ADICIONAL PARA RESUMEN FINANCIERO
// ============================================================================

const additionalStyles = `
<style>
.financial-summary {
    background: rgba(107, 159, 255, 0.08);
    border: 1px solid rgba(107, 159, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
}

.summary-header {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
    color: var(--text-primary);
}

.summary-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
}

.stat {
    background: rgba(255, 255, 255, 0.04);
    padding: 10px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.stat .label {
    font-size: 12px;
    color: var(--text-secondary);
}

.stat .value {
    font-size: 18px;
    font-weight: 700;
}

.stat.income .value {
    color: #00D4AA;
}

.stat.expense .value {
    color: #FF6B6B;
}

.stat.balance .value {
    color: #6B9FFF;
}

.account-confirmation {
    background: rgba(107, 159, 255, 0.08);
    border: 1px solid rgba(107, 159, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
}

.account-confirmation button {
    margin: 8px 8px 0 0;
    padding: 8px 16px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
}

.account-confirmation button:first-of-type {
    background: linear-gradient(135deg, #6B9FFF 0%, #8B6BFF 100%);
    color: white;
}

.account-confirmation button:last-of-type {
    background: rgba(255, 107, 107, 0.15);
    color: #FF6B6B;
}

.typing-indicator {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    margin: 8px 0;
}

.typing-dots {
    display: flex;
    gap: 4px;
}

.typing-dots span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(107, 159, 255, 0.6);
    animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.6;
    }
    30% {
        transform: translateY(-10px);
        opacity: 1;
    }
}

.emoji-success { color: #00D4AA; }
.emoji-error { color: #FF6B6B; }
.emoji-pending { color: #FFA500; }
</style>
`;

// Inyectar estilos
document.head.insertAdjacentHTML('beforeend', additionalStyles);


// ============================================================================
// EXPORTAR PARA DEBUGGING
// ============================================================================

window.chatDebug = {
    sendMessage,
    confirmComponent,
    getCurrentPendingTransaction: () => currentPendingTransaction,
    refreshAll: async () => {
        await refreshTransactions();
        await updateBalance();
        await refreshAccounts();
    }
};

console.log('✅ Chat mejorado cargado. Usa window.chatDebug para debugging.');
