# 📁 Builder System - File Structure & Reference

## 📍 Quick File Locations

### Start Here (Documents in Root)
```
c:\projects\AthSys_ver1\
├── START_HERE_BUILDER.md          ← Read this first (5 min)
├── BUILDER_STATUS.md              ← System status overview
├── BUILDER_VERIFICATION.md        ← Testing checklist
├── BUILDER_IMPLEMENTATION.md      ← Architecture details
└── README.md                       ← Project overview
```

---

## 🗂️ Backend Files

### API Routes
```
c:\projects\AthSys_ver1\src\backend\routes\
└── builder.py (588 lines)
    ├── Pages API (6 endpoints)
    ├── Sections API (3 endpoints)
    ├── Blocks API (3 endpoints)
    ├── Themes API (4 endpoints)
    ├── Menus API (4 endpoints)
    ├── Menu Items API (3 endpoints)
    ├── Components API (5 endpoints)
    └── Versions API (2 endpoints)
```

### Models
```
c:\projects\AthSys_ver1\src\backend\models.py
├── PageBuilder (pages table)
├── PageSection
├── PageBlock
├── Theme
├── Menu
├── MenuItem
├── ComponentLibraryItem
└── PageVersion
```

### Main Application
```
c:\projects\AthSys_ver1\src\backend\app.py
├── Line 23-28: Builder blueprint import
├── Line 115-118: Blueprint registration
└── Line 2281-2285: /builder route
```

### Documentation
```
c:\projects\AthSys_ver1\src\backend\BUILDER_README.md
├── Complete API reference
├── Database schema
├── Feature documentation
├── Best practices
└── Troubleshooting
```

---

## 🎨 Frontend Files

### Dashboard
```
c:\projects\AthSys_ver1\src\frontend\builder-dashboard.html
├── 📊 Stats section (pages, themes, menus, components count)
├── 🎯 4 tool cards (Page Builder, Theme, Menu, Components)
├── 📄 Recent pages list
├── ➕ Create page modal
├── JavaScript (loads stats, recent pages)
└── CSS (responsive grid layout)
```

### Page Builder
```
c:\projects\AthSys_ver1\src\frontend\page-builder.html
├── Three-panel layout:
│   ├── Left: Library & Sections tabs
│   ├── Center: Page canvas
│   └── Right: Properties inspector
├── Features:
│   ├── Drag-drop sections
│   ├── Drag-drop blocks
│   ├── Section management
│   ├── Block editing
│   ├── Theme selector
│   ├── Menu selector
│   ├── Save/Publish buttons
│   └── Version history
└── JavaScript: 1000+ lines managing state & events
```

### Theme Customizer
```
c:\projects\AthSys_ver1\src\frontend\theme-customizer.html
├── Two-panel layout:
│   ├── Left: Theme editor (forms)
│   └── Right: Live preview
├── Features:
│   ├── Color pickers (4 colors)
│   ├── Font family selectors
│   ├── Border radius slider
│   ├── Custom CSS textarea
│   ├── Live preview
│   ├── Theme grid (existing themes)
│   └── Create/Edit/Delete
└── JavaScript: Color management, preview sync
```

### Menu Builder
```
c:\projects\AthSys_ver1\src\frontend\menu-builder.html
├── Two-column layout:
│   ├── Left: Menu list by location
│   └── Right: Menu detail editor
├── Features:
│   ├── Create menu modal
│   ├── Menu properties (name, location, display)
│   ├── Add menu items form
│   ├── Menu items list
│   ├── Edit/delete items
│   └── Nested item support
└── JavaScript: Menu CRUD operations
```

### Component Library
```
c:\projects\AthSys_ver1\src\frontend\component-library.html
├── Grid layout with search bar
├── Features:
│   ├── Component grid (cards)
│   ├── Search & filter
│   ├── Category filter
│   ├── Status filter (featured/system)
│   ├── Create component modal
│   ├── Edit existing components
│   ├── Duplicate components
│   ├── Delete components
│   └── Component metadata
└── JavaScript: Component management
```

