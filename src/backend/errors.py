"""
Enterprise Error Handling
Custom exceptions and error handlers for API
"""

from flask import jsonify, request
from datetime import datetime
from typing import Optional, Dict, Any


class APIException(Exception):
    """Base API exception"""
    
    def __init__(
        self,
        message: str,
        code: int = 500,
        error_type: str = 'InternalServerError',
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to response dictionary"""
        return {
            'error': self.message,
            'code': self.code,
            'error_type': self.error_type,
            'details': self.details,
            'timestamp': datetime.utcnow().isoformat()
        }


class ValidationError(APIException):
    """Request validation error"""
    
    def __init__(self, message: str = 'Validation failed', details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code=400,
            error_type='ValidationError',
            details=details
        )


class AuthenticationError(APIException):
    """Authentication failed"""
    
    def __init__(self, message: str = 'Authentication failed'):
        super().__init__(
            message=message,
            code=401,
            error_type='AuthenticationError'
        )


class AuthorizationError(APIException):
    """User not authorized to perform action"""
    
    def __init__(self, message: str = 'Insufficient permissions'):
        super().__init__(
            message=message,
            code=403,
            error_type='AuthorizationError'
        )


class NotFoundError(APIException):
    """Resource not found"""
    
    def __init__(self, resource: str = 'Resource'):
        super().__init__(
            message=f'{resource} not found',
            code=404,
            error_type='NotFoundError'
        )


class ConflictError(APIException):
    """Resource already exists or conflict"""
    
    def __init__(self, message: str = 'Resource already exists'):
        super().__init__(
            message=message,
            code=409,
            error_type='ConflictError'
        )


class RateLimitError(APIException):
    """Rate limit exceeded"""
    
    def __init__(self, message: str = 'Rate limit exceeded'):
        super().__init__(
            message=message,
            code=429,
            error_type='RateLimitError'
        )


class DatabaseError(APIException):
    """Database operation failed"""
    
    def __init__(self, message: str = 'Database operation failed'):
        super().__init__(
            message=message,
            code=500,
            error_type='DatabaseError'
        )


class ExternalServiceError(APIException):
    """External service call failed"""
    
    def __init__(self, service: str = 'External Service'):
        super().__init__(
            message=f'{service} temporarily unavailable',
            code=503,
            error_type='ExternalServiceError'
        )


class InvalidTokenError(AuthenticationError):
    """JWT token is invalid or expired"""
    
    def __init__(self, message: str = 'Invalid or expired token'):
        super().__init__(message)
        self.code = 401


class BadRequestError(APIException):
    """Bad request"""
    
    def __init__(self, message: str = 'Bad request'):
        super().__init__(
            message=message,
            code=400,
            error_type='BadRequestError'
        )


def register_error_handlers(app):
    """Register error handlers with Flask application"""
    
    @app.errorhandler(APIException)
    def handle_api_exception(error: APIException):
        """Handle custom API exceptions"""
        response = error.to_dict()
        return jsonify(response), error.code
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 Bad Request"""
        exc = BadRequestError(str(error.description))
        return jsonify(exc.to_dict()), 400
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle 401 Unauthorized"""
        exc = AuthenticationError('Authentication required')
        return jsonify(exc.to_dict()), 401
    
    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle 403 Forbidden"""
        exc = AuthorizationError('Access denied')
        return jsonify(exc.to_dict()), 403
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found"""
        exc = NotFoundError(f'Endpoint {request.path}')
        return jsonify(exc.to_dict()), 404
    
    @app.errorhandler(429)
    def handle_rate_limit(error):
        """Handle 429 Rate Limit"""
        exc = RateLimitError('Too many requests')
        return jsonify(exc.to_dict()), 429
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 Internal Server Error"""
        exc = APIException(
            message='An unexpected error occurred',
            code=500,
            error_type='InternalServerError'
        )
        return jsonify(exc.to_dict()), 500
    
    @app.errorhandler(503)
    def handle_service_unavailable(error):
        """Handle 503 Service Unavailable"""
        exc = ExternalServiceError()
        return jsonify(exc.to_dict()), 503


def validate_request_json(data):
    """Validate that request has JSON data"""
    if not data:
        raise BadRequestError('Request body is required')
    return data
