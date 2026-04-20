import logging
import uuid
from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from redis import Redis

from config import get_config

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record),
            "logger": record.name,
        }

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        import json

        return json.dumps(log_data)


def setup_logging(app: Flask) -> None:
    """Configure structured logging."""
    config = app.config.get("CONFIG_OBJECT")

    if config:
        log_level = getattr(config, "LOG_LEVEL", "INFO")
        log_format = getattr(config, "LOG_FORMAT", "json")

        handler = logging.StreamHandler()
        handler.setLevel(getattr(logging, log_level))

        if log_format == "json":
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )

        app.logger.addHandler(handler)
        app.logger.setLevel(getattr(logging, log_level))


def create_error_response(
    error: str, message: str, status_code: int, request_id: str
) -> tuple:
    """Create standardized error response."""
    response = jsonify(
        {"error": error, "message": message, "request_id": request_id}
    )
    response.status_code = status_code
    return response


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        request_id = getattr(request, "request_id", str(uuid.uuid4()))
        return create_error_response(
            "Bad Request", str(error.description), 400, request_id
        )

    @app.errorhandler(401)
    def unauthorized(error):
        request_id = getattr(request, "request_id", str(uuid.uuid4()))
        return create_error_response(
            "Unauthorized", str(error.description), 401, request_id
        )

    @app.errorhandler(403)
    def forbidden(error):
        request_id = getattr(request, "request_id", str(uuid.uuid4()))
        return create_error_response(
            "Forbidden", str(error.description), 403, request_id
        )

    @app.errorhandler(404)
    def not_found(error):
        request_id = getattr(request, "request_id", str(uuid.uuid4()))
        return create_error_response(
            "Not Found", str(error.description), 404, request_id
        )

    @app.errorhandler(429)
    def ratelimit_handler(error):
        request_id = getattr(request, "request_id", str(uuid.uuid4()))
        return create_error_response(
            "Rate Limit Exceeded", str(error.description), 429, request_id
        )

    @app.errorhandler(500)
    def internal_error(error):
        request_id = getattr(request, "request_id", str(uuid.uuid4()))
        app.logger.error(f"Internal error: {error}", extra={"request_id": request_id})
        return create_error_response(
            "Internal Server Error", "An unexpected error occurred", 500, request_id
        )


def init_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    config = app.config.get("CONFIG_OBJECT")

    db.init_app(app)
    limiter.init_app(app)
    JWTManager(app)

    if config and getattr(config, "TALISMAN_ENABLED", False):
        talisman.init_app(
            app,
            force_https=getattr(config, "FORCE_HTTPS", False),
            content_security_policy={
                "default-src": "'self'",
                "script-src": ["'self'", "'unsafe-inline'"],
                "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
                "font-src": ["'self'", "https://fonts.gstatic.com"],
            },
        )

    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
    )


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""
    from api.data_api import data_bp

    app.register_blueprint(data_bp, url_prefix="/api/data")


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)

    config = get_config()
    app.config.from_object(config)
    app.config["CONFIG_OBJECT"] = config

    setup_logging(app)
    init_extensions(app)
    register_error_handlers(app)
    register_blueprints(app)

    @app.before_request
    def before_request():
        request.request_id = str(uuid.uuid4())
        app.logger.info(
            f"{request.method} {request.path}",
            extra={"request_id": request.request_id},
        )

    @app.after_request
    def after_request(response):
        response.headers["X-Request-ID"] = getattr(request, "request_id", "")
        return response

    @app.route("/api/health")
    @limiter.exempt
    def health_check():
        return jsonify(
            {
                "status": "healthy",
                "version": config.APP_VERSION,
                "service": config.APP_NAME,
            }
        )

    with app.app_context():
        db.create_all()

    app.logger.info(f"{config.APP_NAME} v{config.APP_VERSION} started")

    return app


app = create_app()
