// Data Store
const dataStore = {
  accounts: [
    { id: 1, name: "Checking", balance: 3567.37, currency: "$", type: "checking" },
    { id: 2, name: "Savings", balance: 12450.0, currency: "$", type: "savings" },
    { id: 3, name: "Investment", balance: 24890.5, currency: "$", type: "investment" },
  ],
  transactions: [
    {
      id: 1,
      name: "Apple Store",
      amount: -49.99,
      category: "Shopping",
      date: "2025-12-03",
      type: "expense",
      icon: "🛍️",
    },
    {
      id: 2,
      name: "Salary Deposit",
      amount: 4500.0,
      category: "Income",
      date: "2025-12-01",
      type: "income",
      icon: "💰",
    },
    {
      id: 3,
      name: "Netflix Subscription",
      amount: -15.99,
      category: "Entertainment",
      date: "2025-11-28",
      type: "expense",
      icon: "🎬",
    },
    {
      id: 4,
      name: "Whole Foods",
      amount: -87.43,
      category: "Groceries",
      date: "2025-11-27",
      type: "expense",
      icon: "🛒",
    },
    {
      id: 5,
      name: "Gas Station",
      amount: -52.3,
      category: "Transport",
      date: "2025-11-26",
      type: "expense",
      icon: "⛽",
    },
  ],
  categories: [
    { name: "Shopping", icon: "🛍️", color: "var(--accent-cyan)" },
    { name: "Food", icon: "🍔", color: "var(--accent-green)" },
    { name: "Transport", icon: "🚗", color: "var(--accent-orange)" },
    { name: "Entertainment", icon: "🎬", color: "var(--accent-cyan)" },
    { name: "Utilities", icon: "💡", color: "var(--accent-red)" },
  ],
}

// Initialize App solo si existe contenedor SPA
document.addEventListener("DOMContentLoaded", () => {
    const app = document.getElementById("app")
    if (app) {
        renderApp()
        setupEventListeners()
    }
})

function renderApp() {
  const app = document.getElementById("app")

  app.innerHTML = `
        <div class="app-container">
            <div class="sidebar">
                <ul class="nav-menu">
                    <li class="nav-item active" data-page="dashboard">
                        <span class="nav-icon">📊</span>
                        <span>Dashboard</span>
                    </li>
                    <li class="nav-item" data-page="transactions">
                        <span class="nav-icon">💸</span>
                        <span>Transactions</span>
                    </li>
                    <li class="nav-item" data-page="add-transaction">
                        <span class="nav-icon">➕</span>
                        <span>Add Transaction</span>
                    </li>
                    <li class="nav-item" data-page="ocr">
                        <span class="nav-icon">📸</span>
                        <span>Receipt Scanner</span>
                    </li>
                    <li class="nav-item" data-page="voice">
                        <span class="nav-icon">🎤</span>
                        <span>Voice Input</span>
                    </li>
                    <li class="nav-item" data-page="accounts">
                        <span class="nav-icon">🏦</span>
                        <span>Accounts</span>
                    </li>
                    <li class="nav-item" data-page="analytics">
                        <span class="nav-icon">📈</span>
                        <span>Analytics</span>
                    </li>
                </ul>
            </div>
            
            <div class="main-content">
                <div class="header">
                    <div class="header-title">
                        <div class="header-icon">FF</div>
                        <span>FinFlow</span>
                    </div>
                    <div class="nav-buttons">
                        <button class="btn btn-secondary btn-sm">Settings</button>
                        <button class="btn btn-primary btn-sm">Export</button>
                    </div>
                </div>
                
                <div class="content-wrapper">
                    <div id="dashboard" class="page active">${renderDashboard()}</div>
                    <div id="transactions" class="page">${renderTransactions()}</div>
                    <div id="add-transaction" class="page">${renderAddTransaction()}</div>
                    <div id="ocr" class="page">${renderOCR()}</div>
                    <div id="voice" class="page">${renderVoice()}</div>
                    <div id="accounts" class="page">${renderAccounts()}</div>
                    <div id="analytics" class="page">${renderAnalytics()}</div>
                </div>
            </div>
        </div>
        
        <div id="transaction-modal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Transaction Details</h2>
                    <button class="modal-close">&times;</button>
                </div>
                <div id="modal-body"></div>
            </div>
        </div>
    `
}

