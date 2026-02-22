/**
 * AthSys Admin API Service
 * Handles all API communications with the backend
 */

class AthSysAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL || (window.location.hostname === 'localhost' 
            ? 'http://localhost:5000' 
            : window.location.origin);
        this.token = localStorage.getItem('authToken');
        this.headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`
        };
    }

    // GET request with error handling
    async get(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'GET',
                headers: this.headers,
                ...options
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`GET ${endpoint} failed:`, error);
            throw error;
        }
    }

    // POST request with error handling
    async post(endpoint, data = {}, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(data),
                ...options
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`POST ${endpoint} failed:`, error);
            throw error;
        }
    }

    // PUT request with error handling
    async put(endpoint, data = {}, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'PUT',
                headers: this.headers,
                body: JSON.stringify(data),
                ...options
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`PUT ${endpoint} failed:`, error);
            throw error;
        }
    }

    // DELETE request with error handling
    async delete(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'DELETE',
                headers: this.headers,
                ...options
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`DELETE ${endpoint} failed:`, error);
            throw error;
        }
    }

    // Handle response and errors
    async handleResponse(response) {
        if (response.status === 401) {
            localStorage.removeItem('authToken');
            window.location.href = 'index.html';
            throw new Error('Unauthorized - please login again');
        }

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw {
                status: response.status,
                message: data.message || `Server error: ${response.status}`,
                data
            };
        }

        return data;
    }

    // ============ DASHBOARD ============
    async getDashboardStats() {
        return this.get('/api/dashboard/stats');
    }

    async getDashboardAnalytics() {
        return this.get('/api/dashboard/analytics');
    }

    // ============ RACES ============
    async getRaces(page = 1, filters = {}) {
        const queryString = new URLSearchParams({ page, ...filters }).toString();
        return this.get(`/api/races?${queryString}`);
    }

    async getRaceById(id) {
        return this.get(`/api/races/${id}`);
    }

    async createRace(data) {
        return this.post('/api/races', data);
    }

    async updateRace(id, data) {
        return this.put(`/api/races/${id}`, data);
    }

    async deleteRace(id) {
        return this.delete(`/api/races/${id}`);
    }

    async bulkDeleteRaces(ids) {
        return this.post('/api/races/bulk/delete', { ids });
    }

    async exportRaces(format = 'csv') {
        return this.get(`/api/races/export?format=${format}`);
    }

    // ============ ATHLETES ============
    async getAthletes(page = 1, filters = {}) {
        const queryString = new URLSearchParams({ page, ...filters }).toString();
        return this.get(`/api/athletes?${queryString}`);
    }

    async getAthleteById(id) {
        return this.get(`/api/athletes/${id}`);
    }

    async createAthlete(data) {
        return this.post('/api/athletes', data);
    }

    async updateAthlete(id, data) {
        return this.put(`/api/athletes/${id}`, data);
    }

    async deleteAthlete(id) {
        return this.delete(`/api/athletes/${id}`);
    }

    async bulkApproveAthletes(ids) {
        return this.post('/api/athletes/bulk/approve', { ids });
    }

    async bulkDeleteAthletes(ids) {
        return this.post('/api/athletes/bulk/delete', { ids });
    }

    async exportAthletes(format = 'csv') {
        return this.get(`/api/athletes/export?format=${format}`);
    }

    // ============ RESULTS ============
    async getResults(page = 1, filters = {}) {
        const queryString = new URLSearchParams({ page, ...filters }).toString();
        return this.get(`/api/results?${queryString}`);
    }

    async getResultById(id) {
        return this.get(`/api/results/${id}`);
    }

    async createResult(data) {
        return this.post('/api/results', data);
    }

    async updateResult(id, data) {
        return this.put(`/api/results/${id}`, data);
    }

    async deleteResult(id) {
        return this.delete(`/api/results/${id}`);
    }

    async bulkDeleteResults(ids) {
        return this.post('/api/results/bulk/delete', { ids });
    }

    async exportResults(format = 'csv') {
        return this.get(`/api/results/export?format=${format}`);
    }

    // ============ USERS ============
    async getUsers(page = 1, filters = {}) {
        const queryString = new URLSearchParams({ page, ...filters }).toString();
        return this.get(`/api/admin/users?${queryString}`);
    }

    async getUserById(id) {
        return this.get(`/api/admin/users/${id}`);
    }

    async createUser(data) {
        return this.post('/api/admin/users', data);
    }

    async updateUser(id, data) {
        return this.put(`/api/admin/users/${id}`, data);
    }

    async deleteUser(id) {
        return this.delete(`/api/admin/users/${id}`);
    }

    async resetUserPassword(id) {
        return this.post(`/api/admin/users/${id}/reset-password`);
    }

    async bulkDeleteUsers(ids) {
        return this.post('/api/admin/users/bulk/delete', { ids });
    }

    // ============ AUDIT LOGS ============
    async getAuditLogs(page = 1, filters = {}) {
        const queryString = new URLSearchParams({ page, ...filters }).toString();
        return this.get(`/api/admin/audit-logs?${queryString}`);
    }

    async getAuditLogsByUser(userId) {
        return this.get(`/api/admin/audit-logs/user/${userId}`);
    }

    // ============ SYSTEM ============
    async getSystemStatus() {
        return this.get('/api/health');
    }

    async getSystemHealth() {
        return this.get('/api/system/health');
    }

    async backupDatabase() {
        return this.post('/api/admin/backup/create');
    }

    async restoreDatabase(backupId) {
        return this.post(`/api/admin/backup/restore/${backupId}`);
    }

    async getBackups() {
        return this.get('/api/admin/backups');
    }

    // ============ NOTIFICATIONS ============
    async getNotifications() {
        return this.get('/api/notifications');
    }

    async markNotificationAsRead(id) {
        return this.post(`/api/notifications/${id}/read`);
    }

    async clearNotifications() {
        return this.post('/api/notifications/clear');
    }

    // ============ SEARCH ============
    async search(query, type = 'all') {
        return this.get(`/api/search?q=${encodeURIComponent(query)}&type=${type}`);
    }
}

// Export for use in Vue components
window.AthSysAPI = AthSysAPI;
