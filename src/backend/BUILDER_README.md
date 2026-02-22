# Page Builder System - Complete Guide

## Overview

The Page Builder System is a comprehensive, WordPress/Elementor-style visual page editor that allows administrators and moderators to create, manage, and customize pages without writing code.

## Features

### 🎯 Page Builder
- **Visual Canvas**: Drag-and-drop interface to build pages from reusable components
- **Section Management**: Organize content into logical sections with custom styling
- **Block Components**: Add individual blocks (buttons, cards, forms, galleries) to sections
- **Version Control**: Automatic version history with ability to restore previous versions
- **Draft & Publish**: Save as draft or publish to make live
- **Responsive Design**: Pages automatically adapt to mobile and desktop

### 🎨 Theme Customizer
- **Global Styling**: Define color schemes applied across all pages
- **Typography Control**: Choose fonts for headings and body text
- **Color Management**: Create and switch between multiple themes
- **Live Preview**: See changes in real-time
- **Custom CSS**: Add custom styles for advanced customization

### ☰ Menu Builder
- **Multiple Menus**: Create different menus for header, footer, sidebar
- **Nested Items**: Build hierarchical navigation menus
- **Custom Icons**: Add icons to menu items
- **Display Types**: Choose horizontal, vertical, or dropdown layouts
- **Quick Activation**: Apply menus to pages instantly

### 📚 Component Library
- **Reusable Components**: Create once, use everywhere
- **Template System**: Define default content and styles
- **Organization**: Categorize components (hero, card, form, gallery, etc.)
- **Featured Components**: Mark components for quick access
- **Duplication**: Clone existing components to create variations

## Quick Start

### Accessing the Builder

1. **Navigate to Dashboard**: Visit `/src/frontend/builder-dashboard.html`
2. **Choose Your Tool**:
   - Page Builder (Create and edit pages)
   - Theme Customizer (Design color schemes)
   - Menu Builder (Create navigation)
   - Component Library (Manage components)

### Creating Your First Page

1. Click **"Create New Page"** on the dashboard
2. Enter page title (e.g., "About Us")
3. Enter URL slug (e.g., "about-us")
4. Choose Draft or Published status
5. Click **"Create Page"** → redirects to Page Builder
6. Start adding sections and blocks

### Building a Page

1. **Add Section**: Click "+" in the Sections tab (left panel)
   - Choose section type (Hero, Content Grid, Gallery, etc.)
   - Customize background color, height, layout

2. **Add Blocks**: Drag components from Library panel into the section
   - Drag components from left panel to canvas
   - Drop into section drop zones
   - Click to select and edit properties

3. **Edit Block Content**: 
   - Click on a block in the canvas
   - Use the Inspector panel (right) to edit:
     - Text content
     - Colors and styling
     - Links and buttons
     - Visual properties

4. **Manage Structure**:
   - Delete sections/blocks with the delete button
   - Reorder blocks by dragging
   - See sections in the canvas outline

5. **Save Your Work**:
   - Click "Save Draft" for unpublished changes
   - Click "Publish" to make live

### Working with Themes

1. **Create Theme**:
   - Open Theme Customizer
   - Click "Create New Theme"
   - Customize:
     - Primary color (main brand color)
     - Secondary color (accents)
     - Text color
     - Background color
   - Choose typography for headings and body

2. **Apply Theme to Page**:
   - In Page Builder, click "Theme" button
   - Select a theme from the list
   - Theme applies immediately

3. **Manage Themes**:
   - Edit existing themes
   - Set active theme
   - Delete unused themes

### Managing Menus

1. **Create Menu**:
   - Open Menu Builder
   - Click "Create New Menu"
   - Set name, location (header/footer/sidebar), display type

2. **Add Menu Items**:
   - Enter label (what users see)
   - Enter URL (where it links)
   - Optional: Add icon
   - Click "Add Item"

3. **Organize Menu**:
   - Reorder items (future drag-drop)
   - Create nested menus (parent/child items)
   - Edit or delete items

4. **Apply to Page**:
   - In Page Builder, click "Menu" button
   - Select menu to display in section

### Component Library

1. **View Components**:
   - Open Component Library
   - See all available components in grid
   - Filter by category (hero, card, form, gallery, etc.)
   - Search by name

2. **Create Component**:
   - Click "Create Component"
   - Fill in name, category, description
   - Define JSON template structure
   - Set default content
   - Mark as featured if commonly used

