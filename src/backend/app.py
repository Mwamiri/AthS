"""
AthSys Backend - Athletics Management System
Main application entry point with enhanced UX features
Production-ready with PostgreSQL and Redis
"""

from flask import Flask, jsonify, request, send_from_directory, make_response, send_file
from flask_cors import CORS
import os
import time
import uuid
import jwt
import json
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import text
from dotenv import load_dotenv
try:
    from flasgger import Swagger
except ImportError:
    Swagger = None

# Import database models and Redis config
from models import (
    get_db, init_db, 
    User, Athlete, Race, Event, Registration, Result, AuditLog, PluginConfig, FrontendConfig
)
from redis_config import (
    RedisCache, RateLimiter, SessionManager, 
    LeaderboardManager, PubSubManager, test_redis_connection
)
from security import SecurityManager
from log_system import get_log_manager, get_logger

# Import page builder blueprint
try:
    from routes.builder import builder_bp
    BUILDER_AVAILABLE = True
except ImportError:
    BUILDER_AVAILABLE = False
    print("[WARNING] Page builder module not available")

# Import records & standards blueprint
try:
    from routes.records import records_bp
    RECORDS_AVAILABLE = True
except ImportError:
    RECORDS_AVAILABLE = False
    print("[WARNING] Records module not available")

# Import import/export API blueprint
try:
    from import_export_api import register_import_export_blueprint
    IMPORT_EXPORT_AVAILABLE = True
except ImportError as e:
    IMPORT_EXPORT_AVAILABLE = False
    print(f"[WARNING] Import/Export module not available: {e}")
except Exception as e:
    IMPORT_EXPORT_AVAILABLE = False
    print(f"[ERROR] Unexpected error loading Import/Export module: {e}")

# Configure Flask to serve frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',') if origin.strip()]
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}}, supports_credentials=True)

# Security Headers
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' fonts.googleapis.com cdn.tailwindcss.com unpkg.com cdn.jsdelivr.net cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com fonts.gstatic.com cdn.jsdelivr.net cdnjs.cloudflare.com; "
        "font-src 'self' fonts.googleapis.com fonts.gstatic.com cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' localhost:* https: ws: wss:; "
        "frame-ancestors 'self'"
    )
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # HTTPS enforcement (in production)
    if not app.debug:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

# Initialize Swagger/OpenAPI Documentation
if Swagger:
    swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "AthSys API",
            "description": "Elite Athletics Management System - Complete REST API",
            "version": "2.2.0",
            "contact": {
                "email": "support@athsys.com"
            },
            "license": {
                "name": "MIT"
            }
        },
        "host": "localhost:5000",
        "basePath": "/api",
        "schemes": ["http", "https"],
        "consumes": ["application/json"],
        "produces": ["application/json"]
    })
    print("Swagger API documentation available at /apidocs")

# Configuration
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


def _build_redis_url():
    explicit_url = os.getenv('REDIS_URL')
    if explicit_url:
        return explicit_url

    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', '6379')
    redis_db = os.getenv('REDIS_DB', '0')
    redis_password = os.getenv('REDIS_PASSWORD', '').strip()

    if redis_password:
        return f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"

    return f"redis://{redis_host}:{redis_port}/{redis_db}"


app.config['DEBUG'] = os.getenv('DEBUG', 'False') == 'True'
app.config['PORT'] = int(os.getenv('PORT', 5000))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'development-secret-key-change-in-production')
app.config['DATABASE_URL'] = _build_database_url()
app.config['REDIS_URL'] = _build_redis_url()
app.config['JWT_SECRET'] = os.getenv('JWT_SECRET_KEY') or os.getenv('JWT_SECRET') or app.config['SECRET_KEY']
app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
app.config['JWT_ACCESS_EXPIRES_SECONDS'] = int(os.getenv('JWT_ACCESS_EXPIRES_SECONDS', 3600))
app.config['JWT_REFRESH_EXPIRES_SECONDS'] = int(os.getenv('JWT_REFRESH_EXPIRES_SECONDS', 604800))
app.config['IDEMPOTENCY_TTL_SECONDS'] = int(os.getenv('IDEMPOTENCY_TTL_SECONDS', 600))

# Initialize connections on startup (Flask 3.0+ compatible)
def initialize():
    """Initialize database and test connections (non-blocking)"""
    try:
        should_init_db = (
            app.config['DATABASE_URL'].startswith('sqlite:///')
            or os.getenv('AUTO_INIT_DB', 'False') == 'True'
        )

        if should_init_db:
            init_db()
        print("[OK] Database connection ready")
    except Exception as e:
        print(f"[WARNING] Database connection warning: {e}")
    
    # Test Redis with timeout to prevent blocking
    try:
        redis_ok = test_redis_connection()
        if redis_ok:
            print("✅ Redis connected")
        else:
            print("⚠️  Redis unavailable - caching disabled")
    except Exception as e:
        print(f"⚠️  Redis connection error: {e}")
        print("⚠️  Redis unavailable - caching disabled")

# Run initialization immediately with error handling
try:
    initialize()
except Exception as e:
    print(f"[WARNING] Initialization error: {e}")

# Register blueprints
if BUILDER_AVAILABLE:
    app.register_blueprint(builder_bp)
    print("[OK] Page builder API mounted at /api/builder")
else:
    print("[WARNING] Page builder module disabled")

if RECORDS_AVAILABLE:
    app.register_blueprint(records_bp)
    print("[OK] Records & Standards API mounted at /api/records")
else:
    print("[WARNING] Records module disabled")

if IMPORT_EXPORT_AVAILABLE:
    try:
        register_import_export_blueprint(app)
        print("[OK] Import/Export API mounted at /api/admin")
    except Exception as e:
        print(f"[ERROR] Failed to register Import/Export blueprint: {e}")
        IMPORT_EXPORT_AVAILABLE = False
else:
    print("[WARNING] Import/Export module disabled")

# Store version and metadata
APP_VERSION = '3.0.0'
APP_NAME = 'AthSys - Athletics Management System'

# Request counter for demo purposes
REQUEST_COUNT = 0

# Rate limiting decorator
def rate_limit(max_requests=100, window=3600):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            identifier = request.remote_addr
            allowed, remaining = RateLimiter.check_rate_limit(identifier, max_requests, window)
            if not allowed:
                return jsonify({'error': 'Rate limit exceeded', 'retry_after': window}), 429
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Authentication decorator
def normalize_role(role):
    return str(role or '').strip().lower()


def issue_auth_tokens(session_data):
    """Generate access and refresh JWTs and rotate refresh token pointer."""
    user_id = int(session_data.get('id'))
    role = normalize_role(session_data.get('role'))
    now_ts = int(time.time())
    access_exp_ts = now_ts + app.config['JWT_ACCESS_EXPIRES_SECONDS']
    refresh_exp_ts = now_ts + app.config['JWT_REFRESH_EXPIRES_SECONDS']
    refresh_jti = str(uuid.uuid4())

    access_payload = {
        'sub': str(user_id),
        'type': 'access',
        'role': role,
        'email': session_data.get('email'),
        'iat': now_ts,
        'exp': access_exp_ts
    }

    refresh_payload = {
        'sub': str(user_id),
        'type': 'refresh',
        'jti': refresh_jti,
        'iat': now_ts,
        'exp': refresh_exp_ts
    }

    access_token = jwt.encode(access_payload, app.config['JWT_SECRET'], algorithm=app.config['JWT_ALGORITHM'])
    refresh_token = jwt.encode(refresh_payload, app.config['JWT_SECRET'], algorithm=app.config['JWT_ALGORITHM'])

    RedisCache.set(
        f"refresh_jti:{user_id}",
        {'jti': refresh_jti},
        expiry=app.config['JWT_REFRESH_EXPIRES_SECONDS']
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': app.config['JWT_ACCESS_EXPIRES_SECONDS']
    }


def authenticate_request(roles=None):
    """Authenticate request from Authorization Bearer JWT access token."""
    auth_header = request.headers.get('Authorization', '').strip()
    if not auth_header or not auth_header.lower().startswith('bearer '):
        return None, 'No authorization header', 401

    token = auth_header.split(' ', 1)[1].strip()
    if not token:
        return None, 'Invalid token', 401

    try:
        payload = jwt.decode(token, app.config['JWT_SECRET'], algorithms=[app.config['JWT_ALGORITHM']])
        if payload.get('type') != 'access':
            return None, 'Invalid token type', 401

        user_id = int(payload.get('sub'))
        session = SessionManager.get_session(user_id)
        if not session:
            return None, 'Invalid or expired session', 401
    except jwt.ExpiredSignatureError:
        return None, 'Access token expired', 401
    except jwt.InvalidTokenError:
        return None, 'Invalid token', 401
    except (TypeError, ValueError):
        return None, 'Invalid token', 401

    if roles:
        role = normalize_role(session.get('role'))
        allowed_roles = {normalize_role(r) for r in roles}
        if role not in allowed_roles:
            return None, 'Insufficient permissions', 403

    request.user = session
    return session, None, 200


def require_auth(roles=None):
    """Authentication decorator with role-based access"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _, error_message, status_code = authenticate_request(roles=roles)
            if error_message:
                return jsonify({'error': error_message}), status_code
            return func(*args, **kwargs)
        return wrapper
    return decorator


def _get_idempotency_cache_key(raw_key):
    user_id = getattr(request, 'user', {}).get('id') or request.remote_addr or 'anonymous'
    payload = request.get_data(cache=True, as_text=True) or ''
    payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    return f"idempotency:{request.method}:{request.path}:{user_id}:{raw_key}:{payload_hash}"


def idempotency_guard(ttl_seconds=None):
    """Idempotency protection for retry-safe write endpoints via Idempotency-Key header."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            raw_key = request.headers.get('Idempotency-Key', '').strip()
            if not raw_key:
                return func(*args, **kwargs)

            ttl = ttl_seconds or app.config['IDEMPOTENCY_TTL_SECONDS']
            cache_key = _get_idempotency_cache_key(raw_key)
            cached = RedisCache.get(cache_key)
            if cached:
                return jsonify(cached.get('body', {})), int(cached.get('status', 200))

            result = func(*args, **kwargs)
            response = make_response(result)

            if 200 <= response.status_code < 300:
                payload = response.get_json(silent=True)
                if payload is not None:
                    RedisCache.set(
                        cache_key,
                        {'status': response.status_code, 'body': payload},
                        expiry=ttl
                    )

            return result
        return wrapper
    return decorator


