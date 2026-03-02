// ==========================================
// TRANSACTIONS PAGE - BACKEND CONNECTED
// Incluye mejoras UX: agrupación por fecha, filtros rápidos, iconos
// ==========================================

let transactions = [];
let filteredTransactions = [];
let currentPage = 1;
const itemsPerPage = 10;
let currentSort = { field: 'date', direction: 'desc' };
let editingTransactionId = null;
let accountsMap = {};
let categoriesMap = {};
let currentQuickFilter = 'all'; // Para filtros rápidos
let accountIdFilter = null; // Para filtrar por cuenta desde URL

document.addEventListener('DOMContentLoaded', () => {
    // La autenticación es manejada por auth-handler.js

    // Verificar si hay un filtro de cuenta en la URL
    const urlParams = new URLSearchParams(window.location.search);
    const accountIdFromUrl = urlParams.get('account');
    if (accountIdFromUrl) {
        accountIdFilter = parseInt(accountIdFromUrl);
        console.log('📌 Se filtrará por cuenta ID:', accountIdFilter);
    }

    // Solo necesitamos cargar los datos
    loadInitialData();
    setupEventListeners();
});

// ==========================================
// DATA LOADING
// ==========================================

async function loadInitialData() {
    try {
        console.log('=== INICIO CARGA DE TRANSACCIONES ===');

        // Cargar datos en paralelo
        const [accountsData, categoriesData, transactionsData] = await Promise.all([
            api.getAccounts(),
            api.getCategories(),
            api.getTransactions({ per_page: 100 })
        ]);

        console.log('✅ Cuentas recibidas:', accountsData);
        console.log('✅ Categorías recibidas:', categoriesData);
        console.log('✅ Transacciones recibidas:', transactionsData);

        // Procesar cuentas
        accountsMap = {};
        const accountsList = accountsData?.accounts || accountsData || [];
        accountsList.forEach(a => {
            accountsMap[a.id] = a.name;
        });
        console.log('📁 Mapa de cuentas:', accountsMap);

        // Procesar categorías
        categoriesMap = {};
        const categoriesList = categoriesData?.categories || categoriesData || [];
        categoriesList.forEach(c => {
            categoriesMap[c.id] = {
                name: c.name,
                icon: c.icon || '📌',
                type: c.category_type || c.type
            };
        });
        console.log('📁 Mapa de categorías:', categoriesMap);

        // Extraer transacciones - el backend devuelve { transactions: [...], pagination: {...} }
        let txList = [];

        if (transactionsData && transactionsData.transactions) {
            txList = transactionsData.transactions;
            console.log('📊 Transacciones extraídas del objeto:', txList.length);
        } else if (Array.isArray(transactionsData)) {
            txList = transactionsData;
            console.log('📊 Transacciones extraídas como array:', txList.length);
        } else {
            console.error('❌ Formato de transacciones no reconocido:', transactionsData);
        }

        // Mapear transacciones
        transactions = txList.map(t => {
            const mapped = {
                id: t.id,
                date: t.date,
                name: t.description || t.category_name || 'Sin nombre',
                description: t.description || '',
                category: t.category_id,
                categoryName: t.category_name || 'Sin categoría',
                categoryIcon: t.category_icon || categoriesMap[t.category_id]?.icon || '📌',
                account: t.account_id,
                accountName: t.account_name || accountsMap[t.account_id] || 'Sin cuenta',
                accountCurrency: t.account_currency || accountsMap[t.account_id]?.currency || 'USD',
                type: t.type,
                amount: t.amount || 0,
                status: 'completed'
            };
            return mapped;
        });

        console.log('✅ Transacciones procesadas:', transactions.length);
        console.log('📋 Primera transacción:', transactions[0]);

        filteredTransactions = [...transactions];
        console.log('📋 Filtered transactions copiadas:', filteredTransactions.length);

        console.log('🎯 Llamando a updateSummary()');
        updateSummary();

        console.log('🎯 Llamando a populateFilterDropdowns()');
        populateFilterDropdowns();

        // Si hay un filtro de cuenta desde la URL, aplicarlo ahora
        if (accountIdFilter) {
            console.log('🔍 Aplicando filtro de cuenta:', accountIdFilter);
            const accountSelect = document.getElementById('filterAccount');
            if (accountSelect) {
                const accountName = accountsMap[accountIdFilter];
                console.log('👉 Nombre de cuenta:', accountName);
                if (accountName) {
                    accountSelect.value = accountName;
                    console.log('✅ Select actualizado a:', accountName);
                }
            }
        }

        console.log('🎯 Llamando a applyFilters()');
        applyFilters();

        console.log('=== FIN CARGA DE DATOS ===');

    } catch (err) {
        console.error('❌ ERROR cargando datos:', err);
        console.error('Stack:', err.stack);
        alert('No se pudieron cargar las transacciones: ' + err.message);
    }
}

