# 🔗 Backend Database Connectivity & Import/Export Guide

## Overview

Complete guide for connecting all frontend files to the enhanced backend with robust database operations, imports, and exports.

---

## 📊 Database Architecture

### Connection Flow
```
Frontend (JavaScript)
    ↓
API Service Layer (api-service.js + data-import-export.js)
    ↓
Flask Backend (app.py + import_export_api.py)
    ↓
Database Validator (db_validator.py)
    ↓
PostgreSQL Database
    ↓
Redis Cache (optional)
```

### Database Components
```
Backend Files:
✅ src/backend/config.py              - Database configuration
✅ src/backend/models.py              - ORM models (tables)
✅ src/backend/app.py                 - Flask routes & endpoints
✅ src/backend/db_validator.py        - NEW: Database health & validation
✅ src/backend/import_export_api.py   - NEW: Import/export endpoints

Frontend Files:
✅ src/frontend/api-service.js        - API communication
✅ src/frontend/data-import-export.js - NEW: Import/export operations
✅ src/frontend/admin-pro.html        - Dashboard UI
```

---

## 🔌 Connection Checklist

### 1. Backend Setup

#### Step 1: Install Dependencies
```bash
cd src/backend
pip install -r requirements.txt
```

Key packages:
- `psycopg2-binary` - PostgreSQL adapter
- `SQLAlchemy` - ORM
- `redis` - Caching
- `Flask` - API framework

#### Step 2: Configure Database Connection
Edit or create `.env` file:
```env
# Database
DATABASE_URL=postgresql://athsys_user:athsys_pass@localhost:5432/athsys_db
SQLALCHEMY_ECHO=False

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
```

#### Step 3: Initialize Database
```bash
python src/backend/init_db.py
```

Output should show:
```
========================================
✅ DATABASE READY FOR OPERATION
========================================
```

#### Step 4: Verify Database Health
```python
# Interactive test
python -c "
from db_validator import setup_database_with_validation
setup_database_with_validation()
"
```

#### Step 5: Register Import/Export Blueprint
Update `src/backend/app.py` around line 100:

```python
# Add to imports
from import_export_api import register_import_export_blueprint

# Add after creating Flask app (around line 50)
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# Register blueprints (around line 120)
register_import_export_blueprint(app)  # NEW: Add this line
```

### 2. Frontend Setup

#### Step 1: Include Service Files in HTML
Add to `src/frontend/admin-pro.html` in `<head>` section:

```html
<!-- After existing script tags -->
<script src="api-service.js"></script>
<script src="data-import-export.js"></script>
```

#### Step 2: Initialize Services in Vue App
Add to admin-pro.html Vue data():

```javascript
data() {
    return {
        // Existing data...
        api: new AthSysAPI(),
        importService: new DataImportExportService(),
        // Import/Export UI state
        showImportModal: false,
        importFile: null,
        importProgress: { imported: 0, failed: 0, total: 0 },
        databaseHealth: { status: 'checking', connected: false }
    }
}
```

#### Step 3: Add Methods for Import/Export
```javascript
// In Vue methods:
async performImport() {
    if (!this.importFile) {
        this.addNotification('Please select a file', 'Import', 'warning');
        return;
    }
    
    try {
        this.importInProgress = true;
        const content = await this.importService.readFileAsText(this.importFile);
        
        const result = await this.importService.importAthletesCsv(content, (progress) => {
            this.importProgress = progress;
        });
        
        if (result.failed === 0) {
            this.addNotification(`✅ Imported ${result.imported} athletes`, 'Import Success', 'success');
        } else {
            this.addNotification(`⚠️ Partial import: ${result.imported} success, ${result.failed} failed`, 'Import Complete', 'warning');
        }
    } catch (error) {
        this.addNotification(`❌ Import failed: ${error.message}`, 'Import Error', 'error');
    } finally {
        this.importInProgress = false;
    }
}
```

### 3. Test Connectivity

#### Test 1: Check Backend is Running
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "checks": {
    "database": "operational",
    "cache": "active"
  }
}
```

#### Test 2: Check Database Connection
```bash
curl http://localhost:5000/api/admin/database/health
```

Expected response:
```json
{
  "status": "healthy",
  "connected": true,
  "tables": {
    "users": true,
    "athletes": true,
    "races": true,
    ...
  },
  "record_counts": {
    "users": 7,
    "athletes": 5,
    ...
  }
}
```

#### Test 3: Test Frontend Connection
In browser console:
```javascript
// Test API service
const api = new AthSysAPI();
api.getRaces().then(races => console.log('✅ API works:', races));

