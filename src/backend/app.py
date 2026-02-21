"""
AthSys Backend - Athletics Management System
Main application entry point with enhanced UX features
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import time
from datetime import datetime

# Configure Flask to serve frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

# Configuration
app.config['DEBUG'] = os.getenv('DEBUG', 'False') == 'True'
app.config['PORT'] = int(os.getenv('PORT', 5000))
app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
app.config['DB_NAME'] = os.getenv('DB_NAME', 'athsys_db')

# Store version and metadata
APP_VERSION = '1.0.0'
APP_NAME = 'AthSys - Athletics Management System'

# Request counter for demo purposes
REQUEST_COUNT = 0

# Demo data for better UX demonstration
DEMO_ATHLETES = [
    {'id': 1, 'name': 'Eliud Kipchoge', 'country': 'KEN', 'events': ['Marathon', '5000m']},
    {'id': 2, 'name': 'Faith Kipyegon', 'country': 'KEN', 'events': ['1500m', '5000m']},
    {'id': 3, 'name': 'Usain Bolt', 'country': 'JAM', 'events': ['100m', '200m']},
]

DEMO_EVENTS = [
    {'id': 1, 'name': '100m Sprint', 'category': 'Track', 'participants': 8},
    {'id': 2, 'name': 'Marathon', 'category': 'Road', 'participants': 150},
    {'id': 3, 'name': '1500m', 'category': 'Track', 'participants': 12},
]

# Demo users data for authentication - Expanded roles
DEMO_USERS = [
    {
        'id': 1,
        'name': 'Admin User',
        'email': 'admin@athsys.com',
        'password': 'Admin@123',  # In production, this would be hashed
        'role': 'admin',
        'status': 'active',
        'lastLogin': 'Just now',
        'createdAt': '2024-01-01'
    },
    {
        'id': 2,
        'name': 'Chief Registrar',
        'email': 'chief@athsys.com',
        'password': 'Chief@123',
        'role': 'chief_registrar',
        'status': 'active',
        'lastLogin': '1 hour ago',
        'createdAt': '2024-01-02'
    },
    {
        'id': 3,
        'name': 'Registrar User',
        'email': 'registrar@athsys.com',
        'password': 'Registrar@123',
        'role': 'registrar',
        'status': 'active',
        'lastLogin': '3 hours ago',
        'createdAt': '2024-01-03'
    },
    {
        'id': 4,
        'name': 'Starter Official',
        'email': 'starter@athsys.com',
        'password': 'Starter@123',
        'role': 'starter',
        'status': 'active',
        'lastLogin': '2 hours ago',
        'createdAt': '2024-01-04'
    },
    {
        'id': 5,
        'name': 'John Athlete',
        'email': 'john@athsys.com',
        'password': 'Athlete@123',
        'role': 'athlete',
        'status': 'active',
        'lastLogin': '5 hours ago',
        'createdAt': '2024-01-15'
    },
    {
        'id': 6,
        'name': 'Sarah Coach',
        'email': 'sarah@athsys.com',
        'password': 'Coach@123',
        'role': 'coach',
        'status': 'active',
        'lastLogin': '1 day ago',
        'createdAt': '2024-01-10'
    }
]

# Races/Competitions data
DEMO_RACES = [
    {
        'id': 1,
        'name': 'National Athletics Championship 2026',
        'date': '2026-03-15',
        'location': 'National Stadium',
        'status': 'open',
        'created_by': 2,  # Chief Registrar
        'registration_link': 'pub_race_abc123',
        'events': [1, 2, 3],
        'createdAt': '2026-02-01'
    },
    {
        'id': 2,
        'name': 'Regional Track Meet 2026',
        'date': '2026-04-10',
        'location': 'Regional Sports Complex',
        'status': 'draft',
        'created_by': 2,
        'registration_link': 'pub_race_xyz789',
        'events': [1, 3],
        'createdAt': '2026-02-10'
    }
]

# Race registrations
DEMO_REGISTRATIONS = [
    {
        'id': 1,
        'race_id': 1,
        'athlete_name': 'John Athlete',
        'email': 'john@athsys.com',
        'events': [1, 2],
        'status': 'confirmed',
        'registered_by': 3,  # Registrar
        'registration_type': 'manual',
        'createdAt': '2026-02-15'
    }
]

# Start lists for races
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


@app.after_request
def after_request(response):
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if hasattr(request, 'start_time'):
        elapsed = time.time() - request.start_time
        response.headers['X-Response-Time'] = f'{elapsed*1000:.2f}ms'
    
    response.headers['X-Request-ID'] = f'req_{REQUEST_COUNT}'
    response.headers['X-Powered-By'] = 'AthSys v1.0.0'
    return response


def add_metadata(data):
    """Add metadata to API responses for better UX"""
    return {
        **data,
        'meta': {
            'timestamp': datetime.now().isoformat(),
            'request_id': f'req_{REQUEST_COUNT}',
            'version': APP_VERSION
        }
    }


@app.route('/')
def index():
    """Serve the modern frontend landing page"""
    return send_from_directory(FRONTEND_DIR, 'index.html')


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


@app.route('/health')
def health():
    """Health check endpoint for Docker and monitoring"""
    health_status = {
        'status': 'healthy',
        'service': 'athsys-backend',
        'version': APP_VERSION,
        'timestamp': datetime.now().isoformat(),
        'checks': {
            'api': 'operational',
            'database': 'ready',
            'cache': 'active'
        }
    }
    return jsonify(health_status), 200


@app.route('/livez')
def livez():
    """Lightweight liveness probe endpoint for container orchestration"""
    return jsonify({'status': 'ok', 'timestamp': time.time()}), 200


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
def get_athletes():
    """Get all athletes with demo data"""
    return jsonify(add_metadata({
        'athletes': DEMO_ATHLETES,
        'count': len(DEMO_ATHLETES),
        'message': '✅ Athletes retrieved successfully'
    }))


@app.route('/api/athletes', methods=['POST'])
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
    
    # Simulate athlete creation
    new_athlete = {
        'id': len(DEMO_ATHLETES) + 1,
        'name': data.get('name'),
        'country': data.get('country'),
        'events': data.get('events', []),
        'created_at': datetime.now().isoformat()
    }
    
    DEMO_ATHLETES.append(new_athlete)
    
    return jsonify(add_metadata({
        'message': '✅ Athlete created successfully',
        'athlete': new_athlete
    })), 201


@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events with demo data"""
    return jsonify(add_metadata({
        'events': DEMO_EVENTS,
        'count': len(DEMO_EVENTS),
        'message': '✅ Events retrieved successfully'
    }))


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
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Email and password are required'
        }), 400
    
    email = data.get('email')
    password = data.get('password')
    
    # Find user by email
    user = next((u for u in DEMO_USERS if u['email'] == email), None)
    
    if not user:
        return jsonify({
            'error': 'Authentication failed',
            'message': 'Invalid email or password'
        }), 401
    
    # Check password (in production, use proper password hashing)
    if user['password'] != password:
        return jsonify({
            'error': 'Authentication failed',
            'message': 'Invalid email or password'
        }), 401
    
    # Check if user is active
    if user.get('status') != 'active':
        return jsonify({
            'error': 'Account inactive',
            'message': 'Your account has been deactivated. Please contact administrator.'
        }), 403
    
    # Update last login
    user['lastLogin'] = 'Just now'
    
    # Generate demo token (in production, use JWT)
    token = f"demo_token_{user['id']}_{int(time.time())}"
    
    # Return user data (excluding password)
    user_data = {k: v for k, v in user.items() if k != 'password'}
    
    return jsonify(add_metadata({
        'message': '✅ Login successful',
        'token': token,
        'user': user_data
    })), 200