function updateSummary() {
    console.log('📊 updateSummary() - transactions:', transactions.length);
    // Agrupar por moneda para el resumen
    const summaryByCurrency = {};

    transactions.forEach(t => {
        const cur = t.accountCurrency || 'USD';
        if (!summaryByCurrency[cur]) summaryByCurrency[cur] = { income: 0, expense: 0 };

        if (t.type === 'income') summaryByCurrency[cur].income += Math.abs(t.amount);
        else if (t.type === 'expense') summaryByCurrency[cur].expense += Math.abs(t.amount);
    });

    // Por ahora mostramos solo la moneda principal o la primera encontrada
    // Idealmente deberíamos mostrar un desglose
    const toggleCurrency = localStorage.getItem('selectedCurrency') || 'COP';
    const mainSummary = summaryByCurrency[toggleCurrency] || { income: 0, expense: 0 };

    // Si no hay datos en la moneda seleccionada, tratar de convertir (PENDIENTE: Implementar conversión real)
    // Por simplicidad, si no hay datos en la moneda seleccionada, mostramos 'USD' si existe, o la primera que haya

    const income = mainSummary.income;
    const expenses = mainSummary.expense;
    const balance = income - expenses;

    const incomeEl = document.querySelector('.summary-card:nth-child(1) .summary-value');
    const expenseEl = document.querySelector('.summary-card:nth-child(2) .summary-value');
    const balanceEl = document.querySelector('.summary-card:nth-child(3) .summary-value');

    if (incomeEl) incomeEl.textContent = formatCurrencyTx(income, toggleCurrency);
    if (expenseEl) expenseEl.textContent = formatCurrencyTx(expenses, toggleCurrency);
    if (balanceEl) balanceEl.textContent = formatCurrencyTx(balance, toggleCurrency);
}

function populateFilterDropdowns() {
    const categorySelect = document.getElementById('filterCategory');
    const accountSelect = document.getElementById('filterAccount');

    if (categorySelect) {
        const firstOpt = categorySelect.options[0];
        categorySelect.innerHTML = '';
        categorySelect.appendChild(firstOpt);
        const cats = [...new Set(transactions.map(t => t.categoryName))].filter(Boolean).sort();
        cats.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            categorySelect.appendChild(opt);
        });
    }

    if (accountSelect) {
        const firstOpt = accountSelect.options[0];
        accountSelect.innerHTML = '';
        accountSelect.appendChild(firstOpt);
        Object.entries(accountsMap).forEach(([id, name]) => {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = name;
            accountSelect.appendChild(opt);
        });
    }

    populateEditModalDropdowns();
}

function populateEditModalDropdowns() {
    const editAccountSel = document.getElementById('editAccount');
    if (editAccountSel) {
        editAccountSel.innerHTML = '';
        Object.entries(accountsMap).forEach(([id, name]) => {
            const opt = document.createElement('option');
            opt.value = id;
            opt.textContent = name;
            editAccountSel.appendChild(opt);
        });
    }
    const editCategorySel = document.getElementById('editCategory');
    if (editCategorySel) {
        editCategorySel.innerHTML = '';
        Object.entries(categoriesMap).forEach(([id, cat]) => {
            const opt = document.createElement('option');
            opt.value = id;
            opt.textContent = cat.name;
            editCategorySel.appendChild(opt);
        });
        if (editCategorySel.options.length === 0) {
            const defaults = [
                ['food', 'Comida'], ['transport', 'Transporte'], ['entertainment', 'Entretenimiento'],
                ['shopping', 'Compras'], ['bills', 'Facturas'], ['health', 'Salud'],
                ['salary', 'Salario'], ['freelance', 'Freelance'], ['other', 'Otro']
            ];
            defaults.forEach(([val, label]) => {
                const opt = document.createElement('option');
                opt.value = val; opt.textContent = label;
                editCategorySel.appendChild(opt);
            });
        }
    }
}

