// Race Management JavaScript
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
            position: fixed; top: 20px; right: 20px; z-index: 10000;
            display: flex; flex-direction: column; gap: 10px;
        `;
        return container;
    }

    show(message, type = 'info') {
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.style.cssText = `
            padding: 1rem 1.5rem; border-radius: 8px; color: white;
            min-width: 250px; animation: slideIn 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        const colors = { success: '#06d6a0', error: '#e63946', warning: '#f7931e', info: '#4a90e2' };
        toast.style.background = colors[type] || colors.info;
        this.container.appendChild(toast);
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
}

const toast = new ToastManager();
let allRaces = [];
let currentEditingRace = null;

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
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
    } catch (error) {
        console.warn('Logout API call failed:', error);
    } finally {
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = 'login.html';
    }
}

async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    
    try {
        const response = await fetch(url, { ...options, headers });
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

async function loadRaces() {
    const user = checkAuth();
    if (!user) return;
    
    document.getElementById('userName').textContent = user.name || user.email;
    
    // Show loading skeleton
    showLoadingSkeleton('racesContainer', 4, 'card');
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/api/races`);
        if (!response) return;
        
        const races = await response.json();
        allRaces = Array.isArray(races) ? races : [];
        displayRaces(allRaces);
        
        // Check permissions for creating races
        const canCreate = ['admin', 'chief_registrar'].includes(user.role);
        document.getElementById('createRaceBtn').style.display = canCreate ? 'inline-block' : 'none';
        
    } catch (error) {
        console.error('Error loading races:', error);
        toast.show('Error loading races', 'error');
        document.getElementById('racesContainer').innerHTML = '<div class="error">Failed to load races</div>';
    }
}

function displayRaces(races) {
    const container = document.getElementById('racesContainer');
    
    if (!races || races.length === 0) {
        showEmptyState('racesContainer', {
            icon: '🏁',
            title: 'No races found',
            message: 'Get started by creating your first race or adjust your search filters',
            actionText: '➕ Create First Race',
            actionCallback: canEdit() ? 'showCreateRaceModal()' : null,
            showAction: canEdit()
        });
        return;
    }
    
    container.innerHTML = races.map(race => {
        const statusColors = {
            upcoming: '#4a90e2',
            registration_open: '#06d6a0',
            registration_closed: '#f7931e',
            in_progress: '#a855f7',
            completed: '#666'
        };
        
        const statusColor = statusColors[race.status] || '#666';
        const raceDate = formatDateLong(race.date);
        
        return `
            <div class="race-card" style="background: var(--background-dark); border-radius: 12px; padding: 1.5rem; border-left: 4px solid ${statusColor};">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: var(--text-color);">${race.name}</h3>
                    <span class="status-badge" style="background: ${statusColor}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem;">
                        ${formatStatus(race.status)}
                    </span>
                </div>
                <p style="color: var(--text-secondary); margin: 0.5rem 0;">
                    📅 ${raceDate} | 📍 ${race.location}
                </p>
                ${race.description ? `<p style="color: var(--text-secondary); margin: 0.5rem 0; font-size: 0.9rem;">${race.description}</p>` : ''}
                <div style="display: flex; gap: 0.5rem; margin-top: 1rem; flex-wrap: wrap;">
                    <button class="btn btn-small btn-primary" onclick="viewRaceDetails(${race.id})">👁️ View Details</button>
                    <button class="btn btn-small btn-secondary" onclick="viewRegistrations(${race.id})">📋 Registrations</button>
                    ${canEdit() ? `<button class="btn btn-small" onclick="editRace(${race.id})">✏️ Edit</button>` : ''}
                    ${race.public_registration ? `<button class="btn btn-small btn-success" onclick="copyPublicLink(${race.id})">🔗 Public Link</button>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function formatStatus(status) {
    return status.replace(/_/g, ' ').toUpperCase();
}

function canEdit() {
    const userStr = localStorage.getItem('user') || sessionStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    return user && ['admin', 'chief_registrar'].includes(user.role);
}

function filterRaces() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const filtered = allRaces.filter(race => 
        race.name.toLowerCase().includes(searchTerm) ||
        race.location.toLowerCase().includes(searchTerm) ||
        (race.description && race.description.toLowerCase().includes(searchTerm))
    );
    displayRaces(filtered);
}

function refreshRaces() {
    toast.show('Refreshing races...', 'info');
    loadRaces();
}

function showCreateRaceModal() {
    currentEditingRace = null;
    document.getElementById('modalTitle').textContent = 'Create New Race';
    document.getElementById('raceForm').reset();
    document.getElementById('raceId').value = '';
    document.getElementById('raceModal').style.display = 'flex';
}

function closeRaceModal() {
    document.getElementById('raceModal').style.display = 'none';
    currentEditingRace = null;
}

async function editRace(raceId) {
    const race = allRaces.find(r => r.id === raceId);
    if (!race) return;
    
    currentEditingRace = race;
    document.getElementById('modalTitle').textContent = 'Edit Race';
    document.getElementById('raceId').value = race.id;
    document.getElementById('raceName').value = race.name;
    document.getElementById('raceDate').value = race.date.split('T')[0];
    document.getElementById('raceLocation').value = race.location;
    document.getElementById('raceDescription').value = race.description || '';
    document.getElementById('raceStatus').value = race.status;
    document.getElementById('racePublic').checked = race.public_registration;
    document.getElementById('raceModal').style.display = 'flex';
}

async function viewRaceDetails(raceId) {
    const race = allRaces.find(r => r.id === raceId);
    if (!race) return;
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/api/races/${raceId}`);
        if (!response) return;
        
        const raceDetails = await response.json();
        
        const content = `
            <div style="padding: 1rem;">
                <h3>${raceDetails.name}</h3>
                <p><strong>Date:</strong> ${new Date(raceDetails.date).toLocaleDateString()}</p>
                <p><strong>Location:</strong> ${raceDetails.location}</p>
                <p><strong>Status:</strong> ${formatStatus(raceDetails.status)}</p>
                ${raceDetails.description ? `<p><strong>Description:</strong> ${raceDetails.description}</p>` : ''}
                <p><strong>Public Registration:</strong> ${raceDetails.public_registration ? 'Enabled' : 'Disabled'}</p>
                ${raceDetails.events && raceDetails.events.length > 0 ? `
                    <h4 style="margin-top: 1.5rem;">Events (${raceDetails.events.length})</h4>
                    <div style="display: grid; gap: 0.5rem;">
                        ${raceDetails.events.map(event => `
                            <div style="padding: 0.75rem; background: var(--background-light); border-radius: 8px;">
                                <strong>${event.name}</strong> - ${event.category} 
                                <span style="color: var(--text-secondary);">(${event.gender})</span>
                            </div>
                        `).join('')}
                    </div>
                ` : '<p style="color: var(--text-secondary);">No events configured yet.</p>'}
            </div>
        `;
        
        document.getElementById('raceDetailsContent').innerHTML = content;
        document.getElementById('raceDetailsModal').style.display = 'flex';
        
    } catch (error) {
        console.error('Error loading race details:', error);
        toast.show('Error loading race details', 'error');
    }
}

