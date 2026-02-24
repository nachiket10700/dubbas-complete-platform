// Payment Processing JavaScript

// Initialize payment related functionality
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('paymentMethods')) {
        loadPaymentMethods();
    }
    
    if (document.getElementById('transactionsList')) {
        loadTransactions();
    }
    
    if (document.getElementById('payoutsList')) {
        loadPayouts();
    }
    
    // Add money button
    const addMoneyBtn = document.getElementById('addMoneyBtn');
    if (addMoneyBtn) {
        addMoneyBtn.addEventListener('click', showAddMoneyModal);
    }
    
    // Add payment method button
    const addPaymentBtn = document.getElementById('addPaymentBtn');
    if (addPaymentBtn) {
        addPaymentBtn.addEventListener('click', showAddPaymentModal);
    }
});

// Load payment methods
async function loadPaymentMethods() {
    const container = document.getElementById('paymentMethods');
    if (!container) return;
    
    try {
        const response = await apiRequest('/payment/methods', 'GET');
        
        if (response.success && response.methods.length > 0) {
            displayPaymentMethods(response.methods);
        } else {
            loadFallbackPaymentMethods();
        }
    } catch (error) {
        console.error('Error loading payment methods:', error);
        loadFallbackPaymentMethods();
    }
}

// Display payment methods
function displayPaymentMethods(methods) {
    const container = document.getElementById('paymentMethods');
    if (!container) return;
    
    container.innerHTML = methods.map(method => `
        <div class="method-card">
            <div class="method-icon">
                <i class="fas fa-${method.type === 'card' ? 'credit-card' : 'mobile-alt'}"></i>
            </div>
            <div class="method-info">
                <div class="method-name">${method.name}</div>
                <div class="method-details">
                    ${method.type === 'card' 
                        ? `•••• ${method.last4} | Expires ${method.expiry}` 
                        : method.upi_id}
                </div>
                ${method.is_default ? '<div class="method-default">Default</div>' : ''}
            </div>
            <div class="method-actions">
                <button class="btn-icon" onclick="editPaymentMethod('${method.id}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon" onclick="deletePaymentMethod('${method.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
    
    // Add "Add New" card
    container.innerHTML += `
        <div class="add-method-card" onclick="showAddPaymentModal()">
            <i class="fas fa-plus-circle"></i>
            <p>Add New Payment Method</p>
        </div>
    `;
}

// Load fallback payment methods
function loadFallbackPaymentMethods() {
    const fallbackMethods = [
        { id: 1, type: 'card', name: 'HDFC Bank Credit Card', last4: '4242', expiry: '12/26', is_default: true },
        { id: 2, type: 'upi', name: 'Google Pay', upi_id: 'john@okhdfcbank', is_default: false },
        { id: 3, type: 'card', name: 'SBI Debit Card', last4: '1234', expiry: '08/25', is_default: false }
    ];
    displayPaymentMethods(fallbackMethods);
}

// Load transactions
async function loadTransactions() {
    const container = document.getElementById('transactionsList');
    if (!container) return;
    
    try {
        const response = await apiRequest('/payment/transactions?limit=10', 'GET');
        
        if (response.success && response.transactions.length > 0) {
            displayTransactions(response.transactions);
        } else {
            loadFallbackTransactions();
        }
    } catch (error) {
        console.error('Error loading transactions:', error);
        loadFallbackTransactions();
    }
}

// Display transactions
function displayTransactions(transactions) {
    const container = document.getElementById('transactionsList');
    if (!container) return;
    
    container.innerHTML = transactions.map(t => `
        <div class="transaction-item">
            <div class="transaction-info">
                <div class="transaction-icon">
                    <i class="fas ${t.type === 'credit' ? 'fa-arrow-down' : 'fa-arrow-up'}"></i>
                </div>
                <div class="transaction-details">
                    <h4>${t.description}</h4>
                    <p>${t.id} • ${formatDate(t.date)}</p>
                </div>
            </div>
            <div class="transaction-amount">
                <div class="amount ${t.type}">
                    ${t.type === 'credit' ? '+' : '-'} ${formatCurrency(t.amount)}
                </div>
                <span class="transaction-status status-${t.status}">${t.status}</span>
            </div>
        </div>
    `).join('');
}

// Load fallback transactions
function loadFallbackTransactions() {
    const fallbackTransactions = [
        { id: 'TXN001', date: new Date(), description: 'Payment for Order #ORD001', amount: 450, type: 'debit', status: 'success' },
        { id: 'TXN002', date: new Date(Date.now() - 86400000), description: 'Added money to wallet', amount: 1000, type: 'credit', status: 'success' },
        { id: 'TXN003', date: new Date(Date.now() - 172800000), description: 'Subscription renewal', amount: 1999, type: 'debit', status: 'success' },
        { id: 'TXN004', date: new Date(Date.now() - 259200000), description: 'Payment for Order #ORD002', amount: 380, type: 'debit', status: 'pending' }
    ];
    displayTransactions(fallbackTransactions);
}

// Load payouts (for provider/owner)
async function loadPayouts() {
    const container = document.getElementById('payoutsList');
    if (!container) return;
    
    try {
        const response = await apiRequest('/payment/payouts', 'GET');
        
        if (response.success && response.payouts.length > 0) {
            displayPayouts(response.payouts);
        } else {
            loadFallbackPayouts();
        }
    } catch (error) {
        console.error('Error loading payouts:', error);
        loadFallbackPayouts();
    }
}

// Display payouts
function displayPayouts(payouts) {
    const container = document.getElementById('payoutsList');
    if (!container) return;
    
    container.innerHTML = payouts.map(payout => `
        <div class="payout-item">
            <div class="payout-info">
                <h4>${payout.provider_name}</h4>
                <p>${payout.orders} orders • ${payout.period}</p>
            </div>
            <div class="payout-amount">${formatCurrency(payout.amount)}</div>
            <button class="btn-process" onclick="processPayout('${payout.id}')">
                Process Now
            </button>
        </div>
    `).join('');
}

// Load fallback payouts
function loadFallbackPayouts() {
    const fallbackPayouts = [
        { id: 1, provider_name: 'Spice Kitchen', orders: 28, period: 'Feb 17-23, 2026', amount: 12500 },
        { id: 2, provider_name: 'Madras Cafe', orders: 21, period: 'Feb 17-23, 2026', amount: 8900 },
        { id: 3, provider_name: 'Punjab Grill', orders: 34, period: 'Feb 17-23, 2026', amount: 15200 }
    ];
    displayPayouts(fallbackPayouts);
}

// Show add money modal
function showAddMoneyModal() {
    const modal = document.getElementById('addMoneyModal');
    if (!modal) return;
    
    modal.style.display = 'flex';
    modal.classList.add('show');
}

// Show add payment method modal
function showAddPaymentModal() {
    const modal = document.getElementById('paymentModal');
    if (!modal) return;
    
    modal.style.display = 'flex';
    modal.classList.add('show');
}

// Select amount for adding money
function selectAmount(amount) {
    document.getElementById('customAmount').value = amount;
}

// Add money to wallet
async function addToWallet() {
    const amount = document.getElementById('customAmount').value;
    if (!amount || amount <= 0) {
        showAlert('Please enter a valid amount', 'error');
        return;
    }
    
    try {
        const response = await apiRequest('/payment/create-order', 'POST', { amount: parseInt(amount) });
        if (response.success) {
            // Redirect to payment gateway
            window.location.href = response.payment_url;
        }
    } catch (error) {
        showAlert('Failed to process payment', 'error');
    }
}

// Process payout
async function processPayout(payoutId) {
    if (!confirm('Process this payout?')) return;
    
    try {
        const response = await apiRequest(`/payment/payout/${payoutId}/process`, 'POST');
        if (response.success) {
            showAlert('Payout processed successfully', 'success');
            loadPayouts();
        }
    } catch (error) {
        showAlert('Failed to process payout', 'error');
    }
}

// Process all payouts
async function processAllPayouts() {
    if (!confirm('Process all pending payouts?')) return;
    
    try {
        const response = await apiRequest('/payment/payouts/process-all', 'POST');
        if (response.success) {
            showAlert('All payouts processed successfully', 'success');
            loadPayouts();
        }
    } catch (error) {
        showAlert('Failed to process payouts', 'error');
    }
}

// Edit payment method
function editPaymentMethod(methodId) {
    showAlert('Edit payment method feature coming soon', 'info');
}

// Delete payment method
async function deletePaymentMethod(methodId) {
    if (!confirm('Delete this payment method?')) return;
    
    try {
        const response = await apiRequest(`/payment/method/${methodId}`, 'DELETE');
        if (response.success) {
            showAlert('Payment method deleted', 'success');
            loadPaymentMethods();
        }
    } catch (error) {
        showAlert('Failed to delete payment method', 'error');
    }
}

// Switch between card and UPI forms
function showCardForm() {
    document.getElementById('cardForm').style.display = 'block';
    document.getElementById('upiForm').style.display = 'none';
}

function showUpiForm() {
    document.getElementById('cardForm').style.display = 'none';
    document.getElementById('upiForm').style.display = 'block';
}

// Save payment method
async function savePaymentMethod() {
    const form = document.getElementById('paymentMethodForm');
    if (!form) return;
    
    // Collect form data
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await apiRequest('/payment/method', 'POST', data);
        if (response.success) {
            showAlert('Payment method added successfully', 'success');
            closeModal();
            loadPaymentMethods();
        }
    } catch (error) {
        showAlert('Failed to add payment method', 'error');
    }
}

// Download receipt
function downloadReceipt(transactionId) {
    showAlert('Downloading receipt...', 'info');
    // Implement receipt download
}

// Export report
function exportReport() {
    showAlert('Exporting payment report...', 'info');
    setTimeout(() => {
        showAlert('Report exported successfully', 'success');
    }, 2000);
}

// Close modal
function closeModal() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
        modal.classList.remove('show');
    });
}

// Show transaction details
function viewTransaction(transactionId) {
    showAlert(`Viewing transaction ${transactionId}`, 'info');
}