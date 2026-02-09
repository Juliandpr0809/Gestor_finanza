/**
 * API Client para FinanceFlow
 */

console.log('api.js loaded');

// Detectar automáticamente la URL base del API
const getAPIBaseURL = () => {
    // Si estamos en despliegues conocidos, usar el mismo host
    if (
        window.location.hostname.includes('devtunnels') ||
        window.location.hostname.includes('azurewebsites') ||
        window.location.hostname.includes('herokuapp') ||
        window.location.hostname.includes('pythonanywhere')
    ) {
        return `${window.location.protocol}//${window.location.host}/api`;
    }
    // En desarrollo local, usar localhost:5000
    return 'http://localhost:5000/api';
};

const API_BASE_URL = getAPIBaseURL();
console.log('API Base URL:', API_BASE_URL);

// Clave única para el token en localStorage (usar 'token' para consistencia)
const TOKEN_KEY = 'token';

class APIClient {
    constructor() {
        // Intentar leer el token; si existe uno viejo, migrarlo
        const legacy1 = localStorage.getItem('auth_token');
        const legacy2 = localStorage.getItem('accessToken');
        const current = localStorage.getItem(TOKEN_KEY);
        
        this.token = current || legacy2 || legacy1;
        
        // Migrar tokens antiguos
        if ((legacy1 || legacy2) && !current) {
            localStorage.setItem(TOKEN_KEY, this.token);
            localStorage.removeItem('auth_token');
            localStorage.removeItem('accessToken');
        }
    }

    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem(TOKEN_KEY, token);
        } else {
            localStorage.removeItem(TOKEN_KEY);
        }
        // Limpia también las claves antiguas por si acaso
        localStorage.removeItem('auth_token');
        localStorage.removeItem('accessToken');
    }

    getToken() {
        return this.token;
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            ...options,
            headers,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth endpoints
    async register(email, password, username) {
        const data = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password, username }),
        });
        this.setToken(data.access_token);
        return data;
    }

    async login(identifier, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ identifier, password }),
        });
        this.setToken(data.access_token);
        return data;
    }

    async logout() {
        await this.request('/auth/logout', { method: 'POST' });
        this.setToken(null);
    }

    async getCurrentUser() {
        return await this.request('/auth/me');
    }

    // Accounts endpoints
    async getAccounts() {
        return await this.request('/accounts');
    }

    async createAccount(accountData) {
        return await this.request('/accounts', {
            method: 'POST',
            body: JSON.stringify(accountData),
        });
    }

    async updateAccount(id, accountData) {
        return await this.request(`/accounts/${id}`, {
            method: 'PUT',
            body: JSON.stringify(accountData),
        });
    }

    async deleteAccount(id) {
        return await this.request(`/accounts/${id}`, {
            method: 'DELETE',
        });
    }

    // Transactions endpoints
    async getTransactions(params = {}) {
        const query = new URLSearchParams(params).toString();
        return await this.request(`/transactions${query ? '?' + query : ''}`);
    }

    async createTransaction(transactionData) {
        return await this.request('/transactions', {
            method: 'POST',
            body: JSON.stringify(transactionData),
        });
    }

    async updateTransaction(id, transactionData) {
        return await this.request(`/transactions/${id}`, {
            method: 'PUT',
            body: JSON.stringify(transactionData),
        });
    }

    async deleteTransaction(id) {
        return await this.request(`/transactions/${id}`, {
            method: 'DELETE',
        });
    }

    // Categories endpoints
    async getCategories() {
        return await this.request('/categories');
    }

    async createCategory(categoryData) {
        return await this.request('/categories', {
            method: 'POST',
            body: JSON.stringify(categoryData),
        });
    }

    async suggestCategoryWithAI(description, type = 'expense', language = 'es') {
        return await this.request('/categories/suggest', {
            method: 'POST',
            body: JSON.stringify({ description, type, language }),
        });
    }

    // Chat endpoints
    async initChat() {
        return await this.request('/chat/init', { method: 'POST' });
    }

    async setCurrency(currency) {
        return await this.request('/chat/set-currency', {
            method: 'POST',
            body: JSON.stringify({ currency })
        });
    }

    async sendChatMessage(content) {
        return await this.request('/chat/send', {
            method: 'POST',
            body: JSON.stringify({ content }),
        });
    }

    async getChatMessages(page = 1) {
        return await this.request(`/chat/messages?page=${page}`);
    }

    async getSpendingAnalysis() {
        return await this.request('/chat/analyze');
    }

    async clearChatHistory() {
        return await this.request('/chat/clear', {
            method: 'POST',
        });
    }
}

// Inicializar instancia global inmediatamente
console.log('Creating api instance...');
window.api = new APIClient();
console.log('api instance created:', typeof window.api);
