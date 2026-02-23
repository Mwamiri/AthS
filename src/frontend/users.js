// User Management JavaScript
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
let allUsers = [];

function checkAuth() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const userStr = localStorage.getItem('user') || sessionStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    
    if (!token || !user) {
        window.location.href = 'login.html';
        return null;
    }
    
    // Only admins can access this page
    if (user.role !== 'admin') {
        toast.show('Access denied. Admin access required.', 'error');
        setTimeout(() => window.location.href = 'dashboard.html', 2000);
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

async function loadUsers() {
    const user = checkAuth();
    if (!user) return;
    
    document.getElementById('userName').textContent = user.name || user.email;    
    // Show loading skeleton
    showLoadingSkeleton('usersContainer', 6, 'card');    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/api/users`);
        if (!response) return;
        
        const users = await response.json();
        allUsers = Array.isArray(users) ? users : [];
        displayUsers(allUsers);
        
    } catch (error) {
        console.error('Error loading users:', error);
        toast.show('Error loading users', 'error');
        document.getElementById('usersContainer').innerHTML = '<div class="error">Failed to load users</div>';
    }
}

function displayUsers(users) {
    const container = document.getElementById('usersContainer');
    
    if (!users || users.length === 0) {
        showEmptyState('usersContainer', {
            icon: '👥',
            title: 'No users found',
            message: 'Create your first user or adjust your search filters',
            actionText: '➕ Add First User',
            actionCallback: 'showAddUserModal()',
            showAction: true
        });
        return;
    }
    
    const roleColors = {
        admin: '#e63946',
        chief_registrar: '#4a90e2',
        registrar: '#06d6a0',
        starter: '#f7931e',
        coach: '#6bcbf7',
        athlete: '#a855f7',
        viewer: '#666'
    };
    
    const roleIcons = {
        admin: '👑',
        chief_registrar: '📋',
        registrar: '✍️',
        starter: '🎯',
        coach: '🏅',
        athlete: '🏃',
        viewer: '👁️'
    };
    
    container.innerHTML = users.map(user => {
        const roleColor = roleColors[user.role] || '#666';
        const roleIcon = roleIcons[user.role] || '👤';
        const statusColor = user.active ? '#06d6a0' : '#999';
        
        return `
            <div class="user-card" style="background: var(--background-dark); border-radius: 12px; padding: 1.5rem; border-left: 4px solid ${roleColor};">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div>
                        <h3 style="margin: 0; color: var(--text-color); display: flex; align-items: center; gap: 0.5rem;">
                            ${roleIcon} ${user.name}
                            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: ${statusColor};"></span>
                        </h3>
                        <p style="color: var(--text-secondary); margin: 0.25rem 0; font-size: 0.9rem;">
                            📧 ${user.email}
                        </p>
                    </div>
                    <span class="role-badge" style="background: ${roleColor}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem;">
                        ${formatRole(user.role)}
                    </span>
                </div>
                
                <div style="display: flex; gap: 0.5rem; margin-top: 1rem; flex-wrap: wrap;">
                    <button class="btn btn-small" onclick="editUser(${user.id})">✏️ Edit</button>
                    ${user.active ? 
                        `<button class="btn btn-small btn-secondary" onclick="toggleUserStatus(${user.id}, false)">🚫 Deactivate</button>` :
                        `<button class="btn btn-small btn-success" onclick="toggleUserStatus(${user.id}, true)">✅ Activate</button>`
                    }
                </div>
            </div>
        `;
    }).join('');
}

function formatRole(role) {
    const roleNames = {
        'admin': 'Administrator',
        'chief_registrar': 'Chief Registrar',
        'registrar': 'Registrar',
        'starter': 'Starter Official',
        'coach': 'Coach',
        'athlete': 'Athlete',
        'viewer': 'Viewer'
    };
    return roleNames[role] || role;
}

function filterUsers() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const roleFilter = document.getElementById('roleFilter').value;
    
    const filtered = allUsers.filter(user => {
        const matchesSearch = user.name.toLowerCase().includes(searchTerm) ||
                            user.email.toLowerCase().includes(searchTerm);
        const matchesRole = !roleFilter || user.role === roleFilter;
        return matchesSearch && matchesRole;
    });
    
    displayUsers(filtered);
}

function refreshUsers() {
    toast.show('Refreshing users...', 'info');
    loadUsers();
}

function showAddUserModal() {
    document.getElementById('modalTitle').textContent = 'Add New User';
    document.getElementById('userForm').reset();
    document.getElementById('userId').value = '';
    document.getElementById('passwordGroup').style.display = 'block';
    document.getElementById('userPassword').required = true;
    document.getElementById('userModal').style.display = 'flex';
}

function closeUserModal() {
    document.getElementById('userModal').style.display = 'none';
}

async function editUser(userId) {
    const user = allUsers.find(u => u.id === userId);
    if (!user) return;
    
    document.getElementById('modalTitle').textContent = 'Edit User';
    document.getElementById('userId').value = user.id;
    document.getElementById('userName').value = user.name;
    document.getElementById('userEmail').value = user.email;
    document.getElementById('userRole').value = user.role;
    document.getElementById('userActive').checked = user.active;
    document.getElementById('passwordGroup').style.display = 'none';
    document.getElementById('userPassword').required = false;
    document.getElementById('userModal').style.display = 'flex';
}

async function toggleUserStatus(userId, activate) {
    const action = activate ? 'activate' : 'deactivate';
    
    if (!confirm(`Are you sure you want to ${action} this user?`)) {
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/api/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify({ active: activate })
        });
        
        if (!response) return;
        
        if (response.ok) {
            toast.show(`User ${activate ? 'activated' : 'deactivated'} successfully!`, 'success');
            loadUsers();
        } else {
            const result = await response.json();
            toast.show(result.message || `Error ${action}ing user`, 'error');
        }
    } catch (error) {
        console.error(`Error ${action}ing user:`, error);
        toast.show(`Error ${action}ing user`, 'error');
    }
}

// Form submission
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    
    document.getElementById('userForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const userId = document.getElementById('userId').value;
        const userData = {
            name: document.getElementById('userName').value,
            email: document.getElementById('userEmail').value,
            role: document.getElementById('userRole').value,
            active: document.getElementById('userActive').checked
        };
        
        // Only include password if it's a new user or being changed
        const password = document.getElementById('userPassword').value;
        if (password) {
            userData.password = password;
        }
        
        try {
            const url = userId 
                ? `${API_BASE_URL}/api/users/${userId}`
                : `${API_BASE_URL}/api/users`;
            
            const method = userId ? 'PUT' : 'POST';
            
            const response = await fetchWithAuth(url, {
                method: method,
                body: JSON.stringify(userData)
            });
            
            if (!response) return;
            
            const result = await response.json();
            
            if (response.ok) {
                toast.show(userId ? 'User updated successfully!' : 'User created successfully!', 'success');
                closeUserModal();
                loadUsers();
            } else {
                toast.show(result.message || 'Error saving user', 'error');
            }
        } catch (error) {
            console.error('Error saving user:', error);
            toast.show('Error saving user', 'error');
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
const debouncedFilterUsers = debounceSearch(filterUsers);

// Export to CSV function
function exportUsers() {
    if (!allUsers || allUsers.length === 0) {
        toast.show('No users to export', 'warning');
        return;
    }
    
    const exportData = allUsers.map(user => ({
        'Name': user.name,
        'Email': user.email,
        'Role': formatRole(user.role),
        'Active': user.active ? 'Yes' : 'No',
        'Created': formatDateTime(user.created_at || '')
    }));
    
    exportToCSV(exportData, 'athsys_users');
    toast.show('Users exported successfully!', 'success');
}

// Initialize keyboard shortcuts
initKeyboardShortcuts([
    {
        key: 'n',
        ctrl: true,
        action: () => {
            showAddUserModal();
        }
    }
]);
