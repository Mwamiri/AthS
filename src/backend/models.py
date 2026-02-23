"""
AthSys Database Models
SQLAlchemy ORM models for all entities
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import bcrypt
import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

Base = declarative_base()

# Database connection
def _build_database_url():
    explicit_url = os.getenv('DATABASE_URL')
    if explicit_url:
        return explicit_url

    has_discrete_db_config = any(
        os.getenv(key) for key in ('DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME')
    )

    if not has_discrete_db_config:
        sqlite_path = os.path.join(PROJECT_ROOT, 'data', 'athsys_local.db')
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        return f"sqlite:///{sqlite_path}"

    db_user = os.getenv('DB_USER', 'athsys_user')
    db_password = os.getenv('DB_PASSWORD', 'athsys_pass')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'athsys_db')

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


DATABASE_URL = _build_database_url()
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class User(Base):
    """User model for authentication and role management"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True)  # admin, chief_registrar, registrar, starter, coach, athlete, viewer
    status = Column(String(20), default='active')  # active, inactive, suspended
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Two-factor authentication
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32), nullable=True)
    
    # Relationships
    athletes = relationship('Athlete', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'status': self.status,
            'lastLogin': self.last_login.isoformat() if self.last_login else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'twoFactorEnabled': self.two_factor_enabled
        }


class Athlete(Base):
    """Athlete model"""
    __tablename__ = 'athletes'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    name = Column(String(100), nullable=False, index=True)
    country = Column(String(3), nullable=False)  # 3-letter country code
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    contact_email = Column(String(150), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    club_team = Column(String(100), nullable=True)
    coach_name = Column(String(100), nullable=True)
    bib_number = Column(String(20), nullable=True, unique=True, index=True)
    photo_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='athletes')
    registrations = relationship('Registration', back_populates='athlete', cascade='all, delete-orphan')
    results = relationship('Result', back_populates='athlete', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'dateOfBirth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'email': self.contact_email,
            'phone': self.contact_phone,
            'clubTeam': self.club_team,
            'coach': self.coach_name,
            'bibNumber': self.bib_number,
            'photoUrl': self.photo_url
        }


class Race(Base):
    """Race model - main competition event"""
    __tablename__ = 'races'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    location = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default='upcoming')  # upcoming, ongoing, completed, cancelled
    registration_open = Column(Boolean, default=True)
    registration_deadline = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = relationship('Event', back_populates='race', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.isoformat() if self.date else None,
            'location': self.location,
            'description': self.description,
            'status': self.status,
            'registrationOpen': self.registration_open,
            'registrationDeadline': self.registration_deadline.isoformat() if self.registration_deadline else None
        }


class Event(Base):
    """Event model - specific competition within a race (e.g., 100m Sprint)"""
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # Track, Field, Road
    gender = Column(String(10), nullable=True)  # Male, Female, Mixed
    age_group = Column(String(20), nullable=True)  # U18, U20, Senior, etc.
    distance = Column(Float, nullable=True)  # Distance in meters
    start_time = Column(DateTime, nullable=True)
    max_participants = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    race = relationship('Race', back_populates='events')
    registrations = relationship('Registration', back_populates='event', cascade='all, delete-orphan')
    results = relationship('Result', back_populates='event', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'raceId': self.race_id,
            'name': self.name,
            'category': self.category,
            'gender': self.gender,
            'ageGroup': self.age_group,
            'distance': self.distance,
            'startTime': self.start_time.isoformat() if self.start_time else None,
            'maxParticipants': self.max_participants
        }


