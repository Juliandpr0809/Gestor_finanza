// ==========================================
// UX IMPROVEMENTS - JavaScript Utilities
// Funciones para mejorar la experiencia visual
// ==========================================

/**
 * Sistema de categorías con iconos
 */
const CATEGORY_ICONS = {
    // Gastos
    'food': '🍔',
    'dining': '🍽️',
    'groceries': '🛒',
    'transport': '🚗',
    'gas': '⛽',
    'taxi': '🚕',
    'services': '📱',
    'utilities': '💡',
    'internet': '🌐',
    'entertainment': '🎮',
    'movies': '🎬',
    'music': '🎵',
    'health': '💊',
    'medical': '🏥',
    'fitness': '💪',
    'shopping': '🛍️',
    'clothes': '👕',
    'bills': '📄',
    'rent': '🏠',
    'insurance': '🛡️',
    'education': '📚',
    'travel': '✈️',
    'pets': '🐾',
    'gifts': '🎁',
    'donations': '❤️',
    
    // Ingresos
    'salary': '💰',
    'income': '💵',
    'freelance': '💼',
    'investment': '📈',
    'refund': '↩️',
    'bonus': '🎉',
    
    // Por defecto
    'other': '📦',
    'expense': '💸',
    'default': '💳'
};

/**
 * Obtener icono de categoría
 */
function getCategoryIcon(category, type = 'expense') {
    const categoryLower = (category || '').toLowerCase().trim();
    
    // Buscar coincidencias parciales
    for (const [key, icon] of Object.entries(CATEGORY_ICONS)) {
        if (categoryLower.includes(key) || key.includes(categoryLower)) {
            return icon;
        }
    }
    
    // Por defecto según tipo
    return type === 'income' ? CATEGORY_ICONS.income : CATEGORY_ICONS.expense;
}

/**
 * Obtener clase de color de categoría
 */
function getCategoryColorClass(category) {
    const categoryLower = (category || '').toLowerCase();
    
    if (categoryLower.includes('food') || categoryLower.includes('comida') || categoryLower.includes('restaur')) {
        return 'food';
    }
    if (categoryLower.includes('transport') || categoryLower.includes('taxi') || categoryLower.includes('gas')) {
        return 'transport';
    }
    if (categoryLower.includes('service') || categoryLower.includes('util') || categoryLower.includes('internet')) {
        return 'services';
    }
    if (categoryLower.includes('entertain') || categoryLower.includes('movie') || categoryLower.includes('game')) {
        return 'entertainment';
    }
    if (categoryLower.includes('health') || categoryLower.includes('medical') || categoryLower.includes('salud')) {
        return 'health';
    }
    if (categoryLower.includes('shop') || categoryLower.includes('cloth') || categoryLower.includes('compra')) {
        return 'shopping';
    }
    if (categoryLower.includes('bill') || categoryLower.includes('factura') || categoryLower.includes('rent')) {
        return 'bills';
    }
    if (categoryLower.includes('income') || categoryLower.includes('salary') || categoryLower.includes('ingreso')) {
        return 'income';
    }
    
    return 'other';
}

/**
 * Crear elemento de icono de categoría
 */
function createCategoryIcon(category, type = 'expense') {
    const icon = getCategoryIcon(category, type);
    const colorClass = getCategoryColorClass(category);
    
    return `
        <div class="category-icon ${colorClass}" title="${category}">
            ${icon}
        </div>
    `;
}

/**
 * Agrupar transacciones por fecha
 */
function groupTransactionsByDate(transactions) {
    const grouped = {};
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    transactions.forEach(tx => {
        const txDate = new Date(tx.date);
        txDate.setHours(0, 0, 0, 0);
        
        let dateLabel;
        if (txDate.getTime() === today.getTime()) {
            dateLabel = 'Hoy';
        } else if (txDate.getTime() === yesterday.getTime()) {
            dateLabel = 'Ayer';
        } else {
            dateLabel = txDate.toLocaleDateString('es-ES', { 
                weekday: 'long', 
                day: 'numeric', 
                month: 'long' 
            });
        }
        
        if (!grouped[dateLabel]) {
            grouped[dateLabel] = {
                date: txDate,
                label: dateLabel,
                transactions: [],
                total: 0
            };
        }
        
        grouped[dateLabel].transactions.push(tx);
        grouped[dateLabel].total += parseFloat(tx.amount || 0);
    });
    
    return Object.values(grouped).sort((a, b) => b.date - a.date);
}

/**
 * Crear HTML de grupo de transacciones por fecha
 */
function createDateGroupHTML(group) {
    const totalClass = group.total >= 0 ? 'positive' : 'negative';
    const totalFormatted = formatCurrency(Math.abs(group.total));
    const totalSign = group.total >= 0 ? '+' : '-';
    
    const transactionsHTML = group.transactions
        .map(tx => createTransactionRowHTML(tx))
        .join('');
    
    return `
        <div class="transaction-date-group">
            <div class="date-group-header">
                <span>${group.label}</span>
                <span class="date-group-total ${totalClass}">
                    ${totalSign}${totalFormatted}
                </span>
            </div>
            <div class="transaction-list-grouped">
                ${transactionsHTML}
            </div>
        </div>
    `;
}

