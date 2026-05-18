// Global state
let cart = JSON.parse(localStorage.getItem('cart')) || [];
let user = JSON.parse(localStorage.getItem('user')) || null;
let token = localStorage.getItem('token') || null;
let razorpayKey = null;

// API Base URL
const API_URL = '/api';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
    if (user) {
        updateUserUI();
    }
    fetchRazorpayKey();
});

// Auth Functions
async function login(email, password) {
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            token = data.token;
            user = data.user;
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(user));
            showAlert('Login successful!', 'success');
            updateUserUI();
            return true;
        } else {
            showAlert(data.message, 'error');
            return false;
        }
    } catch (error) {
        showAlert('Login failed. Please try again.', 'error');
        return false;
    }
}

async function register(userData) {
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            token = data.token;
            user = data.user;
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(user));
            showAlert('Registration successful!', 'success');
            updateUserUI();
            return true;
        } else {
            showAlert(data.message, 'error');
            return false;
        }
    } catch (error) {
        showAlert('Registration failed. Please try again.', 'error');
        return false;
    }
}

function logout() {
    token = null;
    user = null;
    cart = [];
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('cart');
    showAlert('Logged out successfully', 'success');
    setTimeout(() => window.location.href = '/', 1500);
}

function updateUserUI() {
    const userMenus = document.querySelectorAll('.user-menu');
    const guestMenus = document.querySelectorAll('.guest-menu');
    const customerNavs = document.querySelectorAll('.customer-nav');
    const adminNavs = document.querySelectorAll('.admin-nav');
    const customerOnlyMenus = document.querySelectorAll('.customer-only');
    
    if (user) {
        userMenus.forEach(el => el.style.display = 'block');
        guestMenus.forEach(el => el.style.display = 'none');
        
        // Update user name in navigation
        const userNameElement = document.getElementById('user-name');
        if (userNameElement) {
            userNameElement.textContent = user.name;
        }
        
        const userNameElements = document.querySelectorAll('.user-name');
        userNameElements.forEach(el => el.textContent = user.name);
        
        // Check if user is admin
        if (user.role === 'admin') {
            // Show admin navigation, hide customer navigation
            adminNavs.forEach(el => el.style.display = 'block');
            customerNavs.forEach(el => el.style.display = 'none');
            customerOnlyMenus.forEach(el => el.style.display = 'none');
        } else {
            // Show customer navigation, hide admin navigation
            adminNavs.forEach(el => el.style.display = 'none');
            customerNavs.forEach(el => el.style.display = 'block');
            customerOnlyMenus.forEach(el => el.style.display = 'block');
        }
    } else {
        userMenus.forEach(el => el.style.display = 'none');
        guestMenus.forEach(el => el.style.display = 'block');
        adminNavs.forEach(el => el.style.display = 'none');
        customerNavs.forEach(el => el.style.display = 'block');
    }
}

// Cart Functions
function addToCart(product) {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ ...product, quantity: 1 });
    }
    
    saveCart();
    updateCartCount();
    showAlert(`${product.name} added to cart!`, 'success');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    updateCartCount();
    renderCart();
    // Call updateOrderSummary if on cart page
    if (typeof updateOrderSummary === 'function') {
        updateOrderSummary();
    }
}

function updateQuantity(productId, quantity) {
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity = parseInt(quantity);
        if (item.quantity <= 0) {
            removeFromCart(productId);
        } else {
            saveCart();
            renderCart();
            // Call updateOrderSummary if on cart page
            if (typeof updateOrderSummary === 'function') {
                updateOrderSummary();
            }
        }
    }
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCartCount() {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const cartCounts = document.querySelectorAll('.cart-count');
    cartCounts.forEach(el => {
        el.textContent = totalItems;
        el.style.display = totalItems > 0 ? 'block' : 'none';
    });
}

function getCartTotal() {
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}

