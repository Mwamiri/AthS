"""
AthSys Security Module
Comprehensive security utilities for authentication, validation, and protection
"""

import re
import html
from functools import wraps
from flask import request, jsonify
import secrets
import hashlib

class SecurityManager:
    """Centralized security management"""
    
    @staticmethod
    def sanitize_input(input_string, field_type='text'):
        """Sanitize user input to prevent XSS and injection attacks"""
        if not isinstance(input_string, str):
            return input_string
        
        # Remove control characters
        clean = ''.join(char for char in input_string if ord(char) >= 32 or char in '\n\r\t')
        
        # HTML escape to prevent XSS
        clean = html.escape(clean, quote=True)
        
        # Additional type-specific validation
        if field_type == 'email':
            # Basic email validation
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', clean):
                return None
        
        elif field_type == 'username':
            # Allow alphanumeric, underscore, hyphen only
            if not re.match(r'^[a-zA-Z0-9_-]{2,32}$', clean):
                return None
        
        elif field_type == 'name':
            # Allow letters, spaces, hyphens, apostrophes
            if not re.match(r"^[a-zA-Z\s'-]{2,100}$", clean):
                return None
        
        return clean
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password meets all security requirements"""
        if not password or len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password is too long (max 128 characters)"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            return False, "Password must contain at least one special character (!@#$%^&*)"
        
        # Check for common weak passwords
        common_weak = ['password', '12345678', 'qwerty', 'abc123', 'letmein']
        if password.lower() in common_weak:
            return False, "Password is too common. Please choose a stronger password"
        
        return True, "Password is strong"
    
    @staticmethod
    def generate_csrf_token():
        """Generate CSRF token for form protection"""
        return secrets.token_hex(32)
    
    @staticmethod
    def verify_csrf_token(token, session_token):
        """Verify CSRF token matches session"""
        return token == session_token
    
    @staticmethod
    def hash_sensitive_data(data):
        """Hash sensitive data for logging/storage"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    @staticmethod
    def is_valid_ip(ip_string):
        """Validate IP address format"""
        parts = ip_string.split('.')
        if len(parts) != 4:
            return False
        return all(0 <= int(part) <= 255 for part in parts)
    
    @staticmethod
    def rate_limit_key(identifier, action):
        """Generate rate limit key combining identifier and action"""
        return f"ratelimit:{action}:{identifier}"
    
    @staticmethod
    def log_security_event(event_type, details, severity='info'):
        """Log security-related events"""
        event = {
            'type': event_type,
            'details': details,
            'severity': severity,  # info, warning, critical
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'ip': request.remote_addr if request else 'unknown'
        }
        print(f"[SECURITY {severity.upper()}] {event_type}: {details}")
        return event


def require_https(f):
    """Decorator to require HTTPS in production"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.environ.get('HTTP_X_FORWARDED_PROTO') == 'https' and not request.is_secure:
            import os
            if os.getenv('ENVIRONMENT', 'development') == 'production':
                return jsonify({'error': 'HTTPS required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def validate_json_content_type(f):
    """Decorator to validate JSON content type"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return decorated_function


def add_csrf_token_header(f):
    """Decorator to add CSRF token to response headers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        if isinstance(response, tuple):
            response_data = response[0]
        else:
            response_data = response
        
        # Generate and send CSRF token
        csrf_token = SecurityManager.generate_csrf_token()
        if isinstance(response, tuple):
            response_obj = response[0]
            status_code = response[1] if len(response) > 1 else 200
            response_obj.headers['X-CSRF-Token'] = csrf_token
            return response_obj, status_code
        else:
            response_data.headers['X-CSRF-Token'] = csrf_token
            return response_data
    
    return decorated_function


# Password strength requirements constants
PASSWORD_REQUIREMENTS = {
    'min_length': 8,
    'max_length': 128,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_numbers': True,
    'require_special': True,
    'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?'
}

# Rate limiting constants
RATE_LIMITS = {
    'login': {'max_attempts': 5, 'window': 1800},  # 5 attempts per 30 minutes
    'register': {'max_attempts': 5, 'window': 3600},  # 5 registrations per hour
    'password_reset': {'max_attempts': 3, 'window': 3600},  # 3 resets per hour
    'api_call': {'max_requests': 100, 'window': 3600}  # 100 requests per hour
}

# Input validation patterns
INPUT_PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'username': r'^[a-zA-Z0-9_-]{2,32}$',
    'phone': r'^[\d+\-\s()]{10,20}$',
    'url': r'^https?://[^\s]+$'
}
