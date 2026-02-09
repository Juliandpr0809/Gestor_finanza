// New Transaction Page Logic

let accounts = [];
let categories = [];
let selectedAccountId = null;
let selectedCategoryId = null;

document.addEventListener('DOMContentLoaded', () => {
    loadData();
    initializeTypeSelectors();
    initializeFileUpload();
    initializeTags();
    initializeCategorySuggestions();
    initializeDateTime();
    initializeAdvancedToggle();
    initializeCategoryTrigger();
    initializeAmountBinding();

    const form = document.getElementById('transaction-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }

    const categoryForm = document.getElementById('createCategoryForm');
    if (categoryForm) {
        categoryForm.addEventListener('submit', handleCreateCategory);
    }
});

// ==========================================
// DATA LOADING
// ==========================================

async function loadData() {
    try {
        const [me, accountsData, categoriesData] = await Promise.all([
            api.getCurrentUser().catch((e) => {
                console.warn('Failed to get user:', e);
                return null;
            }),
            api.getAccounts(),
            api.getCategories()
        ]);
        const accountsList = accountsData?.accounts || accountsData || [];
        const categoriesList = categoriesData?.categories || categoriesData || [];

        accounts = Array.isArray(accountsList) ? accountsList : [];
        categories = Array.isArray(categoriesList) ? categoriesList : [];

        console.log('Loaded accounts:', accounts);
        console.log('Loaded categories:', categories);
        console.log('Current user:', me);

        // Set default currency from user preference if available
        const currencySelect = document.getElementById('currency');
        if (currencySelect && me) {
            // Intentar me.preferred_currency primero, luego me.user.preferred_currency
            const userCurrency = me.preferred_currency || (me.user && me.user.preferred_currency);
            if (userCurrency) {
                currencySelect.value = userCurrency;
                console.log('Set currency to:', userCurrency);
            }
        }

        populateAccounts();
        populateCategories();

        updateCategoryPreview();
        updateSummary();

        // Filter accounts by currency selection
        if (currencySelect) {
            currencySelect.addEventListener('change', () => {
                filterAccountsByCurrency();
                updateSummary();
            });
            filterAccountsByCurrency();
        }
    } catch (err) {
        console.error('Error cargando datos:', err);
        alert('Error al cargar datos: ' + (err.message || 'Error desconocido'));
    }
}

function populateAccounts() {
    const accountSelect = document.getElementById('account');
    const chipsContainer = document.getElementById('accountChips');
    if (!accountSelect) return;

    console.log('Populating accounts:', accounts);
    accountSelect.innerHTML = '<option value="">Select Account</option>';

    accounts.forEach(acc => {
        const option = document.createElement('option');
        option.value = acc.id;
        option.textContent = `${acc.name} (${acc.currency}) - ${acc.current_balance || 0}`;
        option.dataset.currency = acc.currency;
        accountSelect.appendChild(option);
    });

    if (chipsContainer) {
        chipsContainer.innerHTML = '';
        accounts.forEach(acc => {
            const chip = document.createElement('div');
            chip.className = `account-chip${selectedAccountId === acc.id ? ' active' : ''}`;
            chip.dataset.id = acc.id;
            chip.dataset.currency = acc.currency;
            chip.innerHTML = `<i class="fas fa-wallet"></i>${acc.name}`;
            chip.addEventListener('click', () => selectAccount(acc));
            chipsContainer.appendChild(chip);
        });
    }

    if (!selectedAccountId && accounts.length) {
        selectAccount(accounts[0]);
    }

    console.log('Accounts populated:', accountSelect.options.length - 1, 'options added');
}

function filterAccountsByCurrency() {
    const currencySelect = document.getElementById('currency');
    const accountSelect = document.getElementById('account');
    const chipsContainer = document.getElementById('accountChips');
    if (!currencySelect || !accountSelect) return;

    const selectedCurrency = currencySelect.value;
    const current = accountSelect.value;

    console.log(`Filtering accounts for currency: ${selectedCurrency}`);

    accountSelect.innerHTML = '<option value="">Select Account</option>';
    if (chipsContainer) chipsContainer.innerHTML = '';

    const available = [];

    accounts.forEach(acc => {
        if (!selectedCurrency || acc.currency === selectedCurrency) {
            const option = document.createElement('option');
            option.value = acc.id;
            option.textContent = `${acc.name} (${acc.currency}) - ${acc.current_balance || 0}`;
            option.dataset.currency = acc.currency;
            accountSelect.appendChild(option);

            if (chipsContainer) {
                const chip = document.createElement('div');
                chip.className = `account-chip${selectedAccountId === acc.id ? ' active' : ''}`;
                chip.dataset.id = acc.id;
                chip.dataset.currency = acc.currency;
                chip.innerHTML = `<i class="fas fa-wallet"></i>${acc.name}`;
                chip.addEventListener('click', () => selectAccount(acc));
                chipsContainer.appendChild(chip);
            }

            available.push(acc);
        }
    });

    // Intentar mantener selección previa si sigue disponible
    if (current && accountSelect.querySelector(`option[value="${current}"]`)) {
        accountSelect.value = current;
        selectedAccountId = parseInt(current, 10);
    } else if (available.length) {
        selectAccount(available[0]);
    } else {
        selectedAccountId = null;
        const summaryAccount = document.getElementById('summaryAccount');
        if (summaryAccount) summaryAccount.textContent = '-';
    }

    if (chipsContainer) {
        chipsContainer.querySelectorAll('.account-chip').forEach(chip => {
            chip.classList.toggle('active', chip.dataset.id === String(selectedAccountId));
        });
    }

    console.log(`Showing ${accountSelect.options.length - 1} account(s) for currency ${selectedCurrency}`);
}

function selectAccount(acc) {
    selectedAccountId = acc?.id || null;

    const accountSelect = document.getElementById('account');
    if (accountSelect && selectedAccountId) {
        accountSelect.value = String(selectedAccountId);
    }

    document.querySelectorAll('.account-chip').forEach(chip => {
        chip.classList.toggle('active', chip.dataset.id === String(selectedAccountId));
    });

    const summaryAccount = document.getElementById('summaryAccount');
    if (summaryAccount) {
        summaryAccount.textContent = acc?.name || '-';
    }

    const currencySelect = document.getElementById('currency');
    if (currencySelect && acc?.currency && !currencySelect.value) {
        currencySelect.value = acc.currency;
    }

    updateSummary();
}

function updateCategoryPreview() {
    const categorySelect = document.getElementById('category');
    const label = document.getElementById('categoryLabel');
    const hint = document.getElementById('categoryHint');
    const previewName = document.getElementById('categoryPreviewName');
    const previewIcon = document.getElementById('categoryPreviewIcon');

    const selectedOption = categorySelect ? categorySelect.options[categorySelect.selectedIndex] : null;
    const catData = selectedOption?.value ? categories.find(c => String(c.id) === String(selectedOption.value)) : null;

    selectedCategoryId = selectedOption?.value ? parseInt(selectedOption.value, 10) : null;

    const name = catData?.name || 'No Category';
    if (label) label.textContent = selectedOption?.value ? name : 'Select a Category';
    if (hint) hint.textContent = selectedOption?.value ? 'Category selected' : 'AI suggestion will appear here';
    if (previewName) previewName.textContent = name;

    if (previewIcon) {
        const icon = catData?.icon;
        const iconMarkup = icon ? (icon.startsWith('fa-') ? `<i class="fas ${icon}"></i>` : icon) : '<i class="fas fa-wallet"></i>';
        previewIcon.innerHTML = iconMarkup;
    }
}

function formatCurrency(value, currency = 'USD') {
    try {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(value || 0);
    } catch (_) {
        const amount = Number(value || 0).toFixed(2);
        return `$${amount}`;
    }
}

function updateSummary() {
    const amountInput = document.getElementById('amount');
    const summaryAmount = document.getElementById('summaryAmount');
    const currency = document.getElementById('currency')?.value || 'USD';
    const amount = parseFloat(amountInput?.value || '0') || 0;
    if (summaryAmount) {
        summaryAmount.textContent = formatCurrency(amount, currency);
    }

    const dateInput = document.getElementById('date');
    const timeInput = document.getElementById('time');
    const summaryDate = document.getElementById('summaryDate');
    if (summaryDate) {
        if (dateInput?.value) {
            const dateObj = new Date(dateInput.value);
            const dateText = dateObj.toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' });
            const timeText = timeInput?.value ? ` ${timeInput.value}` : '';
            summaryDate.textContent = `${dateText}${timeText}`.trim();
        } else {
            summaryDate.textContent = '-';
        }
    }
}

function populateCategories() {
    const categorySelect = document.getElementById('category');
    if (!categorySelect) return;

    const typeBtn = document.querySelector('.type-tab.active');
    const type = typeBtn ? typeBtn.dataset.type : 'expense';
    const filteredCategories = categories.filter(c => (c.type || c.category_type) === type);

    // Add specific value for "Create New" to detect it easily
    categorySelect.innerHTML = '<option value="">Select Category</option>' +
        filteredCategories.map(cat => `<option value="${cat.id}">${cat.name}</option>`).join('') +
        '<option value="CREATE_NEW" style="color: #007AFF; font-weight: bold;">+ Create New Category</option>';

    if (selectedCategoryId && categorySelect.querySelector(`option[value="${selectedCategoryId}"]`)) {
        categorySelect.value = selectedCategoryId;
    } else {
        selectedCategoryId = null;
        categorySelect.value = '';
    }

    updateCategoryPreview();
}

// ==========================================
// CATEGORY SUGGESTIONS
// ==========================================

function initializeCategorySuggestions() {
    const descriptionInput = document.getElementById('description');
    const titleInput = document.getElementById('title');
    const inputs = [descriptionInput, titleInput].filter(Boolean);

    inputs.forEach(input => {
        input.addEventListener('input', () => {
            const combined = [descriptionInput?.value, titleInput?.value].filter(Boolean).join(' ').trim();
            if (combined.length === 0) {
                resetCategorySuggestion();
            } else if (combined.length >= 3) {
                suggestCategoryWithAI(combined);
            }
        });
    });
}

function resetCategorySuggestion() {
    const categorySelect = document.getElementById('category');
    if (!categorySelect) return;

    categorySelect.value = '';
    const firstOption = categorySelect.querySelector('option:first-child');
    if (firstOption) {
        firstOption.textContent = 'Select Category';
        firstOption.style.color = 'inherit';
    }

    window.suggestedCategoryName = '';
    updateCategoryPreview();
}

async function suggestCategoryWithAI(description) {
    try {
        const typeBtn = document.querySelector('.type-tab.active');
        const type = typeBtn ? typeBtn.dataset.type : 'expense';

        // Get language from browser or default to Spanish
        const language = navigator.language.split('-')[0] || 'es';

        // Call backend AI suggestion endpoint
        const suggestion = await api.suggestCategoryWithAI(description, type, language);

        if (suggestion.category) {

            // Handle Cross-Type Suggestion (e.g. Income detected while in Expense tab)
            if (suggestion.suggested_type && suggestion.category_id) {
                const targetTypeBtn = document.querySelector(`.type-tab[data-type="${suggestion.suggested_type}"]`);
                if (targetTypeBtn && !targetTypeBtn.classList.contains('active')) {
                    // Update global state before switching to ensure it sticks
                    selectedCategoryId = suggestion.category_id;

                    // Click to switch tabs (this triggers populateCategories)
                    targetTypeBtn.click();

                    // Ensure the selection is applied and preview updated
                    const categorySelect = document.getElementById('category');
                    if (categorySelect) {
                        categorySelect.value = suggestion.category_id;
                        updateCategoryPreview();
                    }
                    return;
                }
            }

            if (suggestion.exists) {
                // Category already exists, auto-select it
                const categorySelect = document.getElementById('category');
                if (categorySelect) {
                    categorySelect.value = suggestion.category_id;
                    selectedCategoryId = suggestion.category_id;
                    updateCategoryPreview();
                }
            } else {
                // Show suggestion for new category creation
                showCategorySuggestion(suggestion.category, type);
            }
        } else {
            // Fall back to keyword-based suggestion
            suggestCategoryByKeywords(description);
        }
    } catch (err) {
        console.error('Error suggesting category:', err);
        // Fall back to keyword-based suggestion
        suggestCategoryByKeywords(description);
    }
}

function suggestCategoryByKeywords(text) {
    if (!text || text.length < 3) return;

    const lowerText = text.toLowerCase();
    const categorySelect = document.getElementById('category');
    const typeBtn = document.querySelector('.type-tab.active');
    const type = typeBtn ? typeBtn.dataset.type : 'expense';

    // Keywords for category suggestions (Multi-language: ES, EN, FR, DE, PT, IT)
    const suggestions = {
        expense: {
            'Comida': [
                // Spanish
                'comida', 'restaurante', 'almuerzo', 'cena', 'desayuno', 'pizza', 'burger', 'cafe', 'supermercado', 'groceries',
                'pan', 'pastel', 'postre', 'bebida', 'vino', 'cerveza', 'jugo',
                // English
                'lunch', 'dinner', 'breakfast', 'restaurant', 'food', 'grocery', 'snack', 'meal', 'cake', 'coffee',
                // French
                'restaurant', 'dejeuner', 'diner', 'petit-dejeuner', 'nourriture', 'cafe', 'boulangerie',
                // German
                'restaurant', 'mittagessen', 'abendessen', 'frühstück', 'lebensmittel', 'kaffee', 'bäckerei',
                // Portuguese
                'restaurante', 'almoço', 'jantar', 'café', 'comida', 'supermercado', 'açougue',
                // Italian
                'ristorante', 'pranzo', 'cena', 'colazione', 'cibo', 'caffè', 'panetteria'
            ],
            'Transporte': [
                // Spanish
                'uber', 'taxi', 'gasolina', 'gas', 'metro', 'bus', 'transporte', 'parking', 'coche', 'viaje', 'gasolinera',
                // English
                'uber', 'taxi', 'gas', 'metro', 'bus', 'transport', 'parking', 'car', 'travel', 'fuel', 'vehicle',
                // French
                'uber', 'taxi', 'essence', 'metro', 'bus', 'transport', 'parking', 'voiture', 'voyage',
                // German
                'uber', 'taxi', 'benzin', 'u-bahn', 'bus', 'transport', 'parkplatz', 'auto', 'fahrt',
                // Portuguese
                'uber', 'taxi', 'gasolina', 'metro', 'ônibus', 'transporte', 'estacionamento', 'carro', 'viagem',
                // Italian
                'uber', 'taxi', 'benzina', 'metropolitana', 'autobus', 'trasporto', 'parcheggio', 'auto', 'viaggio'
            ],
            'Vivienda': [
                // Spanish
                'alquiler', 'renta', 'hipoteca', 'casa', 'apartamento', 'inquilino', 'propietario', 'vivienda',
                // English
                'rent', 'mortgage', 'house', 'apartment', 'home', 'tenant', 'landlord', 'housing',
                // French
                'loyer', 'hypotheque', 'maison', 'appartement', 'logement', 'locataire', 'proprietaire',
                // German
                'miete', 'hypothek', 'haus', 'wohnung', 'wohnraum', 'mieter', 'vermieter',
                // Portuguese
                'aluguel', 'hipoteca', 'casa', 'apartamento', 'moradia', 'inquilino', 'proprietário',
                // Italian
                'affitto', 'mutuo', 'casa', 'appartamento', 'abitazione', 'affittuario', 'proprietario'
            ],
            'Servicios': [
                // Spanish
                'luz', 'agua', 'internet', 'telefono', 'electricidad', 'gas', 'servicio', 'factura', 'recibo',
                // English
                'electricity', 'water', 'internet', 'phone', 'utilities', 'bill', 'invoice', 'power',
                // French
                'electricite', 'eau', 'internet', 'telephone', 'services', 'facture', 'quittance',
                // German
                'strom', 'wasser', 'internet', 'telefon', 'nebenkosten', 'rechnung', 'beleg',
                // Portuguese
                'luz', 'água', 'internet', 'telefone', 'serviços', 'conta', 'fatura',
                // Italian
                'elettricità', 'acqua', 'internet', 'telefono', 'servizi', 'bolletta', 'ricevuta'
            ],
            'Salud': [
                // Spanish
                'farmacia', 'doctor', 'medico', 'hospital', 'medicina', 'consulta', 'dentista', 'cirugia',
                // English
                'pharmacy', 'doctor', 'medical', 'hospital', 'medicine', 'appointment', 'dentist', 'surgery',
                // French
                'pharmacie', 'docteur', 'medical', 'hopital', 'medicament', 'consultation', 'dentiste',
                // German
                'apotheke', 'arzt', 'medizinisch', 'krankenhaus', 'medikament', 'zahnarzt', 'operation',
                // Portuguese
                'farmácia', 'médico', 'hospital', 'medicina', 'consulta', 'dentista', 'cirurgia',
                // Italian
                'farmacia', 'medico', 'ospedale', 'medicina', 'visita', 'dentista', 'chirurgia'
            ],
            'Entretenimiento': [
                // Spanish
                'netflix', 'spotify', 'cine', 'pelicula', 'concierto', 'juego', 'game', 'cine', 'teatro', 'musica',
                // English
                'netflix', 'spotify', 'cinema', 'movie', 'concert', 'game', 'theater', 'music', 'entertainment',
                // French
                'netflix', 'spotify', 'cinema', 'film', 'concert', 'jeu', 'theatre', 'musique',
                // German
                'netflix', 'spotify', 'kino', 'film', 'konzert', 'spiel', 'theater', 'musik',
                // Portuguese
                'netflix', 'spotify', 'cinema', 'filme', 'show', 'jogo', 'teatro', 'música',
                // Italian
                'netflix', 'spotify', 'cinema', 'film', 'concerto', 'gioco', 'teatro', 'musica'
            ],
            'Compras': [
                // Spanish
                'amazon', 'tienda', 'ropa', 'zapatos', 'compra', 'shopping', 'mall', 'tienda online',
                // English
                'amazon', 'store', 'clothes', 'shoes', 'shopping', 'mall', 'purchase', 'retail',
                // French
                'amazon', 'magasin', 'vetements', 'chaussures', 'shopping', 'centre commercial', 'achat',
                // German
                'amazon', 'laden', 'kleidung', 'schuhe', 'einkaufen', 'einkaufszentrum', 'kauf',
                // Portuguese
                'amazon', 'loja', 'roupa', 'sapatos', 'compra', 'shopping', 'centro comercial',
                // Italian
                'amazon', 'negozio', 'vestiti', 'scarpe', 'acquisto', 'centro commerciale'
            ],
            'Educacion': [
                // Spanish
                'curso', 'libro', 'universidad', 'colegio', 'escuela', 'educacion', 'clase', 'estudiante',
                // English
                'course', 'book', 'university', 'school', 'education', 'class', 'student', 'tuition',
                // French
                'cours', 'livre', 'universite', 'ecole', 'education', 'classe', 'etudiant',
                // German
                'kurs', 'buch', 'universitat', 'schule', 'bildung', 'klasse', 'student',
                // Portuguese
                'curso', 'livro', 'universidade', 'escola', 'educação', 'classe', 'aluno',
                // Italian
                'corso', 'libro', 'università', 'scuola', 'educazione', 'classe', 'studente'
            ]
        },
        income: {
            'Salario': [
                // Spanish
                'salario', 'sueldo', 'nomina', 'pago', 'salary', 'paga',
                // English
                'salary', 'wage', 'paycheck', 'salary', 'pay', 'income',
                // French
                'salaire', 'paie', 'salaire', 'revenu', 'paiement',
                // German
                'gehalt', 'lohn', 'zahlung', 'einkommen', 'bezahlung',
                // Portuguese
                'salário', 'soldo', 'pagamento', 'renda', 'paga',
                // Italian
                'stipendio', 'salario', 'paga', 'reddito', 'pagamento'
            ],
            'Freelance': [
                // Spanish
                'freelance', 'proyecto', 'trabajo', 'honorarios', 'consultoria',
                // English
                'freelance', 'project', 'work', 'consulting', 'contract',
                // French
                'freelance', 'projet', 'travail', 'consultation', 'contrat',
                // German
                'freiberufler', 'projekt', 'arbeit', 'beratung', 'vertrag',
                // Portuguese
                'freelancer', 'projeto', 'trabalho', 'consultoria', 'contrato',
                // Italian
                'freelance', 'progetto', 'lavoro', 'consulenza', 'contratto'
            ],
            'Inversiones': [
                // Spanish
                'dividendo', 'interes', 'ganancia', 'investment', 'bolsa', 'fondo',
                // English
                'dividend', 'interest', 'profit', 'investment', 'stock', 'fund',
                // French
                'dividende', 'interet', 'profit', 'investissement', 'bourse', 'fonds',
                // German
                'dividende', 'zinsen', 'gewinn', 'investition', 'boerse', 'fonds',
                // Portuguese
                'dividendo', 'juros', 'lucro', 'investimento', 'bolsa', 'fundo',
                // Italian
                'dividendo', 'interesse', 'profitto', 'investimento', 'borsa', 'fondo'
            ],
            'Venta': [
                // Spanish
                'venta', 'vendido', 'sale', 'articulo', 'producto',
                // English
                'sale', 'sold', 'selling', 'item', 'product',
                // French
                'vente', 'vendu', 'articles', 'produits',
                // German
                'verkauf', 'verkauft', 'artikel', 'produkte',
                // Portuguese
                'venda', 'vendido', 'artigo', 'produto',
                // Italian
                'vendita', 'venduto', 'articolo', 'prodotto'
            ]
        }
    };

    const typeSuggestions = suggestions[type] || {};

    for (const [categoryName, keywords] of Object.entries(typeSuggestions)) {
        for (const keyword of keywords) {
            if (lowerText.includes(keyword)) {
                // Check if category exists
                const existingCategory = categories.find(c =>
                    c.name.toLowerCase() === categoryName.toLowerCase() && c.type === type
                );

                if (existingCategory && categorySelect) {
                    categorySelect.value = existingCategory.id;
                    selectedCategoryId = existingCategory.id;
                    updateCategoryPreview();
                    return;
                } else {
                    // Suggest creating this category
                    showCategorySuggestion(categoryName, type);
                    return;
                }
            }
        }
    }
}

function showCategorySuggestion(categoryName, type) {
    const categorySelect = document.getElementById('category');
    if (!categorySelect) return;

    // Update the empty option to show suggestion
    const existingOption = categorySelect.querySelector('option[value=""]');
    if (existingOption) {
        existingOption.textContent = `💡 Create "${categoryName}" category`;
        existingOption.style.color = '#007AFF';
    }

    // Store suggested name globally for quick access
    window.suggestedCategoryName = categoryName;
}

// Update the button to use suggested name
document.addEventListener('DOMContentLoaded', () => {
    const newCategoryBtn = document.querySelector('[onclick*="openCreateCategoryModal"]');
    if (newCategoryBtn) {
        newCategoryBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const suggestedName = window.suggestedCategoryName || '';
            openCreateCategoryModal(suggestedName);
        });
    }
});

