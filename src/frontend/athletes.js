// Athletes Management JavaScript
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
let allAthletes = [];

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
        clearMode: 'all'
    });
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

async function loadAthletes() {
    const user = checkAuth();
    if (!user) return;
    
    document.getElementById('userName').textContent = user.name || user.email;
    
    // Show loading skeleton
    showLoadingSkeleton('athletesContainer', 6, 'card');
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/api/athletes`);
        if (!response) return;
        
        const athletes = await response.json();
        allAthletes = Array.isArray(athletes) ? athletes : [];
        displayAthletes(allAthletes);
        
        // Check permissions for adding athletes
        const canAdd = ['admin', 'chief_registrar', 'registrar'].includes(user.role);
        document.getElementById('addAthleteBtn').style.display = canAdd ? 'inline-block' : 'none';
        
    } catch (error) {
        console.error('Error loading athletes:', error);
        toast.show('Error loading athletes', 'error');
        document.getElementById('athletesContainer').innerHTML = '<div class="error">Failed to load athletes</div>';
    }
}

function displayAthletes(athletes) {
    const container = document.getElementById('athletesContainer');
    
    if (!athletes || athletes.length === 0) {
        showEmptyState('athletesContainer', {
            icon: '🏃',
            title: 'No athletes found',
            message: 'Start building your athlete database or adjust your search filters',
            actionText: '➕ Add First Athlete',
            actionCallback: canEdit() ? 'showAddAthleteModal()' : null,
            showAction: canEdit()
        });
        return;
    }
    
    container.innerHTML = athletes.map(athlete => {
        const age = calculateAge(athlete.date_of_birth);
        const genderColor = athlete.gender === 'Male' ? '#4a90e2' : '#ff6b9d';
        
        return `
            <div class="athlete-card" style="background: var(--background-dark); border-radius: 12px; padding: 1.5rem; border-left: 4px solid ${genderColor};">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div>
                        <h3 style="margin: 0; color: var(--text-color);">${athlete.name}</h3>
                        <p style="color: var(--text-secondary); margin: 0.25rem 0; font-size: 0.9rem;">
                            ${athlete.gender} • ${age} years old
                        </p>
                    </div>
                    <span class="gender-badge" style="background: ${genderColor}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem;">
                        ${athlete.gender === 'Male' ? '👨' : '👩'} ${athlete.gender}
                    </span>
                </div>
                
                ${athlete.team ? `<p style="color: var(--text-secondary); margin: 0.5rem 0;">🏢 ${athlete.team}</p>` : ''}
                ${athlete.coach ? `<p style="color: var(--text-secondary); margin: 0.5rem 0;">👨‍🏫 Coach: ${athlete.coach}</p>` : ''}
                ${athlete.email ? `<p style="color: var(--text-secondary); margin: 0.5rem 0;">📧 ${athlete.email}</p>` : ''}
                
                <div style="display: flex; gap: 0.5rem; margin-top: 1rem; flex-wrap: wrap;">
                    <button class="btn btn-small btn-primary" onclick="viewAthleteDetails(${athlete.id})">👁️ View Profile</button>
                    ${canEdit() ? `<button class="btn btn-small" onclick="editAthlete(${athlete.id})">✏️ Edit</button>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function calculateAge(dobString) {
    const dob = new Date(dobString);
    const today = new Date();
    let age = today.getFullYear() - dob.getFullYear();
    const monthDiff = today.getMonth() - dob.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
        age--;
    }
    return age;
}

function canEdit() {
    const userStr = localStorage.getItem('user') || sessionStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    return user && ['admin', 'chief_registrar', 'registrar'].includes(user.role);
}

function filterAthletes() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const genderFilter = document.getElementById('genderFilter').value;
    
    const filtered = allAthletes.filter(athlete => {
        const matchesSearch = athlete.name.toLowerCase().includes(searchTerm) ||
                            (athlete.team && athlete.team.toLowerCase().includes(searchTerm)) ||
                            (athlete.email && athlete.email.toLowerCase().includes(searchTerm));
        const matchesGender = !genderFilter || athlete.gender === genderFilter;
        return matchesSearch && matchesGender;
    });
    
    displayAthletes(filtered);
}

function refreshAthletes() {
    toast.show('Refreshing athletes...', 'info');
    loadAthletes();
}

function showAddAthleteModal() {
    document.getElementById('modalTitle').textContent = 'Add New Athlete';
    document.getElementById('athleteForm').reset();
    document.getElementById('athleteId').value = '';
    document.getElementById('athleteModal').style.display = 'flex';
}

function closeAthleteModal() {
    document.getElementById('athleteModal').style.display = 'none';
}

async function editAthlete(athleteId) {
    const athlete = allAthletes.find(a => a.id === athleteId);
    if (!athlete) return;
    
    document.getElementById('modalTitle').textContent = 'Edit Athlete';
    document.getElementById('athleteId').value = athlete.id;
    document.getElementById('athleteName').value = athlete.name;
    document.getElementById('athleteDob').value = athlete.date_of_birth.split('T')[0];
    document.getElementById('athleteGender').value = athlete.gender;
    document.getElementById('athleteEmail').value = athlete.email || '';
    document.getElementById('athletePhone').value = athlete.phone || '';
    document.getElementById('athleteTeam').value = athlete.team || '';
    document.getElementById('athleteCoach').value = athlete.coach || '';
    document.getElementById('athleteModal').style.display = 'flex';
}

async function viewAthleteDetails(athleteId) {
    const athlete = allAthletes.find(a => a.id === athleteId);
    if (!athlete) return;
    
    const age = calculateAge(athlete.date_of_birth);
    const genderColor = athlete.gender === 'Male' ? '#4a90e2' : '#ff6b9d';
    
    const content = `
        <div style="padding: 1rem;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="width: 100px; height: 100px; border-radius: 50%; background: ${genderColor}; display: inline-flex; align-items: center; justify-content: center; font-size: 3rem; margin-bottom: 1rem;">
                    ${athlete.gender === 'Male' ? '👨' : '👩'}
                </div>
                <h3 style="margin: 0;">${athlete.name}</h3>
                <p style="color: var(--text-secondary);">${athlete.gender} • ${age} years old</p>
            </div>
            
            <div style="display: grid; gap: 1rem;">
                <div style="padding: 1rem; background: var(--background-light); border-radius: 8px;">
                    <strong>📅 Date of Birth:</strong> ${new Date(athlete.date_of_birth).toLocaleDateString()}
                </div>
                ${athlete.email ? `
                    <div style="padding: 1rem; background: var(--background-light); border-radius: 8px;">
                        <strong>📧 Email:</strong> ${athlete.email}
                    </div>
                ` : ''}
                ${athlete.phone ? `
                    <div style="padding: 1rem; background: var(--background-light); border-radius: 8px;">
                        <strong>📱 Phone:</strong> ${athlete.phone}
                    </div>
                ` : ''}
                ${athlete.team ? `
                    <div style="padding: 1rem; background: var(--background-light); border-radius: 8px;">
                        <strong>🏢 Team/Club:</strong> ${athlete.team}
                    </div>
                ` : ''}
                ${athlete.coach ? `
                    <div style="padding: 1rem; background: var(--background-light); border-radius: 8px;">
                        <strong>👨‍🏫 Coach:</strong> ${athlete.coach}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
    
    document.getElementById('athleteDetailsContent').innerHTML = content;
    document.getElementById('athleteDetailsModal').style.display = 'flex';
}

function closeDetailsModal() {
    document.getElementById('athleteDetailsModal').style.display = 'none';
}

// Form submission
document.addEventListener('DOMContentLoaded', () => {
    loadAthletes();
    
    document.getElementById('athleteForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const athleteId = document.getElementById('athleteId').value;
        const athleteData = {
            name: document.getElementById('athleteName').value,
            date_of_birth: document.getElementById('athleteDob').value,
            gender: document.getElementById('athleteGender').value,
            email: document.getElementById('athleteEmail').value || null,
            phone: document.getElementById('athletePhone').value || null,
            team: document.getElementById('athleteTeam').value || null,
            coach: document.getElementById('athleteCoach').value || null
        };
        
        try {
            const url = athleteId 
                ? `${API_BASE_URL}/api/athletes/${athleteId}`
                : `${API_BASE_URL}/api/athletes`;
            
            const method = athleteId ? 'PUT' : 'POST';
            
            const response = await fetchWithAuth(url, {
                method: method,
                body: JSON.stringify(athleteData)
            });
            
            if (!response) return;
            
            const result = await response.json();
            
            if (response.ok) {
                toast.show(athleteId ? 'Athlete updated successfully!' : 'Athlete added successfully!', 'success');
                closeAthleteModal();
                loadAthletes();
            } else {
                toast.show(result.message || 'Error saving athlete', 'error');
            }
        } catch (error) {
            console.error('Error saving athlete:', error);
            toast.show('Error saving athlete', 'error');
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
const debouncedFilterAthletes = debounceSearch(filterAthletes);

// Export to CSV function
function exportAthletes() {
    if (!allAthletes || allAthletes.length === 0) {
        toast.show('No athletes to export', 'warning');
        return;
    }
    
    const exportData = allAthletes.map(athlete => ({
        'Full Name': athlete.full_name,
        'Date of Birth': formatDate(athlete.date_of_birth),
        'Age': calculateAge(athlete.date_of_birth),
        'Gender': athlete.gender,
        'Email': athlete.email || '',
        'Phone': athlete.phone || '',
        'Team/Club': athlete.team_club || '',
        'Coach': athlete.coach || ''
    }));
    
    exportToCSV(exportData, 'athsys_athletes');
    toast.show('Athletes exported successfully!', 'success');
}

// Initialize keyboard shortcuts
initKeyboardShortcuts([
    {
        key: 'n',
        ctrl: true,
        action: () => {
            const btn = document.getElementById('addAthleteBtn');
            if (btn && btn.style.display !== 'none') {
                showAddAthleteModal();
            }
        }
    }
]);
