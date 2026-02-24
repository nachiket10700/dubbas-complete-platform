// Customer Dashboard JavaScript

// Initialize customer dashboard
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.customer-dashboard')) {
        initCustomerDashboard();
    }
    
    if (document.getElementById('recommendationsGrid')) {
        loadRecommendations();
    }
    
    if (document.getElementById('ordersContainer')) {
        loadOrders();
    }
    
    if (document.getElementById('plansContainer')) {
        loadSubscriptionPlans();
    }
});

// Initialize customer dashboard
function initCustomerDashboard() {
    console.log('Customer Dashboard initialized');
    updateGreeting();
    loadUserStats();
}

// Update greeting based on time
function updateGreeting() {
    const greetingEl = document.getElementById('greeting');
    if (!greetingEl) return;
    
    const hour = new Date().getHours();
    let greeting = 'Good evening';
    
    if (hour < 12) {
        greeting = 'Good morning';
    } else if (hour < 17) {
        greeting = 'Good afternoon';
    }
    
    const username = localStorage.getItem('username') || 'Guest';
    greetingEl.textContent = `${greeting}, ${username}!`;
}

// Load user stats
async function loadUserStats() {
    try {
        const response = await apiRequest('/customer/profile', 'GET');
        if (response.success) {
            document.getElementById('loyaltyPoints').textContent = response.profile?.loyalty_points || '0';
            document.getElementById('activeOrders').textContent = response.active_orders || '0';
            document.getElementById('totalOrders').textContent = response.total_orders || '0';
            document.getElementById('activeSubscriptions').textContent = response.active_subscriptions || '0';
        }
    } catch (error) {
        console.error('Error loading user stats:', error);
    }
}

// Load personalized recommendations
async function loadRecommendations() {
    const container = document.getElementById('recommendationsGrid');
    if (!container) return;
    
    showLoading(container);
    
    try {
        const city = document.querySelector('.city-btn.active')?.dataset.city || 'mumbai';
        const response = await apiRequest(`/recommendations?city=${city}&limit=8`, 'GET');
        
        hideLoading(container);
        
        if (response.success && response.recommendations.length > 0) {
            displayRecommendations(response.recommendations);
        } else {
            loadFallbackRecommendations();
        }
    } catch (error) {
        hideLoading(container);
        loadFallbackRecommendations();
    }
}

// Display recommendations
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsGrid');
    if (!container) return;
    
    container.innerHTML = recommendations.map(meal => `
        <div class="meal-card" onclick="viewMealDetails('${meal.id}')">
            <div class="meal-image">
                <span class="meal-tag">${meal.cuisine || 'Indian'}</span>
            </div>
            <div class="meal-content">
                <div class="meal-header">
                    <h3 class="meal-name">${meal.name}</h3>
                    <span class="meal-price">₹${meal.price}</span>
                </div>
                <div class="meal-provider">${meal.provider_name || 'Local Kitchen'}</div>
                <div class="meal-rating">
                    <div class="stars">
                        ${generateStars(meal.rating || 4.5)}
                    </div>
                    <span class="rating-count">(${meal.order_count || 0}+ orders)</span>
                </div>
                ${meal.explanation ? `
                    <div class="explanation-badge">
                        <i class="fas fa-robot"></i>
                        <span>${meal.explanation}</span>
                    </div>
                ` : ''}
                <button class="btn-add" onclick="addToCartFromCard(event, ${JSON.stringify(meal).replace(/"/g, '&quot;')})">
                    <i class="fas fa-plus"></i> Add to Cart
                </button>
            </div>
        </div>
    `).join('');
}

// Generate star rating HTML
function generateStars(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5;
    let stars = '';
    
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star"></i>';
    }
    if (halfStar) {
        stars += '<i class="fas fa-star-half-alt"></i>';
    }
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star"></i>';
    }
    return stars;
}

// Load fallback recommendations
function loadFallbackRecommendations() {
    const fallbackMeals = [
        { id: 1, name: 'Butter Chicken', cuisine: 'North Indian', price: 350, rating: 4.8, provider: 'Delhi Darbar', orders: 1234, explanation: 'Because you love North Indian cuisine' },
        { id: 2, name: 'Masala Dosa', cuisine: 'South Indian', price: 120, rating: 4.9, provider: 'Madras Cafe', orders: 2341, explanation: 'Popular in your area' },
        { id: 3, name: 'Vada Pav', cuisine: 'Maharashtrian', price: 30, rating: 4.7, provider: 'Mumbai Tiffin', orders: 3456, explanation: 'You ordered this before' },
        { id: 4, name: 'Hyderabadi Biryani', cuisine: 'Hyderabadi', price: 350, rating: 4.8, provider: 'Biryani House', orders: 4567, explanation: 'Trending now' }
    ];
    
    displayRecommendations(fallbackMeals);
}

// Add to cart from card (prevent event bubbling)
function addToCartFromCard(event, meal) {
    event.stopPropagation();
    addToCart(meal);
}

// View meal details
function viewMealDetails(mealId) {
    window.location.href = `meal-details.html?id=${mealId}`;
}

// Load orders
async function loadOrders() {
    const container = document.getElementById('ordersContainer');
    if (!container) return;
    
    try {
        const response = await apiRequest('/customer/orders?limit=3', 'GET');
        
        if (response.success && response.orders.length > 0) {
            displayOrders(response.orders);
        } else {
            loadFallbackOrders();
        }
    } catch (error) {
        loadFallbackOrders();
    }
}

