# AthSys Demo Credentials

## 🔑 Login Instructions

Visit **https://athsys.appstore.co.ke/login.html** and use any of these demo accounts:

---

## 👑 Admin Account
**Full system access - User management, system configuration**

- **Email:** `admin@athsys.com`
- **Password:** `Admin@123`
- **Dashboard:** `admin.html`

**Capabilities:**
- ✅ Manage all users and roles
- ✅ System configuration
- ✅ View all dashboards
- ✅ Full CRUD operations
- ✅ Security settings

---

## 📋 Chief Registrar Account
**Race operations and event management**

- **Email:** `chief@athsys.com`
- **Password:** `Chief@123`
- **Dashboard:** `operations.html`

**Capabilities:**
- ✅ Create and manage races
- ✅ Create events for races
- ✅ Generate public registration links
- ✅ Upload organization logo
- ✅ Configure race settings

---

## ✍️ Registrar Account
**Athlete registration and data entry**

- **Email:** `registrar@athsys.com`
- **Password:** `Registrar@123`
- **Dashboard:** `operations.html`

**Capabilities:**
- ✅ Register athletes manually
- ✅ Bulk upload via Excel
- ✅ View all registrations
- ✅ Confirm/cancel registrations
- ✅ Download registration reports

---

## 🎯 Starter Account
**Start list management and race starts**

- **Email:** `starter@athsys.com`
- **Password:** `Starter@123`
- **Dashboard:** `starter.html`

**Capabilities:**
- ✅ View start lists by race/event
- ✅ Check athlete presence (present/absent)
- ✅ Confirm start lists
- ✅ View confirmed start list history
- ✅ Real-time athlete statistics

---

## 🏅 Coach Account
**Team and athlete management**

- **Email:** `sarah@athsys.com`
- **Password:** `Coach@123`
- **Dashboard:** TBD

**Capabilities:**
- ✅ Manage team athletes
- ✅ View athlete performance
- ✅ Track team registrations
- ✅ View race results

---

## 🏃 Athlete Account
**Personal profile and race registration**

- **Email:** `john@athsys.com`
- **Password:** `Athlete@123`
- **Dashboard:** TBD

**Capabilities:**
- ✅ View personal records
- ✅ Register for races
- ✅ View race results
- ✅ Track personal statistics

---

## 👁️ Viewer Account (Read-Only)
**System monitoring and reporting**

- **Email:** `viewer@athsys.com`
- **Password:** `Viewer@123`
- **Dashboard:** TBD

**Capabilities:**
- ✅ View all data (read-only)
- ✅ Generate reports
- ✅ Export data
- ❌ No edit/delete permissions

---

## 🔄 Role-Based Access

The system implements **7 distinct roles** with different permission levels:

1. **Admin** - Full system control
2. **Chief Registrar** - Race and event creation
3. **Registrar** - Athlete registration and data entry
4. **Starter** - Start list confirmation and race starts
5. **Coach** - Team management
6. **Athlete** - Personal profile management
7. **Viewer** - Read-only access

---

## 🚀 Quick Start Workflow

### For Race Management:
1. Login as **Chief Registrar** (`chief@athsys.com`)
2. Create a new race in Operations Dashboard
3. Add events to the race
4. Generate public registration link
5. Share link with athletes

### For Athlete Registration:
1. Login as **Registrar** (`registrar@athsys.com`)
2. Register athletes manually OR
3. Download Excel template
4. Fill Excel with athlete data
5. Bulk upload via Operations Dashboard

### For Race Start:
1. Login as **Starter** (`starter@athsys.com`)
2. Select race and event
3. Check athlete presence (tick checkboxes)
4. Review statistics (total/present/absent)
5. Click "Confirm Start List"

---

## 🔒 Security Notes

**Demo Mode:**
- Passwords are stored in plain text for demo purposes
- In production, passwords should be hashed using bcrypt/argon2
- JWT tokens expire after 24 hours
- All API requests require authentication token

**Password Requirements:**
- Minimum 6 characters
- Must include: uppercase, lowercase, number, special character
- Example format: `Admin@123`

---

## 📊 System Features

**Dynamic Features (After Login):**
- Real-time statistics updates
- Role-based UI rendering
- Interactive dashboards
- Toast notifications
- Excel bulk operations
- Public registration links
- Start list confirmation
- User management (admin only)

**Static Landing Page:**
- System overview
- Feature showcase
- API information
- Quick access credentials
- Login/Dashboard buttons

---

## 🛠️ Testing Different Roles

To see role-based differences:

1. **Login as Admin** - See user management panel
2. **Login as Chief Registrar** - See race creation options
3. **Login as Registrar** - See registration interface (no race creation)
4. **Login as Starter** - See start list confirmation only
5. **Compare dashboards** - Notice different permissions per role

---

## 📱 Direct Access URLs

After deployment:

- **Landing Page:** `https://athsys.appstore.co.ke/`
- **Login:** `https://athsys.appstore.co.ke/login.html`
- **Admin Dashboard:** `https://athsys.appstore.co.ke/admin.html`
- **Operations:** `https://athsys.appstore.co.ke/operations.html`
- **Starter Dashboard:** `https://athsys.appstore.co.ke/starter.html`
- **Public Registration:** `https://athsys.appstore.co.ke/public-register.html?link=pub_race_xxx`
- **API Info:** `https://athsys.appstore.co.ke/api/info`
- **Health Check:** `https://athsys.appstore.co.ke/livez`

---

## 💡 Tips

1. **Use Chrome DevTools** to see API requests/responses
2. **Check localStorage** to view JWT tokens
3. **Try different roles** to understand permission system
4. **Use Excel bulk upload** to register multiple athletes quickly
5. **Generate public link** to test athlete self-registration
6. **Confirm start lists** to see real-time statistics

---

**Need Help?** Check the main [README.md](../README.md) for system architecture and deployment instructions.
