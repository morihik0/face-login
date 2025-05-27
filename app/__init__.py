"""
Main application package for Face Login system.
This module initializes the Flask application and sets up all necessary configurations.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import API, LOGGING
from app.database.db import init_db

# Configure logger
logger = logging.getLogger(__name__)

def create_app(test_config=None):
    """
    Create and configure the Flask application.
    
    Args:
        test_config (dict, optional): Test configuration to override default configs.
        
    Returns:
        Flask: The configured Flask application instance.
    """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        DATABASE=os.path.join(app.instance_path, 'face_login.db'),
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production'),
        JWT_ACCESS_TOKEN_EXPIRES=3600,  # 1 hour
        JWT_REFRESH_TOKEN_EXPIRES=2592000,  # 30 days
    )
    
    # Load test config if provided, otherwise load from environment variables
    if test_config is not None:
        app.config.update(test_config)
    
    # Configure CORS
    CORS(app, resources={r"/api/*": {"origins": API['cors_origins']}})
    
    # Configure JWT
    jwt = JWTManager(app)
    
    # Configure rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    # Configure logging
    configure_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Register blueprints
    register_blueprints(app)
    
    # Create a simple index route
    @app.route('/')
    def index():
        return jsonify({
            "status": "success",
            "message": "Face Login API is running",
            "version": "1.0.0"
        })
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "status": "error",
            "message": "Token has expired",
            "error": "token_expired"
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "status": "error",
            "message": "Invalid token",
            "error": "invalid_token"
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "status": "error",
            "message": "Authorization required",
            "error": "authorization_required"
        }), 401
    
    logger.info("Flask application initialized successfully")
    return app

def configure_logging(app):
    """
    Configure logging for the application.
    
    Args:
        app (Flask): The Flask application instance.
    """
    # Set log level
    log_level = getattr(logging, LOGGING['level'].upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=LOGGING['format']
    )
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(LOGGING['file'])
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create file handler
    file_handler = RotatingFileHandler(
        LOGGING['file'],
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(LOGGING['format']))
    file_handler.setLevel(log_level)
    
    # Add file handler to app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    
    # Add file handler to root logger
    logging.getLogger().addHandler(file_handler)
    
    logger.info(f"Logging configured with level: {LOGGING['level']}")

def register_error_handlers(app):
    """
    Register global error handlers for the application.
    
    Args:
        app (Flask): The Flask application instance.
    """
    @app.errorhandler(400)
    def bad_request(error):
        logger.error(f"Bad request: {error}")
        return jsonify({
            "status": "error",
            "message": "Bad request",
            "error": str(error)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"Resource not found: {error}")
        return jsonify({
            "status": "error",
            "message": "Resource not found",
            "error": str(error)
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "error": str(error)
        }), 500
    
    # Generic exception handler
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.exception(f"Unhandled exception: {error}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred",
            "error": str(error)
        }), 500
    
    logger.info("Error handlers registered")

def register_blueprints(app):
    """
    Register blueprints for the application.
    
    Args:
        app (Flask): The Flask application instance.
    """
    # Import blueprints
    from app.api import users_bp, recognition_bp, auth_bp, public_bp
    
    # Register blueprints
    app.register_blueprint(public_bp, url_prefix='/api/public')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(recognition_bp, url_prefix='/api/recognition')
    
    logger.info("Blueprints registered")