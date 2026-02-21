// Starter Dashboard JavaScript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '/api';

let currentUser = null;
let currentRaces = [];
let currentStartList = null;
let athletePresence = {};

// Toast Manager
class ToastManager {
    static show(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${this.getIcon(type)}</span>
            <span class="toast-message">${message}</span>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    static getIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }
}

// Check Authentication
function checkAuth() {
    const user = localStorage.getItem('athsys_user');
    if (!user) {
        window.location.href = 'login.html';
        return null;
    }
    
    try {
        currentUser = JSON.parse(user);
        
        // Check if user is starter or admin
        if (currentUser.role !== 'starter' && currentUser.role !== 'admin') {
            ToastManager.show('Access denied. Starter access required.', 'error');
            setTimeout(() => window.location.href = 'index.html', 2000);
            return null;
        }
        
        return currentUser;
    } catch (e) {
        window.location.href = 'login.html';
        return null;
    }
}

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', async () => {
    const user = checkAuth();
    if (!user) return;
    
    // Display user info
    document.getElementById('starter-user-name').textContent = user.name;
    document.getElementById('starter-user-display').textContent = `Role: STARTER`;
    
    // Setup logout
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Setup controls
    document.getElementById('load-startlist-btn').addEventListener('click', loadStartList);
    document.getElementById('check-all-btn').addEventListener('click', checkAll);
    document.getElementById('uncheck-all-btn').addEventListener('click', uncheckAll);
    document.getElementById('confirm-startlist-btn').addEventListener('click', confirmStartList);
    
    // Load initial data
    await loadRaces();
    await loadConfirmedStartLists();
});

// Load Races
async function loadRaces() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/races`, {
            headers: {
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            currentRaces = data.data;
            populateRaceFilter(currentRaces);
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        ToastManager.show('Failed to load races: ' + error.message, 'error');
    }
}

// Populate Race Filter
function populateRaceFilter(races) {
    const select = document.getElementById('race-filter');
    select.innerHTML = '<option value="">Select Race</option>' + 
        races.filter(r => r.status === 'open' || r.status === 'completed')
              .map(race => `<option value="${race.id}">${race.name} - ${new Date(race.date).toLocaleDateString()}</option>`)
              .join('');
    
    select.addEventListener('change', loadEventsForRace);
}

// Load Events for Selected Race
async function loadEventsForRace() {
    const raceId = document.getElementById('race-filter').value;
    if (!raceId) {
        document.getElementById('event-filter').innerHTML = '<option value="">Select Event</option>';
        return;
    }
    
    const race = currentRaces.find(r => r.id === parseInt(raceId));
    if (!race) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/events`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const raceEvents = data.data.filter(e => race.events && race.events.includes(e.id));
            const eventSelect = document.getElementById('event-filter');
            eventSelect.innerHTML = '<option value="">Select Event</option>' + 
                raceEvents.map(event => `<option value="${event.id}">${event.name}</option>`).join('');
        }
    } catch (error) {
        ToastManager.show('Failed to load events: ' + error.message, 'error');
    }
}