class Registration(Base):
    """Registration model - athlete registration for an event"""
    __tablename__ = 'registrations'
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    registration_type = Column(String(20), default='manual')  # manual, bulk, public
    status = Column(String(20), default='registered')  # registered, confirmed, cancelled, dns
    payment_status = Column(String(20), default='pending')  # pending, paid, refunded
    bib_number = Column(String(20), nullable=True)
    heat_number = Column(Integer, nullable=True)
    lane_number = Column(Integer, nullable=True)
    confirmed_present = Column(Boolean, default=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    athlete = relationship('Athlete', back_populates='registrations')
    event = relationship('Event', back_populates='registrations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'athleteId': self.athlete_id,
            'eventId': self.event_id,
            'registrationType': self.registration_type,
            'status': self.status,
            'paymentStatus': self.payment_status,
            'bibNumber': self.bib_number,
            'heatNumber': self.heat_number,
            'laneNumber': self.lane_number,
            'confirmedPresent': self.confirmed_present,
            'registeredAt': self.registered_at.isoformat() if self.registered_at else None
        }


class Result(Base):
    """Result model - competition results"""
    __tablename__ = 'results'
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    position = Column(Integer, nullable=True)
    time_seconds = Column(Float, nullable=True)  # Time in seconds
    distance_meters = Column(Float, nullable=True)  # For field events
    points = Column(Integer, nullable=True)
    status = Column(String(20), default='finished')  # finished, dns, dnf, dq
    heat_number = Column(Integer, nullable=True)
    lane_number = Column(Integer, nullable=True)
    wind_speed = Column(Float, nullable=True)  # m/s
    is_record = Column(Boolean, default=False)
    record_type = Column(String(20), nullable=True)  # world, continental, national, meet
    recorded_at = Column(DateTime, default=datetime.utcnow)
    recorded_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    athlete = relationship('Athlete', back_populates='results')
    event = relationship('Event', back_populates='results')
    
    def to_dict(self):
        return {
            'id': self.id,
            'athleteId': self.athlete_id,
            'eventId': self.event_id,
            'position': self.position,
            'timeSeconds': self.time_seconds,
            'distanceMeters': self.distance_meters,
            'points': self.points,
            'status': self.status,
            'heatNumber': self.heat_number,
            'laneNumber': self.lane_number,
            'windSpeed': self.wind_speed,
            'isRecord': self.is_record,
            'recordType': self.record_type,
            'recordedAt': self.recorded_at.isoformat() if self.recorded_at else None
        }


class AuditLog(Base):
    """Audit log for tracking all system changes"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String(50), nullable=False, index=True)  # create, update, delete, login, etc.
    entity_type = Column(String(50), nullable=False)  # user, athlete, race, event, etc.
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)  # JSON string with details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'action': self.action,
            'entityType': self.entity_type,
            'entityId': self.entity_id,
            'details': self.details,
            'ipAddress': self.ip_address,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class PluginConfig(Base):
    """Plugin configuration and status tracking"""
    __tablename__ = 'plugin_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    plugin_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., 'official_timing'
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=False, index=True)
    required = Column(Boolean, default=False)  # Cannot be disabled if required
    category = Column(String(50), nullable=True)  # core, enterprise, features, infrastructure, security
    version = Column(String(20), nullable=True)  # e.g., '2.1.6'
    module_name = Column(String(100), nullable=True)  # Python module name
    settings = Column(Text, nullable=True)  # JSON string for plugin-specific settings
    enabled_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # Admin who enabled it
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    enabler = relationship('User', foreign_keys=[enabled_by])
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'pluginId': self.plugin_id,
            'name': self.name,
            'description': self.description,
            'enabled': self.enabled,
            'required': self.required,
            'category': self.category,
            'version': self.version,
            'moduleName': self.module_name,
            'settings': json.loads(self.settings) if self.settings else {},
            'enabledBy': self.enabled_by,
            'lastModified': self.last_modified.isoformat() if self.last_modified else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class FrontendConfig(Base):
    """Frontend navigation and display configuration - control from backend"""
    __tablename__ = 'frontend_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)  # e.g., 'nav_links', 'features', 'show_logs'
    value = Column(Text, nullable=False)  # JSON string with configuration
    description = Column(String(255), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    updater = relationship('User', foreign_keys=[updated_by])
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'key': self.key,
            'value': json.loads(self.value) if self.value else {},
            'description': self.description,
            'updatedBy': self.updated_by,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


# ====== PAGE BUILDER MODELS ======

class PageBuilder(Base):
    """Page model - manages pages that can be edited with the builder"""
    __tablename__ = 'pages'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)  # URL-friendly identifier
    description = Column(Text, nullable=True)
    status = Column(String(20), default='draft')  # draft, published, archived
    theme_id = Column(Integer, ForeignKey('themes.id'), nullable=True)
    menu_id = Column(Integer, ForeignKey('menus.id'), nullable=True)
    layout_data = Column(Text, nullable=True)  # JSON - stores grid/sections structure
    page_metadata = Column(Text, nullable=True)  # JSON - SEO, og tags, custom meta (renamed from metadata to avoid SQLAlchemy conflict)
    published_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sections = relationship('PageSection', back_populates='page', cascade='all, delete-orphan')
    versions = relationship('PageVersion', back_populates='page', cascade='all, delete-orphan')
    creator = relationship('User', foreign_keys=[created_by])
    updater = relationship('User', foreign_keys=[updated_by])
    menu = relationship('Menu', foreign_keys=[menu_id])
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'status': self.status,
            'themeId': self.theme_id,
            'menuId': self.menu_id,
            'layoutData': json.loads(self.layout_data) if self.layout_data else {},
            'metadata': json.loads(self.page_metadata) if self.page_metadata else {},
            'publishedAt': self.published_at.isoformat() if self.published_at else None,
            'createdBy': self.created_by,
            'updatedBy': self.updated_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class PageSection(Base):
    """Section/Block in a page"""
    __tablename__ = 'page_sections'
    
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey('pages.id'), nullable=False)
    name = Column(String(100), nullable=False)
    section_type = Column(String(50), nullable=False)  # hero, content, grid, gallery, form, etc.
    position = Column(Integer, default=0)  # Order in page
    column_count = Column(Integer, default=1)  # For grid sections
    background_color = Column(String(7), nullable=True)  # Hex color
    background_image = Column(String(255), nullable=True)  # Image URL
    padding = Column(String(50), default='20px')  # CSS padding
    content = Column(Text, nullable=True)  # JSON content for section
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    page = relationship('PageBuilder', back_populates='sections')
    blocks = relationship('PageBlock', back_populates='section', cascade='all, delete-orphan')
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'pageId': self.page_id,
            'name': self.name,
            'sectionType': self.section_type,
            'position': self.position,
            'columnCount': self.column_count,
            'backgroundColor': self.background_color,
            'backgroundImage': self.background_image,
            'padding': self.padding,
            'content': json.loads(self.content) if self.content else {},
            'isVisible': self.is_visible,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class PageBlock(Base):
    """Individual block/component in a section"""
    __tablename__ = 'page_blocks'
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey('page_sections.id'), nullable=False)
    component_id = Column(Integer, ForeignKey('component_library.id'), nullable=True)  # Reference to library
    name = Column(String(100), nullable=False)
    block_type = Column(String(50), nullable=False)  # button, text, image, card, form, etc.
    position = Column(Integer, default=0)
    width = Column(String(50), default='100%')  # CSS width
    content = Column(Text, nullable=True)  # JSON - block-specific content
    styles = Column(Text, nullable=True)  # JSON - inline CSS/Tailwind classes
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    section = relationship('PageSection', back_populates='blocks')
    library_item = relationship('ComponentLibraryItem')
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'sectionId': self.section_id,
            'componentId': self.component_id,
            'name': self.name,
            'blockType': self.block_type,
            'position': self.position,
            'width': self.width,
            'content': json.loads(self.content) if self.content else {},
            'styles': json.loads(self.styles) if self.styles else {},
            'isVisible': self.is_visible,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class Theme(Base):
    """Theme model - manages site themes/color schemes"""
    __tablename__ = 'themes'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False, index=True)
    colors = Column(Text, nullable=False)  # JSON - primary, secondary, text, bg, etc.
    fonts = Column(Text, nullable=False)  # JSON - font families and sizes
    spacing = Column(Text, nullable=False)  # JSON - padding, margin values
    border_radius = Column(String(50), default='6px')
    shadow = Column(String(100), default='0 2px 8px rgba(0,0,0,0.05)')
    custom_css = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship('User', foreign_keys=[created_by])
    updater = relationship('User', foreign_keys=[updated_by])
    pages = relationship('PageBuilder', backref='theme')
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'isActive': self.is_active,
            'colors': json.loads(self.colors) if self.colors else {},
            'fonts': json.loads(self.fonts) if self.fonts else {},
            'spacing': json.loads(self.spacing) if self.spacing else {},
            'borderRadius': self.border_radius,
            'shadow': self.shadow,
            'customCss': self.custom_css,
            'createdBy': self.created_by,
            'updatedBy': self.updated_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class Menu(Base):
    """Menu model - manages navigation menus"""
    __tablename__ = 'menus'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    location = Column(String(50), nullable=False)  # header, footer, sidebar, etc.
    description = Column(Text, nullable=True)
    display_type = Column(String(50), default='horizontal')  # horizontal, vertical, dropdown
    is_visible = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship('User', foreign_keys=[created_by])
    updater = relationship('User', foreign_keys=[updated_by])
    items = relationship('MenuItem', back_populates='menu', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
            'displayType': self.display_type,
            'isVisible': self.is_visible,
            'createdBy': self.created_by,
            'updatedBy': self.updated_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class MenuItem(Base):
    """Menu item model"""
    __tablename__ = 'menu_items'
    
    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey('menus.id'), nullable=False)
    label = Column(String(100), nullable=False)
    url = Column(String(255), nullable=True)  # Can be external URL or internal page slug
    icon = Column(String(50), nullable=True)  # Icon name
    position = Column(Integer, default=0)
    parent_id = Column(Integer, ForeignKey('menu_items.id'), nullable=True)  # For nested items
    is_visible = Column(Boolean, default=True)
    open_in_new_tab = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    menu = relationship('Menu', back_populates='items')
    parent = relationship('MenuItem', remote_side=[id], back_populates='children')
    children = relationship('MenuItem', back_populates='parent', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'menuId': self.menu_id,
            'label': self.label,
            'url': self.url,
            'icon': self.icon,
            'position': self.position,
            'parentId': self.parent_id,
            'isVisible': self.is_visible,
            'openInNewTab': self.open_in_new_tab,
            'children': [child.to_dict() for child in self.children],
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class ComponentLibraryItem(Base):
    """Reusable components/blocks library"""
    __tablename__ = 'component_library'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # hero, card, form, button, gallery, etc.
    description = Column(Text, nullable=True)
    thumbnail = Column(String(255), nullable=True)  # Preview image URL
    template = Column(Text, nullable=False)  # JSON - component template/structure
    default_content = Column(Text, nullable=True)  # JSON - default content
    styles = Column(Text, nullable=True)  # JSON - default styles
    is_system = Column(Boolean, default=False)  # System components cannot be deleted
    is_featured = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship('User', foreign_keys=[created_by])
    updater = relationship('User', foreign_keys=[updated_by])
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'thumbnail': self.thumbnail,
            'template': json.loads(self.template) if self.template else {},
            'defaultContent': json.loads(self.default_content) if self.default_content else {},
            'styles': json.loads(self.styles) if self.styles else {},
            'isSystem': self.is_system,
            'isFeatured': self.is_featured,
            'createdBy': self.created_by,
            'updatedBy': self.updated_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class PageVersion(Base):
    """Version history for pages - undo/redo and revision tracking"""
    __tablename__ = 'page_versions'
    
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey('pages.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    layout_data = Column(Text, nullable=False)  # JSON - full page state
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    page = relationship('PageBuilder', back_populates='versions')
    creator = relationship('User', foreign_keys=[created_by])
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'pageId': self.page_id,
            'versionNumber': self.version_number,
            'title': self.title,
            'description': self.description,
            'layoutData': json.loads(self.layout_data) if self.layout_data else {},
            'createdBy': self.created_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


# ==================== RECORDS & STANDARDS MODELS ====================

class PersonalBest(Base):
    """Track athlete's personal best for each event"""
    __tablename__ = 'personal_bests'
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False, index=True)
    event_name = Column(String(50), nullable=False)  # '100m', '1500m', '5K', etc.
    
    time = Column(Float, nullable=False)  # in seconds
    date_achieved = Column(Date, nullable=False)
    location = Column(String(100))  # Where the PB was set
    race_id = Column(Integer, ForeignKey('races.id'), nullable=True)
    
    # Ranking info
    national_ranking = Column(Integer, nullable=True)  # Position in country ranking
    world_ranking = Column(Integer, nullable=True)  # Position in world ranking
    
    # Standards qualifications
    qualifies_for_national = Column(Boolean, default=False)
    qualifies_for_continental = Column(Boolean, default=False)
    qualifies_for_world = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    athlete = relationship('Athlete', back_populates='personal_bests')
    event = relationship('Event')
    race = relationship('Race')
    
    def to_dict(self):
        return {
            'id': self.id,
            'athlete_id': self.athlete_id,
            'event_id': self.event_id,
            'event_name': self.event_name,
            'time': self.time,
            'date_achieved': self.date_achieved.isoformat(),
            'location': self.location,
            'national_ranking': self.national_ranking,
            'world_ranking': self.world_ranking,
            'qualifies_for_national': self.qualifies_for_national,
            'qualifies_for_continental': self.qualifies_for_continental,
            'qualifies_for_world': self.qualifies_for_world,
        }