function renderDashboard() {
  const currentAccount = dataStore.accounts[0]
  const income = dataStore.transactions.filter((t) => t.type === "income").reduce((sum, t) => sum + t.amount, 0)
  const expenses = Math.abs(
    dataStore.transactions.filter((t) => t.type === "expense").reduce((sum, t) => sum + t.amount, 0),
  )

  return `
        <h1>Dashboard</h1>
        
        <div class="dashboard-grid">
            <div class="balance-card">
                <div class="card-title">Primary Account</div>
                <div class="balance-value">${currentAccount.currency}${currentAccount.balance.toFixed(2)}</div>
                <div class="balance-account">${currentAccount.name}</div>
                <div class="balance-change positive">
                    <span>↑</span>
                    <span>+12.5% this month</span>
                </div>
            </div>
            
            <div class="balance-card">
                <div class="card-title">Monthly Income</div>
                <div class="balance-value" style="color: var(--accent-green);">${currentAccount.currency}${income.toFixed(2)}</div>
                <div class="balance-account">From all sources</div>
                <div class="balance-change positive">
                    <span>✓</span>
                    <span>On track</span>
                </div>
            </div>
            
            <div class="balance-card">
                <div class="card-title">Monthly Expenses</div>
                <div class="balance-value" style="color: var(--accent-red);">${currentAccount.currency}${expenses.toFixed(2)}</div>
                <div class="balance-account">All categories</div>
                <div class="balance-change negative">
                    <span>↑</span>
                    <span>+8% vs last month</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>Recent Transactions</h3>
            <div style="margin-top: var(--spacing-lg);">
                ${dataStore.transactions
                  .slice(0, 5)
                  .map(
                    (t) => `
                    <div class="transaction-item">
                        <div class="flex" style="flex: 1; align-items: center;">
                            <div class="transaction-icon">${t.icon}</div>
                            <div class="transaction-info">
                                <div>${t.name}</div>
                                <div style="font-size: 12px; color: var(--text-tertiary);">${t.category}</div>
                            </div>
                        </div>
                        <div class="transaction-amount ${t.type === "income" ? "positive" : "negative"}">
                            ${t.type === "income" ? "+" : ""}${t.currency || "$"}${Math.abs(t.amount).toFixed(2)}
                        </div>
                    </div>
                `,
                  )
                  .join("")}
            </div>
        </div>
    `
}

function renderTransactions() {
  return `
        <h1>All Transactions</h1>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--spacing-lg); margin-bottom: var(--spacing-lg);">
            <div class="card">
                <div class="card-title">Filter by Category</div>
                <select class="form-select" id="category-filter" style="margin-top: var(--spacing-md);">
                    <option value="">All Categories</option>
                    ${dataStore.categories.map((cat) => `<option value="${cat.name}">${cat.name}</option>`).join("")}
                </select>
            </div>
        </div>
        
        <div class="card">
            <h3>Transactions</h3>
            <div style="margin-top: var(--spacing-lg);">
                ${dataStore.transactions
                  .map(
                    (t) => `
                    <div class="transaction-item" data-id="${t.id}" data-category="${t.category}">
                        <div class="flex" style="flex: 1; align-items: center;">
                            <div class="transaction-icon">${t.icon}</div>
                            <div class="transaction-info">
                                <div>${t.name}</div>
                                <div style="font-size: 12px; color: var(--text-tertiary);">${t.category} • ${t.date}</div>
                            </div>
                        </div>
                        <div class="transaction-amount ${t.type === "income" ? "positive" : "negative"}">
                            ${t.type === "income" ? "+" : ""}$${Math.abs(t.amount).toFixed(2)}
                        </div>
                    </div>
                `,
                  )
                  .join("")}
            </div>
        </div>
    `
}

function renderAddTransaction() {
  return `
        <h1>Add New Transaction</h1>
        
        <div class="form-container">
            <form id="transaction-form">
                <div class="form-section">
                    <div class="form-group">
                        <label class="form-label">Transaction Type</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md);">
                            <button type="button" class="btn btn-secondary transaction-type-btn active" data-type="expense">
                                💸 Expense
                            </button>
                            <button type="button" class="btn btn-secondary transaction-type-btn" data-type="income">
                                💰 Income
                            </button>
                        </div>
                        <input type="hidden" id="transaction-type" value="expense">
                    </div>
                </div>
                
                <div class="form-section">
                    <div class="form-group">
                        <label class="form-label">Description</label>
                        <input id="transaction-description" type="text" class="form-input" placeholder="e.g., Coffee at Starbucks" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Amount</label>
                        <input id="transaction-amount" type="number" class="form-input" placeholder="0.00" step="0.01" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Category</label>
                        <select id="transaction-category" class="form-select" required>
                            <option value="">Select a category</option>
                            ${dataStore.categories.map((cat) => `<option value="${cat.name}">${cat.icon} ${cat.name}</option>`).join("")}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Date</label>
                        <input id="transaction-date" type="date" class="form-input" value="2025-12-04" required>
                    </div>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Save Transaction</button>
                    <button type="reset" class="btn btn-secondary">Clear</button>
                </div>
            </form>
        </div>
    `
}

