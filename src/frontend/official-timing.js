// Official Timing System - JavaScript

const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : window.location.origin;

// Timer state
let timerState = {
    isRunning: false,
    startTime: 0,
    elapsedTime: 0,
    animationFrameId: null,
    selectedEventId: null
};

// Toast notification
class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container') || this.createContainer();
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 10000;
            display: flex; flex-direction: column; gap: 10px;
        `;
        document.body.appendChild(container);
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

// Authentication check
function checkAuth() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const userStr = localStorage.getItem('user') || sessionStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    
    if (!token || !user) {
        window.location.href = 'login.html';
        return null;
    }
    
    // Check role - only chief_registrar and official can access
    if (!['chief_registrar', 'official'].includes(user.role)) {
        toast.show('❌ Unauthorized: Only Chief Registrars and Officials can access this page', 'error');
        setTimeout(() => window.location.href = 'dashboard.html', 2000);
        return null;
    }
    
    return user;
}
// Check if plugin is enabled
async function checkPluginStatus() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/plugins/official_timing`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) {
            throw new Error('Plugin not found');
        }
        
        const data = await response.json();
        const plugin = data.plugin;
        
        if (!plugin.enabled) {
            toast.show('❌ Official Timing System is currently disabled by admin', 'error');
            setTimeout(() => window.location.href = 'dashboard.html', 3000);
            return false;
        }
        
        return true;
    } catch (error) {
        console.warn('Could not verify plugin status (may not be admin):', error);
        // Allow access if not admin user - plugin status will only be checked by admins
        return true;
    }
}
async function logout() {
    return logoutWithRevocation({
        redirectTo: 'login.html',
        clearMode: 'all'
    });
}

// Format time MM:SS.CC (centiseconds)
function formatTime(milliseconds) {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const centiseconds = Math.floor((milliseconds % 1000) / 10);
    
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(centiseconds).padStart(2, '0')}`;
}

// Update timer display
function updateTimerDisplay() {
    const now = Date.now();
    const elapsed = timerState.elapsedTime + (timerState.isRunning ? now - timerState.startTime : 0);
    document.getElementById('timer-display').textContent = formatTime(elapsed);
}

// Start timer
function startTimer() {
    if (!timerState.selectedEventId) {
        toast.show('⚠️ Please select an event first', 'warning');
        return;
    }

    if (timerState.isRunning) return;
    
    timerState.isRunning = true;
    timerState.startTime = Date.now();
    
    document.getElementById('btn-start').disabled = true;
    document.getElementById('btn-stop').disabled = false;
    
    const statusEl = document.getElementById('timer-status');
    statusEl.textContent = '▶ RUNNING';
    statusEl.classList.remove('stopped');
    statusEl.classList.add('running');
    
    // Animation loop
    function animate() {
        updateTimerDisplay();
        timerState.animationFrameId = requestAnimationFrame(animate);
    }
    animate();
    
    toast.show('✅ Timer started', 'success');
}

// Stop timer
function stopTimer() {
    if (!timerState.isRunning) return;
    
    timerState.isRunning = false;
    timerState.elapsedTime += Date.now() - timerState.startTime;
    
    if (timerState.animationFrameId) {
        cancelAnimationFrame(timerState.animationFrameId);
    }
    
    document.getElementById('btn-start').disabled = false;
    document.getElementById('btn-stop').disabled = true;
    
    const statusEl = document.getElementById('timer-status');
    statusEl.textContent = '⏹ STOPPED';
    statusEl.classList.remove('running');
    statusEl.classList.add('stopped');
    
    // Get final time
    const finalTime = formatTime(timerState.elapsedTime);
    toast.show(`⏱️ Timer stopped at ${finalTime}`, 'info');
}

// Reset timer
function resetTimer() {
    timerState.isRunning = false;
    timerState.elapsedTime = 0;
    timerState.startTime = 0;
    
    if (timerState.animationFrameId) {
        cancelAnimationFrame(timerState.animationFrameId);
    }
    
    document.getElementById('timer-display').textContent = '00:00.00';
    document.getElementById('btn-start').disabled = false;
    document.getElementById('btn-stop').disabled = true;
    
    const statusEl = document.getElementById('timer-status');
    statusEl.textContent = 'READY';
    statusEl.classList.remove('running');
    statusEl.classList.add('stopped');
    
    toast.show('🔄 Timer reset', 'info');
}

// Load events from API
async function loadEvents() {
    try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        const response = await fetch(`${API_BASE_URL}/api/events`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) throw new Error('Failed to load events');
        
        const events = await response.json();
        const select = document.getElementById('event-select');
        
        if (Array.isArray(events)) {
            events.forEach(event => {
                const option = document.createElement('option');
                option.value = event.id;
                option.textContent = `${event.name} (${event.race_name || 'Race'})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading events:', error);
        toast.show('⚠️ Could not load events', 'warning');
    }
}