### Quick Start Guide
```
c:\projects\AthSys_ver1\src\frontend\BUILDER_QUICKSTART.md
├── 5-minute getting started
├── Step-by-step instructions
├── Common questions
├── Keyboard shortcuts
└── Exercises
```

---

## 📚 Documentation Hierarchy

```
START_HERE_BUILDER.md (You are here!)
    ↓
BUILDER_QUICKSTART.md (5 minutes)
    ↓
BUILDER_README.md (30 minutes)
    ↓
BUILDER_VERIFICATION.md (Testing)
    ↓
BUILDER_IMPLEMENTATION.md (Deep dive)
    ↓
BUILDER_STATUS.md (Overview)
    ↓
FILE_STRUCTURE.md (THIS FILE)
```

---

## 🔗 File Dependencies

```
app.py
├── imports builder_bp from routes/builder.py
│   ├── which imports models from models.py
│   └── which defines 8 new tables
├── serves frontend files from /src/frontend/
│   ├── builder-dashboard.html
│   ├── page-builder.html
│   ├── theme-customizer.html
│   ├── menu-builder.html
│   └── component-library.html
└── has route /builder serving builder-dashboard.html
```

---

## 📊 File Sizes & Line Counts

| File | Location | Lines | Type |
|------|----------|-------|------|
| builder.py | routes/ | 588 | Python |
| page-builder.html | frontend/ | 1000+ | HTML/JS |
| theme-customizer.html | frontend/ | 700+ | HTML/JS |
| menu-builder.html | frontend/ | 600+ | HTML/JS |
| component-library.html | frontend/ | 650+ | HTML/JS |
| builder-dashboard.html | frontend/ | 400+ | HTML/JS |
| models.py | backend/ | 8 models | Python |
| app.py | backend/ | 3 changes | Python |

**Total Backend**: ~600 lines of new code  
**Total Frontend**: ~4000 lines of HTML/JS/CSS  
**Total New Code**: ~4600 lines

---

## 🎯 What Each File Does

### Essential (Must Have)
- **app.py** → Main Flask application, registers builder API
- **models.py** → Database schema definitions
- **builder.py** → All API endpoints (the backend)

### Frontend Tools (User Interfaces)
- **builder-dashboard.html** → Starting point, links to all tools
- **page-builder.html** → Main page editor
- **theme-customizer.html** → Design colors & fonts
- **menu-builder.html** → Create navigation
- **component-library.html** → Manage components

### Documentation (Learning)
- **START_HERE_BUILDER.md** → Getting started
- **BUILDER_QUICKSTART.md** → 5-minute guide
- **BUILDER_README.md** → Complete reference
- **BUILDER_VERIFICATION.md** → Testing checklist
- **BUILDER_IMPLEMENTATION.md** → Architecture
- **BUILDER_STATUS.md** → Status overview

---

## 🔄 File Relationships

```
User Browser
    ↓
Frontend Files (HTML/JS/CSS)
    ↓
Flask Routes in app.py
    ↓
builder.py (API endpoints)
    ↓
models.py (Database objects)
    ↓
PostgreSQL Database
    ↓
Return JSON Response
    ↓
Frontend Updates UI
```

---

## 📝 File Modification Guide

### If you need to...

**Add a new page type**
→ Modify: `builder.py` → Add new route

**Change database fields**
→ Modify: `models.py` → Add new field

**Adjust builder UI**
→ Modify: `page-builder.html` → Edit HTML/CSS/JS

**Add more tools**
→ Create: New HTML file in `/src/frontend/`

**Update documentation**
→ Modify: Relevant `.md` file

**Customize styling**
→ Modify: CSS sections in HTML files

---

## 🔍 Finding Things

### Need to find an endpoint?
→ Open `routes/builder.py` and search for `@app.route`

