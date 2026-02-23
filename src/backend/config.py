"""
Enterprise Configuration Management
Handles development, testing, and production configurations
"""

import os
from datetime import timedelta
from typing import Optional


class BaseConfig:
    """Base configuration shared across all environments"""
    
    # Flask Configuration
    DEBUG = False
    TESTING = False
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'development-secret-key-change-in-production')
    
    # Server Configuration
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Database Configuration
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://athsys_user:athsys_pass@localhost:5432/athsys_db'
    )
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    SESSION_REDIS_URL = REDIS_URL
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Two-Factor Authentication (2FA) Configuration
    TWO_FA_ENABLED = os.getenv('TWO_FA_ENABLED', 'True') == 'True'
    TWO_FA_OPTIONAL = os.getenv('TWO_FA_OPTIONAL', 'True') == 'True'
    TWO_FA_ISSUER_NAME = 'AthSys'
    TWO_FA_TOTP_WINDOW = 1  # Allow ±1 time window for TOTP verification
    TWO_FA_BACKUP_CODES_COUNT = 10
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = '100/hour'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = 'json'  # 'json' or 'text'
    LOG_FILE = os.getenv('LOG_FILE', 'logs/athsys.log')
    
    # Monitoring & Metrics
    PROMETHEUS_ENABLED = True
    METRICS_PORT = 9090
    
    # Application Version
    APP_VERSION = '2.3.0'  # Semantic versioning: MAJOR.MINOR.PATCH
    API_VERSION = 'v2.3'
    API_TITLE = 'AthSys API'
    
    # Version History for tracking
    VERSION_HISTORY = {
        '2.3.0': 'Enterprise reliability baseline: JWT auth with refresh rotation, global admin RBAC enforcement, Redis in-memory fallback resilience, request correlation IDs, global API idempotency replay support',
        '2.2.0': 'Modular plugin system with 20+ configurable plugins, Official timing system for chiefs/officials with manual timer, Public races & results portal (no login required), Plugin admin dashboard, Advanced search and filtering, World Athletics standard timing format',
        '2.1.6': 'CI/CD pipeline, Database migrations, Health monitoring with alerts, Audit logging, Email notifications, Feature flags, Request deduplication, Rate limit dashboard, Graceful shutdown, 2FA optional',
        '2.1.5': 'Two-Factor Authentication (optional, TOTP + backup codes)',
        '2.1.4': 'Advanced admin dashboard, real-time features',
        '2.1.3': 'Report generation system',
        '2.1.2': 'API rate limiting with per-user policies',
        '2.1.1': 'Enterprise backend infrastructure (config, logging, validation, error handling, API service layer, monitoring, documentation, testing, state management, DevOps)',
        '2.1.0': 'Joomla-style menu system, notification center, offline caching, enhanced authentication'
    }
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # File Upload
    MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx'}
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True
    LOG_LEVEL = 'DEBUG'
    RATELIMIT_ENABLED = False


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    REDIS_URL = 'redis://localhost:6379/1'
    LOG_LEVEL = 'DEBUG'
    RATELIMIT_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    SQLALCHEMY_ECHO = False
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = '1000/hour'


def get_config(env: Optional[str] = None) -> BaseConfig:
    """Get configuration based on environment"""
    env = env or os.getenv('FLASK_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
    }
    
    return configs.get(env, DevelopmentConfig)()
