"""
API Service Layer
Provides common functionality for all API endpoints
"""

from flask import request, jsonify
from functools import wraps
from datetime import datetime
from typing import Callable, Optional, Dict, Any, List
from pydantic import ValidationError as PydanticValidationError
import time
import jwt

from logger import APILogger, get_logger
from errors import (
    ValidationError, AuthenticationError, AuthorizationError,
    NotFoundError, BadRequestError, InvalidTokenError
)


logger = get_logger(__name__)


class APIResponse:
    """API Response builder"""
    
    @staticmethod
    def success(
        data: Optional[Any] = None,
        message: str = 'Success',
        code: int = 200
    ) -> tuple:
        """Build success response"""
        response = {
            'success': True,
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(response), code
    
    @staticmethod
    def error(
        message: str,
        code: int = 400,
        error_type: str = 'Error',
        details: Optional[Dict] = None
    ) -> tuple:
        """Build error response"""
        response = {
            'success': False,
            'error': message,
            'error_type': error_type,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(response), code
    
    @staticmethod
    def paginated(
        data: List,
        total: int,
        page: int = 1,
        per_page: int = 20,
        code: int = 200
    ) -> tuple:
        """Build paginated response"""
        total_pages = (total + per_page - 1) // per_page
        response = {
            'success': True,
            'data': data,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(response), code


class RequestValidator:
    """Validate and parse requests"""
    
    @staticmethod
    def validate_json_body(required: bool = True) -> Dict[str, Any]:
        """Validate and get JSON body"""
        if not request.is_json:
            raise BadRequestError('Request must be JSON')
        
        data = request.get_json(silent=True)
        
        if data is None and required:
            raise BadRequestError('Request body is required')
        
        return data or {}
    
    @staticmethod
    def validate_schema(schema_class, data: Dict[str, Any]):
        """Validate data against Pydantic schema"""
        try:
            return schema_class(**data)
        except PydanticValidationError as e:
            # Extract validation error details
            errors = {}
            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'])
                errors[field] = error['msg']
            
            raise ValidationError(
                message='Request validation failed',
                details={'field_errors': errors}
            )
    
    @staticmethod
    def get_pagination_params() -> tuple[int, int]:
        """Extract pagination parameters from query"""
        try:
            page = max(1, int(request.args.get('page', 1)))
            per_page = max(1, min(100, int(request.args.get('per_page', 20))))
            return page, per_page
        except (ValueError, TypeError):
            raise BadRequestError('Invalid pagination parameters')
    
    @staticmethod
    def get_sort_params() -> tuple[Optional[str], str]:
        """Extract sort parameters from query"""
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc').lower()
        
        if sort_order not in ('asc', 'desc'):
            raise BadRequestError('sort_order must be "asc" or "desc"')
        
        return sort_by, sort_order


class TokenValidator:
    """Validate JWT tokens"""
    
    @staticmethod
    def get_token_from_header() -> str:
        """Extract JWT token from Authorization header"""
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            raise AuthenticationError('Missing or invalid Authorization header')
        
        return auth_header[7:]  # Remove 'Bearer ' prefix
    
    @staticmethod
    def verify_token(token: str, secret_key: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError('Token has expired')
        except jwt.InvalidTokenError:
            raise InvalidTokenError('Invalid token')
    
    @staticmethod
    def decode_token_safe(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
        """Safely decode token, return None if invalid"""
        try:
            return jwt.decode(token, secret_key, algorithms=['HS256'])
        except Exception:
            return None


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require JWT authentication
    Extracts and validates token, adds to request context
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            token = TokenValidator.get_token_from_header()
            from flask import current_app
            payload = TokenValidator.verify_token(token, current_app.config['JWT_SECRET_KEY'])
            
            # Store in request context
            request.user_id = payload.get('user_id')
            request.user_role = payload.get('role')
            request.auth_token = token
            
            return func(*args, **kwargs)
        except AuthenticationError as e:
            return APIResponse.error(e.message, 401, 'AuthenticationError'), 401
    
    return wrapped


def require_role(*allowed_roles: str) -> Callable:
    """
    Decorator to require specific user role
    Must be used after @require_auth
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not hasattr(request, 'user_role'):
                return APIResponse.error('Authentication required', 401, 'AuthenticationError'), 401
            
            if request.user_role not in allowed_roles:
                return APIResponse.error(
                    f'This operation requires one of: {", ".join(allowed_roles)}',
                    403,
                    'AuthorizationError'
                ), 403
            
            return func(*args, **kwargs)
        
        return wrapped
    return decorator


def log_api_call(func: Callable) -> Callable:
    """
    Decorator to log API calls
    Logs request, response, and performance metrics
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        start_time = time.time()
        endpoint = f'{request.method} {request.path}'
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            # Extract status code from response
            status_code = 200
            if isinstance(result, tuple):
                status_code = result[1] if len(result) > 1 else 200
            
            APILogger.log_response(
                request.method,
                request.path,
                status_code,
                duration_ms,
                getattr(request, 'user_id', None)
            )
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            APILogger.log_error(e, request.path, getattr(request, 'user_id', None))
            logger.exception(f'Error in {endpoint}')
            raise
    
    return wrapped


def validate_input(schema_class) -> Callable:
    """
    Decorator to validate request against Pydantic schema
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                data = RequestValidator.validate_json_body()
                validated = RequestValidator.validate_schema(schema_class, data)
                return func(validated, *args, **kwargs)
            except (ValidationError, BadRequestError, AuthenticationError) as e:
                return APIResponse.error(
                    e.message,
                    e.code,
                    e.error_type,
                    e.details
                ), e.code
        
        return wrapped
    return decorator


class PaginationHelper:
    """Helper for paginating database queries"""
    
    @staticmethod
    def paginate(query, page: int = 1, per_page: int = 20):
        """Paginate SQLAlchemy query"""
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return items, total
    
    @staticmethod
    def apply_sort(query, sort_by: Optional[str], sort_order: str = 'asc', allowed_fields: List[str] = None):
        """Apply sorting to query"""
        if not sort_by or not allowed_fields or sort_by not in allowed_fields:
            return query
        
        # Get column from model
        sort_column = getattr(query.column_descriptions[0]['type'], sort_by, None)
        if not sort_column:
            return query
        
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        return query