// Test import service
const importService = new DataImportExportService();
importService.checkDatabaseHealth().then(health => console.log('✅ Database:', health));
```

---

## 📥 Import Operations

### 1. Import Athletes from CSV

#### Format
```csv
name,country,gender,email,phone,club,coach,bib_number
John Kipchoge,KEN,M,john@example.com,+254700000000,Elite Runners,Coach Ali,101
Mary Kipchoge,KEN,F,mary@example.com,+254700000001,Elite Runners,Coach Ali,102
```

#### JavaScript
```javascript
const importService = new DataImportExportService();

// Read file
const file = document.getElementById('csvInput').files[0];
const csvContent = await importService.readFileAsText(file);

// Import with progress tracking
const result = await importService.importAthletesCsv(csvContent, (progress) => {
    console.log(`Imported: ${progress.imported}/${progress.total}`);
});

console.log(result);
// Output: { status: 'success', imported: 50, failed: 2, errors: [...] }
```

#### cURL
```bash
curl -X POST http://localhost:5000/api/admin/import/athletes-csv \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@athletes.csv"
```

### 2. Import Races from JSON

#### Format
```json
{
  "races": [
    {
      "name": "Olympic Marathon",
      "date": "2026-08-15",
      "location": "Paris, France",
      "status": "scheduled"
    },
    {
      "name": "100m Sprint",
      "date": "2026-08-16",
      "location": "Paris, France",
      "status": "scheduled"
    }
  ]
}
```

#### JavaScript
```javascript
const importService = new DataImportExportService();

const racesData = {
    races: [
        {
            name: 'Marathon',
            date: '2026-08-15',
            location: 'Paris',
            status: 'scheduled'
        }
    ]
};

const result = await importService.importRacesJson(racesData);
console.log(result); // status, imported, failed, errors
```

#### cURL
```bash
curl -X POST http://localhost:5000/api/admin/import/races-json \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @races.json
```

### 3. Bulk Import Multiple Data Types

#### Format
```json
{
  "users": [
    {
      "name": "Admin User",
      "email": "admin@example.com",
      "role": "admin",
      "password": "SecurePass@123"
    }
  ],
  "athletes": [...],
  "races": [...],
  "events": [...]
}
```

#### JavaScript
```javascript
const importService = new DataImportExportService();

const bulkData = {
    users: [
        { name: 'Admin', email: 'admin@example.com', role: 'admin', password: 'Pass@123' }
    ],
    athletes: [
        { name: 'John', country: 'KEN', gender: 'M', email: 'john@example.com' }
    ],
    races: [
        { name: 'Marathon', date: '2026-08-15', location: 'Paris', status: 'scheduled' }
    ]
};

const result = await importService.importBulkJson(bulkData, (progress) => {
    console.log(`Progress:`, progress);
});
```

---

## 📤 Export Operations

### 1. Export Athletes as CSV
```javascript
const importService = new DataImportExportService();
await importService.exportAthletesCsv();
// File: athletes_YYYYMMDD_HHMMSS.csv is downloaded
```

### 2. Export Races as CSV
```javascript
const importService = new DataImportExportService();
await importService.exportRacesCsv();
```

### 3. Export All Data as JSON
```javascript
const importService = new DataImportExportService();
const allData = await importService.exportAllJson();
// File: athsys_backup_YYYY-MM-DD.json is downloaded
```

---

## 🔍 Database Health Monitoring

### Check Health
```javascript
const importService = new DataImportExportService();

const health = await importService.checkDatabaseHealth();
console.log(health);

// Output:
// {
//   "health_check": {
//     "status": "healthy",
//     "connected": true,
//     "tables": { "users": true, "athletes": true, ... },
//     "record_counts": { "users": 7, "athletes": 5, ... }
//   },
//   "timestamp": "2026-02-22T12:34:56.789Z"
// }
```

### Validate Database
```javascript
const result = await importService.validateDatabase();

// Field by field validation output
if (!result.connection) {
    console.error('❌ Cannot connect to database');
    // Retry initialization
    await importService.initializeDatabase();
}
```

### Initialize Database
```javascript
const result = await importService.initializeDatabase();

if (result.status === 'success') {
    console.log('✅ Database initialized');
    console.log('Tables created:', result.tables_created);
}
```

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to database"

**Cause**: PostgreSQL not running or credentials wrong

**Solution**:
```bash
# Check PostgreSQL status
sudo service postgresql status

# Start PostgreSQL
sudo service postgresql start