// Select event
function selectEvent() {
    const eventId = document.getElementById('event-select').value;
    const eventName = document.getElementById('event-select').options[document.getElementById('event-select').selectedIndex].text;
    
    if (eventId) {
        timerState.selectedEventId = eventId;
        document.getElementById('current-event').textContent = eventName;
        document.getElementById('btn-start').disabled = false;
        toast.show(`✅ Event selected: ${eventName}`, 'success');
    } else {
        timerState.selectedEventId = null;
        document.getElementById('current-event').textContent = 'No event selected';
        document.getElementById('btn-start').disabled = true;
    }
}

// Add result field
function addResultField() {
    const container = document.getElementById('results-container');
    const position = container.children.length + 1;
    
    const resultDiv = document.createElement('div');
    resultDiv.className = 'result-position';
    resultDiv.id = `result-${position}`;
    resultDiv.innerHTML = `
        <div class="result-position-number">#${position}</div>
        <input type="number" class="result-input" placeholder="Enter bib number" 
               data-position="${position}" min="1" required>
        <button class="result-remove" onclick="removeResultField(${position})">✕</button>
    `;
    
    container.appendChild(resultDiv);
    const input = resultDiv.querySelector('input');
    input.focus();
    
    if (position === 1) {
        toast.show('📝 Add bib numbers in finishing order', 'info');
    }
}

// Remove result field
function removeResultField(position) {
    const resultDiv = document.getElementById(`result-${position}`);
    if (resultDiv) {
        resultDiv.remove();
        
        // Renumber remaining fields
        const container = document.getElementById('results-container');
        Array.from(container.children).forEach((child, index) => {
            const newPosition = index + 1;
            child.id = `result-${newPosition}`;
            child.querySelector('.result-position-number').textContent = `#${newPosition}`;
            child.querySelector('input').dataset.position = newPosition;
            child.querySelector('button').onclick = () => removeResultField(newPosition);
        });
    }
}

// Submit results
async function submitResults() {
    if (!timerState.selectedEventId) {
        toast.show('⚠️ Please select an event', 'warning');
        return;
    }
    
    const resultContainer = document.getElementById('results-container');
    const inputs = resultContainer.querySelectorAll('input');
    
    if (inputs.length === 0) {
        toast.show('⚠️ Please add at least one finisher', 'warning');
        return;
    }
    
    // Validate and collect results
    const results = [];
    const bibs = new Set();
    
    for (let i = 0; i < inputs.length; i++) {
        const bib = inputs[i].value.trim();
        
        if (!bib) {
            toast.show(`⚠️ Position ${i + 1}: Please enter a bib number`, 'warning');
            return;
        }
        
        if (bibs.has(bib)) {
            toast.show(`⚠️ Duplicate bib number: ${bib}`, 'error');
            return;
        }
        
        bibs.add(bib);
        results.push({
            position: i + 1,
            bib: parseInt(bib),
            time: timerState.elapsedTime
        });
    }
    
    // Submit to API
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const submitBtn = document.getElementById('btn-submit');
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/events/${timerState.selectedEventId}/results`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                results,
                finish_time: timerState.elapsedTime,
                recorded_by: 'official'
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const messageEl = document.getElementById('result-message');
            messageEl.textContent = `✅ ${results.length} result(s) submitted successfully!`;
            messageEl.classList.add('show', 'success');
            
            // Clear results form
            setTimeout(() => {
                resultContainer.innerHTML = '';
                resetTimer();
                messageEl.classList.remove('show');
            }, 2000);
            
            toast.show(`🏆 Results submitted for ${results.length} finisher(s)`, 'success');
        } else {
            const messageEl = document.getElementById('result-message');
            messageEl.textContent = `❌ Error: ${data.message || 'Failed to submit results'}`;
            messageEl.classList.add('show', 'error');
            toast.show(`Error: ${data.message || 'Failed to submit'}`, 'error');
        }
    } catch (error) {
        console.error('Error submitting results:', error);
        const messageEl = document.getElementById('result-message');
        messageEl.textContent = '❌ Connection error. Please try again.';
        messageEl.classList.add('show', 'error');
        toast.show('Connection error', 'error');
    } finally {
        submitBtn.disabled = false;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const user = checkAuth();
    if (!user) return;
    
    document.getElementById('userName').textContent = `👤 ${user.name} (${user.role.toUpperCase()})`;
    
    // Load events
    loadEvents();
    
    // Add first result field
    addResultField();
    
    console.log('⏱️ Official Timing System initialized');
});

// Export for global access
window.OfficialTiming = {
    startTimer,
    stopTimer,
    resetTimer,
    selectEvent,
    addResultField,
    removeResultField,
    submitResults,
    logout
};
