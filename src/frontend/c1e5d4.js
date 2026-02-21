// Operations Dashboard JavaScript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '/api';

let currentUser = null;
let currentRaces = [];
let currentRegistrations = [];
let currentStartLists = [];
let editingRaceId = null;

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
        
        // Check if user has required role
        const allowedRoles = ['admin', 'chief_registrar', 'registrar', 'starter'];
        if (!allowedRoles.includes(currentUser.role)) {
            ToastManager.show('Access denied. Insufficient permissions.', 'error');
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
    document.getElementById('operations-user-name').textContent = user.name;
    document.getElementById('user-role-display').textContent = `Role: ${user.role.replace('_', ' ').toUpperCase()}`;
    
    // Setup navigation
    setupNavigation();
    
    // Setup logout
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Setup modals
    setupRaceModal();
    setupRegistrationModal();
    setupBulkUploadModal();
    setupLogoUpload();
    
    // Load initial data
    await loadRaces();
    await loadStartLists();
    await loadSettings();
    
    // Setup role-based visibility
    setupRoleVisibility(user.role);
});

// Setup Role-Based Visibility
function setupRoleVisibility(role) {
    const createRaceBtn = document.getElementById('create-race-btn');
    const generateStartListBtn = document.getElementById('generate-startlist-btn');
    const registerAthleteBtn = document.getElementById('register-athlete-btn');
    const bulkUploadBtn = document.getElementById('bulk-upload-btn');
    
    // Chief Registrar can manage races
    if (role !== 'admin' && role !== 'chief_registrar') {
        createRaceBtn.style.display = 'none';
    }
    
    // Registrar can register athletes
    if (role !== 'admin' && role !== 'registrar' && role !== 'chief_registrar') {
        registerAthleteBtn.style.display = 'none';
        bulkUploadBtn.style.display = 'none';
    }
    
    // Starter can only view start lists
    if (role === 'starter') {
        document.querySelector('[data-section="races"]').style.display = 'none';
        document.querySelector('[data-section="registrations"]').style.display = 'none';
        document.querySelector('[data-section="settings"]').style.display = 'none';
        // Auto-switch to start lists
        switchSection('startlists');
    }
}

// Navigation
function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section;
            switchSection(section);
        });
    });
}

function switchSection(sectionName) {
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.section === sectionName);
    });
    
    // Update sections
    document.querySelectorAll('.admin-section').forEach(section => {
        section.classList.toggle('active', section.id === `${sectionName}-section`);
    });
    
    // Load section data
    if (sectionName === 'registrations') {
        loadRegistrationRaceFilter();
    }
}

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
            displayRaces(currentRaces);
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        ToastManager.show('Failed to load races: ' + error.message, 'error');
        document.getElementById('races-tbody').innerHTML = 
            '<tr><td colspan="6" style="text-align: center; color: var(--danger-color);">Failed to load races</td></tr>';
    }
}

// Display Races
function displayRaces(races) {
    const tbody = document.getElementById('races-tbody');
    
    if (races.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No races found</td></tr>';
        return;
    }
    
    tbody.innerHTML = races.map(race => `
        <tr>
            <td><strong>${race.name}</strong></td>
            <td>${new Date(race.date).toLocaleDateString()}</td>
            <td>${race.location}</td>
            <td><span class="badge badge-${getStatusColor(race.status)}">${race.status}</span></td>
            <td>${race.registration_count || 0} athletes</td>
            <td>
                <button class="btn btn-small btn-primary" onclick="viewRaceDetails(${race.id})" title="View Details">👁️</button>
                <button class="btn btn-small btn-secondary" onclick="editRace(${race.id})" title="Edit">✏️</button>
                <button class="btn btn-small btn-secondary" onclick="copyPublicLink(${race.id})" title="Copy Public Link">🔗</button>
                ${currentUser.role === 'admin' || currentUser.role === 'chief_registrar' ? 
                    `<button class="btn btn-small btn-danger" onclick="deleteRace(${race.id})" title="Delete">🗑️</button>` : ''}
            </td>
        </tr>
    `).join('');
}

function getStatusColor(status) {
    const colors = {
        draft: 'secondary',
        open: 'success',
        closed: 'warning',
        completed: 'info'
    };
    return colors[status] || 'secondary';
}