class SeasonBest(Base):
    """Track athlete's best time in current/past season"""
    __tablename__ = 'season_bests'
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False, index=True)
    event_name = Column(String(50), nullable=False)
    season = Column(Integer, nullable=False)  # 2024, 2025, etc.
    
    time = Column(Float, nullable=False)
    date_achieved = Column(Date, nullable=False)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=True)
    location = Column(String(100))
    
    # Ranking in season
    season_ranking = Column(Integer, nullable=True)  # Best in country this season
    improvement_from_pb = Column(Float, nullable=True)  # How much improved from PB
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    athlete = relationship('Athlete', back_populates='season_bests')
    event = relationship('Event')
    race = relationship('Race')
    
    def to_dict(self):
        return {
            'id': self.id,
            'athlete_id': self.athlete_id,
            'event_name': self.event_name,
            'season': self.season,
            'time': self.time,
            'date_achieved': self.date_achieved.isoformat(),
            'location': self.location,
            'season_ranking': self.season_ranking,
            'improvement_from_pb': self.improvement_from_pb,
        }


class CountryRecord(Base):
    """National records for specific country"""
    __tablename__ = 'country_records'
    
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(3), nullable=False, index=True)  # ISO code: KEN, USA, GBR, etc.
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    event_name = Column(String(50), nullable=False)
    category = Column(String(50))  # 'Male', 'Female', 'U20', 'Masters', etc.
    
    time = Column(Float, nullable=False)
    athlete_name = Column(String(100), nullable=False)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=True)
    date_set = Column(Date, nullable=False)
    location = Column(String(100))
    race_id = Column(Integer, ForeignKey('races.id'), nullable=True)
    
    # Record info
    previous_record = Column(Float, nullable=True)  # Previous record time
    improvement = Column(Float, nullable=True)  # Time improvement (seconds)
    wind_speed = Column(Float, nullable=True)  # For sprints: wind assistance
    ratified = Column(Boolean, default=False)  # Official ratification status
    
    created_at = Column(DateTime, default=datetime.utcnow)
    athlete = relationship('Athlete')
    event = relationship('Event')
    race = relationship('Race')
    
    def to_dict(self):
        return {
            'id': self.id,
            'country': self.country,
            'event_name': self.event_name,
            'category': self.category,
            'time': self.time,
            'athlete_name': self.athlete_name,
            'date_set': self.date_set.isoformat(),
            'location': self.location,
            'improvement': self.improvement,
            'ratified': self.ratified,
        }