// ==========================================
// TYPE SELECTOR
// ==========================================
function initializeTypeSelectors() {
    const buttons = document.querySelectorAll('.type-tab');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active from all
            buttons.forEach(b => b.classList.remove('active'));
            // Add active to clicked
            btn.classList.add('active');

            const type = btn.dataset.type;
            populateCategories();
        });
    });

    // Initialize with default type (expense)
    populateCategories();
}

function initializeDateTime() {
    const dateInput = document.getElementById('date');
    const timeInput = document.getElementById('time');
    const dateDisplay = document.getElementById('dateDisplay');
    const timeDisplay = document.getElementById('timeDisplay');

    const today = new Date();

    if (dateInput) {
        dateInput.value = today.toISOString().split('T')[0];
        dateDisplay.textContent = today.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' });
        dateInput.addEventListener('change', () => {
            if (dateInput.value) {
                const dateObj = new Date(dateInput.value);
                dateDisplay.textContent = dateObj.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' });
            } else {
                dateDisplay.textContent = 'Today';
            }
            updateSummary();
        });
    }

    if (timeInput) {
        const hh = String(today.getHours()).padStart(2, '0');
        const mm = String(today.getMinutes()).padStart(2, '0');
        timeInput.value = `${hh}:${mm}`;
        timeDisplay.textContent = `${hh}:${mm}`;
        timeInput.addEventListener('change', () => {
            timeDisplay.textContent = timeInput.value || '12:00';
            updateSummary();
        });
    }

    const dateTrigger = document.getElementById('dateTrigger');
    const timeTrigger = document.getElementById('timeTrigger');
    if (dateTrigger && dateInput) {
        dateTrigger.addEventListener('click', () => dateInput.showPicker ? dateInput.showPicker() : dateInput.focus());
    }
    if (timeTrigger && timeInput) {
        timeTrigger.addEventListener('click', () => timeInput.showPicker ? timeInput.showPicker() : timeInput.focus());
    }

    updateSummary();
}