/**
 * Crear chips de filtros rápidos
 */
function createQuickFiltersHTML() {
    return `
        <div class="quick-filters">
            <div class="filter-chip active" data-filter="all">
                <i class="fas fa-list"></i>
                <span data-i18n="All">Todos</span>
            </div>
            <div class="filter-chip" data-filter="today">
                <i class="fas fa-calendar-day"></i>
                <span data-i18n="Today">Hoy</span>
            </div>
            <div class="filter-chip" data-filter="week">
                <i class="fas fa-calendar-week"></i>
                <span data-i18n="This Week">Esta Semana</span>
            </div>
            <div class="filter-chip" data-filter="month">
                <i class="fas fa-calendar"></i>
                <span data-i18n="This Month">Este Mes</span>
            </div>
            <div class="filter-chip" data-filter="high">
                <i class="fas fa-exclamation-triangle"></i>
                <span data-i18n="High Amounts">Montos Altos</span>
            </div>
            <div class="filter-chip" data-filter="income">
                <i class="fas fa-arrow-down"></i>
                <span data-i18n="Income">Ingresos</span>
            </div>
            <div class="filter-chip" data-filter="expense">
                <i class="fas fa-arrow-up"></i>
                <span data-i18n="Expenses">Gastos</span>
            </div>
        </div>
    `;
}

/**
 * Inicializar event listeners de filtros rápidos
 */
function initQuickFilters(onFilterChange) {
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.addEventListener('click', function() {
            // Toggle active state
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            
            // Trigger callback
            const filter = this.dataset.filter;
            if (onFilterChange) {
                onFilterChange(filter);
            }
        });
    });
}

/**
 * Crear indicador de uso de crédito
 */
function createCreditUsageIndicator(currentBalance, creditLimit) {
    const used = Math.abs(currentBalance);
    const percentage = (used / creditLimit) * 100;
    
    let usageClass = 'low';
    if (percentage > 70) usageClass = 'high';
    else if (percentage > 40) usageClass = 'medium';
    
    return `
        <div class="credit-usage-indicator">
            <div class="usage-label">
                <span data-i18n="Credit Used">Crédito Usado</span>
                <span class="usage-percentage">${percentage.toFixed(0)}%</span>
            </div>
            <div class="usage-bar">
                <div class="usage-fill ${usageClass}" style="width: ${percentage}%"></div>
            </div>
            <div class="credit-limit">
                ${formatCurrency(used)} / ${formatCurrency(creditLimit)}
            </div>
        </div>
    `;
}

/**
 * Animar cambios en números
 */
function animateNumberChange(element, newValue, duration = 500) {
    const oldValue = parseFloat(element.textContent.replace(/[^0-9.-]/g, '')) || 0;
    const diff = newValue - oldValue;
    const steps = 30;
    const stepValue = diff / steps;
    const stepDuration = duration / steps;
    
    let current = oldValue;
    let step = 0;
    
    element.classList.add('updating');
    
    const interval = setInterval(() => {
        step++;
        current += stepValue;
        
        if (step >= steps) {
            current = newValue;
            clearInterval(interval);
            element.classList.remove('updating');
        }
        
        element.textContent = formatCurrency(current);
    }, stepDuration);
}

/**
 * Formatear moneda
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * Crear tooltip
 */
function createTooltip(content) {
    return `
        <div class="tooltip-wrapper">
            <i class="fas fa-info-circle" style="color: rgba(255,255,255,0.5); font-size: 12px;"></i>
            <div class="tooltip-content">${content}</div>
        </div>
    `;
}

/**
 * Mostrar estado vacío
 */
function showEmptyState(container, config = {}) {
    const {
        icon = '📭',
        title = 'No hay datos',
        description = 'Comienza agregando tu primera transacción',
        actionText = 'Agregar Transacción',
        actionUrl = '#'
    } = config;
    
    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">${icon}</div>
            <div class="empty-state-title">${title}</div>
            <div class="empty-state-description">${description}</div>
            <button class="empty-state-action" onclick="window.location.href='${actionUrl}'">
                ${actionText}
            </button>
        </div>
    `;
}

/**
 * Crear skeleton loader
 */
function createSkeletonLoader(type = 'card', count = 3) {
    let html = '';
    for (let i = 0; i < count; i++) {
        if (type === 'card') {
            html += '<div class="skeleton skeleton-card"></div>';
        } else if (type === 'text') {
            html += '<div class="skeleton skeleton-text"></div>';
        }
    }
    return html;
}

// Exportar funciones
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getCategoryIcon,
        getCategoryColorClass,
        createCategoryIcon,
        groupTransactionsByDate,
        createDateGroupHTML,
        createQuickFiltersHTML,
        initQuickFilters,
        createCreditUsageIndicator,
        animateNumberChange,
        formatCurrency,
        createTooltip,
        showEmptyState,
        createSkeletonLoader
    };
}
