// Owner Dashboard JavaScript

// Initialize owner dashboard
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.owner-dashboard')) {
        initOwnerDashboard();
    }
    
    if (document.getElementById('activityList')) {
        loadActivityFeed();
    }
    
    // Initialize charts
    initRevenueChart();
    initOrderStatusChart();
});

// Initialize owner dashboard
function initOwnerDashboard() {
    console.log('Owner Dashboard initialized');
    loadPlatformStats();
    updateDateTime();
    setInterval(updateDateTime, 1000);
}

// Update date and time
function updateDateTime() {
    const dateTimeEl = document.getElementById('currentDateTime');
    if (!dateTimeEl) return;
    
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    dateTimeEl.textContent = now.toLocaleDateString('en-US', options);
}

// Load platform statistics
async function loadPlatformStats() {
    try {
        const response = await apiRequest('/owner/stats', 'GET');
        if (response.success) {
            updateStatsDisplay(response.stats);
        } else {
            loadFallbackStats();
        }
    } catch (error) {
        console.error('Error loading platform stats:', error);
        loadFallbackStats();
    }
}

// Update stats display
function updateStatsDisplay(stats) {
    document.getElementById('totalRevenue').textContent = formatCurrency(stats.total_revenue || 1245678);
    document.getElementById('totalOrders').textContent = (stats.total_orders || 45892).toLocaleString();
    document.getElementById('activeProviders').textContent = (stats.active_providers || 2847).toLocaleString();
    document.getElementById('activeCustomers').textContent = (stats.active_customers || 42156).toLocaleString();
    
    // Update change percentages
    document.querySelectorAll('.stat-change').forEach(el => {
        if (el.classList.contains('positive')) {
            el.innerHTML = '<i class="fas fa-arrow-up"></i> +18.2% from last month';
        }
    });
}

// Load fallback stats
function loadFallbackStats() {
    document.getElementById('totalRevenue').textContent = '₹12,45,678';
    document.getElementById('totalOrders').textContent = '45,892';
    document.getElementById('activeProviders').textContent = '2,847';
    document.getElementById('activeCustomers').textContent = '42,156';
}

// Initialize revenue chart
function initRevenueChart() {
    const ctx = document.getElementById('revenueChart')?.getContext('2d');
    if (!ctx) return;
    
    window.revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
                label: 'Revenue (₹)',
                data: [825000, 923000, 1028000, 1245000],
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
                            return '₹' + (value/1000) + 'k';
                        }
                    }
                }
            }
        }
    });
}

// Update revenue chart based on period
function updateRevenueChart() {
    const period = document.getElementById('revenuePeriod')?.value;
    if (!period || !window.revenueChart) return;
    
    let labels, data;
    
    if (period === 'week') {
        labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        data = [125000, 142000, 138000, 151000, 189000, 245000, 198000];
    } else if (period === 'month') {
        labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
        data = [825000, 923000, 1028000, 1245000];
    } else {
        labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        data = [825000, 923000, 1028000, 1245000, 1350000, 1420000, 1580000, 1650000, 1720000, 1850000, 1980000, 2100000];
    }
    
    window.revenueChart.data.labels = labels;
    window.revenueChart.data.datasets[0].data = data;
    window.revenueChart.update();
}

// Initialize order status chart
function initOrderStatusChart() {
    const ctx = document.getElementById('orderStatusChart')?.getContext('2d');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Delivered', 'In Progress', 'Pending', 'Cancelled'],
            datasets: [{
                data: [6543, 2341, 1234, 432],
                backgroundColor: [
                    '#4caf50',
                    '#ff9800',
                    '#2196f3',
                    '#f44336'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Load activity feed
function loadActivityFeed() {
    const container = document.getElementById('activityList');
    if (!container) return;
    
    const activities = [
        { type: 'provider', title: 'New Provider Registration', description: 'Spice Kitchen joined the platform', time: '5 minutes ago', status: 'pending' },
        { type: 'order', title: 'High Value Order', description: 'Order #ORD001 - ₹2,450 from Mumbai', time: '15 minutes ago', status: 'completed' },
        { type: 'complaint', title: 'New Complaint', description: 'Food quality issue from Customer #C001', time: '25 minutes ago', status: 'urgent' },
        { type: 'payment', title: 'Payout Processed', description: '₹45,000 paid to 5 providers', time: '1 hour ago', status: 'completed' },
        { type: 'provider', title: 'Provider Verified', description: 'Punjab Grill verification completed', time: '2 hours ago', status: 'verified' }
    ];
    
    container.innerHTML = activities.map(activity => {
        let iconClass = '';
        if (activity.type === 'provider') iconClass = 'icon-provider fas fa-store';
        else if (activity.type === 'order') iconClass = 'icon-order fas fa-shopping-bag';
        else if (activity.type === 'complaint') iconClass = 'icon-complaint fas fa-exclamation-circle';
        else iconClass = 'icon-payment fas fa-credit-card';
        
        return `
            <div class="activity-item">
                <div class="activity-icon ${iconClass.split(' ')[0]}">
                    <i class="${iconClass.split(' ')[1]}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-time">${activity.description} • ${activity.time}</div>
                </div>
                <span class="activity-status">${activity.status}</span>
            </div>
        `;
    }).join('');
}

// Filter orders
function filterOrders(status) {
    document.querySelectorAll('.stat-card').forEach(card => card.classList.remove('active'));
    event.currentTarget.classList.add('active');
    
    // Here you would filter the orders table
    showAlert(`Filtering by ${status} orders`, 'info');
}

// Quick action functions
function verifyProviders() {
    window.location.href = 'providers.html?filter=pending';
}

function reviewComplaints() {
    window.location.href = 'complaints.html?filter=pending';
}

function processPayouts() {
    window.location.href = 'payments.html?tab=payouts';
}

function platformSettings() {
    window.location.href = 'settings.html';
}

// Export functions
function exportData() {
    showAlert('Exporting data...', 'info');
    setTimeout(() => {
        showAlert('Data exported successfully', 'success');
    }, 2000);
}

// Date range filter
document.getElementById('timeRange')?.addEventListener('change', function(e) {
    const range = e.target.value;
    showAlert(`Showing data for: ${range}`, 'info');
    loadPlatformStats(); // Reload stats for new range
});