function initializeAdvancedToggle() {
    const toggle = document.getElementById('toggleAdvanced');
    const panel = document.getElementById('advancedFields');
    if (!toggle || !panel) return;

    toggle.addEventListener('click', () => {
        const isOpen = panel.style.display !== 'none';
        panel.style.display = isOpen ? 'none' : 'block';
        toggle.classList.toggle('open', !isOpen);
    });
}

function initializeCategoryTrigger() {
    const select = document.getElementById('category');
    if (!select) return;

    select.addEventListener('change', () => {
        if (select.value === 'CREATE_NEW') {
            const suggestedName = window.suggestedCategoryName || '';
            if (typeof openCreateCategoryModal === 'function') {
                openCreateCategoryModal(suggestedName);
            } else {
                console.error('openCreateCategoryModal function not found');
                // Fallback or alert
                const modal = document.getElementById('createCategoryModal');
                if (modal) modal.style.display = 'flex';
            }
            select.value = ''; // Reset selection
            return;
        }

        selectedCategoryId = select.value ? parseInt(select.value, 10) : null;
        updateCategoryPreview();
    });

    // Ensure preview is updated on load
    updateCategoryPreview();
}

function initializeAmountBinding() {
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', updateSummary);
    }
}

// ==========================================
// CUSTOM SELECT
// // ==========================================
// ==========================================
// FILE UPLOAD
// ==========================================
function initializeFileUpload() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');

    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#007AFF';
        dropZone.style.background = 'rgba(0, 122, 255, 0.1)';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'rgba(255, 255, 255, 0.15)';
        dropZone.style.background = 'rgba(255, 255, 255, 0.02)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'rgba(255, 255, 255, 0.15)';
        dropZone.style.background = 'rgba(255, 255, 255, 0.02)';

        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
}

