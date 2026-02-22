# 🧪 Backend Features - Quick Test Guide

**Purpose**: Verify all backend features are active and accessible  
**Time Required**: 5-10 minutes  
**Tools**: cURL, PowerShell/Terminal, or Postman

---

## ✅ Step 1: Start Backend Service

### Option A: Direct Python
```bash
cd c:\projects\AthSys_ver1\src\backend
python app.py
```

### Option B: Using Windows Batch
```bash
cd c:\projects\AthSys_ver1
start_backend.bat
```

### Expected Output
```
WARNING:werkzeug:Running on http://0.0.0.0:5000
[OK] Page builder API mounted at /api/builder
[OK] Records & Standards API mounted at /api/records
[OK] Import/Export API mounted at /api/admin
✅ Redis connected (or: Redis unavailable - caching disabled)
```

✅ If you see all three `[OK]` messages, backend features are **ACTIVE**

---

## ✅ Step 2: Test Core Health Endpoints

### 2.1 Basic Health Check
```powershell
curl http://localhost:5000/health
```

**Expected Response** (Status: 200):
```json
{
  "status": "healthy",
  "message": "✅ All systems operational",
  "timestamp": "2026-02-22T15:30:45.123456",
  "version": "2.2",
  "environment": "development"
}
```

### 2.2 API Info Endpoint
```powershell
curl http://localhost:5000/api/info
```

**Expected Response** (Status: 200):
```json
{
  "app": "AthSys",
  "version": "2.2",
  "environment": "development",
  "endpoints": 45,
  "features": ["auth", "athletes", "races", "results", "import_export", "builder", "records"]
}
```

### 2.3 Liveness Probe
```powershell
curl http://localhost:5000/livez
```

**Expected Response** (Status: 200):
```json
{
  "status": "alive",
  "timestamp": "2026-02-22T15:30:45.123456"
}
```

---

## ✅ Step 3: Test Authentication Module

### 3.1 User Login
```powershell
$body = @{
    email = "admin@athsys.com"
    password = "Admin@123"
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -Body $body
```

