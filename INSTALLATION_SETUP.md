# 🚀 Installation & Setup Instructions

Complete step-by-step guide to setup AthSys v3.0 with enhanced database connectivity.

---

## Prerequisites

- **Python 3.8+**
- **PostgreSQL 12+** (or compatible)
- **Node.js** (optional, for frontend build tools)
- **Git** (for version control)
- **pip** (Python package manager)
- **Redis** (optional, for caching)

---

## Step 1: Clone & Setup Project

```bash
# Clone repository
git clone https://github.com/your-org/athsys.git
cd athsys

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

---

## Step 2: Install Backend Dependencies

```bash
cd src/backend

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "Flask|SQLAlchemy|psycopg2|redis"
```

**Key packages installed**:
- Flask & Flask-CORS
- SQLAlchemy & psycopg2-binary (PostgreSQL)
- Redis (caching)
- PyJWT & bcrypt (security)
- python-dateutil & python-dotenv

---

## Step 3: Configure Database

### Option A: Local PostgreSQL (Development)

#### Windows
```bash
# Install PostgreSQL from https://www.postgresql.org/download/windows/
# During installation, note the password for 'postgres' user

# Create database and user
"C:\Program Files\PostgreSQL\15\bin\psql" -U postgres

# In PostgreSQL console:
CREATE USER athsys_user WITH PASSWORD 'athsys_pass';
CREATE DATABASE athsys_db OWNER athsys_user;
GRANT ALL PRIVILEGES ON DATABASE athsys_db TO athsys_user;
\q
```

#### macOS (using Homebrew)
```bash
# Install PostgreSQL
brew install postgresql@15

# Start service
brew services start postgresql@15

# Create user and database
createuser -P athsys_user
createdb -U athsys_user athsys_db
```

#### Linux (Ubuntu/Debian)
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create user and database
sudo -u postgres createuser athsys_user
sudo -u postgres createdb -O athsys_user athsys_db

# Set password
sudo -u postgres psql -c "ALTER USER athsys_user WITH PASSWORD 'athsys_pass';"
```

### Option B: Docker PostgreSQL

```bash
# Run PostgreSQL in Docker
docker run --name athsys-db \
  -e POSTGRES_USER=athsys_user \
  -e POSTGRES_PASSWORD=athsys_pass \
  -e POSTGRES_DB=athsys_db \
  -p 5432:5432 \
  -d postgres:15-alpine

# Verify connection
docker exec -it athsys-db psql -U athsys_user -d athsys_db -c "SELECT 1;"
```

### Verify Database Connection

```bash
# Test connection
psql -U athsys_user -d athsys_db -h localhost

# Should show: athsys_db=>
# Type \q to exit
```

---

## Step 4: Create Environment Configuration

Create `.env` file in `src/backend/`:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-dev-secret-key-change-in-production
PORT=5000
HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://athsys_user:athsys_pass@localhost:5432/athsys_db
SQLALCHEMY_ECHO=False
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=86400

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/athsys.log

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## Step 5: Initialize Database Schema

```bash
cd src/backend

# Run initialization script
python init_db.py

# Expected output:
# ========================================
# 🔄 Initializing database...
# ✅ Database tables created
# 🔄 Seeding database with demo data...
# ✅ Created 7 users
# ✅ Created 5 athletes
# ✅ Created 3 races
# ========================================
```

### Verify Database Initialized

```bash
# Check tables
psql -U athsys_user -d athsys_db -c "\dt"

# Should show:
# public | users        | table
# public | athletes     | table
# public | races        | table
# ...
```

---

## Step 6: Verify Database Connectivity

```bash
# Run connectivity test
python -c "
from db_validator import setup_database_with_validation
setup_database_with_validation()
"

# Expected output:
# ============================================================
# 🔍 DATABASE CONNECTIVITY CHECK
# ============================================================
# 1️⃣  Attempting database connection...
# ✅ Database connection successful
# 2️⃣  Verifying database tables...
# ✅ All tables exist
# 3️⃣  Performing health check...
# Status: healthy
# Tables: 7/7 ✅
# Users: 7 records
# ...
# ============================================================
# ✅ DATABASE READY FOR OPERATION
# ============================================================
```

---

## Step 7: Register Import/Export Blueprint

Edit `src/backend/app.py`:

**Find line ~30 (imports section) and add**:
```python
from import_export_api import register_import_export_blueprint
```