function handleFile(file) {
    const dropZone = document.getElementById('drop-zone');
    if (!dropZone) return;
    dropZone.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; gap: 12px;">
            <div style="display:flex; align-items:center; gap:12px;">
                <i class="fas fa-file-upload" style="color:#00D4AA;"></i>
                <div style="text-align: left;">
                    <div style="color: #fff; font-weight: 500;">${file.name}</div>
                    <div style="font-size: 12px; color: #8E8E93;">${(file.size / 1024 / 1024).toFixed(2)} MB</div>
                </div>
            </div>
            <button onclick="resetUpload(event)" type="button" style="background: none; border: none; color: #ff3b30; cursor: pointer;">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

window.resetUpload = function (e) {
    e.stopPropagation();
    const dropZone = document.getElementById('drop-zone');
    if (!dropZone) return;
    dropZone.innerHTML = `
        <i class="fas fa-paperclip"></i>
        <span>Click to upload or drag and drop (JPG, PNG, PDF max 5MB)</span>
        <i class="fas fa-chevron-right"></i>
        <input type="file" id="file-input" hidden>
    `;
    initializeFileUpload();
};

// ==========================================
// TAGS
// ==========================================
function initializeTags() {
    const input = document.getElementById('tags-input');
    const container = document.getElementById('tags-container');

    if (!input) return;

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            const val = input.value.trim().replace(',', '');
            if (val) {
                addTag(val);
                input.value = '';
            }
        }
    });

    function addTag(text) {
        const tag = document.createElement('div');
        tag.className = 'tag-badge';
        tag.innerHTML = `<span>#${text}</span> <i class="fas fa-times" style="cursor: pointer" onclick="this.parentElement.remove()"></i>`;
        container.insertBefore(tag, input);
    }
}

