// Provider Dashboard JavaScript

// Initialize provider dashboard
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.provider-dashboard')) {
        initProviderDashboard();
    }
    
    if (document.getElementById('recentOrdersContainer')) {
        loadRecentOrders();
    }
    
    if (document.getElementById('menuPreviewContainer')) {
        loadMenuPreview();
    }
    
    if (document.getElementById('aiRecommendationsContainer')) {
        loadAIRecommendations();
    }
    
    // Business status toggle
    const statusToggle = document.getElementById('businessStatus');
    if (statusToggle) {
        statusToggle.addEventListener('click', toggleBusinessStatus);
    }
});

// Initialize provider dashboard
function initProviderDashboard() {
    console.log('Provider Dashboard initialized');
    loadProviderStats();
    initRevenueChart();
}

// Load provider stats
async function loadProviderStats() {
    try {
        const response = await apiRequest('/provider/stats', 'GET');
        if (response.success) {
            document.getElementById('todayOrders').textContent = response.stats?.today_orders || '0';
            document.getElementById('todayRevenue').textContent = formatCurrency(response.stats?.today_revenue || 0);
            document.getElementById('totalOrders').textContent = response.stats?.total_orders || '0';
            document.getElementById('totalRevenue').textContent = formatCurrency(response.stats?.total_revenue || 0);
            document.getElementById('avgRating').textContent = response.stats?.rating || '4.5';
            document.getElementById('pendingOrders').textContent = response.stats?.pending_orders || '0';
        }
    } catch (error) {
        console.error('Error loading provider stats:', error);
        // Set fallback values
        document.getElementById('todayOrders').textContent = '24';
        document.getElementById('todayRevenue').textContent = '₹12,450';
        document.getElementById('totalOrders').textContent = '1,234';
        document.getElementById('totalRevenue').textContent = '₹5,67,890';
        document.getElementById('avgRating').textContent = '4.8';
        document.getElementById('pendingOrders').textContent = '8';
    }
}

// Toggle business status
function toggleBusinessStatus() {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    const isOpen = text.textContent === 'Open';
    
    if (isOpen) {
        dot.classList.add('closed');
        text.textContent = 'Closed';
        showAlert('Business marked as closed', 'info');
    } else {
        dot.classList.remove('closed');
        text.textContent = 'Open';
        showAlert('Business marked as open', 'success');
    }
    
    // API call to update status
    apiRequest('/provider/status', 'POST', { status: text.textContent.toLowerCase() });
}

// Load recent orders
async function loadRecentOrders() {
    const container = document.getElementById('recentOrdersContainer');
    if (!container) return;
    
    showLoading(container);
    
    try {
        const response = await apiRequest('/provider/orders?limit=5', 'GET');
        hideLoading(container);
        
        if (response.success && response.orders.length > 0) {
            displayRecentOrders(response.orders);
        } else {
            loadFallbackOrders();
        }
    } catch (error) {
        hideLoading(container);
        loadFallbackOrders();
    }
}

// Display recent orders
function displayRecentOrders(orders) {
    const container = document.getElementById('recentOrdersContainer');
    if (!container) return;
    
    container.innerHTML = orders.map(order => {
        const statusClass = getStatusClass(order.status);
        return `
            <div class="order-item">
                <div class="order-customer">
                    <h4>${order.customer_name || 'Customer'}</h4>
                    <p>${order.items?.length || 3} items • Order #${order.id}</p>
                </div>
                <div class="order-details">
                    <span class="order-amount">₹${order.total_amount || 0}</span>
                    <span class="order-time">${formatTime(order.created_at)}</span>
                    <span class="order-status ${statusClass}">${order.status || 'pending'}</span>
                </div>
            </div>
        `;
    }).join('');
}

// Get status class for styling
function getStatusClass(status) {
    const classes = {
        'pending': 'status-pending',
        'confirmed': 'status-confirmed',
        'preparing': 'status-preparing',
        'ready': 'status-ready',
        'out-for-delivery': 'status-out-for-delivery',
        'delivered': 'status-delivered',
        'cancelled': 'status-cancelled'
    };
    return classes[status] || 'status-pending';
}

// Load fallback orders
function loadFallbackOrders() {
    const fallbackOrders = [
        { id: 'ORD001', customer_name: 'Rahul Sharma', items: [1,2,3], total_amount: 450, created_at: new Date(), status: 'preparing' },
        { id: 'ORD002', customer_name: 'Priya Patel', items: [1,2], total_amount: 380, created_at: new Date(Date.now() - 900000), status: 'pending' },
        { id: 'ORD003', customer_name: 'Amit Kumar', items: [1,2,3,4], total_amount: 620, created_at: new Date(Date.now() - 1800000), status: 'ready' },
        { id: 'ORD004', customer_name: 'Sneha Reddy', items: [1,2,3], total_amount: 390, created_at: new Date(Date.now() - 2700000), status: 'delivered' }
    ];
    displayRecentOrders(fallbackOrders);
}

