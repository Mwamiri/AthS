import os
from datetime import timedelta
from typing import Optional


class Config:
    """Base configuration with validation."""

    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", self.SECRET_KEY)
        self.JWT_ACCESS_TOKEN_EXPIRES = timedelta(
            seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))
        )
        self.JWT_REFRESH_TOKEN_EXPIRES = timedelta(
            seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 604800))
        )
        self.TALISMAN_ENABLED = os.getenv("TALISMAN_ENABLED", "false").lower() == "true"
        self.FORCE_HTTPS = os.getenv("FORCE_HTTPS", "false").lower() == "true"
        self.RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "100 per hour")
        self.RATELIMIT_STORAGE_URL = os.getenv(
            "RATELIMIT_STORAGE_URL", self.REDIS_URL
        )
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
        self.APP_NAME = os.getenv("APP_NAME", "AthS")
        self.APP_VERSION = os.getenv("APP_VERSION", "3.0.0")
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
        self.JSON_SORT_KEYS = False
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024

        self._validate()

    def _validate(self):
        """Validate required configuration."""
        errors = []

        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            errors.append(
                "SECRET_KEY must be set and at least 32 characters long"
            )

        if not self.DATABASE_URL:
            errors.append("DATABASE_URL must be set")

        if not self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
            errors.append(
                "JWT_SECRET_KEY must be set and at least 32 characters long"
            )

        if errors:
            raise ValueError(f"Configuration errors: {'; '.join(errors)}")


class DevelopmentConfig(Config):
    """Development configuration."""

    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.TALISMAN_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    def __init__(self):
        super().__init__()
        self.DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": ProductionConfig,
}


def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv("FLASK_ENV", "production")
    config_class = config_map.get(env, ProductionConfig)
    return config_class()
