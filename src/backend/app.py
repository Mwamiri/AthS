"""
AthSys Backend - Athletics Management System
Main application entry point
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
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


@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'name': APP_NAME,
        'version': APP_VERSION,
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health')
def health():
    """Health check endpoint for Docker and monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'athsys-backend',
        'version': APP_VERSION,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/athletes', methods=['GET'])
def get_athletes():
    """Get all athletes"""
    # TODO: Connect to database and fetch real data
    return jsonify({
        'athletes': [],
        'message': 'Athlete management coming soon'
    })


@app.route('/api/athletes', methods=['POST'])
def create_athlete():
    """Create new athlete"""
    data = request.get_json()
    # TODO: Implement athlete creation
    return jsonify({
        'message': 'Athlete creation endpoint',
        'received': data
    }), 201


@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    return jsonify({
        'events': [],
        'message': 'Event management coming soon'
    })


@app.route('/api/results', methods=['GET'])
def get_results():
    """Get competition results"""
    return jsonify({
        'results': [],
        'message': 'Results tracking coming soon'
    })


@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    return jsonify({
        'total_athletes': 0,
        'total_events': 0,
        'total_results': 0,
        'system_status': 'operational'
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An error occurred processing your request'
    }), 500


if __name__ == '__main__':
    port = app.config['PORT']
    print(f"Starting {APP_NAME} v{APP_VERSION}")
    print(f"Running on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