// Display orders
function displayOrders(orders) {
    const container = document.getElementById('ordersContainer');
    if (!container) return;
    
    container.innerHTML = orders.map(order => `
        <div class="order-card">
            <div class="order-header">
                <div>
                    <span class="order-id">#${order.id}</span>
                    <span class="order-date">${formatDate(order.created_at)}</span>
                </div>
                <span class="order-status status-${order.status}">
                    ${order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                </span>
            </div>
            <div class="order-items">
                ${order.items.map(item => `
                    <div class="order-item">
                        <span>${item.name} x${item.quantity}</span>
                        <span>₹${item.price * item.quantity}</span>
                    </div>
                `).join('')}
            </div>
            <div class="order-total">
                <span>Total</span>
                <span class="total-amount">₹${order.total}</span>
            </div>
            <div class="order-actions">
                <button class="btn-track" onclick="trackOrder('${order.id}')">
                    <i class="fas fa-map-marker-alt"></i> Track
                </button>
                <button class="btn-reorder" onclick="reorder('${order.id}')">
                    <i class="fas fa-redo-alt"></i> Reorder
                </button>
            </div>
        </div>
    `).join('');
}

// Load fallback orders
function loadFallbackOrders() {
    const fallbackOrders = [
        { id: 'ORD001', created_at: new Date(), items: [{ name: 'Butter Chicken', quantity: 1, price: 350 }, { name: 'Naan', quantity: 2, price: 60 }], total: 470, status: 'delivered' },
        { id: 'ORD002', created_at: new Date(Date.now() - 86400000), items: [{ name: 'Masala Dosa', quantity: 2, price: 120 }], total: 240, status: 'preparing' }
    ];
    displayOrders(fallbackOrders);
}

// Track order
function trackOrder(orderId) {
    window.location.href = `order-tracking.html?id=${orderId}`;
}

// Reorder
async function reorder(orderId) {
    try {
        const response = await apiRequest(`/customer/order/${orderId}/reorder`, 'POST');
        if (response.success) {
            showAlert('Order placed successfully!', 'success');
        }
    } catch (error) {
        showAlert('Failed to reorder', 'error');
    }
}

// Load subscription plans
async function loadSubscriptionPlans() {
    const container = document.getElementById('plansContainer');
    if (!container) return;
    
    try {
        const response = await apiRequest('/customer/subscriptions', 'GET');
        
        if (response.success && response.subscriptions.length > 0) {
            displaySubscriptions(response.subscriptions);
        } else {
            loadFallbackPlans();
        }
    } catch (error) {
        loadFallbackPlans();
    }
}

// Display subscriptions
function displaySubscriptions(subscriptions) {
    const container = document.getElementById('plansContainer');
    if (!container) return;
    
    const plans = [
        { name: 'Daily Delight', price: 99, meals: 1, features: ['1 meal per day', 'Free delivery'] },
        { name: 'Weekly Warrior', price: 599, meals: 7, features: ['7 meals', 'Free delivery', 'Save 15%'] },
        { name: 'Monthly Master', price: 1999, meals: 30, features: ['30 meals', 'Free delivery', 'Save 33%'] }
    ];
    
    container.innerHTML = plans.map((plan, index) => {
        const isActive = subscriptions.some(s => s.plan_name === plan.name && s.status === 'active');
        return `
            <div class="plan-card ${isActive ? 'active' : ''}">
                <h3 class="plan-name">${plan.name}</h3>
                <div class="plan-price">₹${plan.price}<span>/month</span></div>
                <ul class="plan-features">
                    ${plan.features.map(f => `<li><i class="fas fa-check"></i> ${f}</li>`).join('')}
                </ul>
                <button class="btn-plan ${isActive ? 'active' : ''}" onclick="subscribe('${plan.name}')">
                    ${isActive ? 'Current Plan' : 'Subscribe'}
                </button>
            </div>
        `;
    }).join('');
}

// Load fallback plans
function loadFallbackPlans() {
    const fallbackPlans = [
        { name: 'Daily Delight', price: 99, meals: 1, active: false },
        { name: 'Weekly Warrior', price: 599, meals: 7, active: true },
        { name: 'Monthly Master', price: 1999, meals: 30, active: false }
    ];
    
    const container = document.getElementById('plansContainer');
    container.innerHTML = fallbackPlans.map(plan => `
        <div class="plan-card ${plan.active ? 'active' : ''}">
            <h3 class="plan-name">${plan.name}</h3>
            <div class="plan-price">₹${plan.price}<span>/month</span></div>
            <ul class="plan-features">
                <li><i class="fas fa-check"></i> ${plan.meals} meals</li>
                <li><i class="fas fa-check"></i> Free delivery</li>
                <li><i class="fas fa-check"></i> Priority support</li>
            </ul>
            <button class="btn-plan ${plan.active ? 'active' : ''}" onclick="subscribe('${plan.name}')">
                ${plan.active ? 'Current Plan' : 'Subscribe'}
            </button>
        </div>
    `).join('');
}

// Subscribe to plan
function subscribe(planName) {
    showAlert(`You have subscribed to ${planName}!`, 'success');
}

// City selector
document.querySelectorAll('.city-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.city-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        loadRecommendations();
    });
});