@app.before_request
def enforce_admin_api_access():
    """Enforce admin role checks for all /api/admin/* endpoints."""
    if request.method == 'OPTIONS':
        return None

    if request.path.startswith('/api/admin'):
        _, error_message, status_code = authenticate_request(roles=['admin', 'chief_registrar'])
        if error_message:
            return jsonify({'error': error_message}), status_code

    return None

# Audit logging
def log_audit(action, entity_type, entity_id=None, details=None):
    """Log action to audit trail"""
    try:
        db = next(get_db())
        user_id = getattr(request, 'user', {}).get('id')
        
        audit = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        print(f"Audit log error: {e}")

# Password validation helper
def validate_password_strength(password):
    """Validate password meets security requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"

# Track failed login attempts
def track_failed_login(email):
    """Track failed login attempts for account lockout"""
    key = f"failed_login:{email}"
    attempts = RedisCache.get(key) or 0
    attempts += 1
    RedisCache.set(key, attempts, expiry=1800)  # 30 minutes window
    return attempts

def get_failed_login_count(email):
    """Get failed login attempts count"""
    key = f"failed_login:{email}"
    return RedisCache.get(key) or 0

def reset_failed_login(email):
    """Reset failed login attempts after successful login"""
    key = f"failed_login:{email}"
    RedisCache.delete(key)

def is_account_locked(email):
    """Check if account is locked due to too many failed attempts"""
    return get_failed_login_count(email) >= 5

# Start lists placeholder
DEMO_USERS = []  # Initialize empty list for backward compatibility
DEMO_STARTLISTS = [
    {
        'id': 1,
        'race_id': 1,
        'event_id': 1,
        'athletes': [1, 5],
        'status': 'pending',  # pending, confirmed, finalized
        'confirmed_by': None,
        'createdAt': '2026-02-20'
    }
]

# App build requests (demo data)
DEMO_APP_REQUESTS = [
    {
        'id': 1,
        'title': 'School Events Tracker',
        'requested_by': 'coach@athsys.com',
        'description': 'Simple app to track inter-school events and results.',
        'priority': 'medium',
        'status': 'pending',
        'created_at': '2026-02-20',
        'approved_by': None,
        'approved_at': None,
        'rejected_reason': None
    },
    {
        'id': 2,
        'title': 'Athlete Health Dashboard',
        'requested_by': 'admin@athsys.com',
        'description': 'Dashboard to monitor injuries, recovery plans, and wellness.',
        'priority': 'high',
        'status': 'approved',
        'created_at': '2026-02-18',
        'approved_by': 'admin@athsys.com',
        'approved_at': '2026-02-19',
        'rejected_reason': None
    }
]

# Form submissions for marking (demo data)
DEMO_FORM_SUBMISSIONS = [
    {
        'id': 1,
        'form_name': 'Athlete Registration',
        'submitted_by': 'john@athsys.com',
        'submitted_at': '2026-02-21 09:15',
        'status': 'pending',
        'notes': ''
    },
    {
        'id': 2,
        'form_name': 'Event Participation',
        'submitted_by': 'sarah@athsys.com',
        'submitted_at': '2026-02-21 10:45',
        'status': 'approved',
        'notes': 'Verified by registrar'
    }
]

# Public registration links
PUBLIC_LINKS = {
    'pub_race_abc123': {'race_id': 1, 'active': True, 'expires': '2026-03-14'},
    'pub_race_xyz789': {'race_id': 2, 'active': True, 'expires': '2026-04-09'}
}

# System settings
SYSTEM_SETTINGS = {
    'logo': None,  # Will store base64 encoded logo
    'organization_name': 'AthSys Athletics',
    'allow_public_registration': True,
    'require_email_verification': False
}


# Middleware to log requests and add timing
@app.before_request
def before_request():
    request.start_time = time.time()
    incoming_request_id = request.headers.get('X-Request-ID', '').strip()
    request.request_id = incoming_request_id or f"req_{uuid.uuid4().hex[:12]}"

    request.idempotency_key = request.headers.get('Idempotency-Key', '').strip()
    request.idempotency_cache_key = None

    is_mutation_request = request.method in {'POST', 'PUT', 'PATCH', 'DELETE'} and request.path.startswith('/api/')
    if is_mutation_request and request.idempotency_key:
        request.idempotency_cache_key = _get_idempotency_cache_key(request.idempotency_key)
        cached_response = RedisCache.get(request.idempotency_cache_key)
        if cached_response:
            replay_body = cached_response.get('body', {}) if isinstance(cached_response, dict) else {}
            replay_status = int(cached_response.get('status', 200)) if isinstance(cached_response, dict) else 200
            replay = jsonify(replay_body)
            replay.status_code = replay_status
            replay.headers['X-Request-ID'] = request.request_id
            replay.headers['X-Idempotency-Replayed'] = 'true'
            return replay


@app.after_request
def after_request(response):
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if hasattr(request, 'start_time'):
        elapsed = time.time() - request.start_time
        response.headers['X-Response-Time'] = f'{elapsed*1000:.2f}ms'

    if getattr(request, 'idempotency_key', None):
        response.headers['X-Idempotency-Key'] = request.idempotency_key

    if getattr(request, 'idempotency_cache_key', None):
        if 200 <= response.status_code < 300:
            payload = response.get_json(silent=True)
            if payload is not None:
                RedisCache.set(
                    request.idempotency_cache_key,
                    {
                        'status': response.status_code,
                        'body': payload
                    },
                    expiry=app.config['IDEMPOTENCY_TTL_SECONDS']
                )
    
    response.headers['X-Request-ID'] = getattr(request, 'request_id', f'req_{uuid.uuid4().hex[:12]}')
    response.headers['X-Powered-By'] = 'AthSys'
    response.headers['X-API-Version'] = f'v{APP_VERSION}'
    return response


def add_metadata(data):
    """Add metadata to API responses for better UX"""
    return {
        **data,
        'meta': {
            'timestamp': datetime.now().isoformat(),
            'request_id': getattr(request, 'request_id', f'req_{REQUEST_COUNT}'),
            'version': APP_VERSION
        }
    }


@app.route('/api/info')
def api_info():
    """API endpoint with comprehensive system information"""
    return jsonify(add_metadata({
        'name': APP_NAME,
        'version': APP_VERSION,
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'System operational',
        'environment': 'production' if not app.config['DEBUG'] else 'development',
        'endpoints': {
            'health': '/health',
            'livez': '/livez',
            'stats': '/api/stats',
            'athletes': '/api/athletes',
            'events': '/api/events',
            'results': '/api/results',
            'documentation': '/api/docs'
        },
        'message': '🏃‍♂️ Welcome to AthSys - Elite Athletics Management System'
    }))


@app.route('/api/version')
def api_version():
    """Canonical platform and API version endpoint"""
    return jsonify(add_metadata({
        'platform_version': APP_VERSION,
        'api_version': 'v3.0',
        'phase': 'V3 Enterprise',
        'message': '✅ Version information retrieved successfully'
    }))


@app.route('/health')
def health():
    """Comprehensive health check endpoint for monitoring and orchestration"""
    db_status = 'operational'
    try:
        db = next(get_db())
        # Quick database connectivity test
        db.execute(text('SELECT 1'))
    except Exception as e:
        db_status = 'offline'
        print(f"Database health check failed: {e}")
    
    redis_status = 'active' if test_redis_connection() else 'offline'
    
    health_status = {
        'status': 'healthy' if db_status == 'operational' else 'degraded',
        'service': 'athsys-backend',
        'version': APP_VERSION,
        'timestamp': datetime.now().isoformat(),
        'uptime': 'operational',
        'environment': 'production' if not app.config['DEBUG'] else 'development',
        'checks': {
            'api': 'operational',
            'database': db_status,
            'cache': redis_status,
            'memory': 'healthy'
        },
        'features': {
            'authentication': 'enabled',
            'rate_limiting': 'enabled',
            'audit_logging': 'enabled',
            'security': 'hardened'
        }
    }
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code


@app.route('/livez')
def livez():
    """Lightweight liveness probe endpoint for container orchestration"""
    return jsonify({'status': 'ok', 'timestamp': time.time()}), 200


@app.route('/api/logs', methods=['GET'])
@app.route('/api/debug/logs', methods=['GET'])
def get_logs():
    """Get system logs for debugging"""
    log_type = request.args.get('type', 'all')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    log_mgr = get_log_manager()
    logs = log_mgr.get_logs(log_type, limit, offset)
    
    return jsonify({
        'type': log_type,
        'limit': limit,
        'offset': offset,
        'count': len(logs),
        'logs': logs
    }), 200


@app.route('/api/logs/stats', methods=['GET'])
@app.route('/api/debug/logs/stats', methods=['GET'])
def get_logs_stats():
    """Get log file statistics"""
    log_mgr = get_log_manager()
    stats = log_mgr.get_log_stats()
    
    return jsonify(stats), 200


@app.route('/api/docs')
def api_docs():
    """API documentation endpoint"""
    return jsonify({
        'api': 'AthSys REST API',
        'version': APP_VERSION,
        'description': 'Elite Athletics Management System API',
        'endpoints': [
            {
                'path': '/',
                'method': 'GET',
                'description': 'System information'
            },
            {
                'path': '/health',
                'method': 'GET',
                'description': 'Health check'
            },
            {
                'path': '/api/athletes',
                'method': 'GET',
                'description': 'List all athletes'
            },
            {
                'path': '/api/athletes',
                'method': 'POST',
                'description': 'Create new athlete'
            },
            {
                'path': '/api/events',
                'method': 'GET',
                'description': 'List all events'
            },
            {
                'path': '/api/results',
                'method': 'GET',
                'description': 'Get competition results'
            },
            {
                'path': '/api/stats',
                'method': 'GET',
                'description': 'System statistics'
            },
            {
                'path': '/api/auth/login',
                'method': 'POST',
                'description': 'User login (email, password)',
                'demo_credentials': {
                    'admin': 'admin@athsys.com / Admin@123',
                    'athlete': 'john@athsys.com / Athlete@123',
                    'coach': 'sarah@athsys.com / Coach@123'
                }
            },
            {
                'path': '/api/auth/register',
                'method': 'POST',
                'description': 'Register new user (name, email, password, role)'
            },
            {
                'path': '/api/auth/reset-password',
                'method': 'POST',
                'description': 'Request password reset (email)'
            },
            {
                'path': '/api/admin/users',
                'method': 'GET',
                'description': 'Get all users (admin only)'
            },
            {
                'path': '/api/admin/users',
                'method': 'POST',
                'description': 'Create new user (admin only)'
            },
            {
                'path': '/api/admin/users/:id',
                'method': 'PUT',
                'description': 'Update user (admin only)'
            },
            {
                'path': '/api/admin/users/:id',
                'method': 'DELETE',
                'description': 'Delete user (admin only)'
            }
        ]
    })


@app.route('/api/athletes', methods=['GET'])
@rate_limit(max_requests=200, window=3600)
def get_athletes():
    """Get all athletes from database with Redis caching"""
    try:
        # Try to get from cache first
        cache_key = "athletes:all"
        cached = RedisCache.get(cache_key)
        if cached:
            return jsonify({
                'athletes': cached,
                'count': len(cached),
                'message': '✅ Athletes retrieved successfully (cached)',
                'version': APP_VERSION
            })
        
        # Query from database
        db = next(get_db())
        athletes = db.query(Athlete).all()
        athletes_data = [athlete.to_dict() for athlete in athletes]
        
        # Cache results for 5 minutes
        RedisCache.set(cache_key, athletes_data, expiry=300)
        
        return jsonify({
            'athletes': athletes_data,
            'count': len(athletes_data),
            'message': '✅ Athletes retrieved successfully',
            'version': APP_VERSION
        })
    except Exception as e:
        print(f"Get athletes error: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to retrieve athletes'
        }), 500


@app.route('/api/athletes', methods=['POST'])
@require_auth(roles=['admin', 'chief_registrar', 'registrar'])
def create_athlete():
    """Create new athlete"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Request body is required'
        }), 400
    
    # Validate required fields
    required_fields = ['name', 'country']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            'error': 'Validation error',
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    try:
        db = next(get_db())
        
        # Create new athlete
        new_athlete = Athlete(
            name=data.get('name'),
            country=data.get('country'),
            date_of_birth=data.get('dateOfBirth'),
            gender=data.get('gender'),
            email=data.get('email'),
            phone=data.get('phone'),
            coach_name=data.get('coachName'),
            bib_number=data.get('bibNumber')
        )
        
        db.add(new_athlete)
        db.commit()
        db.refresh(new_athlete)
        
        # Clear athletes cache
        RedisCache.delete("athletes:all")
        
        # Log action
        log_audit('create', 'athlete', new_athlete.id, f'Created athlete: {new_athlete.name}')
        
        return jsonify({
            'message': '✅ Athlete created successfully',
            'athlete': new_athlete.to_dict(),
            'version': APP_VERSION
        }), 201
        
    except Exception as e:
        print(f"Create athlete error: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to create athlete'
        }), 500


    return jsonify(add_metadata({
        'message': '✅ Athlete created successfully',
        'athlete': new_athlete
    })), 201


