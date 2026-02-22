"""
Database Validation & Import Service
Ensures database connectivity and handles data imports
"""

from sqlalchemy import create_engine, inspect, text, event
from sqlalchemy.pool import Pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, DatabaseError
from models import Base, User, Athlete, Race, Event, Registration, Result, init_db
from config import DevelopmentConfig, ProductionConfig
import os
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json
import csv
from io import StringIO

logger = logging.getLogger(__name__)

class DatabaseValidator:
    """Validates database connectivity and health"""
    
    def __init__(self, config=None):
        self.config = config or DevelopmentConfig()
        self.engine = None
        self.SessionLocal = None
        self.connection_status = False
        self.tables_status = {}
        
    def connect(self) -> bool:
        """Attempt database connection with logging"""
        try:
            self.engine = create_engine(
                self.config.DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verify connections before using
                echo=self.config.DEBUG
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.SessionLocal = sessionmaker(bind=self.engine)
            self.connection_status = True
            logger.info("✅ Database connection successful")
            return True
            
        except Exception as e:
            self.connection_status = False
            logger.error(f"❌ Database connection failed: {str(e)}")
            return False
    
    def verify_tables(self) -> Dict[str, bool]:
        """Check if all required tables exist"""
        if not self.connection_status:
            logger.warning("⚠️  Database not connected. Cannot verify tables.")
            return {}
        
        try:
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = ['users', 'athletes', 'races', 'events', 'registrations', 'results']
            
            self.tables_status = {
                table: (table in existing_tables) 
                for table in required_tables
            }
            
            all_exist = all(self.tables_status.values())
            status_msg = "✅ All tables exist" if all_exist else "⚠️  Some tables missing"
            logger.info(f"{status_msg}: {self.tables_status}")
            
            return self.tables_status
            
        except Exception as e:
            logger.error(f"❌ Table verification failed: {str(e)}")
            return {}
    
    def initialize_database(self) -> bool:
        """Create all tables if they don't exist"""
        if not self.connection_status:
            if not self.connect():
                return False
        
        try:
            logger.info("🔄 Initializing database schema...")
            init_db()
            logger.info("✅ Database schema initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            return False
    
    def check_health(self) -> Dict:
        """Comprehensive database health check"""
        if not self.connection_status:
            self.connect()
        
        health = {
            'status': 'healthy' if self.connection_status else 'unhealthy',
            'connected': self.connection_status,
            'tables': self.verify_tables(),
            'record_counts': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if self.connection_status and self.SessionLocal:
            try:
                session = self.SessionLocal()
                health['record_counts'] = {
                    'users': session.query(User).count(),
                    'athletes': session.query(Athlete).count(),
                    'races': session.query(Race).count(),
                    'events': session.query(Event).count(),
                    'registrations': session.query(Registration).count(),
                    'results': session.query(Result).count(),
                }
                session.close()
            except Exception as e:
                logger.warning(f"⚠️  Could not retrieve record counts: {str(e)}")
        
        return health


class DataImportService:
    """Handles bulk data imports with validation"""
    
    def __init__(self, db_session: Session):
        self.session = db_session
        self.import_log = []
        self.error_log = []
    
    def import_athletes_csv(self, csv_content: str) -> Dict:
        """Import athletes from CSV content"""
        result = {
            'success': 0,
            'failed': 0,
            'errors': [],
            'imported_ids': []
        }
        
        try:
            csv_file = StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
                try:
                    athlete = Athlete(
                        name=row.get('name', '').strip(),
                        country=row.get('country', 'UNK').strip()[:3],
                        gender=row.get('gender', '').strip(),
                        contact_email=row.get('email', '').strip() or None,
                        contact_phone=row.get('phone', '').strip() or None,
                        club_team=row.get('club', '').strip() or None,
                        coach_name=row.get('coach', '').strip() or None,
                        bib_number=row.get('bib_number', '').strip() or None
                    )
                    
                    # Validate required fields
                    if not athlete.name:
                        raise ValueError("Name is required")
                    if not athlete.country:
                        raise ValueError("Country is required")
                    
                    self.session.add(athlete)
                    self.session.flush()
                    result['imported_ids'].append(athlete.id)
                    result['success'] += 1
                    
                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append(f"Row {row_num}: {str(e)}")
                    logger.warning(f"⚠️  Error importing athlete at row {row_num}: {str(e)}")
            
            self.session.commit()
            logger.info(f"✅ Imported {result['success']} athletes")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ CSV import failed: {str(e)}")
            result['errors'].append(f"Import failed: {str(e)}")
        
        return result
    
    def import_races_json(self, json_content: str) -> Dict:
        """Import races from JSON content"""
        result = {
            'success': 0,
            'failed': 0,
            'errors': [],
            'imported_ids': []
        }
        
        try:
            data = json.loads(json_content)
            races_list = data if isinstance(data, list) else data.get('races', [])
            
            for item in races_list:
                try:
                    race = Race(
                        name=item.get('name', '').strip(),
                        date=datetime.fromisoformat(item['date']) if 'date' in item else datetime.utcnow(),
                        location=item.get('location', 'TBD').strip(),
                        status=item.get('status', 'scheduled').strip(),
                        registration_open=item.get('registration_open', True),
                        registration_link=item.get('registration_link', '').strip() or None,
                        description=item.get('description', '').strip() or None
                    )
                    
                    # Validate
                    if not race.name:
                        raise ValueError("Race name is required")
                    
                    self.session.add(race)
                    self.session.flush()
                    result['imported_ids'].append(race.id)
                    result['success'] += 1
                    
                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append(f"Race import error: {str(e)}")
                    logger.warning(f"⚠️  Error importing race: {str(e)}")
            
            self.session.commit()
            logger.info(f"✅ Imported {result['success']} races")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ JSON import failed: {str(e)}")
            result['errors'].append(f"Import failed: {str(e)}")
        
        return result
    
    def import_bulk_json(self, json_content: str) -> Dict:
        """Import multiple data types from JSON"""
        result = {
            'users': {'success': 0, 'failed': 0},
            'athletes': {'success': 0, 'failed': 0},
            'races': {'success': 0, 'failed': 0},
            'events': {'success': 0, 'failed': 0},
            'errors': []
        }
        
        try:
            data = json.loads(json_content)
            
            # Import Users
            for user_data in data.get('users', []):
                try:
                    user = User(
                        name=user_data.get('name'),
                        email=user_data.get('email'),
                        role=user_data.get('role', 'viewer'),
                        status=user_data.get('status', 'active')
                    )
                    user.set_password(user_data.get('password', 'DefaultPassword123'))
                    self.session.add(user)
                    result['users']['success'] += 1
                except Exception as e:
                    result['users']['failed'] += 1
                    result['errors'].append(f"User import: {str(e)}")
            
            # Import Athletes
            for athlete_data in data.get('athletes', []):
                try:
                    athlete = Athlete(
                        name=athlete_data.get('name'),
                        country=athlete_data.get('country', 'UNK'),
                        gender=athlete_data.get('gender'),
                        contact_email=athlete_data.get('email'),
                        contact_phone=athlete_data.get('phone'),
                        club_team=athlete_data.get('club'),
                        coach_name=athlete_data.get('coach')
                    )
                    self.session.add(athlete)
                    result['athletes']['success'] += 1
                except Exception as e:
                    result['athletes']['failed'] += 1
                    result['errors'].append(f"Athlete import: {str(e)}")
            
            # Import Races
            for race_data in data.get('races', []):
                try:
                    race = Race(
                        name=race_data.get('name'),
                        location=race_data.get('location', 'TBD'),
                        status=race_data.get('status', 'scheduled')
                    )
                    self.session.add(race)
                    result['races']['success'] += 1
                except Exception as e:
                    result['races']['failed'] += 1
                    result['errors'].append(f"Race import: {str(e)}")
            
            self.session.commit()
            logger.info(f"✅ Bulk import completed")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Bulk import failed: {str(e)}")
            result['errors'].append(f"Import failed: {str(e)}")
        
        return result


class DataExportService:
    """Handles data exports in multiple formats"""
    
    def __init__(self, db_session: Session):
        self.session = db_session
    
    def export_athletes_csv(self) -> str:
        """Export athletes as CSV"""
        try:
            athletes = self.session.query(Athlete).all()
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                'id', 'name', 'country', 'gender', 'email', 'phone', 'club', 'coach', 'bib_number'
            ])
            
            writer.writeheader()
            for athlete in athletes:
                writer.writerow({
                    'id': athlete.id,
                    'name': athlete.name,
                    'country': athlete.country,
                    'gender': athlete.gender,
                    'email': athlete.contact_email,
                    'phone': athlete.contact_phone,
                    'club': athlete.club_team,
                    'coach': athlete.coach_name,
                    'bib_number': athlete.bib_number
                })
            
            return output.getvalue()
        except Exception as e:
            logger.error(f"❌ Athletes export failed: {str(e)}")
            return ""
    
    def export_all_json(self) -> str:
        """Export all data as JSON"""
        try:
            export_data = {
                'users': [u.to_dict() for u in self.session.query(User).all()],
                'athletes': [a.to_dict() for a in self.session.query(Athlete).all()],
                'races': [r.to_dict() for r in self.session.query(Race).all()],
                'exported_at': datetime.utcnow().isoformat()
            }
            return json.dumps(export_data, indent=2)
        except Exception as e:
            logger.error(f"❌ JSON export failed: {str(e)}")
            return "{}"


# Initialization function for app startup
def setup_database_with_validation():
    """Setup and validate database on app startup"""
    import sys
    
    validator = DatabaseValidator()
    
    print("\n" + "="*60)
    print("🔍 DATABASE CONNECTIVITY CHECK")
    print("="*60)
    
    # Step 1: Connect
    print("\n1️⃣  Attempting database connection...")
    if not validator.connect():
        print("❌ CRITICAL: Cannot connect to database!")
        print(f"   Database URL: {validator.config.DATABASE_URL}")
        print("\n   Possible fixes:")
        print("   • Check PostgreSQL is running")
        print("   • Verify DATABASE_URL in .env or config")
        print("   • Check database credentials")
        return False
    
    # Step 2: Verify tables
    print("\n2️⃣  Verifying database tables...")
    tables = validator.verify_tables()
    if not tables:
        print("⚠️  No tables found. Initializing database schema...")
        if validator.initialize_database():
            validator.verify_tables()
        else:
            print("❌ CRITICAL: Could not initialize database!")
            return False
    
    # Step 3: Health check
    print("\n3️⃣  Performing health check...")
    health = validator.check_health()
    print(f"   Status: {health['status']}")
    print(f"   Tables: {sum(1 for v in health['tables'].values() if v)}/{len(health['tables'])} ✅")
    for entity, count in health['record_counts'].items():
        print(f"   {entity.capitalize()}: {count} records")
    
    print("\n" + "="*60)
    print("✅ DATABASE READY FOR OPERATION")
    print("="*60 + "\n")
    
    return True


if __name__ == '__main__':
    # Test database connectivity
    setup_database_with_validation()
