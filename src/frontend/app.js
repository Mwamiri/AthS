/**
 * AthSys Frontend Application
 * Connects to backend API and displays system information
 */

// Configuration
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '/api';

// Fetch API information
async function fetchAPIInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        const data = await response.json();
        
        document.getElementById('api-info').innerHTML = `
            <pre>${JSON.stringify(data, null, 2)}</pre>
        `;
        
        document.getElementById('system-status').textContent = data.status || 'Online';
    } catch (error) {
        console.error('Error fetching API info:', error);
        document.getElementById('api-info').innerHTML = `
            <pre style="color: #ef4444;">Error connecting to backend API</pre>
        `;
        document.getElementById('system-status').textContent = 'Offline';
    }
}

// Fetch system statistics
async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        const data = await response.json();
        
        document.getElementById('total-athletes').textContent = data.total_athletes || 0;
        document.getElementById('total-events').textContent = data.total_events || 0;
        document.getElementById('total-results').textContent = data.total_results || 0;
    } catch (error) {
        console.error('Error fetching stats:', error);
        document.getElementById('total-athletes').textContent = '?';
        document.getElementById('total-events').textContent = '?';
        document.getElementById('total-results').textContent = '?';
    }
}

// Check health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            document.querySelector('.status-indicator').style.background = '#10b981';
        }
    } catch (error) {
        document.querySelector('.status-indicator').style.background = '#ef4444';
    }
}

// Initialize application
function init() {
    console.log('AthSys Frontend initialized');
    
    // Fetch initial data
    fetchAPIInfo();
    fetchStats();
    checkHealth();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        checkHealth();
        fetchStats();
    }, 30000);
}

// Run when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
