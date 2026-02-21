// Public Registration JavaScript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '/api';

let currentRace = null;
let availableEvents = [];

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
        }, 4000);
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

// Initialize Registration Page
document.addEventListener('DOMContentLoaded', async () => {
    // Get link ID from URL
    const pathParts = window.location.pathname.split('/');
    const linkId = pathParts[pathParts.length - 1] || getQueryParam('link');
    
    if (!linkId) {
        showError('Invalid registration link. Please check your URL.');
        return;
    }
    
    await loadRaceInfo(linkId);
    setupForm();
});

function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Load Race Information
async function loadRaceInfo(linkId) {
    try {
        const response = await fetch(`${API_BASE_URL}/register/${linkId}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            currentRace = data.data;
            displayRaceInfo(currentRace);
            await loadEvents(currentRace.race_id);
        } else {
            throw new Error(data.message || 'Failed to load race information');
        }
    } catch (error) {
        showError('This registration link is invalid or has expired. ' + error.message);
    }
}

// Display Race Information
function displayRaceInfo(race) {
    document.getElementById('race-name-display').textContent = race.name;
    
    const raceInfo = document.getElementById('race-info');
    raceInfo.innerHTML = `
        <span>📅 ${new Date(race.date).toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        })}</span>
        <span>📍 ${race.location}</span>
    `;
}

// Load Events for Race
async function loadEvents(raceId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/events`);
        const data = await response.json();
        
        if (data.status === 'success') {
            // Filter events for this race
            availableEvents = data.data.filter(event => 
                currentRace.events && currentRace.events.includes(event.id)
            );
            displayEvents(availableEvents);
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        document.getElementById('events-container').innerHTML = 
            `<p style="color: var(--danger-color); text-align: center;">Failed to load events</p>`;
    }
}

// Display Events
function displayEvents(events) {
    const container = document.getElementById('events-container');
    
    if (events.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No events available for this race</p>';
        return;
    }
    
    container.innerHTML = events.map(event => `
        <div class="event-card" onclick="toggleEvent(${event.id})">
            <input type="checkbox" id="event-${event.id}" name="events" value="${event.id}" 
                   onclick="event.stopPropagation(); toggleEvent(${event.id})">
            <div class="event-info">
                <div class="event-name">${event.name}</div>
                <div class="event-details">
                    ${event.category ? event.category + ' • ' : ''}
                    ${event.distance || 'Track Event'}
                </div>
            </div>
        </div>
    `).join('');
}

// Toggle Event Selection
function toggleEvent(eventId) {
    const checkbox = document.getElementById(`event-${eventId}`);
    checkbox.checked = !checkbox.checked;
    
    const card = checkbox.closest('.event-card');
    if (checkbox.checked) {
        card.classList.add('selected');
    } else {
        card.classList.remove('selected');
    }
}

// Setup Form
function setupForm() {
    const form = document.getElementById('public-registration-form');
    form.addEventListener('submit', handleRegistration);
}

// Handle Registration Submission
async function handleRegistration(e) {
    e.preventDefault();
    
    // Get selected events
    const selectedEvents = Array.from(document.querySelectorAll('input[name="events"]:checked'))
        .map(cb => parseInt(cb.value));
    
    if (selectedEvents.length === 0) {
        ToastManager.show('Please select at least one event', 'warning');
        return;
    }
    
    // Validate email
    const email = document.getElementById('athlete-email').value;
    if (!validateEmail(email)) {
        ToastManager.show('Please enter a valid email address', 'error');
        return;
    }
    
    // Prepare registration data
    const registrationData = {
        athlete_name: document.getElementById('athlete-name').value.trim(),
        athlete_email: email,
        phone: document.getElementById('athlete-phone').value.trim() || null,
        team: document.getElementById('athlete-team').value.trim() || null,
        events: selectedEvents
    };
    
    // Disable submit button
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>⏳ Processing...</span>';
    
    try {
        const linkId = window.location.pathname.split('/').pop() || getQueryParam('link');
        const response = await fetch(`${API_BASE_URL}/register/${linkId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(registrationData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showSuccess(registrationData, selectedEvents);
        } else {
            throw new Error(data.message || 'Registration failed');
        }
    } catch (error) {
        ToastManager.show('Registration failed: ' + error.message, 'error');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

// Show Success Message
function showSuccess(registrationData, selectedEventIds) {
    document.getElementById('registration-form-container').style.display = 'none';
    
    const selectedEventNames = availableEvents
        .filter(e => selectedEventIds.includes(e.id))
        .map(e => e.name);
    
    const summary = `
        <div style="text-align: left;">
            <p><strong>Name:</strong> ${registrationData.athlete_name}</p>
            <p><strong>Email:</strong> ${registrationData.athlete_email}</p>
            ${registrationData.phone ? `<p><strong>Phone:</strong> ${registrationData.phone}</p>` : ''}
            ${registrationData.team ? `<p><strong>Team:</strong> ${registrationData.team}</p>` : ''}
            <p><strong>Events:</strong></p>
            <ul style="list-style: none; padding: 0;">
                ${selectedEventNames.map(name => `<li>✓ ${name}</li>`).join('')}
            </ul>
        </div>
    `;
    
    document.getElementById('registration-summary').innerHTML = summary;
    document.getElementById('success-message').style.display = 'block';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Show Error
function showError(message) {
    document.getElementById('registration-form-container').style.display = 'none';
    document.getElementById('error-message').textContent = message;
    document.getElementById('error-container').style.display = 'block';
}

// Email Validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}