**Expected Response** (Status: 200):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "name": "Admin User",
    "email": "admin@athsys.com",
    "role": "admin"
  }
}
```

**Save the token** - you'll need it for other tests!

### 3.2 User Registration
```powershell
$body = @{
    name = "Test Athlete"
    email = "test.athlete@example.com"
    password = "TestPass@123"
    role = "athlete"
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/auth/register `
  -H "Content-Type: application/json" `
  -Body $body
```

**Expected Response** (Status: 201):
```json
{
  "message": "✅ User created successfully",
  "user": {
    "id": 2,
    "name": "Test Athlete",
    "email": "test.athlete@example.com",
    "role": "athlete"
  }
}
```

---

## ✅ Step 4: Test Athlete Management

### 4.1 Get All Athletes
```powershell
curl http://localhost:5000/api/athletes
```

**Expected Response** (Status: 200):
```json
{
  "athletes": [
    {
      "id": 1,
      "name": "Sample Athlete 1",
      "country": "Kenya",
      "club": "Running Club"
    },
    {
      "id": 2,
      "name": "Sample Athlete 2",
      "country": "Uganda",
      "club": "Athletics Club"
    }
  ],
  "count": 2
}
```

### 4.2 Create New Athlete (Requires Admin/Registrar)
```powershell
$token = "YOUR_TOKEN_HERE"  # From step 3.1

$body = @{
    name = "John Kipchoge"
    date_of_birth = "1984-11-20"
    country = "Kenya"
    gender = "M"
    club = "Kenyan Running Club"
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/athletes `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $token" `
  -Body $body
```

**Expected Response** (Status: 201):
```json
{
  "message": "✅ Athlete created",
  "athlete": {
    "id": 3,
    "name": "John Kipchoge",
    "country": "Kenya"
  }
}
```

---

## ✅ Step 5: Test Race Management

### 5.1 Get All Races
```powershell
curl http://localhost:5000/api/races
```

**Expected Response** (Status: 200):
```json
{
  "races": [
    {
      "id": 1,
      "name": "National Championship 2026",
      "location": "Nairobi",
      "date": "2026-03-15",
      "status": "open"
    }
  ],
  "count": 1
}
```

### 5.2 Create New Race (Requires Chief Registrar)
```powershell
$token = "YOUR_TOKEN_HERE"

$body = @{
    name = "International Marathon 2026"
    location = "Kampala"
    date = "2026-04-20"
    distance = 42.195
    description = "Annual international marathon"
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/races `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $token" `
  -Body $body
```

**Expected Response** (Status: 201):
```json
{
  "message": "✅ Race created",
  "race": {
    "id": 2,
    "name": "International Marathon 2026",
    "location": "Kampala"
  }
}
```

---

## ✅ Step 6: Test Import/Export API (NEW FEATURE)

### 6.1 Database Health Check
```powershell
curl -X POST http://localhost:5000/api/admin/database/health
```

**Expected Response** (Status: 200):
```json
{
  "health_check": {
    "status": "healthy",
    "database": "connected",
    "redis": "connected",
    "record_counts": {
      "users": 1,
      "athletes": 2,
      "races": 1,
      "events": 5,
      "registrations": 10,
      "results": 8
    }
  },
  "timestamp": "2026-02-22T15:30:45.123456",
  "message": "✅ Health check complete"
}
```

### 6.2 Get Athlete Template (for CSV import)
```powershell
curl http://localhost:5000/api/admin/import/athletes-template
```

**Expected Response** (Status: 200):
```csv
name,date_of_birth,country,gender,club
John Doe,1990-05-15,Kenya,M,Nairobi Runners
Jane Smith,1992-08-20,Uganda,F,Kampala Athletics
```

### 6.3 Export Athletes as CSV
```powershell
$token = "YOUR_TOKEN_HERE"

curl -X GET http://localhost:5000/api/admin/export/athletes-csv `
  -H "Authorization: Bearer $token" `
  -o athletes.csv
```

**Result**: CSV file saved as `athletes.csv`

### 6.4 Export All Data as JSON
```powershell
$token = "YOUR_TOKEN_HERE"

curl -X GET http://localhost:5000/api/admin/export/all-json `
  -H "Authorization: Bearer $token" `
  -o backup.json
```

**Result**: Complete backup saved as `backup.json`

---

## ✅ Step 7: Test Optional Modules

### 7.1 Page Builder API (if available)
```powershell
curl http://localhost:5000/api/builder/pages
```

**Expected Response** (Status: 200):
```json
{
  "pages": [],
  "message": "✅ Page builder available"
}
```

**If not available**:
```json
{
  "error": "Module not available",
  "message": "Page builder module not loaded"
}
```

### 7.2 Records & Standards API (if available)
```powershell
curl http://localhost:5000/api/records/standards
```

**Expected Response** (Status: 200):
```json
{
  "standards": [],
  "message": "✅ Records module available"
}
```

---

## ✅ Step 8: Using Bearer Token for Protected Endpoints

Most endpoints require authentication. Here's how to use tokens:

### Get a Token
```powershell
$login = @{
    email = "admin@athsys.com"
    password = "Admin@123"
} | ConvertTo-Json

$response = curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -Body $login

$token = ($response | ConvertFrom-Json).token
```

### Use Token in Requests
```powershell
curl -H "Authorization: Bearer $token" `
  http://localhost:5000/api/admin/users
```

---

## ⚠️ Troubleshooting

### Issue: "Module not found" error
```bash
cd src\backend
pip install -r requirements.txt
```

### Issue: "Connection refused" error
- Make sure backend is running: `python app.py`
- Check port 5000 is not in use: `netstat -ano | findstr 5000`

### Issue: "Unauthorized" (401) error
- You need a valid bearer token
- Login first to get a token (Step 3.1)
- Include token in Authorization header

### Issue: "Forbidden" (403) error
- Your user role doesn't have permission
- Use admin account for /api/admin endpoints
- Use Chief Registrar for race management

### Issue: "Redis unavailable"
- This is OK! Backend works without Redis
- Caching and rate limiting are optional
- Check Redis service if needed: `redis-cli ping`

---

## 📊 Test Summary Table

| Feature | Endpoint | Method | Status |
|---------|----------|--------|--------|
| Health | `/health` | GET | ✅ |
| API Info | `/api/info` | GET | ✅ |
| Liveness | `/livez` | GET | ✅ |
| Login | `/api/auth/login` | POST | ✅ |
| Register | `/api/auth/register` | POST | ✅ |
| Athletes | `/api/athletes` | GET/POST | ✅ |
| Races | `/api/races` | GET/POST | ✅ |
| DB Health | `/api/admin/database/health` | POST | ✅ |
| Export CSV | `/api/admin/export/*-csv` | GET | ✅ |
| Export JSON | `/api/admin/export/all-json` | GET | ✅ |
| Builder API | `/api/builder/*` | GET/POST | ⚠️ Optional |
| Records API | `/api/records/*` | GET/POST | ⚠️ Optional |

---

## ✅ Success Criteria

**All features are ACTIVE if you see:**

1. ✅ Startup shows `[OK]` for all three blueprint registrations
2. ✅ Health endpoint returns healthy status
3. ✅ Login endpoint accepts credentials and returns token
4. ✅ Athletes endpoint returns athlete list
5. ✅ Import/Export endpoints accessible
6. ✅ All responses have appropriate status codes

---

## 📝 Notes

- Default admin credentials: `admin@athsys.com` / `Admin@123`
- All timestamps in UTC ISO format
- Pagination supported on list endpoints (add `?page=1&limit=20`)
- Filtering available (check API documentation)
- Rate limiting active on sensitive endpoints

---

**Ready to test?** Start backend now and run tests above! 🚀
