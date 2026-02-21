# 🎯 AthSys Coolify Services Overview

After deploying with Docker Compose, you'll see **3 services** in Coolify:

---

## 📊 Services Display (Like Your Traccar Example)

### 1. **AthSys Backend** (Main Application)
```
athsys-backend (athsys/backend:latest)
https://athsys.appstore.co.ke (or auto-generated URL)
Status: Running (healthy) ✅
```
- **Publicly accessible** - This is your main application
- **Has domain/URL** - Auto-generated or custom domain
- **Port**: 5000
- **Health check**: Active at `/health`

---

### 2. **PostgreSQL Database**
```
athsys-postgres (postgres:16-alpine)
Internal only - No public URL
Status: Running (healthy) ✅
```
- **NOT publicly accessible** - Internal service only
- **No domain** - Only accessible within Docker network
- **Port**: 5432 (internal)
- **Health check**: PostgreSQL ready check

---

### 3. **Redis Cache**
```
athsys-redis (redis:7-alpine)
Internal only - No public URL
Status: Running (healthy) ✅
```
- **NOT publicly accessible** - Internal service only
- **No domain** - Only accessible within Docker network
- **Port**: 6379 (internal)
- **Health check**: Redis ping check

---

## 🌐 What You'll See in Coolify UI

### Service List View:
```
┌─────────────────────────────────────────────────────────────┐
│ AthSys Docker Compose Application                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ● athsys-backend                                            │
│   athsys/backend:latest                                     │
│   🌐 https://athsys-abc123.coolify.yourserver.com          │
│   ✅ Running (healthy)                                      │
│   [Open] [Logs] [Terminal] [Settings]                      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ● athsys-postgres                                           │
│   postgres:16-alpine                                        │
│   🔒 Internal only                                          │
│   ✅ Running (healthy)                                      │
│   [Logs] [Terminal] [Settings]                             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ● athsys-redis                                              │
│   redis:7-alpine                                            │
│   🔒 Internal only                                          │
│   ✅ Running (healthy)                                      │
│   [Logs] [Terminal] [Settings]                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔗 Accessing Services

### ✅ Backend (PUBLIC - Has URL)
**Click the URL in Coolify dashboard:**
- Auto-generated: `https://athsys-abc123.coolify.yourserver.com`
- Or custom: `https://athsys.appstore.co.ke`

**Features:**
- 🌐 Direct browser access
- 🔒 SSL certificate (HTTPS)
- 📊 Health status "Running (healthy)"
- 🎯 Can click "Open" button to launch

### ❌ PostgreSQL (INTERNAL - No URL)
**Not accessible from outside:**
- No public URL shown
- Only backend service can connect
- Connection string: `postgresql://athsys_user:pass@postgres:5432/athsys_db`

**To Access (if needed):**
- Use Coolify "Terminal" button
- Or connect via backend container

### ❌ Redis (INTERNAL - No URL)  
**Not accessible from outside:**
- No public URL shown
- Only backend service can connect
- Connection string: `redis://:pass@redis:6379/0`

**To Access (if needed):**
- Use Coolify "Terminal" button
- Run: `redis-cli -a your_password`

---

## 📋 What Each Label Does

### Backend Service Labels:
```yaml
labels:
  - "coolify.managed=true"           # Managed by Coolify
  - "coolify.name=athsys-backend"    # Display name
  - "coolify.type=application"       # Service type
  - "coolify.proxy.enabled=true"     # ✅ Enable public access
  - "coolify.public=true"            # ✅ Show public URL
  - "coolify.main=true"              # ✅ Main service
  - "coolify.domain.auto=true"       # ✅ Auto-generate domain
```
**Result:** Shows URL like your Traccar example! 🎉

### Postgres/Redis Labels:
```yaml
labels:
  - "coolify.managed=true"           # Managed by Coolify
  - "coolify.name=athsys-postgres"   # Display name
  - "coolify.type=database"          # Service type
  - "coolify.proxy.enabled=false"    # ❌ NO public access
```
**Result:** Internal only, no URL shown ✅

---

## 🎯 Just Like Your Traccar Example

**What you showed:**
```
Traccar (traccar/traccar:latest)
https://t.appstore.co.ke:8082
Running (healthy) ✅
```

**What you'll get with AthSys:**
```
AthSys Backend (athsys/backend:latest)
https://athsys.appstore.co.ke (or auto-generated)
Running (healthy) ✅
```

### Key Similarities:
✅ Service name displayed  
✅ Docker image shown  
✅ Public URL visible and clickable  
✅ Health status (green checkmark)  
✅ Can open directly from Coolify  

---

## 💡 Adding Your Custom Domain

**To use `athsys.appstore.co.ke` instead of auto-generated:**

1. **In Coolify Dashboard:**
   - Click on **athsys-backend** service
   - Go to **"Domains"** tab
   - Click **"+ Add Domain"**
   - Enter: `athsys.appstore.co.ke`
   - Enable SSL, Save

2. **Update DNS:**
   ```
   A Record: athsys.appstore.co.ke → [Your Coolify Server IP]
   ```

3. **Wait 5-10 minutes** for DNS propagation

4. **Result:**
   ```
   AthSys Backend (athsys/backend:latest)
   https://athsys.appstore.co.ke  ← Your custom domain!
   Running (healthy) ✅
   ```

---

## 🔍 Health Status Meanings

**✅ Running (healthy)**
- Container is running
- Health check passing
- Application responding correctly
- Safe to use!

**🟡 Running (unhealthy)**  
- Container running but health check failing
- Check logs for errors
- May need redeployment

**🔴 Stopped**
- Container not running
- Check deployment logs
- May need manual restart

**🔵 Starting**
- Container initializing
- Wait for health checks
- Usually takes 1-2 minutes

---

## 📊 Port Information

### Backend (PUBLIC):
- **Internal Port**: 5000
- **Exposed Port**: 5000
- **Public Access**: Via domain (80/443)
- **Protocol**: HTTP/HTTPS

### Postgres (INTERNAL):
- **Internal Port**: 5432
- **NOT exposed externally**
- **Access**: Docker network only

### Redis (INTERNAL):
- **Internal Port**: 6379
- **NOT exposed externally**
- **Access**: Docker network only

---

## ✅ What You Should See After Deploy

1. **Deployment Status**: "Deployment successful"
2. **3 Services Listed**: backend, postgres, redis
3. **Backend Service**: Shows public URL (clickable)
4. **All Services**: Green "Running (healthy)" status
5. **Access Application**: Click backend URL to open

---

## 🎉 Ready!

With these enhanced labels, your AthSys deployment will look **exactly like your Traccar example**:
- ✅ Clear service name
- ✅ Docker image displayed
- ✅ Public URL shown
- ✅ Health status visible
- ✅ One-click access

**Deploy now and you'll see the URL immediately!** 🚀
