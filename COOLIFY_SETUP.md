# AthSys v2.1 - Complete Coolify Deployment Guide

**Step-by-step instructions to deploy AthSys from scratch on Coolify**

---

## 📋 Pre-Deployment Checklist

- [ ] Coolify server running and accessible
- [ ] GitHub repository: `https://github.com/Mwamiri/AthS`
- [ ] Domain configured: `athsys.appstore.co.ke`
- [ ] SSL certificate ready (Coolify handles this)

---

## 🗑️ STEP 1: Clean Up Old Deployment (If Exists)

1. Go to your Coolify dashboard
2. Navigate to your AthSys project
3. Click **Actions** → **Delete**
4. Confirm deletion
5. Wait for complete removal

---

## 📦 STEP 2: Create PostgreSQL Database Service

### 2.1 Add Database Service
1. In Coolify dashboard, click **+ New Resource**
2. Select **Database**
3. Choose **PostgreSQL 16**
4. Click **Continue**

### 2.2 Configure PostgreSQL
```
Name: athsys-postgres
Database Name: athsys_db
Username: athsys_user
Password: [Generate Strong Password - Save this!]
Port: 5432
```

### 2.3 Set Persistent Storage
- **Volume Path**: `/var/lib/postgresql/data`
- **Mount Path**: `postgres_data`
- ✅ Enable persistent storage

### 2.4 Deploy PostgreSQL
1. Click **Save**
2. Click **Deploy**
3. Wait for status: **Running** (green indicator)
4. **IMPORTANT**: Copy the internal connection URL shown
   - Format: `postgresql://athsys_user:PASSWORD@athsys-postgres:5432/athsys_db`

---

## 🔴 STEP 3: Create Redis Cache Service

### 3.1 Add Redis Service
1. Click **+ New Resource**
2. Select **Database**
3. Choose **Redis 7**
4. Click **Continue**

### 3.2 Configure Redis
```
Name: athsys-redis
Password: [Generate Strong Password - Save this!]
Port: 6379
```

### 3.3 Set Persistent Storage
- **Volume Path**: `/data`
- **Mount Path**: `redis_data`
- ✅ Enable persistent storage

### 3.4 Deploy Redis
1. Click **Save**
2. Click **Deploy**
3. Wait for status: **Running** (green indicator)
4. **IMPORTANT**: Copy the internal connection URL shown
   - Format: `redis://:PASSWORD@athsys-redis:6379/0`

---

## 🚀 STEP 4: Deploy AthSys Backend Application

### 4.1 Create New Application
1. Click **+ New Resource**
2. Select **Application**
3. Choose **Public Repository**
4. Click **Continue**

### 4.2 Repository Configuration
```
Git Repository URL: https://github.com/Mwamiri/AthS
Branch: main
Build Pack: Dockerfile
```
Click **Continue**

### 4.3 General Configuration
```
Name: AthSys
Description: Enterprise Athletics Management System v2.1 - PostgreSQL & Redis powered
Dockerfile Location: /Dockerfile
Base Directory: /
Port: 5000
```

### 4.4 Domain Configuration
```
Domain: https://athsys.appstore.co.ke
```
- ✅ Enable SSL/HTTPS (Coolify handles this automatically)
- ✅ Allow www & non-www (optional)

### 4.5 Health Check Configuration
```
Health Check Enabled: ✅ Yes
Health Check Path: /health
Health Check Method: GET
Health Check Port: 5000
Health Check Interval: 30s
Health Check Timeout: 10s
Health Check Retries: 3
```

### 4.6 Custom Docker Options
**Leave this EMPTY** or use only:
```
--ulimit nofile=4096:4096
```
❌ **DO NOT** use: `--cap-add SYS_ADMIN` or `--device=/dev/fuse` (causes issues)

---

## 🔐 STEP 5: Configure Environment Variables

Click on **Environment Variables** tab and add these **ONE BY ONE**:

### Database Configuration
```bash
DATABASE_URL=postgresql://athsys_user:YOUR_POSTGRES_PASSWORD@athsys-postgres:5432/athsys_db
```
⚠️ Replace `YOUR_POSTGRES_PASSWORD` with the password from Step 2

### Redis Configuration
```bash
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@athsys-redis:6379/0
```
⚠️ Replace `YOUR_REDIS_PASSWORD` with the password from Step 3

### Security Keys (Generate New Values!)

**Generate SECRET_KEY locally**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy output and add:
```bash
SECRET_KEY=<paste_generated_value_here>
```

**Generate JWT_SECRET locally**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy output and add:
```bash
JWT_SECRET=<paste_generated_value_here>
```

### Application Settings
```bash
DEBUG=False
PORT=5000
LOG_LEVEL=INFO
```

### Summary - All Environment Variables:
```bash
DATABASE_URL=postgresql://athsys_user:YOUR_POSTGRES_PASSWORD@athsys-postgres:5432/athsys_db
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@athsys-redis:6379/0
SECRET_KEY=<generated_64_char_hex>
JWT_SECRET=<generated_64_char_hex>
DEBUG=False
PORT=5000
LOG_LEVEL=INFO
```

---

## 💾 STEP 6: Configure Persistent Storage

Click on **Volumes** tab and add:

### Volume 1: Application Logs
```
Source Path: /app/logs
Mount Path: athsys_logs
```

### Volume 2: Backups
```
Source Path: /app/backups
Mount Path: athsys_backups
```

### Volume 3: Data Files
```
Source Path: /app/data
Mount Path: athsys_data
```

---

## 🏗️ STEP 7: Deploy Application

1. Review all configurations
2. Click **Save** (bottom right)
3. Click **Deploy** button
4. Monitor deployment logs in real-time
5. Wait for build to complete (2-5 minutes)
6. Status should show: **Running** (green)

---

## 🗄️ STEP 8: Initialize Database with Demo Data

### 8.1 Access Application Console
1. In Coolify, go to your AthSys application
2. Click **Actions** → **Execute Command**

### 8.2 Run Database Initialization
Execute this command:
```bash
cd /app/backend && python init_db.py
```

### 8.3 Verify Output
You should see:
```
✅ Database tables created
✅ Created 7 users
✅ Created 6 athletes
✅ Created 3 races
✅ Created 9 events
✅ Created 6 registrations
✅ Created 3 results
```

---

## ✅ STEP 9: Test Your Deployment

### 9.1 Check Health Endpoint
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

### 9.2 Access Frontend
Open browser: `https://athsys.appstore.co.ke`

You should see the AthSys landing page with version 2.1

### 9.3 Test Login
Click **Login** and use these credentials:

**Admin Access:**
- Email: `admin@athsys.com`
- Password: `Admin@123`

**Other Test Accounts:**
- Chief Registrar: `chief@athsys.com` / `Chief@123`
- Registrar: `registrar@athsys.com` / `Registrar@123`
- Starter: `starter@athsys.com` / `Starter@123`
- Athlete: `john@athsys.com` / `Athlete@123`
- Coach: `sarah@athsys.com` / `Coach@123`
- Viewer: `viewer@athsys.com` / `Viewer@123`

---

## 🔍 STEP 10: Verify All Features

### Database Connection
1. Login as admin
2. Navigate to athletes section
3. Create a new athlete
4. Verify data persists after page refresh

### Redis Caching
1. Open browser dev tools (F12)
2. Go to Network tab
3. Navigate to athletes list
4. First load: "retrieved successfully"
5. Refresh page: "retrieved successfully (cached)"

### Session Management
1. Login and note you stay logged in
2. Close browser
3. Reopen: should still be logged in (24-hour session)

---

## 🛠️ Troubleshooting

### Application Won't Start
**Check logs in Coolify:**
1. Go to application → **Logs** tab
2. Look for errors

**Common issues:**
- Missing environment variables
- Database not accessible
- Wrong database credentials