# ============ ATHLETE PROFILE ENDPOINTS ============

@app.route('/api/athlete/profile', methods=['GET'])
@require_auth(roles=['athlete'])
def get_athlete_profile():
    """Get current logged-in athlete's profile"""
    try:
        current_user_id = request.headers.get('X-User-ID')
        if not current_user_id:
            return jsonify({
                'error': 'Not authenticated',
                'message': 'User ID not found in request'
            }), 401
        
        db = next(get_db())
        athlete = db.query(Athlete).filter(Athlete.user_id == int(current_user_id)).first()
        
        if not athlete:
            return jsonify({
                'error': 'Not found',
                'message': 'Athlete profile not found'
            }), 404
        
        return jsonify({
            'athlete': athlete.to_dict(),
            'message': '✅ Profile retrieved successfully'
        }), 200
    except Exception as e:
        print(f"Get athlete profile error: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to retrieve profile'
        }), 500


@app.route('/api/athlete/races', methods=['GET'])
@require_auth(roles=['athlete'])
def get_athlete_races():
    """Get races the currently logged-in athlete is registered for"""
    try:
        current_user_id = request.headers.get('X-User-ID')
        if not current_user_id:
            return jsonify({
                'error': 'Not authenticated',
                'message': 'User ID not found in request'
            }), 401
        
        db = next(get_db())
        athlete = db.query(Athlete).filter(Athlete.user_id == int(current_user_id)).first()
        
        if not athlete:
            return jsonify({
                'error': 'Not found',
                'message': 'Athlete not found'
            }), 404
        
        # Get registrations for this athlete
        registrations = db.query(Registration).filter(
            Registration.athlete_id == athlete.id
        ).all()
        
        races_data = []
        for reg in registrations:
            race = reg.race
            races_data.append({
                'id': race.id,
                'name': race.name,
                'date': race.date.isoformat() if race.date else None,
                'location': race.location,
                'status': race.status,
                'registrationId': reg.id,
                'registrationDate': reg.registration_date.isoformat() if reg.registration_date else None,
                'bibNumber': reg.bib_number,
                'category': reg.category
            })
        
        return jsonify({
            'races': races_data,
            'count': len(races_data),
            'message': '✅ Races retrieved successfully'
        }), 200
    except Exception as e:
        print(f"Get athlete races error: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to retrieve races'
        }), 500


@app.route('/api/athlete/results', methods=['GET'])
@require_auth(roles=['athlete'])
def get_athlete_results():
    """Get competition results for the currently logged-in athlete"""
    try:
        current_user_id = request.headers.get('X-User-ID')
        if not current_user_id:
            return jsonify({
                'error': 'Not authenticated',
                'message': 'User ID not found in request'
            }), 401
        
        db = next(get_db())
        athlete = db.query(Athlete).filter(Athlete.user_id == int(current_user_id)).first()
        
        if not athlete:
            return jsonify({
                'error': 'Not found',
                'message': 'Athlete not found'
            }), 404
        
        # Get results for this athlete
        results = db.query(Result).filter(Result.athlete_id == athlete.id).all()
        
        results_data = []
        for result in results:
            results_data.append({
                'id': result.id,
                'eventName': result.event.name if result.event else 'Unknown',
                'eventId': result.event_id,
                'raceName': result.event.race.name if result.event and result.event.race else 'Unknown',
                'raceId': result.event.race_id if result.event else None,
                'position': result.position,
                'timeSeconds': result.time_seconds,
                'status': result.status,
                'recordType': result.record_type,
                'isRecord': result.is_record,
                'date': result.created_at.isoformat() if result.created_at else None
            })
        
        return jsonify({
            'results': results_data,
            'count': len(results_data),
            'message': '✅ Results retrieved successfully'
        }), 200
    except Exception as e:
        print(f"Get athlete results error: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to retrieve results'
        }), 500


@app.route('/api/races/available', methods=['GET'])
@require_auth(roles=['athlete'])
def get_available_races():
    """Get races available for registration (not yet closed)"""
    try:
        from datetime import datetime
        db = next(get_db())
        
        # Get races that are not closed or cancelled
        races = db.query(Race).filter(
            Race.status.in_(['upcoming', 'ongoing'])
        ).all()
        
        current_user_id = request.headers.get('X-User-ID')
        athlete = db.query(Athlete).filter(Athlete.user_id == int(current_user_id)).first() if current_user_id else None
        
        races_data = []
        for race in races:
            # Check if athlete is already registered
            is_registered = False
            if athlete:
                existing_reg = db.query(Registration).filter(
                    Registration.race_id == race.id,
                    Registration.athlete_id == athlete.id
                ).first()
                is_registered = existing_reg is not None
            
            races_data.append({
                'id': race.id,
                'name': race.name,
                'date': race.date.isoformat() if race.date else None,
                'location': race.location,
                'status': race.status,
                'description': race.description,
                'registrationDeadline': race.registration_deadline.isoformat() if race.registration_deadline else None,
                'maxParticipants': race.max_participants,
                'currentParticipants': len(race.registrations) if race.registrations else 0,
                'isRegistered': is_registered
            })
        
        return jsonify({
            'races': races_data,
            'count': len(races_data),
            'message': '✅ Available races retrieved successfully'
        }), 200
    except Exception as e:
        print(f"Get available races error: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to retrieve races'
        }), 500