3. **Use Components**:
   - Components appear in Library tab in Page Builder
   - Drag into canvas to use
   - Each use is independent (editing one doesn't affect others)

## API Endpoints

### Pages
- `GET /api/builder/pages` - List all pages
- `GET /api/builder/pages/{id}` - Get page details
- `POST /api/builder/pages` - Create new page
- `PUT /api/builder/pages/{id}` - Update page
- `DELETE /api/builder/pages/{id}` - Delete page
- `POST /api/builder/pages/{id}/publish` - Publish page

### Sections
- `POST /api/builder/pages/{id}/sections` - Add section to page
- `PUT /api/builder/sections/{id}` - Update section
- `DELETE /api/builder/sections/{id}` - Delete section

### Blocks
- `POST /api/builder/sections/{id}/blocks` - Add block to section
- `PUT /api/builder/blocks/{id}` - Update block
- `DELETE /api/builder/blocks/{id}` - Delete block

### Themes
- `GET /api/builder/themes` - List themes
- `POST /api/builder/themes` - Create theme
- `PUT /api/builder/themes/{id}` - Update theme
- `DELETE /api/builder/themes/{id}` - Delete theme

### Menus
- `GET /api/builder/menus` - List menus
- `POST /api/builder/menus` - Create menu
- `PUT /api/builder/menus/{id}` - Update menu
- `DELETE /api/builder/menus/{id}` - Delete menu
- `POST /api/builder/menus/{id}/items` - Add menu item
- `PUT /api/builder/menu-items/{id}` - Update menu item
- `DELETE /api/builder/menu-items/{id}` - Delete menu item

### Components
- `GET /api/builder/components` - List all components
- `GET /api/builder/components/category/{category}` - Filter by category
- `POST /api/builder/components` - Create component
- `PUT /api/builder/components/{id}` - Update component
- `DELETE /api/builder/components/{id}` - Delete component

### Versions
- `GET /api/builder/pages/{id}/versions` - Get version history
- `POST /api/builder/pages/{id}/versions/{version_id}/restore` - Restore version

## Access Control

The builder system has role-based access:

- **Admin**: Full access to all builder features
- **Moderator**: Full access to all builder features
- **Members**: No access (protected)
- **Public**: Can view published pages

## Database Schema

### PageBuilder (pages)
```
id, title, slug, description, status (draft/published),
theme_id (foreign key), menu_id, layout_data (JSON),
metadata (JSON), created_at, updated_at
```

### PageSection
```
id, page_id, section_type (hero/content/grid/gallery/form/contact),
column_count, background_color, styles (JSON),
position, created_at, updated_at
```

### PageBlock (individual components)
```
id, section_id, block_type, content (JSON),
styles (JSON), width, visibility, position, created_at, updated_at
```

### Theme
```
id, name, colors (JSON: primary, secondary, text, bg),
fonts (JSON: body, heading), spacing (JSON),
border_radius, custom_css, is_active, created_at, updated_at
```

### Menu
```
id, name, location (header/footer/sidebar/mobile),
display_type (horizontal/vertical/dropdown),
items relationship, created_at, updated_at
```

### MenuItem
```
id, menu_id, label, url, icon, position,
parent_id (for nested items), openInNewTab, created_at, updated_at
```

### ComponentLibraryItem
```
id, name, category, description, template (JSON),
defaultContent (JSON), styles (JSON),
thumbnail, is_system, is_featured, created_at, updated_at
```

### PageVersion (undo/redo)
```
id, page_id, version_number, layout_data (JSON snapshot),
created_by, created_at
```

## Best Practices

### Page Structure
1. Use **Hero sections** at the top for impact
2. Use **Content sections** for text and mixed content
3. Use **Grid sections** for showcasing multiple items
4. Use **Gallery sections** for images
5. Use **Contact sections** for forms at the bottom

### Component Design
- Create small, focused components (buttons, cards)
- Use meaningful defaults
- Document intended use (in description)
- Test across responsive sizes

### Theme Management
- Create themes that match brand identity
- Test theme on different page types
- Document color meanings (primary = main, secondary = accent)
- Keep consistent typography across themes

### Menu Organization
- Keep main navigation simple (5-7 items)
- Use nesting for sub-categories
- Use descriptive labels
- Test menu on mobile (ensure dropdowns work)

## Troubleshooting

### Page not saving?
- Check browser console for errors
- Verify user has admin/moderator role
- Check network tab to see API responses

### Components not appearing?
- Refresh page-builder.html
- Check Components Library has components
- Verify component category is correct

### Styling not applying?
- Clear browser cache
- Check theme is activated
- Verify custom CSS syntax

### Menu not visible?
- Check menu is assigned to page
- Verify menu location is correct
- Check menu has items added

## Future Enhancements

Potential features for future versions:
- [ ] Drag-to-reorder sections/blocks
- [ ] Undo/Redo UI buttons
- [ ] Template browser (pre-made page layouts)
- [ ] Advanced block options (spacing, padding, animations)
- [ ] SEO management (meta tags, sitemap)
- [ ] A/B testing (compare page versions)
- [ ] Export pages as static HTML
- [ ] Scheduled publishing (publish at specific date/time)

## Support

For issues or questions:
1. Check the [API Endpoints](#api-endpoints) section
2. Review browser console for JavaScript errors
3. Check browser network tab for API errors
4. Consult the [Database Schema](#database-schema) for data structure
5. Refer to [Access Control](#access-control) for permission issues