# Verify connection
psql -U athsys_user -d athsys_db -h localhost

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

### Issue: "Table does not exist"

**Cause**: Database schema not initialized

**Solution**:
```bash
# Initialize database
python src/backend/init_db.py

# Verify tables
python -c "
from db_validator import DatabaseValidator
validator = DatabaseValidator()
validator.connect()
print(validator.verify_tables())
"
```

### Issue: "Unauthorized (401)" on import

**Cause**: Missing or invalid authentication token

**Solution**:
```javascript
// Check token
console.log('Token:', localStorage.getItem('authToken'));

// Login first
await fetch('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({
        email: 'admin@athsys.com',
        password: 'Admin@123'
    })
})
.then(r => r.json())
.then(data => {
    localStorage.setItem('authToken', data.token);
    location.reload();
});
```

### Issue: "Invalid CSV format"

**Cause**: Headers don't match expected columns

**Solution**: Use template from API
```javascript
const template = await importService.getAthletesImportTemplate();
console.log('Expected headers:', template.template.headers);
console.log('Sample data:', template.template.sample_data);
```

### Issue: Import fails silently

**Cause**: Server logs not being checked

**Solution**:
```bash
# Check backend logs
tail -f logs/athsys.json

# Or check Flask debug mode
FLASK_ENV=development python src/backend/app.py
```

---

## 📋 Connection Verification Checklist

- [ ] PostgreSQL is running (`sudo service postgresql status`)
- [ ] Database exists (`psql -l | grep athsys`)
- [ ] Backend is running (`curl http://localhost:5000/health`)
- [ ] `/api/admin/database/health` returns healthy status
- [ ] Frontend includes `api-service.js` and `data-import-export.js`
- [ ] localStorage has valid `authToken` and `user`
- [ ] Import/export endpoints are registered in Flask
- [ ] Test import with sample file succeeds
- [ ] Test export creates file successfully
- [ ] All CRUD operations work (Create, Read, Update, Delete)

---

## 🚀 Production Deployment

### Database Backup Before Deployment
```bash
# Export all data
curl -X GET http://localhost:5000/api/admin/export/all-json \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" > backup.json

# Or use PostgreSQL native backup
pg_dump athsys_db > athsys_backup_$(date +%Y%m%d).sql
```

### Connection String for Different Environments

**Development**:
```
postgresql://athsys_user:athsys_pass@localhost:5432/athsys_db
```

**Docker**:
```
postgresql://athsys_user:athsys_pass@db:5432/athsys_db
```

**AWS RDS**:
```
postgresql://user:pass@dbname.xxxxx.us-east-1.rds.amazonaws.com:5432/athsys_db
```

**Azure Database for PostgreSQL**:
```
postgresql://user@server:pass@server.postgres.database.azure.com:5432/athsys_db
```

---

## 📚 API Reference

### Database Health
- **GET** `/api/admin/database/health` - Check database status
- **POST** `/api/admin/database/validate` - Validate schema
- **POST** `/api/admin/database/initialize` - Create tables

### Imports
- **POST** `/api/admin/import/athletes-csv` - Import athletes from CSV
- **POST** `/api/admin/import/races-json` - Import races from JSON
- **POST** `/api/admin/import/bulk-json` - Bulk import multiple types
- **GET** `/api/admin/import/athletes-template` - Get CSV template
- **GET** `/api/admin/import/races-template` - Get JSON template
- **GET** `/api/admin/import/bulk-template` - Get bulk template

### Exports
- **GET** `/api/admin/export/athletes-csv` - Export athletes as CSV
- **GET** `/api/admin/export/races-csv` - Export races as CSV
- **GET** `/api/admin/export/all-json` - Export all data as JSON

### Sync
- **GET** `/api/admin/sync/status` - Get synchronization status

---

## 🎯 Next Steps

1. ✅ Verify all files created
2. ✅ Test database connectivity
3. ✅ Register import/export blueprint in app.py
4. ✅ Add service files to admin-pro.html
5. ✅ Test imports with sample data
6. ✅ Test exports and file downloads
7. ✅ Monitor logs for errors
8. ✅ Deploy to production with backup strategy

---

## 📞 Support

If you encounter issues:

1. Check backend logs: `tail -f logs/athsys.json`
2. Test API endpoint directly: `curl http://localhost:5000/api/admin/database/health`
3. Verify database: `psql -U athsys_user -d athsys_db`
4. Review error messages in browser console
5. Check import file format matches template

---

**Status**: ✅ Backend completely connected and ready for data import/export operations

Generated: February 22, 2026
