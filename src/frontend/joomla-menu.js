// Joomla-Style Menu System for AthSys v2.1
// Provides hierarchical navigation with categories and access control

class JoomlaMenu {
    constructor() {
        this.isCollapsed = false;
        this.currentUser = this.getUser();
        this.menuStructure = this.buildMenuStructure();
        this.init();
    }

    getUser() {
        const userStr = localStorage.getItem('user') || sessionStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }

    buildMenuStructure() {
        const user = this.currentUser;
        if (!user) return [];

        const menu = [
            {
                category: 'Dashboard',
                icon: '📊',
                items: [
                    { name: 'Home', icon: '🏠', url: 'dashboard.html', roles: ['all'] },
                    { name: 'Statistics', icon: '📈', url: '#statistics', roles: ['all'] },
                    { name: 'Reports', icon: '📄', url: '#reports', roles: ['admin', 'chief_registrar'] }
                ]
            },
            {
                category: 'Competition Management',
                icon: '🏆',
                items: [
                    { name: 'Races', icon: '🏁', url: 'races.html', roles: ['admin', 'chief_registrar', 'registrar', 'starter', 'coach'] },
                    { name: 'Events', icon: '🎯', url: '#events', roles: ['admin', 'chief_registrar', 'registrar'] },
                    { name: 'Results', icon: '🏅', url: 'results.html', roles: ['all'] },
                    { 
                        name: 'Scheduling', 
                        icon: '📅', 
                        url: '#scheduling', 
                        roles: ['admin', 'chief_registrar'],
                        badge: 'New'
                    }
                ]
            },
            {
                category: 'Participant Management',
                icon: '👥',
                items: [
                    { name: 'Athletes', icon: '🏃', url: 'athletes.html', roles: ['admin', 'chief_registrar', 'registrar', 'coach'] },
                    { name: 'Registration', icon: '✍️', url: '#registration', roles: ['admin', 'chief_registrar', 'registrar'] },
                    { name: 'Teams', icon: '👨‍👩‍👧‍👦', url: '#teams', roles: ['admin', 'coach'] },
                    { 
                        name: 'Bulk Import', 
                        icon: '📥', 
                        url: '#bulk-import', 
                        roles: ['admin', 'chief_registrar', 'registrar']
                    }
                ]
            },
            {
                category: 'System',
                icon: '⚙️',
                items: [
                    { name: 'Users', icon: '👤', url: 'users.html', roles: ['admin'] },
                    { name: 'Settings', icon: '🔧', url: '#settings', roles: ['admin'] },
                    { name: 'Cache Manager', icon: '💾', url: '#cache', roles: ['admin'], badge: 'v2.1' },
                    { name: 'API Status', icon: '🔗', url: '#api-status', roles: ['admin'] },
                    {
                        name: 'Notifications',
                        icon: '🔔',
                        url: '#notifications',
                        roles: ['all'],
                        onClick: () => {
                            if (typeof notificationCenter !== 'undefined') {
                                notificationCenter.toggle();
                            }
                        }
                    }
                ]
            },
            {
                category: 'Tools',
                icon: '🛠️',
                items: [
                    { name: 'Export Data', icon: '📤', url: '#export', roles: ['admin', 'chief_registrar'] },
                    { name: 'Backup', icon: '💼', url: '#backup', roles: ['admin'] },
                    { name: 'Logs', icon: '📜', url: '#logs', roles: ['admin'] },
                    { name: 'Help Center', icon: '❓', url: '#help', roles: ['all'] }
                ]
            },
            {
                category: 'Account',
                icon: '👤',
                items: [
                    { name: 'Profile', icon: '👨‍💼', url: '#profile', roles: ['all'] },
                    { name: 'Preferences', icon: '⚙️', url: '#preferences', roles: ['all'] },
                    { 
                        name: 'Logout', 
                        icon: '🚪', 
                        url: '#logout', 
                        roles: ['all'],
                        onClick: () => this.logout()
                    }
                ]
            }
        ];

        // Filter menu based on user role
        return menu.map(category => ({
            ...category,
            items: category.items.filter(item => 
                item.roles.includes('all') || item.roles.includes(user.role)
            )
        })).filter(category => category.items.length > 0);
    }