class RegionalRecord(Base):
    """Regional/continental records (Africa, Europe, etc.)"""
    __tablename__ = 'regional_records'
    
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String(50), nullable=False, index=True)  # 'Africa', 'Europe', 'Asia', 'Americas'
    country = Column(String(3), nullable=False)
    event_name = Column(String(50), nullable=False)
    category = Column(String(50))
    
    time = Column(Float, nullable=False)
    athlete_name = Column(String(100), nullable=False)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=True)
    date_set = Column(Date, nullable=False)
    location = Column(String(100))
    
    previous_record = Column(Float, nullable=True)
    improvement = Column(Float, nullable=True)
    ratified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    athlete = relationship('Athlete')
    
    def to_dict(self):
        return {
            'region': self.region,
            'country': self.country,
            'event_name': self.event_name,
            'time': self.time,
            'athlete_name': self.athlete_name,
            'date_set': self.date_set.isoformat(),
            'improvement': self.improvement,
        }


class StadiumRecord(Base):
    """Best ever run at a specific venue/stadium"""
    __tablename__ = 'stadium_records'
    
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(50), nullable=False)
    stadium_name = Column(String(100), nullable=False, index=True)
    location = Column(String(100), nullable=False)  # City/Country
    
    time = Column(Float, nullable=False)
    athlete_name = Column(String(100), nullable=False)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=True)
    date_set = Column(Date, nullable=False)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=True)
    
    # Track condition
    track_type = Column(String(50))  # 'synthetic', 'clay', 'grass'
    previous_record = Column(Float, nullable=True)
    improvement = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    athlete = relationship('Athlete')
    race = relationship('Race')
    
    def to_dict(self):
        return {
            'event_name': self.event_name,
            'stadium_name': self.stadium_name,
            'time': self.time,
            'athlete_name': self.athlete_name,
            'date_set': self.date_set.isoformat(),
            'improvement': self.improvement,
        }


