// Admin Dashboard JavaScript

const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '/api';

// Toast notification system (same as auth.js)
const toast = window.AuthManager?.toast || {
    show: (message, type) => alert(message)
};

// Check admin authentication
function checkAdminAuth() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token || !user.email) {
        toast.show('Please log in to continue', 'error');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1500);
        return false;
    }
    
    if (user.role !== 'admin') {
        toast.show('Access denied. Admin privileges required.', 'error');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1500);
        return false;
    }
    
    // Display user info
    const userInfoElement = document.getElementById('admin-user-name');
    if (userInfoElement) {
        userInfoElement.textContent = user.name;
    }
    
    return true;
}

// Navigation between admin sections
function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.admin-section');
    
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.dataset.section;
            
            // Update active states
            navButtons.forEach(btn => btn.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            
            button.classList.add('active');
            document.getElementById(`${target}-section`).classList.add('active');
            
            // Load section data
            if (target === 'users') {
                loadUsers();
            } else if (target === 'audit') {
                loadAuditLogs();
            }
        });
    });
}

// Sample users data (will be replaced with API calls)
let usersData = [
    {
        id: 1,
        name: 'John Athlete',
        email: 'john@athsys.com',
        role: 'athlete',
        status: 'active',
        lastLogin: '2 hours ago',
        createdAt: '2024-01-15'
    },
    {
        id: 2,
        name: 'Sarah Coach',
        email: 'sarah@athsys.com',
        role: 'coach',
        status: 'active',
        lastLogin: '1 day ago',
        createdAt: '2024-01-10'
    },
    {
        id: 3,
        name: 'Chief Registrar',
        email: 'chief@athsys.com',
        role: 'chief_registrar',
        status: 'active',
        lastLogin: '3 hours ago',
        createdAt: '2024-01-08'
    },
    {
        id: 4,
        name: 'Registrar User',
        email: 'registrar@athsys.com',
        role: 'registrar',
        status: 'active',
        lastLogin: '5 hours ago',
        createdAt: '2024-01-07'
    },
    {
        id: 5,
        name: 'Starter Official',
        email: 'starter@athsys.com',
        role: 'starter',
        status: 'active',
        lastLogin: '1 day ago',
        createdAt: '2024-01-06'
    },
    {
        id: 6,
        name: 'Admin User',
        email: 'admin@athsys.com',
        role: 'admin',
        status: 'active',
        lastLogin: 'Just now',
        createdAt: '2024-01-01'
    },
    {
        id: 7,
        name: 'Viewer User',
        email: 'viewer@athsys.com',
        role: 'viewer',
        status: 'active',
        lastLogin: '1 week ago',
        createdAt: '2024-01-05'
    }
];

// Load users into table
async function loadUsers(filters = {}) {
    const tbody = document.getElementById('users-tbody');
    
    if (!tbody) return;
    
    // Show loading state
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">Loading users...</td></tr>';
    
    try {
        // In production, this would fetch from API
        // const response = await fetch(`${API_BASE_URL}/api/admin/users`);
        // const users = await response.json();
        
        // For now, use demo data
        let users = [...usersData];
        
        // Apply filters
        if (filters.search) {
            const search = filters.search.toLowerCase();
            users = users.filter(u => 
                u.name.toLowerCase().includes(search) || 
                u.email.toLowerCase().includes(search)
            );
        }
        
        if (filters.role && filters.role !== 'all') {
            users = users.filter(u => u.role === filters.role);
        }
        
        if (filters.status && filters.status !== 'all') {
            users = users.filter(u => u.status === filters.status);
        }
        
        // Update role statistics
        updateRoleStats(usersData);
        
        // Render users
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">No users found</td></tr>';
            return;
        }
        
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>
                    <div class="user-cell">
                        <div class="user-avatar">${user.name.charAt(0)}</div>
                        <div class="user-details">
                            <div class="user-name">${user.name}</div>
                            <div style="color: var(--text-secondary); font-size: 0.875rem;">${user.email}</div>
                        </div>
                    </div>
                </td>
                <td><span class="role-badge">${user.role}</span></td>
                <td><span class="status-badge ${user.status}">${user.status}</span></td>
                <td style="color: var(--text-secondary);">${user.lastLogin}</td>
                <td style="color: var(--text-secondary);">${user.createdAt}</td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn" onclick="editUser(${user.id})">✏️ Edit</button>
                        <button class="action-btn danger" onclick="deleteUser(${user.id})">🗑️ Delete</button>
                    </div>
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error loading users:', error);
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--track-red);">Error loading users</td></tr>';
        toast.show('Failed to load users', 'error');
    }
}