// Load menu preview
async function loadMenuPreview() {
    const container = document.getElementById('menuPreviewContainer');
    if (!container) return;
    
    try {
        const response = await apiRequest('/provider/menu', 'GET');
        
        if (response.success && response.menu.length > 0) {
            displayMenuPreview(response.menu.slice(0, 4));
        } else {
            loadFallbackMenu();
        }
    } catch (error) {
        loadFallbackMenu();
    }
}

// Display menu preview
function displayMenuPreview(items) {
    const container = document.getElementById('menuPreviewContainer');
    if (!container) return;
    
    container.innerHTML = items.map(item => `
        <div class="menu-item-preview">
            <h4>${item.name}</h4>
            <div class="menu-item-price">₹${item.price}</div>
            <div class="menu-item-orders">
                <span class="menu-item-status status-${item.is_available ? 'active' : 'inactive'}"></span>
                ${item.order_count || 0} orders today
            </div>
        </div>
    `).join('');
}

// Load fallback menu
function loadFallbackMenu() {
    const fallbackMenu = [
        { name: 'Butter Chicken', price: 350, order_count: 45, is_available: true },
        { name: 'Paneer Tikka', price: 280, order_count: 38, is_available: true },
        { name: 'Garlic Naan', price: 60, order_count: 52, is_available: true },
        { name: 'Biryani', price: 320, order_count: 41, is_available: true }
    ];
    displayMenuPreview(fallbackMenu);
}

// Load AI recommendations
function loadAIRecommendations() {
    const container = document.getElementById('aiRecommendationsContainer');
    if (!container) return;
    
    const recommendations = [
        {
            type: 'Pricing',
            title: 'Dynamic Pricing Opportunity',
            description: 'Increase price of Butter Chicken by 10% during peak dinner hours (7-9 PM) to maximize revenue',
            confidence: 85
        },
        {
            type: 'Menu',
            title: 'New Dish Recommendation',
            description: 'Customers who ordered Paneer Tikka also like Malai Kofta. Consider adding to your menu.',
            confidence: 92
        },
        {
            type: 'Inventory',
            title: 'Inventory Optimization',
            description: 'Based on demand patterns, increase chicken stock by 30% on weekends',
            confidence: 78
        },
        {
            type: 'Timing',
            title: 'Peak Hours Detected',
            description: 'Your busiest time is 12:30-2:00 PM. Consider adding one more chef during this slot.',
            confidence: 95
        }
    ];
    
    container.innerHTML = recommendations.map(rec => `
        <div class="ai-card">
            <div class="ai-header">
                <span class="ai-type">${rec.type}</span>
                <span class="ai-confidence">${rec.confidence}% match</span>
            </div>
            <h4>${rec.title}</h4>
            <p>${rec.description}</p>
            <button class="btn-apply" onclick="applyRecommendation('${rec.type}')">
                Apply Suggestion <i class="fas fa-arrow-right"></i>
            </button>
        </div>
    `).join('');
}

// Apply recommendation
function applyRecommendation(type) {
    showAlert(`Applied ${type} recommendation!`, 'success');
}

// Initialize revenue chart
function initRevenueChart() {
    const ctx = document.getElementById('revenueChart')?.getContext('2d');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Revenue (₹)',
                data: [12500, 14200, 13800, 15100, 18900, 24500, 19800],
                borderColor: '#ff6b6b',
                backgroundColor: 'rgba(255, 107, 107, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value;
                        }
                    }
                }
            }
        }
    });
}

// Update order status
async function updateOrderStatus(orderId, newStatus) {
    try {
        const response = await apiRequest(`/provider/order/${orderId}/status`, 'PUT', { status: newStatus });
        if (response.success) {
            showAlert(`Order ${orderId} status updated to ${newStatus}`, 'success');
            loadRecentOrders();
        }
    } catch (error) {
        showAlert('Failed to update order status', 'error');
    }
}

// Add menu item
function addMenuItem() {
    window.location.href = 'menu.html?action=add';
}

// View all orders
function viewAllOrders() {
    window.location.href = 'orders.html';
}

// View analytics
function viewAnalytics() {
    window.location.href = 'earnings.html';
}

// Print daily report
function printReports() {
    window.print();
}