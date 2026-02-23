// Results Dashboard JavaScript
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
    
    if (!token) {
        window.location.href = 'login.html';
        return null;
    }
    
    // Allow admin, chief_registrar, registrar, starter
    const allowedRoles = ['admin', 'chief_registrar', 'registrar', 'starter'];
    if (!allowedRoles.includes(user.role)) {
        window.location.href = 'index.html';
        return null;
    }
    
    return user;
}

async function logout() {
    return logoutWithRevocation({
        redirectTo: 'login.html'
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

function formatTime(seconds) {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(2);
    return `${mins}:${secs.padStart(5, '0')}`;
}

// Load races into dropdowns
async function loadRaces() {
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/races`);
        const races = await response.json();
        
        const raceSelect = document.getElementById('raceSelect');
        const leaderboardRace = document.getElementById('leaderboardRace');
        
        races.forEach(race => {
            const option = `<option value="${race.id}">${race.name} - ${new Date(race.date).toLocaleDateString()}</option>`;
            raceSelect.innerHTML += option;
            leaderboardRace.innerHTML += option;
        });
    } catch (error) {
        console.error('Error loading races:', error);
    }
}

async function loadRaceEvents() {
    const raceId = document.getElementById('raceSelect').value;
    if (!raceId) return;
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/races/${raceId}`);
        const race = await response.json();
        
        const eventSelect = document.getElementById('eventSelect');
        const leaderboardEvent = document.getElementById('leaderboardEvent');
        
        eventSelect.innerHTML = '<option value="">Select Event</option>';
        leaderboardEvent.innerHTML = '<option value="">All Events</option>';
        
        if (race.events && race.events.length > 0) {
            race.events.forEach(event => {
                const option = `<option value="${event.id}">${event.name}</option>`;
                eventSelect.innerHTML += option;
                leaderboardEvent.innerHTML += option;
            });
        }
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

async function loadEventAthletes() {
    const raceId = document.getElementById('raceSelect').value;
    const eventId = document.getElementById('eventSelect').value;
    
    if (!raceId || !eventId) return;
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/registrations?race_id=${raceId}`);
        const registrations = await response.json();
        
        const container = document.getElementById('quickEntryContainer');
        
        if (registrations.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #999;">No athletes registered for this event</p>';
            return;
        }
        
        container.innerHTML = registrations.map((reg, index) => `
            <div class="quick-entry">
                <div class="form-group">
                    <label>Pos</label>
                    <input type="number" id="position_${index}" value="${index + 1}" min="1">
                </div>
                <div class="form-group">
                    <label>Athlete</label>
                    <input type="text" value="${reg.athlete_name}" readonly style="background: #f8f9fa;">
                </div>
                <div class="form-group">
                    <label>Time (MM:SS.MS)</label>
                    <input type="text" id="time_${index}" placeholder="0:00.00" pattern="[0-9]+:[0-9]{2}\\.[0-9]{2}">
                </div>
                <div class="form-group">
                    <label>Points</label>
                    <input type="number" id="points_${index}" value="${10 - index}" min="0">
                </div>
                <div class="form-group">
                    <label>Status</label>
                    <select id="status_${index}">
                        <option value="completed">Completed</option>
                        <option value="DNS">DNS</option>
                        <option value="DNF">DNF</option>
                        <option value="DQ">DQ</option>
                    </select>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading athletes:', error);
    }
}

function markStatus(status) {
    // Get selected athlete rows and mark them with the status
    toast.show(`Mark as ${status} feature coming soon`, 'info');
}

async function saveResults() {
    const raceId = document.getElementById('raceSelect').value;
    const eventId = document.getElementById('eventSelect').value;
    const heat = document.getElementById('heatSelect').value;
    
    if (!raceId || !eventId) {
        toast.show('Please select race and event', 'error');
        return;
    }
    
    // Collect results from form
    const results = [];
    let index = 0;
    
    while (document.getElementById(`position_${index}`)) {
        const position = document.getElementById(`position_${index}`).value;
        const time = document.getElementById(`time_${index}`).value;
        const points = document.getElementById(`points_${index}`).value;
        const status = document.getElementById(`status_${index}`).value;
        
        results.push({
            race_id: parseInt(raceId),
            event_id: parseInt(eventId),
            heat,
            position: parseInt(position),
            time,
            points: parseInt(points),
            status
        });
        
        index++;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/results/batch`, {
            method: 'POST',
            body: JSON.stringify({ results })
        });
        
        if (response.ok) {
            toast.show('Results saved successfully!', 'success');
            loadLeaderboard();
        } else {
            toast.show('Error saving results', 'error');
        }
    } catch (error) {
        console.error('Error saving results:', error);
        toast.show('Error saving results', 'error');
    }
}

async function loadLeaderboard() {
    const raceId = document.getElementById('leaderboardRace').value;
    const eventId = document.getElementById('leaderboardEvent').value;
    
    try {
        let url = `${API_BASE_URL}/results`;
        const params = [];
        if (raceId) params.push(`race_id=${raceId}`);
        if (eventId) params.push(`event_id=${eventId}`);
        if (params.length > 0) url += '?' + params.join('&');
        
        const response = await fetchWithAuth(url);
        const results = await response.json();
        
        const tbody = document.getElementById('leaderboardBody');
        
        if (results.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7">
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <div>No results available</div>
                </div>
            </td></tr>`;
            return;
        }
        
        // Sort by time
        results.sort((a, b) => {
            if (a.time && b.time) return parseFloat(a.time) - parseFloat(b.time);
            return 0;
        });
        
        tbody.innerHTML = results.map((result, index) => {
            const position = index + 1;
            let positionClass = 'position-other';
            if (position === 1) positionClass = 'position-1';
            else if (position === 2) positionClass = 'position-2';
            else if (position === 3) positionClass = 'position-3';
            
            return `
                <tr>
                    <td><div class="position-badge ${positionClass}">${position}</div></td>
                    <td>${result.bib_number || '-'}</td>
                    <td><strong>${result.athlete_name || 'Unknown'}</strong></td>
                    <td>${result.team || '-'}</td>
                    <td><span class="time-display">${formatTime(result.time)}</span></td>
                    <td>${result.points || 0}</td>
                    <td><span class="badge badge-success">${result.status || 'Completed'}</span></td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading leaderboard:', error);
    }
}

function exportResults() {
    const format = document.getElementById('exportFormat').value;
    const include = document.getElementById('exportInclude').value;
    
    toast.show(`Exporting as ${format.toUpperCase()}...`, 'info');
    
    // In production, this would trigger actual export
    setTimeout(() => {
        toast.show('Export feature coming soon', 'info');
    }, 1000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const user = checkAuth();
    if (user) {
        document.getElementById('userName').textContent = user.name;
        loadRaces();
    }
});