function closeDetailsModal() {
    document.getElementById('raceDetailsModal').style.display = 'none';
}

function viewRegistrations(raceId) {
    window.location.href = `registrations.html?race_id=${raceId}`;
}

function copyPublicLink(raceId) {
    const publicUrl = `${window.location.origin}/public-register.html?race_id=${raceId}`;
    navigator.clipboard.writeText(publicUrl).then(() => {
        toast.show('Public registration link copied!', 'success');
    }).catch(() => {
        toast.show('Failed to copy link', 'error');
    });
}

// Form submission
document.addEventListener('DOMContentLoaded', () => {
    loadRaces();
    
    document.getElementById('raceForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const raceId = document.getElementById('raceId').value;
        const raceData = {
            name: document.getElementById('raceName').value,
            date: document.getElementById('raceDate').value,
            location: document.getElementById('raceLocation').value,
            description: document.getElementById('raceDescription').value,
            status: document.getElementById('raceStatus').value,
            public_registration: document.getElementById('racePublic').checked
        };
        
        try {
            const url = raceId 
                ? `${API_BASE_URL}/api/races/${raceId}`
                : `${API_BASE_URL}/api/races`;
            
            const method = raceId ? 'PUT' : 'POST';
            
            const response = await fetchWithAuth(url, {
                method: method,
                body: JSON.stringify(raceData)
            });
            
            if (!response) return;
            
            const result = await response.json();
            
            if (response.ok) {
                toast.show(raceId ? 'Race updated successfully!' : 'Race created successfully!', 'success');
                closeRaceModal();
                loadRaces();
            } else {
                toast.show(result.message || 'Error saving race', 'error');
            }
        } catch (error) {
            console.error('Error saving race:', error);
            toast.show('Error saving race', 'error');
        }
    });
});

// Modal click outside to close
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});
// ============================================
// New Improvements
// ============================================

// Debounced filter function
const debouncedFilterRaces = debounceSearch(filterRaces);

// Export to CSV function
function exportRaces() {
    if (!allRaces || allRaces.length === 0) {
        toast.show('No races to export', 'warning');
        return;
    }
    
    const exportData = allRaces.map(race =>  ({
        'Race Name': race.name,
        'Date': formatDate(race.date),
        'Location': race.location,
        'Status': formatStatus(race.status),
        'Public Registration': race.public_registration ? 'Yes' : 'No',
        'Description': race.description || ''
    }));
    
    exportToCSV(exportData, 'athsys_races');
    toast.show('Races exported successfully!', 'success');
}

// Show loading skeleton
function showRacesLoading() {
    showLoadingSkeleton('racesContainer', 4, 'card');
}

// Initialize keyboard shortcuts
initKeyboardShortcuts([
    {
        key: 'n',
        ctrl: true,
        action: () => {
            const btn = document.getElementById('createRaceBtn');
            if (btn && btn.style.display !== 'none') {
                showCreateRaceModal();
            }
        }
    }
]);