class WorldRecord(Base):
    """World records by event (reference/external data)"""
    __tablename__ = 'world_records'
    
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(50), nullable=False, unique=True)
    category = Column(String(50))  # 'Male', 'Female', 'U20', etc.
    
    time = Column(Float, nullable=False)
    athlete_name = Column(String(100), nullable=False)
    country = Column(String(3), nullable=False)
    date_set = Column(Date, nullable=False)
    location = Column(String(100))
    
    # Source
    source = Column(String(50), default='World Athletics')  # Where data came from
    url = Column(String(255), nullable=True)  # Link to official record
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'event_name': self.event_name,
            'time': self.time,
            'athlete_name': self.athlete_name,
            'country': self.country,
            'date_set': self.date_set.isoformat(),
        }


class QualifyingStandard(Base):
    """Standards required to qualify for championships"""
    __tablename__ = 'qualifying_standards'
    
    id = Column(Integer, primary_key=True, index=True)
    championship = Column(String(100), nullable=False)  # 'Olympic Games', 'World Champs', 'African Champs'
    year = Column(Integer, nullable=False)
    
    event_name = Column(String(50), nullable=False)
    category = Column(String(50))  # 'Male', 'Female', 'U20'
    
    standard_time = Column(Float, nullable=False)  # Time needed to qualify
    type = Column(String(20), default='A')  # 'A' (auto qualify), 'B' (needs consideration)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'championship': self.championship,
            'year': self.year,
            'event_name': self.event_name,
            'category': self.category,
            'standard_time': self.standard_time,
            'type': self.type,
        }


