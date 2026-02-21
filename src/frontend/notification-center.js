// Notification Center with Activity Tracking
// Handles real-time notifications, activity logging, and user alerts

class NotificationCenter {
    constructor() {
        this.notifications = this.loadFromStorage();
        this.maxNotifications = 50;
        this.isOpen = false;
        this.unreadCount = this.notifications.filter(n => !n.read).length;
        this.init();
    }

    init() {
        this.createNotificationCenter();
        this.updateBadge();
        
        // Check for stored notifications on load
        if (this.notifications.length > 0) {
            this.updateBadge();
        }
        
        // Listen for online/offline events
        window.addEventListener('online', () => {
            this.add('system', 'Back Online', 'Internet connection restored', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.add('system', 'Offline Mode', 'Operating in offline mode', 'warning');
        });
    }

    createNotificationCenter() {
        // Create notification bell button
        const bellButton = document.createElement('button');
        bellButton.id = 'notification-bell';
        bellButton.className = 'notification-bell';
        bellButton.innerHTML = `
            <span class="bell-icon">🔔</span>
            <span class="notification-badge" id="notif-badge" style="display: none;">0</span>
        `;
        bellButton.onclick = () => this.toggle();

        // Create notification panel
        const panel = document.createElement('div');
        panel.id = 'notification-panel';
        panel.className = 'notification-panel';
        panel.innerHTML = `
            <div class="notification-header">
                <h3>🔔 Notifications</h3>
                <div class="notification-actions">
                    <button onclick="notificationCenter.markAllAsRead()" class="notif-action-btn">
                        ✓ Mark All Read
                    </button>
                    <button onclick="notificationCenter.clearAll()" class="notif-action-btn">
                        🗑️ Clear All
                    </button>
                </div>
            </div>
            <div class="notification-tabs">
                <button class="notif-tab active" data-filter="all" onclick="notificationCenter.filterNotifications('all')">
                    All
                </button>
                <button class="notif-tab" data-filter="unread" onclick="notificationCenter.filterNotifications('unread')">
                    Unread <span id="unread-count-tab">(${this.unreadCount})</span>
                </button>
                <button class="notif-tab" data-filter="system" onclick="notificationCenter.filterNotifications('system')">
                    System
                </button>
            </div>
            <div class="notification-list" id="notification-list">
                ${this.renderNotifications()}
            </div>
        `;

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .notification-bell {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                background: linear-gradient(135deg, var(--primary-color), var(--danger-color));
                border: none;
                border-radius: 50%;
                width: 56px;
                height: 56px;
                cursor: pointer;
                box-shadow: 0 4px 16px rgba(0,0,0,0.2);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .notification-bell:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }
            
            .bell-icon {
                font-size: 1.5rem;
            }
            
            .notification-badge {
                position: absolute;
                top: -5px;
                right: -5px;
                background: var(--danger-color);
                color: white;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.75rem;
                font-weight: 700;
                border: 2px solid var(--background-color);
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            .notification-panel {
                position: fixed;
                top: 90px;
                right: 20px;
                width: 420px;
                max-height: 600px;
                background: var(--card-bg);
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                z-index: 9998;
                display: none;
                flex-direction: column;
                animation: slideIn 0.3s ease;
            }
            
            .notification-panel.open {
                display: flex;
            }
            
            .notification-header {
                padding: 1.5rem;
                border-bottom: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .notification-header h3 {
                margin: 0;
                font-size: 1.25rem;
            }
            
            .notification-actions {
                display: flex;
                gap: 0.5rem;
            }
            
            .notif-action-btn {
                padding: 0.5rem;
                background: rgba(6, 214, 160, 0.1);
                border: 1px solid var(--success-color);
                border-radius: 6px;
                color: var(--success-color);
                cursor: pointer;
                font-size: 0.75rem;
                transition: all 0.2s;
            }
            
            .notif-action-btn:hover {
                background: var(--success-color);
                color: white;
            }
            
            .notification-tabs {
                display: flex;
                border-bottom: 1px solid var(--border-color);
                padding: 0 1.5rem;
            }
            
            .notif-tab {
                padding: 0.75rem 1rem;
                background: none;
                border: none;
                border-bottom: 2px solid transparent;
                cursor: pointer;
                font-weight: 600;
                color: var(--text-secondary);
                transition: all 0.2s;
            }
            
            .notif-tab.active {
                color: var(--primary-color);
                border-bottom-color: var(--primary-color);
            }
            
            .notification-list {
                flex: 1;
                overflow-y: auto;
                padding: 0.5rem;
            }
            
            .notification-item {
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: 8px;
                background: rgba(255,255,255,0.05);
                border-left: 4px solid var(--primary-color);
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .notification-item:hover {
                background: rgba(255,255,255,0.1);
                transform: translateX(4px);
            }
            
            .notification-item.unread {
                background: rgba(6, 214, 160, 0.1);
                border-left-color: var(--success-color);
            }
            
            .notification-item.warning {
                border-left-color: var(--accent-color);
            }
            
            .notification-item.error {
                border-left-color: var(--danger-color);
            }
            
            .notification-title {
                font-weight: 600;
                margin-bottom: 0.25rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .notification-message {
                font-size: 0.9rem;
                color: var(--text-secondary);
                margin-bottom: 0.5rem;
            }
            
            .notification-time {
                font-size: 0.75rem;
                color: var(--text-secondary);
                opacity: 0.7;
            }
            
            .empty-notifications {
                text-align: center;
                padding: 3rem 2rem;
                color: var(--text-secondary);
            }
            
            .empty-notifications .empty-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
                opacity: 0.5;
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(bellButton);
        document.body.appendChild(panel);
        
        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('notification-panel');
            const bell = document.getElementById('notification-bell');
            if (this.isOpen && !panel.contains(e.target) && !bell.contains(e.target)) {
                this.toggle();
            }
        });
    }

    add(type, title, message, severity = 'info') {
        const notification = {
            id: Date.now(),
            type,
            title,
            message,
            severity,
            timestamp: new Date().toISOString(),
            read: false
        };
        
        this.notifications.unshift(notification);
        
        // Limit stored notifications
        if (this.notifications.length > this.maxNotifications) {
            this.notifications = this.notifications.slice(0, this.maxNotifications);
        }
        
        this.unreadCount++;
        this.saveToStorage();
        this.updateBadge();
        this.renderNotifications();
        
        // Auto-open for errors
        if (severity === 'error' && !this.isOpen) {
            setTimeout(() => this.toggle(), 300);
        }
    }

    markAsRead(id) {
        const notif = this.notifications.find(n => n.id === id);
        if (notif && !notif.read) {
            notif.read = true;
            this.unreadCount--;
            this.saveToStorage();
            this.updateBadge();
            this.renderNotifications();
        }
    }

    markAllAsRead() {
        this.notifications.forEach(n => n.read = true);
        this.unreadCount = 0;
        this.saveToStorage();
        this.updateBadge();
        this.renderNotifications();
    }

    clearAll() {
        if (confirm('Clear all notifications?')) {
            this.notifications = [];
            this.unreadCount = 0;
            this.saveToStorage();
            this.updateBadge();
            this.renderNotifications();
        }
    }

    toggle() {
        this.isOpen = !this.isOpen;
        const panel = document.getElementById('notification-panel');
        panel.classList.toggle('open', this.isOpen);
    }

    filterNotifications(filter) {
        // Update active tab
        document.querySelectorAll('.notif-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.filter === filter);
        });
        
        this.renderNotifications(filter);
    }

    renderNotifications(filter = 'all') {
        let filtered = this.notifications;
        
        if (filter === 'unread') {
            filtered = this.notifications.filter(n => !n.read);
        } else if (filter !== 'all') {
            filtered = this.notifications.filter(n => n.type === filter);
        }
        
        const list = document.getElementById('notification-list');
        if (!list) return '';
        
        if (filtered.length === 0) {
            list.innerHTML = `
                <div class="empty-notifications">
                    <div class="empty-icon">🔕</div>
                    <p>No notifications</p>
                </div>
            `;
            return;
        }
        
        list.innerHTML = filtered.map(notif => {
            const timeAgo = this.timeAgo(notif.timestamp);
            const unreadClass = notif.read ? '' : 'unread';
            const severityClass = notif.severity;
            
            return `
                <div class="notification-item ${unreadClass} ${severityClass}" 
                     onclick="notificationCenter.markAsRead(${notif.id})">
                    <div class="notification-title">
                        <span>${notif.title}</span>
                        ${!notif.read ? '<span style="color: var(--success-color);">●</span>' : ''}
                    </div>
                    <div class="notification-message">${notif.message}</div>
                    <div class="notification-time">${timeAgo}</div>
                </div>
            `;
        }).join('');
        
        // Update unread count in tab
        const unreadTab = document.getElementById('unread-count-tab');
        if (unreadTab) {
            unreadTab.textContent = `(${this.unreadCount})`;
        }
    }

    updateBadge() {
        const badge = document.getElementById('notif-badge');
        if (badge) {
            if (this.unreadCount > 0) {
                badge.style.display = 'flex';
                badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            } else {
                badge.style.display = 'none';
            }
        }
    }

    timeAgo(timestamp) {
        const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
        
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`;
        
        return new Date(timestamp).toLocaleDateString();
    }

    saveToStorage() {
        try {
            localStorage.setItem('athsys_notifications', JSON.stringify(this.notifications));
        } catch (e) {
            console.warn('Could not save notifications:', e);
        }
    }

    loadFromStorage() {
        try {
            const stored = localStorage.getItem('athsys_notifications');
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            console.warn('Could not load notifications:', e);
            return [];
        }
    }
}

// Initialize notification center globally
let notificationCenter;
window.addEventListener('DOMContentLoaded', () => {
    notificationCenter = new NotificationCenter();
    
    // Add welcome notification
    notificationCenter.add('system', 'Welcome to AthSys v2.1', 
        'Real-time dashboard with offline support enabled', 'success');
});