// ==========================================
// HELPERS
// ==========================================

const ensureAuth = (err) => {
    if (err?.message?.includes('401') || err?.message?.includes('Unauthorized')) {
        window.location.href = '/frontend/html/login.html';
        return true;
    }
    return false;
};

const formatCurrencyTx = (amount, currency = 'USD') => {
    try {
        return new Intl.NumberFormat('es-CO', { style: 'currency', currency: currency }).format(amount || 0);
    } catch (_) {
        return `${currency} ${(amount || 0).toFixed(2)}`;
    }
};

const formatDate = (iso) => {
    try {
        const d = new Date(iso);
        // Formato: "3 ene, 00:45" o simplemente "3 ene" si en el mismo día
        const now = new Date();
        const isToday = d.getDate() === now.getDate() &&
            d.getMonth() === now.getMonth() &&
            d.getFullYear() === now.getFullYear();

        if (isToday) {
            // Si es hoy, mostrar solo la hora
            return d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
        } else {
            // Mostrar fecha y hora
            return d.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' }) +
                ' ' + d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
        }
    } catch (_) {
        return iso;
    }
};

// Filtrar por categoría
function filterByCategory(categoryName) {
    const filterEl = document.getElementById('filterCategory');
    if (filterEl) {
        filterEl.value = categoryName;
        applyFilters();
        // Scroll a la tabla
        setTimeout(() => {
            document.querySelector('.content-panel')?.scrollIntoView({ behavior: 'smooth' });
        }, 300);
    }
}

// ==========================================
// RENDERING
// ==========================================

// Renderizar resumen por categorías
function renderCategorySummary() {
    const container = document.getElementById('categorySummaryGrid');
    if (!container) return;

    // Agrupar transacciones por categoría
    const categoryMap = {};
    filteredTransactions.forEach(t => {
        const catId = t.category;
        const catName = t.categoryName || 'Sin categoría';
        const catIcon = t.categoryIcon || '📌';
        const catType = t.type || 'expense';

        if (!categoryMap[catId]) {
            categoryMap[catId] = {
                id: catId,
                name: catName,
                icon: catIcon,
                type: catType,
                total: 0,
                count: 0,
                transactions: []
            };
        }
        categoryMap[catId].total += Math.abs(t.amount || 0);
        categoryMap[catId].count += 1;
        categoryMap[catId].transactions.push(t);
    });

    const categories = Object.values(categoryMap).sort((a, b) => b.total - a.total);

    if (categories.length === 0) {
        container.innerHTML = `
            <div class="category-empty">
                <div class="category-empty-icon">📊</div>
                <div class="category-empty-text">No hay transacciones para mostrar</div>
                <div style="font-size: 12px; color: #666;">Crea tu primera transacción para verla aquí</div>
            </div>
        `;
        return;
    }

    container.innerHTML = categories.map(cat => {
        const currency = (filteredTransactions.find(t => t.category === cat.id)?.accountCurrency) || 'USD'; 
        const isExpense = cat.type === 'expense';
        const typeLabel = isExpense ? 'Gastos' : 'Ingresos';
        const formattedAmount = formatCurrencyTx(cat.total, currency);
        
        // Convertir nombre de clase FontAwesome a icono
        const iconHtml = cat.icon.startsWith('fa-') 
            ? `<i class="fas ${cat.icon}"></i>` 
            : cat.icon;
        
        return `
            <div class="category-card ${cat.type}" data-category-id="${cat.id}">
                <div class="category-card-header">
                    <div class="category-icon">${iconHtml}</div>
                    <div class="category-name">
                        <span class="category-title">${cat.name}</span>
                        <span class="category-type">${typeLabel}</span>
                    </div>
                    <span class="category-count">${cat.count}</span>
                </div>
                
                <div class="category-card-body">
                    <div class="category-total">
                        ${formattedAmount}
                    </div>
                    <div class="category-trend ${isExpense ? 'negative' : ''}">
                        <i class="fas fa-arrow-${isExpense ? 'down' : 'up'}"></i>
                        ${cat.count} transacción${cat.count !== 1 ? 'es' : ''}
                    </div>
                </div>
                
                <div class="category-card-footer">
                    <div class="category-actions">
                        <button class="category-btn-small" onclick="filterByCategory('${cat.name}')">
                            <i class="fas fa-filter"></i> Filtrar
                        </button>
                    </div>
                    <a class="category-view-all" onclick="filterByCategory('${cat.name}')">
                        Ver detalles →
                    </a>
                </div>
            </div>
        `;
    }).join('');
}