// ==========================================
// QUICK ADD
// ==========================================
window.quickFill = function (type) {
    const amount = document.getElementById('amount');
    const description = document.getElementById('description');
    const presets = {
        coffee: { amount: 5, desc: 'Morning Coffee', keywords: ['coffee', 'cafe', 'food'] },
        lunch: { amount: 15, desc: 'Lunch', keywords: ['lunch', 'food'] },
        gas: { amount: 50, desc: 'Gas Station', keywords: ['gas', 'fuel', 'transporte'] },
        groceries: { amount: 100, desc: 'Weekly Groceries', keywords: ['grocery', 'market', 'super'] }
    };

    const preset = presets[type];
    if (!preset) return;

    const expenseTab = document.querySelector('.type-tab[data-type="expense"]');
    if (expenseTab) {
        document.querySelectorAll('.type-tab').forEach(b => b.classList.remove('active'));
        expenseTab.classList.add('active');
        populateCategories();
    }

    if (amount) amount.value = preset.amount;
    if (description) description.value = preset.desc;

    const categorySelect = document.getElementById('category');
    if (categorySelect) {
        const match = categories.find(c => (c.type || c.category_type) === 'expense' &&
            preset.keywords.some(k => c.name.toLowerCase().includes(k)));
        if (match) {
            categorySelect.value = match.id;
            selectedCategoryId = match.id;
            updateCategoryPreview();
        }
    }

    updateSummary();
};