// Search and filter handlers
function initFilters() {
    const searchInput = document.getElementById('user-search');
    const roleFilter = document.getElementById('role-filter');
    const statusFilter = document.getElementById('status-filter');
    
    let searchTimeout;
    
    const applyFilters = () => {
        const filters = {
            search: searchInput?.value || '',
            role: roleFilter?.value || 'all',
            status: statusFilter?.value || 'all'
        };
        loadUsers(filters);
    };
    
    // Search with debounce
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(applyFilters, 300);
        });
    }
    
    // Filter changes
    if (roleFilter) roleFilter.addEventListener('change', applyFilters);
    if (statusFilter) statusFilter.addEventListener('change', applyFilters);
}

// Update role statistics
function updateRoleStats(users) {
    const roleCounts = {
        admin: 0,
        chief_registrar: 0,
        registrar: 0,
        starter: 0,
        coach: 0,
        athlete: 0,
        viewer: 0
    };
    
    users.forEach(user => {
        if (roleCounts.hasOwnProperty(user.role)) {
            roleCounts[user.role]++;
        }
    });
    
    // Update DOM elements
    Object.keys(roleCounts).forEach(role => {
        const element = document.getElementById(`${role}-count`);
        if (element) {
            element.textContent = roleCounts[role];
        }
    });
}

// Add new user modal
function showAddUserModal() {
    const modal = document.getElementById('user-modal');
    const form = document.getElementById('user-form');
    
    if (!modal || !form) return;
    
    // Set modal title
    document.getElementById('modal-title').textContent = 'Add New User';
    
    // Reset form
    form.reset();
    form.dataset.userId = '';
    
    // Show modal
    modal.classList.add('active');
}

// Edit user modal
function editUser(userId) {
    const user = usersData.find(u => u.id === userId);
    if (!user) return;
    
    const modal = document.getElementById('user-modal');
    const form = document.getElementById('user-form');
    
    if (!modal || !form) return;
    
    // Set modal title
    document.getElementById('modal-title').textContent = 'Edit User';
    
    // Populate form
    document.getElementById('user-name').value = user.name;
    document.getElementById('user-email').value = user.email;
    document.getElementById('user-role-select').value = user.role;
    document.getElementById('user-status').value = user.status;
    
    // Store user ID
    form.dataset.userId = userId;
    
    // Show modal
    modal.classList.add('active');
}

// Delete user
function deleteUser(userId) {
    const user = usersData.find(u => u.id === userId);
    if (!user) return;
    
    if (!confirm(`Are you sure you want to delete ${user.name}?`)) return;
    
    // In production, this would call API
    // await fetch(`${API_BASE_URL}/api/admin/users/${userId}`, { method: 'DELETE' });
    
    // For now, remove from demo data
    usersData = usersData.filter(u => u.id !== userId);
    
    toast.show('User deleted successfully', 'success');
    loadUsers();
}

