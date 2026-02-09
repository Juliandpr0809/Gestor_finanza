// ==========================================
// SCAN RECEIPT - OCR FUNCTIONALITY
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const uploadZone = document.getElementById('uploadZone');
    const uploadContainer = document.getElementById('uploadContainer');
    const receiptInput = document.getElementById('receiptInput');
    const browseBtn = document.getElementById('browseBtn');
    const previewArea = document.getElementById('previewArea');
    const previewImage = document.getElementById('previewImage');
    const removeImageBtn = document.getElementById('removeImageBtn');
    const rotateBtn = document.getElementById('rotateBtn');
    const processBtn = document.getElementById('processBtn');
    const processingState = document.getElementById('processingState');
    const dataSection = document.getElementById('dataSection');
    const extractedForm = document.getElementById('extractedForm');
    const cancelBtn = document.getElementById('cancelBtn');
    const addItemBtn = document.getElementById('addItemBtn');
    const itemsList = document.getElementById('itemsList');
    const itemCount = document.getElementById('itemCount');

    let currentRotation = 0;
    let selectedFile = null;

    // Browse button
    browseBtn.addEventListener('click', () => {
        receiptInput.click();
    });

    // Click upload zone
    uploadZone.addEventListener('click', () => {
        receiptInput.click();
    });

    // File input change
    receiptInput.addEventListener('change', (e) => {
        handleFile(e.target.files[0]);
    });

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    // Handle file selection
    function handleFile(file) {
        if (!file) return;

        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
        if (!validTypes.includes(file.type)) {
            alert('Please upload a valid image (JPG, PNG) or PDF file');
            return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('File size must be less than 10MB');
            return;
        }

        selectedFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            uploadZone.classList.add('hidden');
            previewArea.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }

    // Remove image
    removeImageBtn.addEventListener('click', () => {
        selectedFile = null;
        receiptInput.value = '';
        previewImage.src = '';
        currentRotation = 0;
        previewArea.classList.add('hidden');
        uploadZone.classList.remove('hidden');
    });

    // Rotate image
    rotateBtn.addEventListener('click', () => {
        currentRotation = (currentRotation + 90) % 360;
        previewImage.style.transform = `rotate(${currentRotation}deg)`;
    });

    // Process receipt
    processBtn.addEventListener('click', () => {
        processReceipt();
    });

    // Process receipt with animation
    function processReceipt() {
        // Hide preview, show processing
        previewArea.classList.add('hidden');
        processingState.classList.remove('hidden');

        // Simulate processing steps
        setTimeout(() => {
            document.getElementById('step2').classList.add('active');
            document.getElementById('step2').querySelector('i').className = 'fas fa-check-circle';
        }, 1000);

        setTimeout(() => {
            document.getElementById('step3').classList.add('active');
            document.getElementById('step3').querySelector('i').className = 'fas fa-spinner fa-spin';
        }, 2000);

        setTimeout(() => {
            document.getElementById('step3').querySelector('i').className = 'fas fa-check-circle';
            document.getElementById('step4').classList.add('active');
            document.getElementById('step4').querySelector('i').className = 'fas fa-spinner fa-spin';
        }, 3000);

        setTimeout(() => {
            document.getElementById('step4').querySelector('i').className = 'fas fa-check-circle';
            
            // Show extracted data
            processingState.classList.add('hidden');
            dataSection.classList.remove('hidden');
            
            // Fill form with extracted data (simulated)
            fillExtractedData();
        }, 4000);
    }

    // Fill form with simulated extracted data
    function fillExtractedData() {
        const merchants = [
            { name: 'Whole Foods Market', category: 'groceries', amount: 127.45 },
            { name: 'Starbucks', category: 'food', amount: 8.50 },
            { name: 'Target', category: 'shopping', amount: 89.99 },
            { name: 'Shell Gas Station', category: 'transport', amount: 45.00 },
            { name: 'CVS Pharmacy', category: 'health', amount: 34.75 }
        ];

        const randomMerchant = merchants[Math.floor(Math.random() * merchants.length)];

        // Fill basic info
        document.getElementById('merchant').value = randomMerchant.name;
        document.getElementById('amount').value = randomMerchant.amount.toFixed(2);
        document.getElementById('category').value = randomMerchant.category;
        document.getElementById('date').value = new Date().toISOString().split('T')[0];
        document.getElementById('account').value = 'main';

        // Add sample items
        const sampleItems = [
            { name: 'Item 1', price: (randomMerchant.amount * 0.4).toFixed(2) },
            { name: 'Item 2', price: (randomMerchant.amount * 0.35).toFixed(2) },
            { name: 'Item 3', price: (randomMerchant.amount * 0.25).toFixed(2) }
        ];

        itemsList.innerHTML = '';
        sampleItems.forEach(item => addItem(item.name, item.price));

        // Set original receipt preview
        document.getElementById('originalReceipt').src = previewImage.src;

        // Update confidence (random between 85-98%)
        const confidence = Math.floor(Math.random() * 13) + 85;
        document.getElementById('confidenceBadge').innerHTML = `
            <i class="fas fa-check-circle"></i>
            ${confidence}% Confidence
        `;
    }

    // Add item to list
    function addItem(name = '', price = '') {
        const itemRow = document.createElement('div');
        itemRow.className = 'item-row';
        itemRow.innerHTML = `
            <input type="text" placeholder="Item name" value="${name}">
            <input type="number" step="0.01" placeholder="0.00" value="${price}">
            <button type="button" class="btn-remove-item" onclick="this.parentElement.remove(); updateItemCount();">
                <i class="fas fa-times"></i>
            </button>
        `;
        itemsList.appendChild(itemRow);
        updateItemCount();
    }

    // Add item button
    addItemBtn.addEventListener('click', () => {
        addItem();
    });

    // Update item count
    window.updateItemCount = function() {
        const count = itemsList.children.length;
        itemCount.textContent = `${count} item${count !== 1 ? 's' : ''}`;
    };

    // Cancel button
    cancelBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to cancel? All extracted data will be lost.')) {
            resetScanner();
        }
    });

    // Form submission
    extractedForm.addEventListener('submit', (e) => {
        e.preventDefault();

        // Get form data
        const formData = {
            merchant: document.getElementById('merchant').value,
            amount: parseFloat(document.getElementById('amount').value),
            date: document.getElementById('date').value,
            category: document.getElementById('category').value,
            account: document.getElementById('account').value,
            notes: document.getElementById('notes').value,
            items: []
        };

        // Get items
        const itemRows = itemsList.querySelectorAll('.item-row');
        itemRows.forEach(row => {
            const inputs = row.querySelectorAll('input');
            if (inputs[0].value && inputs[1].value) {
                formData.items.push({
                    name: inputs[0].value,
                    price: parseFloat(inputs[1].value)
                });
            }
        });

        // Save transaction (simulate)
        console.log('Saving transaction:', formData);
        
        // Show success message
        alert('✅ Transaction saved successfully!');
        
        // Reset scanner
        resetScanner();
    });

    // Reset scanner to initial state
    function resetScanner() {
        selectedFile = null;
        receiptInput.value = '';
        previewImage.src = '';
        currentRotation = 0;
        
        previewArea.classList.add('hidden');
        processingState.classList.add('hidden');
        dataSection.classList.add('hidden');
        uploadZone.classList.remove('hidden');
        
        // Reset processing steps
        document.querySelectorAll('.step').forEach((step, index) => {
            if (index === 0) {
                step.classList.add('active');
                step.querySelector('i').className = 'fas fa-check-circle';
            } else {
                step.classList.remove('active');
                step.querySelector('i').className = 'fas fa-circle';
            }
        });

        // Clear form
        extractedForm.reset();
        itemsList.innerHTML = '';
        updateItemCount();
    }

    // Camera button (simulation)
    document.getElementById('cameraBtn').addEventListener('click', () => {
        alert('📸 Camera feature coming soon!\n\nThis will allow you to capture receipts directly from your device camera.');
    });
});
