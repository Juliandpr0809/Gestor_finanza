// Dashboard dinámico conectado al backend

document.addEventListener('DOMContentLoaded', () => {
    const balanceEl = document.getElementById('cardBalance');
    const currencyEl = document.getElementById('cardCurrency');
    const numberEl = document.getElementById('cardNumber');
    const holderEl = document.getElementById('cardHolder');
    const virtualCardEl = document.querySelector('.virtual-card');
    const tickerEl = document.getElementById('headerTicker');
    const profileNameEl = document.getElementById('profileName');
    const profileAvatarEl = document.getElementById('profileAvatar');
    const activityList = document.getElementById('activityList');
    const quickAccountsCountEl = document.getElementById('quickAccountsCount');
    const quickActivityCountEl = document.getElementById('quickActivityCount');
    const cardSection = document.querySelector('.card-section');
    const headerRight = document.querySelector('.header-right');

    let accounts = [];
    let selectedAccountId = null;
    let selectedCurrency = localStorage.getItem('preferredCurrency');
    if (!selectedCurrency) {
        selectedCurrency = 'USD';
    }
    let selectedLanguage = localStorage.getItem('preferredLanguage') || 'es';
    const fallbackRates = { USD: 1, EUR: 0.92, COP: 4000, MXN: 17, GBP: 0.78 };
    let rates = { ...fallbackRates };

    // La autenticación es manejada por auth-handler.js

    if (!window.api) {
        console.error('api no está disponible');
        return;
    }

    const fmtMoney = (amount, currency = 'USD') => {
        try {
            return new Intl.NumberFormat(selectedLanguage === 'es' ? 'es-ES' : 'en-US', { style: 'currency', currency }).format(amount || 0);
        } catch (_) {
            return `${currency} ${(amount || 0).toFixed(2)}`;
        }
    };

    const fmtDate = (iso) => {
        const d = new Date(iso);
        const opts = { month: 'short', day: 'numeric' };
        return d.toLocaleDateString(selectedLanguage === 'es' ? 'es-ES' : 'en-US', opts);
    };

    const translate = (key) => {
        const t = {
            es: {
                cards_title: 'Mis Tarjetas Virtuales',
                transactions_title: 'Transacciones',
                no_transactions: 'Sin transacciones',
                add_card: 'Agregar tarjeta',
                add_transaction: 'Agregar Transacción',
                upload_files: 'Subir Archivos',
                ai_chat: 'Chat IA',
                voice_input: 'Entrada de Voz',
                credit: 'CRÉDITO',
                savings: 'AHORROS',
                checking: 'CORRIENTE',
                account: 'CUENTA',
            },
            en: {
                cards_title: 'My Virtual Cards',
                transactions_title: 'Transactions',
                no_transactions: 'No transactions',
                add_card: 'Add New Card',
                add_transaction: 'Add Transaction',
                upload_files: 'Upload Files',
                ai_chat: 'AI Chat',
                voice_input: 'Voice Input',
                credit: 'CREDIT',
                savings: 'SAVINGS',
                checking: 'CHECKING',
                account: 'ACCOUNT',
            }
        };
        return t[selectedLanguage]?.[key] || t.en[key] || key;
    };

    const convertAmount = (amount, fromCurrency = 'USD') => {
        const from = fromCurrency || 'USD';
        const to = selectedCurrency || 'USD';
        if (from === to) return amount;
        const rateFrom = rates[from] || 1;
        const rateTo = rates[to] || 1;
        return amount * (rateTo / rateFrom);
    };

    async function loadProfile() {
        try {
            const me = await api.getCurrentUser();
            if (profileNameEl) profileNameEl.innerHTML = `${me.email || me.username || 'Usuario'} <i class="fas fa-sign-out-alt verified-badge"></i>`;
            if (profileAvatarEl) {
                const img = profileAvatarEl.querySelector('img');
                if (img) img.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(me.username || me.email || 'U')}&background=random`;
            }
        } catch (err) {
            console.warn('No se pudo cargar el perfil, redirigiendo:', err);
            window.location.href = '/frontend/html/login.html';
        }
    }

    const applyCardTheme = (account) => {
        if (!virtualCardEl) return;
        const variants = ['card-variant-default', 'card-variant-checking', 'card-variant-savings', 'card-variant-credit', 'card-variant-highlight'];
        variants.forEach(v => virtualCardEl.classList.remove(v));
        const map = {
            checking: 'card-variant-checking',
            savings: 'card-variant-savings',
            credit: 'card-variant-credit',
        };
        virtualCardEl.classList.add(map[account?.account_type] || 'card-variant-default');
    };

    function renderAccountCard(account) {
        if (!account) return;
        const displayBalance = convertAmount(account.current_balance, account.currency || 'USD');
        if (balanceEl) balanceEl.textContent = fmtMoney(displayBalance, selectedCurrency);
        if (currencyEl) currencyEl.textContent = selectedCurrency;
        if (numberEl) numberEl.textContent = account.name || 'Cuenta';
        if (holderEl) holderEl.textContent = account.account_type || 'Cuenta';
        applyCardTheme(account);
    }


    function renderAccountSwitcher(list) {
        if (!cardSection) return;

        let container = document.getElementById('accountSwitcherContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'accountSwitcherContainer';
            container.className = 'account-switcher-container';

            // Create carousel wrapper
            const carousel = document.createElement('div');
            carousel.id = 'accountSwitcher';
            carousel.className = 'account-carousel';
            container.appendChild(carousel);

            const cardWrapper = cardSection.querySelector('.card-wrapper');
            cardSection.insertBefore(container, cardWrapper);
        }

        const carousel = container.querySelector('.account-carousel');


        carousel.innerHTML = list.map(acc => {
            const type = acc.account_type || 'account';
            const displayBalance = convertAmount(acc.current_balance, acc.currency || 'USD');
            const isActive = acc.id === selectedAccountId;

            // Minimalist Icon Mapping
            const iconMap = {
                checking: 'fa-university',
                savings: 'fa-piggy-bank',
                credit: 'fa-credit-card',
                cash: 'fa-money-bill-wave'
            };
            const iconClass = iconMap[type] || 'fa-wallet';

            // Minimalist Chip HTML
            return `
            <div class="account-chip-minimal ${isActive ? 'active' : ''}" data-id="${acc.id}">
                <div class="chip-header-min">
                    <i class="fas ${iconClass} chip-icon-min"></i>
                    <i class="fas fa-check-circle chip-check-min"></i>
                </div>
                <div class="chip-name-min">${acc.name || 'Cuenta'}</div>
                <div class="chip-balance-min">${fmtMoney(displayBalance, selectedCurrency)}</div>
            </div>`;
        }).join('');

        carousel.querySelectorAll('.account-chip-minimal').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = Number(btn.dataset.id);
                if (id === selectedAccountId) return;

                // Visual toggle
                carousel.querySelectorAll('.account-chip-minimal').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');

                selectedAccountId = id;
                const account = accounts.find(a => a.id === id);
                renderAccountCard(account);
                loadTransactions(id);
            });
        });
    }

    async function loadAccounts() {
        try {
            accounts = await api.getAccounts();
            if (quickAccountsCountEl) {
                quickAccountsCountEl.textContent = String(accounts.length || 0);
            }
            if (!accounts.length) {
                if (balanceEl) balanceEl.textContent = '$0';
                if (numberEl) numberEl.textContent = 'Sin cuentas';
                if (holderEl) holderEl.textContent = 'Agrega una cuenta';
                return null;
            }
            if (!selectedAccountId) {
                selectedAccountId = accounts[0].id;
            }
            const current = accounts.find(a => a.id === selectedAccountId) || accounts[0];
            selectedAccountId = current.id;
            if (!localStorage.getItem('preferredCurrency') && current?.currency) {
                selectedCurrency = current.currency;
                localStorage.setItem('preferredCurrency', selectedCurrency);
            }
            renderAccountCard(current);
            renderAccountSwitcher(accounts);
            return current;
        } catch (err) {
            console.error('Error cargando cuentas:', err);
            if (balanceEl) balanceEl.textContent = '$0';
            if (numberEl) numberEl.textContent = 'Error al cargar';
            return null;
        }
    }

    function renderTransactions(list) {
        if (!activityList) return;
        if (quickActivityCountEl) {
            quickActivityCountEl.textContent = String((list || []).length || 0);
        }
        if (!list || !list.length) {
            activityList.innerHTML = `<div class="activity-group-header">${translate('no_transactions')}</div>`;
            return;
        }

        const groups = {};
        list.forEach(t => {
            const key = fmtDate(t.date).toLowerCase();
            if (!groups[key]) groups[key] = { label: fmtDate(t.date), items: [] };
            groups[key].items.push(t);
        });

        const markup = Object.values(groups).map(g => {
            const items = g.items.map(t => {
                const account = accounts.find(a => a.id === t.account_id) || {};
                const converted = convertAmount(t.amount, account.currency || 'USD');
                const amountClass = converted >= 0 ? 'green' : '';
                return `
                    <div class="activity-item">
                        <div class="activity-item-time">${fmtDate(t.date)}</div>
                        <div class="activity-item-icon icon-white"><i class="fas fa-wallet"></i></div>
                        <div class="activity-item-details">
                            <div class="activity-item-name">${t.description || t.category_name || 'Transacción'}</div>
                            <div class="activity-item-category">${t.account_name || ''}</div>
                        </div>
                        <div class="activity-item-amounts">
                            <div class="activity-item-amount ${amountClass}">${fmtMoney(converted, selectedCurrency)}</div>
                            <div class="activity-item-crypto">${t.category_name || ''}</div>
                        </div>
                    </div>`;
            }).join('');
            return `<div class="activity-group-header">${g.label}</div>${items}`;
        }).join('');

        activityList.innerHTML = markup;
    }

    async function loadTransactions(accountId = selectedAccountId) {
        try {
            const data = await api.getTransactions({ per_page: 10, account_id: accountId });
            renderTransactions(data.transactions || []);
        } catch (err) {
            console.error('Error cargando transacciones:', err);
            if (activityList) activityList.innerHTML = '<div class="activity-group-header">No se pudieron cargar las transacciones</div>';
        }
    }

    function renderTicker() {
        if (!tickerEl) return;
        tickerEl.innerHTML = '<span class="ticker-pair">USD</span><span class="ticker-value">—</span><span class="ticker-change">&nbsp;</span>';
    }

    async function loadRates() {
        try {
            const res = await fetch('https://api.exchangerate.host/latest?base=USD&symbols=USD,EUR,COP,MXN,GBP');
            const data = await res.json();
            if (data && data.rates) {
                rates = { ...fallbackRates, ...data.rates };
            } else {
                rates = { ...fallbackRates };
            }
        } catch (err) {
            console.warn('No se pudieron cargar tasas, usando fallback', err);
            rates = { ...fallbackRates };
        }
    }

    function applyTranslations() {
        const cardsTitle = document.querySelector('.section-title');
        if (cardsTitle) cardsTitle.textContent = translate('cards_title');
        const trxTitle = document.querySelector('.activity-title');
        if (trxTitle) trxTitle.textContent = translate('transactions_title');
        const addCardBtn = document.querySelector('.btn-add-card');
        if (addCardBtn) addCardBtn.textContent = translate('add_card');

        // Traducir botones de acción
        const actionBtns = document.querySelectorAll('.action-btn-text');
        if (actionBtns[0]) actionBtns[0].textContent = translate('add_transaction');
        if (actionBtns[1]) actionBtns[1].textContent = translate('upload_files');
        if (actionBtns[2]) actionBtns[2].textContent = translate('ai_chat');
        if (actionBtns[3]) actionBtns[3].textContent = translate('voice_input');
    }

    renderTicker();
    loadProfile();
    applyTranslations();
    loadRates().then(() => loadAccounts().then(() => loadTransactions()));

    // Inicializar selector de moneda
    initCurrencySelector();

    // User Menu Toggle (Mobile Enhanced)
    const userMenuToggle = document.getElementById('userMenuToggle');
    const userDropdown = document.getElementById('userDropdown');

    console.log('🔍 User Menu Elements:', {
        userMenuToggle: !!userMenuToggle,
        userDropdown: !!userDropdown,
        userDropdownElement: userDropdown
    });

    if (userMenuToggle && userDropdown) {
        console.log('✅ User menu elements found, adding event listener');
        
        // Agregar indicador visual de estado
        userMenuToggle.style.transition = 'all 0.3s ease';
        
        userMenuToggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('👤 User menu clicked');
            
            const wasShowing = userDropdown.classList.contains('show');
            
            // Toggle clase show
            if (wasShowing) {
                userDropdown.classList.remove('show');
                userMenuToggle.classList.remove('active');
                userMenuToggle.style.background = '';
            } else {
                userDropdown.classList.add('show');
                userMenuToggle.classList.add('active');
                userMenuToggle.style.background = 'rgba(102, 126, 234, 0.2)';
            }
            
            // Log detallado
            console.log('📋 Dropdown classes:', userDropdown.className);
            const computedStyles = getComputedStyle(userDropdown);
            console.log('🎨 Computed styles:', {
                display: computedStyles.display,
                opacity: computedStyles.opacity,
                visibility: computedStyles.visibility,
                zIndex: computedStyles.zIndex,
                position: computedStyles.position,
                top: computedStyles.top,
                right: computedStyles.right,
                transform: computedStyles.transform
            });
            console.log('📊 Show state:', !wasShowing ? 'SHOWING' : 'HIDING');
            
            // Mostrar alerta visual si no se está mostrando
            if (!wasShowing) {
                setTimeout(() => {
                    const stillVisible = getComputedStyle(userDropdown).visibility === 'visible';
                    if (!stillVisible) {
                        alert('⚠️ El menú debería estar visible pero no lo está. Revisa la consola.');
                    }
                }, 100);
            }
        });

        document.addEventListener('click', (e) => {
            if (!userMenuToggle.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.remove('show');
                userMenuToggle.classList.remove('active');
            }
        });

        // Logout Handler
        document.querySelectorAll('[data-action="logout"]').forEach(btn => {
            btn.addEventListener('click', () => {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                sessionStorage.clear();
                window.location.href = 'login.html';
            });
        });
    }
});

// Selector de moneda en header
function initCurrencySelector() {
    const currencyValue = document.getElementById('currencyValue');
    const currencyDropdown = document.getElementById('currencyDropdown');

    console.log('💰 Currency Selector Elements:', {
        currencyValue: !!currencyValue,
        currencyDropdown: !!currencyDropdown
    });

    if (!currencyValue || !currencyDropdown) return;

    // Mostrar moneda actual
    const savedCurrency = localStorage.getItem('preferredCurrency') || 'COP';
    currencyValue.textContent = savedCurrency;

    // Marcar opción activa
    document.querySelectorAll('.currency-option').forEach(opt => {
        if (opt.dataset.currency === savedCurrency) {
            opt.classList.add('active');
        }
    });

    // Toggle dropdown
    currencyValue.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('💱 Currency selector clicked');
        
        const wasShowing = currencyDropdown.classList.contains('show');
        currencyDropdown.classList.toggle('show');
        
        console.log('📋 Currency dropdown classes:', currencyDropdown.className);
        console.log('🎨 Currency computed styles:', {
            display: getComputedStyle(currencyDropdown).display,
            opacity: getComputedStyle(currencyDropdown).opacity,
            visibility: getComputedStyle(currencyDropdown).visibility,
            zIndex: getComputedStyle(currencyDropdown).zIndex,
            position: getComputedStyle(currencyDropdown).position
        });
        console.log('📊 Show state:', !wasShowing ? 'SHOWING' : 'HIDING');
    });

    // Cambiar moneda
    document.querySelectorAll('.currency-option').forEach(opt => {
        opt.addEventListener('click', (e) => {
            e.stopPropagation();
            const newCurrency = opt.dataset.currency;

            // Actualizar UI
            currencyValue.textContent = newCurrency;
            document.querySelectorAll('.currency-option').forEach(o => o.classList.remove('active'));
            opt.classList.add('active');

            // Guardar y recargar
            localStorage.setItem('preferredCurrency', newCurrency);
            currencyDropdown.classList.remove('show');

            // Recargar página para aplicar cambios
            window.location.reload();
        });
    });

    // Cerrar al hacer click fuera
    document.addEventListener('click', () => {
        currencyDropdown.classList.remove('show');
    });
}