// ==========================================
// SUBMIT
// ==========================================
async function handleFormSubmit(e) {
    e.preventDefault();

    const typeBtn = document.querySelector('.type-tab.active');
    const type = typeBtn ? typeBtn.dataset.type : 'expense';
    const currency = document.getElementById('currency')?.value || '';
    const accountId = parseInt(document.getElementById('account').value);
    let categoryId = parseInt(document.getElementById('category').value);
    const amount = parseFloat(document.getElementById('amount').value);
    const description = document.getElementById('description').value;
    const date = document.getElementById('date').value;

    // Si no hay categoría pero tenemos una sugerida, crearla automáticamente
    if (!categoryId && window.suggestedCategoryName) {
        try {
            const categoryData = {
                name: window.suggestedCategoryName,
                category_type: type,
                icon: 'fa-folder',
                color: '#7cb342'
            };
            const created = await api.createCategory(categoryData);
            if (created && created.id) {
                categoryId = created.id;
                const categorySelect = document.getElementById('category');
                if (categorySelect) {
                    categorySelect.value = created.id;
                }
            }
        } catch (err) {
            console.error('Error autogenerando categoría sugerida:', err);
            alert('No se pudo crear la categoría sugerida. Selecciona una categoría manualmente.');
        }
    }

    if (!accountId || !categoryId || !amount || !date || !currency) {
        alert('Por favor completa todos los campos obligatorios');
        return;
    }
    const title = document.getElementById('title')?.value.trim();
    const notes = document.getElementById('description')?.value.trim();
    const fullDescription = title && notes ? `${title} - ${notes}` : (title || notes || '');

    const time = document.getElementById('time')?.value;
    const dateTime = time ? `${date}T${time}` : date;

    const transactionData = {
        account_id: accountId,
        category_id: categoryId,
        type: type,
        amount: Math.abs(amount),
        description: fullDescription,
        date: dateTime,
        currency_hint: currency
    };

    try {
        await api.createTransaction(transactionData);
        alert('¡Transacción creada exitosamente!');
        window.location.href = 'transactions.html';
    } catch (err) {
        console.error('Error creando transacción:', err);
        alert('Error al crear la transacción: ' + (err.message || 'Error desconocido'));
    }
}

