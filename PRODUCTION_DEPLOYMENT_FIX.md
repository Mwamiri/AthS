# 🚀 Production Deployment Fix - AthSys at ath.appstore.co.ke

**Status**: ⚠️ CRITICAL - Multiple frontend pages unable to connect to backend  
**Date**: February 22, 2026  
**Environment**: Production (ath.appstore.co.ke)

---

## 🔍 Issue Diagnosis

### Symptoms
- ❌ `races.html` - Not working
- ❌ `athletes.html` - Not working
- ❌ `dashboard.html` - Not working
- ❌ `index.html` - Not working
- ✅ `results.html` - WORKS (partial functionality)
- ❌ Backend status shows "Unknown"

### Root Causes Identified

#### 1. **Incorrect API Base URL Configuration**
**File**: `src/frontend/races.js` (and similar files)

**Current Code**:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : window.location.origin;
```

**Problem**: When accessing `https://ath.appstore.co.ke`, the code sets `API_BASE_URL = https://ath.appstore.co.ke`, but:
- The backend might be on a different port (e.g., 5000)
- The backend might be on a subdomain (e.g., `api.appstore.co.ke`)
- The backend might not be accessible via HTTPS

**Impact**: All API calls fail with CORS errors or connection timeouts

---

#### 2. **Backend Not Configured for Production Domain**
**Issue**: Flask CORS is set to allow all origins (`"origins": "*"`), but:
- The backend might not be running on the production server
- The backend might not be accessible from the frontend domain
- There might be a firewall/proxy issue

**Impact**: Frontend can't reach backend API

---

#### 3. **Missing Environment Configuration**
**Issue**: The production deployment doesn't have:
- Environment variables set correctly
- Database connection to production PostgreSQL
- Redis connection (optional but recommended)
- HTTPS/SSL configuration
- Proper proxy setup

---

## ✅ Solution: Complete Production Fix

### Step 1: Identify Backend Location

**First, determine where your backend is running:**

```bash
# Test if backend is running on the same domain
curl -I https://ath.appstore.co.ke:5000/health
curl -I https://ath.appstore.co.ke/api/health

# Test if backend is on a subdomain
curl -I https://api.appstore.co.ke/health

# Check what's actually running
curl https://ath.appstore.co.ke/health
```

---

### Step 2: Create Production Configuration

Create `src/backend/.env.production`:

```env
# Flask Configuration
FLASK_ENV=production
DEBUG=False
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
PORT=5000
HOST=0.0.0.0

# Database Configuration (MUST be correct for production)
DATABASE_URL=postgresql://athsys_user:athsys_pass@your-db-host:5432/athsys_db

# Redis Configuration (Optional)
REDIS_URL=redis://your-redis-host:6379/0

# JWT Configuration
JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
JWT_ACCESS_TOKEN_EXPIRES=86400

# CORS Configuration
CORS_ORIGINS=https://ath.appstore.co.ke,https://api.appstore.co.ke

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/athsys/backend.log
```

---

### Step 3: Update Backend CORS Configuration

Edit `src/backend/app.py` around line 50:

```python
# BEFORE (allows all origins - NOT secure for production):
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# AFTER (specific production domains):
import os
allowed_origins = os.getenv('CORS_ORIGINS', '').split(',')
CORS(app, 
    resources={r"/api/*": {"origins": allowed_origins}}, 
    supports_credentials=True,
    allow_headers=['Content-Type', 'Authorization'],
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
)
```

---

### Step 4: Create API Configuration File

Create `src/frontend/api-config.js`:

```javascript
/**
 * API Configuration for Production
 * Determines backend URL based on environment
 */

window.API_CONFIG = {
    // Get API base URL
    getBaseURL() {
        // Define environment-specific URLs
        const environments = {
            'localhost': 'http://localhost:5000',
            'localhost:3000': 'http://localhost:5000',
            'ath.appstore.co.ke': 'https://ath.appstore.co.ke',  // Same domain
            'api.appstore.co.ke': 'https://api.appstore.co.ke',  // API subdomain
            'admin.appstore.co.ke': 'https://api.appstore.co.ke' // Different subdomain
        };
        
        const hostname = window.location.hostname;
        const port = window.location.port ? `:${window.location.port}` : '';
        const hostWithPort = hostname + port;
        
        // Check if we have a specific configuration
        if (environments[hostWithPort]) {
            return environments[hostWithPort];
        }
        
        // Check if we have a domain-only configuration
        if (environments[hostname]) {
            return environments[hostname];
        }
        
        // Default: use same origin
        console.warn(`[API Config] Unknown environment: ${hostWithPort}. Using window.location.origin`);
        return window.location.origin;
    },
    
    // Get full API endpoint URL
    endpoint(path) {
        const baseURL = this.getBaseURL();
        return `${baseURL}${path.startsWith('/') ? path : '/' + path}`;
    },
    
    // Test connectivity
    async testConnection() {
        try {
            const response = await fetch(this.endpoint('/health'), {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            return {
                connected: response.ok,
                status: response.status,
                baseURL: this.getBaseURL()
            };
        } catch (error) {
            return {
                connected: false,
                error: error.message,
                baseURL: this.getBaseURL()
            };
        }
    }
};

// Log configuration on load
console.log('[API Config] Configured for:', window.API_CONFIG.getBaseURL());
```

