/**
 * TRANSACTION CONFIRMATION COMPONENT
 * Componente JavaScript para confirmación visual de transacciones
 * Compatible con la mejora de IA (ai_service_improved.py)
 */

class TransactionConfirmationComponent {
    constructor(container) {
        this.container = container || document.querySelector('.chat-messages');
        this.currentConfirmation = null;
        this.onConfirm = null;
        this.onCancel = null;
    }

    /**
     * Crea y muestra el componente de confirmación
     * @param {Object} transactionData - Datos de la transacción a confirmar
     * @param {Function} onConfirmCallback - Callback al confirmar
     * @param {Function} onCancelCallback - Callback al cancelar
     */
    show(transactionData, onConfirmCallback, onCancelCallback) {
        // Limpiar confirmación anterior si existe
        this.hide();

        // Guardar callbacks
        this.onConfirm = onConfirmCallback;
        this.onCancel = onCancelCallback;

        // Crear componente
        const confirmationHTML = this.createConfirmationHTML(transactionData);
        
        // Insertar en el contenedor
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = confirmationHTML;
        this.currentConfirmation = tempDiv.firstElementChild;
        
        // Agregar al chat
        this.container.appendChild(this.currentConfirmation);
        
        // Scroll hasta el componente
        this.currentConfirmation.scrollIntoView({ behavior: 'smooth', block: 'end' });
        
        // Agregar event listeners
        this.attachEventListeners();
    }

