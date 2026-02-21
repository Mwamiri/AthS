# AthSys v2.1 - One-Click Coolify Deployment

## 🚀 Automatic Multi-Service Deployment

This guide enables **automatic deployment** of PostgreSQL, Redis, and AthSys backend in one go using Docker Compose in Coolify.

---

## ✅ Prerequisites

- Coolify instance running
- Domain configured: `athsys.appstore.co.ke`
- GitHub repository access

---

## 📋 Quick Deployment Steps

### Step 1: Create New Resource in Coolify

1. Go to your Coolify dashboard
2. Click **"+ New Resource"**
3. Select **"Docker Compose"** (NOT "Dockerfile" or "Simple Deployment")
4. Choose deployment type: **"Public Repository"**

### Step 2: Configure Repository

**Source Configuration:**
```
Repository URL: https://github.com/Mwamiri/AthS
Branch: main
Build Pack: Docker Compose
```

**Important:** Make sure Coolify detects `docker-compose.yml` at the root of your repository.

### Step 3: Configure Environment Variables

Click **"Environment Variables"** and add these:

```env
# Database Configuration
DB_USER=athsys_user
DB_PASSWORD=your_secure_postgres_password_here
DB_NAME=athsys_db

# Redis Configuration
REDIS_PASSWORD=your_secure_redis_password_here

# Application Secrets (IMPORTANT: Generate secure values)
SECRET_KEY=your_64_character_secret_key_here
JWT_SECRET=your_64_character_jwt_secret_here

# Application Settings
DEBUG=False
PORT=5000
LOG_LEVEL=INFO
```

**🔐 Generate Secure Secrets:**
Run these commands locally to generate secure keys:
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Configure Domain & Port

**Domains:**
```
Primary Domain: athsys.appstore.co.ke
```

**Port Configuration:**
- Coolify will automatically detect port `5000` from the backend service
- Ensure port 5000 is exposed in the configuration