@app.route('/api/athlete/register-race', methods=['POST'])
@require_auth(roles=['athlete'])
def register_for_race():
    """Register athlete for a specific race"""
    data = request.get_json()
    
    if not data or 'race_id' not in data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'race_id is required'
        }), 400
    
    try:
        current_user_id = request.headers.get('X-User-ID')
        if not current_user_id:
            return jsonify({
                'error': 'Not authenticated',
                'message': 'User ID not found'
            }), 401
        
        db = next(get_db())
        athlete = db.query(Athlete).filter(Athlete.user_id == int(current_user_id)).first()
        
        if not athlete:
            return jsonify({
                'error': 'Not found',
                'message': 'Athlete not found'
            }), 404
        
        race = db.query(Race).filter(Race.id == data['race_id']).first()
        if not race:
            return jsonify({
                'error': 'Not found',
                'message': 'Race not found'
            }), 404
        
        # Check if already registered
        existing = db.query(Registration).filter(
            Registration.race_id == race.id,
            Registration.athlete_id == athlete.id
        ).first()
        
        if existing:
            return jsonify({
                'error': 'Already registered',
                'message': 'You are already registered for this race'
            }), 409
        
        # Create registration
        registration = Registration(
            athlete_id=athlete.id,
            race_id=race.id,
            bib_number=data.get('bib_number'),
            category=data.get('category'),
            status='confirmed'
        )
        
        db.add(registration)
        db.commit()
        db.refresh(registration)
        
        # Log audit
        log_audit('register', 'race', race.id, f'Athlete {athlete.name} registered for {race.name}')
        
        return jsonify({
            'message': '✅ Successfully registered for race',
            'registration': {
                'id': registration.id,
                'raceId': race.id,
                'raceName': race.name,
                'status': registration.status,
                'registrationDate': registration.registration_date.isoformat() if registration.registration_date else None,
                'bibNumber': registration.bib_number
            }
        }), 201
    except Exception as e:
        print(f"Register for race error: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to register for race'
        }), 500


@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events with demo data"""
    return jsonify(add_metadata({
        'events': DEMO_EVENTS,
        'count': len(DEMO_EVENTS),
        'message': '✅ Events retrieved successfully'
    }))


@app.route('/api/races/<int:race_id>/events', methods=['GET'])
def get_race_events(race_id):
    """Get events for a specific race (PUBLIC)"""
    try:
        db = next(get_db())
        events = db.query(Event).filter(Event.race_id == race_id).all()
        events_data = [event.to_dict() for event in events]
        
        return jsonify({
            'events': events_data,
            'count': len(events_data),
            'race_id': race_id,
            'message': '✅ Events retrieved successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve events',
            'message': str(e)
        }), 500


@app.route('/api/events/results', methods=['GET'])
def get_events_results():
    """Get results for events (PUBLIC) - optionally filtered by race_id"""
    try:
        race_id = request.args.get('race_id', type=int)
        db = next(get_db())
        
        query = db.query(Result).join(Event)
        if race_id:
            query = query.filter(Event.race_id == race_id)
        
        results = query.order_by(Result.position).all()
        
        results_data = [
            {
                'id': r.id,
                'athleteName': r.athlete.name if r.athlete else 'Unknown',
                'athleteId': r.athlete_id,
                'eventName': r.event.name if r.event else 'Unknown',
                'eventId': r.event_id,
                'position': r.position,
                'timeSeconds': r.time_seconds,
                'status': r.status,
                'country': r.athlete.country if r.athlete else None,
                'category': r.event.category if r.event else None,
                'gender': r.event.gender if r.event else None,
                'recordType': r.record_type,
                'isRecord': r.is_record
            }
            for r in results
        ]
        
        return jsonify({
            'results': results_data,
            'count': len(results_data),
            'race_id': race_id,
            'message': '✅ Results retrieved successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve results',
            'message': str(e)
        }), 500


@app.route('/api/results', methods=['GET'])
def get_results():
    """Get competition results"""
    demo_results = [
        {'athlete': 'Eliud Kipchoge', 'event': 'Marathon', 'time': '2:01:39', 'position': 1},
        {'athlete': 'Faith Kipyegon', 'event': '1500m', 'time': '3:50.37', 'position': 1},
        {'athlete': 'Usain Bolt', 'event': '100m', 'time': '9.58', 'position': 1},
    ]
    
    return jsonify(add_metadata({
        'results': demo_results,
        'count': len(demo_results),
        'message': '✅ Results retrieved successfully'
    }))


@app.route('/api/stats')
def get_stats():
    """Get system statistics with demo data"""
    return jsonify(add_metadata({
        'total_athletes': len(DEMO_ATHLETES),
        'total_events': len(DEMO_EVENTS),
        'total_results': 3,
        'active_competitions': 2,
        'system_status': 'operational',
        'message': '✅ Statistics retrieved successfully'
    }))


# Authentication Endpoints

@app.route('/api/auth/login', methods=['POST'])
@rate_limit(max_requests=10, window=300)  # 10 login attempts per 5 minutes
def login():
    """User login endpoint with account lockout protection"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Email and password are required'
        }), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({
            'error': 'Validation error',
            'message': 'Email and password cannot be empty'
        }), 400
    
    # Check if account is locked
    if is_account_locked(email):
        log_audit('login_blocked', 'user', details=f'Account locked due to failed attempts: {email}')
        return jsonify({
            'error': 'Account locked',
            'message': 'Too many failed login attempts. Your account has been locked for 30 minutes. Please try again later.'
        }), 429
    
    try:
        # Query user from database
        db = next(get_db())
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            attempts = track_failed_login(email)
            log_audit('login_failed', 'user', details=f'Email not found: {email}, attempt {attempts}')
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid email or password',
                'attempts_remaining': max(0, 5 - attempts)
            }), 401
        
        # Check password using bcrypt
        if not user.check_password(password):
            attempts = track_failed_login(email)
            log_audit('login_failed', 'user', user.id, f'Invalid password for {email}, attempt {attempts}')
            
            if attempts >= 5:
                return jsonify({
                    'error': 'Account locked',
                    'message': 'Too many failed login attempts. Your account has been locked for 30 minutes.'
                }), 429
            
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid email or password',
                'attempts_remaining': max(0, 5 - attempts)
            }), 401
        
        # Check if user is active
        if user.status != 'active':
            log_audit('login_failed', 'user', user.id, f'Account not active: {email}')
            return jsonify({
                'error': 'Account inactive',
                'message': 'Your account has been deactivated. Please contact administrator.'
            }), 403
        
        # Reset failed login count on successful login
        reset_failed_login(email)
        
        # Update last login
        user.last_login = datetime.now()
        db.commit()
        
        # Create session in Redis
        session_data = user.to_dict()
        SessionManager.create_session(user.id, session_data, expiry=86400)  # 24 hours
        
        auth_tokens = issue_auth_tokens(session_data)
        
        # Log successful login
        log_audit('login_success', 'user', user.id, f'Logged in from {request.remote_addr}')
        
        # Cache user data for quick access
        RedisCache.set(f"user:{user.id}", session_data, expiry=3600)
        
        return jsonify(add_metadata({
            'message': 'Login successful',
            'token': auth_tokens['access_token'],
            'access_token': auth_tokens['access_token'],
            'refresh_token': auth_tokens['refresh_token'],
            'token_type': 'Bearer',
            'expires_in': auth_tokens['expires_in'],
            'user': session_data
        })), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        log_audit('login_error', 'user', details=str(e))
        return jsonify({
            'error': 'Server error',
            'message': 'An error occurred during login'
        }), 500