    init() {
        this.render();
        this.attachEventListeners();
        this.initSearch();
        this.restoreMenuState();
    }

    render() {
        const menuHTML = `
            <div class="joomla-menu-container" id="joomlaMenu">
                <div class="joomla-menu-header">
                    <div class="joomla-menu-logo">
                        🏃 AthSys
                    </div>
                    <button class="joomla-menu-toggle" id="menuToggle">
                        ☰
                    </button>
                </div>
                
                <div class="joomla-menu-search">
                    <input type="text" id="menuSearch" placeholder="🔍 Search menu...">
                </div>
                
                <nav class="joomla-menu-nav">
                    ${this.renderCategories()}
                </nav>
                
                <div class="joomla-menu-footer">
                    <div style="margin-bottom: 0.5rem;">
                        <strong>${this.currentUser?.name || 'User'}</strong>
                    </div>
                    <div style="opacity: 0.7;">
                        ${this.formatRole(this.currentUser?.role)}
                    </div>
                    <div style="margin-top: 0.5rem; opacity: 0.5; font-size: 0.7rem;">
                        AthSys v2.1 © 2026
                    </div>
                </div>
            </div>
            
            <div class="joomla-settings-icon" id="settingsIcon" title="System Settings">
                ⚙️
            </div>
        `;

        // Insert menu into DOM
        const existingMenu = document.getElementById('joomlaMenu');
        if (existingMenu) {
            existingMenu.remove();
        }

        document.body.insertAdjacentHTML('afterbegin', menuHTML);

        // Add content wrapper if it doesn't exist
        if (!document.querySelector('.joomla-content-area')) {
            const content = document.querySelector('.container') || document.body;
            const wrapper = document.createElement('div');
            wrapper.className = 'joomla-content-area';
            content.parentNode.insertBefore(wrapper, content);
            wrapper.appendChild(content);
        }
    }

    renderCategories() {
        return this.menuStructure.map(category => `
            <div class="joomla-menu-category" data-category="${category.category}">
                <div class="joomla-menu-category-header">
                    <span>${category.icon} ${category.category}</span>
                    <span class="joomla-menu-category-icon">▼</span>
                </div>
                <ul class="joomla-menu-items">
                    ${category.items.map(item => this.renderMenuItem(item)).join('')}
                </ul>
            </div>
        `).join('');
    }

    renderMenuItem(item) {
        const isActive = window.location.pathname.includes(item.url) || 
                        window.location.hash === item.url;
        const activeClass = isActive ? 'active' : '';
        const badge = item.badge ? `<span class="joomla-menu-badge">${item.badge}</span>` : '';
        
        return `
            <li class="joomla-menu-item" data-name="${item.name}">
                <a href="${item.url}" class="joomla-menu-link ${activeClass}" 
                   ${item.onClick ? 'onclick="event.preventDefault(); joomlaMenu.handleItemClick(\'' + item.name + '\');"' : ''}>
                    <span class="joomla-menu-icon">${item.icon}</span>
                    <span>${item.name}</span>
                    ${badge}
                </a>
            </li>
        `;
    }

    handleItemClick(itemName) {
        this.menuStructure.forEach(category => {
            const item = category.items.find(i => i.name === itemName);
            if (item && item.onClick) {
                item.onClick();
            }
        });
    }

