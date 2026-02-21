# 🌐 AthSys - Quick Coolify Domain Setup

## Auto-Generated Domain (Immediate After Deploy)

When you deploy AthSys using Docker Compose in Coolify, the system **automatically generates a domain** for you.

### 📍 Where to Find Your Auto-Generated URL:

#### Method 1: Application Dashboard (Easiest)
1. After deployment completes → You'll see your app dashboard
2. Look at the top section → **"Domains"** or **"URL"** field
3. You'll see something like: `https://athsys-abc123.your-coolify-server.com`
4. **Click the URL** to open your application immediately! 🚀

#### Method 2: Backend Service Page
1. Click on the **"backend"** service in your deployment
2. Look for **"Public URL"** or **"Application Domain"**
3. The auto-generated domain will be displayed
4. Click the **copy icon** or **open link** button

#### Method 3: Domains Tab
1. Navigate to **"Domains"** tab in your application
2. You'll see a list of domains (auto-generated one listed first)
3. Click **"Edit"** icon if you want to add a custom domain

---

## ✏️ How to Edit/Add Your Custom Domain

### To Replace with Your Custom Domain (athsys.appstore.co.ke):

1. **In Coolify Dashboard:**
   - Go to your AthSys deployment
   - Click **"Domains"** tab
   - Click **"+ Add Domain"** button

2. **Enter Your Domain:**
   ```
   athsys.appstore.co.ke
   ```

3. **Enable SSL:**
   - ✅ Check "Generate SSL Certificate"
   - ✅ Check "Force HTTPS Redirect"
   - Click **"Save"**

4. **Update DNS (Important!):**
   - Go to your domain provider (e.g., GoDaddy, Namecheap, Cloudflare)
   - Add an **A Record**:
     ```
     Type: A
     Name: athsys
     Value: [Your Coolify Server IP Address]
     TTL: 3600
     ```
   - Wait 5-10 minutes for DNS propagation

5. **Verify:**
   - Visit `https://athsys.appstore.co.ke`
   - You should see your AthSys application
   - Green padlock 🔒 = SSL working!

---

## 🔍 What the Auto-Generated URL Looks Like

**Format:**
```
https://<app-name>-<random-hash>.<coolify-domain>
```

**Examples:**
- `https://athsys-7a8b9c.coolify.example.com`
- `https://athsys-x1y2z3.mycoolifyserver.com`
- `https://backend-4d5e6f.coolify.io`

The random hash ensures uniqueness across all deployments.

---

## 🎯 Labels Added for Auto-Domain

Your `docker-compose.yml` now includes these Coolify labels:

```yaml
labels:
  # Enable public access
  - "coolify.proxy.enabled=true"
  - "coolify.http.enabled=true"
  - "coolify.https.enabled=true"
  
  # Service configuration
  - "coolify.main=true"  # ← Marks this as main service
  - "coolify.proxy.port=5000"  # ← Exposes port 5000
  
  # Auto-SSL
  - "coolify.ssl.enabled=true"
  - "coolify.ssl.letsencrypt=true"
```

These labels tell Coolify:
- ✅ This is the main service to expose publicly
- ✅ Generate a domain automatically
- ✅ Enable HTTP/HTTPS access
- ✅ Auto-provision SSL certificate via Let's Encrypt
- ✅ Route traffic to port 5000

---

## 🚀 Quick Deployment Flow

1. **Deploy** → Click "Deploy" button in Coolify
2. **Wait** → 3-5 minutes for build and startup
3. **Auto-Domain Appears** → Coolify generates URL automatically
4. **Access** → Click the URL to open your app
5. **Login** → Use demo credentials:
   ```
   admin@athsys.com / Admin@123
   ```

---

## 💡 Pro Tips

### Using Multiple Domains
You can have BOTH the auto-generated domain AND your custom domain:
- Auto-generated: For quick testing during development
- Custom domain: For production use with your brand

### Finding Domain in Deployment Logs
At the end of successful deployment logs, you'll see:
```
✓ Deployment successful
✓ Application is running at: https://athsys-abc123.coolify.server.com
```

### No Domain Showing?
If you don't see an auto-generated domain:
1. Check deployment status (must be "Running" with green ✓)
2. Look specifically at the **backend** service (not postgres/redis)
3. Verify labels are present in docker-compose.yml
4. Try clicking **"Generate Domain"** button in Coolify UI
5. Check Coolify logs for proxy configuration errors

---

## 🔐 Security Notes

- Auto-generated domains get SSL certificates automatically
- Custom domains need DNS A record pointing to Coolify server
- SSL certificates auto-renew via Let's Encrypt
- Force HTTPS redirect is enabled by default

---

## 📞 Quick Support

**Problem:** Can't see auto-generated domain
**Solution:** Check that `coolify.proxy.enabled=true` label exists on backend service

**Problem:** Domain shows but site won't load
**Solution:** Check backend container logs for startup errors

**Problem:** Want to change custom domain
**Solution:** Just add new domain in Coolify UI, remove old one

---

## ✅ Ready!

After deployment with these labels, you'll immediately see:
- 🌐 Auto-generated HTTPS domain
- 🔒 SSL certificate active
- 🎯 Ready to use or add custom domain

**No manual configuration needed!** 🎉
