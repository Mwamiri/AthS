// Offline Caching System for AthSys
// Enables the system to work without internet connection

class OfflineCache {
    constructor() {
        this.cacheName = 'athsys-cache-v2.1';
        this.dataCache = 'athsys-data-cache';
        this.maxAge = 24 * 60 * 60 * 1000; // 24 hours
        this.isOnline = navigator.onLine;
        this.init();
    }

    init() {
        // Monitor online/offline status
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.syncWhenOnline();
            console.log('✅ Back online - syncing data...');
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            console.log('⚠️ Offline mode activated');
        });

        // Register service worker if available
        if ('serviceWorker' in navigator) {
            this.registerServiceWorker();
        }

        console.log(`🔧 Offline caching initialized - Status: ${this.isOnline ? 'Online' : 'Offline'}`);
    }

    async registerServiceWorker() {
        try {
            const registration = await navigator.serviceWorker.register('/service-worker.js');
            console.log('Service Worker registered:', registration);
        } catch (error) {
            console.log('Service Worker registration failed:', error);
        }
    }

    // Cache data with timestamp
    setCache(key, data) {
        try {
            const cacheData = {
                data: data,
                timestamp: Date.now(),
                version: '2.1'
            };
            localStorage.setItem(`cache_${key}`, JSON.stringify(cacheData));
            return true;
        } catch (e) {
            console.warn('Cache write failed:', e);
            return false;
        }
    }

    // Get cached data if not expired
    getCache(key, maxAge = this.maxAge) {
        try {
            const cached = localStorage.getItem(`cache_${key}`);
            if (!cached) return null;

            const cacheData = JSON.parse(cached);
            const age = Date.now() - cacheData.timestamp;

            // Return cached data if not expired
            if (age < maxAge) {
                return cacheData.data;
            }

            // Remove expired cache
            this.removeCache(key);
            return null;
        } catch (e) {
            console.warn('Cache read failed:', e);
            return null;
        }
    }

    removeCache(key) {
        try {
            localStorage.removeItem(`cache_${key}`);
        } catch (e) {
            console.warn('Cache remove failed:', e);
        }
    }

    clearAllCache() {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith('cache_')) {
                    localStorage.removeItem(key);
                }
            });
            console.log('🗑️ All cache cleared');
        } catch (e) {
            console.warn('Cache clear failed:', e);
        }
    }

    // Smart fetch - uses cache when offline
    async fetchWithCache(url, options = {}, cacheKey = null) {
        const key = cacheKey || this.urlToKey(url);

        // If offline, return cached data
        if (!this.isOnline) {
            const cached = this.getCache(key);
            if (cached) {
                console.log(`📦 Using cached data for: ${url}`);
                return {
                    ok: true,
                    json: async () => cached,
                    fromCache: true
                };
            } else {
                throw new Error('No internet connection and no cached data available');
            }
        }

        // Online - fetch and cache
        try {
            const response = await fetch(url, options);
            
            if (response.ok && options.method === 'GET' || !options.method) {
                const data = await response.clone().json();
                this.setCache(key, data);
            }
            
            return response;
        } catch (error) {
            // Network error - try cache
            const cached = this.getCache(key);
            if (cached) {
                console.log(`📦 Network error - using cached data for: ${url}`);
                return {
                    ok: true,
                    json: async () => cached,
                    fromCache: true
                };
            }
            throw error;
        }
    }

    urlToKey(url) {
        return url.replace(/[^a-zA-Z0-9]/g, '_');
    }

    // Queue operations for when back online
    queueOperation(operation) {
        try {
            const queue = JSON.parse(localStorage.getItem('operation_queue') || '[]');
            queue.push({
                ...operation,
                timestamp: Date.now(),
                id: Date.now() + Math.random()
            });
            localStorage.setItem('operation_queue', JSON.stringify(queue));
            console.log('📝 Operation queued for sync');
        } catch (e) {
            console.warn('Queue operation failed:', e);
        }
    }

    async syncWhenOnline() {
        try {
            const queue = JSON.parse(localStorage.getItem('operation_queue') || '[]');
            
            if (queue.length === 0) return;

            console.log(`🔄 Syncing ${queue.length} queued operations...`);

            for (const op of queue) {
                try {
                    await fetch(op.url, op.options);
                    console.log(`✅ Synced: ${op.url}`);
                } catch (e) {
                    console.warn(`❌ Sync failed: ${op.url}`, e);
                }
            }

            // Clear queue after sync
            localStorage.setItem('operation_queue', '[]');
            
            if (typeof notificationCenter !== 'undefined') {
                notificationCenter.add('system', 'Data Synced', 
                    `Successfully synced ${queue.length} operations`, 'success');
            }
        } catch (e) {
            console.warn('Sync failed:', e);
        }
    }

    // Get cache statistics
    getCacheStats() {
        try {
            const keys = Object.keys(localStorage);
            const cacheKeys = keys.filter(k => k.startsWith('cache_'));
            
            let totalSize = 0;
            const items = [];

            cacheKeys.forEach(key => {
                const value = localStorage.getItem(key);
                const size = new Blob([value]).size;
                totalSize += size;
                
                try {
                    const parsed = JSON.parse(value);
                    items.push({
                        key: key.replace('cache_', ''),
                        size: (size / 1024).toFixed(2) + ' KB',
                        age: this.formatAge(Date.now() - parsed.timestamp)
                    });
                } catch (e) {}
            });

            return {
                itemCount: cacheKeys.length,
                totalSize: (totalSize / 1024).toFixed(2) + ' KB',
                items: items,
                online: this.isOnline
            };
        } catch (e) {
            return { error: e.message };
        }
    }

    formatAge(ms) {
        const minutes = Math.floor(ms / 60000);
        if (minutes < 60) return `${minutes} min`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours} hours`;
        const days = Math.floor(hours / 24);
        return `${days} days`;
    }
}

// Initialize offline cache globally
const offlineCache = new OfflineCache();

// Enhanced fetch function that uses cache
async function fetchWithCache(url, options = {}) {
    return await offlineCache.fetchWithCache(url, options);
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { OfflineCache, offlineCache, fetchWithCache };
}
