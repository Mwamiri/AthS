"""
Enterprise Logging Configuration
Structured logging with JSON format for production
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
import structlog


def setup_logging(app):
    """
    Configure structured logging for Flask application
    Supports both text and JSON formats
    """
    
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = app.config.get('LOG_FORMAT', 'json')
    log_file = app.config.get('LOG_FILE', 'logs/athsys.log')
    
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.flatten_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    
    if log_format == 'json':
        # JSON formatter for production
        formatter = jsonlogger.JsonFormatter()
        
        # Console handler with JSON
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler with JSON
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    else:
        # Text formatter for development
        text_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler with text
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(text_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler with text
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(text_formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress noisy loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


class APILogger:
    """
    Logger for API requests and responses
    Provides detailed logging for debugging and monitoring
    """
    
    @staticmethod
    def log_request(method: str, endpoint: str, params: dict = None, user_id: str = None):
        """Log incoming API request"""
        logger = get_logger('api.request')
        logger.info(
            'api_request',
            extra={
                'method': method,
                'endpoint': endpoint,
                'params': params,
                'user_id': user_id,
            }
        )
    
    @staticmethod
    def log_response(method: str, endpoint: str, status_code: int, duration_ms: float, user_id: str = None):
        """Log API response"""
        logger = get_logger('api.response')
        level = 'info'
        if status_code >= 500:
            level = 'error'
        elif status_code >= 400:
            level = 'warning'
        
        getattr(logger, level)(
            'api_response',
            extra={
                'method': method,
                'endpoint': endpoint,
                'status_code': status_code,
                'duration_ms': duration_ms,
                'user_id': user_id,
            }
        )
    
    @staticmethod
    def log_error(error: Exception, endpoint: str, user_id: str = None):
        """Log API error"""
        logger = get_logger('api.error')
        logger.exception(
            'api_error',
            extra={
                'endpoint': endpoint,
                'user_id': user_id,
                'error_type': type(error).__name__,
            }
        )
    
    @staticmethod
    def log_auth(action: str, user_id: str, success: bool, details: str = None):
        """Log authentication events"""
        logger = get_logger('auth')
        level = 'info' if success else 'warning'
        getattr(logger, level)(
            f'auth_{action}',
            extra={
                'user_id': user_id,
                'success': success,
                'details': details,
            }
        )


class DatabaseLogger:
    """Logger for database operations"""
    
    @staticmethod
    def log_query(query: str, duration_ms: float, rows_affected: int = None):
        """Log database query"""
        logger = get_logger('db.query')
        logger.debug(
            'db_query',
            extra={
                'query': query,
                'duration_ms': duration_ms,
                'rows_affected': rows_affected,
            }
        )
    
    @staticmethod
    def log_transaction(action: str, table: str, user_id: str = None):
        """Log database transaction"""
        logger = get_logger('db.transaction')
        logger.info(
            f'db_{action}',
            extra={
                'table': table,
                'user_id': user_id,
            }
        )


class AuditLogger:
    """Logger for audit trail and compliance"""
    
    @staticmethod
    def log_action(action: str, resource: str, resource_id: int, user_id: str, changes: dict = None):
        """Log auditable action"""
        logger = get_logger('audit')
        logger.info(
            'audit_action',
            extra={
                'action': action,
                'resource': resource,
                'resource_id': resource_id,
                'user_id': user_id,
                'changes': changes,
            }
        )
