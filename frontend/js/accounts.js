document.addEventListener('DOMContentLoaded', () => {
    // La autenticación es manejada por auth-handler.js

    // Elements
    const btnAddAccount = document.getElementById('btnAddAccount');
    const accountModal = document.getElementById('accountModal');
    const accountForm = document.getElementById('accountForm');
    const accountTypeSelect = document.getElementById('accountType');
    const creditLimitGroup = document.querySelector('.credit-limit-group');
    const savingsGoalGroup = document.querySelector('.savings-goal-group');
    const accountTypeFilter = document.getElementById('accountTypeFilter');
    const accountsSortBtn = document.getElementById('accountsSortBtn');
    const accountsGrid = document.getElementById('accountsGrid');
    const accountActionSheet = document.getElementById('accountActionSheet');
    const actionSheetOverlay = document.getElementById('actionSheetOverlay');
    const actionEdit = document.getElementById('actionEdit');
    const actionDelete = document.getElementById('actionDelete');
    const accountDetailModal = document.getElementById('accountDetailModal');
    const btnDeleteFromModal = document.getElementById('btnDeleteFromModal');
    const accountBalanceInput = document.getElementById('accountBalance');
    const accountCurrencySelect = document.getElementById('accountCurrency');
    const modalBalancePreview = document.getElementById('modalBalancePreview');

    let accountsCache = [];
    let editingAccountId = null;
    let selectedAccountId = null;
    let sortAscending = false;

    // ==========================================
    // HELPERS
    // ==========================================

    let preferredCurrency = localStorage.getItem('preferredCurrency');

    const formatMoney = (amount, currency = 'USD') => {
        try {
            return new Intl.NumberFormat('es-CO', { style: 'currency', currency }).format(amount);
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
            <div class="credit-usage-indicator" style="margin-top: 8px;">
                <div class="usage-label">
                    <span style="font-size: 10px; color: rgba(255,255,255,0.5);">Crédito usado</span>
                    <span class="usage-percentage" style="font-size: 10px; font-weight: 600;">${percentage.toFixed(0)}%</span>
                </div>
                <div class="usage-bar" style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 3px; overflow: hidden;">
                    <div class="usage-fill ${usageClass}" style="width: ${percentage}%; height: 100%; border-radius: 2px; transition: width 0.3s ease;"></div>
                </div>
                <div class="credit-limit" style="font-size: 9px; color: rgba(255,255,255,0.4); margin-top: 3px;">
                    ${formatMoney(used, acc.currency || 'COP')} / ${formatMoney(limit, acc.currency || 'COP')}
                </div>
            </div>
        `;
    };

    const updateModalBalancePreview = () => {
        if (!modalBalancePreview || !accountBalanceInput || !accountCurrencySelect) return;
        const amount = parseFloat(accountBalanceInput.value) || 0;
        const currency = accountCurrencySelect.value || preferredCurrency || 'COP';
        modalBalancePreview.textContent = formatMoney(amount, currency);
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
            updateFilters(data);
            updateSummary(data);
            refreshAccountsView();
        } catch (err) {
            console.error('Error al cargar cuentas:', err);
            if (ensureAuth(err)) return;
            accountsGrid.innerHTML = '<p class="empty-text">No se pudieron cargar las cuentas.</p>';
            alert(`No se pudieron cargar las cuentas: ${err.message}`);
        }
    }

    function getTypeLabel(type) {
        if (type === 'checking') return 'Corriente';
        if (type === 'savings') return 'Ahorros';
        if (type === 'credit') return 'Crédito';
        if (type === 'cash') return 'Efectivo';
        return 'Cuenta';
    }

    function getTypeIcon(type) {
        if (type === 'credit') return 'fa-credit-card';
        if (type === 'savings') return 'fa-piggy-bank';
        if (type === 'cash') return 'fa-dollar-sign';
        if (type === 'checking') return 'fa-university';
        return 'fa-wallet';
    }

    function getFilteredAndSortedAccounts() {
        const selectedFilter = accountTypeFilter?.value || 'all';
        const filtered = selectedFilter === 'all'
            ? [...accountsCache]
            : accountsCache.filter(acc => acc.account_type === selectedFilter);

        filtered.sort((left, right) => {
            const leftBalance = left.current_balance || 0;
            const rightBalance = right.current_balance || 0;
            return sortAscending ? leftBalance - rightBalance : rightBalance - leftBalance;
        });

        return filtered;
    }

    function refreshAccountsView() {
        renderAccounts(getFilteredAndSortedAccounts());
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

            const balanceClass = acc.current_balance < 0 ? 'negative' : '';
            const typeLabel = getTypeLabel(acc.account_type);
            const typeIcon = getTypeIcon(acc.account_type);

            card.innerHTML = `
                <div class="account-leading-icon">
                    <i class="fas ${typeIcon}"></i>
                </div>

                <div class="account-content">
                    <div class="account-main-row">
                        <div class="account-name">${acc.name}</div>
                        <div class="account-balance ${balanceClass}">${formatMoney(acc.current_balance || 0, acc.currency || 'USD')}</div>
                    </div>
                    <div class="account-subtitle">${typeLabel}</div>
                </div>

                <button class="account-more-btn" onclick="openAccountActions(${acc.id})" aria-label="Más opciones">
                    <i class="fas fa-ellipsis-h"></i>
                </button>
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

        if (accountTypeFilter) {
            const labelMap = {
                all: 'Todos',
                checking: 'Corriente',
                savings: 'Ahorros',
                credit: 'Crédito',
                cash: 'Efectivo'
            };

            Array.from(accountTypeFilter.options).forEach(option => {
                const filter = option.value;
                const total = filter === 'all' ? (counts.all || 0) : (counts[filter] || 0);
                option.textContent = `${labelMap[filter]} (${total})`;
            });
        }
    }

    // ==========================================
    // SUMMARY (cabecera y tarjetas)
    // ==========================================

    function updateSummary(accounts) {
        const totalBalance = accounts.reduce((sum, a) => sum + (a.current_balance || 0), 0);
        const displayCurrency = preferredCurrency || accounts[0]?.currency || 'USD';
        const totalBalEl = document.getElementById('summaryTotalBalance');
        if (totalBalEl) totalBalEl.textContent = formatMoney(totalBalance, displayCurrency);

        const activeCount = accounts.filter(a => a.is_active !== false).length;
        const uniqueTypes = new Set(accounts.map(a => a.account_type).filter(Boolean));

        const accountCountEl = document.getElementById('summaryAccountCount');
        if (accountCountEl) accountCountEl.textContent = `${accounts.length} cuenta${accounts.length === 1 ? '' : 's'}`;

        const activeCountEl = document.getElementById('summaryActiveCount');
        if (activeCountEl) activeCountEl.textContent = `${activeCount} Activo`;

        const portfolioTypesEl = document.getElementById('summaryPortfolioTypes');
        if (portfolioTypesEl) portfolioTypesEl.textContent = `${uniqueTypes.size} Tipos`;
    }

    // ==========================================
    // FILTER & SORT
    // ==========================================

    if (accountTypeFilter) {
        accountTypeFilter.addEventListener('change', () => {
            refreshAccountsView();
        });
    }

    if (accountsSortBtn) {
        accountsSortBtn.addEventListener('click', () => {
            sortAscending = !sortAscending;
            accountsSortBtn.classList.toggle('active', sortAscending);
            refreshAccountsView();
        });
    }

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

    accountBalanceInput?.addEventListener('input', updateModalBalancePreview);
    accountCurrencySelect?.addEventListener('change', updateModalBalancePreview);

    // ==========================================
    // OPEN ADD ACCOUNT MODAL
    // ==========================================

    btnAddAccount.addEventListener('click', () => {
        editingAccountId = null;
        document.getElementById('modalTitle').textContent = 'Nueva cuenta';
        accountModal.classList.remove('edit-mode');
        btnDeleteFromModal?.classList.add('hidden');
        accountForm.reset();
        if (accountTypeSelect) accountTypeSelect.value = 'checking';
        if (accountCurrencySelect) accountCurrencySelect.value = preferredCurrency || 'COP';
        if (accountBalanceInput) accountBalanceInput.value = '0';
        creditLimitGroup.classList.add('hidden');
        savingsGoalGroup.classList.add('hidden');
        updateModalBalancePreview();
        accountModal.classList.remove('hidden');
    });

    // ==========================================
    // EDIT ACCOUNT (solo front de momento)
    // ==========================================

    window.editAccount = function (accountId) {
        const acc = accountsCache.find(a => a.id === accountId);
        if (!acc) return;

        editingAccountId = accountId;
        document.getElementById('modalTitle').textContent = 'Editar cuenta';
        accountModal.classList.add('edit-mode');
        btnDeleteFromModal?.classList.remove('hidden');

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

        updateModalBalancePreview();
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
            closeAccountActions();
            if (accountDetailModal && !accountDetailModal.classList.contains('hidden')) {
                closeAccountDetail();
            }
            alert('Cuenta eliminada correctamente');
        } catch (err) {
            console.error('Error al eliminar cuenta:', err);
            if (ensureAuth(err)) return;
            alert(`No se pudo eliminar: ${err.message}`);
        }
    };

    // ==========================================
    // ACTION SHEET
    // ==========================================

    window.openAccountActions = function (accountId) {
        selectedAccountId = accountId;
        const acc = accountsCache.find(a => a.id === accountId);
        if (!acc) return;
        
        // Show detail modal directly instead of action sheet on mobile
        if (window.innerWidth <= 768) {
            showAccountDetail(acc);
        } else {
            accountActionSheet?.classList.remove('hidden');
        }
    };

    function showAccountDetail(acc) {
        selectedAccountId = acc.id;
        
        document.getElementById('detailAccountName').textContent = acc.name || 'Cuenta';
        document.getElementById('detailBalanceAmount').textContent = formatMoney(acc.current_balance || 0, acc.currency || 'USD');
        document.getElementById('detailAccountType').textContent = getTypeLabel(acc.account_type);
        document.getElementById('detailAccountCurrency').textContent = acc.currency || 'USD';
        document.getElementById('detailAccountBank').textContent = acc.bank || acc.account_type || '—';
        document.getElementById('detailAccountStatus').textContent = acc.is_active !== false ? 'Activa' : 'Inactiva';
        
        accountDetailModal?.classList.remove('hidden');
    }

    window.closeAccountDetail = function() {
        accountDetailModal?.classList.add('hidden');
        selectedAccountId = null;
    };

    window.editAccountFromDetail = function() {
        if (!selectedAccountId) return;
        const accountId = selectedAccountId; // Guardar el ID antes de cerrar
        closeAccountDetail();
        editAccount(accountId);
    };

    window.viewTransactionsFromDetail = function() {
        if (!selectedAccountId) return;
        viewTransactions(selectedAccountId);
    };

    function closeAccountActions() {
        selectedAccountId = null;
        accountActionSheet?.classList.add('hidden');
    }

    actionSheetOverlay?.addEventListener('click', closeAccountActions);

    actionEdit?.addEventListener('click', () => {
        if (!selectedAccountId) return;
        closeAccountActions();
        editAccount(selectedAccountId);
    });

    actionDelete?.addEventListener('click', async () => {
        if (!selectedAccountId) return;
        await deleteAccount(selectedAccountId);
    });

    btnDeleteFromModal?.addEventListener('click', async () => {
        if (!editingAccountId) return;
        const accountIdToDelete = editingAccountId;
        closeModal();
        await deleteAccount(accountIdToDelete);
    });

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
        accountModal.classList.remove('edit-mode');
        btnDeleteFromModal?.classList.add('hidden');
        accountForm.reset();
        editingAccountId = null;
        updateModalBalancePreview();
    };

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !accountModal.classList.contains('hidden')) {
            closeModal();
        }

        if (e.key === 'Escape' && accountActionSheet && !accountActionSheet.classList.contains('hidden')) {
            closeAccountActions();
        }

        if (e.key === 'Escape' && accountDetailModal && !accountDetailModal.classList.contains('hidden')) {
            closeAccountDetail();
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
        const resetLoading = setLoadingBtn(submitBtn, editingAccountId ? 'Guardando...' : 'Guardando...');

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
