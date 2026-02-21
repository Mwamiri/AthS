/**
 * AthSys Frontend Application
 * Modern Athletics Management System Interface
 * Connects to backend API and displays system information
 */

// Configuration
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : window.location.origin;

// Color schemes for different statuses
const STATUS_COLORS = {
    online: '#06d6a0',
    offline: '#ef4444',
    warning: '#fbbf24'
};

// Toast notification system
class ToastManager {
    constructor() {
        this.container = this.createContainer();
        document.body.appendChild(this.container);
    }

    createContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        return container;
    }

    show(message, type = 'info', title = null, duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            info: 'ℹ️',
            warning: '⚠️'
        };

        const titles = {
            success: 'Success',
            error: 'Error',
            info: 'Information',
            warning: 'Warning'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-content">
                <div class="toast-title">${title || titles[type] || 'Notification'}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">×</button>
        `;

        this.container.appendChild(toast);

        // Close button handler
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.remove(toast));

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => this.remove(toast), duration);
        }

        return toast;
    }

    remove(toast) {
        toast.classList.add('removing');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    success(message, title = null) {
        return this.show(message, 'success', title);
    }

    error(message, title = null) {
        return this.show(message, 'error', title);
    }

    info(message, title = null) {
        return this.show(message, 'info', title);
    }

    warning(message, title = null) {
        return this.show(message, 'warning', title);
    }
}

// Initialize toast manager
const toast = new ToastManager();

// Loading state management
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.position = 'relative';
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        element.appendChild(overlay);
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
}

// Animate numbers counting up
function animateValue(element, start, end, duration) {
    if (!element) return;
    
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            element.textContent = end;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Fetch API information
async function fetchAPIInfo() {
    const apiInfoElement = document.getElementById('api-info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/info`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const responseTime = response.headers.get('X-Response-Time');
        
        // Pretty print with syntax highlighting
        const jsonString = JSON.stringify(data, null, 2);
        apiInfoElement.innerHTML = `
            <pre>${jsonString}</pre>
            ${responseTime ? `<div style="margin-top: 1rem; color: var(--success-color); font-size: 0.9rem;">⚡ Response time: ${responseTime}</div>` : ''}
        `;
        
        const statusElement = document.getElementById('system-status');
        statusElement.textContent = data.status || 'Online';
        
        // Update status indicator color
        updateStatusIndicator('online');
        
        // Show success toast
        toast.success('Successfully connected to backend API', 'System Online');
        
    } catch (error) {
        console.error('Error fetching API info:', error);
        apiInfoElement.innerHTML = `
            <pre style="color: #ef4444;">❌ Error connecting to backend API
            
Error: ${error.message}

Please ensure:
1. Backend server is running on port 5000
2. CORS is properly configured
3. Network connection is stable</pre>
        `;
        document.getElementById('system-status').textContent = 'Offline';
        updateStatusIndicator('offline');
        
        // Show error toast
        toast.error('Failed to connect to backend API. Check console for details.', 'Connection Error');
    }
}

// Update status indicator with color and animation
function updateStatusIndicator(status) {
    const indicator = document.querySelector('.status-indicator');
    if (indicator) {
        indicator.style.background = STATUS_COLORS[status] || STATUS_COLORS.offline;
        indicator.style.boxShadow = `0 0 20px ${STATUS_COLORS[status] || STATUS_COLORS.offline}`;
    }
}

// Fetch system statistics
async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Animate the counting for each stat
        const athletesEl = document.getElementById('total-athletes');
        const eventsEl = document.getElementById('total-events');
        const resultsEl = document.getElementById('total-results');
        
        const athletes = data.total_athletes || 0;
        const events = data.total_events || 0;
        const results = data.total_results || 0;
        
        animateValue(athletesEl, 0, athletes, 1000);
        animateValue(eventsEl, 0, events, 1200);
        animateValue(resultsEl, 0, results, 1400);
        
        // Show info toast with stats
        if (athletes > 0 || events > 0 || results > 0) {
            toast.info(`System has ${athletes} athletes, ${events} events, and ${results} results`, 'Statistics Updated');
        }
        
    } catch (error) {
        console.error('Error fetching stats:', error);
        document.getElementById('total-athletes').textContent = '?';
        document.getElementById('total-events').textContent = '?';
        document.getElementById('total-results').textContent = '?';
        
        toast.warning('Unable to load statistics. Data may be unavailable.', 'Stats Warning');
    }
}

// Check health with improved feedback
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateStatusIndicator('online');
        } else {
            updateStatusIndicator('warning');
            toast.warning('System health check returned a warning status', 'Health Warning');
        }
    } catch (error) {
        updateStatusIndicator('offline');
        console.error('Health check failed:', error);
    }
}

// Add fade-in animation to sections
function animateSections() {
    const sections = document.querySelectorAll('section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Add interactive click handlers for stat cards
function enhanceStatCards() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach((card, index) => {
        card.classList.add('clickable');
        
        card.addEventListener('click', async () => {
            const labels = ['Athletes', 'Events', 'Results'];
            const endpoints = ['/api/athletes', '/api/events', '/api/results'];
            
            toast.info(`Loading ${labels[index]} data...`, 'Fetching Data');
            
            try {
                const response = await fetch(`${API_BASE_URL}${endpoints[index]}`);
                const data = await response.json();
                
                if (data.count || data.athletes || data.events || data.results) {
                    const count = data.count || data.athletes?.length || data.events?.length || data.results?.length || 0;
                    toast.success(`Found ${count} ${labels[index].toLowerCase()}`, labels[index]);
                } else {
                    toast.info(`No ${labels[index].toLowerCase()} available yet`, labels[index]);
                }
            } catch (error) {
                toast.error(`Failed to load ${labels[index].toLowerCase()}`, 'Error');
            }
        });
    });
}

// Add keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + R: Refresh data
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            toast.info('Refreshing all data...', 'Manual Refresh');
            fetchAPIInfo();
            fetchStats();
            checkHealth();
        }
        
        // Ctrl/Cmd + H: Show health status
        if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
            e.preventDefault();
            checkHealth();
            toast.info('Health check initiated', 'System Check');
        }
    });
}

// Add connection status monitoring
let connectionLost = false;

async function monitorConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, { 
            method: 'HEAD',
            cache: 'no-cache'
        });
        
        if (response.ok && connectionLost) {
            connectionLost = false;
            toast.success('Connection restored!', 'Backend Online');
            updateStatusIndicator('online');
        }
    } catch (error) {
        if (!connectionLost) {
            connectionLost = true;
            toast.error('Lost connection to backend server', 'Connection Lost');
            updateStatusIndicator('offline');
        }
    }
}

// Initialize application
function init() {
    console.log('🏃‍♂️ AthSys Frontend initialized');
    console.log('⚡ Elite Athletics Management System');
    console.log('📋 Keyboard shortcuts:');
    console.log('   Ctrl/Cmd + R: Refresh data');
    console.log('   Ctrl/Cmd + H: Health check');
    
    // Show welcome toast
    setTimeout(() => {
        toast.info('Welcome to AthSys! Click on stat cards for details.', 'System Ready', 6000);
    }, 500);
    
    // Animate sections on load
    animateSections();
    
    // Fetch initial data
    fetchAPIInfo();
    fetchStats();
    checkHealth();
    
    // Enhance interactive elements
    enhanceStatCards();
    setupKeyboardShortcuts();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        checkHealth();
        fetchStats();
    }, 30000);
    
    // Monitor connection every 10 seconds
    setInterval(monitorConnection, 10000);
    
    // Add hover effects to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    console.log('✅ System ready');
}

// Run when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
