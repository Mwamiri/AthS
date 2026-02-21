// Viewer Dashboard JavaScript
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
    
    if (!token || user.role !== 'viewer') {
        window.location.href = 'login.html';
        return null;
    }
    
    return user;
}

function logout() {
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
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

function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

function filterTable(tableId, searchValue) {
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');
    const filter = searchValue.toLowerCase();
    
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
    }
}

async function loadAllData() {
    const user = checkAuth();
    if (!user) return;
    
    document.getElementById('userName').textContent = user.name;
    
    try {
        const [racesResp, athletesResp, regsResp, resultsResp] = await Promise.all([
            fetchWithAuth(`${API_BASE_URL}/races`),
            fetchWithAuth(`${API_BASE_URL}/athletes`),
            fetchWithAuth(`${API_BASE_URL}/registrations`),
            fetchWithAuth(`${API_BASE_URL}/results`)
        ]);
        
        const races = await racesResp.json();
        const athletes = await athletesResp.json();
        const registrations = await regsResp.json();
        const results = await resultsResp.json();
        
        // Update stats
        document.getElementById('totalRaces').textContent = races.length;
        document.getElementById('totalAthletes').textContent = athletes.length;
        document.getElementById('totalEvents').textContent = countTotalEvents(races);
        document.getElementById('totalRegistrations').textContent = registrations.length;
        
        // Load tables
        loadRacesTable(races, registrations);
        loadAthletesTable(athletes, results);
        loadResultsTable(results, races);
        
    } catch (error) {
        console.error('Error loading data:', error);
        toast.show('Error loading data', 'error');
    }
}

function countTotalEvents(races) {
    return races.reduce((total, race) => total + (race.events ? race.events.length : 0), 0);
}

function loadRacesTable(races, registrations) {
    const tbody = document.getElementById('racesTableBody');
    
    if (races.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><div class="empty-state-icon">🏁</div><div>No races found</div></div></td></tr>`;
        return;
    }
    
    tbody.innerHTML = races.map(race => {
        const raceRegs = registrations.filter(r => r.race_id === race.id).length;
        const status = new Date(race.date) > new Date() ? 'Upcoming' : 'Completed';
        const badgeClass = status === 'Upcoming' ? 'badge-warning' : 'badge-success';
        
        return `
            <tr>
                <td><strong>${race.name}</strong></td>
                <td>${new Date(race.date).toLocaleDateString()}</td>
                <td>${race.location || 'TBA'}</td>
                <td>${race.events ? race.events.length : 0}</td>
                <td>${raceRegs}</td>
                <td><span class="badge ${badgeClass}">${status}</span></td>
            </tr>
        `;
    }).join('');
}

function loadAthletesTable(athletes, results) {
    const tbody = document.getElementById('athletesTableBody');
    
    if (athletes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state"><div class="empty-state-icon">🏃</div><div>No athletes found</div></div></td></tr>`;
        return;
    }
    
    tbody.innerHTML = athletes.map(athlete => {
        const athleteResults = results.filter(r => r.athlete_email === athlete.email);
        const bestTime = getBestTime(athleteResults);
        
        return `
            <tr>
                <td><strong>${athlete.name}</strong></td>
                <td>${athlete.email}</td>
                <td>${athlete.team || '-'}</td>
                <td>${athleteResults.length}</td>
                <td>${formatTime(bestTime)}</td>
            </tr>
        `;
    }).join('');
}

function loadResultsTable(results, races) {
    const tbody = document.getElementById('resultsTableBody');
    
    if (results.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><div class="empty-state-icon">📊</div><div>No results found</div></div></td></tr>`;
        return;
    }
    
    tbody.innerHTML = results.map(result => {
        const race = races.find(r => r.id === result.race_id);
        
        return `
            <tr>
                <td>${race ? race.name : 'Unknown'}</td>
                <td>${result.event_name || '-'}</td>
                <td><strong>${result.athlete_name || 'Unknown'}</strong></td>
                <td>${formatTime(result.time)}</td>
                <td>${result.position || '-'}</td>
                <td>${result.points || 0}</td>
            </tr>
        `;
    }).join('');
}

function getBestTime(results) {
    const times = results.filter(r => r.time).map(r => r.time);
    return times.length > 0 ? Math.min(...times) : null;
}

function formatTime(seconds) {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(2);
    return `${mins}:${secs.padStart(5, '0')}`;
}

function exportData(type) {
    toast.show(`Exporting ${type} data...`, 'info');
    setTimeout(() => {
        toast.show('Export feature coming soon', 'info');
    }, 1000);
}

function generateReport(type) {
    toast.show(`Generating ${type} report...`, 'info');
    setTimeout(() => {
        toast.show('Report generation coming soon', 'info');
    }, 1000);
}

document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
});