# 🎛️ CMS System - Backend Controls Frontend

## Overview

AthSys v2.2 now includes a **complete CMS (Content Management System)** where the **backend controls what the frontend displays**. No more hardcoded content!

### What Can Be Controlled from Backend?

✅ **Navigation Links** - Show/hide/edit menu items  
✅ **Feature Toggles** - Enable/disable features without redeploying  
✅ **Logs Modal** - Toggle visibility of system logs modal  
✅ **Login Modal** - Toggle visibility of login/register modal  
✅ **Features Section** - Show/hide features showcase  
✅ **Custom Configurations** - Add any custom frontend settings  

---

## 📊 Architecture

### Database Model

```python
class FrontendConfig(Base):
    """Frontend configuration controlled from backend"""
    key          # e.g., 'nav_links', 'show_logs_modal'
    value        # JSON string with configuration
    description  # Human-readable description
    updated_by   # Admin user ID who made changes
    updated_at   # Timestamp of last update
```

### API Endpoints

#### Public Endpoints (No Auth Required)

**GET `/api/config/frontend`**  
Returns all frontend configuration. Frontend loads this on page load.

```bash
curl https://ath.appstore.co.ke/api/config/frontend
```

Response:
```json
{
  "config": {
    "nav_links": [
      {"label": "Home", "url": "/", "visible": true},
      {"label": "Features", "url": "#features", "visible": true},
      {"label": "Logs", "url": "#logs", "visible": true}
    ],
    "show_logs_modal": true,
    "show_login_modal": true,
    "show_features_section": true
  }
}
```

#### Admin Endpoints (Auth Required - Admin Role)

**PUT `/api/admin/config/frontend/nav-links`**  
Update navigation links

```bash
curl -X PUT https://ath.appstore.co.ke/api/admin/config/frontend/nav-links \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "links": [
      {"label": "Home", "url": "/", "visible": true},
      {"label": "Features", "url": "#features", "visible": true},
      {"label": "Documentation", "url": "/docs", "visible": true}
    ]
  }'
```

**POST `/api/admin/config/frontend/toggle-feature/<feature_name>`**  
Enable/disable features

```bash
# Disable logs modal
curl -X POST https://ath.appstore.co.ke/api/admin/config/frontend/toggle-feature/logs_modal \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

**GET/PUT `/api/admin/config/frontend/<key>`**  
Get or update specific configuration key

```bash
curl https://ath.appstore.co.ke/api/admin/config/frontend/nav_links \
  -H "Authorization: Bearer <token>"
```

---

## 🖥️ CMS Admin Panel

### Access

**URL**: `https://ath.appstore.co.ke/cms-admin.html`

**Requirements**:
- Must be logged in with **Admin role**
- Admin account will be created during initial setup

### Features

#### 1. Navigation Links Manager

**Add/Edit/Delete Navigation Links**

- **Label**: Text displayed in navigation (e.g., "Features")
- **URL**: Link destination (e.g., "#features" or "/page.html")
- **Visible**: Toggle to show/hide the link

Changes save to database immediately. Frontend reloads config on next access.

#### 2. Feature Toggles

**Enable/Disable Frontend Features**

| Feature | Controls |
|---------|----------|
| 📋 System Logs | Shows/hides "System Logs" link and logs modal |
| 🔐 Login Modal | Shows/hides login/register modal |
| ✨ Features Section | Shows/hides features showcase |

Toggle any feature on/off without redeploying!

#### 3. Configuration Status

View all active configurations and when they were last updated.

#### 4. API Reference

See all available endpoints for developers.

---

## 🔄 How It Works

### Frontend Flow

```
1. User visits https://ath.appstore.co.ke/
2. index.html loads
3. JavaScript runs: loadFrontendConfig()
4. Fetches /api/config/frontend (public, no auth)
5. Dynamically builds navigation from response
6. Shows/hides modals based on backend config
7. No hardcoded content on frontend!
```

### Backend Flow

```
1. Admin logs in and visits /cms-admin.html
2. Loads current config from /api/config/frontend
3. Admin makes changes (add link, toggle feature, etc.)
4. Submits to /api/admin/config/frontend/...
5. Backend stores in FrontendConfig database table
6. All users see updated content on next page reload
```

---

## 💡 Use Cases

### Example 1: Hide Logs During Maintenance

**Step 1**: Admin logs in to `cms-admin.html`  
**Step 2**: Under "Feature Toggles", toggle "📋 System Logs" OFF  
**Step 3**: Page reloads, logs link disappears for all users  
**Step 4**: Users no longer see logs modal  

### Example 2: Add New Navigation Link

**Step 1**: In "Navigation Links Manager", fill:
- Label: "Documentation"
- URL: "/docs.html"
- Visible: ✓ Checked

**Step 2**: Click "➕ Add Link"  
**Step 3**: All users see new "Documentation" link in nav  

### Example 3: Disable Login During Maintenance

**Step 1**: Toggle "🔐 Login Modal" OFF in Feature Toggles  
**Step 2**: Users will not see login button  
**Step 3**: Use to prevent new logins during database maintenance  

---

## 🔐 Security

### Permissions

| Endpoint | Public | Admin | Notes |
|----------|--------|-------|-------|
| `/api/config/frontend` | ✅ GET | - | Public, cached in frontend |
| `/api/admin/config/frontend/<key>` | ❌ | ✅ GET/PUT | Admin only |
| `/api/admin/config/frontend/nav-links` | ❌ | ✅ PUT | Admin only |
| `/api/admin/config/frontend/toggle-feature/<name>` | ❌ | ✅ POST | Admin only |

### Authentication

- Config management requires **valid JWT token** with **admin role**
- Public config endpoint has no auth (safe - only shows frontend config)
- All updates logged to audit trail

