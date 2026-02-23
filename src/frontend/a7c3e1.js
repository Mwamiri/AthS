// Main Dashboard JavaScript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000/api' 
    : '/api';

class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container');
    }

    show(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        this.container.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 10);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

const toast = new ToastManager();

function checkAuth() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token) {
        window.location.href = 'login.html';
        return null;
    }
    
    return user;
}

async function logout() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
    } catch (error) {
        console.warn('Logout API call failed:', error);
    } finally {
        localStorage.removeItem('authToken');
        sessionStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    }
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
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        logout();
        return null;
    }
    
    return response;
}

// Role-based quick actions
const roleActions = {
    admin: [
        { icon: '👥', title: 'Manage Users', desc: 'Add, edit, or remove users', link: 'd4f8a9.view' },
        { icon: '⚙️', title: 'System Settings', desc: 'Configure system preferences', link: 'd4f8a9.view' },
        { icon: '📊', title: 'View Reports', desc: 'Generate system reports', link: '5c8b9e.view' },
        { icon: '🔐', title: 'Security', desc: 'Manage permissions and roles', link: 'd4f8a9.view' }
    ],
    chief_registrar: [
        { icon: '🏁', title: 'Manage Races', desc: 'Create and configure races', link: 'c1e5d4.view' },
        { icon: '📝', title: 'Registrations', desc: 'View all registrations', link: 'c1e5d4.view' },
        { icon: '📊', title: 'Start Lists', desc: 'Generate start lists', link: 'c1e5d4.view' },
        { icon: '🏆', title: 'Enter Results', desc: 'Record race results', link: '2a1f8d.view' }
    ],
    registrar: [
        { icon: '✍️', title: 'Register Athletes', desc: 'Add athlete registrations', link: 'c1e5d4.view' },
        { icon: '📤', title: 'Bulk Upload', desc: 'Upload athlete data', link: 'c1e5d4.view' },
        { icon: '📋', title: 'View Registrations', desc: 'See all registrations', link: 'c1e5d4.view' },
        { icon: '🔍', title: 'Search Athletes', desc: 'Find athlete information', link: 'c1e5d4.view' }
    ],
    starter: [
        { icon: '✅', title: 'Check Presence', desc: 'Mark athlete attendance', link: '8b2d7e.view' },
        { icon: '🎯', title: 'Confirm Start Lists', desc: 'Verify race participants', link: '8b2d7e.view' },
        { icon: '🏁', title: 'View Races', desc: 'See upcoming races', link: '8b2d7e.view' },
        { icon: '📊', title: 'Race Status', desc: 'Update race progress', link: '2a1f8d.view' }
    ],
    coach: [
        { icon: '👥', title: 'Team Roster', desc: 'Manage your athletes', link: '7e3f9a.view' },
        { icon: '📊', title: 'Performance', desc: 'View athlete analytics', link: '7e3f9a.view' },
        { icon: '📋', title: 'Registrations', desc: 'Team race entries', link: '7e3f9a.view' },
        { icon: '📝', title: 'Training Notes', desc: 'Document training plans', link: '7e3f9a.view' }
    ],
    athlete: [
        { icon: '🏆', title: 'My Records', desc: 'View personal bests', link: '9b4e7c.view' },
        { icon: '📅', title: 'Upcoming Races', desc: 'See registered races', link: '9b4e7c.view' },
        { icon: '📈', title: 'Performance', desc: 'Track your progress', link: '9b4e7c.view' },
        { icon: '🏁', title: 'Find Races', desc: 'Browse available races', link: 'index.html' }
    ],
    viewer: [
        { icon: '🏁', title: 'View Races', desc: 'See all races', link: '5c8b9e.view' },
        { icon: '🏃', title: 'View Athletes', desc: 'Browse athlete profiles', link: '5c8b9e.view' },
        { icon: '📊', title: 'View Results', desc: 'See race results', link: '5c8b9e.view' },
        { icon: '📄', title: 'Reports', desc: 'Generate reports', link: '5c8b9e.view' }
    ]
};

async function loadDashboard() {
    const user = checkAuth();
    if (!user) return;
    
    // Update user info
    document.getElementById('userName').textContent = user.name;
    document.getElementById('userWelcome').textContent = user.name;
    document.getElementById('userRole').textContent = formatRole(user.role);
    
    // Load quick actions based on role
    loadQuickActions(user.role);
    
    // Load statistics
    try {
        const [racesResp, athletesResp, resultsResp] = await Promise.all([
            fetchWithAuth(`${API_BASE_URL}/races`),
            fetchWithAuth(`${API_BASE_URL}/athletes`),
            fetchWithAuth(`${API_BASE_URL}/results`)
        ]);
        
        const races = await racesResp.json();
        const athletes = await athletesResp.json();
        const results = await resultsResp.json();
        
        document.getElementById('totalRaces').textContent = races.length;
        document.getElementById('totalAthletes').textContent = athletes.length;
        document.getElementById('totalEvents').textContent = countTotalEvents(races);
        document.getElementById('totalResults').textContent = results.length;
        
        // Load recent activity
        loadRecentActivity(user, races, results);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        toast.show('Error loading dashboard data', 'error');
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
    return roleNames[role] || role;
}

function loadQuickActions(role) {
    const grid = document.getElementById('quickActionsGrid');
    const actions = roleActions[role] || [];
    
    grid.innerHTML = actions.map(action => `
        <a href="${action.link}" class="action-btn">
            <div class="action-icon">${action.icon}</div>
            <div class="action-text">
                <h3>${action.title}</h3>
                <p>${action.desc}</p>
            </div>
        </a>
    `).join('');
}

function countTotalEvents(races) {
    return races.reduce((total, race) => total + (race.events ? race.events.length : 0), 0);
}

function loadRecentActivity(user, races, results) {
    const container = document.getElementById('activityContainer');
    const activities = [];
    
    // Add welcome message
    activities.push({
        time: 'Just now',
        desc: `Welcome back, ${user.name}! ${getWelcomeMessage(user.role)}`
    });
    
    // Add recent races
    const upcomingRaces = races.filter(r => new Date(r.date) > new Date()).slice(0, 2);
    upcomingRaces.forEach(race => {
        const daysUntil = Math.floor((new Date(race.date) - new Date()) / (1000 * 60 * 60 * 24));
        activities.push({
            time: `${daysUntil} day${daysUntil !== 1 ? 's' : ''} from now`,
            desc: `Upcoming race: ${race.name} at ${race.location || 'TBA'}`
        });
    });
    
    // Add recent results
    if (results.length > 0) {
        const recentResults = results.slice(-2);
        recentResults.forEach(result => {
            activities.push({
                time: 'Recently',
                desc: `${result.athlete_name || 'Athlete'} completed ${result.event_name || 'event'}`
            });
        });
    }
    
    container.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-time">${activity.time}</div>
            <p class="activity-desc">${activity.desc}</p>
        </div>
    `).join('');
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
