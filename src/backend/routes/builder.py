"""
Page Builder API Routes
Handles page, theme, menu, and component management
"""

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from functools import wraps
import json

from models import (
    PageBuilder, PageSection, PageBlock, Theme, Menu, MenuItem, 
    ComponentLibraryItem, PageVersion, User, SessionLocal
)

builder_bp = Blueprint('builder', __name__, url_prefix='/api/builder')

# ====== PERMISSION DECORATORS ======

def token_required(f):
    """Check if user is authenticated"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').split(' ')[-1]
        # Token validation would go here - for now simplified
        if not token or token == 'undefined':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_or_moderator_required(f):
    """Check if user is admin or moderator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        role = request.headers.get('X-User-Role', '')
        if role not in ['admin', 'moderator']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        return f(*args, **kwargs)
    return decorated

def get_user_id():
    """Get user ID from request headers"""
    return request.headers.get('X-User-ID', 1)  # Default to 1 for development


# ====== PAGE MANAGEMENT ======

@builder_bp.route('/pages', methods=['GET'])
@token_required
def list_pages():
    """Get all pages"""
    try:
        db = SessionLocal()
        pages = db.query(PageBuilder).all()
        return jsonify({
            'success': True,
            'data': [page.to_dict() for page in pages]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/pages/<int:page_id>', methods=['GET'])
@token_required
def get_page(page_id):
    """Get single page with all sections and blocks"""
    try:
        db = SessionLocal()
        page = db.query(PageBuilder).get(page_id)
        if not page:
            return jsonify({'error': 'Page not found'}), 404
        
        page_dict = page.to_dict()
        page_dict['sections'] = [
            {
                **section.to_dict(),
                'blocks': [block.to_dict() for block in section.blocks]
            } for section in page.sections
        ]
        
        return jsonify({
            'success': True,
            'data': page_dict
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/pages/slug/<slug>', methods=['GET'])
def get_published_page_by_slug(slug):
    """Get a published page by slug for public rendering"""
    try:
        db = SessionLocal()
        page = db.query(PageBuilder).filter_by(slug=slug, status='published').first()
        if not page:
            return jsonify({'error': 'Published page not found'}), 404

        page_dict = page.to_dict()
        page_dict['sections'] = [
            {
                **section.to_dict(),
                'blocks': [block.to_dict() for block in section.blocks]
            } for section in page.sections if section.is_visible
        ]

        return jsonify({
            'success': True,
            'data': page_dict
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/pages', methods=['POST'])
@token_required
@admin_or_moderator_required
def create_page():
    """Create new page"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        # Check if slug already exists
        existing = db.query(PageBuilder).filter_by(slug=data.get('slug')).first()
        if existing:
            return jsonify({'error': 'Slug already exists'}), 400
        
        new_page = PageBuilder(
            title=data.get('title'),
            slug=data.get('slug'),
            description=data.get('description', ''),
            theme_id=data.get('themeId'),
            menu_id=data.get('menuId'),
            created_by=int(get_user_id()),
            layout_data=json.dumps(data.get('layoutData', {}))
        )
        
        db.add(new_page)
        db.commit()
        db.refresh(new_page)
        
        return jsonify({
            'success': True,
            'message': 'Page created successfully',
            'data': new_page.to_dict()
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/pages/<int:page_id>', methods=['PUT'])
@token_required
@admin_or_moderator_required
def update_page(page_id):
    """Update page"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        page = db.query(PageBuilder).get(page_id)
        if not page:
            return jsonify({'error': 'Page not found'}), 404
        
        # Update fields
        if 'title' in data:
            page.title = data['title']
        if 'slug' in data:
            # Check if new slug already exists elsewhere
            existing = db.query(PageBuilder).filter(
                PageBuilder.slug == data['slug'],
                PageBuilder.id != page_id
            ).first()
            if existing:
                return jsonify({'error': 'Slug already exists'}), 400
            page.slug = data['slug']
        if 'description' in data:
            page.description = data['description']
        if 'status' in data:
            page.status = data['status']
            if data['status'] == 'published':
                page.published_at = datetime.utcnow()
        if 'themeId' in data:
            page.theme_id = data['themeId']
        if 'menuId' in data:
            page.menu_id = data['menuId']
        if 'layoutData' in data:
            page.layout_data = json.dumps(data['layoutData'])
        if 'metadata' in data:
            page.metadata = json.dumps(data['metadata'])
        
        page.updated_by = int(get_user_id())
        page.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(page)
        
        return jsonify({
            'success': True,
            'message': 'Page updated successfully',
            'data': page.to_dict()
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/pages/<int:page_id>', methods=['DELETE'])
@token_required
@admin_or_moderator_required
def delete_page(page_id):
    """Delete page"""
    try:
        db = SessionLocal()
        page = db.query(PageBuilder).get(page_id)
        if not page:
            return jsonify({'error': 'Page not found'}), 404
        
        db.delete(page)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Page deleted successfully'
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/pages/<int:page_id>/publish', methods=['POST'])
@token_required
@admin_or_moderator_required
def publish_page(page_id):
    """Publish a page"""
    try:
        db = SessionLocal()
        page = db.query(PageBuilder).get(page_id)
        if not page:
            return jsonify({'error': 'Page not found'}), 404
        
        # Create version before publishing
        latest_version = db.query(PageVersion).filter_by(page_id=page_id).order_by(PageVersion.version_number.desc()).first()
        version_number = (latest_version.version_number + 1) if latest_version else 1
        
        version = PageVersion(
            page_id=page_id,
            version_number=version_number,
            title=f"Published: {page.title}",
            layout_data=page.layout_data,
            created_by=int(get_user_id())
        )
        
        page.status = 'published'
        page.published_at = datetime.utcnow()
        page.updated_by = int(get_user_id())
        
        db.add(version)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Page published successfully'
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ====== SECTION MANAGEMENT ======

@builder_bp.route('/pages/<int:page_id>/sections', methods=['POST'])
@token_required
@admin_or_moderator_required
def create_section(page_id):
    """Create section in page"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        page = db.query(PageBuilder).get(page_id)
        if not page:
            return jsonify({'error': 'Page not found'}), 404
        
        section = PageSection(
            page_id=page_id,
            name=data.get('name', 'Section'),
            section_type=data.get('sectionType', 'content'),
            position=data.get('position', 0),
            column_count=data.get('columnCount', 1),
            background_color=data.get('backgroundColor'),
            background_image=data.get('backgroundImage'),
            padding=data.get('padding', '20px'),
            content=json.dumps(data.get('content', {}))
        )
        
        db.add(section)
        db.commit()
        db.refresh(section)
        
        return jsonify({
            'success': True,
            'data': section.to_dict()
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/sections/<int:section_id>', methods=['PUT'])
@token_required
@admin_or_moderator_required
def update_section(section_id):
    """Update section"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        section = db.query(PageSection).get(section_id)
        if not section:
            return jsonify({'error': 'Section not found'}), 404
        
        # Update fields
        if 'name' in data:
            section.name = data['name']
        if 'sectionType' in data:
            section.section_type = data['sectionType']
        if 'position' in data:
            section.position = data['position']
        if 'columnCount' in data:
            section.column_count = data['columnCount']
        if 'backgroundColor' in data:
            section.background_color = data['backgroundColor']
        if 'backgroundImage' in data:
            section.background_image = data['backgroundImage']
        if 'padding' in data:
            section.padding = data['padding']
        if 'content' in data:
            section.content = json.dumps(data['content'])
        if 'isVisible' in data:
            section.is_visible = data['isVisible']
        
        section.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(section)
        
        return jsonify({
            'success': True,
            'data': section.to_dict()
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/sections/<int:section_id>', methods=['DELETE'])
@token_required
@admin_or_moderator_required
def delete_section(section_id):
    """Delete section"""
    try:
        db = SessionLocal()
        section = db.query(PageSection).get(section_id)
        if not section:
            return jsonify({'error': 'Section not found'}), 404
        
        db.delete(section)
        db.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ====== BLOCK MANAGEMENT ======

@builder_bp.route('/sections/<int:section_id>/blocks', methods=['POST'])
@token_required
@admin_or_moderator_required
def create_block(section_id):
    """Create block in section"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        section = db.query(PageSection).get(section_id)
        if not section:
            return jsonify({'error': 'Section not found'}), 404
        
        block = PageBlock(
            section_id=section_id,
            component_id=data.get('componentId'),
            name=data.get('name', 'Block'),
            block_type=data.get('blockType', 'text'),
            position=data.get('position', 0),
            width=data.get('width', '100%'),
            content=json.dumps(data.get('content', {})),
            styles=json.dumps(data.get('styles', {}))
        )
        
        db.add(block)
        db.commit()
        db.refresh(block)
        
        return jsonify({
            'success': True,
            'data': block.to_dict()
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/blocks/<int:block_id>', methods=['PUT'])
@token_required
@admin_or_moderator_required
def update_block(block_id):
    """Update block"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        block = db.query(PageBlock).get(block_id)
        if not block:
            return jsonify({'error': 'Block not found'}), 404
        
        if 'name' in data:
            block.name = data['name']
        if 'blockType' in data:
            block.block_type = data['blockType']
        if 'position' in data:
            block.position = data['position']
        if 'width' in data:
            block.width = data['width']
        if 'content' in data:
            block.content = json.dumps(data['content'])
        if 'styles' in data:
            block.styles = json.dumps(data['styles'])
        if 'isVisible' in data:
            block.is_visible = data['isVisible']
        
        block.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(block)
        
        return jsonify({
            'success': True,
            'data': block.to_dict()
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/blocks/<int:block_id>', methods=['DELETE'])
@token_required
@admin_or_moderator_required
def delete_block(block_id):
    """Delete block"""
    try:
        db = SessionLocal()
        block = db.query(PageBlock).get(block_id)
        if not block:
            return jsonify({'error': 'Block not found'}), 404
        
        db.delete(block)
        db.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ====== THEME MANAGEMENT ======

@builder_bp.route('/themes', methods=['GET'])
@token_required
def list_themes():
    """Get all themes"""
    try:
        db = SessionLocal()
        themes = db.query(Theme).all()
        return jsonify({
            'success': True,
            'data': [theme.to_dict() for theme in themes]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/themes', methods=['POST'])
@token_required
@admin_or_moderator_required
def create_theme():
    """Create new theme"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        theme = Theme(
            name=data.get('name'),
            description=data.get('description', ''),
            colors=json.dumps(data.get('colors', {})),
            fonts=json.dumps(data.get('fonts', {})),
            spacing=json.dumps(data.get('spacing', {})),
            border_radius=data.get('borderRadius', '6px'),
            shadow=data.get('shadow', '0 2px 8px rgba(0,0,0,0.05)'),
            custom_css=data.get('customCss', ''),
            created_by=int(get_user_id())
        )
        
        db.add(theme)
        db.commit()
        db.refresh(theme)
        
        return jsonify({
            'success': True,
            'data': theme.to_dict()
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/themes/<int:theme_id>', methods=['PUT'])
@token_required
@admin_or_moderator_required
def update_theme(theme_id):
    """Update theme"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        theme = db.query(Theme).get(theme_id)
        if not theme:
            return jsonify({'error': 'Theme not found'}), 404
        
        if 'name' in data:
            theme.name = data['name']
        if 'description' in data:
            theme.description = data['description']
        if 'colors' in data:
            theme.colors = json.dumps(data['colors'])
        if 'fonts' in data:
            theme.fonts = json.dumps(data['fonts'])
        if 'spacing' in data:
            theme.spacing = json.dumps(data['spacing'])
        if 'borderRadius' in data:
            theme.border_radius = data['borderRadius']
        if 'shadow' in data:
            theme.shadow = data['shadow']
        if 'customCss' in data:
            theme.custom_css = data['customCss']
        if 'isActive' in data:
            # Deactivate other themes if activating this one
            if data['isActive']:
                db.query(Theme).update({'is_active': False})
            theme.is_active = data['isActive']
        
        theme.updated_by = int(get_user_id())
        theme.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(theme)
        
        return jsonify({
            'success': True,
            'data': theme.to_dict()
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/themes/<int:theme_id>', methods=['DELETE'])
@token_required
@admin_or_moderator_required
def delete_theme(theme_id):
    """Delete theme"""
    try:
        db = SessionLocal()
        theme = db.query(Theme).get(theme_id)
        if not theme:
            return jsonify({'error': 'Theme not found'}), 404
        
        db.delete(theme)
        db.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ====== MENU MANAGEMENT ======

@builder_bp.route('/menus', methods=['GET'])
@token_required
def list_menus():
    """Get all menus"""
    try:
        db = SessionLocal()
        menus = db.query(Menu).all()
        menu_dicts = []
        for menu in menus:
            menu_dict = menu.to_dict()
            menu_dict['items'] = [item.to_dict() for item in menu.items]
            menu_dicts.append(menu_dict)
        
        return jsonify({
            'success': True,
            'data': menu_dicts
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/menus', methods=['POST'])
@token_required
@admin_or_moderator_required
def create_menu():
    """Create new menu"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        menu = Menu(
            name=data.get('name'),
            location=data.get('location', 'header'),
            description=data.get('description', ''),
            display_type=data.get('displayType', 'horizontal'),
            created_by=int(get_user_id())
        )
        
        db.add(menu)
        db.commit()
        db.refresh(menu)
        
        return jsonify({
            'success': True,
            'data': menu.to_dict()
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/menus/<int:menu_id>', methods=['PUT'])
@token_required
@admin_or_moderator_required
def update_menu(menu_id):
    """Update menu"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        menu = db.query(Menu).get(menu_id)
        if not menu:
            return jsonify({'error': 'Menu not found'}), 404
        
        if 'name' in data:
            menu.name = data['name']
        if 'location' in data:
            menu.location = data['location']
        if 'description' in data:
            menu.description = data['description']
        if 'displayType' in data:
            menu.display_type = data['displayType']
        if 'isVisible' in data:
            menu.is_visible = data['isVisible']
        
        menu.updated_by = int(get_user_id())
        menu.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(menu)
        
        return jsonify({
            'success': True,
            'data': menu.to_dict()
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/menus/<int:menu_id>', methods=['DELETE'])
@token_required
@admin_or_moderator_required
def delete_menu(menu_id):
    """Delete menu"""
    try:
        db = SessionLocal()
        menu = db.query(Menu).get(menu_id)
        if not menu:
            return jsonify({'error': 'Menu not found'}), 404
        
        db.delete(menu)
        db.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ====== MENU ITEM MANAGEMENT ======

@builder_bp.route('/menus/<int:menu_id>/items', methods=['POST'])
@token_required
@admin_or_moderator_required
def create_menu_item(menu_id):
    """Create menu item"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        menu = db.query(Menu).get(menu_id)
        if not menu:
            return jsonify({'error': 'Menu not found'}), 404
        
        item = MenuItem(
            menu_id=menu_id,
            label=data.get('label'),
            url=data.get('url'),
            icon=data.get('icon'),
            position=data.get('position', 0),
            parent_id=data.get('parentId'),
            open_in_new_tab=data.get('openInNewTab', False)
        )
        
        db.add(item)
        db.commit()
        db.refresh(item)
        
        return jsonify({
            'success': True,
            'data': item.to_dict()
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/menu-items/<int:item_id>', methods=['PUT'])
@token_required
@admin_or_moderator_required
def update_menu_item(item_id):
    """Update menu item"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        item = db.query(MenuItem).get(item_id)
        if not item:
            return jsonify({'error': 'Menu item not found'}), 404
        
        if 'label' in data:
            item.label = data['label']
        if 'url' in data:
            item.url = data['url']
        if 'icon' in data:
            item.icon = data['icon']
        if 'position' in data:
            item.position = data['position']
        if 'parentId' in data:
            item.parent_id = data['parentId']
        if 'isVisible' in data:
            item.is_visible = data['isVisible']
        if 'openInNewTab' in data:
            item.open_in_new_tab = data['openInNewTab']
        
        item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(item)
        
        return jsonify({
            'success': True,
            'data': item.to_dict()
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/menu-items/<int:item_id>', methods=['DELETE'])
@token_required
@admin_or_moderator_required
def delete_menu_item(item_id):
    """Delete menu item"""
    try:
        db = SessionLocal()
        item = db.query(MenuItem).get(item_id)
        if not item:
            return jsonify({'error': 'Menu item not found'}), 404
        
        db.delete(item)
        db.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ====== COMPONENT LIBRARY ======

@builder_bp.route('/components', methods=['GET'])
@token_required
def list_components():
    """Get all components"""
    try:
        db = SessionLocal()
        components = db.query(ComponentLibraryItem).all()
        return jsonify({
            'success': True,
            'data': [comp.to_dict() for comp in components]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/components/category/<category>', methods=['GET'])
@token_required
def get_components_by_category(category):
    """Get components by category"""
    try:
        db = SessionLocal()
        components = db.query(ComponentLibraryItem).filter_by(category=category).all()
        return jsonify({
            'success': True,
            'data': [comp.to_dict() for comp in components]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/components', methods=['POST'])
@token_required
@admin_or_moderator_required
def create_component():
    """Create new component"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        component = ComponentLibraryItem(
            name=data.get('name'),
            category=data.get('category'),
            description=data.get('description', ''),
            thumbnail=data.get('thumbnail'),
            template=json.dumps(data.get('template', {})),
            default_content=json.dumps(data.get('defaultContent', {})),
            styles=json.dumps(data.get('styles', {})),
            is_featured=data.get('isFeatured', False),
            created_by=int(get_user_id())
        )
        
        db.add(component)
        db.commit()
        db.refresh(component)
        
        return jsonify({
            'success': True,
            'data': component.to_dict()
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/components/<int:component_id>', methods=['PUT'])
@token_required
@admin_or_moderator_required
def update_component(component_id):
    """Update component"""
    try:
        data = request.get_json()
        db = SessionLocal()
        
        component = db.query(ComponentLibraryItem).get(component_id)
        if not component:
            return jsonify({'error': 'Component not found'}), 404
        
        if 'name' in data:
            component.name = data['name']
        if 'category' in data:
            component.category = data['category']
        if 'description' in data:
            component.description = data['description']
        if 'thumbnail' in data:
            component.thumbnail = data['thumbnail']
        if 'template' in data:
            component.template = json.dumps(data['template'])
        if 'defaultContent' in data:
            component.default_content = json.dumps(data['defaultContent'])
        if 'styles' in data:
            component.styles = json.dumps(data['styles'])
        if 'isFeatured' in data:
            component.is_featured = data['isFeatured']
        
        component.updated_by = int(get_user_id())
        component.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(component)
        
        return jsonify({
            'success': True,
            'data': component.to_dict()
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/components/<int:component_id>', methods=['DELETE'])
@token_required
@admin_or_moderator_required
def delete_component(component_id):
    """Delete component"""
    try:
        db = SessionLocal()
        component = db.query(ComponentLibraryItem).get(component_id)
        if not component:
            return jsonify({'error': 'Component not found'}), 404
        
        if component.is_system:
            return jsonify({'error': 'Cannot delete system components'}), 403
        
        db.delete(component)
        db.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ====== PAGE VERSIONS ======

@builder_bp.route('/pages/<int:page_id>/versions', methods=['GET'])
@token_required
def get_page_versions(page_id):
    """Get all versions of a page"""
    try:
        db = SessionLocal()
        versions = db.query(PageVersion).filter_by(page_id=page_id).order_by(
            PageVersion.version_number.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'data': [v.to_dict() for v in versions]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@builder_bp.route('/pages/<int:page_id>/versions/<int:version_id>/restore', methods=['POST'])
@token_required
@admin_or_moderator_required
def restore_version(page_id, version_id):
    """Restore page to previous version"""
    try:
        db = SessionLocal()
        
        page = db.query(PageBuilder).get(page_id)
        if not page:
            return jsonify({'error': 'Page not found'}), 404
        
        version = db.query(PageVersion).get(version_id)
        if not version or version.page_id != page_id:
            return jsonify({'error': 'Version not found'}), 404
        
        # Restore layout data
        page.layout_data = version.layout_data
        page.updated_by = int(get_user_id())
        page.updated_at = datetime.utcnow()
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'Restored to version {version.version_number}'
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