function renderOCR() {
  return `
        <h1>Receipt Scanner (OCR)</h1>
        
        <div class="card" style="margin-bottom: var(--spacing-lg); padding: var(--spacing-xl); text-align: center;">
            <div style="font-size: 48px; margin-bottom: var(--spacing-md);">📷</div>
            <h3>Upload Receipt</h3>
            <p>Scan or upload a receipt image to automatically extract transaction details</p>
            <div style="margin-top: var(--spacing-lg);">
                <label for="receipt-upload" class="btn btn-primary">
                    Choose File
                </label>
                <input type="file" id="receipt-upload" accept="image/*" style="display: none;">
            </div>
        </div>
        
        <div id="receipt-result" style="display: none;">
            <div class="receipt-container">
                <div class="receipt-image">
                    <img id="receipt-image-preview" src="/placeholder.svg" alt="Receipt">
                </div>
                
                <div class="receipt-data">
                    <div class="card">
                        <h3>Extracted Data</h3>
                        <div class="form-group" style="margin-top: var(--spacing-lg);">
                            <label class="form-label">Store Name</label>
                            <input type="text" class="form-input" id="ocr-store" placeholder="Store name" value="Whole Foods Market">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Total Amount</label>
                            <input type="number" class="form-input" id="ocr-total" placeholder="0.00" step="0.01" value="127.43">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Date</label>
                            <input type="date" class="form-input" id="ocr-date" value="2025-12-04">
                        </div>
                        <button class="btn btn-primary" style="width: 100%; margin-top: var(--spacing-lg);">
                            Save Transaction
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="receipt-items">
                <h3 style="margin-bottom: var(--spacing-lg);">Items</h3>
                <div class="receipt-item">
                    <div class="receipt-item-name">Organic Vegetables</div>
                    <div class="receipt-item-price">$24.99</div>
                </div>
                <div class="receipt-item">
                    <div class="receipt-item-name">Greek Yogurt</div>
                    <div class="receipt-item-price">$8.49</div>
                </div>
                <div class="receipt-item">
                    <div class="receipt-item-name">Coffee Beans</div>
                    <div class="receipt-item-price">$12.99</div>
                </div>
                <div class="receipt-item">
                    <div class="receipt-item-name">Whole Grain Bread</div>
                    <div class="receipt-item-price">$6.49</div>
                </div>
                <div class="receipt-item">
                    <div class="receipt-item-name">Fresh Salmon</div>
                    <div class="receipt-item-price">$34.99</div>
                </div>
                <div class="receipt-item" style="border-bottom: 2px solid var(--border-color); font-weight: 600;">
                    <div class="receipt-item-name">Subtotal</div>
                    <div class="receipt-item-price">$87.95</div>
                </div>
                <div class="receipt-item">
                    <div class="receipt-item-name">Tax</div>
                    <div class="receipt-item-price">$7.04</div>
                </div>
                <div class="receipt-item" style="font-weight: 600; color: var(--accent-cyan);">
                    <div class="receipt-item-name">Total</div>
                    <div class="receipt-item-price">$94.99</div>
                </div>
            </div>
        </div>
    `
}