**Find line ~120 (after creating Flask app) and add**:
```python
# Register blueprint for import/export functionality
register_import_export_blueprint(app)
```

---

## Step 8: Start Backend Server

```bash
cd src/backend

# Run development server
python app.py

# Or with auto-reload and debugging
FLASK_ENV=development flask run

# Expected output:
# * Serving Flask app 'app'
# * Debug mode: on
# * Running on http://127.0.0.1:5000
# * WARNING: This is a development server. Do not use it in production.
```

---

## Step 9: Verify Backend is Running

### In a new terminal:
```bash
# Test health endpoint
curl http://localhost:5000/health

# Expected response:
# {
#   "status": "healthy",
#   "checks": {
#     "api": "operational",
#     "database": "operational",
#     "cache": "active"
#   }
# }

# Test import/export endpoint
curl http://localhost:5000/api/admin/database/health \
  -H "Authorization: Bearer 1"

# Expected response:
# {
#   "status": "healthy",
#   "connected": true,
#   "tables": { ... },
#   "record_counts": { ... }
# }
```

---

## Step 10: Setup Frontend

### Add Service Files to admin-pro.html

Edit `src/frontend/admin-pro.html`, in `<head>` section:

```html
<!-- Add after existing script imports -->
<script src="api-service.js"></script>
<script src="data-import-export.js"></script>
```

### Update Vue App Initialization

In admin-pro.html, in the Vue app's `data()` method:

```javascript
data() {
    return {
        // ... existing properties ...
        
        // API services
        api: new AthSysAPI(),
        importService: new DataImportExportService(),
        
        // Import/Export UI state
        showImportModal: false,
        importFile: null,
        importProgress: { imported: 0, failed: 0, total: 0 },
        databaseHealth: null,
        importInProgress: false,
        
        // Import type selector
        importType: 'athletes' // 'athletes', 'races', 'bulk'
    }
}
```

### Add Import/Export Methods

In the Vue app's `methods`:

```javascript
async performImport() {
    if (!this.importFile) {
        this.addNotification('Please select a file', 'Import', 'warning');
        return;
    }
    
    try {
        this.importInProgress = true;
        const content = await this.importService.readFileAsText(this.importFile);
        
        let result;
        if (this.importType === 'athletes') {
            result = await this.importService.importAthletesCsv(content, (progress) => {
                this.importProgress = progress;
            });
        } else if (this.importType === 'races') {
            const jsonData = JSON.parse(content);
            result = await this.importService.importRacesJson(jsonData, (progress) => {
                this.importProgress = progress;
            });
        } else {
            const jsonData = JSON.parse(content);
            result = await this.importService.importBulkJson(jsonData, (progress) => {
                this.importProgress = progress;
            });
        }
        
        if (result.status === 'success') {
            this.addNotification(`✅ Imported ${result.imported} records`, 'Success', 'success');
            // Reload data
            await this.loadDashboardData();
        } else {
            this.addNotification(`⚠️  ${result.imported} imported, ${result.failed} failed`, 'Partial Import', 'warning');
        }
    } catch (error) {
        this.addNotification(`❌ ${error.message}`, 'Import Error', 'error');
    } finally {
        this.importInProgress = false;
        this.importFile = null;
        this.showImportModal = false;
    }
},

async performExport() {
    try {
        if (this.importType === 'athletes') {
            await this.importService.exportAthletesCsv();
        } else if (this.importType === 'races') {
            await this.importService.exportRacesCsv();
        } else {
            await this.importService.exportAllJson();
        }
        this.addNotification('✅ Export completed', 'Success', 'success');
    } catch (error) {
        this.addNotification(`❌ Export failed: ${error.message}`, 'Error', 'error');
    }
},

async checkDatabaseHealth() {
    try {
        this.databaseHealth = await this.importService.checkDatabaseHealth();
        if (this.databaseHealth.status === 'healthy') {
            this.addNotification('✅ Database is healthy', 'Status', 'success');
        } else {
            this.addNotification('⚠️  Database issues detected', 'Status', 'warning');
        }
    } catch (error) {
        this.addNotification(`❌ Could not check database: ${error.message}`, 'Error', 'error');
    }
}
```

---

## Step 11: Test Complete Integration

### Test 1: Frontend Connection
```javascript
// In browser console on admin-pro.html page:

const service = new DataImportExportService();
service.checkDatabaseHealth().then(health => {
    console.log('✅ Frontend connected to backend:', health);
});
```

