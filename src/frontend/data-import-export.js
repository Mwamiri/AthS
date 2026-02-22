/**
 * Data Import/Export Service for AthSys Admin Dashboard
 * Handles bulk data operations with progress tracking and error handling
 */

class DataImportExportService {
    constructor(baseURL = '') {
        this.baseURL = baseURL || (window.location.hostname === 'localhost' 
            ? 'http://localhost:5000' 
            : window.location.origin);
        this.token = localStorage.getItem('authToken');
        this.headers = {
            'Authorization': `Bearer ${this.token}`
        };
        this.uploadProgress = 0;
        this.importInProgress = false;
    }

    // ==================== DATABASE HEALTH CHECK ====================
    
    async checkDatabaseHealth() {
        """Check database connectivity and health status"""
        try {
            const response = await fetch(`${this.baseURL}/api/admin/database/health`, {
                headers: this.headers
            });
            return await response.json();
        } catch (error) {
            console.error('Database health check failed:', error);
            return {
                status: 'error',
                message: 'Could not reach database',
                health: { status: 'unhealthy', connected: false }
            };
        }
    }

    async validateDatabase() {
        """Validate database schema and connectivity"""
        try {
            const response = await fetch(`${this.baseURL}/api/admin/database/validate`, {
                method: 'POST',
                headers: this.headers
            });
            return await response.json();
        } catch (error) {
            console.error('Database validation failed:', error);
            throw error;
        }
    }

    async initializeDatabase() {
        """Initialize database tables if not exists"""
        try {
            const response = await fetch(`${this.baseURL}/api/admin/database/initialize`, {
                method: 'POST',
                headers: this.headers
            });
            return await response.json();
        } catch (error) {
            console.error('Database initialization failed:', error);
            throw error;
        }
    }

    // ==================== IMPORT OPERATIONS ====================
    
    async importAthletesCsv(csvContent, onProgress = null) {
        """Import athletes from CSV content"""
        try {
            this.importInProgress = true;
            
            // Create FormData for file upload
            const formData = new FormData();
            const blob = new Blob([csvContent], { type: 'text/csv' });
            formData.append('file', blob, 'athletes.csv');
            
            const response = await fetch(`${this.baseURL}/api/admin/import/athletes-csv`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                    // Note: Don't set Content-Type for FormData - browser sets it automatically
                },
                body: formData
            });
            
            const result = await response.json();
            this.importInProgress = false;
            
            if (onProgress) {
                onProgress({
                    total: result.imported + result.failed,
                    imported: result.imported,
                    failed: result.failed,
                    errors: result.errors
                });
            }
            