### Need to find a database model?
→ Open `models.py` and search for `class`

### Need to adjust page builder UI?
→ Open `page-builder.html` and search for relevant HTML ID

### Need to understand a feature?
→ Open `BUILDER_README.md` and search for feature name

### Need API documentation?
→ Open `BUILDER_README.md` and see "API Endpoints"

### Need to test the system?
→ Open `BUILDER_VERIFICATION.md` and follow checklist

---

## 🗂️ Directory Tree

```
AthSys_ver1/
├── START_HERE_BUILDER.md          ← Start here!
├── BUILDER_STATUS.md
├── BUILDER_VERIFICATION.md
├── BUILDER_IMPLEMENTATION.md
├── FILE_STRUCTURE.md (this file)
│
├── src/
│   ├── backend/
│   │   ├── app.py                 ← Modified
│   │   ├── models.py              ← Modified
│   │   ├── BUILDER_README.md       ← Created
│   │   └── routes/
│   │       └── builder.py          ← Created
│   │
│   └── frontend/
│       ├── builder-dashboard.html  ← Created
│       ├── page-builder.html       ← Created
│       ├── theme-customizer.html   ← Created
│       ├── menu-builder.html       ← Created
│       ├── component-library.html  ← Created
│       ├── BUILDER_QUICKSTART.md   ← Created
│       └── [other frontend files]
│
└── [other project files]
```

---

## ✅ File Checklist

### Backend
- [ ] `/src/backend/routes/builder.py` exists
- [ ] `/src/backend/models.py` has 8 new models
- [ ] `/src/backend/app.py` has builder imports
- [ ] `/src/backend/app.py` has blueprint registration
- [ ] `/src/backend/app.py` has /builder route
- [ ] `/src/backend/BUILDER_README.md` exists

### Frontend
- [ ] `/src/frontend/builder-dashboard.html` exists
- [ ] `/src/frontend/page-builder.html` exists
- [ ] `/src/frontend/theme-customizer.html` exists
- [ ] `/src/frontend/menu-builder.html` exists
- [ ] `/src/frontend/component-library.html` exists
- [ ] `/src/frontend/BUILDER_QUICKSTART.md` exists

### Documentation (Root)
- [ ] `START_HERE_BUILDER.md` exists
- [ ] `BUILDER_STATUS.md` exists
- [ ] `BUILDER_VERIFICATION.md` exists
- [ ] `BUILDER_IMPLEMENTATION.md` exists
- [ ] `FILE_STRUCTURE.md` exists (this file)

**All files present?** ✅ Ready to use!

---

## 🎯 Navigation Guide

### To access the builder:
```
Browser → http://localhost:5000/builder
```

### To find API documentation:
```
File → /src/backend/BUILDER_README.md
CLI → http://localhost:5000/api/docs
```

### To understand the system:
```
File → BUILDER_IMPLEMENTATION.md
File → BUILDER_QUICKSTART.md
```

### To test everything:
```
File → BUILDER_VERIFICATION.md
```

### To get started immediately:
```
File → START_HERE_BUILDER.md
```

---

## 📞 File Reference Quick Links

| Need Help With | Check This File |
|---|---|
| Getting started | START_HERE_BUILDER.md |
| Creating your first page | BUILDER_QUICKSTART.md |
| All features & API | BUILDER_README.md |
| System status & metrics | BUILDER_STATUS.md |
| Testing & verification | BUILDER_VERIFICATION.md |
| Architecture & design | BUILDER_IMPLEMENTATION.md |
| File locations & structure | This file (FILE_STRUCTURE.md) |

---

## 🚀 Next Steps

1. **Read**: START_HERE_BUILDER.md (5 min)
2. **Start**: Flask app in terminal
3. **Access**: http://localhost:5000/builder
4. **Create**: Your first page
5. **Explore**: All the builder tools

---

**All files organized and documented!** 🎊