// ==========================================
// CREATE CATEGORY MODAL
// ==========================================

window.openCreateCategoryModal = function (suggestedName = '') {
    const modal = document.getElementById('createCategoryModal');
    if (modal) {
        modal.style.display = 'flex';

        // Set default type based on current transaction type
        const typeBtn = document.querySelector('.type-tab.active');
        const type = typeBtn ? typeBtn.dataset.type : 'expense';
        const typeSelect = document.getElementById('newCategoryType');
        if (typeSelect) typeSelect.value = type;

        // Pre-fill suggested name
        const nameInput = document.getElementById('newCategoryName');
        if (nameInput) {
            nameInput.value = suggestedName || '';
        }

        // Initialize grids
        populateIconGrid();
        populateColorGrid();

        // Set defaults with slight delay to ensure grid is rendered
        setTimeout(() => {
            selectIcon('fa-wallet');
            selectColor('#2196F3');
        }, 100);
    }
};

function populateColorGrid() {
    const colorGrid = document.getElementById('colorGrid');
    if (!colorGrid) return;

    const colors = [
        // Neutrals & Whites
        '#FFFFFF', '#F5F5F5', '#E0E0E0', '#BDBDBD', '#9E9E9E',
        // Grays & Blacks
        '#757575', '#616161', '#424242', '#212121', '#000000',
        // Reds
        '#FFCDD2', '#EF9A9A', '#E57373', '#EF5350', '#F44336',
        '#E53935', '#D32F2F', '#C62828', '#B71C1C', '#FF5252',
        // Pinks
        '#F8BBD0', '#F48FB1', '#F06292', '#EC407A', '#E91E63',
        // Purples
        '#E1BEE7', '#CE93D8', '#BA68C8', '#AB47BC', '#9C27B0',
        // Deep Purples
        '#D1C4E9', '#B39DDB', '#9575CD', '#7E57C2', '#673AB7',
        // Indigos
        '#C5CAE9', '#9FA8DA', '#7986CB', '#5C6BC0', '#3F51B5',
        // Blues
        '#BBDEFB', '#90CAF9', '#64B5F6', '#42A5F5', '#2196F3',
        '#1E88E5', '#1976D2', '#1565C0', '#0D47A1', '#448AFF',
        // Light Blues
        '#B3E5FC', '#81D4FA', '#4FC3F7', '#29B6F6', '#03A9F4',
        // Cyans
        '#B2EBF2', '#80DEEA', '#4DD0E1', '#26C6DA', '#00BCD4',
        // Teals
        '#B2DFDB', '#80CBC4', '#4DB6AC', '#26A69A', '#009688',
        // Greens
        '#C8E6C9', '#A5D6A7', '#81C784', '#66BB6A', '#4CAF50',
        '#43A047', '#388E3C', '#2E7D32', '#1B5E20', '#69F0AE',
        // Light Greens
        '#DCEDC8', '#C5E1A5', '#AED581', '#9CCC65', '#8BC34A',
        // Limes
        '#F0F4C3', '#E6EE9C', '#DCE775', '#D4E157', '#CDDC39',
        // Yellows
        '#FFF9C4', '#FFF59D', '#FFF176', '#FFEE58', '#FFEB3B',
        '#FDD835', '#FBC02D', '#F9A825', '#F57F17', '#FFFF00',
        // Ambers
        '#FFECB3', '#FFE082', '#FFD54F', '#FFCA28', '#FFC107',
        // Oranges
        '#FFE0B2', '#FFCC80', '#FFB74D', '#FFA726', '#FF9800',
        '#FB8C00', '#F57C00', '#EF6C00', '#E65100', '#FF9100',
        // Deep Oranges
        '#FFCCBC', '#FFAB91', '#FF8A65', '#FF7043', '#FF5722',
        // Browns
        '#D7CCC8', '#BCAAA4', '#A1887F', '#8D6E63', '#795548',
        '#6D4C41', '#5D4037', '#4E342E', '#3E2723', '#8D6E63'
    ];

    colorGrid.innerHTML = colors.map(color => `
        <div class="color-option" data-color="${color}" style="
            width: 32px; 
            height: 32px; 
            background: ${color}; 
            border: 2px solid #3C3C3E; 
            border-radius: 6px; 
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: inset 0 0 0 1px rgba(0,0,0,0.1);
        " onclick="selectColor('${color}')">
        </div>
    `).join('');

    // Select white by default
    selectColor('#FFFFFF');
}

window.selectColor = function (colorCode) {
    const hiddenInput = document.getElementById('newCategoryColor');
    if (hiddenInput) hiddenInput.value = colorCode;

    // Update visual selection
    document.querySelectorAll('.color-option').forEach(opt => {
        if (opt.dataset.color === colorCode) {
            opt.style.borderColor = '#007AFF';
            opt.style.borderWidth = '3px';
            opt.style.transform = 'scale(1.1)';
        } else {
            opt.style.borderColor = '#3C3C3E';
            opt.style.borderWidth = '2px';
            opt.style.transform = 'scale(1)';
        }
    });
};