function renderVoice() {
  return `
        <h1>Voice Input</h1>
        
        <div class="form-container" style="max-width: 100%;">
            <div class="voice-input">
                <h2>Speak Your Transaction</h2>
                <p style="color: var(--text-secondary); margin-bottom: var(--spacing-lg);">
                    Try saying: "I spent 45 dollars on groceries" or "I earned 500 dollars freelancing"
                </p>
                
                <button id="voice-btn" class="btn btn-primary" style="width: 200px; height: 200px; border-radius: 50%; font-size: 48px;">
                    🎤
                </button>
                
                <div id="voice-status" style="text-align: center; color: var(--text-secondary);">
                    Click the microphone to start
                </div>
                
                <div class="voice-waveform" id="waveform" style="display: none;">
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                </div>
            </div>
            
            <div id="voice-result" style="display: none; margin-top: var(--spacing-xl);">
                <div class="card">
                    <h3>Recognized Transaction</h3>
                    <div style="margin-top: var(--spacing-lg);">
                        <div class="form-group">
                            <label class="form-label">What You Said</label>
                            <div style="background-color: var(--secondary-bg); padding: var(--spacing-md); border-radius: var(--radius-md); color: var(--text-secondary);" id="voice-transcript">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Amount</label>
                                <input type="number" class="form-input" id="voice-amount" placeholder="0.00">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Type</label>
                                <select class="form-select" id="voice-type">
                                    <option value="expense">Expense</option>
                                    <option value="income">Income</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Category</label>
                            <select class="form-select" id="voice-category">
                                <option value="">Select category</option>
                                ${dataStore.categories.map((cat) => `<option value="${cat.name}">${cat.icon} ${cat.name}</option>`).join("")}
                            </select>
                        </div>
                        
                        <div style="display: flex; gap: var(--spacing-md); margin-top: var(--spacing-lg);">
                            <button class="btn btn-primary" style="flex: 1;">Save</button>
                            <button class="btn btn-secondary" style="flex: 1;">Cancel</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `
}

function renderAccounts() {
  return `
        <h1>Manage Accounts</h1>
        
        <div class="grid grid-2" style="margin-bottom: var(--spacing-xl);">
            ${dataStore.accounts
              .map(
                (account) => `
                <div class="card">
                    <div class="flex-between">
                        <h3>${account.name}</h3>
                        <span style="background-color: var(--secondary-bg); padding: 4px 8px; border-radius: var(--radius-sm); font-size: 12px;">
                            ${account.type}
                        </span>
                    </div>
                    <div style="margin-top: var(--spacing-lg);">
                        <div class="card-title">Current Balance</div>
                        <div style="font-size: 28px; font-weight: 700; margin: var(--spacing-md) 0; color: var(--accent-cyan);">
                            ${account.currency}${account.balance.toFixed(2)}
                        </div>
                        <div style="display: flex; gap: var(--spacing-md); margin-top: var(--spacing-lg);">
                            <button class="btn btn-secondary btn-sm" style="flex: 1;">Edit</button>
                            <button class="btn btn-secondary btn-sm" style="flex: 1;">Delete</button>
                        </div>
                    </div>
                </div>
            `,
              )
              .join("")}
        </div>
        
        <div class="card">
            <h3>Add New Account</h3>
            <form style="margin-top: var(--spacing-lg);">
                <div class="form-group">
                    <label class="form-label">Account Name</label>
                    <input type="text" class="form-input" placeholder="e.g., Emergency Fund">
                </div>
                <div class="form-group">
                    <label class="form-label">Account Type</label>
                    <select class="form-select">
                        <option value="">Select type</option>
                        <option value="checking">Checking</option>
                        <option value="savings">Savings</option>
                        <option value="investment">Investment</option>
                        <option value="credit">Credit Card</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Initial Balance</label>
                    <input type="number" class="form-input" placeholder="0.00" step="0.01">
                </div>
                <button type="submit" class="btn btn-primary">Create Account</button>
            </form>
        </div>
    `
}

function renderAnalytics() {
  return `
        <h1>Analytics & Reports</h1>
        
        <div class="grid grid-2" style="margin-bottom: var(--spacing-lg);">
            <div class="chart-container">
                <div class="chart-title">Spending by Category</div>
                <canvas id="category-chart"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">Income vs Expenses</div>
                <canvas id="income-chart"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">Monthly Trend</div>
            <canvas id="trend-chart"></canvas>
        </div>
    `
}

function setupEventListeners() {
  // Navigation
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.addEventListener("click", (e) => {
      const page = e.currentTarget.getAttribute("data-page")
      switchPage(page)

      document.querySelectorAll(".nav-item").forEach((i) => i.classList.remove("active"))
      e.currentTarget.classList.add("active")
    })
  })

    bindDynamicListeners()

  // Modal close
  const modal = document.getElementById("transaction-modal")
  document.querySelector(".modal-close")?.addEventListener("click", () => {
    modal.classList.remove("active")
  })

  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.classList.remove("active")
  })

  // Charts
  setTimeout(() => drawCharts(), 100)
}

