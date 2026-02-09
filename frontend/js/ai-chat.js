// ==========================================
// AI CHAT - FUNCTIONALITY
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // La autenticación es manejada por auth-handler.js

    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const voiceBtn = document.getElementById('voiceBtn');
    const chatMessages = document.getElementById('chatMessages');
    const suggestionChips = document.querySelectorAll('.suggestion-chip');
    const btnHelp = document.getElementById('btnHelp');
    const btnCloseHelp = document.getElementById('btnCloseHelp');
    const helpPanel = document.getElementById('helpPanel');

    let isLoading = false;

    // Historial de mensajes para navegación con flechas
    let messageHistory = [];
    let historyIndex = -1;
    let currentDraft = ''; // Guardar el borrador actual

    // Help panel toggle
    if (btnHelp) {
        btnHelp.addEventListener('click', () => {
            helpPanel.style.display = 'flex';
        });
    }

    if (btnCloseHelp) {
        btnCloseHelp.addEventListener('click', () => {
            helpPanel.style.display = 'none';
        });
    }

    // Close help panel when clicking outside
    if (helpPanel) {
        helpPanel.addEventListener('click', (e) => {
            if (e.target === helpPanel) {
                helpPanel.style.display = 'none';
            }
        });
    }

    // Close help panel with ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && helpPanel.style.display === 'flex') {
            helpPanel.style.display = 'none';
        }
    });

    // Load chat history on init y lanzar inicialización de moneda si aplica
    loadChatHistory();

    // Async initialization de chat
    (async () => {
        try {
            const init = await api.initChat();
            if (init && init.initialized === false && init.message) {
                // Mostrar mensaje de bienvenida/moneda del sistema
                addMessage(init.message, 'ai');
            }
        } catch (e) {
            // Ignorar si ya inicializado o si falla sin token
            console.log('Init chat skipped:', e?.message || e);
        }
    })();

    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = chatInput.scrollHeight + 'px';

        // Enable/disable send button
        sendBtn.disabled = chatInput.value.trim() === '' || isLoading;
    });

    // Handle Enter key to send message (Shift+Enter for new line)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (chatInput.value.trim() && !isLoading) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
        // Navegación del historial con flechas arriba/abajo
        else if (e.key === 'ArrowUp') {
            e.preventDefault();
            navigateHistory('up');
        }
        else if (e.key === 'ArrowDown') {
            e.preventDefault();
            navigateHistory('down');
        }
    });

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();

        if (message && !isLoading) {
            // Guardar en historial
            messageHistory.push(message);
            historyIndex = messageHistory.length; // Resetear índice
            currentDraft = ''; // Limpiar borrador

            await sendMessage(message);
            chatInput.value = '';
            chatInput.style.height = 'auto';
            sendBtn.disabled = true;
        }
    });

    // Handle suggestion chips
    suggestionChips.forEach(chip => {
        chip.addEventListener('click', async () => {
            const prompt = chip.dataset.prompt;
            await sendMessage(prompt);

            // Remove suggestions after first interaction
            document.querySelector('.quick-suggestions')?.remove();
        });
    });

    // Load chat history
    async function loadChatHistory() {
        try {
            const data = await api.getChatMessages(1);
            if (data.messages && data.messages.length > 0) {
                // Clear welcome message if history exists
                chatMessages.innerHTML = '';

                data.messages.forEach(msg => {
                    addMessage(msg.content, msg.role === 'user' ? 'user' : 'ai', false);
                });
            }
        } catch (err) {
            console.error('Error loading chat history:', err);
        }
    }

    // Send user message
    async function sendMessage(text) {
        if (isLoading) return;

        isLoading = true;
        sendBtn.disabled = true;

        // Add user message
        addMessage(text, 'user');

        // Remove suggestions if present
        document.querySelector('.quick-suggestions')?.remove();

        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await api.sendChatMessage(text);
            hideTypingIndicator();

            if (response.assistant_message) {
                addMessage(response.assistant_message.content, 'ai');
            }
        } catch (err) {
            hideTypingIndicator();
            console.error('Error sending message:', err);
            addMessage('⚠️ Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.', 'ai');
        } finally {
            isLoading = false;
            sendBtn.disabled = false;
        }
    }

    // Add message to chat
    function addMessage(text, sender, scroll = true) {
        const messageGroup = document.createElement('div');
        messageGroup.className = `message-group ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'ai'
            ? '<i class="fas fa-robot"></i>'
            : '<span>U</span>';

        const content = document.createElement('div');
        content.className = 'message-content';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = formatMessage(text);

        const time = document.createElement('span');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit'
        });

        content.appendChild(bubble);
        content.appendChild(time);
        messageGroup.appendChild(avatar);
        messageGroup.appendChild(content);

        chatMessages.appendChild(messageGroup);

        if (scroll) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Format message with HTML
    function formatMessage(text) {
        // Convert line breaks
        text = text.replace(/\n/g, '<br>');

        // Make numbers bold
        text = text.replace(/\$[\d,]+\.?\d*/g, '<strong>$&</strong>');

        // Make emojis bigger
        text = text.replace(/([\u{1F300}-\u{1F9FF}])/gu, '<span style="font-size: 1.2em;">$1</span>');

        return text;
    }

    // Voice input (Real Web Speech API)
    let isRecording = false;
    let recognition = null;

    // Initialize Speech Recognition if available
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false; // Stop after one sentence
        recognition.interimResults = true; // Show results while speaking
        recognition.lang = 'es-ES'; // Default to Spanish

        recognition.onstart = () => {
            isRecording = true;
            voiceBtn.classList.add('recording');
            voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
            chatInput.placeholder = 'Escuchando...';
        };

        recognition.onend = () => {
            isRecording = false;
            voiceBtn.classList.remove('recording');
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            chatInput.placeholder = 'Escribe tu mensaje aquí...';
        };

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            // Update input with current transcript
            chatInput.value = finalTranscript || interimTranscript;

            // Auto resize
            chatInput.style.height = 'auto';
            chatInput.style.height = chatInput.scrollHeight + 'px';

            // Enable send button if we have text
            sendBtn.disabled = !chatInput.value.trim();
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            isRecording = false;
            voiceBtn.classList.remove('recording');
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';

            let errorMessage = 'Error de reconocimiento de voz.';
            if (event.error === 'no-speech') {
                errorMessage = 'No se detectó voz. Intenta de nuevo.';
            } else if (event.error === 'not-allowed') {
                errorMessage = 'Permiso de micrófono denegado.';
            } else if (event.error === 'network') {
                errorMessage = 'Error de red. Verifica tu conexión.';
            }

            alert(errorMessage);
        };
    } else {
        console.warn('Speech Recognition API not supported in this browser.');
        voiceBtn.style.display = 'none'; // Hide button if not supported
    }

    voiceBtn.addEventListener('click', () => {
        if (!recognition) {
            alert('Tu navegador no soporta reconocimiento de voz. Por favor usa Chrome, Edge o Safari.');
            return;
        }

        if (isRecording) {
            recognition.stop();
        } else {
            // Start recording
            try {
                recognition.start();
            } catch (e) {
                console.error('Error starting recognition:', e);
                // If it fails (e.g. already started), try to stop and restart or just reset
                recognition.stop();
            }
        }
    });

    // Show typing indicator
    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message-group ai-message typing-indicator-group';
        indicator.id = 'typingIndicator';
        indicator.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Hide typing indicator
    function hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Función para navegar por el historial de mensajes
    function navigateHistory(direction) {
        if (messageHistory.length === 0) return;

        if (direction === 'up') {
            // Si estamos en el último índice, guardar el borrador actual
            if (historyIndex === messageHistory.length) {
                currentDraft = chatInput.value;
            }

            // Navegar hacia atrás (mensajes más antiguos)
            if (historyIndex > 0) {
                historyIndex--;
                chatInput.value = messageHistory[historyIndex];
            }
        } else if (direction === 'down') {
            // Navegar hacia adelante (mensajes más recientes)
            if (historyIndex < messageHistory.length - 1) {
                historyIndex++;
                chatInput.value = messageHistory[historyIndex];
            } else if (historyIndex === messageHistory.length - 1) {
                // Volver al borrador actual
                historyIndex = messageHistory.length;
                chatInput.value = currentDraft;
            }
        }

        // Auto-resize textarea después de cambiar el contenido
        chatInput.style.height = 'auto';
        chatInput.style.height = chatInput.scrollHeight + 'px';

        // Actualizar estado del botón enviar
        sendBtn.disabled = chatInput.value.trim() === '' || isLoading;
    }

    // New chat button
    const newChatBtn = document.querySelector('.btn-new-chat');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', async () => {
            if (confirm('¿Limpiar el historial de chat?')) {
                try {
                    await api.clearChatHistory();

                    // Limpiar historial de navegación
                    messageHistory = [];
                    historyIndex = -1;
                    currentDraft = '';

                    chatMessages.innerHTML = `
                        <div class="message-group ai-message">
                            <div class="message-avatar">
                                <i class="fas fa-robot"></i>
                            </div>
                            <div class="message-content">
                                <div class="message-bubble">
                                    <p>¡Hola! Soy tu asistente financiero. Puedo ayudarte a registrar gastos, consultar tu balance, darte consejos de ahorro y más.</p>
                                    <p>Solo háblame naturalmente, por ejemplo: <em>"Gasté 50.000 en supermercado"</em> o <em>"¿Cuánto llevo gastado este mes?"</em></p>
                                </div>
                            </div>
                        </div>
                    `;
                } catch (err) {
                    console.error('Error clearing chat:', err);
                    alert('No se pudo limpiar el historial');
                }
            }
        });
    }

    // Initial setup
    sendBtn.disabled = true;
});
