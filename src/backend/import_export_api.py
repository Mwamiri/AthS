"""
Database Import/Export API Endpoints
Handles bulk data imports, exports, and database validation
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import json
import csv
from io import StringIO, BytesIO
import logging

# Import database and services
from models import SessionLocal, User, Athlete, Race, Event, Registration, Result
from db_validator import DatabaseValidator, DataImportService, DataExportService

logger = logging.getLogger(__name__)

# Create Blueprint
import_export_bp = Blueprint('import_export', __name__, url_prefix='/api/admin')


# ================================================================================
# DATABASE HEALTH & VALIDATION ENDPOINTS
# ================================================================================

@import_export_bp.route('/database/health', methods=['GET'])
def database_health_check():
    """Get comprehensive database health status"""
    validator = DatabaseValidator()
    health = validator.check_health()
    
    status_code = 200 if health['status'] == 'healthy' else 503
    
    return jsonify({
        'health_check': health,
        'timestamp': datetime.utcnow().isoformat(),
        'message': '✅ Health check complete' if health['status'] == 'healthy' else '⚠️  Database degraded'
    }), status_code


@import_export_bp.route('/database/validate', methods=['POST'])
def validate_database():
    """Validate database connectivity and schema"""
    validator = DatabaseValidator()
    
    # Step 1: Connect
    if not validator.connect():
        return jsonify({
            'status': 'failed',
            'error': 'Cannot connect to database',
            'database_url': validator.config.DATABASE_URL,
            'message': '❌ Database connection failed'
        }), 503
    
    # Step 2: Verify tables
    tables = validator.verify_tables()
    
    # Step 3: Check record counts
    health = validator.check_health()
    
    return jsonify({
        'status': 'success',
        'connection': health['connected'],
        'tables': health['tables'],
        'record_counts': health['record_counts'],
        'timestamp': health['timestamp'],
        'message': '✅ Database validation successful'
    }), 200


@import_export_bp.route('/database/initialize', methods=['POST'])
def initialize_database():
    """Initialize database schema (create tables if not exist)"""
    validator = DatabaseValidator()
    
    if not validator.connect():
        return jsonify({
            'status': 'failed',
            'error': 'Cannot connect to database',
            'message': '❌ Database connection required'
        }), 503
    
    # Check if tables already exist
    existing_tables = validator.verify_tables()
    if all(existing_tables.values()):
        return jsonify({
            'status': 'already_initialized',
            'tables': existing_tables,
            'message': '⚠️  Database is already initialized'
        }), 200
    
    # Initialize
    if validator.initialize_database():
        validator.verify_tables()
        health = validator.check_health()
        
        return jsonify({
            'status': 'success',
            'tables_created': health['tables'],
            'message': '✅ Database initialization complete'
        }), 201
    else:
        return jsonify({
            'status': 'failed',
            'error': 'Could not initialize database',
            'message': '❌ Database initialization failed'
        }), 500


# ================================================================================
# DATA IMPORT ENDPOINTS (CSV/JSON)
# ================================================================================

@import_export_bp.route('/import/athletes-csv', methods=['POST'])
def import_athletes_csv():
    """Import athletes from CSV format"""
    if 'file' not in request.files:
        return jsonify({
            'status': 'failed',
            'error': 'No file provided',
            'message': '❌ CSV file is required'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'status': 'failed',
            'error': 'No file selected',
            'message': '❌ Please select a file'
        }), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({
            'status': 'failed',
            'error': 'Invalid file type',
            'message': '❌ Only CSV files are supported'
        }), 400
    
    try:
        # Read CSV file
        csv_content = file.read().decode('utf-8')
        
        # Import using service
        db = SessionLocal()
        service = DataImportService(db)
        result = service.import_athletes_csv(csv_content)
        
        return jsonify({
            'status': 'success' if result['failed'] == 0 else 'partial',
            'imported': result['success'],
            'failed': result['failed'],
            'imported_ids': result['imported_ids'],
            'errors': result['errors'],
            'message': f"✅ Imported {result['success']} athletes" if result['failed'] == 0 else f"⚠️  Imported {result['success']}, failed {result['failed']}"
        }), 201 if result['failed'] == 0 else 207
        
    except Exception as e:
        logger.error(f"CSV import error: {str(e)}")
        return jsonify({
            'status': 'failed',
            'error': 'Import failed',
            'message': f'❌ Error: {str(e)}'
        }), 500


@import_export_bp.route('/import/races-json', methods=['POST'])
def import_races_json():
    """Import races from JSON format"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'failed',
            'error': 'No data provided',
            'message': '❌ JSON data is required'
        }), 400
    
    try:
        # Convert to JSON string if needed
        if isinstance(data, dict) or isinstance(data, list):
            json_content = json.dumps(data)
        else:
            json_content = str(data)
        
        # Import using service
        db = SessionLocal()
        service = DataImportService(db)
        result = service.import_races_json(json_content)
        
        return jsonify({
            'status': 'success' if result['failed'] == 0 else 'partial',
            'imported': result['success'],
            'failed': result['failed'],
            'imported_ids': result['imported_ids'],
            'errors': result['errors'],
            'message': f"✅ Imported {result['success']} races" if result['failed'] == 0 else f"⚠️  Imported {result['success']}, failed {result['failed']}"
        }), 201 if result['failed'] == 0 else 207
        
    except Exception as e:
        logger.error(f"JSON import error: {str(e)}")
        return jsonify({
            'status': 'failed',
            'error': 'Import failed',
            'message': f'❌ Error: {str(e)}'
        }), 500