**Fix:**
```bash
# Test database connection manually
docker exec -it athsys-container python -c "from models import init_db; init_db()"
```

### Database Connection Failed
1. Verify PostgreSQL service is running (green status)
2. Check `DATABASE_URL` environment variable
3. Ensure hostname is `athsys-postgres` (internal Docker name)

### Redis Connection Failed
1. Verify Redis service is running (green status)
2. Check `REDIS_URL` environment variable
3. Test connection:
```bash
docker exec -it athsys-container python -c "from redis_config import test_redis_connection; test_redis_connection()"
```

### Port Issues
- Ensure Port is set to **5000** in application settings
- Health check should target port **5000**

### SSL/HTTPS Issues
- Coolify handles SSL automatically
- Ensure domain is correctly configured
- Wait 2-3 minutes for certificate provisioning

---

## 📊 Monitoring & Maintenance

### View Logs
```bash
# Application logs
Coolify → AthSys → Logs tab

# Database logs
Coolify → athsys-postgres → Logs tab

# Redis logs
Coolify → athsys-redis → Logs tab
```

### Database Backup
```bash
# Manual backup via Coolify command
docker exec athsys-postgres pg_dump -U athsys_user athsys_db > /app/backups/backup_$(date +%Y%m%d).sql
```

### Monitor Resource Usage
- Coolify dashboard shows CPU, RAM, Network usage
- Set up alerts for high resource consumption

---

## 🔒 Security Recommendations

### Immediately After Deployment:

1. **Change Default Passwords**
   - Login as each user
   - Navigate to profile settings
   - Update passwords

2. **Enable 2FA** (if implemented)
   - Admin settings → Security → Enable 2FA

3. **Review Access Logs**
   - Check audit logs for suspicious activity

4. **Update Secrets**
   - Rotate `SECRET_KEY` and `JWT_SECRET` monthly
   - Update in Coolify environment variables
   - Redeploy application

5. **Database Security**
   - Ensure PostgreSQL is not exposed externally
   - Only accessible via internal Docker network

6. **Enable Rate Limiting**
   - Already configured in code (10 login attempts per 5 min)
   - Monitor in logs

---

## 📈 Scaling (Optional)

### Increase Resources
Coolify → Application → **Resources** tab:
- Increase CPU limit
- Increase RAM limit
- Adjust based on load

### Add Replicas
For high availability:
1. Increase replica count to 2-3
2. Coolify handles load balancing automatically

### Database Connection Pool
Already configured in `models.py`:
- Pool size: 10 connections
- Max overflow: 20 connections

---

## 🎉 Success Checklist

- [ ] PostgreSQL service running (green)
- [ ] Redis service running (green)
- [ ] AthSys application running (green)
- [ ] Health endpoint returns 200 OK
- [ ] Frontend loads at `https://athsys.appstore.co.ke`
- [ ] Admin login works
- [ ] Athletes list displays
- [ ] Data persists after restart
- [ ] Caching works (check response headers)
- [ ] Sessions maintained across browser restarts

---

## 📞 Support

If you encounter issues:

1. **Check Coolify Logs**: Most issues show up in deployment/runtime logs
2. **Verify Environment Variables**: Ensure all required vars are set
3. **Test Services Independently**: Check if PostgreSQL and Redis are accessible
4. **Review Documentation**: Refer to `DEPLOYMENT.md` for detailed troubleshooting

---

## 🔄 Redeployment (Updates)

When you push code updates to GitHub:

1. Coolify auto-detects changes (if webhook enabled)
2. Or manually: Click **Redeploy** button
3. Coolify rebuilds and deploys automatically
4. Zero-downtime deployment (if multiple replicas)

---

**Deployment Time**: ~10-15 minutes for complete setup

**Next Steps After Successful Deployment:**
1. Change all default passwords
2. Configure email notifications (optional)
3. Set up automated backups
4. Monitor logs for first 24 hours
5. Create custom user accounts

---

**Good luck with your deployment! 🚀**

*AthSys v2.1 - Built with ❤️ for the athletics community*