// Load Start List
async function loadStartList() {
    const raceId = document.getElementById('race-filter').value;
    const eventId = document.getElementById('event-filter').value;
    
    if (!raceId || !eventId) {
        ToastManager.show('Please select both race and event', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/startlists`, {
            headers: {
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Find start list for selected race and event
            currentStartList = data.data.find(sl => 
                sl.race_id === parseInt(raceId) && sl.event_id === parseInt(eventId)
            );
            
            if (currentStartList) {
                displayStartList(currentStartList);
            } else {
                // Generate mock start list from registrations
                await generateStartListFromRegistrations(raceId, eventId);
            }
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        ToastManager.show('Failed to load start list: ' + error.message, 'error');
    }
}

// Generate Start List from Registrations
async function generateStartListFromRegistrations(raceId, eventId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/races/${raceId}/registrations`, {
            headers: {
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const registrations = data.data;
            
            // Filter by event
            const eventResponse = await fetch(`${API_BASE_URL}/api/events`);
            const eventData = await eventResponse.json();
            const event = eventData.data.find(e => e.id === parseInt(eventId));
            
            const athletesInEvent = registrations.filter(reg => 
                reg.events && reg.events.some(e => e === event?.name)
            );
            
            const race = currentRaces.find(r => r.id === parseInt(raceId));
            
            currentStartList = {
                id: Date.now(),
                race_id: parseInt(raceId),
                event_id: parseInt(eventId),
                race_name: race?.name || 'Unknown Race',
                event_name: event?.name || 'Unknown Event',
                athletes: athletesInEvent.map((reg, idx) => ({
                    id: reg.id,
                    name: reg.athlete_name,
                    bib_number: idx + 1,
                    team: reg.team || 'Individual'
                })),
                status: 'pending'
            };
            
            displayStartList(currentStartList);
        }
    } catch (error) {
        ToastManager.show('Failed to generate start list: ' + error.message, 'error');
    }
}

// Display Start List
function displayStartList(startList) {
    document.getElementById('startlist-container').style.display = 'block';
    document.getElementById('startlist-title').textContent = `${startList.race_name} - ${startList.event_name}`;
    document.getElementById('startlist-info').textContent = 
        `Status: ${startList.status.toUpperCase()} • Athletes: ${startList.athletes.length}`;
    
    // Reset presence tracking
    athletePresence = {};
    startList.athletes.forEach(athlete => {
        athletePresence[athlete.id] = false;
    });
    
    // Display athletes
    const container = document.getElementById('athletes-list');
    container.innerHTML = startList.athletes.map(athlete => `
        <div class="athlete-item">
            <input type="checkbox" class="athlete-checkbox" id="athlete-${athlete.id}" 
                   data-athlete-id="${athlete.id}" onchange="updatePresence(${athlete.id})">
            <div class="athlete-details">
                <div class="athlete-name">
                    <span style="color: var(--primary-color); font-weight: 900; margin-right: 0.5rem;">
                        #${athlete.bib_number || athlete.id}
                    </span>
                    ${athlete.name}
                </div>
                <div class="athlete-info">
                    ${athlete.team || 'Individual'}
                </div>
            </div>
            <span class="athlete-status status-absent" id="status-${athlete.id}">Absent</span>
        </div>
    `).join('');
    
    updateStats();
    
    // Scroll to start list
    document.getElementById('startlist-container').scrollIntoView({ behavior: 'smooth' });
}

// Update Athlete Presence
function updatePresence(athleteId) {
    const checkbox = document.getElementById(`athlete-${athleteId}`);
    const status = document.getElementById(`status-${athleteId}`);
    
    athletePresence[athleteId] = checkbox.checked;
    
    if (checkbox.checked) {
        status.textContent = 'Present';
        status.className = 'athlete-status status-present';
    } else {
        status.textContent = 'Absent';
        status.className = 'athlete-status status-absent';
    }
    
    updateStats();
}

// Update Statistics
function updateStats() {
    const total = Object.keys(athletePresence).length;
    const present = Object.values(athletePresence).filter(p => p).length;
    const absent = total - present;
    
    document.getElementById('total-athletes').textContent = total;
    document.getElementById('present-count').textContent = present;
    document.getElementById('absent-count').textContent = absent;
}

// Check All Athletes
function checkAll() {
    Object.keys(athletePresence).forEach(athleteId => {
        const checkbox = document.getElementById(`athlete-${athleteId}`);
        if (checkbox) {
            checkbox.checked = true;
            updatePresence(parseInt(athleteId));
        }
    });
    ToastManager.show('All athletes marked as present', 'success');
}

// Uncheck All Athletes
function uncheckAll() {
    Object.keys(athletePresence).forEach(athleteId => {
        const checkbox = document.getElementById(`athlete-${athleteId}`);
        if (checkbox) {
            checkbox.checked = false;
            updatePresence(parseInt(athleteId));
        }
    });
    ToastManager.show('All athletes marked as absent', 'info');
}

// Confirm Start List
async function confirmStartList() {
    if (!currentStartList) {
        ToastManager.show('No start list loaded', 'warning');
        return;
    }
    
    const presentCount = Object.values(athletePresence).filter(p => p).length;
    const totalCount = Object.keys(athletePresence).length;
    
    if (presentCount === 0) {
        ToastManager.show('No athletes marked as present', 'warning');
        return;
    }
    
    const confirmMsg = `Confirm start list with ${presentCount} of ${totalCount} athletes present?`;
    if (!confirm(confirmMsg)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/startlists/${currentStartList.id}/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            },
            body: JSON.stringify({
                confirmed_by: currentUser.id,
                present_athletes: Object.entries(athletePresence)
                    .filter(([_, present]) => present)
                    .map(([id, _]) => parseInt(id))
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            ToastManager.show('Start list confirmed successfully!', 'success');
            
            // Reset form
            document.getElementById('startlist-container').style.display = 'none';
            document.getElementById('race-filter').value = '';
            document.getElementById('event-filter').innerHTML = '<option value="">Select Event</option>';
            currentStartList = null;
            
            // Reload confirmed lists
            await loadConfirmedStartLists();
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        ToastManager.show('Failed to confirm start list: ' + error.message, 'error');
    }
}

// Load Confirmed Start Lists
async function loadConfirmedStartLists() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/startlists`, {
            headers: {
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const confirmedLists = data.data.filter(sl => sl.status === 'confirmed');
            displayConfirmedLists(confirmedLists);
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Failed to load confirmed lists:', error);
        document.getElementById('confirmed-lists-tbody').innerHTML = 
            '<tr><td colspan="5" style="text-align: center; color: var(--danger-color);">Failed to load confirmed start lists</td></tr>';
    }
}

// Display Confirmed Lists
function displayConfirmedLists(lists) {
    const tbody = document.getElementById('confirmed-lists-tbody');
    
    if (lists.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No confirmed start lists yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = lists.slice(0, 10).map(sl => `
        <tr>
            <td>${sl.race_name}</td>
            <td>${sl.event_name}</td>
            <td>${sl.athletes.length} athletes</td>
            <td>${sl.confirmed_at ? new Date(sl.confirmed_at).toLocaleString() : 'Recently'}</td>
            <td><span class="badge badge-success">Confirmed</span></td>
        </tr>
    `).join('');
}

// Logout
function logout() {
    localStorage.clear();
    sessionStorage.clear();
    ToastManager.show('Logged out successfully', 'success');
    setTimeout(() => window.location.href = 'login.html', 1000);
}
