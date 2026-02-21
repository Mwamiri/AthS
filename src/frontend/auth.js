// Authentication JavaScript

const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '/api';

// Toast notification system
class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container') || this.createContainer();
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
        return container;
    }

    show(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            min-width: 250px;
            animation: slideIn 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        
        const colors = {
            success: '#06d6a0',
            error: '#e63946',
            warning: '#f7931e',
            info: '#4a90e2'
        };
        
        toast.style.background = colors[type] || colors.info;
        this.container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
}

const toast = new ToastManager();

// Tab switching functionality
function initTabs() {
    const tabs = document.querySelectorAll('.auth-tab');
    const forms = document.querySelectorAll('.auth-form');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            
            // Update active states
            tabs.forEach(t => t.classList.remove('active'));
            forms.forEach(f => f.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(`${target}-form`).classList.add('active');
        });
    });
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    if (password.length < 8) {
        return { valid: false, message: 'Password must be at least 8 characters' };
    }
    if (!/[A-Z]/.test(password)) {
        return { valid: false, message: 'Password must contain at least one uppercase letter' };
    }
    if (!/[a-z]/.test(password)) {
        return { valid: false, message: 'Password must contain at least one lowercase letter' };
    }
    if (!/[0-9]/.test(password)) {
        return { valid: false, message: 'Password must contain at least one number' };
    }
    return { valid: true };
}

// Show loading state
function showLoading(button) {
    button.dataset.originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `<div class="btn-loader"></div> Processing...`;
}

function hideLoading(button) {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText;
}

// Login form handler
async function handleLogin(event) {
    event.preventDefault();
    
    const button = event.target.querySelector('button[type="submit"]');
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    const remember = document.getElementById('remember-me').checked;
    
    // Validation
    if (!validateEmail(email)) {
        toast.show('Please enter a valid email address', 'error');
        return;
    }
    
    if (!password) {
        toast.show('Please enter your password', 'error');
        return;
    }
    
    showLoading(button);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password, remember })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store authentication token
            if (remember) {
                localStorage.setItem('authToken', data.token);
            } else {
                sessionStorage.setItem('authToken', data.token);
            }
            
            // Store user info
            localStorage.setItem('user', JSON.stringify(data.user));
            
            toast.show('Login successful! Redirecting...', 'success');
            
            // Redirect based on role (obfuscated routes for security)
            setTimeout(() => {
                const roleRoutes = {
                    'admin': 'd4f8a9.view',
                    'chief_registrar': 'c1e5d4.view',
                    'registrar': 'c1e5d4.view',
                    'starter': '8b2d7e.view',
                    'coach': '7e3f9a.view',
                    'athlete': '9b4e7c.view',
                    'viewer': '5c8b9e.view'
                };
                window.location.href = roleRoutes[data.user.role] || 'a7c3e1.view';
            }, 1500);
        } else {
            toast.show(data.message || 'Login failed. Please check your credentials.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        toast.show('Connection error. Please try again.', 'error');
    } finally {
        hideLoading(button);
    }
}

// Register form handler
async function handleRegister(event) {
    event.preventDefault();
    
    const button = event.target.querySelector('button[type="submit"]');
    const name = document.getElementById('register-name').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const role = document.getElementById('user-role').value;
    
    // Validation
    if (name.length < 2) {
        toast.show('Please enter your full name', 'error');
        return;
    }
    
    if (!validateEmail(email)) {
        toast.show('Please enter a valid email address', 'error');
        return;
    }
    
    const passwordCheck = validatePassword(password);
    if (!passwordCheck.valid) {
        toast.show(passwordCheck.message, 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        toast.show('Passwords do not match', 'error');
        return;
    }
    
    if (!role) {
        toast.show('Please select a role', 'error');
        return;
    }
    
    showLoading(button);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, password, role })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            toast.show('Registration successful! Please log in.', 'success');
            
            // Clear form
            event.target.reset();
            
            // Switch to login tab after 2 seconds
            setTimeout(() => {
                document.querySelector('[data-tab="login"]').click();
            }, 2000);
        } else {
            toast.show(data.message || 'Registration failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        toast.show('Connection error. Please try again.', 'error');
    } finally {
        hideLoading(button);
    }
}

// Password reset form handler
async function handleResetPassword(event) {
    event.preventDefault();
    
    const button = event.target.querySelector('button[type="submit"]');
    const email = document.getElementById('reset-email').value.trim();
    
    // Validation
    if (!validateEmail(email)) {
        toast.show('Please enter a valid email address', 'error');
        return;
    }
    
    showLoading(button);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            toast.show('Password reset link sent! Check your email.', 'success');
            event.target.reset();
        } else {
            toast.show(data.message || 'Failed to send reset link.', 'error');
        }
    } catch (error) {
        console.error('Reset password error:', error);
        toast.show('Connection error. Please try again.', 'error');
    } finally {
        hideLoading(button);
    }
}

// Demo access handler
function handleDemoAccess() {
    // Store demo user info
    const demoUser = {
        id: 'demo-001',
        name: 'Demo User',
        email: 'demo@athsys.com',
        role: 'athlete'
    };
    
    localStorage.setItem('user', JSON.stringify(demoUser));
    localStorage.setItem('authToken', 'demo-token-' + Date.now());
    
    toast.show('Welcome! Entering demo mode...', 'success');
    
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1500);
}

// Check if user is already logged in
function checkAuth() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (token && user.email) {
        // Redirect to appropriate page
        if (user.role === 'admin') {
            window.location.href = 'd4f8a9.view';
        } else {
            window.location.href = 'index.html';
        }
    }
}

// Logout functionality
function logout() {
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    localStorage.removeItem('user');
    
    toast.show('Logged out successfully', 'info');
    
    setTimeout(() => {
        window.location.href = 'login.html';
    }, 1500);
}

// Password visibility toggle
function initPasswordToggle() {
    const toggleButtons = document.querySelectorAll('.toggle-password');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const input = button.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            button.textContent = type === 'password' ? '👁️' : '🙈';
        });
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to submit active form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeForm = document.querySelector('.auth-form.active form');
        if (activeForm) {
            activeForm.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check if already authenticated
    checkAuth();
    
    // Initialize tabs
    initTabs();
    
    // Initialize password toggles
    initPasswordToggle();
    
    // Attach form event listeners
    const loginForm = document.getElementById('login-form')?.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    const registerForm = document.getElementById('register-form')?.querySelector('form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    const resetForm = document.getElementById('reset-form')?.querySelector('form');
    if (resetForm) {
        resetForm.addEventListener('submit', handleResetPassword);
    }
    
    const demoButton = document.getElementById('demo-access');
    if (demoButton) {
        demoButton.addEventListener('click', handleDemoAccess);
    }
    
    console.log('🔐 Authentication system initialized');
});

// Export functions for global access
window.AuthManager = {
    logout,
    checkAuth,
    toast
};