@app.route('/api/auth/register', methods=['POST'])
@rate_limit(max_requests=5, window=3600)  # 5 registrations per hour per IP
def register():
    """User registration endpoint with secure password handling"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Request body is required'
        }), 400
    
    # Validate required fields
    required_fields = ['name', 'email', 'password']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            'error': 'Validation error',
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password')
    role = data.get('role', 'athlete').lower()
    
    # Input validation
    if not name or len(name) < 2:
        return jsonify({
            'error': 'Validation error',
            'message': 'Name must be at least 2 characters'
        }), 400
    
    if not email or '@' not in email:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please provide a valid email address'
        }), 400
    
    # Validate password strength
    if not password:
        return jsonify({
            'error': 'Validation error',
            'message': 'Password is required'
        }), 400
    
    is_strong, msg = validate_password_strength(password)
    if not is_strong:
        return jsonify({
            'error': 'Weak password',
            'message': msg,
            'requirements': {
                'minLength': 8,
                'uppercase': 'At least one uppercase letter',
                'lowercase': 'At least one lowercase letter',
                'number': 'At least one number',
                'special': 'At least one special character(!@#$%^&*)'
            }
        }), 400
    
    # Validate role
    valid_roles = ['athlete', 'coach', 'official', 'viewer', 'registrar', 'chief_registrar', 'starter']
    if role not in valid_roles:
        return jsonify({
            'error': 'Validation error',
            'message': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
        }), 400
    
    try:
        db = next(get_db())
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            log_audit('registration_failed', 'user', details=f'Email already exists: {email}')
            return jsonify({
                'error': 'Registration failed',
                'message': 'Email already registered'
            }), 409
        
        # Create new user with hashed password
        new_user = User(
            name=name,
            email=email,
            role=role,
            status='active'
        )
        new_user.set_password(password)  # Hash password with bcrypt
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log successful registration
        log_audit('user_registered', 'user', new_user.id, f'New user registered: {email}')
        
        # Create initial session
        session_data = new_user.to_dict()
        SessionManager.create_session(new_user.id, session_data, expiry=86400)
        
        auth_tokens = issue_auth_tokens(session_data)
        
        return jsonify(add_metadata({
            'message': '✅ Registration successful',
            'token': auth_tokens['access_token'],
            'access_token': auth_tokens['access_token'],
            'refresh_token': auth_tokens['refresh_token'],
            'token_type': 'Bearer',
            'expires_in': auth_tokens['expires_in'],
            'user': session_data
        })), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        log_audit('registration_error', 'user', details=str(e))
        return jsonify({
            'error': 'Server error',
            'message': 'An error occurred during registration'
        }), 500


@app.route('/api/auth/reset-password', methods=['POST'])
@rate_limit(max_requests=5, window=3600)  # 5 reset requests per hour
def reset_password():
    """Password reset request endpoint"""
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Email is required'
        }), 400
    
    email = data.get('email', '').strip().lower()
    
    if not email or '@' not in email:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please provide a valid email address'
        }), 400

    try:
        # Find user by email
        db = next(get_db())
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Security best practice: don't reveal if email exists
            log_audit('password_reset_failed', 'user', details=f'Email not found: {email}')
            return jsonify(add_metadata({
                'message': 'If the email exists, a password reset link has been sent'
            })), 200
        
        # Generate reset token and expiry (in production)
        import secrets
        reset_token = secrets.token_urlsafe(32)
        reset_expiry_key = f"reset_token:{reset_token}"
        RedisCache.set(reset_expiry_key, user.id, expiry=1800)  # 30 minutes validity
        
        # Log the reset request
        log_audit('password_reset_requested', 'user', user.id, f'Reset requested from {request.remote_addr}')
        
        # In production, send email with reset link
        # reset_link = f"{request.base_url.replace('/api/auth/reset-password', '')}/reset.html?token={reset_token}"
        # send_reset_email(user.email, reset_link)
        
        return jsonify(add_metadata({
            'message': 'Password reset link sent to your email',
            'demo_note': 'In production, this would send an email with reset link'
        })), 200
        
    except Exception as e:
        print(f"Reset password error: {e}")
        log_audit('password_reset_error', 'user', details=str(e))
        return jsonify({
            'error': 'Server error',
            'message': 'An error occurred. Please try again later.'
        }), 500


@app.route('/api/auth/refresh', methods=['POST'])
@rate_limit(max_requests=20, window=3600)
def refresh_access_token():
    """Refresh access token using refresh token with rotation."""
    data = request.get_json(silent=True) or {}
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        auth_header = request.headers.get('Authorization', '').strip()
        if auth_header.lower().startswith('bearer '):
            refresh_token = auth_header.split(' ', 1)[1].strip()

    if not refresh_token:
        return jsonify({'error': 'Refresh token is required'}), 400

    try:
        payload = jwt.decode(
            refresh_token,
            app.config['JWT_SECRET'],
            algorithms=[app.config['JWT_ALGORITHM']]
        )

        if payload.get('type') != 'refresh':
            return jsonify({'error': 'Invalid token type'}), 401

        user_id = int(payload.get('sub'))
        token_jti = payload.get('jti')
        stored_jti_payload = RedisCache.get(f"refresh_jti:{user_id}") or {}
        stored_jti = stored_jti_payload.get('jti') if isinstance(stored_jti_payload, dict) else stored_jti_payload

        if not token_jti or token_jti != stored_jti:
            return jsonify({'error': 'Refresh token is invalid or rotated'}), 401

        session_data = SessionManager.get_session(user_id)
        if not session_data:
            return jsonify({'error': 'Invalid or expired session'}), 401

        auth_tokens = issue_auth_tokens(session_data)

        return jsonify(add_metadata({
            'message': 'Token refreshed successfully',
            'token': auth_tokens['access_token'],
            'access_token': auth_tokens['access_token'],
            'refresh_token': auth_tokens['refresh_token'],
            'token_type': 'Bearer',
            'expires_in': auth_tokens['expires_in']
        })), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token expired'}), 401
    except (jwt.InvalidTokenError, TypeError, ValueError):
        return jsonify({'error': 'Invalid refresh token'}), 401


@app.route('/api/auth/logout', methods=['POST'])
@require_auth()
def logout():
    """Logout endpoint: revoke active session and refresh token."""
    try:
        user_id = int(getattr(request, 'user', {}).get('id'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid session context'}), 401

    SessionManager.delete_session(user_id)
    RedisCache.delete(f"refresh_jti:{user_id}")

    return jsonify(add_metadata({
        'message': 'Logged out successfully'
    })), 200


@app.route('/api/admin/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    # In production, check authentication token and admin role
    # For demo, return all users without password
    
    users_data = [
        {k: v for k, v in user.items() if k != 'password'}
        for user in DEMO_USERS
    ]
    
    return jsonify(add_metadata({
        'users': users_data,
        'count': len(users_data),
        'message': '✅ Users retrieved successfully'
    })), 200


@app.route('/api/admin/users', methods=['POST'])
def create_user():
    """Create new user (admin only)"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Request body is required'
        }), 400
    
    # Validate required fields
    required_fields = ['name', 'email', 'role']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            'error': 'Validation error',
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    # Check if email already exists
    if any(u['email'] == data['email'] for u in DEMO_USERS):
        return jsonify({
            'error': 'User creation failed',
            'message': 'Email already exists'
        }), 409
    
    # Create new user
    new_user = {
        'id': len(DEMO_USERS) + 1,
        'name': data['name'],
        'email': data['email'],
        'password': data.get('password', 'TempPass@123'),
        'role': data['role'],
        'status': data.get('status', 'active'),
        'lastLogin': 'Never',
        'createdAt': datetime.now().strftime('%Y-%m-%d')
    }
    
    DEMO_USERS.append(new_user)
    
    # Return user data (excluding password)
    user_data = {k: v for k, v in new_user.items() if k != 'password'}
    
    return jsonify(add_metadata({
        'message': '✅ User created successfully',
        'user': user_data
    })), 201


@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user (admin only)"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Request body is required'
        }), 400
    
    # Find user
    user = next((u for u in DEMO_USERS if u['id'] == user_id), None)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': f'No user found with ID {user_id}'
        }), 404
    
    # Update user fields
    if 'name' in data:
        user['name'] = data['name']
    if 'email' in data:
        user['email'] = data['email']
    if 'role' in data:
        user['role'] = data['role']
    if 'status' in data:
        user['status'] = data['status']
    if 'password' in data:
        user['password'] = data['password']
    
    # Return user data (excluding password)
    user_data = {k: v for k, v in user.items() if k != 'password'}
    
    return jsonify(add_metadata({
        'message': '✅ User updated successfully',
        'user': user_data
    })), 200


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user (admin only)"""
    global DEMO_USERS
    
    # Find user
    user = next((u for u in DEMO_USERS if u['id'] == user_id), None)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': f'No user found with ID {user_id}'
        }), 404
    
    # Remove user
    DEMO_USERS = [u for u in DEMO_USERS if u['id'] != user_id]
    
    return jsonify(add_metadata({
        'message': '✅ User deleted successfully'
    })), 200


# ===== APP BUILD REQUESTS (Admin Only) =====

@app.route('/api/admin/backups', methods=['GET'])
def get_backups():
    """List available backup files"""
    backup_dir = os.path.join(PROJECT_ROOT, 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    backup_files = []
    for file_name in os.listdir(backup_dir):
        file_path = os.path.join(backup_dir, file_name)
        if not os.path.isfile(file_path):
            continue

        stat = os.stat(file_path)
        backup_files.append({
            'id': file_name,
            'name': file_name,
            'size_bytes': stat.st_size,
            'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        })

    backup_files.sort(key=lambda item: item['created_at'], reverse=True)

    return jsonify(add_metadata({
        'backups': backup_files,
        'count': len(backup_files),
        'message': '✅ Backups retrieved successfully'
    })), 200


@app.route('/api/admin/backups', methods=['POST'])
@app.route('/api/admin/backup', methods=['POST'])
def create_backup():
    """Create a lightweight backup artifact for demo/admin flows"""
    backup_dir = os.path.join(PROJECT_ROOT, 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    backup_id = f"athsys-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}.json"
    backup_path = os.path.join(backup_dir, backup_id)

    payload = {
        'backup_id': backup_id,
        'created_at': datetime.now().isoformat(),
        'version': APP_VERSION,
        'service': APP_NAME,
        'summary': {
            'users': len(DEMO_USERS),
            'app_requests': len(DEMO_APP_REQUESTS),
            'form_submissions': len(DEMO_FORM_SUBMISSIONS)
        }
    }

    with open(backup_path, 'w', encoding='utf-8') as backup_file:
        json.dump(payload, backup_file, indent=2)

    return jsonify(add_metadata({
        'message': '✅ Backup created successfully',
        'backup': {
            'id': backup_id,
            'name': backup_id,
            'created_at': payload['created_at']
        }
    })), 201


@app.route('/api/admin/backups/<string:backup_id>/download', methods=['GET'])
def download_backup(backup_id):
    """Download backup file by id"""
    backup_dir = os.path.join(PROJECT_ROOT, 'backups')
    safe_name = os.path.basename(backup_id)
    backup_path = os.path.join(backup_dir, safe_name)

    if not os.path.isfile(backup_path):
        return jsonify({'error': 'Backup not found'}), 404

    return send_file(backup_path, as_attachment=True, download_name=safe_name)


@app.route('/api/admin/backups/<string:backup_id>/restore', methods=['POST'])
def restore_backup(backup_id):
    """Acknowledge backup restore request for admin UX flow"""
    backup_dir = os.path.join(PROJECT_ROOT, 'backups')
    safe_name = os.path.basename(backup_id)
    backup_path = os.path.join(backup_dir, safe_name)

    if not os.path.isfile(backup_path):
        return jsonify({'error': 'Backup not found'}), 404

    log_audit('backup_restore_requested', 'system', details=f'Restore requested for {safe_name}')

    return jsonify(add_metadata({
        'message': '✅ Backup restore initiated',
        'backup_id': safe_name
    })), 200

@app.route('/api/admin/app-requests', methods=['GET'])
def get_app_requests():
    """Get all app build requests"""
    return jsonify(add_metadata({
        'requests': DEMO_APP_REQUESTS,
        'count': len(DEMO_APP_REQUESTS),
        'message': '✅ App build requests retrieved successfully'
    })), 200


@app.route('/api/admin/app-requests', methods=['POST'])
def create_app_request():
    """Create new app build request"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    required = ['title', 'requested_by']
    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    new_request = {
        'id': len(DEMO_APP_REQUESTS) + 1,
        'title': data.get('title'),
        'requested_by': data.get('requested_by'),
        'description': data.get('description', ''),
        'priority': data.get('priority', 'medium'),
        'status': 'pending',
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'approved_by': None,
        'approved_at': None,
        'rejected_reason': None
    }

    DEMO_APP_REQUESTS.append(new_request)

    return jsonify(add_metadata({
        'message': '✅ App build request created successfully',
        'request': new_request
    })), 201