**SSL/TLS:**
- ✅ Enable "Generate SSL Certificate" (Let's Encrypt)
- ✅ Enable "Force HTTPS Redirect"

### Step 5: Deploy!

1. Click **"Deploy"** button
2. Coolify will:
   - ✅ Clone your repository
   - ✅ Read `docker-compose.yml`
   - ✅ Build all services (postgres, redis, backend)
   - ✅ Create persistent volumes automatically
   - ✅ Start all containers with health checks
   - ✅ Configure SSL certificate

**Build Time:** Approximately 3-5 minutes

### Step 6: Monitor Deployment

Watch the deployment logs in real-time:
- **PostgreSQL**: Should show "database system is ready to accept connections"
- **Redis**: Should show "Ready to accept connections"
- **Backend**: Should show "Starting gunicorn" and pass health checks

### Step 7: Initialize Database

Once deployment is successful, initialize the database with demo data:

1. Click on the **athsys_backend** service
2. Open **"Terminal"** or **"Execute Command"**
3. Run:
   ```bash
   cd /app/backend
   python init_db.py
   ```

**Expected Output:**
```
🗄️  AthSys Database Initialization
✅ Database tables created successfully
✅ Created 7 users
✅ Created 6 demo athletes
✅ Created 3 races with 9 events
✅ Created 6 registrations
✅ Created 3 results
✅ Database initialization complete!
```

### Step 8: Verify Deployment

**Health Check:**
```bash
curl https://athsys.appstore.co.ke/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.1",
  "database": "connected",
  "redis": "connected"
}
```

**Access Frontend:**
```
https://athsys.appstore.co.ke
```

**Test Login:**
Try logging in with any of these accounts:
- **Admin**: admin@athsys.com / Admin@123
- **Chief Registrar**: chief@athsys.com / Chief@123
- **Registrar**: registrar@athsys.com / Registrar@123
- **Starter**: starter@athsys.com / Starter@123
- **Athlete**: john@athsys.com / Athlete@123
- **Coach**: sarah@athsys.com / Coach@123
- **Viewer**: viewer@athsys.com / Viewer@123

---

## 🔍 Verify All Services

### Check Service Status in Coolify

All services should show **"Running"** status:
- `postgres` - PostgreSQL database
- `redis` - Redis cache
- `backend` - Flask API

### Check Logs

**Backend Logs:**
```
Should see: "Application startup complete"
No errors about database or Redis connection
```

**PostgreSQL Logs:**
```
Should see: "database system is ready to accept connections"
```

**Redis Logs:**
```
Should see: "Ready to accept connections"
```

---

## 🗂️ Persistent Data Volumes

Coolify automatically creates these volumes (data persists across restarts):

- **postgres_data**: Database files
- **redis_data**: Redis persistence (AOF)
- **app_logs**: Application logs
- **app_data**: Application data files

---

## 🔄 Redeployment & Updates

### Update Application Code

1. Push changes to GitHub repository
2. In Coolify, click **"Redeploy"** button
3. Coolify will:
   - Pull latest code
   - Rebuild changed services only
   - Restart with zero downtime (rolling update)
   - Data in PostgreSQL and Redis is preserved

### Force Rebuild All Services

```bash
# In Coolify UI: Click "Force Rebuild All"
```

---

## 🛠️ Troubleshooting

### Problem: Services Won't Start

**Check 1: Environment Variables**
- Ensure all required variables are set
- Verify no special characters breaking the config

**Check 2: Port Conflicts**
- Only backend port (5000) should be exposed externally
- Internal services (postgres, redis) communicate via Docker network

**Check 3: Health Checks Failing**
```bash
# Check backend service logs
# Look for database connection errors
```

### Problem: Database Connection Failed

**Solution:**
```bash
# Connect to backend terminal in Coolify
cd /app/backend
python -c "from models import engine; print(engine.url)"
# Verify URL matches: postgresql://DB_USER:DB_PASSWORD@postgres:5432/DB_NAME
```

### Problem: Redis Connection Failed

**Solution:**
```bash
# Connect to backend terminal
python -c "import redis; r=redis.from_url('redis://:REDIS_PASSWORD@redis:6379/0'); print(r.ping())"
# Should print: True
```

### Problem: SSL Certificate Not Generating

**Solution:**
- Verify domain DNS points to Coolify server IP
- Wait 2-3 minutes for Let's Encrypt validation
- Check Coolify logs for certificate generation errors

---

## 🔐 Security Checklist (Post-Deployment)

- [ ] Changed all default passwords for 7 test user accounts
- [ ] Generated and set secure SECRET_KEY (64 characters)  
- [ ] Generated and set secure JWT_SECRET (64 characters)
- [ ] Set secure DB_PASSWORD (different from default)
- [ ] Set secure REDIS_PASSWORD (different from default)
- [ ] Verified SSL certificate is active (https works)
- [ ] Reviewed audit logs in database
- [ ] Disabled DEBUG mode (set to False)
- [ ] Configured backup strategy

---

## 📊 Monitoring

### View Logs in Coolify

1. Click on service name (e.g., "athsys_backend")
2. Click **"Logs"** tab
3. Set to **"Live"** for real-time monitoring

### Check Resource Usage

Navigate to service → **"Metrics"**:
- CPU usage
- Memory usage
- Network traffic

### Application Logs

Access via backend terminal:
```bash
cd /app/logs
tail -f application.log
```

---

## 💾 Backup & Restore

### Backup Database

```bash
# In backend terminal or via Coolify Execute Command
docker exec athsys_postgres pg_dump -U athsys_user athsys_db > /app/data/backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
docker exec -i athsys_postgres psql -U athsys_user athsys_db < /app/data/backup_YYYYMMDD.sql
```

### Automated Backups

Set up a cron job in Coolify:
```bash
# Daily backup at 2 AM
0 2 * * * docker exec athsys_postgres pg_dump -U athsys_user athsys_db > /app/data/backup_$(date +\%Y\%m\%d).sql
```

---

## 📈 Scaling

### Increase Resources

In Coolify service settings:
- **CPU**: Increase CPU allocation
- **Memory**: Increase RAM limit (recommend 2GB+ for backend)

### Database Connection Pool

Already configured in `models.py`:
- Pool size: 10 connections
- Max overflow: 20 connections
- Total available: 30 simultaneous connections

---

## ✅ Success Checklist

After deployment, verify:

- [ ] All 3 services running (postgres, redis, backend)
- [ ] Health endpoint returns "healthy" status
- [ ] Frontend loads at https://athsys.appstore.co.ke
- [ ] Can login with test credentials
- [ ] Athletes list loads from database
- [ ] Race data displays correctly
- [ ] SSL certificate active (padlock in browser)
- [ ] No errors in backend logs
- [ ] Database persistence works (data survives restart)
- [ ] Redis caching active (check network tab for speed)
- [ ] All default passwords changed

---

## 🎯 Advantages of This Method

✅ **One-Click Deployment**: All services deployed together  
✅ **Automatic Setup**: No manual service creation  
✅ **Proper Dependencies**: Services start in correct order  
✅ **Health Checks**: Built-in monitoring  
✅ **Persistent Data**: Volumes created automatically  
✅ **Easy Updates**: Single redeploy button  
✅ **Environment Isolation**: Docker network for service communication  
✅ **Rollback Support**: Coolify keeps previous deployment history  

---

## 📞 Support

If you encounter issues:

1. Check Coolify deployment logs
2. Review service-specific logs (postgres, redis, backend)
3. Verify environment variables are correct
4. Ensure domain DNS is configured
5. Check health endpoint response

**Common Issues:**
- **Build fails**: Check Dockerfile syntax and dependencies
- **Services don't start**: Verify environment variables
- **Can't connect to database**: Check DATABASE_URL format
- **SSL issues**: Verify domain DNS and wait for certificate generation

---

## 🎉 You're Done!

Your AthSys application is now running with:
- ✅ PostgreSQL database with 7 users, 6 athletes, 3 races
- ✅ Redis caching and session management  
- ✅ Flask backend API with authentication
- ✅ SSL certificate with auto-renewal
- ✅ Persistent data storage
- ✅ Automated health monitoring
- ✅ Zero-downtime redeployment

**Next Steps:**
1. Change default passwords
2. Add real athlete data
3. Create actual race events
4. Invite users to register

Enjoy your automated athletics system! 🏃‍♂️🏃‍♀️