class AthleteStandard(Base):
    """Track athlete's achievement of qualifying standards"""
    __tablename__ = 'athlete_standards'
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=False, index=True)
    standard_id = Column(Integer, ForeignKey('qualifying_standards.id'), nullable=False)
    
    championship = Column(String(100), nullable=False)
    final_time = Column(Float, nullable=False)
    status = Column(String(20))  # 'achieved', 'close', 'needs_improvement'
    
    # How good is the achievement?
    time_below_standard = Column(Float, nullable=True)  # seconds below standard
    percentage_below = Column(Float, nullable=True)  # % below standard
    rank_for_team = Column(Integer, nullable=True)  # Position for team selection
    
    achieved_date = Column(Date, nullable=False)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    athlete = relationship('Athlete')
    standard = relationship('QualifyingStandard')
    
    def to_dict(self):
        return {
            'athlete_id': self.athlete_id,
            'championship': self.championship,
            'final_time': self.final_time,
            'status': self.status,
            'time_below_standard': self.time_below_standard,
            'achieved_date': self.achieved_date.isoformat(),
        }


class CourseRecord(Base):
    """Best time for a specific race course"""
    __tablename__ = 'course_records'
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False, unique=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    event_name = Column(String(50), nullable=False)
    
    time = Column(Float, nullable=False)
    athlete_name = Column(String(100), nullable=False)
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=True)
    year = Column(Integer, nullable=False)
    
    # Course conditions
    weather = Column(String(100))  # 'Sunny', 'Rainy', etc.
    temperature = Column(Float, nullable=True)  # Celsius
    elevation = Column(Float, nullable=True)  # meters
    course_difficulty = Column(String(50))  # 'flat', 'hilly', 'very_hilly'
    
    previous_record = Column(Float, nullable=True)
    improvement = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    race = relationship('Race')
    athlete = relationship('Athlete')
    
    def to_dict(self):
        return {
            'event_name': self.event_name,
            'time': self.time,
            'athlete_name': self.athlete_name,
            'year': self.year,
            'improvement': self.improvement,
            'course_difficulty': self.course_difficulty,
        }


