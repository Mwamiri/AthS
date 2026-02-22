# ⚡ Quick Start - Database Connectivity (5 Minutes)

**TLDR**: Complete backend connectivity setup in exact order below.

---

## 🚀 The 5-Minute Setup

### Step 1: Register Backend Endpoint (1 min)
Edit `src/backend/app.py`:

**Add at line ~30**:
```python
from import_export_api import register_import_export_blueprint
```

**Add at line ~120**:
```python
register_import_export_blueprint(app)
```

**Test**:
```bash
python src/backend/app.py
# In another terminal:
curl http://localhost:5000/api/admin/database/health
```

✅ Should return `{"status": "healthy", ...}`

---

### Step 2: Initialize Database (1 min)
```bash
cd src/backend
python init_db.py
```

✅ Should show ✅ for all steps

---

### Step 3: Add Frontend Service (1 min)
Edit `src/frontend/admin-pro.html`:

**In `<head>` section, add**:
```html
<script src="data-import-export.js"></script>
```

---

### Step 4: Test Connection (1 min)
Open admin-pro.html in browser, open Console (F12), run:

```javascript
const service = new DataImportExportService();
service.checkDatabaseHealth().then(h => console.log('✅', h));
```

✅ Should show health status

---

### Step 5: Test Import (1 min)
In browser console:

```javascript
const service = new DataImportExportService();
const csv = 'name,country,gender,email\nTest,KEN,M,test@test.com';
service.importAthletesCsv(csv).then(r => console.log('✅', r));
```

✅ Should show import result

---

## 📁 Files Already Created For You

All these files are **ready to use**, no coding needed:

| File | Purpose | Status |
|------|---------|--------|
| `src/backend/db_validator.py` | Database validation & import/export service | ✅ Ready |
| `src/backend/import_export_api.py` | API endpoints (14 total) | ✅ Ready |
| `src/frontend/data-import-export.js` | Frontend import/export service | ✅ Ready |
| `DATABASE_CONNECTIVITY_GUIDE.md` | Full setup guide with examples | ✅ Ready |
| `BACKEND_CONNECTIVITY_IMPROVEMENTS.md` | Architecture & improvements summary | ✅ Ready |
| `INSTALLATION_SETUP.md` | Complete installation instructions | ✅ Ready |
| `INTEGRATION_CHECKLIST.md` | Step-by-step integration tasks | ✅ Ready |

---

## 🎯 What You Get

### Backend
- ✅ Database health monitoring
- ✅ CSV import for athletes
- ✅ JSON import for races
- ✅ Bulk import for all data types
- ✅ CSV export for all tables
- ✅ JSON export for all data
- ✅ Automatic transaction rollback on errors
- ✅ Partial import support (continue on error)

### Frontend
- ✅ Import/export orchestration
- ✅ Progress tracking for large imports
- ✅ File parsing (CSV ↔ JSON conversion)
- ✅ Data validation before upload
- ✅ Error handling with clear messages
- ✅ File downloading utilities

---

## 📊 API Endpoints Available

After completing steps above, these endpoints are active:

### Database Operations
```
POST   /api/admin/database/health        → Check database health
POST   /api/admin/database/validate      → Validate schema
POST   /api/admin/database/initialize    → Create tables
```

### Imports
```
POST   /api/admin/import/athletes-csv    → Import athletes from CSV
POST   /api/admin/import/races-json      → Import races from JSON
POST   /api/admin/import/bulk-json       → Import multiple types
```

### Exports
```
GET    /api/admin/export/athletes-csv    → Download athletes as CSV
GET    /api/admin/export/races-csv       → Download races as CSV
GET    /api/admin/export/all-json        → Download all data as JSON
```

### Templates
```
GET    /api/admin/import/athletes-template   → CSV format guide
GET    /api/admin/import/races-template      → JSON format guide
GET    /api/admin/import/bulk-template       → Bulk format guide
```

---

## 🧪 Test Commands

### Test Backend Health
```bash
curl http://localhost:5000/api/admin/database/health
```

### Test CSV Import
```bash
curl -X POST http://localhost:5000/api/admin/import/athletes-csv \
  -H "Authorization: Bearer 1" \
  -H "Content-Type: application/json" \
  -d '{"csv":"name,country,gender,email\nTest,KEN,M,test@test.com"}'
```

### Test CSV Export
```bash
curl http://localhost:5000/api/admin/export/athletes-csv \
  -H "Authorization: Bearer 1" \
  > athletes.csv
```

