// Coach Dashboard JavaScript
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
    
    if (!token || user.role !== 'coach') {
        window.location.href = 'login.html';
        return null;
    }
    
    return user;
}

// Logout function
async function logout() {
    return logoutWithRevocation({
        redirectTo: 'login.html'
    });
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

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

// Load coach data
async function loadCoachData() {
    const user = checkAuth();
    if (!user) return;
    
    // Update user info
    document.getElementById('userName').textContent = user.name;
    document.getElementById('coachName').textContent = user.name;
    document.getElementById('coachEmail').textContent = `📧 ${user.email}`;
    document.getElementById('coachTeam').textContent = `📍 ${user.team || 'Independent Coach'}`;
    
    try {
        // Load athletes and results
        const athletesResponse = await fetchWithAuth(`${API_BASE_URL}/athletes`);
        const athletes = await athletesResponse.json();
        
        const resultsResponse = await fetchWithAuth(`${API_BASE_URL}/results`);
        const results = await resultsResponse.json();
        
        const racesResponse = await fetchWithAuth(`${API_BASE_URL}/races`);
        const races = await racesResponse.json();
        
        const regsResponse = await fetchWithAuth(`${API_BASE_URL}/registrations`);
        const registrations = await regsResponse.json();
        
        // Filter for team athletes (same team as coach)
        const teamAthletes = athletes.filter(a => a.team === user.team);
        const teamEmails = teamAthletes.map(a => a.email);
        const teamResults = results.filter(r => teamEmails.includes(r.athlete_email));
        
        // Update statistics
        document.getElementById('totalAthletes').textContent = teamAthletes.length;
        document.getElementById('activeAthletes').textContent = countActiveAthletes(teamAthletes, registrations);
        document.getElementById('upcomingRaces').textContent = countUpcomingRaces(registrations, races, teamEmails);
        document.getElementById('teamRecords').textContent = countTeamRecords(teamResults);
        
        // Load team roster
        loadTeamRoster(teamAthletes, teamResults);
        
        // Load performance data
        loadPerformanceData(teamAthletes, teamResults);
        
        // Load registrations
        loadRegistrations(races, registrations, teamEmails);
        
    } catch (error) {
        console.error('Error loading coach data:', error);
        toast.show('Error loading data', 'error');
    }
}

function countActiveAthletes(athletes, registrations) {
    const activeEmails = new Set(registrations.map(r => r.athlete_email));
    return athletes.filter(a => activeEmails.has(a.email)).length;
}

function countUpcomingRaces(registrations, races, teamEmails) {
    const now = new Date();
    return registrations.filter(reg => {
        const race = races.find(r => r.id === reg.race_id);
        return race && new Date(race.date) > now && teamEmails.includes(reg.athlete_email);
    }).length;
}

function countTeamRecords(results) {
    const eventBests = {};
    results.forEach(result => {
        if (result.time && (!eventBests[result.event_id] || result.time < eventBests[result.event_id])) {
            eventBests[result.event_id] = result.time;
        }
    });
    return Object.keys(eventBests).length;
}

function loadTeamRoster(athletes, results) {
    const grid = document.getElementById('athleteGrid');
    
    if (athletes.length === 0) {
        grid.innerHTML = `<div class="empty-state">
            <div class="empty-state-icon">👥</div>
            <div>No athletes in your team yet</div>
        </div>`;
        return;
    }
    
    grid.innerHTML = athletes.map(athlete => {
        const athleteResults = results.filter(r => r.athlete_email === athlete.email);
        const totalRaces = athleteResults.length;
        const prs = countPRs(athleteResults);
        
        return `
            <div class="athlete-card">
                <div class="athlete-card-header">
                    <div class="athlete-avatar">${athlete.name.charAt(0).toUpperCase()}</div>
                    <div>
                        <div class="athlete-name">${athlete.name}</div>
                        <div class="athlete-team">${athlete.email}</div>
                    </div>
                </div>
                <div class="athlete-stats">
                    <div class="athlete-stat">
                        <div class="athlete-stat-value">${totalRaces}</div>
                        <div class="athlete-stat-label">Races</div>
                    </div>
                    <div class="athlete-stat">
                        <div class="athlete-stat-value">${prs}</div>
                        <div class="athlete-stat-label">PRs</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function countPRs(results) {
    const eventBests = {};
    results.forEach(result => {
        if (result.time && (!eventBests[result.event_id] || result.time < eventBests[result.event_id])) {
            eventBests[result.event_id] = result.time;
        }
    });
    return Object.keys(eventBests).length;
}

function formatTime(seconds) {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(2);
    return `${mins}:${secs.padStart(5, '0')}`;
}

function loadPerformanceData(athletes, results) {
    const tbody = document.getElementById('performanceTableBody');
    
    if (athletes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6">
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <div>No performance data available</div>
            </div>
        </td></tr>`;
        return;
    }
    
    tbody.innerHTML = athletes.map(athlete => {
        const athleteResults = results.filter(r => r.athlete_email === athlete.email);
        const totalRaces = athleteResults.length;
        const prs = countPRs(athleteResults);
        const bestTime = getBestTime(athleteResults);
        const avgPosition = getAvgPosition(athleteResults);
        const events = new Set(athleteResults.map(r => r.event_name).filter(Boolean)).size;
        
        return `
            <tr>
                <td><strong>${athlete.name}</strong></td>
                <td>${events || '-'}</td>
                <td>${totalRaces}</td>
                <td>${formatTime(bestTime)}</td>
                <td>${avgPosition || '-'}</td>
                <td>${prs}</td>
            </tr>
        `;
    }).join('');
}

function getBestTime(results) {
    const times = results.filter(r => r.time).map(r => r.time);
    return times.length > 0 ? Math.min(...times) : null;
}

function getAvgPosition(results) {
    const positions = results.filter(r => r.position).map(r => r.position);
    if (positions.length === 0) return null;
    const avg = positions.reduce((a, b) => a + b, 0) / positions.length;
    return avg.toFixed(1);
}

function loadRegistrations(races, registrations, teamEmails) {
    const tbody = document.getElementById('registrationsTableBody');
    
    // Group registrations by race
    const raceGroups = {};
    registrations.forEach(reg => {
        if (teamEmails.includes(reg.athlete_email)) {
            if (!raceGroups[reg.race_id]) {
                raceGroups[reg.race_id] = [];
            }
            raceGroups[reg.race_id].push(reg);
        }
    });
    
    if (Object.keys(raceGroups).length === 0) {
        tbody.innerHTML = `<tr><td colspan="5">
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <div>No race registrations yet</div>
            </div>
        </td></tr>`;
        return;
    }
    
    tbody.innerHTML = Object.entries(raceGroups).map(([raceId, regs]) => {
        const race = races.find(r => r.id === parseInt(raceId));
        if (!race) return '';
        
        const status = new Date(race.date) > new Date() ? 'Upcoming' : 'Completed';
        const badgeClass = status === 'Upcoming' ? 'badge-warning' : 'badge-success';
        
        return `
            <tr>
                <td><strong>${race.name}</strong></td>
                <td>${new Date(race.date).toLocaleDateString()}</td>
                <td>${race.location || 'TBA'}</td>
                <td>${regs.length} athletes</td>
                <td><span class="badge ${badgeClass}">${status}</span></td>
            </tr>
        `;
    }).join('');
}

function addAthlete() {
    toast.show('Add athlete feature coming soon', 'info');
}

function addNote() {
    toast.show('Training notes feature coming soon', 'info');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadCoachData();
});