    attachEventListeners() {
        // Menu toggle
        const toggle = document.getElementById('menuToggle');
        if (toggle) {
            toggle.addEventListener('click', () => this.toggleMenu());
        }

        // Category collapse/expand
        document.querySelectorAll('.joomla-menu-category-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const category = e.target.closest('.joomla-menu-category');
                category.classList.toggle('collapsed');
                this.saveMenuState();
            });
        });

        // Settings icon
        const settingsIcon = document.getElementById('settingsIcon');
        if (settingsIcon) {
            settingsIcon.addEventListener('click', () => this.openSettings());
        }

        // Highlight active page
        this.highlightActivePage();
    }

    toggleMenu() {
        this.isCollapsed = !this.isCollapsed;
        const menu = document.getElementById('joomlaMenu');
        const content = document.querySelector('.joomla-content-area');
        
        if (menu) menu.classList.toggle('collapsed', this.isCollapsed);
        if (content) content.classList.toggle('expanded', this.isCollapsed);
        
        localStorage.setItem('joomla_menu_collapsed', this.isCollapsed);
    }

    initSearch() {
        const searchInput = document.getElementById('menuSearch');
        if (!searchInput) return;

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            
            if (!query) {
                // Show all items
                document.querySelectorAll('.joomla-menu-item').forEach(item => {
                    item.style.display = '';
                    item.classList.remove('search-highlight');
                });
                document.querySelectorAll('.joomla-menu-category').forEach(cat => {
                    cat.style.display = '';
                    cat.classList.remove('collapsed');
                });
                return;
            }

            // Search and highlight
            let hasResults = false;
            document.querySelectorAll('.joomla-menu-category').forEach(category => {
                let categoryHasMatch = false;
                
                category.querySelectorAll('.joomla-menu-item').forEach(item => {
                    const name = item.dataset.name.toLowerCase();
                    const matches = name.includes(query);
                    
                    item.style.display = matches ? '' : 'none';
                    item.classList.toggle('search-highlight', matches);
                    
                    if (matches) {
                        categoryHasMatch = true;
                        hasResults = true;
                    }
                });
                
                category.style.display = categoryHasMatch ? '' : 'none';
                if (categoryHasMatch) {
                    category.classList.remove('collapsed');
                }
            });

            if (!hasResults && typeof notificationCenter !== 'undefined') {
                notificationCenter.add('search', 'No Results', 
                    `No menu items found for "${query}"`, 'info');
            }
        });
    }

    highlightActivePage() {
        const currentPath = window.location.pathname.split('/').pop();
        document.querySelectorAll('.joomla-menu-link').forEach(link => {
            const href = link.getAttribute('href');
            if (href && (href.includes(currentPath) || href === '#' + window.location.hash)) {
                link.classList.add('active');
            }
        });
    }

    saveMenuState() {
        const state = {};
        document.querySelectorAll('.joomla-menu-category').forEach(category => {
            const name = category.dataset.category;
            state[name] = category.classList.contains('collapsed');
        });
        localStorage.setItem('joomla_menu_state', JSON.stringify(state));
    }

    restoreMenuState() {
        try {
            const collapsed = localStorage.getItem('joomla_menu_collapsed') === 'true';
            if (collapsed) this.toggleMenu();

            const state = JSON.parse(localStorage.getItem('joomla_menu_state') || '{}');
            Object.keys(state).forEach(categoryName => {
                const category = document.querySelector(`[data-category="${categoryName}"]`);
                if (category && state[categoryName]) {
                    category.classList.add('collapsed');
                }
            });
        } catch (e) {
            console.warn('Could not restore menu state:', e);
        }
    }

    openSettings() {
        if (typeof notificationCenter !== 'undefined') {
            notificationCenter.add('system', 'Settings', 
                'Opening system settings panel...', 'info');
        }
        // Navigate to settings or open modal
        window.location.hash = '#settings';
    }

    formatRole(role) {
        const roleNames = {
            'admin': '👑 Administrator',
            'chief_registrar': '📋 Chief Registrar',
            'registrar': '✍️ Registrar',
            'starter': '🎯 Starter',
            'coach': '🏅 Coach',
            'athlete': '🏃 Athlete',
            'viewer': '👁️ Viewer'
        };
        return roleNames[role] || role;
    }

    async logout() {
        if (confirm('Are you sure you want to logout?')) {
            const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
            try {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: token ? { 'Authorization': `Bearer ${token}` } : {}
                });
            } catch (error) {
                console.warn('Logout API call failed:', error);
            } finally {
                localStorage.removeItem('authToken');
                sessionStorage.removeItem('authToken');
                localStorage.removeItem('refreshToken');
                localStorage.removeItem('user');
                sessionStorage.removeItem('user');
                
                if (typeof notificationCenter !== 'undefined') {
                    notificationCenter.add('auth', 'Logged Out', 
                        'You have been successfully logged out', 'success');
                }
                
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1000);
            }
        }
    }
}

// Auto-initialize when DOM is ready
let joomlaMenu;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        joomlaMenu = new JoomlaMenu();
    });
} else {
    joomlaMenu = new JoomlaMenu();
}