---

### Step 5: Update Frontend Pages to Use Configuration

All JavaScript files need to be updated to use `API_CONFIG.endpoint()` instead of hardcoded URLs.

#### For races.js:

**BEFORE**:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : window.location.origin;

// Usage:
const response = await fetchWithAuth(`${API_BASE_URL}/api/races`);
```

**AFTER**:
```javascript
// Add this at the top after script loads
const API_BASE_URL = window.API_CONFIG.getBaseURL();

// Usage remains the same:
const response = await fetchWithAuth(`${API_BASE_URL}/api/races`);
```

#### For All HTML Files:

Add this to the `<head>` section:

```html
<!-- API Configuration - Must load first -->
<script src="api-config.js"></script>
```

---

### Step 6: Create Health Check Page

Create `src/frontend/health-check.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AthSys Health Check</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 2rem;
            max-width: 1000px;
            margin: 0 auto;
        }
        .status-ok { color: green; }
        .status-error { color: red; }
        .status-warning { color: orange; }
        .section {
            margin: 2rem 0;
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
        code {
            background: #f5f5f5;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h1>🏥 AthSys Health Check</h1>
    
    <div class="section">
        <h2>Frontend Environment</h2>
        <p>Hostname: <code id="hostname"></code></p>
        <p>Origin: <code id="origin"></code></p>
        <p>API Base URL: <code id="apiBaseURL"></code></p>
    </div>
    
    <div class="section">
        <h2>Backend Connectivity</h2>
        <div id="backendStatus">Checking...</div>
    </div>
    
    <div class="section">
        <h2>Database Status</h2>
        <div id="databaseStatus">Checking...</div>
    </div>
    
    <div class="section">
        <h2>API Endpoints Test</h2>
        <div id="endpointsStatus">Testing...</div>
    </div>

    <script src="api-config.js"></script>
    <script>
        document.getElementById('hostname').textContent = window.location.hostname;
        document.getElementById('origin').textContent = window.location.origin;
        document.getElementById('apiBaseURL').textContent = window.API_CONFIG.getBaseURL();
        
        async function checkHealth() {
            // Test backend
            try {
                const response = await fetch(
                    window.API_CONFIG.endpoint('/health'),
                    { method: 'GET' }
                );
                const data = await response.json();
                document.getElementById('backendStatus').innerHTML = 
                    `<div class="status-ok">✅ Backend Connected</div><pre>${JSON.stringify(data, null, 2)}</pre>`;
            } catch (error) {
                document.getElementById('backendStatus').innerHTML = 
                    `<div class="status-error">❌ Backend Error: ${error.message}</div>`;
            }
            
            // Test database
            try {
                const response = await fetch(
                    window.API_CONFIG.endpoint('/api/admin/database/health'),
                    { 
                        method: 'POST',
                        headers: { 'Authorization': 'Bearer 1' }
                    }
                );
                const data = await response.json();
                document.getElementById('databaseStatus').innerHTML = 
                    `<div class="status-ok">✅ Database Status: ${data.status}</div><pre>${JSON.stringify(data, null, 2)}</pre>`;
            } catch (error) {
                document.getElementById('databaseStatus').innerHTML = 
                    `<div class="status-warning">⚠️  Database Check: ${error.message}</div>`;
            }
            
            // Test endpoints
            const endpoints = [
                '/api/races',
                '/api/athletes',
                '/api/users',
                '/health'
            ];
            
            let results = '';
            for (const endpoint of endpoints) {
                try {
                    const response = await fetch(window.API_CONFIG.endpoint(endpoint));
                    const status = response.ok ? '✅' : '⚠️ ';
                    results += `${status} ${endpoint} (${response.status})<br>`;
                } catch (error) {
                    results += `❌ ${endpoint} (${error.message})<br>`;
                }
            }
            document.getElementById('endpointsStatus').innerHTML = results;
        }
        
        checkHealth();
    </script>
</body>
</html>
```

---

### Step 7: Update Frontend HTML Files

Add this line to the `<head>` of each HTML file (index.html, races.html, athletes.html, dashboard.html, results.html):

```html
<!-- API Configuration - Must load first -->
<script src="api-config.js"></script>
```

---

### Step 8: Docker Deployment (Recommended)

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: athsys_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: athsys_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - athsys-net
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    networks:
      - athsys-net
    restart: unless-stopped

  # Flask Backend
  backend:
    build:
      context: ./src/backend
      dockerfile: Dockerfile
    environment:
      FLASK_ENV: production
      DATABASE_URL: postgresql://athsys_user:${DB_PASSWORD}@postgres:5432/athsys_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      CORS_ORIGINS: https://ath.appstore.co.ke,https://api.appstore.co.ke
    ports:
      - "5000:5000"
    depends_on:
      - postgres
      - redis
    networks:
      - athsys-net
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./src/frontend:/usr/share/nginx/html:ro
    depends_on:
      - backend
    networks:
      - athsys-net
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  athsys-net:
    driver: bridge
```

---

### Step 9: Nginx Configuration

Create `config/nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:5000;
    }

    server {
        listen 80;
        server_name ath.appstore.co.ke;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name ath.appstore.co.ke;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri /index.html;
            add_header Cache-Control "public, max-age=3600";
        }

        # API Proxy
        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_buffering off;
        }

        # Health endpoint
        location /health {
            proxy_pass http://backend;
            access_log off;
        }
    }
}
```

---

## 🚀 Deployment Steps

### Option A: Single Server Deployment

```bash
# 1. SSH into your production server
ssh user@ath.appstore.co.ke

# 2. Clone/update your repository
cd /app/AthSys_ver1
git pull origin main

# 3. Set environment variables
export FLASK_ENV=production
export DATABASE_URL=postgresql://athsys_user:PASSWORD@localhost:5432/athsys_db
export REDIS_URL=redis://localhost:6379/0
export CORS_ORIGINS=https://ath.appstore.co.ke

# 4. Install dependencies
cd src/backend
pip install -r requirements.txt

# 5. Initialize database
python init_db.py

# 6. Start backend (use systemd or supervisor)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option B: Docker Deployment

```bash
# 1. Navigate to project directory
cd /app/AthSys_ver1

# 2. Create .env file
cat > .env << EOF
DB_PASSWORD=your-secure-password
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
EOF

# 3. Generate SSL certificates
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# 4. Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# 5. Monitor logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

## 🧪 Testing Production Deployment

### Test 1: Health Check Page
```bash
curl https://ath.appstore.co.ke/health-check.html
```

### Test 2: API Connectivity
```bash
curl -X GET https://ath.appstore.co.ke/api/races \
  -H "Authorization: Bearer 1" \
  -H "Content-Type: application/json"
```

### Test 3: Frontend Pages
```bash
# Test each page loads
curl -I https://ath.appstore.co.ke/
curl -I https://ath.appstore.co.ke/races.html
curl -I https://ath.appstore.co.ke/athletes.html
curl -I https://ath.appstore.co.ke/dashboard.html
curl -I https://ath.appstore.co.ke/results.html
```

### Test 4: CORS
```bash
curl -X OPTIONS https://ath.appstore.co.ke/api/races \
  -H "Origin: https://ath.appstore.co.ke" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Database credentials configured
- [ ] Environment variables set
- [ ] SSL certificates prepared
- [ ] Backend code updated with CORS fix
- [ ] Frontend pages updated with api-config.js
- [ ] Nginx configuration created
- [ ] Docker images built and tested locally

### Deployment
- [ ] Database initialized
- [ ] Backend service started
- [ ] Nginx reverse proxy configured
- [ ] Frontend served from static directory
- [ ] Health endpoints responding

### Post-Deployment
- [ ] Health check page loads
- [ ] API endpoints accessible
- [ ] All HTML pages load
- [ ] Data displays correctly
- [ ] Import/export functions work
- [ ] Login/authentication works
- [ ] Logs monitored for errors

---

## Troubleshooting

### Issue: "Backend status shows Unknown"
**Solution**: 
1. Check API_CONFIG.getBaseURL() in browser console
2. Verify backend is running on correct port
3. Check CORS headers in network tab
4. Test: `curl https://ath.appstore.co.ke/health`

### Issue: "404 Not Found" for API endpoints
**Solution**:
1. Ensure backend is accessible at configured URL
2. Check Nginx proxy configuration
3. Verify Flask routes are registered
4. Check DATABASE_URL configuration

### Issue: "CORS error" on API calls
**Solution**:
1. Verify CORS_ORIGINS environment variable
2. Check Access-Control-Allow-Origin header
3. Update CORS_ORIGINS to include your domain
4. Restart backend service

### Issue: "Database connection failed"
**Solution**:
1. Test PostgreSQL connection: `psql -U athsys_user -d athsys_db`
2. Verify DATABASE_URL is correct
3. Check database credentials
4. Ensure database server is running

---

## 📞 Support

For issues with deployment:
1. Check logs: `docker-compose logs -f` or `/var/log/athsys/backend.log`
2. Test health page: `https://ath.appstore.co.ke/health-check.html`
3. Review INTEGRATION_CHECKLIST.md for backend setup
4. Check DATABASE_CONNECTIVITY_GUIDE.md for API reference

---

**Last Updated**: February 22, 2026  
**Status**: Production Deployment Guide Ready