---

## 🔧 Configuration

### Database
Located in `src/backend/config.py`:
```python
DATABASE_URL = 'postgresql://athsys_user:athsys_pass@localhost:5432/athsys_db'
```

### Environment (.env file)
Create `.env` in `src/backend/`:
```env
FLASK_ENV=development
DATABASE_URL=postgresql://athsys_user:athsys_pass@localhost:5432/athsys_db
SECRET_KEY=dev-secret-key
```

---

## ⚡ Frontend Integration (Optional)

To add UI buttons for import/export in admin-pro.html:

**In Vue `data()`**:
```javascript
importService: new DataImportExportService(),
showImportModal: false
```

**In Vue `methods`**:
```javascript
async performImport() {
    const csv = await this.importService.readFileAsText(this.importFile);
    const result = await this.importService.importAthletesCsv(csv);
    console.log('✅ Imported:', result.imported);
}
```

**In HTML template**:
```html
<button @click="showImportModal = true">Import Data</button>
<input type="file" @change="(e) => importFile = e.target.files[0]" />
<button @click="performImport">Upload</button>
```

---

## ✅ Verification

After completing 5 steps above, you should have:

- [ ] Backend running on http://localhost:5000
- [ ] Health endpoint responds with status
- [ ] Database initialized with demo data
- [ ] Frontend loads without errors
- [ ] DataImportExportService available in console
- [ ] Can import CSV from console
- [ ] Can export data from console

---

## 🚨 If Something Fails

### "Cannot connect to database"
```bash
# Make sure PostgreSQL is running
sudo service postgresql status

# Check connection
psql -U athsys_user -d athsys_db
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r src/backend/requirements.txt
```

### "Port already in use"
```bash
# Use different port
PORT=5001 python src/backend/app.py
```

### "CORS error from frontend"
```
The app.py already has CORS enabled.
Make sure both frontend and backend are running.
```

### "401 Unauthorized on import"
```javascript
// In browser console:
localStorage.setItem('authToken', '1');  // Use test token
```

---

## 📚 Full Documentation

- **Setup Details**: See `INSTALLATION_SETUP.md`
- **Integration Steps**: See `INTEGRATION_CHECKLIST.md`  
- **API Reference**: See `DATABASE_CONNECTIVITY_GUIDE.md`
- **Architecture**: See `BACKEND_CONNECTIVITY_IMPROVEMENTS.md`

---

## 🎓 Example Usage

### Import Athletes from CSV
```javascript
const service = new DataImportExportService();

const csvData = `name,country,gender,email
Alice Johnson,KEN,F,alice@example.com
Bob Smith,USA,M,bob@example.com
Carol White,CAN,F,carol@example.com`;

service.importAthletesCsv(csvData, (progress) => {
    console.log(`${progress.imported}/${progress.total} imported`);
}).then(result => {
    console.log(`✅ ${result.imported} records imported`);
    if (result.failed > 0) {
        console.warn(`⚠️  ${result.failed} records failed`, result.errors);
    }
});
```

### Export All Data as JSON
```javascript
const service = new DataImportExportService();

service.exportAllJson().then(() => {
    console.log('✅ Data exported to athsys_backup.json');
});
```

### Check Database Health
```javascript
const service = new DataImportExportService();

service.checkDatabaseHealth().then(health => {
    console.log('Status:', health.status);
    console.log('Tables:', Object.keys(health.tables));
    console.log('Athletes:', health.record_counts.athletes);
});
```

---

## 📞 Need Help?

1. **Error in browser**: Check Developer Tools → Console tab
2. **Backend won't start**: Check Python syntax: `python -m py_compile src/backend/app.py`
3. **Database issues**: Check PostgreSQL service is running
4. **Import fails**: Check CSV format matches template
5. **Still stuck**: Read INSTALLATION_SETUP.md Troubleshooting section

---

## 🎉 You're Done!

Once these 5 steps complete, your system has:

✅ Full database connectivity  
✅ Import/export capabilities  
✅ Error handling  
✅ Progress tracking  
✅ Data validation  
✅ Complete API documentation  

Start using the system by logging in to admin-pro.html with:
- **Email**: admin@athsys.com
- **Password**: Admin@123

---

**Time to Complete**: 5-15 minutes  
**Difficulty**: Beginner-Friendly  
**Support**: See detailed guides above  

**Generated**: February 22, 2026