function populateIconGrid() {
    const iconGrid = document.getElementById('iconGrid');
    if (!iconGrid) return;

    const icons = [
        // Money & Finance
        'fa-money-bill-wave', 'fa-dollar-sign', 'fa-coins', 'fa-wallet', 'fa-credit-card', 'fa-piggy-bank',
        // Food & Drinks
        'fa-utensils', 'fa-coffee', 'fa-burger', 'fa-pizza-slice', 'fa-wine-glass', 'fa-mug-hot',
        // Transport
        'fa-car', 'fa-bus', 'fa-train', 'fa-plane', 'fa-bicycle', 'fa-motorcycle', 'fa-taxi', 'fa-gas-pump',
        // Home & Living
        'fa-house', 'fa-bed', 'fa-couch', 'fa-door-open', 'fa-key', 'fa-lightbulb',
        // Shopping & Retail
        'fa-bag-shopping', 'fa-cart-shopping', 'fa-basket-shopping', 'fa-store', 'fa-gift', 'fa-shirt',
        // Health & Fitness
        'fa-heart-pulse', 'fa-hospital', 'fa-pills', 'fa-syringe', 'fa-dumbbell', 'fa-person-running',
        // Entertainment
        'fa-film', 'fa-music', 'fa-gamepad', 'fa-tv', 'fa-headphones', 'fa-camera',
        // Work & Education
        'fa-briefcase', 'fa-laptop-code', 'fa-graduation-cap', 'fa-book', 'fa-pen', 'fa-paperclip',
        // Technology
        'fa-mobile', 'fa-desktop', 'fa-laptop', 'fa-wifi', 'fa-plug', 'fa-battery-full',
        // Utilities
        'fa-bolt', 'fa-droplet', 'fa-fire', 'fa-wind', 'fa-snowflake', 'fa-sun',
        // Misc
        'fa-circle-question', 'fa-circle-check', 'fa-circle-xmark', 'fa-star', 'fa-bell', 'fa-calendar'
    ];

    iconGrid.innerHTML = icons.map(icon => `
        <div class="icon-option" data-icon="${icon}" style="
            width: 40px; 
            height: 40px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            background: #1C1C1E; 
            border: 2px solid #3C3C3E; 
            border-radius: 8px; 
            cursor: pointer;
            transition: all 0.2s;
        " onclick="selectIcon('${icon}')">
            <i class="fa-solid ${icon}" style="color: #FFFFFF; font-size: 18px;"></i>
        </div>
    `).join('');
}

window.selectIcon = function (iconName) {
    const hiddenInput = document.getElementById('newCategoryIcon');
    if (hiddenInput) hiddenInput.value = iconName;

    // Update visual selection
    document.querySelectorAll('.icon-option').forEach(opt => {
        if (opt.dataset.icon === iconName) {
            opt.style.borderColor = '#007AFF';
            opt.style.background = '#1A4F7A';
        } else {
            opt.style.borderColor = '#3C3C3E';
            opt.style.background = '#1C1C1E';
        }
    });
};

window.closeCreateCategoryModal = function () {
    const modal = document.getElementById('createCategoryModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.add('hidden');

        // Reset form
        const form = document.getElementById('createCategoryForm');
        if (form) form.reset();
    }
};

async function handleCreateCategory(e) {
    e.preventDefault();

    const name = document.getElementById('newCategoryName').value.trim();
    const type = document.getElementById('newCategoryType').value;
    const icon = document.getElementById('newCategoryIcon').value.trim();
    const color = document.getElementById('newCategoryColor').value.trim();
    const selectedAccount = document.getElementById('account')?.value || '';
    const activeType = document.querySelector('.type-tab.active')?.dataset.type || 'expense';

    // Debug: Log los valores
    console.log('DEBUG handleCreateCategory:');
    console.log('  name:', name, '| isEmpty:', !name);
    console.log('  type:', type, '| isEmpty:', !type);
    console.log('  icon:', icon, '| isEmpty:', !icon);
    console.log('  color:', color, '| isEmpty:', !color);

    if (!name || !type || !icon || !color) {
        console.error('Validación fallida - Campos vacíos detectados');
        alert('Por favor completa todos los campos obligatorios (nombre, tipo, ícono y color)');
        return;
    }

    const categoryData = {
        name: name,
        category_type: type,
        icon: icon,
        color: color
    };

    console.log('Enviando categoryData:', categoryData);

    try {
        const created = await api.createCategory(categoryData);
        const newCategoryId = created?.category?.id || created?.id;
        const newCategoryType = created?.category?.type || type || activeType;

        alert('¡Categoría creada exitosamente!');

        // Solo recargar categorías para evitar perder selección de cuenta
        categories = await api.getCategories();

        // Asegurar que el tipo activo corresponde al de la categoría creada
        const typeBtnToActivate = document.querySelector(`.type-tab[data-type="${newCategoryType}"]`);
        if (typeBtnToActivate) {
            document.querySelectorAll('.type-tab').forEach(b => b.classList.remove('active'));
            typeBtnToActivate.classList.add('active');
        }

        populateCategories();

        // Seleccionar la nueva categoría si tenemos el id
        const categorySelect = document.getElementById('category');
        if (categorySelect && newCategoryId) {
            categorySelect.value = newCategoryId;
            selectedCategoryId = newCategoryId;
            updateCategoryPreview();
        }

        // Restaurar la cuenta seleccionada previamente
        const accountSelect = document.getElementById('account');
        if (accountSelect && selectedAccount) {
            accountSelect.value = selectedAccount;
        }

        closeCreateCategoryModal();
    } catch (err) {
        console.error('Error creando categoría:', err);
        alert('Error al crear la categoría: ' + (err.message || 'Error desconocido'));
    }
}