function renderCart() {
    const cartContainer = document.getElementById('cart-items');
    if (!cartContainer) return;
    
    if (cart.length === 0) {
        cartContainer.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
        document.getElementById('cart-total').textContent = '₹0';
        return;
    }
    
    cartContainer.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-info">
                <h4>${item.name}</h4>
                <p class="cart-item-price">₹${item.price}</p>
            </div>
            <div class="cart-item-controls">
                <button onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                <input type="number" value="${item.quantity}" min="1" 
                       onchange="updateQuantity(${item.id}, this.value)">
                <button onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                <button onclick="removeFromCart(${item.id})" class="btn-remove">Remove</button>
            </div>
        </div>
    `).join('');
    
    document.getElementById('cart-total').textContent = `₹${getCartTotal()}`;
}

// Product Functions
async function loadProducts(filters = {}) {
    try {
        const params = new URLSearchParams(filters);
        const response = await fetch(`${API_URL}/products?${params}`);
        const data = await response.json();
        
        if (data.success) {
            renderProducts(data.products);
        }
    } catch (error) {
        console.error('Failed to load products:', error);
    }
}

function renderProducts(products) {
    const container = document.getElementById('products-container');
    if (!container) return;
    
    if (products.length === 0) {
        container.innerHTML = '<p>No products found</p>';
        return;
    }
    
    container.innerHTML = products.map(product => `
        <div class="product-card">
            <div class="product-img"></div>
            <div class="product-info">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-price">₹${product.price}</p>
                <div class="product-badges">
                    ${product.isVeg ? '<span class="product-badge badge-veg">🌿 Veg</span>' : ''}
                    ${product.isHealthBox ? '<span class="product-badge badge-health">💪 Health</span>' : ''}
                </div>
                <p>${product.description || ''}</p>
                <button class="btn btn-primary" onclick='addToCart(${JSON.stringify(product)})'>
                    Add to Cart
                </button>
            </div>
        </div>
    `).join('');
}

// Order Functions
async function placeOrder(orderData) {
    if (!token) {
        showAlert('Please login to place an order', 'error');
        setTimeout(() => window.location.href = '/login', 1500);
        return false;
    }
    
    try {
        const response = await fetch(`${API_URL}/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(orderData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            cart = [];
            saveCart();
            updateCartCount();
            showAlert('Order placed successfully!', 'success');
            return data.order;
        } else {
            showAlert(data.message, 'error');
            return false;
        }
    } catch (error) {
        showAlert('Failed to place order', 'error');
        return false;
    }
}

// Payment Functions
async function fetchRazorpayKey() {
    try {
        const response = await fetch(`${API_URL}/payment/key`);
        const data = await response.json();
        
        if (data.success) {
            razorpayKey = data.key;
        } else {
            console.warn('Razorpay not configured:', data.message);
        }
    } catch (error) {
        console.error('Failed to fetch Razorpay key:', error);
    }
}

async function createRazorpayOrder(amount) {
    try {
        const response = await fetch(`${API_URL}/payment/create-order`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ amount })
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data.orderId;
        } else {
            showAlert(data.message, 'error');
            return null;
        }
    } catch (error) {
        showAlert('Failed to create payment order', 'error');
        return null;
    }
}

async function initiatePayment(amount, orderDetails = {}) {
    if (!razorpayKey) {
        showAlert('Payment gateway not configured. Please contact support.', 'error');
        return false;
    }
    
    // Create Razorpay order
    const razorpayOrderId = await createRazorpayOrder(amount);
    
    if (!razorpayOrderId) {
        return false;
    }
    
    // Razorpay checkout options
    const options = {
        key: razorpayKey,
        amount: amount * 100, // Amount in paise
        currency: 'INR',
        name: 'SWAAD SADAN',
        description: orderDetails.description || 'Order Payment',
        order_id: razorpayOrderId,
        handler: function(response) {
            verifyPayment(response, orderDetails);
        },
        prefill: {
            name: user?.name || '',
            email: user?.email || '',
            contact: user?.phone || ''
        },
        theme: {
            color: '#FF6B35'
        },
        modal: {
            ondismiss: function() {
                showAlert('Payment cancelled', 'warning');
            }
        }
    };
    
    const rzp = new Razorpay(options);
    rzp.open();
    return true;
}

async function verifyPayment(response, orderDetails = {}) {
    try {
        const result = await fetch(`${API_URL}/payment/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(response)
        });
        
        const data = await result.json();
        
        if (data.success) {
            showAlert('Payment verified successfully!', 'success');
            
            // Call success callback if provided, pass both paymentId and full payment response
            if (orderDetails.onSuccess && typeof orderDetails.onSuccess === 'function') {
                orderDetails.onSuccess(data.paymentId, response);
            } else {
                // Default behavior - redirect to orders page
                setTimeout(() => window.location.href = '/my-orders', 2000);
            }
        } else {
            showAlert('Payment verification failed: ' + data.message, 'error');
            
            if (orderDetails.onFailure && typeof orderDetails.onFailure === 'function') {
                orderDetails.onFailure();
            }
        }
    } catch (error) {
        showAlert('Payment verification failed', 'error');
        
        if (orderDetails.onFailure && typeof orderDetails.onFailure === 'function') {
            orderDetails.onFailure();
        }
    }
}

// UI Helper Functions
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '250px';
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Form Helpers
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validatePhone(phone) {
    return /^\d{10}$/.test(phone);
}