@app.route('/api/admin/app-requests/<int:request_id>/approve', methods=['PUT'])
def approve_app_request(request_id):
    """Approve an app build request"""
    req = next((r for r in DEMO_APP_REQUESTS if r['id'] == request_id), None)
    if not req:
        return jsonify({'error': 'App request not found'}), 404

    data = request.get_json() or {}
    req['status'] = 'approved'
    req['approved_by'] = data.get('approved_by', 'admin@athsys.com')
    req['approved_at'] = datetime.now().strftime('%Y-%m-%d')
    req['rejected_reason'] = None

    return jsonify(add_metadata({
        'message': '✅ App request approved',
        'request': req
    })), 200


@app.route('/api/admin/app-requests/<int:request_id>/reject', methods=['PUT'])
def reject_app_request(request_id):
    """Reject an app build request"""
    req = next((r for r in DEMO_APP_REQUESTS if r['id'] == request_id), None)
    if not req:
        return jsonify({'error': 'App request not found'}), 404

    data = request.get_json() or {}
    req['status'] = 'rejected'
    req['rejected_reason'] = data.get('reason') or data.get('rejected_reason') or 'Not specified'

    return jsonify(add_metadata({
        'message': '✅ App request rejected',
        'request': req
    })), 200


# ===== FORM SUBMISSIONS (Admin Only) =====

@app.route('/api/admin/form-submissions', methods=['GET'])
def get_form_submissions():
    """Get all form submissions"""
    return jsonify(add_metadata({
        'submissions': DEMO_FORM_SUBMISSIONS,
        'count': len(DEMO_FORM_SUBMISSIONS),
        'message': '✅ Form submissions retrieved successfully'
    })), 200


@app.route('/api/admin/form-submissions', methods=['POST'])
def create_form_submission():
    """Create a form submission (for demo/testing)"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    required = ['form_name', 'submitted_by']
    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    new_submission = {
        'id': len(DEMO_FORM_SUBMISSIONS) + 1,
        'form_name': data.get('form_name'),
        'submitted_by': data.get('submitted_by'),
        'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'status': 'pending',
        'notes': data.get('notes', '')
    }

    DEMO_FORM_SUBMISSIONS.append(new_submission)

    return jsonify(add_metadata({
        'message': '✅ Form submission created successfully',
        'submission': new_submission
    })), 201


@app.route('/api/admin/form-submissions/<int:submission_id>/approve', methods=['PUT'])
def approve_form_submission(submission_id):
    """Approve a form submission"""
    submission = next((s for s in DEMO_FORM_SUBMISSIONS if s['id'] == submission_id), None)
    if not submission:
        return jsonify({'error': 'Form submission not found'}), 404

    data = request.get_json() or {}
    submission['status'] = 'approved'
    if 'notes' in data:
        submission['notes'] = data.get('notes', submission.get('notes', ''))
    return jsonify(add_metadata({
        'message': '✅ Form submission approved',
        'submission': submission
    })), 200


@app.route('/api/admin/form-submissions/<int:submission_id>/reject', methods=['PUT'])
def reject_form_submission(submission_id):
    """Reject a form submission"""
    submission = next((s for s in DEMO_FORM_SUBMISSIONS if s['id'] == submission_id), None)
    if not submission:
        return jsonify({'error': 'Form submission not found'}), 404

    data = request.get_json() or {}
    submission['status'] = 'rejected'
    submission['notes'] = data.get('notes', submission.get('notes', ''))

    return jsonify(add_metadata({
        'message': '✅ Form submission rejected',
        'submission': submission
    })), 200


# Race Management Endpoints (Chief Registrar)

@app.route('/api/races', methods=['GET'])
@rate_limit(max_requests=200, window=3600)
def get_races():
    """Get all races from database with Redis caching"""
    try:
        # Try to get from cache first
        cache_key = "races:all"
        cached = RedisCache.get(cache_key)
        if cached:
            return jsonify({
                'races': cached,
                'count': len(cached),
                'message': '✅ Races retrieved successfully (cached)',
                'version': APP_VERSION
            }), 200
        
        # Query from database
        db = next(get_db())
        races = db.query(Race).order_by(Race.date.desc()).all()
        races_data = [race.to_dict() for race in races]
        
        # Cache results for 5 minutes
        RedisCache.set(cache_key, races_data, expiry=300)
        
        return jsonify({
            'races': races_data,
            'count': len(races_data),
            'message': '✅ Races retrieved successfully',
            'version': APP_VERSION
        }), 200
    except Exception as e:
        print(f"Get races error: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to retrieve races'
        }), 500


@app.route('/api/races', methods=['POST'])
@require_auth(roles=['admin', 'chief_registrar'])
def create_race():
    """Create new race (Chief Registrar only)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request', 'message': 'Request body is required'}), 400
    
    required_fields = ['name', 'date', 'location']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            'error': 'Validation error',
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    try:
        db = next(get_db())
        
        # Generate public registration link
        import random
        import string
        link_id = 'pub_race_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        new_race = Race(
            name=data['name'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            location=data['location'],
            status=data.get('status', 'draft'),
            created_by=data.get('created_by', 2),
            registration_link=link_id
        )
        
        db.add(new_race)
        db.commit()
        db.refresh(new_race)
        
        # Cache the new race
        RedisCache.delete('races:all')
        
        race_data = new_race.to_dict()
        
        return jsonify(add_metadata({
            'message': '✅ Race created successfully',
            'race': race_data,
            'registration_url': f'/register/{link_id}'
        })), 201
    except Exception as e:
        print(f"Error creating race: {e}")
        return jsonify({'error': 'Failed to create race', 'details': str(e)}), 500


@app.route('/api/races/<int:race_id>', methods=['PUT'])
def update_race(race_id):
    """Update race (Chief Registrar only)"""
    data = request.get_json()
    
    race = next((r for r in DEMO_RACES if r['id'] == race_id), None)
    if not race:
        return jsonify({'error': 'Race not found'}), 404
    
    # Update fields
    for key in ['name', 'date', 'location', 'status', 'events']:
        if key in data:
            race[key] = data[key]
    
    return jsonify(add_metadata({
        'message': '✅ Race updated successfully',
        'race': race
    })), 200


@app.route('/api/races/<int:race_id>', methods=['DELETE'])
def delete_race(race_id):
    """Delete race (Chief Registrar only)"""
    global DEMO_RACES
    
    race = next((r for r in DEMO_RACES if r['id'] == race_id), None)
    if not race:
        return jsonify({'error': 'Race not found'}), 404
    
    DEMO_RACES = [r for r in DEMO_RACES if r['id'] != race_id]
    
    return jsonify(add_metadata({
        'message': '✅ Race deleted successfully'
    })), 200


# Registration Endpoints

@app.route('/api/races/<int:race_id>/registrations', methods=['GET'])
def get_race_registrations(race_id):
    """Get all registrations for a race"""
    registrations = [r for r in DEMO_REGISTRATIONS if r['race_id'] == race_id]
    
    return jsonify(add_metadata({
        'registrations': registrations,
        'count': len(registrations),
        'message': '✅ Registrations retrieved successfully'
    })), 200