function renderTransactions() {
    console.log('=== RENDERIZANDO TRANSACCIONES ===');
    console.log('Filtered transactions:', filteredTransactions.length);
    console.log('Current page:', currentPage);
    console.log('Items per page:', itemsPerPage);

    const tbody = document.getElementById('transactionsBody');
    if (!tbody) {
        console.error('ERROR: No se encontró el elemento transactionsBody');
        return;
    }

    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageTransactions = filteredTransactions.slice(start, end);

    console.log('Transacciones de la página actual:', pageTransactions.length);

    if (!pageTransactions.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-gray" style="padding: 40px;">Sin transacciones</td></tr>';
    } else {
        tbody.innerHTML = pageTransactions.map(t => {
            // Icono de categoría con emojis y color (usa helpers de ux-improvements.js)
            const categoryLabel = t.categoryName || t.category || 'Sin categoría';
            const categoryType = t.type === 'income' ? 'income' : 'expense';
            const categoryIconEl = (typeof createCategoryIcon === 'function')
                ? createCategoryIcon(categoryLabel, categoryType)
                : `<div class="table-icon-circle ${t.type === 'income' ? 'bg-work' : 'bg-grocery'}"><i class="fas fa-${t.amount > 0 ? 'arrow-down' : 'shopping-bag'}"></i></div>`;

            const amountColor = t.type === 'income' ? 'text-green' : 'text-white';
            const amountPrefix = t.type === 'income' ? '+' : '-';

            return `
            <tr>
                <td>
                    ${categoryIconEl}
                </td>
                <td>
                    <div class="fw-500 text-white">${t.name || 'Transacción'}</div>
                    <div class="text-gray" style="font-size: 11px;">${t.description || t.accountName || ''}</div>
                </td>
                <td class="text-gray">${formatDate(t.date)}</td>
                <td>
                    <span class="badge-gray">${categoryLabel}</span>
                </td>
                <td class="text-right">
                    <span class="fw-600 ${amountColor}">
                        ${amountPrefix}${formatCurrencyTx(Math.abs(t.amount), t.accountCurrency)}
                    </span>
                </td>
                <td class="text-center">
                    <div style="display: flex; justify-content: flex-end; gap: 8px;">
                         <button class="btn-icon-tiny" onclick="editTransaction(${t.id})" title="Edit">
                            <i class="fas fa-pen" style="font-size: 12px;"></i>
                        </button>
                         <button class="btn-icon-tiny" onclick="deleteTransaction(${t.id})" title="Delete">
                            <i class="fas fa-trash-alt" style="font-size: 12px;"></i>
                        </button>
                    </div>
                </td>
            </tr>`;
        }).join('');
    }

    updatePagination();
}

function updatePagination() {
    const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage);
    const start = (filteredTransactions.length === 0) ? 0 : (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(start + itemsPerPage - 1, filteredTransactions.length);

    // Update info text (if visible)
    const showingStartEl = document.getElementById('showingStart');
    if (showingStartEl) showingStartEl.textContent = start;
    const showingEndEl = document.getElementById('showingEnd');
    if (showingEndEl) showingEndEl.textContent = end;
    const totalTransactionsEl = document.getElementById('totalTransactions');
    if (totalTransactionsEl) totalTransactionsEl.textContent = filteredTransactions.length;

    // Update page buttons
    const btnPrev = document.getElementById('btnPrevPage');
    const btnNext = document.getElementById('btnNextPage');
    if (btnPrev) btnPrev.disabled = currentPage === 1;
    if (btnNext) btnNext.disabled = currentPage === totalPages || totalPages === 0;

    // Render page numbers
    const pageNumbers = document.getElementById('pageNumbers');
    if (pageNumbers) {
        pageNumbers.innerHTML = '';

        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
                const btn = document.createElement('button');
                btn.className = `btn-page-clean ${i === currentPage ? 'active' : ''}`;
                btn.textContent = i;
                btn.onclick = () => goToPage(i);
                pageNumbers.appendChild(btn);
            } else if (i === currentPage - 2 || i === currentPage + 2) {
                const span = document.createElement('span');
                span.textContent = '...';
                span.style.color = '#8E8E93';
                span.style.padding = '0 4px';
                span.style.display = 'flex';
                span.style.alignItems = 'center';
                pageNumbers.appendChild(span);
            }
        }
    }
}

