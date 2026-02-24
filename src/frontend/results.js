// Results Management JavaScript
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
let allResults = [];
let allRaces = [];
let allAthletes = [];
let currentUser = null;

const WORKFLOW_TRANSITION_MAP = {
    captured: ['reviewed'],
    reviewed: ['captured', 'ratified'],
    ratified: ['reviewed', 'published'],
    published: ['ratified']
};

const WORKFLOW_BADGE_COLORS = {
    captured: '#6b7280',
    reviewed: '#2563eb',
    ratified: '#059669',
    published: '#7c3aed'
};

function normalizeApiList(payload, preferredKey = null) {
    if (Array.isArray(payload)) return payload;
    if (!payload || typeof payload !== 'object') return [];
    if (preferredKey && Array.isArray(payload[preferredKey])) return payload[preferredKey];

    const candidates = ['results', 'races', 'athletes', 'data', 'items'];
    for (const key of candidates) {
        if (Array.isArray(payload[key])) {
            return payload[key];
        }
    }
    return [];
}

function normalizeWorkflowStatus(value) {
    const valid = ['captured', 'reviewed', 'ratified', 'published'];
    const normalized = (value || '').toString().trim().toLowerCase();
    return valid.includes(normalized) ? normalized : 'captured';
}

function getWorkflowStateLabel(state) {
    const normalized = normalizeWorkflowStatus(state);
    return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

function canTransitionWorkflows() {
    return !!currentUser && ['admin', 'chief_registrar', 'registrar', 'official'].includes(currentUser.role);
}

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

async function loadResults() {
    const user = checkAuth();
    if (!user) return;
    currentUser = user;
    
    document.getElementById('userName').textContent = user.name || user.email;
    
    // Show loading skeleton
    showLoadingSkeleton('resultsContainer', 5, 'table');
    
    try {
        // Load all data
        const [resultsResp, racesResp, athletesResp] = await Promise.all([
            fetchWithAuth(`${API_BASE_URL}/api/results`),
            fetchWithAuth(`${API_BASE_URL}/api/races`),
            fetchWithAuth(`${API_BASE_URL}/api/athletes`)
        ]);
        
        if (resultsResp) {
            const resultPayload = await resultsResp.json();
            allResults = normalizeApiList(resultPayload, 'results').map(result => ({
                ...result,
                workflowStatus: normalizeWorkflowStatus(result.workflowStatus),
                athlete_name: result.athlete_name || result.athleteName,
                event_name: result.event_name || result.eventName,
                race_id: result.race_id || result.raceId,
                race_name: result.race_name || result.raceName,
                time: result.time || result.timeSeconds,
                notes: result.notes || ''
            }));
        }
        if (racesResp) {
            const racesPayload = await racesResp.json();
            allRaces = normalizeApiList(racesPayload, 'races');
            populateRaceFilter();
            populateRaceDropdown();
        }
        if (athletesResp) {
            const athletesPayload = await athletesResp.json();
            allAthletes = normalizeApiList(athletesPayload, 'athletes');
        }
        
        displayResults(allResults);
        
        // Check permissions
        const canAdd = ['admin', 'chief_registrar', 'starter'].includes(user.role);
        document.getElementById('addResultBtn').style.display = canAdd ? 'inline-block' : 'none';
        
    } catch (error) {
        console.error('Error loading data:', error);
        toast.show('Error loading results', 'error');
        document.getElementById('resultsContainer').innerHTML = '<div class="error" style="padding: 2rem; text-align: center;">Failed to load results</div>';
    }
}

function populateRaceFilter() {
    const select = document.getElementById('raceFilter');
    select.innerHTML = '<option value="">All Races</option>' + 
        allRaces.map(race => `<option value="${race.id}">${race.name}</option>`).join('');
}

function populateRaceDropdown() {
    const select = document.getElementById('resultRace');
    select.innerHTML = '<option value="">Choose a race...</option>' + 
        allRaces.map(race => `<option value="${race.id}">${race.name}</option>`).join('');
}

function resolveRaceName(result) {
    const raceId = result.race_id || result.raceId;
    if (!raceId || !Array.isArray(allRaces)) return null;
    const race = allRaces.find(item => Number(item.id) === Number(raceId));
    return race ? race.name : null;
}

function displayResults(results) {
    const container = document.getElementById('resultsContainer');
    
    if (!results || results.length === 0) {
        container.innerHTML = '<div class="empty-state" style="padding: 2rem; text-align: center;">No results found.</div>';
        return;
    }
    
    // Group results by race
    const groupedByRace = {};
    results.forEach(result => {
        const raceName = result.race_name || result.raceName || resolveRaceName(result) || 'Unknown Race';
        if (!groupedByRace[raceName]) {
            groupedByRace[raceName] = [];
        }
        groupedByRace[raceName].push(result);
    });
    
    let html = '';
    for (const [raceName, raceResults] of Object.entries(groupedByRace)) {
        html += `
            <div style="padding: 1.5rem; border-bottom: 1px solid var(--border-color);">
                <h3 style="margin: 0 0 1rem 0; color: var(--primary-color);">🏁 ${raceName}</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: var(--background-light); text-align: left;">
                                <th style="padding: 0.75rem; border-bottom: 2px solid var(--border-color);">Position</th>
                                <th style="padding: 0.75rem; border-bottom: 2px solid var(--border-color);">Athlete</th>
                                <th style="padding: 0.75rem; border-bottom: 2px solid var(--border-color);">Event</th>
                                <th style="padding: 0.75rem; border-bottom: 2px solid var(--border-color);">Time</th>
                                <th style="padding: 0.75rem; border-bottom: 2px solid var(--border-color);">Workflow</th>
                                <th style="padding: 0.75rem; border-bottom: 2px solid var(--border-color);">Notes</th>
                                <th style="padding: 0.75rem; border-bottom: 2px solid var(--border-color);">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${raceResults.sort((a, b) => a.position - b.position).map(result => {
                                const medal = result.position === 1 ? '🥇' : result.position === 2 ? '🥈' : result.position === 3 ? '🥉' : '';
                                const workflowState = normalizeWorkflowStatus(result.workflowStatus);
                                const workflowBadgeColor = WORKFLOW_BADGE_COLORS[workflowState] || WORKFLOW_BADGE_COLORS.captured;
                                const transitionOptions = WORKFLOW_TRANSITION_MAP[workflowState] || [];
                                const workflowActionHtml = canTransitionWorkflows()
                                    ? `
                                        <button class="btn btn-secondary" style="margin-right: 0.4rem; padding: 0.35rem 0.6rem;" onclick="openWorkflowHistory(${result.id})">History</button>
                                        <select data-result-id="${result.id}" class="workflow-select" style="padding: 0.35rem; border-radius: 6px; border: 1px solid var(--border-color); min-width: 130px;" onchange="transitionWorkflowFromSelect(this)">
                                            <option value="">Move to...</option>
                                            ${transitionOptions.map(state => `<option value="${state}">${getWorkflowStateLabel(state)}</option>`).join('')}
                                        </select>
                                    `
                                    : `<button class="btn btn-secondary" style="padding: 0.35rem 0.6rem;" onclick="openWorkflowHistory(${result.id})">History</button>`;

                                return `
                                    <tr style="border-bottom: 1px solid var(--border-color);">
                                        <td style="padding: 0.75rem; font-weight: bold;">${medal} ${result.position}</td>
                                        <td style="padding: 0.75rem;">${result.athlete_name || 'Unknown'}</td>
                                        <td style="padding: 0.75rem;">${result.event_name || 'N/A'}</td>
                                        <td style="padding: 0.75rem; font-family: monospace;">${result.time || 'N/A'}</td>
                                        <td style="padding: 0.75rem;">
                                            <span style="display:inline-block; padding:0.2rem 0.55rem; border-radius:999px; color:#fff; background:${workflowBadgeColor}; font-size:0.8rem; font-weight:600;">
                                                ${getWorkflowStateLabel(workflowState)}
                                            </span>
                                        </td>
                                        <td style="padding: 0.75rem; color: var(--text-secondary); font-size: 0.9rem;">${result.notes || '-'}</td>
                                        <td style="padding: 0.75rem;">${workflowActionHtml}</td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function ensureWorkflowHistoryModal() {
    let modal = document.getElementById('workflowHistoryModal');
    if (modal) return modal;

    modal = document.createElement('div');
    modal.id = 'workflowHistoryModal';
    modal.className = 'modal hidden-element';
    modal.innerHTML = `
        <div class="modal-content modal-medium" style="max-width: 720px;">
            <div class="modal-header">
                <h2 id="workflowHistoryTitle">Workflow History</h2>
                <button class="btn-close" onclick="closeWorkflowHistoryModal()">×</button>
            </div>
            <div class="modal-body" id="workflowHistoryBody" style="max-height: 60vh; overflow-y: auto;">
                <div class="loading">Loading workflow history...</div>
            </div>
            <div class="modal-actions" style="padding: 0 1rem 1rem;">
                <button type="button" class="btn btn-secondary" onclick="closeWorkflowHistoryModal()">Close</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    return modal;
}

function closeWorkflowHistoryModal() {
    const modal = document.getElementById('workflowHistoryModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function openWorkflowHistory(resultId) {
    if (!resultId) return;

    const modal = ensureWorkflowHistoryModal();
    const title = document.getElementById('workflowHistoryTitle');
    const body = document.getElementById('workflowHistoryBody');
    title.textContent = `Workflow History · Result #${resultId}`;
    body.innerHTML = '<div class="loading">Loading workflow history...</div>';
    modal.style.display = 'flex';

    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/api/results/${resultId}/workflow-history`);
        if (!response) return;

        const payload = await response.json();
        if (!response.ok) {
            body.innerHTML = `<div class="error" style="padding: 1rem;">${payload.message || payload.error || 'Failed to load history'}</div>`;
            return;
        }

        const history = Array.isArray(payload.history) ? payload.history : [];
        const currentState = getWorkflowStateLabel(payload.currentState || 'captured');

        if (!history.length) {
            body.innerHTML = `
                <div style="padding: 1rem; color: var(--text-secondary);">
                    <p style="margin: 0 0 0.5rem 0;"><strong>Current State:</strong> ${currentState}</p>
                    <p style="margin: 0;">No transition history yet. The result is currently in its initial state.</p>
                </div>
            `;
            return;
        }

        body.innerHTML = `
            <div style="padding: 0.5rem 0.25rem 0.25rem; color: var(--text-secondary); font-size: 0.9rem;">
                Current State: <strong>${currentState}</strong>
            </div>
            <table style="width: 100%; border-collapse: collapse; margin-top: 0.5rem;">
                <thead>
                    <tr style="background: var(--background-light); text-align: left;">
                        <th style="padding: 0.65rem; border-bottom: 1px solid var(--border-color);">From</th>
                        <th style="padding: 0.65rem; border-bottom: 1px solid var(--border-color);">To</th>
                        <th style="padding: 0.65rem; border-bottom: 1px solid var(--border-color);">Reason</th>
                        <th style="padding: 0.65rem; border-bottom: 1px solid var(--border-color);">Changed At</th>
                    </tr>
                </thead>
                <tbody>
                    ${history.map(item => {
                        const fromState = getWorkflowStateLabel(item.fromState || 'captured');
                        const toState = getWorkflowStateLabel(item.toState || 'captured');
                        const changedAt = item.changedAt ? new Date(item.changedAt).toLocaleString() : 'N/A';
                        return `
                            <tr style="border-bottom: 1px solid var(--border-color);">
                                <td style="padding: 0.65rem;">${fromState}</td>
                                <td style="padding: 0.65rem; font-weight: 600;">${toState}</td>
                                <td style="padding: 0.65rem; color: var(--text-secondary);">${item.reason || '-'}</td>
                                <td style="padding: 0.65rem;">${changedAt}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Workflow history error:', error);
        body.innerHTML = '<div class="error" style="padding: 1rem;">Failed to load workflow history.</div>';
    }
}

async function transitionWorkflowFromSelect(selectEl) {
    const resultId = Number(selectEl.getAttribute('data-result-id'));
    const toState = (selectEl.value || '').trim().toLowerCase();

    if (!resultId || !toState) return;

    const reasonInput = window.prompt(
        `Provide reason for moving result #${resultId} to ${getWorkflowStateLabel(toState)}:`,
        ''
    );

    if (reasonInput === null) {
        selectEl.value = '';
        return;
    }

    const reason = reasonInput.trim();
    if (!reason) {
        toast.show('Transition reason is required.', 'warning');
        selectEl.value = '';
        return;
    }

    const previousValue = '';
    selectEl.disabled = true;

    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/api/results/${resultId}/workflow-transition`, {
            method: 'POST',
            body: JSON.stringify({ toState, reason })
        });

        if (!response) return;

        const payload = await response.json();
        if (!response.ok) {
            toast.show(payload.message || payload.error || 'Workflow transition failed', 'error');
            selectEl.value = previousValue;
            return;
        }

        const localIndex = allResults.findIndex(item => Number(item.id) === resultId);
        if (localIndex >= 0) {
            allResults[localIndex].workflowStatus = toState;
        }

        filterResults();
        toast.show(`Workflow moved to ${getWorkflowStateLabel(toState)}`, 'success');
    } catch (error) {
        console.error('Workflow transition error:', error);
        toast.show('Error updating workflow state', 'error');
        selectEl.value = previousValue;
    } finally {
        selectEl.disabled = false;
        selectEl.value = '';
    }
}

function filterResults() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const raceId = document.getElementById('raceFilter').value;
    
    const filtered = allResults.filter(result => {
        const matchesSearch = !searchTerm || 
            (result.athlete_name && result.athlete_name.toLowerCase().includes(searchTerm)) ||
            (result.event_name && result.event_name.toLowerCase().includes(searchTerm));
        const matchesRace = !raceId || result.race_id == raceId;
        return matchesSearch && matchesRace;
    });
    
    displayResults(filtered);
}

function refreshResults() {
    toast.show('Refreshing results...', 'info');
    loadResults();
}

function showAddResultModal() {
    document.getElementById('resultForm').reset();
    document.getElementById('resultModal').style.display = 'flex';
}

function closeResultModal() {
    document.getElementById('resultModal').style.display = 'none';
}

async function loadRaceEvents() {
    const raceId = document.getElementById('resultRace').value;
    const eventSelect = document.getElementById('resultEvent');
    
    eventSelect.innerHTML = '<option value="">Choose an event...</option>';
    document.getElementById('resultAthlete').innerHTML = '<option value="">Choose an athlete...</option>';
    
    if (!raceId) return;
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/api/races/${raceId}`);
        if (!response) return;
        
        const race = await response.json();
        if (race.events && race.events.length > 0) {
            eventSelect.innerHTML = '<option value="">Choose an event...</option>' +
                race.events.map(event => `<option value="${event.id}">${event.name} (${event.gender})</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading events:', error);
        toast.show('Error loading events', 'error');
    }
}

async function loadEventAthletes() {
    const eventId = document.getElementById('resultEvent').value;
    const athleteSelect = document.getElementById('resultAthlete');
    
    athleteSelect.innerHTML = '<option value="">Choose an athlete...</option>';
    
    if (!eventId) return;
    
    try {
        // For now, show all athletes. In production, you'd filter by registration
        athleteSelect.innerHTML = '<option value="">Choose an athlete...</option>' +
            allAthletes.map(athlete => `<option value="${athlete.id}">${athlete.name}</option>`).join('');
    } catch (error) {
        console.error('Error loading athletes:', error);
    }
}

// Form submission
document.addEventListener('DOMContentLoaded', () => {
    loadResults();
    
    document.getElementById('resultForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const resultData = {
            race_id: parseInt(document.getElementById('resultRace').value),
            event_id: parseInt(document.getElementById('resultEvent').value),
            athlete_id: parseInt(document.getElementById('resultAthlete').value),
            position: parseInt(document.getElementById('resultPosition').value),
            time: document.getElementById('resultTime').value || null,
            notes: document.getElementById('resultNotes').value || null
        };
        
        try {
            const response = await fetchWithAuth(`${API_BASE_URL}/api/results`, {
                method: 'POST',
                body: JSON.stringify(resultData)
            });
            
            if (!response) return;
            
            const result = await response.json();
            
            if (response.ok) {
                toast.show('Result added successfully!', 'success');
                closeResultModal();
                loadResults();
            } else {
                toast.show(result.message || 'Error adding result', 'error');
            }
        } catch (error) {
            console.error('Error adding result:', error);
            toast.show('Error adding result', 'error');
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
const debouncedFilterResults = debounceSearch(filterResults);

// Export to CSV function
function exportResults() {
    if (!allResults || allResults.length === 0) {
        toast.show('No results to export', 'warning');
        return;
    }
    
    const exportData = allResults.map(result => ({
        'Position': result.position,
        'Athlete': result.athlete_name,
        'Race': result.race_name,
        'Event': result.event_name,
        'Time': result.time || 'N/A',
        'Notes': result.notes || ''
    }));
    
    exportToCSV(exportData, 'athsys_results');
    toast.show('Results exported successfully!', 'success');
}

// Initialize keyboard shortcuts
initKeyboardShortcuts([
    {
        key: 'n',
        ctrl: true,
        action: () => {
            const btn = document.getElementById('addResultBtn');
            if (btn && btn.style.display !== 'none') {
                showAddResultModal();
            }
        }
    }
]);