@import_export_bp.route('/import/bulk-json', methods=['POST'])
def import_bulk_json():
    """Import multiple data types from single JSON file"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'failed',
            'error': 'No data provided',
            'message': '❌ JSON data is required. Expected: {users: [], athletes: [], races: [], events: []}'
        }), 400
    
    try:
        # Import using service
        db = SessionLocal()
        service = DataImportService(db)
        json_content = json.dumps(data)
        result = service.import_bulk_json(json_content)
        
        total_imported = sum(v['success'] for v in result.values() if isinstance(v, dict))
        total_failed = sum(v['failed'] for v in result.values() if isinstance(v, dict))
        
        return jsonify({
            'status': 'success' if total_failed == 0 else 'partial',
            'results': {
                'users': result['users'],
                'athletes': result['athletes'],
                'races': result['races'],
                'events': result['events']
            },
            'total_imported': total_imported,
            'total_failed': total_failed,
            'errors': result['errors'],
            'message': f"✅ Bulk import complete: {total_imported} records" if total_failed == 0 else f"⚠️  Partial import: {total_imported} success, {total_failed} failed"
        }), 201 if total_failed == 0 else 207
        
    except Exception as e:
        logger.error(f"Bulk import error: {str(e)}")
        return jsonify({
            'status': 'failed',
            'error': 'Bulk import failed',
            'message': f'❌ Error: {str(e)}'
        }), 500


# ================================================================================
# DATA EXPORT ENDPOINTS (CSV/JSON)
# ================================================================================

@import_export_bp.route('/export/athletes-csv', methods=['GET'])
def export_athletes_csv():
    """Export all athletes as CSV file"""
    try:
        db = SessionLocal()
        service = DataExportService(db)
        csv_content = service.export_athletes_csv()
        
        # Create file buffer
        output = BytesIO()
        output.write(csv_content.encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'athletes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        logger.error(f"Athletes export error: {str(e)}")
        return jsonify({
            'status': 'failed',
            'error': 'Export failed',
            'message': f'❌ Error: {str(e)}'
        }), 500


@import_export_bp.route('/export/all-json', methods=['GET'])
def export_all_json():
    """Export all data as JSON file"""
    try:
        db = SessionLocal()
        service = DataExportService(db)
        json_content = service.export_all_json()
        
        # Create response
        response = {
            'data': json.loads(json_content),
            'exported_at': datetime.utcnow().isoformat(),
            'format': 'json',
            'message': '✅ Data exported successfully'
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"JSON export error: {str(e)}")
        return jsonify({
            'status': 'failed',
            'error': 'Export failed',
            'message': f'❌ Error: {str(e)}'
        }), 500


@import_export_bp.route('/export/races-csv', methods=['GET'])
def export_races_csv():
    """Export all races as CSV file"""
    try:
        db = SessionLocal()
        races = db.query(Race).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=['id', 'name', 'date', 'location', 'status', 'created_at'])
        
        writer.writeheader()
        for race in races:
            writer.writerow({
                'id': race.id,
                'name': race.name,
                'date': race.date.isoformat() if race.date else '',
                'location': race.location,
                'status': race.status,
                'created_at': race.created_at.isoformat() if race.created_at else ''
            })
        
        # Create file buffer
        output_buffer = BytesIO()
        output_buffer.write(output.getvalue().encode('utf-8'))
        output_buffer.seek(0)
        
        return send_file(
            output_buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'races_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        logger.error(f"Races export error: {str(e)}")
        return jsonify({
            'status': 'failed',
            'error': 'Export failed',
            'message': f'❌ Error: {str(e)}'
        }), 500


# ================================================================================
# IMPORT TEMPLATE/FORMAT ENDPOINTS
# ================================================================================

@import_export_bp.route('/import/athletes-template', methods=['GET'])
def get_athletes_import_template():
    """Get sample CSV template for athletes import"""
    template = {
        'format': 'CSV',
        'headers': ['name', 'country', 'gender', 'email', 'phone', 'club', 'coach', 'bib_number'],
        'sample_data': [
            {
                'name': 'John Kipchoge',
                'country': 'KEN',
                'gender': 'M',
                'email': 'john@example.com',
                'phone': '+254700000000',
                'club': 'Elite Runners',
                'coach': 'Coach Ali',
                'bib_number': '101'
            },
            {
                'name': 'Mary Kipchoge',
                'country': 'KEN',
                'gender': 'F',
                'email': 'mary@example.com',
                'phone': '+254700000001',
                'club': 'Elite Runners',
                'coach': 'Coach Ali',
                'bib_number': '102'
            }
        ],
        'requirements': {
            'name': 'Required, string',
            'country': 'Required, 3-letter country code (e.g., KEN, USA, GBR)',
            'gender': 'Optional, M or F',
            'email': 'Optional, valid email',
            'phone': 'Optional, phone number',
            'club': 'Optional, club/team name',
            'coach': 'Optional, coach name',
            'bib_number': 'Optional, unique bib number'
        }
    }
    
    return jsonify({
        'template': template,
        'message': '✅ Import template retrieved'
    }), 200


@import_export_bp.route('/import/races-template', methods=['GET'])
def get_races_import_template():
    """Get sample JSON template for races import"""
    template = {
        'format': 'JSON',
        'structure': {
            'races': [
                {
                    'name': 'Olympic Marathon',
                    'date': '2026-08-15',
                    'location': 'Paris, France',
                    'status': 'scheduled',
                    'description': 'Elite marathon competition'
                },
                {
                    'name': '100m Sprint',
                    'date': '2026-08-16',
                    'location': 'Paris, France',
                    'status': 'scheduled',
                    'description': 'Sprint race event'
                }
            ]
        },
        'requirements': {
            'name': 'Required, string',
            'date': 'Required, YYYY-MM-DD format',
            'location': 'Required, string',
            'status': 'Optional, scheduled|ongoing|completed|cancelled',
            'description': 'Optional, string'
        }
    }
    
    return jsonify({
        'template': template,
        'message': '✅ Import template retrieved'
    }), 200


@import_export_bp.route('/import/bulk-template', methods=['GET'])
def get_bulk_import_template():
    """Get sample JSON template for bulk multi-type import"""
    template = {
        'format': 'JSON',
        'structure': {
            'users': [
                {
                    'name': 'Admin User',
                    'email': 'admin@example.com',
                    'role': 'admin',
                    'password': 'SecurePass@123'
                }
            ],
            'athletes': [
                {
                    'name': 'John Athlete',
                    'country': 'KEN',
                    'gender': 'M',
                    'email': 'john@example.com',
                    'club': 'Club Name'
                }
            ],
            'races': [
                {
                    'name': 'Marathon Race',
                    'date': '2026-08-15',
                    'location': 'City',
                    'status': 'scheduled'
                }
            ],
            'events': [
                {
                    'name': '100m',
                    'category': 'Sprint',
                    'gender': 'M',
                    'distance': '100'
                }
            ]
        },
        'requirements': {
            'users': 'Array of user objects (name, email, role, password)',
            'athletes': 'Array of athlete objects',
            'races': 'Array of race objects',
            'events': 'Array of event objects'
        }
    }
    
    return jsonify({
        'template': template,
        'message': '✅ Bulk import template retrieved'
    }), 200


# ================================================================================
# DATA SYNCHRONIZATION ENDPOINTS
# ================================================================================

@import_export_bp.route('/sync/status', methods=['GET'])
def sync_status():
    """Get data synchronization status"""
    try:
        validator = DatabaseValidator()
        validator.connect()
        health = validator.check_health()
        
        return jsonify({
            'last_sync': datetime.utcnow().isoformat(),
            'records': health['record_counts'],
            'status': 'synchronized',
            'message': '✅ Data is synchronized'
        }), 200
        
    except Exception as e:
        logger.error(f"Sync status error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Could not retrieve sync status',
            'message': f'❌ Error: {str(e)}'
        }), 500


# Register blueprint in app
def register_import_export_blueprint(app):
    """Register the import/export blueprint with the Flask app"""
    app.register_blueprint(import_export_bp)
    logger.info("✅ Import/Export API endpoints registered")