### Audit Trail

Every change is logged in `AuditLog` table:
- **Action**: UPDATE_CONFIG, TOGGLE_FEATURE, UPDATE_NAV_LINKS
- **Entity**: FrontendConfig
- **User**: Admin who made change
- **Timestamp**: When change occurred

---

## 📝 Database Schema

### FrontendConfig Table

```sql
CREATE TABLE frontend_configs (
    id INTEGER PRIMARY KEY,
    key VARCHAR(100) UNIQUE,           -- Configuration key
    value TEXT,                        -- JSON value
    description VARCHAR(255),          -- Human-readable description
    updated_by INTEGER,                -- Admin user ID
    updated_at DATETIME,              -- Last update timestamp
    created_at DATETIME               -- Creation timestamp
);
```

### Example Data

```json
INSERT INTO frontend_configs (key, value, description) VALUES
(
  'nav_links',
  '[
    {"label": "Home", "url": "/", "visible": true},
    {"label": "Features", "url": "#features", "visible": true},
    {"label": "Login", "url": "#login", "visible": true}
  ]',
  'Navigation links visible on home page'
),
(
  'show_logs_modal',
  'true',
  'Toggle system logs modal visibility'
),
(
  'show_login_modal',
  'true',
  'Toggle login/register modal visibility'
);
```

---

## 🚀 Deployment

### Initial Setup

```bash
# Database migration (if needed)
python -c "from models import init_db; init_db()"

# Create default CMS config
python -c "
from models import FrontendConfig, SessionLocal
import json

db = SessionLocal()

# Add default nav links
db.add(FrontendConfig(
    key='nav_links',
    value=json.dumps([
        {'label': 'Home', 'url': '/', 'visible': True},
        {'label': 'Features', 'url': '#features', 'visible': True},
        {'label': 'About', 'url': '#stats', 'visible': True}
    ]),
    description='Navigation links on home page'
))

# Add default feature toggles
db.add(FrontendConfig(key='show_logs_modal', value='true', description='System logs modal'))
db.add(FrontendConfig(key='show_login_modal', value='true', description='Login modal'))

db.commit()
print('✅ Default CMS configuration created')
"
```

### Docker Deployment

```yaml
# docker-compose.yml already configured
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/athsys_db
      - REDIS_URL=redis://redis:6379/0
```

---

## 🛠️ Development

### Adding New Configurable Feature

**Step 1**: Identify what should be configurable
**Step 2**: Add JavaScript function in `index.html`:

```javascript
async function applyCustomConfig() {
    const config = await fetch('/api/config/frontend').then(r => r.json());
    
    // Use config
    if (config.config.my_feature === 'show') {
        // Show element
    }
}
```

**Step 3**: Add toggle in `cms-admin.html`:

```html
<tr>
    <td>My Feature</td>
    <td>Show/hide my custom feature</td>
    <td><span class="status-badge status-active">Active</span></td>
    <td>
        <label class="switch">
            <input type="checkbox" checked onchange="toggleFeature('my_feature')">
            <span class="slider"></span>
        </label>
    </td>
</tr>
```

**Step 4**: Toggle from admin panel!

---

## 📊 Monitoring & Debugging

### Check Current Config

```bash
curl https://ath.appstore.co.ke/api/config/frontend | python -m json.tool
```

### View Audit Log

```bash
# Via database
SELECT * FROM audit_logs WHERE entity_type = 'FrontendConfig' ORDER BY created_at DESC LIMIT 20;
```

### Frontend Console

Open browser DevTools (F12) and check:

```javascript
// See loaded config
console.log(frontendConfig);

// Manually refresh config
loadFrontendConfig();
```

---

## 🎓 Best Practices

1. **Test Changes Locally First** - Use localhost:5000 before deploying
2. **Document Your Configs** - Fill in description field for clarity
3. **Use Version Control** - Export/backup configs before major changes
4. **Monitor Audit Trail** - Review who changed what and when
5. **Plan Rollback** - Keep previous configurations in case of issues
6. **Communicate Changes** - Inform users of significant frontend changes

---

## ⚠️ Limitations & Notes

- Configuration changes take effect **on next page reload**
- Cached content may take time to update (check Ctrl+Shift+Delete)
- Admin panel requires authentication (add auth check to cms-admin.html)
- JSON values must be valid JSON in database
- Navigation URL validation is basic (test links work before saving)

---

## 📞 Support

### Troubleshooting

**Links not appearing?**
- Check FrontendConfig table has data
- Verify `/api/config/frontend` returns data
- Clear browser cache (Ctrl+Shift+Delete)

**Feature toggle not working?**
- Ensure admin is logged in
- Check browser console for JS errors
- Verify token hasn't expired

**Admin panel not loading?**
- Must be logged in as admin role
- Check localStorage has authToken
- Open browser console for errors

---

## 📋 API Response Examples

### Navigation Links Response

```json
{
  "config": {
    "nav_links": [
      {
        "label": "Home",
        "url": "/",
        "visible": true
      },
      {
        "label": "Features",
        "url": "#features",
        "visible": true
      },
      {
        "label": "System Logs",
        "url": "#logs",
        "visible": true
      }
    ]
  }
}
```

### Feature Toggle Response

```json
{
  "feature": "logs_modal",
  "enabled": true,
  "message": "✅ Feature \"logs_modal\" enabled"
}
```

---

## 🎯 Next Steps

1. **Access CMS Admin**: Login → Visit `/cms-admin.html`
2. **Test Navigation**: Add a new navigation link
3. **Test Features**: Toggle a feature off and refresh
4. **Monitor Logs**: Check audit trail in database
5. **Deploy**: Update production config as needed

---

**Version**: v2.2.0  
**Last Updated**: February 22, 2026  
**Status**: ✅ Production Ready