class RankingByTime(Base):
    """Current rankings for each event (by country/region)"""
    __tablename__ = 'rankings_by_time'
    
    id = Column(Integer, primary_key=True, index=True)
    ranking_type = Column(String(50))  # 'national', 'regional', 'all_time'
    country = Column(String(3), nullable=True)  # NULL for world rankings
    region = Column(String(50), nullable=True)  # 'Africa', 'Europe', etc.
    
    year = Column(Integer, nullable=True)  # NULL for all-time
    event_name = Column(String(50), nullable=False)
    category = Column(String(50))
    
    position = Column(Integer, nullable=False)  # 1st, 2nd, 3rd, etc.
    athlete_id = Column(Integer, ForeignKey('athletes.id'), nullable=False)
    athlete_name = Column(String(100), nullable=False)
    time = Column(Float, nullable=False)
    date_achieved = Column(Date, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    athlete = relationship('Athlete')
    
    def to_dict(self):
        return {
            'position': self.position,
            'athlete_name': self.athlete_name,
            'time': self.time,
            'year': self.year,
        }


# Extend Athlete model with relationships
def update_athlete_relationships():
    """Add relationships to Athlete model"""
    if not hasattr(Athlete, 'personal_bests'):
        Athlete.personal_bests = relationship('PersonalBest', back_populates='athlete', cascade='all, delete-orphan')
        Athlete.season_bests = relationship('SeasonBest', back_populates='athlete', cascade='all, delete-orphan')


update_athlete_relationships()


# Get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