// ==========================================
// FILTERING & SORTING
// ==========================================

function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const filterType = document.getElementById('filterType');
    const filterCategory = document.getElementById('filterCategory');
    const filterAccount = document.getElementById('filterAccount');
    const filterDateFrom = document.getElementById('filterDateFrom');
    const filterDateTo = document.getElementById('filterDateTo');

    [searchInput, filterType, filterCategory, filterAccount, filterDateFrom, filterDateTo].forEach(el => {
        if (el) {
            el.addEventListener('change', applyFilters);
            if (el.tagName === 'INPUT' && el.type === 'text') {
                el.addEventListener('input', applyFilters);
            }
        }
    });

    const btnPrev = document.getElementById('btnPrevPage');
    const btnNext = document.getElementById('btnNextPage');
    if (btnPrev) btnPrev.onclick = prevPage;
    if (btnNext) btnNext.onclick = nextPage;
}

function initializeFilters() {
    setupEventListeners();
}

function applyFilters() {
    const searchInput = document.getElementById('searchInput');
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';

    const filterType = document.getElementById('filterType');
    const typeFilter = filterType ? filterType.value : '';

    const filterCategory = document.getElementById('filterCategory');
    const categoryFilter = filterCategory ? filterCategory.value : '';

    const filterAccount = document.getElementById('filterAccount');
    const accountFilter = filterAccount ? filterAccount.value : '';

    const filterDateFrom = document.getElementById('filterDateFrom');
    const dateFrom = filterDateFrom ? filterDateFrom.value : '';

    const filterDateTo = document.getElementById('filterDateTo');
    const dateTo = filterDateTo ? filterDateTo.value : '';

    filteredTransactions = transactions.filter(t => {
        const matchesSearch = !searchTerm ||
            (t.name && t.name.toLowerCase().includes(searchTerm)) ||
            (t.description && t.description.toLowerCase().includes(searchTerm)) ||
            (t.categoryName && t.categoryName.toLowerCase().includes(searchTerm));

        const matchesType = !typeFilter || t.type === typeFilter;
        const matchesCategory = !categoryFilter || t.categoryName === categoryFilter;
        const matchesAccount = !accountFilter || t.accountName === accountFilter;
        const matchesDateFrom = !dateFrom || t.date >= dateFrom;
        const matchesDateTo = !dateTo || t.date <= dateTo;

        return matchesSearch && matchesType && matchesCategory && matchesAccount && matchesDateFrom && matchesDateTo;
    });

    currentPage = 1;
    applySorting();
    renderCategorySummary();
    renderTransactions();
}

function clearFilters() {
    const ids = ['searchInput', 'filterType', 'filterCategory', 'filterAccount', 'filterDateFrom', 'filterDateTo'];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });

    applyFilters();
}

function applySorting() {
    filteredTransactions.sort((a, b) => {
        let aVal = a[currentSort.field];
        let bVal = b[currentSort.field];

        if (currentSort.field === 'amount') {
            aVal = Math.abs(aVal);
            bVal = Math.abs(bVal);
        }

        if (aVal < bVal) return currentSort.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return currentSort.direction === 'asc' ? 1 : -1;
        return 0;
    });
}

function sortTable(field) {
    if (currentSort.field === field) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.field = field;
        currentSort.direction = 'desc';
    }

    applySorting();
    renderTransactions();
}

// ==========================================
// PAGINATION
// ==========================================

function goToPage(page) {
    currentPage = page;
    renderTransactions();
}

