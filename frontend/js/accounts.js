document.addEventListener('DOMContentLoaded', () => {
    // La autenticación es manejada por auth-handler.js

    // Elements
    const btnAddAccount = document.getElementById('btnAddAccount');
    const accountModal = document.getElementById('accountModal');
    const accountForm = document.getElementById('accountForm');
    const accountTypeSelect = document.getElementById('accountType');
    const creditLimitGroup = document.querySelector('.credit-limit-group');
    const savingsGoalGroup = document.querySelector('.savings-goal-group');
    const filterTabs = document.querySelectorAll('.tab-btn');
    const accountsGrid = document.getElementById('accountsGrid');

    let accountsCache = [];
    let editingAccountId = null;

    // ==========================================
    // HELPERS
    // ==========================================

    let preferredCurrency = localStorage.getItem('preferredCurrency');

    const formatMoney = (amount, currency = 'USD') => {
        try {
            return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount);
        } catch (_) {
            return `${currency} ${amount.toFixed(2)}`;
        }
    };

    const setLoadingBtn = (btn, text) => {
        const original = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i><span>${text}</span>`;
        return () => {
            btn.disabled = false;
            btn.innerHTML = original;
        };
    };

    const ensureAuth = (err) => {
        if (err?.message?.includes('401') || err?.message?.includes('Unauthorized')) {
            window.location.href = '/frontend/html/login.html';
            return true;
        }
        return false;
    };

    // Generar indicador de uso de crédito (UX Improvement)
    const generateCreditUsageIndicator = (acc) => {
        if (acc.account_type !== 'credit' || !acc.credit_limit) {
            return '';
        }

        const used = Math.abs(acc.current_balance || 0);
        const limit = acc.credit_limit;
        const percentage = Math.min(100, (used / limit) * 100);

        let usageClass = 'low';
        if (percentage > 70) usageClass = 'high';
        else if (percentage > 40) usageClass = 'medium';

        return `
            <div class="credit-usage-indicator" style="margin-top: 12px;">
                <div class="usage-label">
                    <span style="font-size: 11px; color: rgba(255,255,255,0.5);">Crédito Usado</span>
                    <span class="usage-percentage" style="font-size: 11px; font-weight: 600;">${percentage.toFixed(0)}%</span>
                </div>
                <div class="usage-bar" style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; margin-top: 4px; overflow: hidden;">
                    <div class="usage-fill ${usageClass}" style="width: ${percentage}%; height: 100%; border-radius: 3px; transition: width 0.3s ease;"></div>
                </div>
                <div class="credit-limit" style="font-size: 10px; color: rgba(255,255,255,0.4); margin-top: 4px;">
                    ${formatMoney(used)} / ${formatMoney(limit)}
                </div>
            </div>
        `;
    };

    // ==========================================
    // LOAD & RENDER ACCOUNTS
    // ==========================================

    async function loadAccounts() {
        accountsGrid.innerHTML = '<p class="empty-text">Cargando cuentas...</p>';
        try {
            const data = await api.getAccounts();
            accountsCache = data;
            if (!preferredCurrency && accountsCache.length && accountsCache[0].currency) {
                preferredCurrency = accountsCache[0].currency;
                localStorage.setItem('preferredCurrency', preferredCurrency);
            }
            renderAccounts(data);
            updateFilters(data);
            updateSummary(data);
        } catch (err) {
            console.error('Error al cargar cuentas:', err);
            if (ensureAuth(err)) return;
            accountsGrid.innerHTML = '<p class="empty-text">No se pudieron cargar las cuentas.</p>';
            alert(`No se pudieron cargar las cuentas: ${err.message}`);
        }
    }

    function renderAccounts(accounts) {
        accountsGrid.innerHTML = '';
        if (!accounts.length) {
            accountsGrid.innerHTML = '<p class="empty-text">Aún no tienes cuentas. Crea la primera.</p>';
            return;
        }

        accounts.forEach((acc, index) => {
            const card = document.createElement('div');
            card.className = 'account-card';
            card.dataset.type = acc.account_type;
            card.style.animation = `fadeInUp 0.5s ease ${index * 0.05}s both`;

            const badgeClass = acc.account_type === 'savings' ? 'savings' : acc.account_type === 'credit' ? 'credit' : 'checking';
            const balanceClass = acc.current_balance < 0 ? 'negative' : '';

            card.innerHTML = `
                <div class="account-card-header">
                    <div class="account-type-badge ${badgeClass}">
                        <i class="fas ${badgeClass === 'credit' ? 'fa-credit-card' : badgeClass === 'savings' ? 'fa-piggy-bank' : 'fa-university'}"></i>
                        ${acc.account_type || 'account'}
                    </div>
                    <div class="account-actions">
                        <button class="btn-action" onclick="editAccount(${acc.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-action" onclick="deleteAccount(${acc.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="account-card-body">
                    <div class="account-name">${acc.name}</div>
                    <div class="account-number">${acc.currency || 'USD'}</div>
                    <div class="account-balance ${balanceClass}">${formatMoney(acc.current_balance || 0, acc.currency || 'USD')}</div>
                    <div class="account-bank">
                        <i class="fas fa-building"></i>
                        ${acc.account_type}
                    </div>
                    ${generateCreditUsageIndicator(acc)}
                </div>
                <div class="account-card-footer">
                    <div class="account-status ${acc.is_active ? 'active' : 'inactive'}">
                        <i class="fas fa-circle"></i>
                        ${acc.is_active ? 'Active' : 'Inactive'}
                    </div>
                    <button class="btn-view-transactions" onclick="viewTransactions(${acc.id})">
                        Ver movimientos
                        <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            `;
            accountsGrid.appendChild(card);
        });
    }

    function updateFilters(accounts) {
        const counts = accounts.reduce((acc, item) => {
            acc[item.account_type] = (acc[item.account_type] || 0) + 1;
            acc.all = (acc.all || 0) + 1;
            return acc;
        }, {});

        filterTabs.forEach(tab => {
            const filter = tab.dataset.filter;
            const countSpan = tab.querySelector('.tab-count');
            if (filter === 'all') {
                countSpan.textContent = counts.all || 0;
            } else {
                countSpan.textContent = counts[filter] || 0;
            }
        });
    }

    // ==========================================
    // SUMMARY (cabecera y tarjetas)
    // ==========================================

    function updateSummary(accounts) {
        const totalBalance = accounts.reduce((sum, a) => sum + (a.current_balance || 0), 0);
        const displayCurrency = preferredCurrency || accounts[0]?.currency || 'USD';
        const checkingCount = accounts.filter(a => a.account_type === 'checking').length;
        const savingsCount = accounts.filter(a => a.account_type === 'savings').length;
        const creditCount = accounts.filter(a => a.account_type === 'credit').length;

        const headerBalanceEl = document.querySelector('.header-balance-amount');
        if (headerBalanceEl) headerBalanceEl.textContent = formatMoney(totalBalance);

        const summaryCards = document.querySelectorAll('.summary-card');
        if (summaryCards[0]) {
            const val = summaryCards[0].querySelector('.summary-value');
            if (val) val.textContent = formatMoney(totalBalance, displayCurrency);
        }
        if (summaryCards[1]) {
            const val = summaryCards[1].querySelector('.summary-value');
            const subtitle = summaryCards[1].querySelector('.summary-subtitle');
            if (val) val.textContent = String(checkingCount + savingsCount);
            if (subtitle) subtitle.textContent = `${checkingCount} checking, ${savingsCount} savings`;
        }
        if (summaryCards[2]) {
            const val = summaryCards[2].querySelector('.summary-value');
            if (val) val.textContent = String(creditCount);
        }
        if (summaryCards[3]) {
            const val = summaryCards[3].querySelector('.summary-value');
                if (val) val.textContent = formatMoney(0, displayCurrency);
        }
    }

    // ==========================================
    // FILTER TABS
    // ==========================================

    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const filter = tab.dataset.filter;
            const accountCards = accountsGrid.querySelectorAll('.account-card');

            accountCards.forEach(card => {
                if (filter === 'all' || card.dataset.type === filter) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // ==========================================
    // ACCOUNT TYPE CHANGE
    // ==========================================

    accountTypeSelect.addEventListener('change', (e) => {
        const type = e.target.value;

        if (type === 'credit') {
            creditLimitGroup.classList.remove('hidden');
            savingsGoalGroup.classList.add('hidden');
        } else if (type === 'savings') {
            savingsGoalGroup.classList.remove('hidden');
            creditLimitGroup.classList.add('hidden');
        } else {
            creditLimitGroup.classList.add('hidden');
            savingsGoalGroup.classList.add('hidden');
        }
    });

    // ==========================================
    // OPEN ADD ACCOUNT MODAL
    // ==========================================

    btnAddAccount.addEventListener('click', () => {
        editingAccountId = null;
        document.getElementById('modalTitle').textContent = 'Add New Account';
        accountForm.reset();
        creditLimitGroup.classList.add('hidden');
        savingsGoalGroup.classList.add('hidden');
        accountModal.classList.remove('hidden');
    });

    // ==========================================
    // EDIT ACCOUNT (solo front de momento)
    // ==========================================

    window.editAccount = function (accountId) {
        const acc = accountsCache.find(a => a.id === accountId);
        if (!acc) return;

        editingAccountId = accountId;
        document.getElementById('modalTitle').textContent = 'Edit Account';

        document.getElementById('accountName').value = acc.name || '';
        document.getElementById('accountType').value = acc.account_type || '';
        document.getElementById('accountCurrency').value = acc.currency || 'COP';
        // Prefill balance using current_balance fallback to initial_balance
        const balanceInput = document.getElementById('accountBalance');
        if (balanceInput) balanceInput.value = (acc.current_balance ?? acc.initial_balance ?? 0);

        // Optional fields: keep previous values if exist in data
        const bankInput = document.getElementById('accountBank');
        if (bankInput) bankInput.value = acc.bank || '';

        const numberInput = document.getElementById('accountNumber');
        if (numberInput) numberInput.value = acc.account_number || '';

        const creditLimitInput = document.getElementById('creditLimit');
        if (creditLimitInput) creditLimitInput.value = acc.credit_limit || '';

        const savingsGoalInput = document.getElementById('savingsGoal');
        if (savingsGoalInput) savingsGoalInput.value = acc.savings_goal || '';

        if (acc.account_type === 'credit') {
            creditLimitGroup.classList.remove('hidden');
        } else if (acc.account_type === 'savings') {
            savingsGoalGroup.classList.remove('hidden');
        }

        accountModal.classList.remove('hidden');
    };

    // ==========================================
    // DELETE ACCOUNT
    // ==========================================

    window.deleteAccount = async function (accountId) {
        const acc = accountsCache.find(a => a.id === accountId);
        if (!acc) return;

        if (!confirm(`¿Seguro que deseas eliminar "${acc.name}"?`)) return;

        try {
            await api.deleteAccount(accountId);
            await loadAccounts();
            alert('Cuenta eliminada');
        } catch (err) {
            console.error('Error al eliminar cuenta:', err);
            if (ensureAuth(err)) return;
            alert(`No se pudo eliminar: ${err.message}`);
        }
    };

    // ==========================================
    // VIEW TRANSACTIONS
    // ==========================================

    window.viewTransactions = function (accountId) {
        window.location.href = `transactions.html?account=${accountId}`;
    };

    // ==========================================
    // CLOSE MODAL
    // ==========================================

    window.closeModal = function () {
        accountModal.classList.add('hidden');
        accountForm.reset();
        editingAccountId = null;
    };

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !accountModal.classList.contains('hidden')) {
            closeModal();
        }
    });

    // ==========================================
    // FORM SUBMISSION
    // ==========================================

    accountForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const balanceVal = parseFloat(document.getElementById('accountBalance').value) || 0;
        const payload = {
            name: document.getElementById('accountName').value.trim(),
            account_type: document.getElementById('accountType').value,
            currency: document.getElementById('accountCurrency').value,
            initial_balance: balanceVal,
            current_balance: balanceVal,
        };

        if (!payload.name || !payload.account_type) {
            alert('Completa nombre y tipo de cuenta');
            return;
        }

        const submitBtn = accountForm.querySelector('button[type="submit"]');
        const resetLoading = setLoadingBtn(submitBtn, editingAccountId ? 'Actualizando...' : 'Guardando...');

        try {
            if (editingAccountId) {
                await api.updateAccount(editingAccountId, payload);
            } else {
                await api.createAccount(payload);
            }
            await loadAccounts();
            closeModal();
        } catch (err) {
            console.error('Error guardando cuenta:', err);
            if (ensureAuth(err)) return;
            alert(`No se pudo guardar la cuenta: ${err.message}`);
        } finally {
            resetLoading();
        }
    });

    // ==========================================
    // INITIAL LOAD
    // ==========================================

    loadAccounts();
});

// Animations CSS injection (se mantiene)
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeOut {
        from { opacity: 1; transform: scale(1); }
        to { opacity: 0; transform: scale(0.9); }
    }
`;
document.head.appendChild(style);

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
            if (typeof loadAccounts === 'function') {
                loadAccounts();
            }
        });
    });

    // Cerrar al hacer clic fuera
    document.addEventListener('click', () => {
        currencyDropdown.classList.remove('show');
    });
}

initCurrencySelector();