function switchPage(pageName) {
  document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"))
  const page = document.getElementById(pageName)
  if (page) {
    page.classList.add("active")
    if (pageName === "analytics") {
      setTimeout(() => drawCharts(), 100)
    }
  }
}

function drawCharts() {
  // Category Chart
  const categoryCtx = document.getElementById("category-chart")
  if (categoryCtx) {
    const categoryData = {
      Shopping: 49.99,
      Food: 87.43,
      Entertainment: 15.99,
      Transport: 52.3,
      Utilities: 0,
    }
    drawPieChart(categoryCtx, Object.keys(categoryData), Object.values(categoryData), "Category Distribution")
  }

  // Income Chart
  const incomeCtx = document.getElementById("income-chart")
  if (incomeCtx) {
    drawBarChart(incomeCtx, ["Income", "Expenses"], [4500, 205.71], "Monthly Summary")
  }

  // Trend Chart
  const trendCtx = document.getElementById("trend-chart")
  if (trendCtx) {
    drawLineChart(trendCtx, ["Week 1", "Week 2", "Week 3", "Week 4"], [1200, 1450, 1100, 1350], "Spending Trend")
  }
}

function drawPieChart(canvas, labels, data, title) {
  const ctx = canvas.getContext("2d")
  const width = canvas.offsetWidth
  const height = 300
  canvas.width = width
  canvas.height = height

  const centerX = width / 2
  const centerY = height / 2
  const radius = Math.min(width, height) / 2 - 20
  const total = data.reduce((a, b) => a + b, 0)
  const colors = ["#00D9FF", "#00E676", "#FF5252", "#FFB74D", "#B0B0B0"]

  let currentAngle = -Math.PI / 2
  data.forEach((value, i) => {
    const sliceAngle = (value / total) * 2 * Math.PI
    ctx.fillStyle = colors[i % colors.length]
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
    ctx.lineTo(centerX, centerY)
    ctx.fill()
    currentAngle += sliceAngle
  })
}

function drawBarChart(canvas, labels, data, title) {
  const ctx = canvas.getContext("2d")
  const width = canvas.offsetWidth
  const height = 300
  canvas.width = width
  canvas.height = height

  const padding = 40
  const chartWidth = width - 2 * padding
  const chartHeight = height - 2 * padding
  const barWidth = chartWidth / (labels.length * 2)
  const maxValue = Math.max(...data)

  // Draw bars
  const colors = ["#00E676", "#FF5252"]
  data.forEach((value, i) => {
    const x = padding + (i * 2 + 1) * barWidth
    const barHeight = (value / maxValue) * chartHeight
    const y = padding + chartHeight - barHeight

    ctx.fillStyle = colors[i]
    ctx.fillRect(x, y, barWidth * 0.8, barHeight)

    // Labels
    ctx.fillStyle = "#B0B0B0"
    ctx.font = "12px sans-serif"
    ctx.textAlign = "center"
    ctx.fillText(labels[i], x + barWidth * 0.4, height - 10)
    ctx.fillText("$" + value.toFixed(0), x + barWidth * 0.4, y - 5)
  })
}

function drawLineChart(canvas, labels, data, title) {
  const ctx = canvas.getContext("2d")
  const width = canvas.offsetWidth
  const height = 300
  canvas.width = width
  canvas.height = height

  const padding = 40
  const chartWidth = width - 2 * padding
  const chartHeight = height - 2 * padding
  const pointSpacing = chartWidth / (labels.length - 1)
  const maxValue = Math.max(...data)

  // Draw line
  ctx.strokeStyle = "#00D9FF"
  ctx.lineWidth = 3
  ctx.beginPath()
  data.forEach((value, i) => {
    const x = padding + i * pointSpacing
    const y = height - padding - (value / maxValue) * chartHeight
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  })
  ctx.stroke()

  // Draw points
  ctx.fillStyle = "#00D9FF"
  data.forEach((value, i) => {
    const x = padding + i * pointSpacing
    const y = height - padding - (value / maxValue) * chartHeight
    ctx.beginPath()
    ctx.arc(x, y, 5, 0, Math.PI * 2)
    ctx.fill()
  })

  // Labels
  ctx.fillStyle = "#B0B0B0"
  ctx.font = "12px sans-serif"
  ctx.textAlign = "center"
  labels.forEach((label, i) => {
    const x = padding + i * pointSpacing
    ctx.fillText(label, x, height - 10)
  })
}

function bindDynamicListeners() {
    bindTransactionTypeButtons()
    bindForms()
}

