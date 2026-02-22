# Page Builder System - Complete Documentation

## Overview

The AthSys Page Builder is a complete visual page building system that allows administrators to create, manage, and customize pages, themes, menus, and components without writing code.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Database Models](#database-models)
4. [API Reference](#api-reference)
5. [Frontend Interfaces](#frontend-interfaces)
6. [Getting Started](#getting-started)
7. [User Guide](#user-guide)
8. [Developer Guide](#developer-guide)
9. [Testing](#testing)
10. [Deployment](#deployment)

---

## Features

### ✅ Complete Feature Set

- **Visual Page Builder**: Drag-and-drop interface for building pages
- **Theme Management**: Create and customize themes with colors, fonts, and styles
- **Menu Builder**: Build hierarchical navigation menus
- **Component Library**: Reusable UI components and blocks
- **Version Control**: Track page changes with version history
- **Role-Based Access**: Secure permissions for admin/moderator users
- **Responsive Design**: Mobile-first, responsive interfaces
- **Real-time Preview**: Live preview of changes
- **SEO Optimization**: Meta tags, descriptions, and slugs
- **Publishing Workflow**: Draft, review, and publish states

---

## Architecture

### Technology Stack

**Backend:**
- Python 3.9+
- Flask (Web Framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)

**Frontend:**
- HTML5, CSS3, JavaScript (Vanilla)
- Responsive Grid Layout
- Drag-and-Drop API

### System Components

```
┌─────────────────────────────────────────────────┐
│              Frontend Layer                      │
├─────────────────┬───────────────────────────────┤
│ Page Builder    │ Theme Customizer              │
│ Menu Builder    │ Component Library             │
└─────────────────┴───────────────────────────────┘
                        ↓ HTTP/REST API
┌─────────────────────────────────────────────────┐
│              Backend Layer                       │
├─────────────────┬───────────────────────────────┤
│ Routes Module   │ Permission Decorators         │
│ (builder.py)    │ (token_required, etc.)        │
└─────────────────┴───────────────────────────────┘
                        ↓ SQLAlchemy ORM
┌─────────────────────────────────────────────────┐
│              Database Layer                      │
├──────────────────────────────────────────────────┤
│ Pages | Sections | Blocks | Themes | Menus     │
│ MenuItems | Components | Versions               │
└─────────────────────────────────────────────────┘
```

---

## Database Models

### PageBuilder Model

Represents a page in the system.

```python
class PageBuilder(Base):
    __tablename__ = 'page_builder'
    
    id: int                      # Primary key
    title: str                   # Page title
    slug: str                    # URL-friendly identifier (unique)
    description: str             # Meta description
    status: str                  # draft, published, archived
    theme_id: int               # Associated theme
    menu_id: int                # Associated menu
    is_homepage: bool           # Homepage flag
    layout: str                 # Layout type
    custom_css: str             # Custom CSS
    custom_js: str              # Custom JavaScript
    meta_tags: str              # JSON - SEO meta tags
    og_tags: str                # JSON - Open Graph tags
    created_by: int             # Creator user ID
    updated_by: int             # Last updater user ID
    published_at: datetime      # Publication timestamp
    created_at: datetime        # Creation timestamp
    updated_at: datetime        # Last update timestamp
    
    # Relationships
    sections: List[PageSection]
    versions: List[PageVersion]
```

### PageSection Model

Represents a section within a page.

```python
class PageSection(Base):
    __tablename__ = 'page_sections'
    
    id: int                     # Primary key
    page_id: int               # Parent page ID
    name: str                  # Section name
    type: str                  # header, content, footer, etc.
    position: int              # Display order
    columns: int               # Grid columns
    styles: str                # JSON - CSS styles
    settings: str              # JSON - Section settings
    is_visible: bool           # Visibility flag
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    blocks: List[PageBlock]
```

### PageBlock Model

Represents a content block within a section.

```python
class PageBlock(Base):
    __tablename__ = 'page_blocks'
    
    id: int                    # Primary key
    section_id: int           # Parent section ID
    block_type: str           # text, image, video, button, etc.
    content: str              # JSON - Block content
    position: int             # Display order
    width: str                # CSS width
    height: str               # CSS height
    styles: str               # JSON - CSS styles
    settings: str             # JSON - Block settings
    grid_column: str          # CSS grid column
    grid_row: str             # CSS grid row
    is_visible: bool          # Visibility flag
    created_at: datetime
    updated_at: datetime
```

### Theme Model

Manages site themes and styling.

```python
class Theme(Base):
    __tablename__ = 'themes'
    
    id: int                   # Primary key
    name: str                 # Theme name
    description: str          # Theme description
    is_active: bool          # Active theme flag
    colors: str              # JSON - Color palette
    fonts: str               # JSON - Font settings
    spacing: str             # JSON - Spacing values
    border_radius: str       # Border radius
    shadow: str              # Box shadow
    custom_css: str          # Additional CSS
    created_by: int
    updated_by: int
    created_at: datetime
    updated_at: datetime
```

### Menu & MenuItem Models

Manages navigation menus.

```python
class Menu(Base):
    __tablename__ = 'menus'
    
    id: int
    name: str
    location: str            # header, footer, sidebar
    description: str
    display_type: str        # horizontal, vertical, dropdown
    is_visible: bool
    created_by: int
    updated_by: int
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    items: List[MenuItem]

class MenuItem(Base):
    __tablename__ = 'menu_items'
    
    id: int
    menu_id: int
    label: str
    url: str
    icon: str
    position: int
    parent_id: int           # For nested items
    is_visible: bool
    open_in_new_tab: bool
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    children: List[MenuItem]
```

### ComponentLibraryItem Model

Stores reusable components.

```python
class ComponentLibraryItem(Base):
    __tablename__ = 'component_library'
    
    id: int
    name: str
    category: str            # hero, card, form, button, etc.
    description: str
    thumbnail: str           # Preview image URL
    template: str            # JSON - Component structure
    default_content: str     # JSON - Default content
    styles: str              # JSON - Default styles
    is_system: bool          # System component (non-deletable)
    is_featured: bool
    created_by: int
    updated_by: int
    created_at: datetime
    updated_at: datetime
```

---

## API Reference

### Authentication

All endpoints require authentication via Bearer token:

```http
Authorization: Bearer <token>
X-User-ID: <user_id>
X-User-Role: <role>
```

Write operations require `admin` or `moderator` role.

### Page Endpoints

#### List Pages
```http
GET /api/builder/pages
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Home Page",
      "slug": "home",
      "status": "published",
      "isHomepage": true,
      "createdAt": "2024-01-20T10:00:00Z"
    }
  ]
}
```

#### Get Page
```http
GET /api/builder/pages/<page_id>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Home Page",
    "sections": [
      {
        "id": 1,
        "name": "Hero Section",
        "blocks": [...]
      }
    ]
  }
}
```

#### Create Page
```http
POST /api/builder/pages
Content-Type: application/json

{
  "title": "New Page",
  "slug": "new-page",
  "description": "Page description",
  "status": "draft",
  "isHomepage": false
}
```

#### Update Page
```http
PUT /api/builder/pages/<page_id>
Content-Type: application/json

{
  "title": "Updated Page",
  "status": "published"
}
```

#### Delete Page
```http
DELETE /api/builder/pages/<page_id>
```

#### Publish Page
```http
POST /api/builder/pages/<page_id>/publish
```

### Section Endpoints

#### Add Section to Page
```http
POST /api/builder/pages/<page_id>/sections
Content-Type: application/json

{
  "name": "Header Section",
  "type": "header",
  "position": 1,
  "columns": 3,
  "styles": "{\"background\": \"#fff\"}"
}
```

#### Update Section
```http
PUT /api/builder/sections/<section_id>
Content-Type: application/json

{
  "name": "Updated Section",
  "columns": 4
}
```

#### Delete Section
```http
DELETE /api/builder/sections/<section_id>
```

### Block Endpoints

#### Add Block to Section
```http
POST /api/builder/sections/<section_id>/blocks
Content-Type: application/json

{
  "blockType": "text",
  "content": "{\"text\": \"Hello World\"}",
  "position": 1,
  "gridColumn": "1 / -1"
}
```

#### Update Block
```http
PUT /api/builder/blocks/<block_id>
Content-Type: application/json

{
  "content": "{\"text\": \"Updated content\"}",
  "styles": "{\"color\": \"red\"}"
}
```

#### Delete Block
```http
DELETE /api/builder/blocks/<block_id>
```

### Theme Endpoints

#### List Themes
```http
GET /api/builder/themes
```

#### Create Theme
```http
POST /api/builder/themes
Content-Type: application/json

{
  "name": "Ocean Blue",
  "description": "A calming blue theme",
  "colors": "{\"primary\": \"#0077be\", \"secondary\": \"#00a8cc\"}",
  "fonts": "{\"body\": \"Arial, sans-serif\"}",
  "spacing": "{\"padding\": \"1rem\"}"
}
```

#### Update Theme
```http
PUT /api/builder/themes/<theme_id>
Content-Type: application/json

{
  "name": "Updated Theme",
  "isActive": true
}
```

#### Delete Theme
```http
DELETE /api/builder/themes/<theme_id>
```

### Menu Endpoints

#### List Menus
```http
GET /api/builder/menus
```

#### Create Menu
```http
POST /api/builder/menus
Content-Type: application/json

{
  "name": "Main Menu",
  "location": "header",
  "displayType": "horizontal",
  "isVisible": true
}
```

#### Update Menu
```http
PUT /api/builder/menus/<menu_id>
Content-Type: application/json

{
  "name": "Updated Menu",
  "location": "footer"
}
```

#### Delete Menu
```http
DELETE /api/builder/menus/<menu_id>
```

#### Add Menu Item
```http
POST /api/builder/menus/<menu_id>/items
Content-Type: application/json

{
  "label": "Home",
  "url": "/",
  "icon": "home",
  "position": 1,
  "parentId": null
}
```

#### Update Menu Item
```http
PUT /api/builder/menu-items/<item_id>
Content-Type: application/json

{
  "label": "About Us",
  "url": "/about"
}
```

#### Delete Menu Item
```http
DELETE /api/builder/menu-items/<item_id>
```

### Component Endpoints

#### List Components
```http
GET /api/builder/components
```

#### List Components by Category
```http
GET /api/builder/components/category/<category>
```

#### Create Component
```http
POST /api/builder/components
Content-Type: application/json

{
  "name": "Hero Banner",
  "category": "hero",
  "description": "A prominent hero section",
  "template": "{\"type\": \"hero\", \"elements\": [...]}",
  "defaultContent": "{\"heading\": \"Welcome\"}",
  "isFeatured": true
}
```

#### Update Component
```http
PUT /api/builder/components/<component_id>
Content-Type: application/json

{
  "name": "Updated Component",
  "isFeatured": false
}
```

#### Delete Component
```http
DELETE /api/builder/components/<component_id>
```

---

## Frontend Interfaces

### 1. Page Builder (`page-builder.html`)

The main visual page building interface.

**Features:**
- Three-panel layout (Components | Canvas | Properties)
- Drag-and-drop component placement
- Real-time preview
- Section and block management
- Inline content editing
- Responsive controls
- Theme and menu selection
- Save/publish workflow

**Usage:**
1. Navigate to `/page-builder.html`
2. Select a page or create a new one
3. Drag components from the left sidebar
4. Configure properties in the right sidebar
5. Save as draft or publish

### 2. Theme Customizer (`theme-customizer.html`)

Theme creation and customization interface.

**Features:**
- Color picker for all theme colors
- Font family and size selectors
- Spacing controls
- Border radius and shadow settings
- Custom CSS editor
- Real-time preview
- Active theme switcher

**Usage:**
1. Navigate to `/theme-customizer.html`
2. Select existing theme or create new
3. Customize colors, fonts, spacing
4. Add custom CSS if needed
5. Preview changes
6. Save and activate theme

### 3. Menu Builder (`menu-builder.html`)

Navigation menu management interface.

**Features:**
- Menu CRUD operations
- Nested menu item support
- Drag-and-drop reordering
- Icon selection
- URL configuration
- Location and display type settings
- Visibility controls

**Usage:**
1. Navigate to `/menu-builder.html`
2. Create or select a menu
3. Add menu items
4. Configure labels, URLs, and icons
5. Drag to reorder or nest items
6. Set visibility and save

### 4. Component Library (`component-library.html`)

Reusable component management interface.

**Features:**
- Component browsing by category
- Component CRUD operations
- Template and content editors
- Thumbnail upload
- Featured component flagging
- Search and filter
- System component protection

**Usage:**
1. Navigate to `/component-library.html`
2. Browse or search components
3. Create new component
4. Define template structure
5. Set default content and styles
6. Save to library

---

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/athsys.git
   cd athsys
   ```

2. **Install dependencies:**
   ```bash
   cd src/backend
   pip install -r requirements.txt
   ```

3. **Configure database:**
   ```bash
   # Edit models.py and set DATABASE_URL
   export DATABASE_URL="postgresql://user:pass@localhost:5432/athsys_db"
   ```

4. **Initialize database:**
   ```python
   from models import init_db
   init_db()
   ```

5. **Start the server:**
   ```bash
   python app.py
   ```

6. **Access the interface:**
   - Page Builder: `http://localhost:5000/page-builder.html`
   - Theme Customizer: `http://localhost:5000/theme-customizer.html`
   - Menu Builder: `http://localhost:5000/menu-builder.html`
   - Component Library: `http://localhost:5000/component-library.html`

---

## User Guide

### Creating Your First Page

1. Open Page Builder
2. Click "Create New Page"
3. Enter page details (title, slug, description)
4. Add sections from the sidebar
5. Drag components into sections
6. Configure block properties
7. Save as draft
8. Preview and publish

### Creating a Custom Theme

1. Open Theme Customizer
2. Click "Create New Theme"
3. Set primary and secondary colors
4. Choose fonts for body and headings
5. Adjust spacing and borders
6. Add custom CSS if needed
7. Preview in different contexts
8. Save and activate

### Building a Navigation Menu

1. Open Menu Builder
2. Click "Create Menu"
3. Set menu name and location
4. Add menu items one by one
5. Drag items to reorder or create hierarchy
6. Set icons and external link flags
7. Toggle visibility
8. Save menu

### Managing Components

1. Open Component Library
2. Browse existing components
3. Click "Create Component" for new ones
4. Define component structure (template)
5. Set default content and styles
6. Upload thumbnail image
7. Mark as featured if desired
8. Save to library

---

## Developer Guide

### Project Structure

```
AthSys_ver1/
├── src/
│   ├── backend/
│   │   ├── app.py                 # Main Flask app
│   │   ├── models.py              # Database models
│   │   ├── routes/
│   │   │   └── builder.py         # Page builder routes
│   │   └── requirements.txt
│   └── frontend/
│       ├── page-builder.html      # Page builder UI
│       ├── theme-customizer.html  # Theme UI
│       ├── menu-builder.html      # Menu UI
│       └── component-library.html # Component UI
├── tests/
│   └── test_page_builder.py       # Test suite
├── docs/
│   └── PAGE_BUILDER.md            # This file
└── README.md
```

### Adding a New Block Type

1. **Update the component palette** in `page-builder.html`:
   ```javascript
   const blockTypes = [
       { type: 'text', icon: '📝', label: 'Text' },
       { type: 'image', icon: '🖼️', label: 'Image' },
       { type: 'custom', icon: '⚙️', label: 'Custom' }  // New type
   ];
   ```

2. **Add block rendering logic**:
   ```javascript
   function renderBlock(block) {
       switch(block.blockType) {
           case 'custom':
               return renderCustomBlock(block);
           // ... other cases
       }
   }
   ```

3. **Add property panel fields**:
   ```javascript
   function renderBlockProperties(block) {
       if (block.blockType === 'custom') {
           return `
               <div class="property-group">
                   <label>Custom Setting:</label>
                   <input type="text" value="${block.customSetting}">
               </div>
           `;
       }
   }
   ```

### Creating a Custom Component

Components are JSON objects with the following structure:

```json
{
  "name": "Call to Action",
  "category": "marketing",
  "description": "A prominent CTA section",
  "template": {
    "type": "cta",
    "elements": [
      {
        "tag": "div",
        "class": "cta-container",
        "children": [
          {
            "tag": "h2",
            "class": "cta-heading",
            "editable": true
          },
          {
            "tag": "button",
            "class": "cta-button",
            "editable": true
          }
        ]
      }
    ]
  },
  "defaultContent": {
    "heading": "Ready to Get Started?",
    "button": "Sign Up Now"
  },
  "styles": {
    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "padding": "4rem 2rem",
    "textAlign": "center",
    "color": "#ffffff"
  }
}
```

### Extending the API

To add a new endpoint:

1. **Define the route** in `routes/builder.py`:
   ```python
   @builder_bp.route('/custom-endpoint', methods=['POST'])
   @token_required
   @admin_or_moderator_required
   def custom_endpoint():
       try:
           data = request.get_json()
           # Process data
           return jsonify({'success': True, 'data': result}), 200
       except Exception as e:
           return jsonify({'error': str(e)}), 500
   ```

2. **Update the frontend** to call the new endpoint:
   ```javascript
   async function callCustomEndpoint(data) {
       const response = await fetch('/api/builder/custom-endpoint', {
           method: 'POST',
           headers: {
               'Authorization': `Bearer ${token}`,
               'Content-Type': 'application/json'
           },
           body: JSON.stringify(data)
       });
       return await response.json();
   }
   ```

---

## Testing

### Running Tests

```bash
cd tests
python test_page_builder.py
```

### Test Coverage

The test suite covers:
- ✅ Theme CRUD operations
- ✅ Menu CRUD operations
- ✅ Menu item management
- ✅ Component CRUD operations
- ✅ Page CRUD operations
- ✅ Section management
- ✅ Block management
- ✅ Permission checks
- ✅ Authorization

### Writing Tests

Example test case:

```python
def test_create_page(self):
    """Test creating a new page"""
    page_data = {
        'title': 'Test Page',
        'slug': 'test-page',
        'status': 'draft'
    }
    
    response = self.client.post('/api/builder/pages',
                               data=json.dumps(page_data),
                               headers=self.headers)
    
    self.assertEqual(response.status_code, 201)
    data = json.loads(response.data)
    self.assertTrue(data['success'])
```

---

## Deployment

### Production Checklist

- [ ] Set strong passwords and secrets
- [ ] Use HTTPS for all connections
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Enable rate limiting
- [ ] Configure logging and monitoring
- [ ] Set up CDN for static assets
- [ ] Optimize database queries
- [ ] Enable database connection pooling
- [ ] Set up error tracking (Sentry, etc.)

### Environment Variables

```bash
# Database
export DATABASE_URL="postgresql://user:pass@localhost:5432/athsys_prod"

# Security
export SECRET_KEY="your-secret-key-here"
export JWT_SECRET="your-jwt-secret-here"

# Application
export FLASK_ENV="production"
export DEBUG="False"

# CORS
export CORS_ORIGINS="https://yourdomain.com"
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

```bash
# Build and run
docker build -t athsys-builder .
docker run -p 5000:5000 --env-file .env athsys-builder
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/athsys
    depends_on:
      - db
  
  db:
    image: postgres:12
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=athsys
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

---

## Troubleshooting

### Common Issues

**Issue: "Permission denied" errors**
- **Solution**: Ensure user has admin or moderator role
- Check `X-User-Role` header is set correctly

**Issue: Pages not saving**
- **Solution**: Check database connection
- Verify `DATABASE_URL` is correct
- Check database user has write permissions

**Issue: Frontend not connecting to API**
- **Solution**: Check CORS configuration
- Verify API URL is correct
- Check authentication token is valid

**Issue: Components not appearing**
- **Solution**: Clear browser cache
- Check component is marked as visible
- Verify component category is correct

---

## FAQ

**Q: Can I use custom HTML in blocks?**
A: Yes, use the "HTML" block type and enter custom HTML in the content editor.

**Q: How many themes can I create?**
A: Unlimited themes, but only one can be active at a time.

**Q: Can I export/import components?**
A: Not currently, but this feature is planned for a future release.

**Q: Is there a limit to page size?**
A: No hard limit, but very large pages may impact performance.

**Q: Can non-admin users view pages?**
A: Yes, published pages are viewable by all users. Only editing requires admin/moderator role.

---

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/yourusername/athsys/issues
- Email: support@athsys.com
- Documentation: https://docs.athsys.com

---

## License

Copyright © 2024 AthSys. All rights reserved.

---

## Changelog

### Version 1.0.0 (2024-01-20)
- ✅ Initial release
- ✅ Complete page builder system
- ✅ Theme customizer
- ✅ Menu builder
- ✅ Component library
- ✅ Role-based permissions
- ✅ Comprehensive test suite
- ✅ Complete documentation

---

**Last Updated:** January 20, 2024  
**Version:** 1.0.0  
**Status:** Production Ready ✅
