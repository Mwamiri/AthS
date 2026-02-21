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

Base = declarative_base()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://athsys_user:athsys_pass@localhost:5432/athsys_db')
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


# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


# Get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