// Save user (add or edit)
async function saveUser(event) {
    event.preventDefault();
    
    const form = event.target;
    const userId = form.dataset.userId;
    
    const userData = {
        name: document.getElementById('user-name').value,
        email: document.getElementById('user-email').value,
        role: document.getElementById('user-role-select').value,
        status: document.getElementById('user-status').value
    };
    
    const password = document.getElementById('user-password').value;
    if (password) {
        userData.password = password;
    }
    
    try {
        if (userId) {
            // Update existing user
            const user = usersData.find(u => u.id == userId);
            if (user) {
                Object.assign(user, userData);
                toast.show('User updated successfully', 'success');
            }
        } else {
            // Add new user
            const newUser = {
                id: Math.max(...usersData.map(u => u.id)) + 1,
                ...userData,
                lastLogin: 'Never',
                createdAt: new Date().toISOString().split('T')[0]
            };
            usersData.push(newUser);
            toast.show('User added successfully', 'success');
        }
        
        // Close modal and reload
        closeModal();
        loadUsers();
        
    } catch (error) {
        console.error('Error saving user:', error);
        toast.show('Failed to save user', 'error');
    }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('user-modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Load audit logs
async function loadAuditLogs() {
    const tbody = document.getElementById('audit-tbody');
    
    if (!tbody) return;
    
    // Show loading state
    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem;">Loading audit logs...</td></tr>';
    
    // Demo audit logs
    const logs = [
        {
            user: 'Admin User',
            action: 'User Created',
            details: 'Created new athlete account for John Doe',
            timestamp: '2 hours ago'
        },
        {
            user: 'Sarah Coach',
            action: 'Event Modified',
            details: 'Updated 100m Sprint event details',
            timestamp: '5 hours ago'
        },
        {
            user: 'Mike Official',
            action: 'Results Approved',
            details: 'Approved results for Marathon event',
            timestamp: '1 day ago'
        },
        {
            user: 'Admin User',
            action: 'Settings Changed',
            details: 'Updated security settings',
            timestamp: '2 days ago'
        }
    ];
    
    tbody.innerHTML = logs.map(log => `
        <tr>
            <td style="color: var(--text-primary); font-weight: 600;">${log.user}</td>
            <td><span class="role-badge">${log.action}</span></td>
            <td style="color: var(--text-secondary);">${log.details}</td>
            <td style="color: var(--text-secondary);">${log.timestamp}</td>
        </tr>
    `).join('');
}

// Security settings handlers
function initSecuritySettings() {
    // 2FA toggle
    const twoFactorToggle = document.getElementById('require-2fa');
    if (twoFactorToggle) {
        twoFactorToggle.addEventListener('change', (e) => {
            const enabled = e.target.checked;
            toast.show(`Two-factor authentication ${enabled ? 'enabled' : 'disabled'}`, 'info');
            // In production: save to backend
        });
    }
    
    // Password policy checkboxes
    const policyCheckboxes = document.querySelectorAll('.setting-options input[type="checkbox"]');
    policyCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            toast.show('Password policy updated', 'info');
            // In production: save to backend
        });
    });
    
    // Session timeout
    const sessionTimeout = document.getElementById('session-timeout');
    if (sessionTimeout) {
        sessionTimeout.addEventListener('change', (e) => {
            toast.show(`Session timeout set to ${e.target.value}`, 'info');
            // In production: save to backend
        });
    }
}

// Logout handler
function handleLogout() {
    if (window.AuthManager && window.AuthManager.logout) {
        window.AuthManager.logout();
    } else {
        localStorage.removeItem('authToken');
        sessionStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check admin authentication
    if (!checkAdminAuth()) return;
    
    // Initialize navigation
    initNavigation();
    
    // Initialize filters
    initFilters();
    
    // Initialize security settings
    initSecuritySettings();
    
    // Load initial data
    loadUsers();
    
    // Attach form event listener
    const userForm = document.getElementById('user-form');
    if (userForm) {
        userForm.addEventListener('submit', saveUser);
    }
    
    // Modal close button
    const modalClose = document.querySelector('.modal-close');
    if (modalClose) {
        modalClose.addEventListener('click', closeModal);
    }
    
    // Close modal on outside click
    const modal = document.getElementById('user-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    
    // Add user button
    const addUserBtn = document.getElementById('add-user-btn');
    if (addUserBtn) {
        addUserBtn.addEventListener('click', showAddUserModal);
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    console.log('👑 Admin dashboard initialized');
});

// Export functions for global access
window.AdminDashboard = {
    loadUsers,
    editUser,
    deleteUser,
    showAddUserModal,
    closeModal,
    handleLogout
};
