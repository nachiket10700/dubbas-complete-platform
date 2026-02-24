// Main JavaScript for Dabba's Platform

// Global variables
let currentUser = null;
let currentLanguage = 'en';
let cart = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    checkAuth();
    setupEventListeners();
    loadUserPreferences();
});

// Initialize app
function initializeApp() {
    console.log('Dabba\'s Platform initialized');
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
    
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('show');
        });
    }
}

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    const userId = localStorage.getItem('userId') || sessionStorage.getItem('userId');
    const userRole = localStorage.getItem('userRole') || sessionStorage.getItem('userRole');
    const username = localStorage.getItem('username') || sessionStorage.getItem('username');
    
    if (token && userId) {
        currentUser = {
            id: userId,
            role: userRole,
            username: username
        };
        
        updateUIForAuthenticatedUser();
    } else {
        updateUIForGuest();
    }
}

// Update UI for authenticated user
function updateUIForAuthenticatedUser() {
    const loginBtns = document.querySelectorAll('.btn-login, .btn-signup');
    loginBtns.forEach(btn => {
        btn.style.display = 'none';
    });
    
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
        userMenu.style.display = 'flex';
        const userAvatar = userMenu.querySelector('.user-avatar');
        const userName = userMenu.querySelector('.user-name');
        
        if (userAvatar && currentUser.username) {
            userAvatar.textContent = currentUser.username.charAt(0).toUpperCase();
        }
        
        if (userName && currentUser.username) {
            userName.textContent = currentUser.username;
        }
    }
}

// Update UI for guest
function updateUIForGuest() {
    const userMenu = document.querySelectorAll('.user-menu');
    userMenu.forEach(menu => {
        menu.style.display = 'none';
    });
}

// Setup event listeners
function setupEventListeners() {
    // Logout button
    const logoutBtns = document.querySelectorAll('#logoutBtn');
    logoutBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    });
    
    // Cart icon
    const cartIcon = document.querySelector('.cart-icon');
    if (cartIcon) {
        cartIcon.addEventListener('click', function() {
            showCart();
        });
    }
    
    // Close modals on outside click
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            closeAllModals();
        }
    });
    
    // Close modals on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeAllModals();
        }
    });
}

// Load user preferences from localStorage
function loadUserPreferences() {
    const savedLanguage = localStorage.getItem('language') || 'en';
    setLanguage(savedLanguage);
    
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
        try {
            cart = JSON.parse(savedCart);
            updateCartBadge();
        } catch (e) {
            console.error('Error loading cart:', e);
        }
    }
}

// Set language
function setLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    document.documentElement.lang = lang;
    
    // Handle RTL for Urdu
    if (lang === 'ur') {
        document.documentElement.dir = 'rtl';
    } else {
        document.documentElement.dir = 'ltr';
    }
    
    // Update language selector
    const langBtn = document.querySelector('.lang-btn span');
    if (langBtn) {
        const languageNames = {
            'en': 'English',
            'hi': 'हिन्दी',
            'mr': 'मराठी',
            'ta': 'தமிழ்',
            'te': 'తెలుగు',
            'kn': 'ಕನ್ನಡ',
            'ml': 'മലയാളം',
            'bn': 'বাংলা',
            'gu': 'ગુજરાતી',
            'pa': 'ਪੰਜਾਬੀ',
            'or': 'ଓଡ଼ିଆ',
            'as': 'অসমীয়া',
            'ur': 'اردو'
        };
        langBtn.textContent = languageNames[lang] || 'English';
    }
    
    // Dispatch language change event
    document.dispatchEvent(new CustomEvent('languageChanged', {
        detail: { language: lang }
    }));
}

// Show alert message
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span>${message}</span>
    `;
    
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            alert.remove();
        }, 300);
    }, duration);
}

// Show loading spinner
function showLoading(container) {
    const loadingEl = document.createElement('div');
    loadingEl.className = 'loading-spinner';
    loadingEl.innerHTML = '<div class="spinner"></div><p>Loading...</p>';
    
    if (container) {
        container.innerHTML = '';
        container.appendChild(loadingEl);
    }
    
    return loadingEl;
}

// Hide loading spinner
function hideLoading(container) {
    if (container) {
        const loadingEl = container.querySelector('.loading-spinner');
        if (loadingEl) {
            loadingEl.remove();
        }
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Format date
function formatDate(date, format = 'medium') {
    const d = new Date(date);
    
    const options = {
        short: { day: 'numeric', month: 'short', year: 'numeric' },
        medium: { day: 'numeric', month: 'long', year: 'numeric' },
        long: { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }
    };
    
    return d.toLocaleDateString('en-IN', options[format] || options.medium);
}

// Format time
function formatTime(date) {
    const d = new Date(date);
    return d.toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Add to cart
function addToCart(item) {
    const existingItem = cart.find(i => i.id === item.id);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: item.id,
            name: item.name,
            price: item.price,
            quantity: 1,
            image: item.image
        });
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartBadge();
    showAlert(`${item.name} added to cart`, 'success');
}

// Remove from cart
function removeFromCart(itemId) {
    cart = cart.filter(item => item.id !== itemId);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartBadge();
    showAlert('Item removed from cart', 'info');
}

// Update cart quantity
function updateCartQuantity(itemId, quantity) {
    const item = cart.find(i => i.id === itemId);
    if (item) {
        if (quantity <= 0) {
            removeFromCart(itemId);
        } else {
            item.quantity = quantity;
            localStorage.setItem('cart', JSON.stringify(cart));
        }
    }
}

// Update cart badge
function updateCartBadge() {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        badge.textContent = totalItems;
        badge.style.display = totalItems > 0 ? 'block' : 'none';
    }
}

// Show cart
function showCart() {
    // Implement cart modal display
    console.log('Cart:', cart);
}

// Logout
function logout() {
    localStorage.clear();
    sessionStorage.clear();
    currentUser = null;
    cart = [];
    
    updateUIForGuest();
    showAlert('Logged out successfully', 'success');
    
    setTimeout(() => {
        window.location.href = '/frontend/index.html';
    }, 1500);
}

// Close all modals
function closeAllModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
        modal.classList.remove('show');
    });
}

// Make API request
async function apiRequest(endpoint, method = 'GET', data = null, requiresAuth = true) {
    const url = `http://localhost:5000/api${endpoint}`;
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (requiresAuth) {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }
    
    const options = {
        method,
        headers
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showAlert(error.message, 'error');
        throw error;
    }
}

// Export functions for use in other scripts
window.Dabbas = {
    setLanguage,
    showAlert,
    formatCurrency,
    formatDate,
    formatTime,
    addToCart,
    removeFromCart,
    updateCartQuantity,
    logout,
    apiRequest,
    currentUser
};