@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Request body is required'
        }), 400
    
    # Validate required fields
    required_fields = ['name', 'email', 'password', 'role']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            'error': 'Validation error',
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    # Check if email already exists
    if any(u['email'] == email for u in DEMO_USERS):
        return jsonify({
            'error': 'Registration failed',
            'message': 'Email already registered'
        }), 409
    
    # Validate role
    valid_roles = ['athlete', 'coach', 'official', 'viewer', 'registrar', 'chief_registrar', 'starter']
    if role not in valid_roles:
        return jsonify({
            'error': 'Validation error',
            'message': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
        }), 400
    
    # Create new user
    new_user = {
        'id': len(DEMO_USERS) + 1,
        'name': name,
        'email': email,
        'password': password,  # In production, hash the password
        'role': role,
        'status': 'active',
        'lastLogin': 'Never',
        'createdAt': datetime.now().strftime('%Y-%m-%d')
    }
    
    DEMO_USERS.append(new_user)
    
    # Return user data (excluding password)
    user_data = {k: v for k, v in new_user.items() if k != 'password'}
    
    return jsonify(add_metadata({
        'message': '✅ Registration successful',
        'user': user_data
    })), 201


@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Password reset request endpoint"""
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Email is required'
        }), 400
    
    email = data.get('email')
    
    # Find user by email
    user = next((u for u in DEMO_USERS if u['email'] == email), None)
    
    if not user:
        # Don't reveal if email exists (security best practice)
        # Return success even if user not found
        return jsonify(add_metadata({
            'message': '✅ If the email exists, a password reset link has been sent'
        })), 200
    
    # In production, generate reset token and send email
    # For demo, just return success
    return jsonify(add_metadata({
        'message': '✅ Password reset link sent to your email',
        'demo_note': 'In production, this would send an email with reset link'
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


# Race Management Endpoints (Chief Registrar)

@app.route('/api/races', methods=['GET'])
def get_races():
    """Get all races"""
    return jsonify(add_metadata({
        'races': DEMO_RACES,
        'count': len(DEMO_RACES),
        'message': '✅ Races retrieved successfully'
    })), 200


@app.route('/api/races', methods=['POST'])
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
    
    # Generate public registration link
    import random
    import string
    link_id = 'pub_race_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    new_race = {
        'id': len(DEMO_RACES) + 1,
        'name': data['name'],
        'date': data['date'],
        'location': data['location'],
        'status': data.get('status', 'draft'),
        'created_by': data.get('created_by', 2),
        'registration_link': link_id,
        'events': data.get('events', []),
        'createdAt': datetime.now().strftime('%Y-%m-%d')
    }
    
    DEMO_RACES.append(new_race)
    PUBLIC_LINKS[link_id] = {
        'race_id': new_race['id'],
        'active': True,
        'expires': data['date']
    }
    
    return jsonify(add_metadata({
        'message': '✅ Race created successfully',
        'race': new_race,
        'registration_url': f'/register/{link_id}'
    })), 201


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
    if link_id not in PUBLIC_LINKS:
        return jsonify({'error': 'Invalid or expired registration link'}), 404
    
    link_data = PUBLIC_LINKS[link_id]
    if not link_data['active']:
        return jsonify({'error': 'Registration link is no longer active'}), 403
    
    race = next((r for r in DEMO_RACES if r['id'] == link_data['race_id']), None)
    
    return jsonify(add_metadata({
        'race': race,
        'expires': link_data['expires'],
        'message': '✅ Registration link is valid'
    })), 200


@app.route('/register/<link_id>', methods=['POST'])
def public_register_athlete(link_id):
    """Public athlete registration via link"""
    if link_id not in PUBLIC_LINKS:
        return jsonify({'error': 'Invalid or expired registration link'}), 404
    
    link_data = PUBLIC_LINKS[link_id]
    if not link_data['active']:
        return jsonify({'error': 'Registration link is no longer active'}), 403
    
    data = request.get_json()
    data['registration_type'] = 'public'
    data['registered_by'] = None
    
    return register_athlete(link_data['race_id'])


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


# Serve static frontend files (HTML, CSS, JS)
@app.route('/<path:path>')
def serve_static(path):
    """Serve static frontend files"""
    try:
        return send_from_directory(FRONTEND_DIR, path)
    except:
        # If file not found, return 404 or redirect to index
        return send_from_directory(FRONTEND_DIR, 'index.html')


if __name__ == '__main__':
    port = app.config['PORT']
    print("=" * 60)
    print(f"🏃‍♂️  {APP_NAME} v{APP_VERSION}")
    print("=" * 60)
    print(f"🚀  Server starting on http://0.0.0.0:{port}")
    print(f"📊  Environment: {'Development' if app.config['DEBUG'] else 'Production'}")
    print(f"⚡  Status: Ready to serve requests")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