            return result;
        } catch (error) {
            this.importInProgress = false;
            console.error('CSV import failed:', error);
            throw error;
        }
    }

    async importRacesJson(racesData, onProgress = null) {
        """Import races from JSON"""
        try {
            this.importInProgress = true;
            
            const response = await fetch(`${this.baseURL}/api/admin/import/races-json`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(racesData)
            });
            
            const result = await response.json();
            this.importInProgress = false;
            
            if (onProgress) {
                onProgress({
                    total: result.imported + result.failed,
                    imported: result.imported,
                    failed: result.failed
                });
            }
            
            return result;
        } catch (error) {
            this.importInProgress = false;
            console.error('JSON import failed:', error);
            throw error;
        }
    }

    async importBulkJson(bulkData, onProgress = null) {
        """Bulk import multiple data types"""
        try {
            this.importInProgress = true;
            
            const response = await fetch(`${this.baseURL}/api/admin/import/bulk-json`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(bulkData)
            });
            
            const result = await response.json();
            this.importInProgress = false;
            
            if (onProgress) {
                onProgress({
                    total: result.total_imported + result.total_failed,
                    imported: result.total_imported,
                    failed: result.total_failed,
                    breakdown: result.results
                });
            }
            
            return result;
        } catch (error) {
            this.importInProgress = false;
            console.error('Bulk import failed:', error);
            throw error;
        }
    }

    // ==================== EXPORT OPERATIONS ====================
    
    async exportAthletesCsv() {
        """Export all athletes as CSV"""
        try {
            const response = await fetch(`${this.baseURL}/api/admin/export/athletes-csv`, {
                headers: this.headers
            });
            
            if (!response.ok) throw new Error('Export failed');
            
            const blob = await response.blob();
            this.downloadFile(blob, 'athletes.csv');
            
            return { status: 'success', message: 'Athletes exported' };
        } catch (error) {
            console.error('Athletes export failed:', error);
            throw error;
        }
    }

    async exportRacesCsv() {
        """Export all races as CSV"""
        try {
            const response = await fetch(`${this.baseURL}/api/admin/export/races-csv`, {
                headers: this.headers
            });
            
            if (!response.ok) throw new Error('Export failed');
            
            const blob = await response.blob();
            this.downloadFile(blob, 'races.csv');
            
            return { status: 'success', message: 'Races exported' };
        } catch (error) {
            console.error('Races export failed:', error);
            throw error;
        }
    }

    async exportAllJson() {
        """Export all data as JSON"""
        try {
            const response = await fetch(`${this.baseURL}/api/admin/export/all-json`, {
                headers: this.headers
            });
            
            const result = await response.json();
            
            // Save as file
            const blob = new Blob([JSON.stringify(result.data, null, 2)], { type: 'application/json' });
            this.downloadFile(blob, `athsys_backup_${new Date().toISOString().split('T')[0]}.json`);
            
            return result;
        } catch (error) {
            console.error('JSON export failed:', error);
            throw error;
        }
    }

    // ==================== IMPORT TEMPLATES ====================
    
    async getAthletesImportTemplate() {
        """Get CSV template for athletes import"""
        try {
            const response = await fetch(`${this.baseURL}/api/admin/import/athletes-template`, {
                headers: this.headers
            });
            return await response.json();
        } catch (error) {
            console.error('Template fetch failed:', error);
            throw error;
        }
    }

    async getRacesImportTemplate() {
        """Get JSON template for races import"""
        try {
            const response = await fetch(`${this.baseURL}/api/admin/import/races-template`, {
                headers: this.headers
            });
            return await response.json();
        } catch (error) {
            console.error('Template fetch failed:', error);
            throw error;
        }
    }

    async getBulkImportTemplate() {
        """Get JSON template for bulk import"""
        try {
            const response = await fetch(`${this.baseURL}/api/admin/import/bulk-template`, {
                headers: this.headers
            });
            return await response.json();
        } catch (error) {
            console.error('Template fetch failed:', error);
            throw error;
        }
    }

    // ==================== HELPER METHODS ====================
    
    downloadFile(blob, filename) {
        """Download blob as file"""
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }

    csvToJson(csvContent) {
        """Convert CSV content to JSON array"""
        const lines = csvContent.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        
        const data = [];
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            const obj = {};
            
            headers.forEach((header, index) => {
                obj[header] = values[index] || null;
            });
            
            data.push(obj);
        }
        
        return data;
    }

    jsonToCsv(jsonArray, headers = null) {
        """Convert JSON array to CSV content"""
        if (!jsonArray || jsonArray.length === 0) {
            return '';
        }
        
        // Get headers from first object or use provided headers
        const cols = headers || Object.keys(jsonArray[0]);
        
        // Create header row
        let csv = cols.join(',') + '\n';
        
        // Create data rows
        for (let obj of jsonArray) {
            const row = cols.map(col => {
                const value = obj[col] || '';
                // Escape quotes and wrap in quotes if contains comma
                return typeof value === 'string' && value.includes(',') 
                    ? `"${value.replace(/"/g, '""')}"` 
                    : value;
            });
            csv += row.join(',') + '\n';
        }
        
        return csv;
    }

    // ==================== VALIDATION ====================
    
    validateAthleteData(athlete) {
        """Validate athlete object"""
        const errors = [];
        
        if (!athlete.name || athlete.name.trim() === '') {
            errors.push('Name is required');
        }
        if (!athlete.country || athlete.country.trim() === '') {
            errors.push('Country is required');
        }
        if (athlete.email && !this.isValidEmail(athlete.email)) {
            errors.push('Invalid email format');
        }
        
        return errors;
    }

    validateRaceData(race) {
        """Validate race object"""
        const errors = [];
        
        if (!race.name || race.name.trim() === '') {
            errors.push('Race name is required');
        }
        if (!race.date) {
            errors.push('Date is required');
        }
        if (!race.location || race.location.trim() === '') {
            errors.push('Location is required');
        }
        
        return errors;
    }

    isValidEmail(email) {
        """Validate email format"""
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // ==================== FILE HANDLING ====================
    
    readFileAsText(file) {
        """Read uploaded file as text"""
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file);
        });
    }

    readFileAsJson(file) {
        """Read uploaded JSON file"""
        return new Promise((resolve, reject) => {
            this.readFileAsText(file)
                .then(content => {
                    try {
                        resolve(JSON.parse(content));
                    } catch (error) {
                        reject(new Error('Invalid JSON: ' + error.message));
                    }
                })
                .catch(reject);
        });
    }

    // ==================== SYNC & STATUS ====================
    
    async getSyncStatus() {
        """Get data synchronization status"""
        try {
            const response = await fetch(`${this.baseURL}/api/admin/sync/status`, {
                headers: this.headers
            });
            return await response.json();
        } catch (error) {
            console.error('Sync status failed:', error);
            throw error;
        }
    }
}

// Export service globally
window.DataImportExportService = DataImportExportService;