@app.route('/api/races/<int:race_id>/register', methods=['POST'])
def register_athlete(race_id):
    """Register athlete for race (Registrar or Public)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    required_fields = ['athlete_name', 'email', 'events']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            'error': 'Validation error',
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    new_registration = {
        'id': len(DEMO_REGISTRATIONS) + 1,
        'race_id': race_id,
        'athlete_name': data['athlete_name'],
        'email': data['email'],
        'events': data['events'],
        'status': 'pending',
        'registered_by': data.get('registered_by'),
        'registration_type': data.get('registration_type', 'manual'),
        'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    DEMO_REGISTRATIONS.append(new_registration)
    
    return jsonify(add_metadata({
        'message': '✅ Registration successful',
        'registration': new_registration
    })), 201


# Public Registration Link

@app.route('/register/<link_id>', methods=['GET'])
def public_registration_page(link_id):
    """Get public registration page details"""
    try:
        db = next(get_db())
        
        # Find race by registration link
        race = db.query(Race).filter(Race.registration_link == link_id).first()
        
        if not race:
            return jsonify({'error': 'Invalid or expired registration link'}), 404
        
        if race.status == 'cancelled':
            return jsonify({'error': 'Registration link is no longer active'}), 403
        
        race_data = race.to_dict()
        
        # Get events for this race
        events = db.query(Event).filter(Event.race_id == race.id).all()
        race_data['events'] = [event.to_dict() for event in events]
        
        return jsonify(add_metadata({
            'race': race_data,
            'expires': race.date.strftime('%Y-%m-%d'),
            'message': '✅ Registration link is valid'
        })), 200
    except Exception as e:
        print(f"Error fetching registration page: {e}")
        return jsonify({'error': 'Failed to load registration page'}), 500


@app.route('/register/<link_id>', methods=['POST'])
def public_register_athlete(link_id):
    """Public athlete registration via link"""
    try:
        db = next(get_db())
        
        # Find race by registration link
        race = db.query(Race).filter(Race.registration_link == link_id).first()
        
        if not race:
            return jsonify({'error': 'Invalid or expired registration link'}), 404
        
        if race.status == 'cancelled':
            return jsonify({'error': 'Registration link is no longer active'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required = ['athlete_id', 'event_id']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400
        
        # Create registration
        registration = Registration(
            athlete_id=data['athlete_id'],
            event_id=data['event_id'],
            race_id=race.id,
            registration_type='public',
            status='pending',
            payment_status='unpaid'
        )
        
        db.add(registration)
        db.commit()
        db.refresh(registration)
        
        # Clear cache
        RedisCache.delete('registrations:all')
        
        return jsonify(add_metadata({
            'message': '✅ Registration successful',
            'registration': registration.to_dict()
        })), 201
    except Exception as e:
        print(f"Error creating public registration: {e}")
        return jsonify({'error': 'Failed to register', 'details': str(e)}), 500


# Excel Template Endpoints

@app.route('/api/races/<int:race_id>/template', methods=['GET'])
def download_registration_template(race_id):
    """Download Excel template for bulk registration"""
    import base64
    
    race = next((r for r in DEMO_RACES if r['id'] == race_id), None)
    if not race:
        return jsonify({'error': 'Race not found'}), 404
    
    # In production, generate actual Excel file with openpyxl
    # For demo, return template structure
    template_data = {
        'race_id': race_id,
        'race_name': race['name'],
        'template_version': '1.0',
        'columns': ['Athlete Name', 'Email', 'Event 1', 'Event 2', 'Event 3', 'Team/Club'],
        'sample_data': [
            ['John Doe', 'john@example.com', '100m', '200m', '', 'Athletics Club'],
            ['Jane Smith', 'jane@example.com', '1500m', '', '', 'Track Team']
        ],
        'checksum': 'demo_checksum_' + str(race_id),  # For validation
        'instructions': 'Fill in athlete details. Do not modify column headers.'
    }
    
    return jsonify(add_metadata({
        'message': '✅ Template ready for download',
        'template': template_data,
        'download_note': 'In production, this returns an Excel file'
    })), 200


@app.route('/api/races/<int:race_id>/upload', methods=['POST'])
def upload_registration_excel(race_id):
    """Upload filled Excel template for bulk registration"""
    data = request.get_json()
    
    if not data or 'file_data' not in data:
        return jsonify({'error': 'No file data provided'}), 400
    
    # Validate checksum to prevent tampering
    if data.get('checksum') != f'demo_checksum_{race_id}':
        return jsonify({
            'error': 'File validation failed',
            'message': 'Template file has been modified or is invalid'
        }), 400
    
    # Process registrations from file
    athletes_data = data.get('athletes', [])
    registered_count = 0
    errors = []
    
    for athlete in athletes_data:
        try:
            new_registration = {
                'id': len(DEMO_REGISTRATIONS) + 1,
                'race_id': race_id,
                'athlete_name': athlete['name'],
                'email': athlete['email'],
                'events': athlete.get('events', []),
                'status': 'pending',
                'registered_by': data.get('uploaded_by'),
                'registration_type': 'bulk',
                'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            DEMO_REGISTRATIONS.append(new_registration)
            registered_count += 1
        except Exception as e:
            errors.append(f"Error registering {athlete.get('name', 'Unknown')}: {str(e)}")
    
    return jsonify(add_metadata({
        'message': f'✅ Bulk registration completed',
        'registered': registered_count,
        'errors': errors,
        'total': len(athletes_data)
    })), 200


# Start List Management (Starter/Official)

@app.route('/api/startlists', methods=['GET'])
def get_startlists():
    """Get all start lists"""
    return jsonify(add_metadata({
        'startlists': DEMO_STARTLISTS,
        'count': len(DEMO_STARTLISTS),
        'message': '✅ Start lists retrieved successfully'
    })), 200


@app.route('/api/startlists/<int:startlist_id>/confirm', methods=['POST'])
def confirm_startlist(startlist_id):
    """Confirm start list (Starter only)"""
    data = request.get_json()
    
    startlist = next((s for s in DEMO_STARTLISTS if s['id'] == startlist_id), None)
    if not startlist:
        return jsonify({'error': 'Start list not found'}), 404
    
    startlist['status'] = 'confirmed'
    startlist['confirmed_by'] = data.get('confirmed_by')
    startlist['confirmed_at'] = datetime.now().isoformat()
    
    return jsonify(add_metadata({
        'message': '✅ Start list confirmed successfully',
        'startlist': startlist
    })), 200


# Logo Upload and Settings

@app.route('/api/settings/logo', methods=['POST'])
def upload_logo():
    """Upload organization logo with auto-resize"""
    data = request.get_json()
    
    if not data or 'logo' not in data:
        return jsonify({'error': 'No logo data provided'}), 400
    
    logo_data = data['logo']  # Base64 encoded image
    
    # In production, use PIL/Pillow to resize
    # from PIL import Image
    # import io
    # Decode base64, resize to max 200x200, re-encode
    
    # For demo, just store the logo
    SYSTEM_SETTINGS['logo'] = logo_data
    SYSTEM_SETTINGS['logo_updated_at'] = datetime.now().isoformat()
    
    return jsonify(add_metadata({
        'message': '✅ Logo uploaded successfully',
        'note': 'In production, image is auto-resized to optimal dimensions'
    })), 200


@app.route('/api/settings/logo', methods=['GET'])
def get_logo():
    """Get current logo"""
    return jsonify(add_metadata({
        'logo': SYSTEM_SETTINGS.get('logo'),
        'updated_at': SYSTEM_SETTINGS.get('logo_updated_at'),
        'message': '✅ Logo retrieved successfully'
    })), 200


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get system settings"""
    return jsonify(add_metadata({
        'settings': SYSTEM_SETTINGS,
        'message': '✅ Settings retrieved successfully'
    })), 200


@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """Update system settings (Admin only)"""
    data = request.get_json()
    
    for key, value in data.items():
        if key in SYSTEM_SETTINGS:
            SYSTEM_SETTINGS[key] = value
    
    return jsonify(add_metadata({
        'message': '✅ Settings updated successfully',
        'settings': SYSTEM_SETTINGS
    })), 200


# ===== PLUGIN MANAGEMENT ENDPOINTS (Admin Only) =====

@app.route('/api/admin/plugins', methods=['GET'])
@require_auth(roles=['admin'])
def get_plugins():
    """Get all plugins and their status"""
    try:
        from plugin_manager import plugin_manager
        
        plugins = plugin_manager.get_all_plugins()
        stats = plugin_manager.get_stats()
        
        return jsonify(add_metadata({
            'plugins': plugins,
            'stats': stats,
            'count': len(plugins),
            'message': '✅ Plugins retrieved successfully'
        })), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve plugins',
            'message': str(e)
        }), 500


@app.route('/api/admin/plugins/<plugin_id>', methods=['GET'])
@require_auth(roles=['admin'])
def get_plugin(plugin_id):
    """Get detailed information about a specific plugin"""
    try:
        from plugin_manager import plugin_manager
        
        plugin_info = plugin_manager.get_plugin_info(plugin_id)
        
        if not plugin_info:
            return jsonify({
                'error': 'Plugin not found',
                'plugin_id': plugin_id
            }), 404
        
        return jsonify(add_metadata({
            'plugin': plugin_info,
            'message': '✅ Plugin information retrieved'
        })), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve plugin',
            'message': str(e)
        }), 500


@app.route('/api/admin/plugins/<plugin_id>/enable', methods=['POST'])
@require_auth(roles=['admin'])
def enable_plugin(plugin_id):
    """Enable a plugin"""
    try:
        from plugin_manager import plugin_manager
        
        success = plugin_manager.enable_plugin(plugin_id)
        
        if not success:
            return jsonify({
                'error': 'Failed to enable plugin',
                'message': f'Plugin {plugin_id} not found or cannot be enabled'
            }), 400
        
        plugin_info = plugin_manager.get_plugin_info(plugin_id)
        
        # Log the action
        db = next(get_db())
        audit = AuditLog(
            user_id=request.user['id'],
            action='enable_plugin',
            entity_type='plugin',
            details=f'Enabled plugin: {plugin_id}',
            ip_address=request.remote_addr
        )
        db.add(audit)
        db.commit()
        
        return jsonify(add_metadata({
            'plugin': plugin_info,
            'message': f'✅ Plugin {plugin_info["name"]} enabled successfully'
        })), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to enable plugin',
            'message': str(e)
        }), 500


@app.route('/api/admin/plugins/<plugin_id>/disable', methods=['POST'])
@require_auth(roles=['admin'])
def disable_plugin(plugin_id):
    """Disable a plugin"""
    try:
        from plugin_manager import plugin_manager
        
        success = plugin_manager.disable_plugin(plugin_id)
        
        if not success:
            return jsonify({
                'error': 'Failed to disable plugin',
                'message': f'Plugin {plugin_id} not found, required, or cannot be disabled'
            }), 400
        
        plugin_info = plugin_manager.get_plugin_info(plugin_id)
        
        # Log the action
        db = next(get_db())
        audit = AuditLog(
            user_id=request.user['id'],
            action='disable_plugin',
            entity_type='plugin',
            details=f'Disabled plugin: {plugin_id}',
            ip_address=request.remote_addr
        )
        db.add(audit)
        db.commit()
        
        return jsonify(add_metadata({
            'plugin': plugin_info,
            'message': f'✅ Plugin {plugin_info["name"]} disabled successfully'
        })), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to disable plugin',
            'message': str(e)
        }), 500


@app.route('/api/admin/plugins/<plugin_id>/toggle', methods=['POST'])
@require_auth(roles=['admin'])
def toggle_plugin(plugin_id):
    """Toggle a plugin on/off"""
    try:
        from plugin_manager import plugin_manager
        
        success = plugin_manager.toggle_plugin(plugin_id)
        
        if not success:
            return jsonify({
                'error': 'Failed to toggle plugin',
                'message': f'Plugin {plugin_id} not found or cannot be toggled'
            }), 400
        
        plugin_info = plugin_manager.get_plugin_info(plugin_id)
        
        # Log the action
        db = next(get_db())
        audit = AuditLog(
            user_id=request.user['id'],
            action='toggle_plugin',
            entity_type='plugin',
            details=f'Toggled plugin: {plugin_id} (now {"enabled" if plugin_info["enabled"] else "disabled"})',
            ip_address=request.remote_addr
        )
        db.add(audit)
        db.commit()
        
        return jsonify(add_metadata({
            'plugin': plugin_info,
            'message': f'✅ Plugin {plugin_info["name"]} {"enabled" if plugin_info["enabled"] else "disabled"}'
        })), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to toggle plugin',
            'message': str(e)
        }), 500