    /**
     * Genera el HTML del componente de confirmación
     * @param {Object} data - Datos de la transacción
     */
    createConfirmationHTML(data) {
        const {
            amount,
            type = 'expense',
            currency = 'COP',
            account,
            category,
            description = '',
            date = new Date().toLocaleDateString('es-ES')
        } = data;

        // Formatear monto
        const formattedAmount = this.formatAmount(amount, type, currency);
        
        // Seleccionar icono según tipo
        const icon = type === 'income' ? 'fa-arrow-down' : 
                     type === 'expense' ? 'fa-arrow-up' : 'fa-exchange-alt';

        return `
            <div class="transaction-confirmation" data-type="${type}">
                <div class="confirmation-header">
                    <div class="confirmation-icon">
                        <i class="fas ${icon}"></i>
                    </div>
                    <h4 class="confirmation-title">Confirmar transacción</h4>
                </div>

                <div class="confirmation-content">
                    <div class="confirmation-amount ${type}">
                        ${formattedAmount}
                    </div>

                    <div class="confirmation-details">
                        ${account ? `
                            <div class="confirmation-detail-item">
                                <i class="fas fa-wallet"></i>
                                <span>Cuenta:</span>
                                <span class="confirmation-detail-value">${account}</span>
                            </div>
                        ` : ''}
                        
                        ${category ? `
                            <div class="confirmation-detail-item">
                                <i class="fas fa-tag"></i>
                                <span>Categoría:</span>
                                <span class="confirmation-detail-value">${category}</span>
                            </div>
                        ` : ''}
                        
                        ${description ? `
                            <div class="confirmation-detail-item">
                                <i class="fas fa-comment"></i>
                                <span>Descripción:</span>
                                <span class="confirmation-detail-value">${description}</span>
                            </div>
                        ` : ''}
                        
                        <div class="confirmation-detail-item">
                            <i class="fas fa-calendar"></i>
                            <span>Fecha:</span>
                            <span class="confirmation-detail-value">${date}</span>
                        </div>
                    </div>
                </div>

                <div class="confirmation-checkbox-area" data-checked="false">
                    <div class="confirmation-checkbox">
                        <input type="checkbox" id="confirm-checkbox" style="display: none;">
                        <div class="custom-checkbox"></div>
                        <label for="confirm-checkbox" class="checkbox-label">
                            Confirmo que los datos son correctos
                        </label>
                    </div>
                </div>

                <div class="confirmation-actions">
                    <button class="btn-confirm" disabled>
                        <i class="fas fa-check"></i>
                        <span>Confirmar</span>
                    </button>
                    <button class="btn-cancel">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Adjunta event listeners al componente
     */
    attachEventListeners() {
        if (!this.currentConfirmation) return;

        const checkboxArea = this.currentConfirmation.querySelector('.confirmation-checkbox-area');
        const customCheckbox = this.currentConfirmation.querySelector('.custom-checkbox');
        const confirmBtn = this.currentConfirmation.querySelector('.btn-confirm');
        const cancelBtn = this.currentConfirmation.querySelector('.btn-cancel');

        // Toggle checkbox al hacer click en el área
        checkboxArea.addEventListener('click', (e) => {
            e.preventDefault();
            const isChecked = checkboxArea.dataset.checked === 'true';
            const newChecked = !isChecked;
            
            checkboxArea.dataset.checked = newChecked;
            checkboxArea.classList.toggle('active', newChecked);
            customCheckbox.classList.toggle('checked', newChecked);
            confirmBtn.disabled = !newChecked;
        });

        // Confirmar transacción
        confirmBtn.addEventListener('click', async () => {
            if (confirmBtn.disabled) return;
            
            // Mostrar loading
            confirmBtn.classList.add('loading');
            confirmBtn.innerHTML = '<i class="fas fa-spinner"></i><span>Guardando...</span>';
            
            try {
                if (this.onConfirm) {
                    await this.onConfirm();
                }
                
                // Mostrar éxito
                this.showSuccess();
                
            } catch (error) {
                console.error('Error al confirmar transacción:', error);
                this.showError();
                confirmBtn.classList.remove('loading');
                confirmBtn.innerHTML = '<i class="fas fa-check"></i><span>Confirmar</span>';
            }
        });

        // Cancelar
        cancelBtn.addEventListener('click', () => {
            if (this.onCancel) {
                this.onCancel();
            }
            this.hide();
        });
    }

    /**
     * Muestra estado de éxito
     */
    showSuccess() {
        if (!this.currentConfirmation) return;
        
        this.currentConfirmation.classList.add('success');
        const confirmBtn = this.currentConfirmation.querySelector('.btn-confirm');
        confirmBtn.classList.remove('loading');
        confirmBtn.innerHTML = '<i class="fas fa-check-circle"></i><span>¡Guardado!</span>';
        
        // Ocultar después de 1.5 segundos
        setTimeout(() => {
            this.hide();
        }, 1500);
    }

    /**
     * Muestra estado de error
     */
    showError() {
        if (!this.currentConfirmation) return;
        
        this.currentConfirmation.classList.add('error');
        const confirmBtn = this.currentConfirmation.querySelector('.btn-confirm');
        confirmBtn.innerHTML = '<i class="fas fa-exclamation-circle"></i><span>Error</span>';
    }

    /**
     * Oculta y remueve el componente
     */
    hide() {
        if (this.currentConfirmation) {
            this.currentConfirmation.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                if (this.currentConfirmation && this.currentConfirmation.parentNode) {
                    this.currentConfirmation.parentNode.removeChild(this.currentConfirmation);
                }
                this.currentConfirmation = null;
            }, 300);
        }
    }

    /**
     * Formatea el monto según el tipo de transacción
     * @param {Number} amount - Monto
     * @param {String} type - Tipo (expense/income)
     * @param {String} currency - Moneda de la cuenta
     */
    formatAmount(amount, type, currency = 'COP') {
        const prefix = type === 'expense' ? '-' : '+';
        const safeCurrency = (currency || 'COP').toUpperCase();
        const formatted = new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: safeCurrency,
            minimumFractionDigits: 2
        }).format(Math.abs(amount));
        
        return `${prefix} ${formatted}`;
    }
}

// Animación de slideOut
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-10px);
        }
    }
`;
document.head.appendChild(style);

// Exportar para uso global
window.TransactionConfirmationComponent = TransactionConfirmationComponent;
