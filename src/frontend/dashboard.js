// Dashboard JavaScript for AthSys v2.1
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : window.location.origin;

class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = this.createContainer();
            document.body.appendChild(this.container);
        }
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

function checkAuth() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const userStr = localStorage.getItem('user') || sessionStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    
    if (!token || !user) {
        window.location.href = 'login.html';
        return null;
    }
    
    return user;
}

async function logout() {
    return logoutWithRevocation({
        redirectTo: 'login.html',
        delayMs: 1000,
        showMessage: () => toast.show('Logged out successfully', 'success')
    });
}

async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        if (response.status === 401) {
            toast.show('Session expired. Please login again.', 'error');
            logout();
            return null;
        }
        
        return response;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Placeholder functions for stat card clicks
function loadRaces() {
    toast.show('Loading races...', 'info');
    // TODO: Navigate to races page when implemented
}

function loadAthletes() {
    toast.show('Loading athletes...', 'info');
    // TODO: Navigate to athletes page when implemented
}

function loadEvents() {
    toast.show('Loading events...', 'info');
    // TODO: Navigate to events page when implemented
}

function loadResults() {
    toast.show('Loading results...', 'info');
    // TODO: Navigate to results page when implemented
}

// Role-based quick actions with real page links
const roleActions = {
    admin: [
        { icon: '👥', title: 'Manage Users', desc: 'Add, edit, or remove users', link: 'users.html' },
        { icon: '🏁', title: 'Manage Races', desc: 'Create and configure races', link: 'races.html' },
        { icon: '🏃', title: 'View Athletes', desc: 'Browse athlete profiles', link: 'athletes.html' },
        { icon: '🏆', title: 'View Results', desc: 'See race results', link: 'results.html' }
    ],
    chief_registrar: [
        { icon: '🏁', title: 'Manage Races', desc: 'Create and configure races', link: 'races.html' },
        { icon: '🏃', title: 'Manage Athletes', desc: 'Add and edit athletes', link: 'athletes.html' },
        { icon: '🏆', title: 'Enter Results', desc: 'Record race results', link: 'results.html' },
        { icon: '📋', title: 'Registrations', desc: 'View all registrations', link: 'races.html' }
    ],
    registrar: [
        { icon: '🏁', title: 'View Races', desc: 'See all races', link: 'races.html' },
        { icon: '🏃', title: 'Register Athletes', desc: 'Add athlete registrations', link: 'athletes.html' },
        { icon: '📋', title: 'View Athletes', desc: 'Browse athlete list', link: 'athletes.html' },
        { icon: '🔍', title: 'Search Athletes', desc: 'Find athlete information', link: 'athletes.html' }
    ],
    starter: [
        { icon: '🏁', title: 'View Races', desc: 'See upcoming races', link: 'races.html' },
        { icon: '🏆', title: 'Enter Results', desc: 'Record race results', link: 'results.html' },
        { icon: '🏃', title: 'View Athletes', desc: 'Check athlete list', link: 'athletes.html' },
        { icon: '📊', title: 'View Results', desc: 'See all results', link: 'results.html' }
    ],
    coach: [
        { icon: '🏃', title: 'Team Athletes', desc: 'View your athletes', link: 'athletes.html' },
        { icon: '🏁', title: 'View Races', desc: 'Browse available races', link: 'races.html' },
        { icon: '🏆', title: 'View Results', desc: 'Check team performance', link: 'results.html' },
        { icon: '📊', title: 'Performance', desc: 'View athlete analytics', link: 'results.html' }
    ],
    athlete: [
        { icon: '🏁', title: 'Find Races', desc: 'Browse available races', link: 'races.html' },
        { icon: '🏆', title: 'My Results', desc: 'View personal results', link: 'results.html' },
        { icon: '🏃', title: 'Athletes', desc: 'View all athletes', link: 'athletes.html' },
        { icon: '📅', title: 'Public Races', desc: 'Register for races', link: 'index.html' }
    ],
    viewer: [
        { icon: '🏁', title: 'View Races', desc: 'See all races', link: 'races.html' },
        { icon: '🏃', title: 'View Athletes', desc: 'Browse athlete profiles', link: 'athletes.html' },
        { icon: '🏆', title: 'View Results', desc: 'See race results', link: 'results.html' },
        { icon: '📊', title: 'Browse System', desc: 'Explore data', link: 'dashboard.html' }
    ]
};

async function loadDashboard() {
    const user = checkAuth();
    if (!user) return;
    
    // Update user info
    document.getElementById('userName').textContent = user.name || user.email;
    document.getElementById('userWelcome').textContent = user.name || user.email.split('@')[0];
    document.getElementById('userRole').textContent = formatRole(user.role);
    
    // Load quick actions based on role
    loadQuickActions(user.role);
    
    // Load statistics
    try {
        const responses = await Promise.allSettled([
            fetchWithAuth(`${API_BASE_URL}/api/races`),
            fetchWithAuth(`${API_BASE_URL}/api/athletes`),
            fetchWithAuth(`${API_BASE_URL}/api/results`)
        ]);
        
        const [racesResp, athletesResp, resultsResp] = responses;
        
        let races = [];
        if (racesResp.status === 'fulfilled' && racesResp.value) {
            races = await racesResp.value.json();
            document.getElementById('totalRaces').textContent = Array.isArray(races) ? races.length : 0;
            // Count total events across all races
            const totalEvents = races.reduce((total, race) => total + (race.events ? race.events.length : 0), 0);
            document.getElementById('totalEvents').textContent = totalEvents;
        }
        
        if (athletesResp.status === 'fulfilled' && athletesResp.value) {
            const athletes = await athletesResp.value.json();
            document.getElementById('totalAthletes').textContent = Array.isArray(athletes) ? athletes.length : 0;
        }
        
        if (resultsResp.status === 'fulfilled' && resultsResp.value) {
            const results = await resultsResp.value.json();
            document.getElementById('totalResults').textContent = Array.isArray(results) ? results.length : 0;
        }
        
        toast.show('Dashboard loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        toast.show('Could not load all dashboard data', 'warning');
    }
}

function formatRole(role) {
    const roleNames = {
        'admin': 'Administrator',
        'chief_registrar': 'Chief Registrar',
        'registrar': 'Registrar',
        'starter': 'Starter Official',
        'coach': 'Coach',
        'athlete': 'Athlete',
        'viewer': 'Viewer'
    };
    return roleNames[role] || role.replace('_', ' ').toUpperCase();
}

function loadQuickActions(role) {
    const grid = document.getElementById('quickActionsGrid');
    const actions = roleActions[role] || [];
    
    grid.innerHTML = actions.map(action => {
        return `
            <a href="${action.link}" class="action-btn">
                <div class="action-icon">${action.icon}</div>
                <div class="action-text">
                    <h3>${action.title}</h3>
                    <p>${action.desc}</p>
                </div>
            </a>
        `;
    }).join('');
}

function getWelcomeMessage(role) {
    const messages = {
        'admin': 'You have full system access.',
        'chief_registrar': 'Ready to manage races and registrations.',
        'registrar': 'Ready to register athletes for upcoming races.',
        'starter': 'Ready to check athlete presence and start races.',
        'coach': 'View your team performance and upcoming races.',
        'athlete': 'Check your personal records and race schedule.',
        'viewer': 'Browse races, athletes, and results.'
    };
    return messages[role] || 'Your dashboard is ready.';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});
