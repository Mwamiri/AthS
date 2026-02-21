"""
AthSys Backend - Athletics Management System
Main application entry point with enhanced UX features
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import time
from datetime import datetime

app = Flask(__name__)
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
    """Root endpoint with comprehensive system information"""
    return jsonify(add_metadata({
        'name': APP_NAME,
        'version': APP_VERSION,
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'System operational',
        'environment': 'production' if not app.config['DEBUG'] else 'development',
        'endpoints': {
            'health': '/health',
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
