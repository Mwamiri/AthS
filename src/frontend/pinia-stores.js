// Frontend State Management with Pinia
// Enterprise-grade state management for scalable frontend

// Installation: npm install pinia
// Usage: See pinia-setup.js for initialization

// 1. Auth Store - Centralized authentication state
const authStore = {
  state: {
    user: null,
    token: null,
    isAuthenticated: false,
    loading: false,
    error: null
  },
  
  actions: {
    async login(email, password) {
      this.loading = true;
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        
        if (!response.ok) throw new Error('Login failed');
        
        const data = await response.json();
        this.token = data.token;
        this.user = data.user;
        this.isAuthenticated = true;
        localStorage.setItem('authToken', data.token);
        
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async logout() {
      await logoutWithRevocation({ redirectTo: null });
      this.user = null;
      this.token = null;
      this.isAuthenticated = false;
    },
    
    async refreshToken() {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${this.token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        this.token = data.token;
        localStorage.setItem('authToken', data.token);
      }
    },
    
    restoreAuth() {
      const token = localStorage.getItem('authToken');
      if (token) {
        this.token = token;
        this.isAuthenticated = true;
      }
    }
  },
  
  getters: {
    isAdmin: (state) => state.user?.role === 'admin',
    isAuthorized: (state) => (roles) => roles.includes(state.user?.role)
  }
};

// 2. Dashboard Store - Dashboard data and statistics
const dashboardStore = {
  state: {
    stats: {
      totalRaces: 0,
      totalAthletes: 0,
      totalResults: 0,
      activeUsers: 0
    },
    races: [],
    athletes: [],
    recentResults: [],
    loading: false,
    error: null,
    lastUpdated: null
  },
  
  actions: {
    async loadStats() {
      this.loading = true;
      try {
        const response = await fetch('/api/dashboard/stats', {
          headers: { 'Authorization': `Bearer ${authStore.state.token}` }
        });
        
        if (!response.ok) throw new Error('Failed to load stats');
        
        const data = await response.json();
        this.stats = data.data;
        this.lastUpdated = new Date();
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },
    
    async loadRaces(page = 1) {
      try {
        const response = await fetch(`/api/races?page=${page}`, {
          headers: { 'Authorization': `Bearer ${authStore.state.token}` }
        });
        
        if (!response.ok) throw new Error('Failed to load races');
        
        const data = await response.json();
        this.races = data.data;
      } catch (error) {
        this.error = error.message;
      }
    },
    
    async loadAthletes(page = 1) {
      try {
        const response = await fetch(`/api/athletes?page=${page}`, {
          headers: { 'Authorization': `Bearer ${authStore.state.token}` }
        });
        
        if (!response.ok) throw new Error('Failed to load athletes');
        
        const data = await response.json();
        this.athletes = data.data;
      } catch (error) {
        this.error = error.message;
      }
    },
    
    // Auto-refresh stats every 30 seconds
    startAutoRefresh(interval = 30000) {
      setInterval(() => this.loadStats(), interval);
    }
  }
};

// 3. UI Store - UI state and notifications
const uiStore = {
  state: {
    sidebarExpanded: true,
    theme: 'light',
    notifications: [],
    activeMenu: 'dashboard'
  },
  
  actions: {
    toggleSidebar() {
      this.sidebarExpanded = !this.sidebarExpanded;
      localStorage.setItem('sidebarExpanded', this.sidebarExpanded);
    },
    
    setTheme(theme) {
      this.theme = theme;
      localStorage.setItem('theme', theme);
      document.documentElement.setAttribute('data-theme', theme);
    },
    
    addNotification(notification) {
      const id = Date.now();
      const notif = { id, ...notification };
      this.notifications.push(notif);
      
      // Auto-remove after 5 seconds
      if (!notification.persistent) {
        setTimeout(() => {
          this.removeNotification(id);
        }, 5000);
      }
      
      return id;
    },
    
    removeNotification(id) {
      this.notifications = this.notifications.filter(n => n.id !== id);
    },
    
    setActiveMenu(menu) {
      this.activeMenu = menu;
    }
  }
};

// 4. Data Store - Cached data management
const dataStore = {
  state: {
    cache: {},
    lastSync: {},
    syncInProgress: {}
  },
  
  actions: {
    setCacheData(key, data, ttl = 300000) {
      this.cache[key] = {
        data,
        expiry: Date.now() + ttl
      };
      this.lastSync[key] = new Date();
    },
    
    getCacheData(key) {
      const cached = this.cache[key];
      if (!cached) return null;
      
      if (Date.now() > cached.expiry) {
        delete this.cache[key];
        return null;
      }
      
      return cached.data;
    },
    
    invalidateCache(key) {
      delete this.cache[key];
      delete this.lastSync[key];
    },
    
    isSyncing(key) {
      return this.syncInProgress[key] || false;
    },
    
    setSyncing(key, value) {
      this.syncInProgress[key] = value;
    }
  }
};

// 5. API Client Store - Centralized API calls
const apiStore = {
  baseURL: '/api',
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authStore.state.token}`,
      ...options.headers
    };
    
    try {
      const response = await fetch(url, {
        ...options,
        headers
      });
      
      if (response.status === 401) {
        // Token expired, try refresh
        await authStore.actions.refreshToken();
        headers['Authorization'] = `Bearer ${authStore.state.token}`;
        return fetch(url, { ...options, headers });
      }
      
      if (!response.ok) {
        const error = await response.json();
        throw error;
      }
      
      return response.json();
    } catch (error) {
      uiStore.actions.addNotification({
        type: 'error',
        message: error.error || 'API request failed'
      });
      throw error;
    }
  },
  
  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },
  
  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  
  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },
  
  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
};

// Export stores
const stores = {
  auth: authStore,
  dashboard: dashboardStore,
  ui: uiStore,
  data: dataStore,
  api: apiStore
};

// initialize with this in main app
function initializeStores() {
  authStore.actions.restoreAuth();
  uiStore.setTheme(localStorage.getItem('theme') || 'light');
  if (localStorage.getItem('sidebarExpanded') !== null) {
    if (localStorage.getItem('sidebarExpanded') === 'false') {
      uiStore.actions.toggleSidebar();
    }
  }
}