### Test 2: Sample Import
```javascript
const service = new DataImportExportService();

// Sample athletes CSV
const athletesCsv = `name,country,gender,email
Test Athlete1,KEN,M,test1@example.com
Test Athlete2,KEN,F,test2@example.com`;

service.importAthletesCsv(athletesCsv).then(result => {
    console.log('✅ Import result:', result);
});
```

### Test 3: Data Export
```javascript
const service = new DataImportExportService();

// Export athletes as CSV
service.exportAthletesCsv().then(() => {
    console.log('✅ Athletes exported');
});

// Export all data as JSON
service.exportAllJson().then(data => {
    console.log('✅ All data exported:', data.data);
});
```

---

## Step 12: Login & Testing

### Admin Account
**Email**: `admin@athsys.com`
**Password**: `Admin@123`
**Role**: `admin`

### Test Import Workflow
1. Navigate to admin-pro.html
2. Login with admin account
3. Click "Import Data" button
4. Select import type (Athletes/Races/Bulk)
5. Upload sample CSV or JSON file
6. Verify import progress
7. Check data appears in respective pages

---

## Step 13: Production Deployment

### Pre-deployment Checklist
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database backup created
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Error tracking setup
- [ ] Security headers configured
- [ ] Database backups automated

### Production Configuration

```env
# Production .env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=generate-with-secrets.token_hex()
DATABASE_URL=postgresql://user:pass@prod-db-host:5432/athsys_db
REDIS_URL=redis://prod-redis-host:6379/0
LOG_LEVEL=WARNING
```

### Production Server

```bash
# Using Gunicorn
pip install gunicorn

# Run with production server
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or with systemd service (Linux)
# Create /etc/systemd/system/athsys.service
[Unit]
Description=AthSys Backend
After=network.target

[Service]
User=athsys
WorkingDirectory=/app/src/backend
ExecStart=/app/venv/bin/gunicorn -w 4 app:app

[Install]
WantedBy=multi-user.target

# Enable service
sudo systemctl enable athsys
sudo systemctl start athsys
```

---

## Troubleshooting

### Issue: "Cannot connect to PostgreSQL"
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Check connection
psql -U athsys_user -d athsys_db

# If fails, check credentials in .env
cat .env | grep DATABASE_URL
```

### Issue: "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask; print(flask.__version__)"
```

### Issue: Port 5000 already in use
```bash
# Find process using port
lsof -i :5000

# Or use different port
PORT=5001 python app.py
```

### Issue: Import fails with 401 Unauthorized
```javascript
// Check token in localStorage
console.log(localStorage.getItem('authToken'));

// Re-login
// Navigate to index.html, login, then return to admin-pro.html
```

### Issue: Database tables don't exist
```bash
# Reinitialize database
python init_db.py

# Or manually create tables
from db_validator import DatabaseValidator
validator = DatabaseValidator()
validator.initialize_database()
```

---

## Verification Checklist

- [ ] PostgreSQL installed and running
- [ ] Database created with correct name & user
- [ ] .env file configured in backend directory
- [ ] Backend dependencies installed (pip list shows Flask, SQLAlchemy, psycopg2)
- [ ] Database initialized (python init_db.py runs successfully)
- [ ] Backend server running (python app.py)
- [ ] Health endpoint responds (curl http://localhost:5000/health)
- [ ] Database health check passes (curl http://localhost:5000/api/admin/database/health)
- [ ] Frontend can reach backend (browser console shows successful API calls)
- [ ] Import/export services initialized (console shows DataImportExportService)
- [ ] Test import completes successfully
- [ ] Test export downloads file
- [ ] Admin panel displays data correctly

---

## Next Steps

1. ✅ Backend setup and initialization
2. ✅ Frontend service integration
3. ✅ Test connectivity
4. → Load production data (if migrating)
5. → Setup automated backups
6. → Configure monitoring
7. → Train users on features
8. → Plan capacity & scaling

---

## Support Resources

- **Documentation**: See `DATABASE_CONNECTIVITY_GUIDE.md`
- **Backend Improvements**: See `BACKEND_CONNECTIVITY_IMPROVEMENTS.md`
- **Admin Dashboard**: See `ADMIN_PRO_IMPLEMENTATION.md`
- **Project Structure**: See `FILE_STRUCTURE.md`
- **API Reference**: Check browser at `http://localhost:5000/api/docs`

---

**Installation Complete!** 🎉

Your AthSys v3.0 system is now ready for development and testing.

Generated: February 22, 2026