function bindTransactionTypeButtons() {
    document.querySelectorAll(".transaction-type-btn").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.preventDefault()
            document.querySelectorAll(".transaction-type-btn").forEach((b) => b.classList.remove("active"))
            e.currentTarget.classList.add("active")
            const type = e.currentTarget.getAttribute("data-type")
            const hidden = document.getElementById("transaction-type")
            if (hidden) hidden.value = type
        })
    })
}

function bindForms() {
    bindAddTransactionForm()
    bindReceiptUpload()
    bindVoiceInput()
    bindCategoryFilter()
}

function bindAddTransactionForm() {
    const form = document.getElementById("transaction-form")
    if (!form) return

    form.addEventListener("submit", (e) => {
        e.preventDefault()

        const type = document.getElementById("transaction-type")?.value || "expense"
        const description = document.getElementById("transaction-description")?.value?.trim()
        const amountValue = parseFloat(document.getElementById("transaction-amount")?.value || "0")
        const category = document.getElementById("transaction-category")?.value || ""
        const date = document.getElementById("transaction-date")?.value || ""

        if (!description || !category || !date || Number.isNaN(amountValue)) return

        const normalizedAmount = type === "income" ? Math.abs(amountValue) : -Math.abs(amountValue)

        dataStore.transactions.unshift({
            id: Date.now(),
            name: description,
            amount: normalizedAmount,
            category,
            date,
            type,
            icon: "💳",
            currency: "$",
        })

        form.reset()
        const hiddenType = document.getElementById("transaction-type")
        if (hiddenType) hiddenType.value = "expense"
        document.querySelectorAll(".transaction-type-btn").forEach((b) => b.classList.remove("active"))
        document.querySelector('.transaction-type-btn[data-type="expense"]')?.classList.add("active")

        refreshUI()
    })
}

function bindReceiptUpload() {
    const uploadInput = document.getElementById("receipt-upload")
    if (!uploadInput) return

    uploadInput.addEventListener("change", (e) => {
        const file = e.target.files?.[0]
        if (!file) return

        const preview = document.getElementById("receipt-image-preview")
        const resultSection = document.getElementById("receipt-result")
        if (preview && resultSection) {
            const reader = new FileReader()
            reader.onload = (ev) => {
                preview.src = ev.target.result
                resultSection.style.display = "block"
            }
            reader.readAsDataURL(file)
        }
    })
}

function bindVoiceInput() {
    const voiceBtn = document.getElementById("voice-btn")
    if (!voiceBtn) return

    const status = document.getElementById("voice-status")
    const waveform = document.getElementById("waveform")
    const result = document.getElementById("voice-result")
    const transcript = document.getElementById("voice-transcript")
    const amountInput = document.getElementById("voice-amount")
    const categorySelect = document.getElementById("voice-category")

    voiceBtn.addEventListener("click", () => {
        if (waveform) waveform.style.display = "flex"
        if (status) status.textContent = "Escuchando..."

        setTimeout(() => {
            if (waveform) waveform.style.display = "none"
            if (status) status.textContent = "Listo"
            if (result) result.style.display = "block"
            if (transcript) transcript.textContent = "Gasté 45 dólares en gasolina"
            if (amountInput) amountInput.value = "45"
            if (categorySelect) categorySelect.value = "Transport"
        }, 1600)
    })
}

function bindCategoryFilter() {
    const filter = document.getElementById("category-filter")
    if (!filter) return

    filter.addEventListener("change", (e) => {
        const value = e.target.value
        document.querySelectorAll(".transaction-item").forEach((item) => {
            const match = !value || item.getAttribute("data-category") === value
            item.style.display = match ? "flex" : "none"
        })
    })
}

function refreshUI() {
    const dashboard = document.getElementById("dashboard")
    if (dashboard) dashboard.innerHTML = renderDashboard()

    const transactions = document.getElementById("transactions")
    if (transactions) transactions.innerHTML = renderTransactions()

    const addTransaction = document.getElementById("add-transaction")
    if (addTransaction) addTransaction.innerHTML = renderAddTransaction()

    const analytics = document.getElementById("analytics")
    if (analytics) analytics.innerHTML = renderAnalytics()

    const accounts = document.getElementById("accounts")
    if (accounts) accounts.innerHTML = renderAccounts()

    bindDynamicListeners()

    const activePage = document.querySelector(".page.active")
    if (activePage && activePage.id === "analytics") {
        setTimeout(() => drawCharts(), 50)
    }
}