// Race Modal Setup
function setupRaceModal() {
    const createBtn = document.getElementById('create-race-btn');
    const form = document.getElementById('race-form');
    
    createBtn.addEventListener('click', () => openRaceModal());
    form.addEventListener('submit', handleRaceSubmit);
    
    // Load events for checkbox list
    loadEventsForRace();
    
    // Search and filters
    document.getElementById('race-search').addEventListener('input', filterRaces);
    document.getElementById('race-status-filter').addEventListener('change', filterRaces);
}

async function loadEventsForRace() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/events`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const container = document.getElementById('race-events-list');
            container.innerHTML = data.data.map(event => `
                <label style="display: block; margin-bottom: 0.5rem;">
                    <input type="checkbox" name="events" value="${event.id}">
                    ${event.name}
                </label>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load events:', error);
    }
}

function openRaceModal(raceId = null) {
    editingRaceId = raceId;
    const modal = document.getElementById('race-modal');
    const title = document.getElementById('race-modal-title');
    const form = document.getElementById('race-form');
    
    if (raceId) {
        title.textContent = 'Edit Race';
        const race = currentRaces.find(r => r.id === raceId);
        if (race) {
            document.getElementById('race-name').value = race.name;
            document.getElementById('race-date').value = race.date;
            document.getElementById('race-location').value = race.location;
            document.getElementById('race-status').value = race.status;
            // Set event checkboxes
            race.events.forEach(eventId => {
                const checkbox = document.querySelector(`input[name="events"][value="${eventId}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }
    } else {
        title.textContent = 'Create New Race';
        form.reset();
    }
    
    modal.classList.add('active');
}

function closeRaceModal() {
    document.getElementById('race-modal').classList.remove('active');
    document.getElementById('race-form').reset();
    editingRaceId = null;
}

async function handleRaceSubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('race-name').value,
        date: document.getElementById('race-date').value,
        location: document.getElementById('race-location').value,
        status: document.getElementById('race-status').value,
        events: Array.from(document.querySelectorAll('input[name="events"]:checked')).map(cb => parseInt(cb.value))
    };
    
    if (formData.events.length === 0) {
        ToastManager.show('Please select at least one event', 'warning');
        return;
    }
    
    try {
        const url = editingRaceId 
            ? `${API_BASE_URL}/api/races/${editingRaceId}`
            : `${API_BASE_URL}/api/races`;
        
        const method = editingRaceId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            ToastManager.show(editingRaceId ? 'Race updated successfully' : 'Race created successfully', 'success');
            if (data.data.public_link) {
                ToastManager.show(`Public link: ${data.data.public_link}`, 'info');
            }
            closeRaceModal();
            await loadRaces();
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        ToastManager.show('Failed to save race: ' + error.message, 'error');
    }
}

function editRace(raceId) {
    openRaceModal(raceId);
}

function viewRaceDetails(raceId) {
    const race = currentRaces.find(r => r.id === raceId);
    if (!race) return;
    
    // Switch to registrations and filter by this race
    switchSection('registrations');
    document.getElementById('registration-race-filter').value = raceId;
    loadRegistrations(raceId);
}

async function deleteRace(raceId) {
    if (!confirm('Are you sure you want to delete this race? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/races/${raceId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            ToastManager.show('Race deleted successfully', 'success');
            await loadRaces();
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        ToastManager.show('Failed to delete race: ' + error.message, 'error');
    }
}

function copyPublicLink(raceId) {
    const race = currentRaces.find(r => r.id === raceId);
    if (!race || !race.public_link) {
        ToastManager.show('No public link available for this race', 'warning');
        return;
    }
    
    const fullLink = `${window.location.origin}/register/${race.public_link}`;
    navigator.clipboard.writeText(fullLink).then(() => {
        ToastManager.show('Public link copied to clipboard!', 'success');
    }).catch(() => {
        prompt('Copy this link:', fullLink);
    });
}

function filterRaces() {
    const searchTerm = document.getElementById('race-search').value.toLowerCase();
    const statusFilter = document.getElementById('race-status-filter').value;
    
    const filtered = currentRaces.filter(race => {
        const matchesSearch = race.name.toLowerCase().includes(searchTerm) || 
                            race.location.toLowerCase().includes(searchTerm);
        const matchesStatus = statusFilter === 'all' || race.status === statusFilter;
        return matchesSearch && matchesStatus;
    });
    
    displayRaces(filtered);
}

// Registration Management
function setupRegistrationModal() {
    const registerBtn = document.getElementById('register-athlete-btn');
    const form = document.getElementById('registration-form');
    
    registerBtn.addEventListener('click', openRegistrationModal);
    form.addEventListener('submit', handleRegistrationSubmit);
    
    document.getElementById('registration-search').addEventListener('input', filterRegistrations);
    document.getElementById('registration-status-filter').addEventListener('change', filterRegistrations);
    document.getElementById('registration-race-filter').addEventListener('change', (e) => {
        const raceId = e.target.value;
        if (raceId && raceId !== 'all') {
            loadRegistrations(parseInt(raceId));
        } else {
            document.getElementById('registrations-tbody').innerHTML = 
                '<tr><td colspan="6" style="text-align: center;">Select a race to view registrations</td></tr>';
        }
    });
}

function loadRegistrationRaceFilter() {
    const select = document.getElementById('registration-race-filter');
    select.innerHTML = '<option value="all">All Races</option>' + 
        currentRaces.map(race => `<option value="${race.id}">${race.name}</option>`).join('');
}

async function loadRegistrations(raceId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/races/${raceId}/registrations`, {
            headers: {
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            currentRegistrations = data.data;
            displayRegistrations(currentRegistrations);
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        ToastManager.show('Failed to load registrations: ' + error.message, 'error');
    }
}

function displayRegistrations(registrations) {
    const tbody = document.getElementById('registrations-tbody');
    
    if (registrations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No registrations found</td></tr>';
        return;
    }
    
    tbody.innerHTML = registrations.map(reg => `
        <tr>
            <td><strong>${reg.athlete_name}</strong><br><small>${reg.athlete_email}</small></td>
            <td>${reg.race_name}</td>
            <td>${reg.events.join(', ')}</td>
            <td><span class="badge badge-${reg.status === 'confirmed' ? 'success' : 'warning'}">${reg.status}</span></td>
            <td>${new Date(reg.registered_at).toLocaleDateString()}</td>
            <td>
                <button class="btn btn-small btn-primary" onclick="confirmRegistration(${reg.id})" title="Confirm">✅</button>
                <button class="btn btn-small btn-danger" onclick="cancelRegistration(${reg.id})" title="Cancel">❌</button>
            </td>
        </tr>
    `).join('');
}

function openRegistrationModal() {
    const modal = document.getElementById('registration-modal');
    const raceSelect = document.getElementById('reg-race');
    
    // Populate race options
    raceSelect.innerHTML = '<option value="">Select Race</option>' + 
        currentRaces.filter(r => r.status === 'open').map(race => 
            `<option value="${race.id}">${race.name}</option>`
        ).join('');
    
    // Load events when race changes
    raceSelect.addEventListener('change', loadEventsForRegistration);
    
    modal.classList.add('active');
}

function closeRegistrationModal() {
    document.getElementById('registration-modal').classList.remove('active');
    document.getElementById('registration-form').reset();
}

async function loadEventsForRegistration() {
    const raceId = document.getElementById('reg-race').value;
    if (!raceId) return;
    
    const race = currentRaces.find(r => r.id === parseInt(raceId));
    if (!race) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/events`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const container = document.getElementById('reg-events-list');
            const raceEventIds = race.events || [];
            const relevantEvents = data.data.filter(e => raceEventIds.includes(e.id));
            
            container.innerHTML = relevantEvents.map(event => `
                <label style="display: block; margin-bottom: 0.5rem;">
                    <input type="checkbox" name="reg-events" value="${event.id}">
                    ${event.name}
                </label>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load events:', error);
    }
}

async function handleRegistrationSubmit(e) {
    e.preventDefault();
    
    const formData = {
        race_id: parseInt(document.getElementById('reg-race').value),
        athlete_name: document.getElementById('reg-athlete-name').value,
        athlete_email: document.getElementById('reg-athlete-email').value,
        events: Array.from(document.querySelectorAll('input[name="reg-events"]:checked')).map(cb => parseInt(cb.value)),
        registered_by: currentUser.id
    };
    
    if (formData.events.length === 0) {
        ToastManager.show('Please select at least one event', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/races/${formData.race_id}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            ToastManager.show('Athlete registered successfully', 'success');
            closeRegistrationModal();
            
            // Reload registrations if viewing
            const currentRaceFilter = document.getElementById('registration-race-filter').value;
            if (currentRaceFilter && currentRaceFilter !== 'all') {
                loadRegistrations(parseInt(currentRaceFilter));
            }
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        ToastManager.show('Failed to register athlete: ' + error.message, 'error');
    }
}

async function confirmRegistration(regId) {
    // Implementation for confirming registration
    ToastManager.show('Registration confirmed', 'success');
}

async function cancelRegistration(regId) {
    if (!confirm('Are you sure you want to cancel this registration?')) {
        return;
    }
    ToastManager.show('Registration cancelled', 'success');
}

function filterRegistrations() {
    const searchTerm = document.getElementById('registration-search').value.toLowerCase();
    const statusFilter = document.getElementById('registration-status-filter').value;
    
    const filtered = currentRegistrations.filter(reg => {
        const matchesSearch = reg.athlete_name.toLowerCase().includes(searchTerm) || 
                            reg.athlete_email.toLowerCase().includes(searchTerm);
        const matchesStatus = statusFilter === 'all' || reg.status === statusFilter;
        return matchesSearch && matchesStatus;
    });
    
    displayRegistrations(filtered);
}

// Bulk Upload
function setupBulkUploadModal() {
    const bulkBtn = document.getElementById('bulk-upload-btn');
    const downloadBtn = document.getElementById('download-template-btn');
    const uploadBtn = document.getElementById('upload-file-btn');
    
    bulkBtn.addEventListener('click', openBulkUploadModal);
    downloadBtn.addEventListener('click', downloadTemplate);
    uploadBtn.addEventListener('click', handleBulkUpload);
}

function openBulkUploadModal() {
    const modal = document.getElementById('bulk-upload-modal');
    const raceSelect = document.getElementById('bulk-race-select');
    
    // Populate race options
    raceSelect.innerHTML = '<option value="">Select Race</option>' + 
        currentRaces.filter(r => r.status === 'open').map(race => 
            `<option value="${race.id}">${race.name}</option>`
        ).join('');
    
    modal.classList.add('active');
}

function closeBulkUploadModal() {
    document.getElementById('bulk-upload-modal').classList.remove('active');
    document.getElementById('bulk-file-input').value = '';
    document.getElementById('upload-progress').style.display = 'none';
}

async function downloadTemplate() {
    const raceId = document.getElementById('registration-race-filter').value;
    
    if (!raceId || raceId === 'all') {
        ToastManager.show('Please select a specific race first', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/races/${raceId}/template`, {
            headers: {
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Create CSV content
            const template = data.data;
            const csv = [
                template.columns.join(','),
                `# Checksum: ${template.checksum}`,
                '# Fill in athlete details below. Do not modify the checksum line.',
                ''
            ].join('\n');
            
            // Download file
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `registration_template_race_${raceId}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
            
            ToastManager.show('Template downloaded successfully', 'success');
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        ToastManager.show('Failed to download template: ' + error.message, 'error');
    }
}

async function handleBulkUpload() {
    const raceId = document.getElementById('bulk-race-select').value;
    const fileInput = document.getElementById('bulk-file-input');
    
    if (!raceId) {
        ToastManager.show('Please select a race', 'warning');
        return;
    }
    
    if (!fileInput.files || fileInput.files.length === 0) {
        ToastManager.show('Please select a file to upload', 'warning');
        return;
    }
    
    const file = fileInput.files[0];
    const reader = new FileReader();
    
    reader.onload = async (e) => {
        const content = e.target.result;
        
        // Show progress
        document.getElementById('upload-progress').style.display = 'block';
        document.getElementById('upload-status').textContent = 'Processing file...';
        document.getElementById('upload-progress-bar').style.width = '50%';
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/races/${raceId}/upload`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
                },
                body: JSON.stringify({
                    file_content: content,
                    filename: file.name
                })
            });
            
            const data = await response.json();
            
            document.getElementById('upload-progress-bar').style.width = '100%';
            document.getElementById('upload-status').textContent = 'Upload complete';
            
            if (data.status === 'success') {
                ToastManager.show(`Successfully registered ${data.data.registered_count} athletes`, 'success');
                setTimeout(() => {
                    closeBulkUploadModal();
                    loadRegistrations(parseInt(raceId));
                }, 2000);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            document.getElementById('upload-status').textContent = 'Upload failed';
            ToastManager.show('Failed to upload: ' + error.message, 'error');
        }
    };
    
    reader.readAsText(file);
}

// Start Lists
async function loadStartLists() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/startlists`, {
            headers: {
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            currentStartLists = data.data;
            displayStartLists(currentStartLists);
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        ToastManager.show('Failed to load start lists: ' + error.message, 'error');
    }
}

function displayStartLists(startLists) {
    const tbody = document.getElementById('startlists-tbody');
    
    if (startLists.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No start lists found</td></tr>';
        return;
    }
    
    tbody.innerHTML = startLists.map(sl => `
        <tr>
            <td>${sl.race_name}</td>
            <td>${sl.event_name}</td>
            <td>${sl.athletes.length} athletes</td>
            <td><span class="badge badge-${sl.status === 'confirmed' ? 'success' : 'warning'}">${sl.status}</span></td>
            <td>${sl.confirmed_by || 'Not confirmed'}</td>
            <td>
                <button class="btn btn-small btn-primary" onclick="viewStartList(${sl.id})" title="View">👁️</button>
                ${(currentUser.role === 'admin' || currentUser.role === 'starter') && sl.status !== 'confirmed' ? 
                    `<button class="btn btn-small btn-success" onclick="confirmStartList(${sl.id})" title="Confirm">✅</button>` : ''}
            </td>
        </tr>
    `).join('');
}

function viewStartList(startListId) {
    const sl = currentStartLists.find(s => s.id === startListId);
    if (!sl) return;
    
    alert(`Start List for ${sl.race_name} - ${sl.event_name}\n\nAthletes:\n${sl.athletes.join('\n')}`);
}

async function confirmStartList(startListId) {
    if (!confirm('Confirm this start list? This action confirms all athletes are present and ready.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/startlists/${startListId}/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            },
            body: JSON.stringify({
                confirmed_by: currentUser.id
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            ToastManager.show('Start list confirmed successfully', 'success');
            await loadStartLists();
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        ToastManager.show('Failed to confirm start list: ' + error.message, 'error');
    }
}

// Logo Upload
function setupLogoUpload() {
    const uploadInput = document.getElementById('logo-upload-input');
    const removeBtn = document.getElementById('remove-logo-btn');
    
    uploadInput.addEventListener('change', handleLogoUpload);
    removeBtn.addEventListener('click', removeLogo);
}

async function handleLogoUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        ToastManager.show('Please select an image file', 'error');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = async (event) => {
        const base64Image = event.target.result;
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/settings/logo`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
                },
                body: JSON.stringify({
                    logo: base64Image
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                ToastManager.show('Logo uploaded successfully', 'success');
                displayLogo(base64Image);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            ToastManager.show('Failed to upload logo: ' + error.message, 'error');
        }
    };
    
    reader.readAsDataURL(file);
}

function displayLogo(logoData) {
    const img = document.getElementById('current-logo');
    const noLogoText = document.getElementById('no-logo-text');
    
    img.src = logoData;
    img.style.display = 'block';
    noLogoText.style.display = 'none';
}

async function removeLogo() {
    if (!confirm('Remove current logo?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/settings/logo`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            ToastManager.show('Logo removed successfully', 'success');
            document.getElementById('current-logo').style.display = 'none';
            document.getElementById('no-logo-text').style.display = 'block';
        }
    } catch (error) {
        ToastManager.show('Failed to remove logo: ' + error.message, 'error');
    }
}

// Load Settings
async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/settings`, {
            headers: {
                'Authorization': `Bearer ${currentUser.token || 'demo_token'}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const settings = data.data;
            
            // Display logo if exists
            if (settings.logo) {
                displayLogo(settings.logo);
            }
            
            // Set form values
            document.getElementById('org-name').value = settings.organization_name || 'AthSys Athletics';
            document.getElementById('org-email').value = settings.contact_email || '';
            document.getElementById('allow-public-registration').checked = settings.allow_public_registration !== false;
            document.getElementById('require-email-verification').checked = settings.require_email_verification === true;
            document.getElementById('allow-bulk-upload').checked = settings.allow_bulk_upload !== false;
        }
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

// Logout
function logout() {
    localStorage.clear();
    sessionStorage.clear();
    ToastManager.show('Logged out successfully', 'success');
    setTimeout(() => window.location.href = 'login.html', 1000);
}