function nextPage() {
    const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        renderTransactions();
    }
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        renderTransactions();
    }
}

// ==========================================
// CRUD OPERATIONS
// ==========================================

window.editTransaction = async function (id) {
    const tx = transactions.find(t => t.id === id);
    if (!tx) { alert('Transacción no encontrada'); return; }

    editingTransactionId = id;

    const editType = document.getElementById('editType');
    const editAmount = document.getElementById('editAmount');
    const editDate = document.getElementById('editDate');
    const editCategory = document.getElementById('editCategory');
    const editDescription = document.getElementById('editDescription');
    const editAccount = document.getElementById('editAccount');

    if (editType) editType.value = tx.type || 'expense';
    if (editAmount) editAmount.value = Math.abs(tx.amount || 0);
    if (editDate) editDate.value = tx.date ? tx.date.substring(0, 10) : '';
    if (editDescription) editDescription.value = tx.description || tx.name || '';

    if (editCategory) {
        const byId = editCategory.querySelector(`option[value="${tx.category}"]`);
        if (byId) editCategory.value = tx.category;
        else {
            const byName = [...editCategory.options].find(o => o.textContent === tx.categoryName);
            if (byName) editCategory.value = byName.value;
        }
    }
    if (editAccount && tx.account) editAccount.value = String(tx.account);

    const modal = document.getElementById('editModal');
    if (modal) modal.classList.remove('hidden');

    const editForm = document.getElementById('editForm');
    if (editForm) editForm.onsubmit = async (e) => { e.preventDefault(); await saveEditTransaction(); };
};

async function saveEditTransaction() {
    if (!editingTransactionId) return;
    const payload = {
        type: document.getElementById('editType')?.value,
        amount: parseFloat(document.getElementById('editAmount')?.value) || 0,
        date: document.getElementById('editDate')?.value,
        category_id: parseInt(document.getElementById('editCategory')?.value) || null,
        description: document.getElementById('editDescription')?.value?.trim(),
        account_id: parseInt(document.getElementById('editAccount')?.value) || null,
    };
    if (!payload.type || !payload.amount || !payload.date) { alert('Completa tipo, monto y fecha'); return; }

    const submitBtn = document.querySelector('#editForm button[type="submit"]');
    if (submitBtn) { submitBtn.disabled = true; submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...'; }

    try {
        await api.updateTransaction(editingTransactionId, payload);
        closeEditModal();
        await loadInitialData();
    } catch (err) {
        console.error('Error guardando transacción:', err);
        if (ensureAuth(err)) return;
        alert('No se pudo guardar: ' + err.message);
    } finally {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = '<i class="fas fa-save"></i> <span>Guardar Cambios</span>'; }
    }
}

window.closeEditModal = function () {
    const modal = document.getElementById('editModal');
    if (modal) modal.classList.add('hidden');
    editingTransactionId = null;
};

document.addEventListener('keydown', (e) => { if (e.key === 'Escape') window.closeEditModal?.(); });

window.deleteTransaction = async function (id) {
    if (!confirm('¿Eliminar esta transacción?')) return;
    try {
        await api.deleteTransaction(id);
        await loadInitialData();
    } catch (err) {
        console.error('Error eliminando transacción:', err);
        if (ensureAuth(err)) return;
        alert('No se pudo eliminar la transacción');
    }
};

// ==========================================
// UX IMPROVEMENTS - Filtros Rápidos y Agrupación
// ==========================================

/**
 * Aplicar filtro rápido
 */
function applyQuickFilter(filter) {
    currentQuickFilter = filter;
    const now = new Date();

    filteredTransactions = [...transactions];

    switch (filter) {
        case 'today':
            filteredTransactions = filteredTransactions.filter(t => {
                const txDate = new Date(t.date);
                return txDate.toDateString() === now.toDateString();
            });
            break;

        case 'week':
            const weekAgo = new Date(now);
            weekAgo.setDate(weekAgo.getDate() - 7);
            filteredTransactions = filteredTransactions.filter(t => {
                const txDate = new Date(t.date);
                return txDate >= weekAgo;
            });
            break;

        case 'month':
            filteredTransactions = filteredTransactions.filter(t => {
                const txDate = new Date(t.date);
                return txDate.getMonth() === now.getMonth() &&
                    txDate.getFullYear() === now.getFullYear();
            });
            break;

        case 'high':
            const avgAmount = transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0) / transactions.length;
            filteredTransactions = filteredTransactions.filter(t => Math.abs(t.amount) > avgAmount * 2);
            break;

        case 'income':
            filteredTransactions = filteredTransactions.filter(t => t.type === 'income');
            break;

        case 'expense':
            filteredTransactions = filteredTransactions.filter(t => t.type === 'expense');
            break;

        case 'all':
        default:
            // Ya tenemos todas las transacciones
            break;
    }

    currentPage = 1;
    updateSummary();
    renderTransactions();
}

