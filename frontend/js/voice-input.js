// ==========================================
// VOICE INPUT - SPEECH RECOGNITION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const voiceButton = document.getElementById('voiceButton');
    const statusIndicator = document.getElementById('statusIndicator');
    const transcriptDisplay = document.getElementById('transcriptDisplay');
    const transcriptText = document.getElementById('transcriptText');
    const audioWaves = document.getElementById('audioWaves');
    const processingSection = document.getElementById('processingSection');
    const transactionPreview = document.getElementById('transactionPreview');
    const languageSelect = document.getElementById('languageSelect');
    const commandChips = document.querySelectorAll('.command-chip');
    const transactionForm = document.getElementById('transactionForm');
    const cancelBtn = document.getElementById('cancelBtn');
    const retryBtn = document.getElementById('retryBtn');

    // Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isRecording = false;

    // Initialize Speech Recognition if available
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = languageSelect.value;
    }

    // Voice button click
    voiceButton.addEventListener('click', () => {
        if (!recognition) {
            alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
            return;
        }

        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    // Start recording
    function startRecording() {
        isRecording = true;
        voiceButton.classList.add('recording');
        voiceButton.innerHTML = '<i class="fas fa-stop"></i>';
        audioWaves.classList.remove('hidden');
        
        statusIndicator.classList.add('listening');
        statusIndicator.innerHTML = '<i class="fas fa-microphone"></i><span>Listening...</span>';

        transcriptDisplay.classList.add('hidden');
        transcriptText.textContent = '';

        try {
            recognition.start();
        } catch (error) {
            console.error('Recognition error:', error);
            resetRecording();
        }
    }

    // Stop recording
    function stopRecording() {
        isRecording = false;
        voiceButton.classList.remove('recording');
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        audioWaves.classList.add('hidden');
        
        statusIndicator.classList.remove('listening');
        statusIndicator.innerHTML = '<i class="fas fa-check-circle"></i><span>Processing...</span>';

        if (recognition) {
            recognition.stop();
        }
    }

    // Reset recording state
    function resetRecording() {
        isRecording = false;
        voiceButton.classList.remove('recording');
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        audioWaves.classList.add('hidden');
        
        statusIndicator.classList.remove('listening');
        statusIndicator.innerHTML = '<i class="fas fa-microphone-slash"></i><span>Tap to start speaking</span>';
    }

    // Speech Recognition Events
    if (recognition) {
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

            // Display transcript
            const displayText = finalTranscript || interimTranscript;
            if (displayText) {
                transcriptDisplay.classList.remove('hidden');
                transcriptText.textContent = displayText;
            }

            // If final result, process it
            if (finalTranscript) {
                processVoiceInput(finalTranscript);
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            resetRecording();
            
            if (event.error === 'no-speech') {
                statusIndicator.innerHTML = '<i class="fas fa-exclamation-circle"></i><span>No speech detected</span>';
            } else if (event.error === 'not-allowed') {
                statusIndicator.innerHTML = '<i class="fas fa-microphone-slash"></i><span>Microphone access denied</span>';
            } else {
                statusIndicator.innerHTML = '<i class="fas fa-exclamation-circle"></i><span>Error: ' + event.error + '</span>';
            }

            setTimeout(resetRecording, 3000);
        };

        recognition.onend = () => {
            if (isRecording) {
                resetRecording();
            }
        };
    }

    // Language change
    languageSelect.addEventListener('change', (e) => {
        if (recognition) {
            recognition.lang = e.target.value;
        }
    });

    // Quick command chips
    commandChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const command = chip.dataset.command;
            transcriptDisplay.classList.remove('hidden');
            transcriptText.textContent = command;
            processVoiceInput(command);
        });
    });

    // Process voice input with AI
    function processVoiceInput(text) {
        // Hide main section
        document.querySelector('.voice-main-section').style.display = 'none';
        
        // Show processing
        processingSection.classList.remove('hidden');
        
        // Simulate AI processing steps
        simulateProcessing(text);
    }

    // Simulate AI processing
    function simulateProcessing(text) {
        const steps = [
            { id: 'step1', delay: 500 },
            { id: 'step2', delay: 1500 },
            { id: 'step3', delay: 2500 },
            { id: 'step4', delay: 3500 }
        ];

        steps.forEach((step, index) => {
            setTimeout(() => {
                const stepElement = document.getElementById(step.id);
                stepElement.classList.add('active');
                
                // Update status icon
                const statusIcon = stepElement.querySelector('.step-status i');
                if (index < steps.length - 1) {
                    statusIcon.className = 'fas fa-spinner fa-spin';
                    setTimeout(() => {
                        statusIcon.className = 'fas fa-check-circle';
                        stepElement.classList.add('completed');
                    }, 800);
                } else {
                    statusIcon.className = 'fas fa-check-circle';
                    stepElement.classList.add('completed');
                }
            }, step.delay);
        });

        // Show transaction preview after processing
        setTimeout(() => {
            processingSection.classList.add('hidden');
            transactionPreview.classList.remove('hidden');
            fillTransactionData(text);
        }, 4500);
    }

    // Fill transaction data from voice input
    function fillTransactionData(text) {
        const lowerText = text.toLowerCase();
        
        // Extract amount (look for numbers with $ or "dollars")
        let amount = 0;
        const amountMatch = text.match(/\$?(\d+(?:\.\d{2})?)/);
        if (amountMatch) {
            amount = parseFloat(amountMatch[1]);
        }

        // Detect category based on keywords
        let category = 'other';
        let description = text;

        if (lowerText.includes('coffee') || lowerText.includes('restaurant') || lowerText.includes('dinner') || lowerText.includes('lunch')) {
            category = 'food';
        } else if (lowerText.includes('groceries') || lowerText.includes('supermarket') || lowerText.includes('whole foods')) {
            category = 'groceries';
        } else if (lowerText.includes('gas') || lowerText.includes('uber') || lowerText.includes('taxi')) {
            category = 'transport';
        } else if (lowerText.includes('shopping') || lowerText.includes('clothes') || lowerText.includes('amazon')) {
            category = 'shopping';
        } else if (lowerText.includes('movie') || lowerText.includes('netflix') || lowerText.includes('spotify')) {
            category = 'entertainment';
        } else if (lowerText.includes('pharmacy') || lowerText.includes('doctor') || lowerText.includes('medicine')) {
            category = 'health';
        }

        // Clean up description
        description = text.replace(/\$?\d+(?:\.\d{2})?/, '').replace(/dollars?/gi, '').trim();
        if (!description) {
            description = getCategoryDescription(category);
        }

        // Fill form
        document.getElementById('description').value = capitalizeFirst(description);
        document.getElementById('amount').value = amount.toFixed(2);
        document.getElementById('date').value = new Date().toISOString().split('T')[0];
        document.getElementById('category').value = category;
        document.getElementById('account').value = 'main';
        
        // Set original transcript
        document.getElementById('originalTranscript').textContent = text;

        // Calculate confidence (random between 85-98%)
        const confidence = Math.floor(Math.random() * 13) + 85;
        document.getElementById('confidenceScore').innerHTML = `
            <i class="fas fa-shield-check"></i>
            ${confidence}% Confidence
        `;
    }

    // Helper functions
    function capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    function getCategoryDescription(category) {
        const descriptions = {
            food: 'Food & Dining',
            groceries: 'Grocery Shopping',
            transport: 'Transportation',
            shopping: 'Shopping',
            entertainment: 'Entertainment',
            health: 'Health & Wellness',
            other: 'Miscellaneous Expense'
        };
        return descriptions[category] || descriptions.other;
    }

    // Cancel button
    cancelBtn.addEventListener('click', () => {
        resetToMainScreen();
    });

    // Retry button
    retryBtn.addEventListener('click', () => {
        resetToMainScreen();
        setTimeout(() => {
            startRecording();
        }, 300);
    });

    // Reset to main screen
    function resetToMainScreen() {
        transactionPreview.classList.add('hidden');
        processingSection.classList.add('hidden');
        document.querySelector('.voice-main-section').style.display = 'block';
        
        // Reset processing steps
        document.querySelectorAll('.process-step').forEach(step => {
            step.classList.remove('active', 'completed');
            const statusIcon = step.querySelector('.step-status i');
            statusIcon.className = 'fas fa-circle';
        });
        
        // Reset first step
        document.getElementById('step1').querySelector('.step-status i').className = 'fas fa-spinner fa-spin';
        
        resetRecording();
        transcriptDisplay.classList.add('hidden');
        transactionForm.reset();
    }

    // Form submission
    transactionForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const formData = {
            description: document.getElementById('description').value,
            amount: parseFloat(document.getElementById('amount').value),
            date: document.getElementById('date').value,
            category: document.getElementById('category').value,
            account: document.getElementById('account').value,
            notes: document.getElementById('notes').value
        };

        console.log('Saving transaction:', formData);
        alert('✅ Transaction saved successfully!');
        resetToMainScreen();
    });

    // Settings button (placeholder)
    document.getElementById('settingsBtn').addEventListener('click', () => {
        alert('⚙️ Voice Settings\n\n• Adjust microphone sensitivity\n• Choose voice language\n• Enable auto-save\n• Customize categories\n\nComing soon!');
    });

    // Replay buttons (placeholder)
    document.querySelectorAll('.btn-replay').forEach(btn => {
        btn.addEventListener('click', () => {
            alert('🔊 Audio playback feature coming soon!\n\nThis will replay your original voice recording.');
        });
    });
});