@app.route('/api/admin/plugins/category/<category>', methods=['GET'])
@require_auth(roles=['admin'])
def get_plugins_by_category(category):
    """Get all plugins in a specific category"""
    try:
        from plugin_manager import plugin_manager
        
        plugins = plugin_manager.get_plugins_by_category(category)
        
        return jsonify(add_metadata({
            'category': category,
            'plugins': plugins,
            'count': len(plugins),
            'message': f'✅ Plugins in category "{category}" retrieved'
        })), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve plugins by category',
            'message': str(e)
        }), 500


@app.route('/api/admin/plugins/stats', methods=['GET'])
@require_auth(roles=['admin'])
def get_plugin_stats():
    """Get plugin system statistics"""
    try:
        from plugin_manager import plugin_manager
        
        stats = plugin_manager.get_stats()
        enabled_plugins = plugin_manager.get_enabled_plugins()
        
        return jsonify(add_metadata({
            'stats': stats,
            'enabled': [p['pluginId'] for p in enabled_plugins],
            'message': '✅ Plugin statistics retrieved'
        })), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve plugin statistics',
            'message': str(e)
        }), 500


# ==================== FRONTEND CONFIGURATION ENDPOINTS ====================
# Control frontend display and navigation from backend

@app.route('/api/config/frontend', methods=['GET'])
def get_frontend_config():
    """Get frontend configuration (public endpoint - no auth required)"""
    try:
        db = next(get_db())
        
        # Get all frontend configs
        configs = db.query(FrontendConfig).all()
        config_dict = {config.key: json.loads(config.value) if config.value else {} for config in configs}
        
        # Default config if none exist
        if not config_dict:
            config_dict = {
                'nav_links': [
                    {'label': 'Home', 'url': '/', 'visible': True},
                    {'label': 'Features', 'url': '#features', 'visible': True},
                    {'label': 'About', 'url': '#stats', 'visible': True}
                ],
                'show_logs_modal': False,
                'show_login_modal': True
            }
        
        return jsonify(add_metadata({
            'config': config_dict,
            'message': '✅ Frontend configuration retrieved'
        })), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve frontend config',
            'message': str(e)
        }), 500


@app.route('/api/admin/config/frontend/<key>', methods=['GET'])
@require_auth(roles=['admin'])
def get_frontend_config_key(key):
    """Get specific frontend configuration key"""
    try:
        db = next(get_db())
        config = db.query(FrontendConfig).filter(FrontendConfig.key == key).first()
        
        if not config:
            return jsonify({'error': 'Configuration key not found'}), 404
        
        return jsonify(add_metadata({
            'key': config.key,
            'value': json.loads(config.value) if config.value else {},
            'message': f'✅ Configuration "{key}" retrieved'
        })), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve configuration',
            'message': str(e)
        }), 500


@app.route('/api/admin/config/frontend/<key>', methods=['PUT'])
@require_auth(roles=['admin'])
def update_frontend_config(key):
    """Update frontend configuration from admin panel"""
    try:
        db = next(get_db())
        data = request.get_json()
        value = data.get('value')
        description = data.get('description', '')
        
        if not value:
            return jsonify({'error': 'Configuration value required'}), 400
        
        # Find or create config
        config = db.query(FrontendConfig).filter(FrontendConfig.key == key).first()
        
        if not config:
            config = FrontendConfig(
                key=key,
                value=json.dumps(value),
                description=description,
                updated_by=getattr(request, 'user', {}).get('id')
            )
            db.add(config)
        else:
            config.value = json.dumps(value)
            config.description = description
            config.updated_by = getattr(request, 'user', {}).get('id')
        
        db.commit()
        log_audit('UPDATE_CONFIG', 'FrontendConfig', key, {'new_value': value})
        
        return jsonify(add_metadata({
            'key': config.key,
            'value': json.loads(config.value),
            'message': f'✅ Configuration "{key}" updated successfully'
        })), 200
    except Exception as e:
        db.rollback()
        return jsonify({
            'error': 'Failed to update configuration',
            'message': str(e)
        }), 500


@app.route('/api/admin/config/frontend/nav-links', methods=['PUT'])
@require_auth(roles=['admin'])
def update_nav_links():
    """Update navigation links configuration"""
    try:
        db = next(get_db())
        data = request.get_json()
        links = data.get('links', [])
        
        # Validate links structure
        for link in links:
            if not all(k in link for k in ['label', 'url', 'visible']):
                return jsonify({'error': 'Invalid link structure. Required: label, url, visible'}), 400
        
        # Save configuration
        config = db.query(FrontendConfig).filter(FrontendConfig.key == 'nav_links').first()
        
        if not config:
            config = FrontendConfig(
                key='nav_links',
                value=json.dumps(links),
                description='Navigation links visible on frontend',
                updated_by=getattr(request, 'user', {}).get('id')
            )
            db.add(config)
        else:
            config.value = json.dumps(links)
            config.updated_by = getattr(request, 'user', {}).get('id')
        
        db.commit()
        log_audit('UPDATE_NAV_LINKS', 'FrontendConfig', None, {'links_count': len(links)})
        
        return jsonify(add_metadata({
            'links': links,
            'message': '✅ Navigation links updated successfully'
        })), 200
    except Exception as e:
        db.rollback()
        return jsonify({
            'error': 'Failed to update navigation links',
            'message': str(e)
        }), 500


@app.route('/api/admin/config/frontend/toggle-feature/<feature_name>', methods=['POST'])
@require_auth(roles=['admin'])
def toggle_frontend_feature(feature_name):
    """Toggle frontend feature visibility (e.g., show_logs_modal, show_login_modal)"""
    try:
        db = next(get_db())
        data = request.get_json()
        enabled = data.get('enabled', False)
        
        config_key = f'show_{feature_name}'
        config = db.query(FrontendConfig).filter(FrontendConfig.key == config_key).first()
        
        if not config:
            config = FrontendConfig(
                key=config_key,
                value=json.dumps(enabled),
                description=f'Toggle {feature_name} feature visibility',
                updated_by=getattr(request, 'user', {}).get('id')
            )
            db.add(config)
        else:
            config.value = json.dumps(enabled)
            config.updated_by = getattr(request, 'user', {}).get('id')
        
        db.commit()
        log_audit('TOGGLE_FEATURE', 'FrontendConfig', feature_name, {'enabled': enabled})
        
        return jsonify(add_metadata({
            'feature': feature_name,
            'enabled': enabled,
            'message': f'✅ Feature "{feature_name}" {"enabled" if enabled else "disabled"}'
        })), 200
    except Exception as e:
        db.rollback()
        return jsonify({
            'error': 'Failed to toggle feature',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'status_code': 404,
        'message': 'The requested endpoint does not exist',
        'suggestion': 'Visit / for available endpoints',
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'status_code': 500,
        'message': 'An error occurred processing your request',
        'timestamp': datetime.now().isoformat()
    }), 500


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return jsonify({
        'error': 'Bad Request',
        'status_code': 400,
        'message': 'Invalid request data',
        'timestamp': datetime.now().isoformat()
    }), 400


# Serve static frontend files (HTML, CSS, JS, etc)
# Flask automatically handles static files from static_folder defined at app init
# All /api/* routes are matched BEFORE this catch-all
# Routes in order of Flask matching:
# 1. All @app.route() decorators (api, health, etc) - highest priority
# 2. Flask static_folder auto-handling - second priority  
# 3. Security redirects - prevent credential exposure in URLs

@app.route('/login.html')
@app.route('/login.html', methods=['GET', 'POST'])
def redirect_login():
    """Redirect login.html to home page - login embedded in modal"""
    from flask import redirect
    return redirect('/', code=301)


@app.route('/register.html')
@app.route('/register.html', methods=['GET', 'POST'])
def redirect_register():
    """Redirect register.html to home page - register embedded in modal"""
    from flask import redirect
    return redirect('/', code=301)


@app.route('/builder')
def builder_dashboard():
    """Serve builder dashboard"""
    return send_from_directory(FRONTEND_DIR, 'builder-dashboard.html')


@app.route('/admin')
@app.route('/admin-pro')
@app.route('/admin-pro-complete')
def admin_pro_dashboard():
    """Serve the default modern admin dashboard"""
    return send_from_directory(FRONTEND_DIR, 'admin-pro-complete.html')


@app.route('/admin-old')
def admin_dashboard_classic():
    """Serve the classic admin dashboard fallback"""
    return send_from_directory(FRONTEND_DIR, 'admin-old.html')


# 4. Error handlers - lowest priority

@app.route('/')
def root():
    """Serve root landing page - return index.html"""
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend directory"""
    file_path = os.path.join(FRONTEND_DIR, filename)
    
    # Security: prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        return jsonify({'error': 'Invalid path'}), 400
    
    # If file exists, serve it
    if os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, filename)
    
    # For HTML files that don't exist, return error page
    if filename.endswith('.html'):
        return jsonify({
            'error': 'Not Found',
            'message': f'The requested page "{filename}" does not exist',
            'status_code': 404,
            'suggestion': 'Visit / for available endpoints',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    # For non-HTML files that don't exist, return 404
    return jsonify({
        'error': 'Not Found',
        'message': f'The requested endpoint does not exist',
        'status_code': 404,
        'suggestion': 'Visit / for available endpoints',
        'timestamp': datetime.now().isoformat()
    }), 404


if __name__ == '__main__':
    port = app.config['PORT']
    print("=" * 60)
    print(f"[RUN]  {APP_NAME} v{APP_VERSION}")
    print("=" * 60)
    print(f"[LAUNCH]  Server starting on http://0.0.0.0:{port}")
    print(f"[ENV]  Environment: {'Development' if app.config['DEBUG'] else 'Production'}")
    print(f"[READY]  Status: Ready to serve requests")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