/**
 * Obtener icono de categoría basado en nombre
 */
function getCategoryIcon(categoryName, type) {
    if (!categoryName) {
        return type === 'income' ? '💰' : '💸';
    }

    const catLower = categoryName.toLowerCase();

    // Mapeo de categorías a emojis
    const iconMap = {
        'food': '🍔', 'comida': '🍔', 'restaurante': '🍽️',
        'transport': '🚗', 'transporte': '🚗', 'taxi': '🚕', 'gasolina': '⛽',
        'services': '📱', 'servicios': '📱', 'utilities': '💡', 'internet': '🌐',
        'entertainment': '🎮', 'entretenimiento': '🎮', 'movies': '🎬',
        'health': '💊', 'salud': '💊', 'medical': '🏥',
        'shopping': '🛍️', 'compras': '🛍️',
        'bills': '📄', 'facturas': '📄', 'rent': '🏠',
        'salary': '💰', 'salario': '💰', 'income': '💵', 'ingreso': '💵'
    };

    for (const [key, icon] of Object.entries(iconMap)) {
        if (catLower.includes(key)) {
            return icon;
        }
    }

    return type === 'income' ? '💵' : '💳';
}

/**
 * Obtener clase de color de categoría
 */
function getCategoryColorClass(categoryName) {
    if (!categoryName) return 'other';

    const catLower = categoryName.toLowerCase();

    if (catLower.includes('food') || catLower.includes('comida')) return 'food';
    if (catLower.includes('transport') || catLower.includes('transporte')) return 'transport';
    if (catLower.includes('service') || catLower.includes('servicio')) return 'services';
    if (catLower.includes('entertain') || catLower.includes('entretenimiento')) return 'entertainment';
    if (catLower.includes('health') || catLower.includes('salud')) return 'health';
    if (catLower.includes('shop') || catLower.includes('compra')) return 'shopping';
    if (catLower.includes('bill') || catLower.includes('factura')) return 'bills';
    if (catLower.includes('income') || catLower.includes('ingreso') || catLower.includes('salary')) return 'income';

    return 'other';
}

// ==========================================
// CURRENCY SELECTOR
// ==========================================
function initCurrencySelector() {
    const currencyValue = document.getElementById('currencyValue');
    const currencyDropdown = document.getElementById('currencyDropdown');
    const currencyOptions = document.querySelectorAll('.currency-option');

    if (!currencyValue || !currencyDropdown) return;

    // Cargar moneda guardada
    const savedCurrency = localStorage.getItem('selectedCurrency') || 'COP';
    currencyValue.textContent = savedCurrency;

    // Marcar opción activa
    currencyOptions.forEach(opt => {
        opt.classList.toggle('active', opt.dataset.currency === savedCurrency);
    });

    // Toggle dropdown
    currencyValue.addEventListener('click', (e) => {
        e.stopPropagation();
        currencyDropdown.classList.toggle('show');
    });

    // Seleccionar moneda
    currencyOptions.forEach(option => {
        option.addEventListener('click', (e) => {
            e.stopPropagation();
            const currency = option.dataset.currency;
            localStorage.setItem('selectedCurrency', currency);
            currencyValue.textContent = currency;

            // Actualizar activo
            currencyOptions.forEach(opt => opt.classList.remove('active'));
            option.classList.add('active');

            currencyDropdown.classList.remove('show');

            // Recargar datos
            loadInitialData();
        });
    });

    // Cerrar al hacer clic fuera
    document.addEventListener('click', () => {
        currencyDropdown.classList.remove('show');
    });
}

initCurrencySelector();
