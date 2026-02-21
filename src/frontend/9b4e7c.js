// Athlete Dashboard JavaScript
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

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token || user.role !== 'athlete') {
        window.location.href = 'login.html';
        return null;
    }
    
    return user;
}

// Logout function
function logout() {
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

// Fetch with auth
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

// Calculate countdown
function calculateCountdown(dateString) {
    const raceDate = new Date(dateString);
    const now = new Date();
    const diff = raceDate - now;
    
    if (diff <= 0) return 'Race Day!';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days} day${days !== 1 ? 's' : ''} away`;
    return `${hours} hour${hours !== 1 ? 's' : ''} away`;
}

// Format time (seconds to MM:SS.MS)
function formatTime(seconds) {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(2);
    return `${mins}:${secs.padStart(5, '0')}`;
}

// Load athlete data
async function loadAthleteData() {
    const user = checkAuth();
    if (!user) return;
    
    // Update user info
    document.getElementById('userName').textContent = user.name;
    document.getElementById('athleteName').textContent = user.name;
    document.getElementById('athleteEmail').textContent = `📧 ${user.email}`;
    document.getElementById('athleteTeam').textContent = `📍 ${user.team || 'No Team'}`;
    
    try {
        // Load athlete races and registrations
        const racesResponse = await fetchWithAuth(`${API_BASE_URL}/races`);
        const races = await racesResponse.json();
        
        const regsResponse = await fetchWithAuth(`${API_BASE_URL}/registrations`);
        const registrations = await regsResponse.json();
        
        const resultsResponse = await fetchWithAuth(`${API_BASE_URL}/results`);
        const results = await resultsResponse.json();
        
        // Filter for this athlete
        const myRegistrations = registrations.filter(r => r.athlete_email === user.email);
        const myResults = results.filter(r => r.athlete_email === user.email);
        
        // Update statistics
        document.getElementById('totalRaces').textContent = myResults.length || 0;
        document.getElementById('personalRecords').textContent = countPersonalRecords(myResults);
        document.getElementById('upcomingRaces').textContent = countUpcomingRaces(myRegistrations, races);
        document.getElementById('bestPosition').textContent = getBestPosition(myResults);
        
        // Load personal records
        loadPersonalRecords(myResults);
        
        // Load upcoming races
        loadUpcomingRaces(myRegistrations, races);
        
        // Load race history
        loadRaceHistory(myResults, races);
        
        // Load performance chart
        loadPerformanceChart(myResults);
        
    } catch (error) {
        console.error('Error loading athlete data:', error);
        toast.show('Error loading data', 'error');
    }
}

function countPersonalRecords(results) {
    const eventBests = {};
    results.forEach(result => {
        if (result.time && (!eventBests[result.event_id] || result.time < eventBests[result.event_id])) {
            eventBests[result.event_id] = result.time;
        }
    });
    return Object.keys(eventBests).length;
}

function countUpcomingRaces(registrations, races) {
    const now = new Date();
    return registrations.filter(reg => {
        const race = races.find(r => r.id === reg.race_id);
        return race && new Date(race.date) > now;
    }).length;
}

function getBestPosition(results) {
    if (results.length === 0) return '-';
    const positions = results.filter(r => r.position).map(r => r.position);
    if (positions.length === 0) return '-';
    const best = Math.min(...positions);
    return best === 1 ? '🥇 1st' : best === 2 ? '🥈 2nd' : best === 3 ? '🥉 3rd' : `#${best}`;
}

function loadPersonalRecords(results) {
    const eventBests = {};
    
    results.forEach(result => {
        if (result.time) {
            const eventId = result.event_id;
            if (!eventBests[eventId] || result.time < eventBests[eventId].time) {
                eventBests[eventId] = result;
            }
        }
    });
    
    const tbody = document.getElementById('recordsTableBody');
    const records = Object.values(eventBests);
    
    if (records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5">
            <div class="empty-state">
                <div class="empty-state-icon">🏆</div>
                <div>No personal records yet. Register for a race to get started!</div>
            </div>
        </td></tr>`;
        return;
    }
    
    tbody.innerHTML = records.map(record => `
        <tr>
            <td><strong>${record.event_name || 'Event'}</strong></td>
            <td><span class="time-badge">${formatTime(record.time)}</span></td>
            <td>${record.race_name || 'Race'}</td>
            <td>${record.date ? new Date(record.date).toLocaleDateString() : '-'}</td>
            <td>${record.position ? `#${record.position}` : '-'}</td>
        </tr>
    `).join('');
}

function loadUpcomingRaces(registrations, races) {
    const now = new Date();
    const upcoming = registrations
        .map(reg => {
            const race = races.find(r => r.id === reg.race_id);
            return race && new Date(race.date) > now ? { ...reg, race } : null;
        })
        .filter(Boolean)
        .sort((a, b) => new Date(a.race.date) - new Date(b.race.date));
    
    const container = document.getElementById('upcomingRacesContainer');
    
    if (upcoming.length === 0) {
        container.innerHTML = `<div class="empty-state">
            <div class="empty-state-icon">🎯</div>
            <div>No upcoming races. Check available races and register!</div>
        </div>`;
        return;
    }
    
    container.innerHTML = upcoming.map(item => `
        <div class="race-card">
            <div class="race-name">${item.race.name}</div>
            <div class="race-details">
                <span>📅 ${new Date(item.race.date).toLocaleDateString()}</span>
                <span>📍 ${item.race.location || 'Location TBA'}</span>
                <span>🏃 ${item.events ? item.events.join(', ') : 'Events TBA'}</span>
            </div>
            <div class="countdown">${calculateCountdown(item.race.date)}</div>
        </div>
    `).join('');
}

function loadRaceHistory(results, races) {
    const tbody = document.getElementById('historyTableBody');
    
    const history = results
        .map(result => {
            const race = races.find(r => r.id === result.race_id);
            return race ? { ...result, race } : null;
        })
        .filter(Boolean)
        .sort((a, b) => new Date(b.race.date) - new Date(a.race.date));
    
    if (history.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6">
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <div>No race history yet</div>
            </div>
        </td></tr>`;
        return;
    }
    
    tbody.innerHTML = history.map(item => `
        <tr>
            <td>${new Date(item.race.date).toLocaleDateString()}</td>
            <td>${item.race.name}</td>
            <td>${item.event_name || 'Event'}</td>
            <td>${item.time ? formatTime(item.time) : '-'}</td>
            <td>${item.position ? `#${item.position}` : '-'}</td>
            <td><span class="badge badge-${item.status === 'completed' ? 'success' : 'warning'}">${item.status || 'Registered'}</span></td>
        </tr>
    `).join('');
}

function loadPerformanceChart(results) {
    // Simple text-based chart placeholder (would use Chart.js in production)
    const canvas = document.getElementById('performanceChart');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = canvas.parentElement.offsetWidth;
    canvas.height = 300;
    
    if (results.length === 0) {
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#999';
        ctx.font = '16px Arial';
        ctx.fillText('No performance data yet', canvas.width / 2, canvas.height / 2);
        return;
    }
    
    // Draw placeholder chart message
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#667eea';
    ctx.font = 'bold 18px Arial';
    ctx.fillText('Performance Analytics Coming Soon', canvas.width / 2, canvas.height / 2 - 20);
    ctx.fillStyle = '#999';
    ctx.font = '14px Arial';
    ctx.fillText('Chart.js integration will display your progress over time', canvas.width / 2, canvas.height / 2 + 20);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadAthleteData();
});
